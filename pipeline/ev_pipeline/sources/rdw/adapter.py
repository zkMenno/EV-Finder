"""RDW Open Data adapter (CC0-1.0): battery-electric passenger cars in NL.

Outputs, first per make (`merk`) x trade name (`handelsbenaming`) x year of first admission
(`jaar`, from `datum_eerste_toelating_dt`), the "coarse" group. The grouping is written into
every record_key as `[merk|handelsbenaming|jaar]`.

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
in the group are not represented. Socrata has `median()` but no percentile function, so the
IQR has to come from the sample.

**Finer split by type-approval codes (T-054).** A coarse group that is too wide for a field
is split by the type-approval codes of `m9d7-ebf2`: first `type` + `variant`
(`[merk|handelsbenaming|jaar|type|variant]`), and a sub-group that is still too wide by
`uitvoering` as well (`[...|variant|uitvoering]`). Price at both levels is again a
server-side median/count/min/max (two more grouped queries); WLTP comes from the same plate
sample, whose histograms are now kept per finest group (with the codes) and summed upwards.
The spread rules are the same at every level. **No double counting:** for each field, a car
is behind at most one emitted record: the coarse record when the coarse group passes,
otherwise the finest passing sub-group that holds it (a `variant` group that passes is not
split further). Small sub-groups are dropped and counted; their cars stay unpriced.

The codes are RDW's, not ours, and we keep **no code -> variant table**. A fine record holds,
for the attach-only matcher (matcher.py rule 9), all fields that passed at that level in one
record (so a price record carries its WLTP km when that passed too) and, as evidence only,
the group's median electric power (`netto_max_vermogen_elektrisch`, kW, fuel table) written
as `variant_name` "<kW> kW" when its spread passes too. Power is never emitted as a fact:
for some dual-motor cars RDW lists one motor (Tesla Model 3 AWD: 158 kW). `registered_count`
on a fine record is the price count when the record holds a price, else the sampled cars
behind its WLTP values.
"""

from __future__ import annotations

import json
import time
from collections import Counter, defaultdict
from collections.abc import Callable, Iterator
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
CODE_COLUMNS = ("type", "variant", "uitvoering")
# Fine levels: name -> how many of CODE_COLUMNS the group adds to the coarse group.
LEVELS = {"variant": 2, "uitvoering": 3}
MAX_IQR_RATIO = 0.05
MIN_SAMPLE = 5

PRICE_FILE = "price-000.json"
PRICE_FILES = {"variant": "price-variant.json", "uitvoering": "price-uitvoering.json"}
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
_PRICE_STATS = (
    "count(catalogusprijs) AS n, median(catalogusprijs) AS med, "
    "min(catalogusprijs) AS mn, max(catalogusprijs) AS mx"
)
_PRICE_WHERE = f"{BEV_WHERE} AND {NEW_IN_NL} AND catalogusprijs > 0"
PRICE_QUERY = {
    "$select": f"merk, handelsbenaming, {JAAR}, {_PRICE_STATS}",
    "$where": _PRICE_WHERE,
    "$group": "merk, handelsbenaming, jaar",
    "$order": "merk, handelsbenaming, jaar",
}


def _fine_price_query(level: str) -> dict[str, str]:
    cols = ", ".join(CODE_COLUMNS[: LEVELS[level]])
    return {
        "$select": f"merk, handelsbenaming, {JAAR}, {cols}, {_PRICE_STATS}",
        "$where": _PRICE_WHERE,
        "$group": f"merk, handelsbenaming, jaar, {cols}",
        "$order": f"merk, handelsbenaming, jaar, {cols}",
    }


PRICE_FINE_QUERIES = {level: _fine_price_query(level) for level in LEVELS}
SAMPLE_MAIN_QUERY = {
    "$select": f"kenteken, merk, handelsbenaming, {JAAR}, type, variant, uitvoering, "
    f"catalogusprijs, {NEW_IN_NL} AS nieuw_nl",
    "$where": f"{BEV_WHERE} AND {SAMPLE_WHERE}",
    "$order": "kenteken",
}
SAMPLE_FUEL_QUERY = {
    "$select": "kenteken, actie_radius_enkel_elektrisch_wltp AS range_km, "
    "elektrisch_verbruik_enkel_elektrisch_wltp AS wh_km, netto_max_vermogen_elektrisch AS kw",
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

HIST_COLS = ("range_km", "wh_km", "price_eur", "kw")


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


def _code(v: object) -> str:
    return "" if v is None else str(v).strip()


def sample_histograms(
    main_rows: list[dict[str, Any]], fuel_rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Join the plate sample in memory; return histograms per finest group (no plates).

    One entry per merk x handelsbenaming x jaar x type x variant x uitvoering; coarser
    groups are sums of these (see `_rollup`).
    """
    fuel: dict[str, dict[str, Any]] = {}
    for row in fuel_rows:
        fuel.setdefault(str(row.get("kenteken")), row)  # one Elektriciteit row per BEV
    groups: dict[tuple[str, ...], dict[str, Any]] = {}
    for row in main_rows:
        make, model, jaar = row.get("merk"), row.get("handelsbenaming"), row.get("jaar")
        if not make or not model:
            continue
        codes = tuple(_code(row.get(col)) for col in CODE_COLUMNS)
        g = groups.setdefault(
            (make, model, str(jaar or ""), *codes),
            {"n": 0, **{col: Counter() for col in HIST_COLS}},
        )
        g["n"] += 1
        price = _num(row.get("catalogusprijs"))
        if price is not None and row.get("nieuw_nl") in (True, "true"):
            g["price_eur"][_value_key(price)] += 1
        f = fuel.get(str(row.get("kenteken")))
        if f is None:
            continue
        for col in ("range_km", "wh_km", "kw"):
            v = _num(f.get(col))
            if v is not None:
                g[col][_value_key(v)] += 1
    out = []
    for (make, model, jaar, *codes), g in sorted(groups.items()):
        entry: dict[str, Any] = {"merk": make, "handelsbenaming": model, "jaar": jaar}
        entry.update(zip(CODE_COLUMNS, codes, strict=True))
        entry["n"] = g["n"]
        for col in HIST_COLS:
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


# Queries whose output the raw folder holds: if one changed since the last fetch, the raw data
# no longer matches the code even when RDW's tables did not change.
_FETCH_QUERIES = {
    "query": QUERY,
    "price_query": PRICE_QUERY,
    "price_variant_query": PRICE_FINE_QUERIES["variant"],
    "price_uitvoering_query": PRICE_FINE_QUERIES["uitvoering"],
    "sample_main_query": SAMPLE_MAIN_QUERY,
    "sample_fuel_query": SAMPLE_FUEL_QUERY,
}


def probe_unchanged(client: httpx.Client, previous_fetch_meta: dict[str, Any]) -> bool | None:
    """`ev refresh` hook: did RDW change since the last fetch? Two metadata calls instead of
    the ~5-minute paged refetch.

    True (unchanged) only when both datasets' `rowsUpdatedAt` (Socrata view metadata) and
    licence metadata equal what the last fetch recorded and our queries are the same. False
    when any of those moved. None (unknown, so the runner fetches) when the previous fetch
    did not record them or the metadata call fails.
    """
    prev_fuel = previous_fetch_meta.get("fuel_dataset") or {}
    before = {
        DATASET: previous_fetch_meta.get("dataset_rows_updated_at"),
        FUEL_DATASET: prev_fuel.get("dataset_rows_updated_at"),
    }
    if any(v in (None, "") for v in before.values()):
        return None
    if any(previous_fetch_meta.get(k) != q for k, q in _FETCH_QUERIES.items()):
        return False
    licences = {
        DATASET: previous_fetch_meta.get("licence_metadata"),
        FUEL_DATASET: prev_fuel.get("licence_metadata"),
    }
    try:
        for dataset in (DATASET, FUEL_DATASET):
            now = _view_meta(client, dataset)
            if now["dataset_rows_updated_at"] in (None, ""):
                return None
            if str(now["dataset_rows_updated_at"]) != str(before[dataset]):
                return False
            if licences[dataset] is not None and now["licence_metadata"] != licences[dataset]:
                return False
    except (httpx.HTTPError, ValueError):
        return None
    return True


def _write_json(path: Path, rows: list[dict[str, Any]], indent: int | None = 0) -> None:
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=indent) + "\n", encoding="utf-8")


def fetch(client: httpx.Client, target: Path, sleep_s: float = PAGE_SLEEP_S) -> int:
    """Fetch licence metadata, counts, price stats (coarse + per type-approval code) and the
    WLTP plate sample into `target`.

    Returns the number of count rows (the fleet table), as before.
    """
    main_meta = _view_meta(client, DATASET)
    fuel_meta = _view_meta(client, FUEL_DATASET)

    target.mkdir(parents=True, exist_ok=True)
    stale = [target / PRICE_FILE, target / SAMPLE_FILE, *(target / f for f in PRICE_FILES.values())]
    for old in [*target.glob("page-*.json"), *stale]:
        old.unlink(missing_ok=True)

    rows = pages = 0
    for batch in _paged(client, DATASET, QUERY, sleep_s):
        _write_json(target / f"page-{pages:03d}.json", batch)
        rows += len(batch)
        pages += 1

    price_counts: dict[str, int] = {}
    for name, query, path in (
        ("coarse", PRICE_QUERY, PRICE_FILE),
        *((lvl, PRICE_FINE_QUERIES[lvl], PRICE_FILES[lvl]) for lvl in LEVELS),
    ):
        if sleep_s:
            time.sleep(sleep_s)  # fair use between queries too
        price_rows: list[dict[str, Any]] = []
        for batch in _paged(client, DATASET, query, sleep_s):
            price_rows.extend(batch)
        _write_json(target / path, price_rows)
        price_counts[name] = len(price_rows)

    main_rows: list[dict[str, Any]] = []
    for batch in _paged(client, DATASET, SAMPLE_MAIN_QUERY, sleep_s):
        main_rows.extend(batch)
    fuel_rows: list[dict[str, Any]] = []
    for batch in _paged(client, FUEL_DATASET, SAMPLE_FUEL_QUERY, sleep_s):
        fuel_rows.extend(batch)
    hist = sample_histograms(main_rows, fuel_rows)
    _write_json(target / SAMPLE_FILE, hist, indent=None)
    joined = sum(1 for _ in _joined_plates(main_rows, fuel_rows))

    c.write_fetch_meta(
        target,
        {
            "url": f"{BASE_URL}/resource/{DATASET}.json",
            "query": QUERY,
            **main_meta,
            "fuel_dataset": {"url": f"{BASE_URL}/resource/{FUEL_DATASET}.json", **fuel_meta},
            **{k: q for k, q in _FETCH_QUERIES.items() if k != "query"},
            "pages": pages,
            "rows": rows,
            "price_groups": price_counts["coarse"],
            "price_groups_variant": price_counts["variant"],
            "price_groups_uitvoering": price_counts["uitvoering"],
            "sample": {
                "main_rows": len(main_rows),
                "fuel_rows": len(fuel_rows),
                "joined_plates": joined,
                "groups": len({(e["merk"], e["handelsbenaming"], e["jaar"]) for e in hist}),
                "fine_groups": len(hist),
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
    """Why fields were not emitted, per field (counted in the run log).

    `wide` / `small` are the coarse groups (as before T-054: a wide coarse group may still be
    recovered by the finer split). The fine split has its own counters, keyed
    "<level>:<field>": `fine_kept` / `fine_wide` / `fine_small` sub-groups, and `recovered`
    per field: wide coarse groups with at least one fine record.
    """

    wide: Counter[str] = field(default_factory=Counter)
    small: Counter[str] = field(default_factory=Counter)
    examples: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    fine_kept: Counter[str] = field(default_factory=Counter)
    fine_wide: Counter[str] = field(default_factory=Counter)
    fine_small: Counter[str] = field(default_factory=Counter)
    recovered: Counter[str] = field(default_factory=Counter)

    def add(self, reason: str, fname: str, what: str, level: str = "") -> None:
        if level:
            (self.fine_wide if reason == "wide" else self.fine_small)[f"{level}:{fname}"] += 1
            tag = f"{level}-{reason}:{fname}"
        else:
            (self.wide if reason == "wide" else self.small)[fname] += 1
            tag = f"{reason}:{fname}"
        if len(self.examples[tag]) < 10:
            self.examples[tag].append(what)


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


Hist = list[tuple[float, int]]
GroupKey = tuple[str, ...]  # (merk, handelsbenaming, jaar, *codes)


def _hist(entry: dict[str, Any], col: str) -> Hist:
    return [(float(v), int(n)) for v, n in entry.get(col) or []]


def _rollup(sample: list[dict[str, Any]], depth: int) -> dict[GroupKey, dict[str, Hist]]:
    """Sum the finest-group histograms to groups of the first `depth` code columns."""
    acc: dict[GroupKey, dict[str, Counter[float]]] = {}
    for e in sample:
        k = (
            str(e["merk"]),
            str(e["handelsbenaming"]),
            str(e.get("jaar") or ""),
            *(_code(e.get(col)) for col in CODE_COLUMNS[:depth]),
        )
        g = acc.setdefault(k, {col: Counter() for col in HIST_COLS})
        for col in HIST_COLS:
            for v, n in _hist(e, col):
                g[col][v] += n
    return {k: {col: sorted(g[col].items()) for col in HIST_COLS} for k, g in acc.items()}


def _price_rows(path: Path, depth: int) -> dict[GroupKey, dict[str, Any]]:
    if not path.exists():
        return {}
    out: dict[GroupKey, dict[str, Any]] = {}
    for row in json.loads(path.read_text(encoding="utf-8")):
        make, model = row.get("merk"), row.get("handelsbenaming")
        if not make or not model:
            continue
        k = (
            str(make),
            str(model),
            str(row.get("jaar") or ""),
            *(_code(row.get(col)) for col in CODE_COLUMNS[:depth]),
        )
        out[k] = row
    return out


@dataclass
class Verdict:
    """One field of one group: `value` (converted) and its weight, or why it was dropped."""

    ok: bool
    reason: str = ""  # "wide" | "small" | "" (nothing to judge)
    value: float | int | None = None
    n: int = 0
    detail: str = ""


_WLTP_FIELDS: dict[str, tuple[FactField, str, Callable[[float], float | int]]] = {
    "range_km": (FactField.wltp_range_km, "km", lambda x: round(x)),
    "wh_km": (FactField.consumption_kwh_100km, "kWh/100km", lambda x: round(x / 10, 2)),
}
FIELD_OF_COL = {"range_km": "wltp_range_km", "wh_km": "consumption_kwh_100km", "price": "price_new"}


def judge_sample(hist: Hist, conv: Callable[[float], float | int] = float) -> Verdict:
    """The spread rule on a plate-sample histogram (WLTP fields and power evidence)."""
    if not hist:
        return Verdict(False)  # no value in the sample (NEDC-era cars): nothing to judge
    s = spread_of(hist)
    assert s is not None
    if s.n < MIN_SAMPLE:
        return Verdict(False, "small", n=s.n, detail=f"n={s.n}")
    if s.iqr_ratio > MAX_IQR_RATIO:
        detail = f"n={s.n} q1={s.q1:g} med={s.median:g} q3={s.q3:g}"
        return Verdict(False, "wide", n=s.n, detail=detail)
    return Verdict(True, value=conv(s.median), n=s.n)


def judge_price(row: dict[str, Any] | None, sample_hist: Hist) -> Verdict:
    """The spread rule on a server-side price row, with the sample histogram for the IQR."""
    if row is None:
        return Verdict(False)
    n, med = int(row.get("n") or 0), _num(row.get("med"))
    if n <= 0 or med is None:
        return Verdict(False)
    mn, mx = _num(row.get("mn")), _num(row.get("mx"))
    narrow_full = mn is not None and mx is not None and (mx - mn) / med <= MAX_IQR_RATIO
    s = spread_of(sample_hist)
    sn = s.n if s else 0
    if n < MIN_SAMPLE:  # a handful of cars is not a catalogue price for the group
        return Verdict(False, "small", n=n, detail=f"n={n} sample={sn}")
    if not narrow_full:
        if s is None or s.n < MIN_SAMPLE:
            return Verdict(False, "small", n=n, detail=f"n={n} sample={sn}")
        if s.iqr_ratio > MAX_IQR_RATIO:
            detail = f"n={n} sample={s.n} q1={s.q1:g} med={s.median:g} q3={s.q3:g}"
            return Verdict(False, "wide", n=n, detail=detail)
    return Verdict(True, value=round(med), n=n)


def _what(k: GroupKey) -> str:
    return "|".join(k)


def spec_records(
    raw_dir: Path, retrieved_at: date, drops: Drops | None = None
) -> list[SourceRecord]:
    """WLTP (plate sample) and NL price (server-side median) records, spread-checked; wide
    coarse groups split by type-approval codes (see module docstring)."""
    drops = drops if drops is not None else Drops()
    sample_path = raw_dir / SAMPLE_FILE
    sample = json.loads(sample_path.read_text(encoding="utf-8")) if sample_path.exists() else []
    hists: dict[GroupKey, dict[str, Hist]] = {}
    for depth in (0, *LEVELS.values()):
        hists.update(_rollup(sample, depth))
    prices: dict[GroupKey, dict[str, Any]] = _price_rows(raw_dir / PRICE_FILE, 0)
    for level, depth in LEVELS.items():
        prices.update(_price_rows(raw_dir / PRICE_FILES[level], depth))
    empty: dict[str, Hist] = {col: [] for col in HIST_COLS}

    def judge(col: str, k: GroupKey) -> Verdict:
        h = hists.get(k, empty)
        if col == "price":
            return judge_price(prices.get(k), h["price_eur"])
        return judge_sample(h[col], _WLTP_FIELDS[col][2])

    out: list[SourceRecord] = []

    def rec(source: Source, key: str, k: GroupKey, **kw: Any) -> SourceRecord:
        return SourceRecord(
            source=source,
            record_key=key,
            kind="spec",
            make=k[0],
            model=k[1],
            year=_year(k[2]),
            retrieved_at=retrieved_at,
            confidence=Confidence.medium,
            **kw,
        )

    coarse_keys = sorted({k for k in hists if len(k) == 3} | {k for k in prices if len(k) == 3})
    # fine group -> {col: verdict} of the fields emitted at that group
    fine: dict[GroupKey, dict[str, Verdict]] = defaultdict(dict)

    pool = hists.keys() | prices.keys()
    by_parent: dict[GroupKey, list[GroupKey]] = defaultdict(list)
    for g in sorted(pool):
        if len(g) == 3 + LEVELS["variant"]:
            by_parent[g[:3]].append(g)  # coarse -> its type + variant groups
        elif len(g) == 3 + LEVELS["uitvoering"]:
            by_parent[g[:-1]].append(g)  # type + variant -> its uitvoering groups

    def split(col: str, parent: GroupKey, fname: str, level: str = "variant") -> bool:
        """Emit the finest passing sub-groups of a wide group; True if any was kept.

        A parent with a single sub-group holds the same cars, so that sub-group is not
        judged again: the split goes one level deeper (or ends at the last level)."""
        kids = by_parent.get(parent, [])
        deeper = "uitvoering" if level == "variant" else None
        if len(kids) <= 1:
            return bool(kids) and deeper is not None and split(col, kids[0], fname, deeper)
        kept = False
        for kid in kids:
            v = judge(col, kid)
            if v.ok:
                fine[kid][col] = v
                drops.fine_kept[f"{level}:{fname}"] += 1
                kept = True
                continue
            if v.reason == "wide" and deeper is not None and len(by_parent.get(kid, [])) > 1:
                kept = split(col, kid, fname, deeper) or kept  # the deeper level counts drops
            elif v.reason:
                drops.add(v.reason, fname, f"{_what(kid)} {v.detail}", level)
        return kept

    for k in coarse_keys:
        year = _year(k[2])
        for col in ("range_km", "wh_km", "price"):
            fname = FIELD_OF_COL[col]
            v = judge(col, k)
            if v.reason:
                drops.add(v.reason, fname, f"{_what(k)} {v.detail}")
            if v.reason == "wide" and split(col, k, fname):
                drops.recovered[fname] += 1
            if not v.ok:
                continue
            if col == "price":
                out.append(
                    rec(
                        SOURCE,
                        f"{_key(DATASET, k[0], k[1], year)}#price_new:NL",
                        k,
                        country=Country.NL,
                        specs={
                            FactField.price_new: SpecValue(value=v.value, unit="EUR"),  # type: ignore[arg-type]
                            FactField.registered_count: SpecValue(value=v.n, unit="count"),
                        },
                    )
                )
            else:
                fact, unit, _ = _WLTP_FIELDS[col]
                out.append(
                    rec(
                        FUEL_SOURCE,
                        f"{_key(FUEL_DATASET + '+' + DATASET, k[0], k[1], year)}#{fact.value}",
                        k,
                        specs={
                            fact: SpecValue(value=v.value, unit=unit),  # type: ignore[arg-type]
                            # The weight: sampled cars behind the median (not a fleet count).
                            FactField.registered_count: SpecValue(value=v.n, unit="count"),
                        },
                    )
                )

    for k, fields in sorted(fine.items()):
        out.append(_fine_record(k, fields, hists.get(k, empty), rec))
    return out


def fine_grouping(depth: int) -> str:
    return "|".join([GROUPING, *CODE_COLUMNS[:depth]])


def _fine_record(
    k: GroupKey,
    fields: dict[str, Verdict],
    hist: dict[str, Hist],
    rec: Callable[..., SourceRecord],
) -> SourceRecord:
    """One record per fine group: every field that passed there, plus power evidence."""
    specs: dict[FactField, SpecValue] = {}
    for col in ("range_km", "wh_km"):
        if col in fields:
            fact, unit, _ = _WLTP_FIELDS[col]
            specs[fact] = SpecValue(value=fields[col].value, unit=unit)  # type: ignore[arg-type]
    if "price" in fields:
        specs[FactField.price_new] = SpecValue(value=fields["price"].value, unit="EUR")  # type: ignore[arg-type]
        weight = fields["price"].n
    else:
        weight = max(v.n for v in fields.values())
    specs[FactField.registered_count] = SpecValue(value=weight, unit="count")
    power = judge_sample(hist.get("kw", []), lambda x: round(x))
    depth = len(k) - 3
    return rec(
        SOURCE if "price" in fields else FUEL_SOURCE,
        f"{DATASET}+{FUEL_DATASET}[{fine_grouping(depth)}]:{_what(k)}",
        k,
        # Evidence for the attach-only matcher (kW in the name), never a power_kw fact.
        variant_name=f"{power.value} kW" if power.ok else None,
        country=Country.NL if "price" in fields else None,
        specs=specs,
    )


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
        price_groups_variant=meta.get("price_groups_variant"),
        price_groups_uitvoering=meta.get("price_groups_uitvoering"),
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
    emitted_fine: Counter[str] = Counter()
    for r in records:
        if r.kind == "spec":
            fields = [f.value for f in r.specs if f != FactField.registered_count]
            emitted.update(fields)
            if "|type|" in r.record_key:
                emitted_fine.update(fields)
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
        spec_fields_emitted_fine=dict(emitted_fine),
        dropped_wide_spread=dict(drops.wide),
        dropped_small_sample=dict(drops.small),
        wide_recovered_by_split=dict(drops.recovered),
        fine_kept=dict(drops.fine_kept),
        fine_dropped_wide=dict(drops.fine_wide),
        fine_dropped_small=dict(drops.fine_small),
        drop_rule=f"IQR > {MAX_IQR_RATIO:.0%} of median, or sample < {MIN_SAMPLE}",
        split_rule="wide coarse group -> type+variant -> +uitvoering; finest passing group "
        "wins, each car behind at most one record per field",
        drop_examples=dict(drops.examples),
    )
    return 0
