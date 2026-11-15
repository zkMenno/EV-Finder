"""RDW Open Data adapter (CC0-1.0): battery-electric passenger cars in NL.

Three outputs, all per make (`merk`) x trade name (`handelsbenaming`) x year of first
admission (`jaar`, from `datum_eerste_toelating_dt`). That grouping is written into every
record_key as `[merk|handelsbenaming|jaar]`.

1. **Fleet count** (`registration_count`, confidence high): one grouped query in
   `m9d7-ebf2` (gekentekende voertuigen). About 3,100 rows.
2. **NL catalogue price** (`spec`, `price_new`, country NL, confidence medium): server-side
   `median(catalogusprijs)` and `count(catalogusprijs)` per group, cars sold new in NL only
   (`datum_eerste_toelating = datum_eerste_tenaamstelling_in_nederland`, so used imports with
   a later NL price don't mix in). RDW definition: "De catalogusprijs is gebaseerd op
   informatie van de importeur en is als volgt berekend: netto-catalogusprijs, verhoogd met
   de BTW en de BPM" (Beschrijving dataset gekentekende voertuigen v5.4). So: EUR, incl. VAT
   and BPM (BEVs paid no BPM before 2025), the bijtelling basis.
3. **WLTP range and consumption** (`spec`, confidence medium): the values live in the fuel
   table `8ys7-d773` (`actie_radius_enkel_elektrisch_wltp`, km;
   `elektrisch_verbruik_enkel_elektrisch_wltp`, Wh/km), which has no make or model, and
   Socrata refuses joins ("joins are not supported"). So we take a **deterministic 10 %
   plate sample** (`kenteken like '___7%'`: 4th character is the digit 7; checked
   2026-11-15 to give 9.0-10.2 % of BEVs in every first-admission year 2015-2026, fewer
   before 2015, which are NEDC-era cars without WLTP anyway), fetch only `kenteken` plus the
   needed columns from both tables, join in memory, and keep **only per-group value
   histograms**. Plates are never written to disk.

BEV filter in `m9d7-ebf2` (fuel is in the other table, so a proxy):

    voertuigsoort = 'Personenauto' AND cilinderinhoud IS NULL
    AND datum_eerste_toelating >= 20100101

Checked on 2026-11-15 against 8ys7-d773 with 1000-row random samples each way: 998/1000
proxy hits were BEV (1 fuel-cell car, 1 petrol), and 554/554 BEV passenger cars from
8ys7-d773 were proxy hits. See data/SOURCES.md.

**Never average across clearly different cars.** For each group and field, the spread is
the interquartile range (IQR) of the plate sample. IQR > 5 % of the median (MAX_IQR_RATIO)
means the group mixes different cars (e.g. Standard and Long Range in one year): we emit
nothing for that field and log it. Fewer than MIN_SAMPLE sampled cars: also nothing, unless
(price only) the group has at least MIN_SAMPLE cars and its server-side min and max are
already within 5 %. Note: a group passes when about three quarters of it share one value;
the median is then that majority car's value (a real car, not a blend), but other trims
in the group are not represented. Matching should attach these by evidence (WLTP km).
Socrata has `median()` but no percentile function, so the IQR has to come from the sample.
"""

from __future__ import annotations

import json
import time
from collections import Counter, defaultdict
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import httpx

from ev_pipeline import net
from ev_pipeline.records import SourceRecord, SpecValue
from ev_pipeline.schema_models import Confidence, Country, FactField, Source
from ev_pipeline.sources import _common as c

NAME = "rdw"
BASE_URL = "https://opendata.rdw.nl"
DATASET = "m9d7-ebf2"
FUEL_DATASET = "8ys7-d773"
PAGE_SIZE = 5000
PAGE_SLEEP_S = 1.0
"""Pause between paged requests (RDW fair use; no app token)."""

GROUPING = "merk|handelsbenaming|jaar"
MAX_IQR_RATIO = 0.05
MIN_SAMPLE = 5

PRICE_FILE = "price-000.json"
SAMPLE_FILE = "sample-groups.json"

BEV_WHERE = (
    "voertuigsoort = 'Personenauto' AND cilinderinhoud IS NULL "
    "AND datum_eerste_toelating >= 20100101"
)
NEW_IN_NL = "datum_eerste_toelating = datum_eerste_tenaamstelling_in_nederland"
SAMPLE_WHERE = "kenteken like '___7%'"
JAAR = "date_extract_y(datum_eerste_toelating_dt) AS jaar"

QUERY = {
    "$select": f"merk, handelsbenaming, {JAAR}, count(*) AS n",
    "$where": BEV_WHERE,
    "$group": "merk, handelsbenaming, jaar",
    "$order": "merk, handelsbenaming, jaar",
}
PRICE_QUERY = {
    "$select": f"merk, handelsbenaming, {JAAR}, count(catalogusprijs) AS n, "
    "median(catalogusprijs) AS med, min(catalogusprijs) AS mn, max(catalogusprijs) AS mx",
    "$where": f"{BEV_WHERE} AND {NEW_IN_NL} AND catalogusprijs > 0",
    "$group": "merk, handelsbenaming, jaar",
    "$order": "merk, handelsbenaming, jaar",
}
SAMPLE_MAIN_QUERY = {
    "$select": f"kenteken, merk, handelsbenaming, {JAAR}, catalogusprijs, {NEW_IN_NL} AS nieuw_nl",
    "$where": f"{BEV_WHERE} AND {SAMPLE_WHERE}",
    "$order": "kenteken",
}
SAMPLE_FUEL_QUERY = {
    "$select": "kenteken, actie_radius_enkel_elektrisch_wltp AS range_km, "
    "elektrisch_verbruik_enkel_elektrisch_wltp AS wh_km",
    "$where": "brandstof_omschrijving = 'Elektriciteit' AND "
    "(actie_radius_enkel_elektrisch_wltp IS NOT NULL OR "
    f"elektrisch_verbruik_enkel_elektrisch_wltp IS NOT NULL) AND {SAMPLE_WHERE}",
    "$order": "kenteken",
}

SOURCE = Source(
    id="rdw",
    name="RDW Open Data",
    url=f"{BASE_URL}/d/{DATASET}",
    licence="CC0-1.0",
    attribution="Bron: RDW Open Data (opendata.rdw.nl), CC0.",
)
FUEL_SOURCE = Source(
    id="rdw",
    name="RDW Open Data",
    url=f"{BASE_URL}/d/{FUEL_DATASET}",
    licence="CC0-1.0",
    attribution="Bron: RDW Open Data (opendata.rdw.nl), CC0.",
)


# --- fetch ------------------------------------------------------------------------------


def _paged(
    client: httpx.Client, dataset: str, query: dict[str, str], sleep_s: float
) -> Iterator[list[dict[str, Any]]]:
    page = 0
    while True:
        if page and sleep_s:
            time.sleep(sleep_s)
        params = {**query, "$limit": str(PAGE_SIZE), "$offset": str(page * PAGE_SIZE)}
        resp = client.get(f"{BASE_URL}/resource/{dataset}.json", params=params)
        resp.raise_for_status()
        batch = resp.json()
        yield batch
        page += 1
        if len(batch) < PAGE_SIZE:
            return


def _num(v: object) -> float | None:
    if v is None or v == "" or isinstance(v, bool):
        return None
    try:
        x = float(v)  # type: ignore[arg-type]  # Socrata sends numbers as strings
    except (TypeError, ValueError):
        return None
    return x if x > 0 else None


def _value_key(x: float) -> str:
    return str(int(x)) if x == int(x) else repr(x)


def sample_histograms(
    main_rows: list[dict[str, Any]], fuel_rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Join the plate sample in memory; return per-group histograms (no plates)."""
    fuel: dict[str, dict[str, Any]] = {}
    for row in fuel_rows:
        fuel.setdefault(str(row.get("kenteken")), row)  # one Elektriciteit row per BEV
    groups: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in main_rows:
        make, model, jaar = row.get("merk"), row.get("handelsbenaming"), row.get("jaar")
        if not make or not model:
            continue
        g = groups.setdefault(
            (make, model, str(jaar or "")),
            {"n": 0, "range_km": Counter(), "wh_km": Counter(), "price_eur": Counter()},
        )
        g["n"] += 1
        price = _num(row.get("catalogusprijs"))
        if price is not None and row.get("nieuw_nl") in (True, "true"):
            g["price_eur"][_value_key(price)] += 1
        f = fuel.get(str(row.get("kenteken")))
        if f is None:
            continue
        for col in ("range_km", "wh_km"):
            v = _num(f.get(col))
            if v is not None:
                g[col][_value_key(v)] += 1
    out = []
    for (make, model, jaar), g in sorted(groups.items()):
        entry: dict[str, Any] = {"merk": make, "handelsbenaming": model, "jaar": jaar, "n": g["n"]}
        for col in ("range_km", "wh_km", "price_eur"):
            entry[col] = sorted(([float(k), n] for k, n in g[col].items()), key=lambda kv: kv[0])
        out.append(entry)
    return out


def _view_meta(client: httpx.Client, dataset: str) -> dict[str, Any]:
    meta = client.get(f"{BASE_URL}/api/views/{dataset}.json")
    meta.raise_for_status()
    view = meta.json()
    licence_custom = view.get("metadata", {}).get("custom_fields", {}).get("Licentie", {})
    return {
        "dataset_name": view.get("name"),
        "dataset_rows_updated_at": view.get("rowsUpdatedAt"),
        "licence_metadata": {
            "license": view.get("license"),
            "licenseId": view.get("licenseId"),
            "custom_fields.Licentie": licence_custom.get("Licentie"),
        },
    }


def fetch(client: httpx.Client, target: Path, sleep_s: float = PAGE_SLEEP_S) -> int:
    """Fetch licence metadata, counts, price stats and the WLTP plate sample into `target`.

    Returns the number of count rows (the fleet table), as before.
    """
    main_meta = _view_meta(client, DATASET)
    fuel_meta = _view_meta(client, FUEL_DATASET)

    target.mkdir(parents=True, exist_ok=True)
    for old in [*target.glob("page-*.json"), target / PRICE_FILE, target / SAMPLE_FILE]:
        old.unlink(missing_ok=True)

    rows = pages = 0
    for batch in _paged(client, DATASET, QUERY, sleep_s):
        (target / f"page-{pages:03d}.json").write_text(
            json.dumps(batch, ensure_ascii=False, indent=0) + "\n", encoding="utf-8"
        )
        rows += len(batch)
        pages += 1

    price_rows: list[dict[str, Any]] = []
    for batch in _paged(client, DATASET, PRICE_QUERY, sleep_s):
        price_rows.extend(batch)
    (target / PRICE_FILE).write_text(
        json.dumps(price_rows, ensure_ascii=False, indent=0) + "\n", encoding="utf-8"
    )

    main_rows: list[dict[str, Any]] = []
    for batch in _paged(client, DATASET, SAMPLE_MAIN_QUERY, sleep_s):
        main_rows.extend(batch)
    fuel_rows: list[dict[str, Any]] = []
    for batch in _paged(client, FUEL_DATASET, SAMPLE_FUEL_QUERY, sleep_s):
        fuel_rows.extend(batch)
    hist = sample_histograms(main_rows, fuel_rows)
    (target / SAMPLE_FILE).write_text(json.dumps(hist, ensure_ascii=False) + "\n", encoding="utf-8")
    joined = sum(1 for _ in _joined_plates(main_rows, fuel_rows))

    c.write_fetch_meta(
        target,
        {
            "url": f"{BASE_URL}/resource/{DATASET}.json",
            "query": QUERY,
            **main_meta,
            "fuel_dataset": {"url": f"{BASE_URL}/resource/{FUEL_DATASET}.json", **fuel_meta},
            "price_query": PRICE_QUERY,
            "sample_main_query": SAMPLE_MAIN_QUERY,
            "sample_fuel_query": SAMPLE_FUEL_QUERY,
            "pages": pages,
            "rows": rows,
            "price_groups": len(price_rows),
            "sample": {
                "main_rows": len(main_rows),
                "fuel_rows": len(fuel_rows),
                "joined_plates": joined,
                "groups": len(hist),
                "note": "Plates are joined in memory and never stored; only histograms.",
            },
        },
    )
    return rows


def _joined_plates(
    main_rows: list[dict[str, Any]], fuel_rows: list[dict[str, Any]]
) -> Iterator[dict[str, Any]]:
    plates = {str(r.get("kenteken")) for r in fuel_rows}
    return (r for r in main_rows if str(r.get("kenteken")) in plates)


# --- statistics -------------------------------------------------------------------------


def weighted_quantile(hist: list[tuple[float, int]], q: float) -> float:
    """Quantile of a sorted (value, count) histogram, linear interpolation (numpy default)."""
    total = sum(n for _, n in hist)
    if total <= 0:
        raise ValueError("empty histogram")
    pos = q * (total - 1)
    lo_i, frac = int(pos), pos - int(pos)

    def at(i: int) -> float:
        seen = 0
        for v, n in hist:
            seen += n
            if i < seen:
                return v
        return hist[-1][0]

    lo = at(lo_i)
    return lo if frac == 0 else lo + (at(lo_i + 1) - lo) * frac


@dataclass
class Spread:
    n: int
    median: float
    q1: float
    q3: float

    @property
    def iqr_ratio(self) -> float:
        return (self.q3 - self.q1) / self.median if self.median else float("inf")


def spread_of(hist: list[tuple[float, int]]) -> Spread | None:
    n = sum(c for _, c in hist)
    if n == 0:
        return None
    return Spread(
        n=n,
        median=weighted_quantile(hist, 0.5),
        q1=weighted_quantile(hist, 0.25),
        q3=weighted_quantile(hist, 0.75),
    )


@dataclass
class Drops:
    """Why fields were not emitted, per field (counted in the run log)."""

    wide: Counter[str] = field(default_factory=Counter)
    small: Counter[str] = field(default_factory=Counter)
    examples: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))

    def add(self, reason: str, fname: str, what: str) -> None:
        (self.wide if reason == "wide" else self.small)[fname] += 1
        if len(self.examples[f"{reason}:{fname}"]) < 10:
            self.examples[f"{reason}:{fname}"].append(what)


# --- normalise --------------------------------------------------------------------------


def _key(dataset: str, make: str, model: str, year: int | None) -> str:
    return f"{dataset}[{GROUPING}]:{make}|{model}|{year or ''}"


def _year(v: object) -> int | None:
    return int(v) if v not in (None, "") else None  # type: ignore[call-overload]


def count_records(raw_dir: Path, retrieved_at: date) -> list[SourceRecord]:
    records: list[SourceRecord] = []
    for page in sorted(raw_dir.glob("page-*.json")):
        for row in json.loads(page.read_text(encoding="utf-8")):
            make, model = row.get("merk"), row.get("handelsbenaming")
            count = int(row.get("n", 0))
            if not make or not model or count <= 0:
                continue  # rows without make or trade name cannot be matched
            year = _year(row.get("jaar"))
            records.append(
                SourceRecord(
                    source=SOURCE,
                    record_key=f"{DATASET}:{make}|{model}|{year or ''}",
                    kind="registration_count",
                    make=make,
                    model=model,
                    year=year,
                    country=Country.NL,
                    specs={FactField.registered_count: SpecValue(value=count, unit="count")},
                    retrieved_at=retrieved_at,
                    confidence=Confidence.high,
                )
            )
    return records


def _hist(entry: dict[str, Any], col: str) -> list[tuple[float, int]]:
    return [(float(v), int(n)) for v, n in entry.get(col) or []]


def spec_records(
    raw_dir: Path, retrieved_at: date, drops: Drops | None = None
) -> list[SourceRecord]:
    """WLTP (plate sample) and NL price (server-side median) records, spread-checked."""
    drops = drops if drops is not None else Drops()
    sample_path, price_path = raw_dir / SAMPLE_FILE, raw_dir / PRICE_FILE
    sample = json.loads(sample_path.read_text(encoding="utf-8")) if sample_path.exists() else []
    prices = json.loads(price_path.read_text(encoding="utf-8")) if price_path.exists() else []
    by_group = {(e["merk"], e["handelsbenaming"], str(e.get("jaar") or "")): e for e in sample}
    out: list[SourceRecord] = []

    def rec(source: Source, key: str, make: str, model: str, year: int | None, **kw: Any):
        return SourceRecord(
            source=source,
            record_key=key,
            kind="spec",
            make=make,
            model=model,
            year=year,
            retrieved_at=retrieved_at,
            confidence=Confidence.medium,
            **kw,
        )

    # WLTP: median of the plate sample, one record per field (its own sample count).
    for (make, model, jaar), entry in sorted(by_group.items()):
        year = _year(jaar)
        what = f"{make}|{model}|{jaar}"
        for col, fact, unit, conv in (
            ("range_km", FactField.wltp_range_km, "km", lambda x: round(x)),
            ("wh_km", FactField.consumption_kwh_100km, "kWh/100km", lambda x: round(x / 10, 2)),
        ):
            hist = _hist(entry, col)
            if not hist:
                continue  # no WLTP value in the sample (NEDC-era cars): nothing to judge
            s = spread_of(hist)
            assert s is not None
            if s.n < MIN_SAMPLE:
                drops.add("small", fact.value, f"{what} n={s.n}")
                continue
            if s.iqr_ratio > MAX_IQR_RATIO:
                drops.add(
                    "wide", fact.value, f"{what} n={s.n} q1={s.q1:g} med={s.median:g} q3={s.q3:g}"
                )
                continue
            out.append(
                rec(
                    FUEL_SOURCE,
                    f"{_key(FUEL_DATASET + '+' + DATASET, make, model, year)}#{fact.value}",
                    make,
                    model,
                    year,
                    specs={
                        fact: SpecValue(value=conv(s.median), unit=unit),
                        # The weight: sampled cars behind the median (not a fleet count).
                        FactField.registered_count: SpecValue(value=s.n, unit="count"),
                    },
                )
            )

    # Price: exact server-side median and count; spread from the sample (or full min/max).
    for row in prices:
        make, model = row.get("merk"), row.get("handelsbenaming")
        n, med = int(row.get("n") or 0), _num(row.get("med"))
        if not make or not model or n <= 0 or med is None:
            continue
        jaar = str(row.get("jaar") or "")
        year, what = _year(jaar), f"{make}|{model}|{jaar}"
        mn, mx = _num(row.get("mn")), _num(row.get("mx"))
        narrow_full = mn is not None and mx is not None and (mx - mn) / med <= MAX_IQR_RATIO
        s = spread_of(_hist(by_group.get((make, model, jaar), {}), "price_eur"))
        if n < MIN_SAMPLE:  # a handful of cars is not a catalogue price for the group
            drops.add("small", "price_new", f"{what} n={n} sample={s.n if s else 0}")
            continue
        if not narrow_full:
            if s is None or s.n < MIN_SAMPLE:
                drops.add("small", "price_new", f"{what} n={n} sample={s.n if s else 0}")
                continue
            if s.iqr_ratio > MAX_IQR_RATIO:
                drops.add(
                    "wide",
                    "price_new",
                    f"{what} n={n} sample={s.n} q1={s.q1:g} med={s.median:g} q3={s.q3:g}",
                )
                continue
        out.append(
            rec(
                SOURCE,
                f"{_key(DATASET, make, model, year)}#price_new:NL",
                make,
                model,
                year,
                country=Country.NL,
                specs={
                    FactField.price_new: SpecValue(value=round(med), unit="EUR"),
                    FactField.registered_count: SpecValue(value=n, unit="count"),
                },
            )
        )
    return out


def normalise(raw_dir: Path, retrieved_at: date, drops: Drops | None = None) -> list[SourceRecord]:
    return count_records(raw_dir, retrieved_at) + spec_records(raw_dir, retrieved_at, drops)


# --- commands ---------------------------------------------------------------------------


def fetch_cmd(client: httpx.Client | None = None) -> int:
    target = c.raw_dir(NAME)
    own = client is None
    client = client or net.safe_client(NAME, timeout=120)
    try:
        rows = fetch(client, target)
    except httpx.HTTPError as exc:
        print(f"fetch {NAME}: failed: {exc}")
        return 1
    finally:
        if own:
            client.close()
    meta = c.read_fetch_meta(target)
    c.log_step(
        step="fetch",
        source=NAME,
        input_=f"{BASE_URL}/resource/{DATASET}.json + {FUEL_DATASET}.json (grouped SoQL "
        "+ 10% plate sample, joined in memory)",
        output=c.rel(target),
        rows_out=rows,
        price_groups=meta.get("price_groups"),
        sample=meta.get("sample"),
    )
    return 0


def normalise_cmd(from_fixtures: bool) -> int:
    src = c.FIXTURES_DIR / NAME if from_fixtures else c.raw_dir(NAME)
    if not any(src.glob("page-*.json")):
        print(f"normalise {NAME}: no data in {src} (run `ev fetch {NAME}` first)")
        return 1
    drops = Drops()
    records = normalise(src, c.retrieved_at_for(src), drops)
    out = c.staging_dir() / f"{NAME}.records.jsonl"
    rows = c.write_records(records, out)
    counts = [r for r in records if r.kind == "registration_count"]
    emitted: Counter[str] = Counter()
    for r in records:
        if r.kind == "spec":
            emitted.update(f.value for f in r.specs if f != FactField.registered_count)
    c.log_step(
        step="normalise",
        source=NAME,
        input_=c.rel(src),
        output=c.rel(out),
        rows_out=rows,
        from_fixtures=from_fixtures,
        count_records=len(counts),
        registered_total=sum(int(r.specs[FactField.registered_count].value) for r in counts),
        spec_fields_emitted=dict(emitted),
        dropped_wide_spread=dict(drops.wide),
        dropped_small_sample=dict(drops.small),
        drop_rule=f"IQR > {MAX_IQR_RATIO:.0%} of median, or sample < {MIN_SAMPLE}",
        drop_examples=dict(drops.examples),
    )
    return 0
