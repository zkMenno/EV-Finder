"""RDW APK defects adapter (CC0-1.0): defects found at Dutch MOT (APK) on battery-electric cars.

Datasets (Socrata, opendata.rdw.nl; licence checked in each dataset's metadata on fetch):

- `a34c-vvps` Geconstateerde Gebreken: one row per plate x inspection report x defect code
  (`kenteken`, `gebrek_identificatie`, `aantal_gebreken_geconstateerd`, `meld_datum_...`,
  `soort_erkenning_keuringsinstantie`). About 24.7 million rows; reports from 2022-06 onward
  (a rolling window, so totals change as old reports fall out). No make or model.
- `hx2c-gt7k` Gebreken: the defect code list (`gebrek_omschrijving`, article number, validity).
- `m9d7-ebf2` Gekentekende voertuigen: make, trade name and first-admission date per plate.
- `vkij-7mwc` Keuringen: only `kenteken` + `vervaldatum_keuring` (APK expiry). It has no
  inspection date or result, so it can't serve as a denominator; we read its licence only.

**Why a sample.** Make and model live in another table, and Socrata refuses joins. A full
in-memory join would mean pulling millions of plates. So, as in `sources/rdw`, we take the
**deterministic 10 % plate sample** `kenteken like '___7%'` of the BEV proxy in `m9d7-ebf2`
(see sources/rdw for how the proxy was checked), keep only cars old enough to have had an
APK (first admission at least MIN_AGE_YEARS calendar years before the fetch year), and ask
`a34c-vvps` for those plates in batches (`kenteken in (...)`, grouped server-side by plate
and defect code, APK light vehicles only, `soort_erkenning_keuringsinstantie = 'AL'`).
Plates are joined in memory and **never written to disk**; fetch stores only per-group
histograms (`groups.json`).

Per make (`merk`) x trade name (`handelsbenaming`) x first-admission year (`jaar`):
`sample_cars` (sampled BEVs), `cars_with_any_defect`, and per defect code the number of
sampled cars with that defect and the number of defects found.

**Output shape.** `records.py` only allows spec/registration_count/corroboration, so this
adapter writes its own documented rows to `data/staging/rdw-defects.defects.jsonl` and leaves
integration ("Known issues" facts) to the coordinator. Two row kinds:

- `defect_group`: one per group: sample_cars, cars_with_any_defect, report window.
- `defect_count`: one per group x defect code: cars_with_defect, defects_found,
  share_of_sample (= cars_with_defect / sample_cars).

Groups with fewer than MIN_SAMPLE_CARS sampled cars are dropped; codes seen on fewer than
MIN_CARS_PER_CODE cars in a group are dropped (noise, and no tiny counts about a handful of
cars). Both drop counts go to the run log.
"""

from __future__ import annotations

import json
import re
import time
from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import httpx

from ev_pipeline import net
from ev_pipeline.sources import _common as c

NAME = "rdw-defects"
DIR = "rdw_defects"
BASE_URL = "https://opendata.rdw.nl"
MAIN = "m9d7-ebf2"
DEFECTS = "a34c-vvps"
CODES = "hx2c-gt7k"
KEURINGEN = "vkij-7mwc"
DATASETS = (MAIN, DEFECTS, CODES, KEURINGEN)

PAGE_SIZE = 5000
BATCH = 300
"""Plates per `kenteken in (...)` query (about 4 kB of URL)."""
SLEEP_S = 0.5
MIN_AGE_YEARS = 3
MIN_SAMPLE_CARS = 20
MIN_CARS_PER_CODE = 3
INSPECTION = "AL"
INSPECTION_LABEL = "APK Lichte voertuigen"
GROUPING = "merk|handelsbenaming|jaar"

GROUPS_FILE = "groups.json"
CODES_FILE = "codes.json"
OUT_SUFFIX = ".defects.jsonl"

BEV_WHERE = (
    "voertuigsoort = 'Personenauto' AND cilinderinhoud IS NULL "
    "AND datum_eerste_toelating >= 20100101"
)
SAMPLE_WHERE = "kenteken like '___7%'"
PLATE_RE = re.compile(r"^[A-Z0-9]{1,8}$")

LICENCE = "CC0-1.0"
SOURCE = {
    "id": "rdw",
    "name": "RDW Open Data: Geconstateerde Gebreken (APK defects)",
    "url": f"{BASE_URL}/d/{DEFECTS}",
    "licence": LICENCE,
    "attribution": "Bron: RDW Open Data (opendata.rdw.nl), CC0.",
}
SAMPLE_RULE = (
    f"BEV proxy ({BEV_WHERE}) AND {SAMPLE_WHERE} (deterministic ~10% plate sample), "
    f"first admission <= fetch year - {MIN_AGE_YEARS}; defects with "
    f"soort_erkenning_keuringsinstantie = '{INSPECTION}'"
)


class LicenceChanged(RuntimeError):
    pass


def main_query(max_year: int) -> dict[str, str]:
    return {
        "$select": "kenteken, merk, handelsbenaming, "
        "date_extract_y(datum_eerste_toelating_dt) AS jaar",
        "$where": f"{BEV_WHERE} AND {SAMPLE_WHERE} AND datum_eerste_toelating < {max_year + 1}0101",
        "$order": "kenteken",
    }


def defects_query(plates: list[str]) -> dict[str, str]:
    bad = [p for p in plates if not PLATE_RE.match(p)]
    if bad:
        raise ValueError(f"refusing {len(bad)} malformed plate value(s) in a SoQL list")
    in_list = ",".join(f"'{p}'" for p in plates)
    return {
        "$select": "kenteken, gebrek_identificatie, "
        "sum(aantal_gebreken_geconstateerd) AS n, "
        "min(meld_datum_door_keuringsinstantie) AS mn, "
        "max(meld_datum_door_keuringsinstantie) AS mx",
        "$where": f"soort_erkenning_keuringsinstantie = '{INSPECTION}' AND kenteken in ({in_list})",
        "$group": "kenteken, gebrek_identificatie",
        "$order": "kenteken, gebrek_identificatie",
    }


# --- fetch ------------------------------------------------------------------------------


def _get_all(
    client: httpx.Client, dataset: str, query: dict[str, str], sleep_s: float
) -> Iterator[dict[str, Any]]:
    page = 0
    while True:
        if page and sleep_s:
            time.sleep(sleep_s)
        params = {**query, "$limit": str(PAGE_SIZE), "$offset": str(page * PAGE_SIZE)}
        resp = client.get(f"{BASE_URL}/resource/{dataset}.json", params=params)
        resp.raise_for_status()
        batch = resp.json()
        yield from batch
        page += 1
        if len(batch) < PAGE_SIZE:
            return


def view_licence(client: httpx.Client, dataset: str) -> dict[str, Any]:
    resp = client.get(f"{BASE_URL}/api/views/{dataset}.json")
    resp.raise_for_status()
    view = resp.json()
    custom = view.get("metadata", {}).get("custom_fields", {}).get("Licentie", {})
    meta = {
        "dataset_name": view.get("name"),
        "dataset_rows_updated_at": view.get("rowsUpdatedAt"),
        "license": view.get("license"),
        "licenseId": view.get("licenseId"),
        "custom_fields.Licentie": custom.get("Licentie"),
    }
    if meta["licenseId"] != "PUBLIC_DOMAIN" and "CC0" not in str(meta["custom_fields.Licentie"]):
        raise LicenceChanged(f"{dataset}: licence metadata no longer says CC0 / Public Domain")
    return meta


def aggregate(
    sample_rows: Iterable[dict[str, Any]], defect_rows: Iterable[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, str | None]]:
    """Join plate sample and defect rows in memory. Returns (groups, report window).

    The result holds no plate: only counts per make x trade name x first-admission year.
    """
    plate_group: dict[str, tuple[str, str, str]] = {}
    sample: Counter[tuple[str, str, str]] = Counter()
    for row in sample_rows:
        make, model = row.get("merk"), row.get("handelsbenaming")
        if not make or not model:
            continue
        key = (str(make), str(model), str(row.get("jaar") or ""))
        plate_group[str(row.get("kenteken"))] = key
        sample[key] += 1
    per_code: dict[tuple[str, str, str], dict[str, list[int]]] = defaultdict(
        lambda: defaultdict(lambda: [0, 0])
    )
    any_defect: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    lo = hi = None
    for row in defect_rows:
        plate = str(row.get("kenteken"))
        key = plate_group.get(plate)
        code = row.get("gebrek_identificatie")
        if key is None or not code:
            continue
        n = int(float(row.get("n") or 0))
        cell = per_code[key][str(code)]
        cell[0] += 1  # one row per plate x code (grouped server-side) = one car
        cell[1] += n
        any_defect[key].add(plate)
        for v in (row.get("mn"), row.get("mx")):
            if v:
                lo = v if lo is None or v < lo else lo
                hi = v if hi is None or v > hi else hi
    groups = []
    for key in sorted(sample):
        make, model, jaar = key
        codes = sorted(
            ([code, cars, n] for code, (cars, n) in per_code.get(key, {}).items()),
            key=lambda x: (-x[1], x[0]),
        )
        groups.append(
            {
                "merk": make,
                "handelsbenaming": model,
                "jaar": jaar,
                "sample_cars": sample[key],
                "cars_with_any_defect": len(any_defect.get(key, ())),
                "codes": codes,
            }
        )
    return groups, {"from": _iso(lo), "to": _iso(hi)}


def _iso(v: str | None) -> str | None:
    if not v:
        return None
    s = str(v)
    return f"{s[:4]}-{s[4:6]}-{s[6:8]}" if len(s) == 8 and s.isdigit() else s


def _chunks(items: list[str], n: int) -> Iterator[list[str]]:
    for i in range(0, len(items), n):
        yield items[i : i + n]


def fetch(
    client: httpx.Client, target: Path, sleep_s: float = SLEEP_S, today: date | None = None
) -> int:
    """Licence check, code list, plate sample, batched defect queries. Returns group count."""
    today = today or datetime.now(UTC).date()
    licences = {ds: view_licence(client, ds) for ds in DATASETS}
    target.mkdir(parents=True, exist_ok=True)

    codes = list(_get_all(client, CODES, {"$order": "gebrek_identificatie"}, sleep_s))
    (target / CODES_FILE).write_text(
        json.dumps(codes, ensure_ascii=False, indent=0) + "\n", encoding="utf-8"
    )

    max_year = today.year - MIN_AGE_YEARS
    sample_rows = list(_get_all(client, MAIN, main_query(max_year), sleep_s))
    plates = sorted({str(r["kenteken"]) for r in sample_rows if r.get("kenteken")})

    def defect_rows() -> Iterator[dict[str, Any]]:
        for i, chunk in enumerate(_chunks(plates, BATCH)):
            if i and sleep_s:
                time.sleep(sleep_s)
            yield from _get_all(client, DEFECTS, defects_query(chunk), 0)

    defect_count = 0

    def counted() -> Iterator[dict[str, Any]]:
        nonlocal defect_count
        for row in defect_rows():
            defect_count += 1
            yield row

    groups, window = aggregate(sample_rows, counted())
    # sample_rows and plates go out of scope here: nothing per plate is written.
    (target / GROUPS_FILE).write_text(
        json.dumps(groups, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    c.write_fetch_meta(
        target,
        {
            "url": f"{BASE_URL}/resource/{DEFECTS}.json",
            "licence": LICENCE,
            "licence_metadata": licences,
            "sample_rule": SAMPLE_RULE,
            "main_query": main_query(max_year),
            "max_first_admission_year": max_year,
            "batch_size": BATCH,
            "sampled_cars": sum(g["sample_cars"] for g in groups),
            "plate_code_rows": defect_count,
            "groups": len(groups),
            "codes": len(codes),
            "report_window": window,
            "note": "Plates are joined in memory and never stored; only per-group counts.",
        },
    )
    return len(groups)


# --- normalise --------------------------------------------------------------------------


def code_table(codes: list[dict[str, Any]]) -> dict[str, dict[str, str | None]]:
    """Code -> description and article; the newest `ingangsdatum_gebrek` wins."""
    out: dict[str, tuple[str, dict[str, str | None]]] = {}
    for row in codes:
        code = row.get("gebrek_identificatie")
        if not code:
            continue
        start = str(row.get("ingangsdatum_gebrek") or "")
        entry = {
            "description": row.get("gebrek_omschrijving"),
            "article": row.get("gebrek_artikel_nummer"),
        }
        if code not in out or start >= out[code][0]:
            out[str(code)] = (start, entry)
    return {k: v for k, (_, v) in out.items()}


def normalise(
    raw_dir: Path, retrieved_at: date, drops: Counter[str] | None = None
) -> list[dict[str, Any]]:
    drops = drops if drops is not None else Counter()
    groups = json.loads((raw_dir / GROUPS_FILE).read_text(encoding="utf-8"))
    codes_path = raw_dir / CODES_FILE
    codes = (
        code_table(json.loads(codes_path.read_text(encoding="utf-8")))
        if codes_path.exists()
        else {}
    )
    meta = c.read_fetch_meta(raw_dir)
    window = meta.get("report_window") or {}
    common = {
        "source": SOURCE,
        "country": "NL",
        "inspection": f"{INSPECTION_LABEL} ({INSPECTION})",
        "reported_from": window.get("from"),
        "reported_to": window.get("to"),
        "sample_rule": meta.get("sample_rule", SAMPLE_RULE),
        "retrieved_at": retrieved_at.isoformat(),
        "confidence": "medium",
    }
    rows: list[dict[str, Any]] = []
    for g in groups:
        make, model, jaar = g["merk"], g["handelsbenaming"], str(g.get("jaar") or "")
        sample = int(g["sample_cars"])
        base_key = f"{DEFECTS}+{MAIN}[{GROUPING}]:{make}|{model}|{jaar}"
        if sample < MIN_SAMPLE_CARS:
            drops["group_small_sample"] += 1
            continue
        year = int(jaar) if jaar else None
        rows.append(
            {
                **common,
                "kind": "defect_group",
                "record_key": base_key,
                "make": make,
                "model": model,
                "year": year,
                "sample_cars": sample,
                "cars_with_any_defect": int(g["cars_with_any_defect"]),
            }
        )
        for code, cars, n in g.get("codes") or []:
            if cars < MIN_CARS_PER_CODE:
                drops["code_few_cars"] += 1
                continue
            info = codes.get(code, {})
            if not info:
                drops["code_unknown"] += 1
            rows.append(
                {
                    **common,
                    "kind": "defect_count",
                    "record_key": f"{base_key}#defect:{code}",
                    "make": make,
                    "model": model,
                    "year": year,
                    "defect_code": code,
                    "defect_description": info.get("description"),
                    "defect_article": info.get("article"),
                    "cars_with_defect": int(cars),
                    "defects_found": int(n),
                    "sample_cars": sample,
                    "share_of_sample": round(cars / sample, 4),
                }
            )
    return sorted(rows, key=lambda r: r["record_key"])


def write_rows(rows: list[dict[str, Any]], out: Path) -> int:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return len(rows)


# --- commands ---------------------------------------------------------------------------


def fetch_cmd(client: httpx.Client | None = None) -> int:
    target = c.raw_dir(DIR)
    own = client is None
    client = client or net.safe_client(NAME, timeout=120)
    try:
        groups = fetch(client, target)
    except (httpx.HTTPError, LicenceChanged, ValueError) as exc:
        print(f"fetch {NAME}: failed: {exc}")
        return 1
    finally:
        if own:
            client.close()
    meta = c.read_fetch_meta(target)
    c.log_step(
        step="fetch",
        source=NAME,
        input_=f"{BASE_URL}/resource/{DEFECTS}.json + {MAIN}.json (10% plate sample, "
        "batched in-lists, joined in memory)",
        output=c.rel(target),
        rows_out=groups,
        unit="groups",
        sampled_cars=meta.get("sampled_cars"),
        plate_code_rows=meta.get("plate_code_rows"),
        report_window=meta.get("report_window"),
    )
    return 0


def normalise_cmd(from_fixtures: bool) -> int:
    src = c.FIXTURES_DIR / DIR if from_fixtures else c.raw_dir(DIR)
    if not (src / GROUPS_FILE).exists():
        print(f"normalise {NAME}: no data in {src} (run `ev fetch {NAME}` first)")
        return 1
    drops: Counter[str] = Counter()
    rows = normalise(src, c.retrieved_at_for(src), drops)
    out = c.staging_dir() / f"{NAME}{OUT_SUFFIX}"
    n = write_rows(rows, out)
    c.log_step(
        step="normalise",
        source=NAME,
        input_=c.rel(src),
        output=c.rel(out),
        rows_out=n,
        from_fixtures=from_fixtures,
        groups=sum(1 for r in rows if r["kind"] == "defect_group"),
        defect_counts=sum(1 for r in rows if r["kind"] == "defect_count"),
        dropped=dict(drops),
        drop_rule=f"group sample < {MIN_SAMPLE_CARS} cars; code on < {MIN_CARS_PER_CODE} cars",
    )
    return 0
