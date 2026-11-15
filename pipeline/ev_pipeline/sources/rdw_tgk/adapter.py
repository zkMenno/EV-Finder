"""RDW type-approval register (TGK) adapter (CC0-1.0): per-version specs of NL BEVs (R-08 item 1).

Datasets (Socrata, opendata.rdw.nl; licence checked in each dataset's metadata on fetch):

- `m9d7-ebf2` Gekentekende voertuigen: which type approvals NL battery-electric cars carry.
  One server-side grouped query (no plates): `typegoedkeuringsnummer` (TAN, with its
  extension number, e.g. `e2*2007/46*0251*13`), `variant`, `uitvoering`, `merk`,
  `handelsbenaming`, first and last first-admission date and the car count. BEV proxy as in
  `sources/rdw` (`BEV_WHERE`).
- `gr7t-qfnb` TGK Energiebron Uitvoering: NEDC range/consumption, WLTP range/consumption
  bounds, 30-minute power, top speed. One row per TAN x variant x uitvoering x revision x
  drivetrain x energy source.
- `byxc-wwua` TGK Basis Uitvoering: length, width, height, wheelbase, mass in running order,
  empty mass, seats (lower/upper bounds), revision dates.
- `x5v3-sewk` TGK Handelsbenaming Fabrikant: the maker's trade names per version (column
  `codevariantgk`, sic: not `codevarianttgk`). Used as matcher evidence only.

The TGK rows are fetched for the TANs the NL fleet uses, in batches of BATCH TANs per
`typegoedkeuringsnummer in (...)` query, SLEEP_S apart, and filtered in memory to the
TAN|variant|uitvoering keys that NL BEV plates carry (`versions.json` + `energy.json` +
`basis.json` + `names.json` in the raw folder; no plate is ever fetched or stored).

**Record per version.** One `spec` record per TAN|variant|uitvoering, record key
`gr7t-qfnb+byxc-wwua[typegoedkeuringsnummer|variant|uitvoering|revisie]:<TAN>|<v>|<u>|<rev>`.
make / model / year come from the plate grouping: the most common `merk` and
`handelsbenaming` of the cars with that version, and the first year of first admission.
Confidence high (type-approval values; R-08 suggested medium for interpolation bounds, but
each bound is itself a stated approval value; the best/worst split makes that explicit).

**Revisions.** Values come from the newest revision (`volgnummerrevisieuitvoering`) that has
an energy row. Plates don't say which revision they were built under, so a field whose value
differs between revisions of one version is **not emitted** (counted as `revision_conflict`).

**Field rules (Decision 023).**

- `nedc_range_km` / `nedc_consumption_kwh_100km` (Wh/km / 10) from the NEDC columns. NEDC
  never fills `wltp_range_km` or `consumption_kwh_100km`. The reverse (A-05 F4): an NEDC
  range within 1 km of the version's WLTP best case is the WLTP figure copied into the NEDC
  column on a WLTP-only approval, so both NEDC fields are dropped (`drop_nedc_copy_of_wltp`,
  count `dropped_nedc_equals_wltp` in the run log). Also dropped: NEDC on a version approved
  under 2018/858 and first admitted after 2020 (`dropped_nedc_wltp_era`), which has no real
  NEDC figure.
- WLTP bounds: RDW glossary (Begrippenlijst TGK, 12 March 2024): range Ogr = "de laagste van
  alle bovengrenzen", Bgr = "de hoogste van alle ondergrenzen"; consumption Ogr = lowest
  lower bound, Bgr = highest upper bound. In the data Ogr is the best case of the
  interpolation family and Bgr the worst, but some rows are swapped, so the adapter orders
  them itself: `wltp_range_km` = max, `wltp_range_km_worst` = min; `consumption_kwh_100km`
  = min, `wltp_consumption_kwh_100km_worst` = max. Equal bounds (or one bound only) emit
  the single value and no `_worst`.
- Dimensions, seats, mass in running order: only when lower bound == upper bound (or one
  bound only). A version whose bounds differ covers several builds; no value is emitted.
- `mass_running_order_kg` from `massarijklaar*` (glossary: "massa bedrijfsklare toestand",
  i.e. EU mass in running order, incl. 75 kg driver). It never fills `weight_kg`.
- `weight_kg`: **never emitted.** The only other mass, `massaledig*`, is defined in the
  glossary as "de maximale massa leeg voertuig", which is not the kerb weight (EU kerb /
  "massa ledig voertuig" on plates is running order minus driver, with fluids). Fill rate on
  NL BEV versions is in the run log (`massaledig_filled`). See QUESTIONS.md.
- `power_30min_kw` from `maximumvermogen30min*` (glossary: "elektrisch continue vermogen"),
  only for versions with exactly one electric drivetrain row (a dual-motor car has one row
  per motor). Never a `power_kw` fact.
- `top_speed_kmh` from `maximumconstructiesnelheid*` (energy table), else the Basis
  `maxconstructiesnelheidahw*`, same equal-bound rule.
- A version with any non-electric energy row (`codeenergiebron` != 'E', e.g. fuel cell 'H')
  is skipped: not a BEV.

**Matcher evidence.** `variant_name` = the maker trade names of the version plus
"30-min <n>" and "<mass> kg". It deliberately has no "<n> kW" text: the matcher reads
"<n> kW" in a name as peak power (match/matcher.py `_KW_RE`), and 30-minute power is not
peak power. This source must be attach-only (ATTACH_ONLY_SOURCES in match/, coordinator).
"""

from __future__ import annotations

import json
import time
from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import httpx

from ev_pipeline import net
from ev_pipeline.records import SourceRecord, SpecValue
from ev_pipeline.schema_models import Confidence, FactField, Source
from ev_pipeline.sources import _common as c
from ev_pipeline.sources.rdw.adapter import BEV_WHERE

NAME = "rdw-tgk"
DIR = "rdw_tgk"
BASE_URL = "https://opendata.rdw.nl"
PLATES = "m9d7-ebf2"
ENERGY = "gr7t-qfnb"
BASIS = "byxc-wwua"
NAMES = "x5v3-sewk"
DATASETS = (PLATES, ENERGY, BASIS, NAMES)

PAGE_SIZE = 5000
BATCH = 80
"""TANs per `typegoedkeuringsnummer in (...)` query (R-08 plan: <= 80)."""
SLEEP_S = 1.0
"""Pause between requests (RDW fair use; no app token)."""

VERSIONS_FILE = "versions.json"
ENERGY_FILE = "energy.json"
BASIS_FILE = "basis.json"
NAMES_FILE = "names.json"

KEY_COLS = ("typegoedkeuringsnummer", "codevarianttgk", "codeuitvoeringtgk")
GROUPING = "typegoedkeuringsnummer|variant|uitvoering|revisie"

VERSIONS_QUERY = {
    "$select": "typegoedkeuringsnummer, variant, uitvoering, merk, handelsbenaming, "
    "min(datum_eerste_toelating) AS first, max(datum_eerste_toelating) AS last, count(*) AS n",
    "$where": f"{BEV_WHERE} AND typegoedkeuringsnummer IS NOT NULL",
    "$group": "typegoedkeuringsnummer, variant, uitvoering, merk, handelsbenaming",
    "$order": "typegoedkeuringsnummer, variant, uitvoering, merk, handelsbenaming",
}
ENERGY_COLS = (
    *KEY_COLS,
    "volgnummerrevisieuitvoering",
    "volgnummeraandrijving",
    "volgnummerenergiebron",
    "codeenergiebron",
    "elektrischeactieradiusnedc",
    "elekverbruikgecombineerdnedc",
    "actieradiusvolledigelekwltpogr",
    "actieradiusvolledigelekwltpbgr",
    "verbruikvolledigelekwltpogr",
    "verbruikvolledigelekwltpbgr",
    "maximumvermogen30minogr",
    "maximumvermogen30minbgr",
    "maximumconstructiesnelheidogr",
    "maximumconstructiesnelheidbgr",
)
BASIS_COLS = (
    *KEY_COLS,
    "volgnummerrevisieuitvoering",
    "begindatumrevisieuitvoering",
    "einddatumrevisieuitvoering",
    "voertuigcategorie",
    "lengteondergrens",
    "lengtebovengrens",
    "breedteondergrens",
    "breedtebovengrens",
    "hoogteondergrens",
    "hoogtebovengrens",
    "wielbasisondergrens",
    "wielbasisbovengrens",
    "massarijklaarondergrens",
    "massarijklaarbovengrens",
    "massaledigondergrens",
    "massaledigbovengrens",
    "aantalzitplaatsenondergrens",
    "aantalzitplaatsenbovengrens",
    "maxconstructiesnelheidahwogr",
    "maxconstructiesnelheidahwbgr",
)
NAMES_COLS = (
    "typegoedkeuringsnummer",
    "codevariantgk",
    "codeuitvoeringtgk",
    "volgnummerrevisieuitvoering",
    "handelsbenamingfabrikant",
)
_ORDER = "typegoedkeuringsnummer, codeuitvoeringtgk, volgnummerrevisieuitvoering"
TGK_QUERIES = {
    ENERGY: {
        "$select": ", ".join(ENERGY_COLS),
        "$order": f"{_ORDER}, volgnummeraandrijving, volgnummerenergiebron",
    },
    BASIS: {"$select": ", ".join(BASIS_COLS), "$order": _ORDER},
    NAMES: {
        "$select": ", ".join(NAMES_COLS),
        "$order": f"{_ORDER}, handelsbenamingfabrikant",
    },
}

ATTRIBUTION = "Bron: RDW Open Data (opendata.rdw.nl), CC0."
SOURCE = Source(
    id=NAME,
    name="RDW Open Data: type-approval register (TGK)",
    url=f"{BASE_URL}/d/{ENERGY}",
    licence="CC0-1.0",
    attribution=ATTRIBUTION,
)

# Plausibility bounds (metric). A value outside them is dropped and counted, never clamped.
PLAUSIBLE: dict[FactField, tuple[float, float]] = {
    FactField.nedc_range_km: (40, 1000),
    FactField.nedc_consumption_kwh_100km: (6, 45),
    FactField.wltp_range_km: (40, 1000),
    FactField.wltp_range_km_worst: (40, 1000),
    FactField.consumption_kwh_100km: (8, 45),
    FactField.wltp_consumption_kwh_100km_worst: (8, 45),
    FactField.length_mm: (2000, 6500),
    FactField.width_mm: (1200, 2500),
    FactField.height_mm: (1000, 2500),
    FactField.wheelbase_mm: (1500, 4000),
    FactField.mass_running_order_kg: (400, 4000),
    FactField.seats: (1, 9),
    FactField.top_speed_kmh: (40, 350),
    FactField.power_30min_kw: (3, 600),
}
UNITS: dict[FactField, str] = {
    FactField.nedc_range_km: "km",
    FactField.nedc_consumption_kwh_100km: "kWh/100km",
    FactField.wltp_range_km: "km",
    FactField.wltp_range_km_worst: "km",
    FactField.consumption_kwh_100km: "kWh/100km",
    FactField.wltp_consumption_kwh_100km_worst: "kWh/100km",
    FactField.length_mm: "mm",
    FactField.width_mm: "mm",
    FactField.height_mm: "mm",
    FactField.wheelbase_mm: "mm",
    FactField.mass_running_order_kg: "kg",
    FactField.seats: "count",
    FactField.top_speed_kmh: "km/h",
    FactField.power_30min_kw: "kW",
}


class LicenceChanged(RuntimeError):
    """A dataset's metadata no longer says CC0 / Public Domain: refuse to fetch."""


# --- fetch ------------------------------------------------------------------------------


def _rows(
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


def view_meta(client: httpx.Client, dataset: str) -> dict[str, Any]:
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


def _s(v: object) -> str:
    return "" if v is None else str(v).strip()


def soql_in(values: Iterable[str]) -> str:
    """`'a', 'b'` for a SoQL in-list; single quotes doubled."""
    return ", ".join("'" + v.replace("'", "''") + "'" for v in values)


def _version_key(row: dict[str, Any], variant_col: str = "codevarianttgk") -> tuple[str, str, str]:
    return (
        _s(row.get("typegoedkeuringsnummer")),
        _s(row.get(variant_col)),
        _s(row.get("codeuitvoeringtgk")),
    )


def fetch(client: httpx.Client, target: Path, sleep_s: float = SLEEP_S) -> int:
    """Licence metadata, the NL BEV version list and the TGK rows of those versions.

    Returns the number of NL versions (TAN|variant|uitvoering keys).
    """
    metas = {}
    for i, ds in enumerate(DATASETS):
        if i and sleep_s:
            time.sleep(sleep_s)
        metas[ds] = view_meta(client, ds)

    target.mkdir(parents=True, exist_ok=True)
    for f in (VERSIONS_FILE, ENERGY_FILE, BASIS_FILE, NAMES_FILE):
        (target / f).unlink(missing_ok=True)

    if sleep_s:
        time.sleep(sleep_s)
    versions = list(_rows(client, PLATES, VERSIONS_QUERY, sleep_s))
    keys = {
        (_s(r.get("typegoedkeuringsnummer")), _s(r.get("variant")), _s(r.get("uitvoering")))
        for r in versions
    }
    keys = {k for k in keys if k[0]}
    tans = sorted({k[0] for k in keys})

    out: dict[str, list[dict[str, Any]]] = {ENERGY: [], BASIS: [], NAMES: []}
    fetched: Counter[str] = Counter()
    requests = 0
    for start in range(0, len(tans), BATCH):
        where = f"typegoedkeuringsnummer in ({soql_in(tans[start : start + BATCH])})"
        for ds, query in TGK_QUERIES.items():
            if sleep_s:
                time.sleep(sleep_s)
            requests += 1
            vcol = "codevariantgk" if ds == NAMES else "codevarianttgk"
            for row in _rows(client, ds, {**query, "$where": where}, sleep_s):
                fetched[ds] += 1
                if _version_key(row, vcol) in keys:
                    out[ds].append(row)

    _write(target / VERSIONS_FILE, versions)
    _write(target / ENERGY_FILE, out[ENERGY])
    _write(target / BASIS_FILE, out[BASIS])
    _write(target / NAMES_FILE, out[NAMES])

    c.write_fetch_meta(
        target,
        {
            "url": f"{BASE_URL}/resource/{ENERGY}.json",
            "datasets": {
                ds: {"url": f"{BASE_URL}/resource/{ds}.json", **metas[ds]} for ds in metas
            },
            "versions_query": VERSIONS_QUERY,
            "tgk_queries": TGK_QUERIES,
            "batch_tans": BATCH,
            "version_groups": len(versions),
            "versions": len(keys),
            "tans": len(tans),
            "tgk_requests": requests,
            "tgk_rows_fetched": dict(fetched),
            "tgk_rows_kept": {ds: len(rows) for ds, rows in out.items()},
            "note": "Grouped plate query only (no plates). TGK rows kept for NL BEV versions.",
        },
    )
    return len(keys)


def _write(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")


def probe_unchanged(client: httpx.Client, previous_fetch_meta: dict[str, Any]) -> bool | None:
    """`ev refresh` hook: True when all four datasets' `rowsUpdatedAt` and licence metadata
    equal the last fetch and our queries are the same; False when one moved; None if unknown."""
    prev = previous_fetch_meta.get("datasets") or {}
    if set(prev) != set(DATASETS):
        return None
    if (
        previous_fetch_meta.get("versions_query") != VERSIONS_QUERY
        or previous_fetch_meta.get("tgk_queries") != TGK_QUERIES
        or previous_fetch_meta.get("batch_tans") != BATCH
    ):
        return False
    try:
        for ds in DATASETS:
            now = view_meta(client, ds)
            if now["dataset_rows_updated_at"] in (None, ""):
                return None
            before = prev[ds]
            if str(now["dataset_rows_updated_at"]) != str(before.get("dataset_rows_updated_at")):
                return False
            for k in ("license", "licenseId", "custom_fields.Licentie"):
                if now[k] != before.get(k):
                    return False
    except LicenceChanged:
        return False
    except (httpx.HTTPError, ValueError):
        return None
    return True


# --- normalise --------------------------------------------------------------------------

Key = tuple[str, str, str]  # (TAN, variant, uitvoering)


@dataclass
class Version:
    """NL plates behind one TAN|variant|uitvoering (from the grouped plate query)."""

    names: Counter[tuple[str, str]] = field(default_factory=Counter)  # (merk, handelsbenaming)
    first_year: int | None = None
    last_year: int | None = None
    cars: int = 0


@dataclass
class Stats:
    """Counts for the run log."""

    versions: int = 0
    no_energy_row: int = 0
    not_bev: int = 0
    emitted: Counter[str] = field(default_factory=Counter)
    revision_conflict: Counter[str] = field(default_factory=Counter)
    bounds_differ: Counter[str] = field(default_factory=Counter)
    implausible: Counter[str] = field(default_factory=Counter)
    wltp_swapped: int = 0
    nedc_equals_wltp: Counter[str] = field(default_factory=Counter)  # A-05 F4 drops per field
    nedc_wltp_era: Counter[str] = field(default_factory=Counter)  # A-05 F4: 2018/858 + 2021+
    multi_drivetrain_power_skipped: int = 0
    massaledig_filled: int = 0
    no_specs: int = 0
    cars_covered: int = 0
    cars_total: int = 0
    examples: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))

    def note(self, tag: str, what: str) -> None:
        if len(self.examples[tag]) < 10:
            self.examples[tag].append(what)


def _num(v: object) -> float | None:
    if v is None or v == "" or isinstance(v, bool):
        return None
    try:
        x = float(v)  # type: ignore[arg-type]  # Socrata sends numbers as strings
    except (TypeError, ValueError):
        return None
    return x if x > 0 else None


def _year(v: object) -> int | None:
    s = _s(v)
    return int(s[:4]) if len(s) >= 4 and s[:4].isdigit() else None


def _rev(row: dict[str, Any]) -> int:
    n = _num(row.get("volgnummerrevisieuitvoering"))
    return int(n) if n is not None else 0


def load_versions(rows: Iterable[dict[str, Any]]) -> dict[Key, Version]:
    out: dict[Key, Version] = {}
    for r in rows:
        k = (_s(r.get("typegoedkeuringsnummer")), _s(r.get("variant")), _s(r.get("uitvoering")))
        make, model = _s(r.get("merk")), _s(r.get("handelsbenaming"))
        n = int(_num(r.get("n")) or 0)
        if not k[0] or n <= 0:
            continue
        v = out.setdefault(k, Version())
        v.cars += n
        if make and model:
            v.names[(make, model)] += n
        for attr, col, pick in (("first_year", "first", min), ("last_year", "last", max)):
            y = _year(r.get(col))
            if y is not None:
                cur = getattr(v, attr)
                setattr(v, attr, y if cur is None else pick(cur, y))
    return out


def single(lo: float | None, hi: float | None) -> tuple[float | None, bool]:
    """(value, bounds_differ): the value when both bounds agree or only one is given."""
    if lo is None and hi is None:
        return None, False
    if lo is None or hi is None:
        return (lo if hi is None else hi), False
    return (lo, False) if lo == hi else (None, True)


def energy_values(rows: list[dict[str, Any]], stats: Stats) -> dict[FactField, float]:
    """Field values of one revision's electric rows (one row per drivetrain)."""
    vals: dict[FactField, float] = {}

    def agree(col: str) -> float | None:
        found = {x for r in rows if (x := _num(r.get(col))) is not None}
        return found.pop() if len(found) == 1 else None  # 2+ different values: no value

    nedc_km, nedc_wh = agree("elektrischeactieradiusnedc"), agree("elekverbruikgecombineerdnedc")
    if nedc_km is not None:
        vals[FactField.nedc_range_km] = round(nedc_km)
    if nedc_wh is not None:
        vals[FactField.nedc_consumption_kwh_100km] = round(nedc_wh / 10, 2)

    r_o, r_b = agree("actieradiusvolledigelekwltpogr"), agree("actieradiusvolledigelekwltpbgr")
    w_o, w_b = agree("verbruikvolledigelekwltpogr"), agree("verbruikvolledigelekwltpbgr")
    if r_o is not None and r_b is not None and r_o < r_b:
        stats.wltp_swapped += 1  # glossary order says Ogr is the best case; we order ourselves
    ranges = [x for x in (r_o, r_b) if x is not None]
    if ranges:
        vals[FactField.wltp_range_km] = round(max(ranges))
        if len(ranges) == 2 and min(ranges) != max(ranges):
            vals[FactField.wltp_range_km_worst] = round(min(ranges))
    cons = [x for x in (w_o, w_b) if x is not None]
    if cons:
        vals[FactField.consumption_kwh_100km] = round(min(cons) / 10, 2)
        if len(cons) == 2 and min(cons) != max(cons):
            vals[FactField.wltp_consumption_kwh_100km_worst] = round(max(cons) / 10, 2)

    if len(rows) == 1:
        p, _ = single(
            _num(rows[0].get("maximumvermogen30minogr")),
            _num(rows[0].get("maximumvermogen30minbgr")),
        )
        if p is not None:
            vals[FactField.power_30min_kw] = round(p, 1)
    elif any(_num(r.get("maximumvermogen30minogr")) for r in rows):
        stats.multi_drivetrain_power_skipped += 1  # one row per motor: no vehicle value

    speeds = {
        single(
            _num(r.get("maximumconstructiesnelheidogr")),
            _num(r.get("maximumconstructiesnelheidbgr")),
        )[0]
        for r in rows
    } - {None}
    if len(speeds) == 1:
        vals[FactField.top_speed_kmh] = round(speeds.pop())  # type: ignore[arg-type]
    return vals


NEDC_SAME_KM = 1.0
NEDC_SAME_KWH_100KM = 0.1


def drop_nedc_copy_of_wltp(vals: dict[FactField, float]) -> set[str]:
    """A-05 F4: on WLTP-only approvals RDW fills the NEDC columns with the WLTP figures. An
    NEDC range within 1 km of the version's WLTP best case is that copy, not an NEDC value:
    both NEDC fields are dropped (the consumption comes from the same filled-in row). An NEDC
    consumption within 0.1 kWh/100 km of the WLTP best case is dropped on its own too.
    Returns the dropped field names."""
    dropped: set[str] = set()
    nedc_km, wltp_km = vals.get(FactField.nedc_range_km), vals.get(FactField.wltp_range_km)
    nedc_c = vals.get(FactField.nedc_consumption_kwh_100km)
    wltp_c = vals.get(FactField.consumption_kwh_100km)
    copied_km = (
        nedc_km is not None and wltp_km is not None and abs(nedc_km - wltp_km) <= (NEDC_SAME_KM)
    )
    copied_c = (
        nedc_c is not None and wltp_c is not None and abs(nedc_c - wltp_c) <= NEDC_SAME_KWH_100KM
    )
    if copied_km:
        del vals[FactField.nedc_range_km]
        dropped.add(FactField.nedc_range_km.value)
    if nedc_c is not None and (copied_km or copied_c):
        del vals[FactField.nedc_consumption_kwh_100km]
        dropped.add(FactField.nedc_consumption_kwh_100km.value)
    return dropped


NEDC_LAST_YEAR = 2020  # NEDC figures stopped with the WLTP switch; 2018/858 types are WLTP-only
_NEDC_FIELDS = (FactField.nedc_range_km, FactField.nedc_consumption_kwh_100km)


def drop_nedc_on_wltp_era_approval(
    tan: str, first_year: int | None, vals: dict[FactField, float]
) -> list[str]:
    """A-05 F4: a version approved under Regulation (EU) 2018/858 and first admitted after
    2020 has no real NEDC figure; the NEDC columns then hold another WLTP figure (Ioniq 5
    58 kWh: "NEDC 384" = its WLTP). Drops both NEDC fields; returns the dropped names."""
    if "2018/858" not in tan or first_year is None or first_year <= NEDC_LAST_YEAR:
        return []
    dropped = [f.value for f in _NEDC_FIELDS if f in vals]
    for f in _NEDC_FIELDS:
        vals.pop(f, None)
    return dropped


BASIS_PAIRS: dict[FactField, tuple[str, str]] = {
    FactField.length_mm: ("lengteondergrens", "lengtebovengrens"),
    FactField.width_mm: ("breedteondergrens", "breedtebovengrens"),
    FactField.height_mm: ("hoogteondergrens", "hoogtebovengrens"),
    FactField.wheelbase_mm: ("wielbasisondergrens", "wielbasisbovengrens"),
    FactField.mass_running_order_kg: ("massarijklaarondergrens", "massarijklaarbovengrens"),
    FactField.seats: ("aantalzitplaatsenondergrens", "aantalzitplaatsenbovengrens"),
}


def basis_values(row: dict[str, Any], stats: Stats) -> dict[FactField, float]:
    vals: dict[FactField, float] = {}
    for fact, (lo, hi) in BASIS_PAIRS.items():
        v, differ = single(_num(row.get(lo)), _num(row.get(hi)))
        if differ:
            stats.bounds_differ[fact.value] += 1
        elif v is not None:
            vals[fact] = round(v)
    v, _ = single(
        _num(row.get("maxconstructiesnelheidahwogr")), _num(row.get("maxconstructiesnelheidahwbgr"))
    )
    if v is not None:
        vals[FactField.top_speed_kmh] = round(v)  # fallback; the energy table wins
    if _num(row.get("massaledigondergrens")) or _num(row.get("massaledigbovengrens")):
        stats.massaledig_filled += 1  # never emitted (see module docstring)
    return vals


def _by_key(
    rows: Iterable[dict[str, Any]], variant_col: str = "codevarianttgk"
) -> dict[Key, list[dict[str, Any]]]:
    out: dict[Key, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        out[_version_key(r, variant_col)].append(r)
    return out


def version_values(
    energy: list[dict[str, Any]], basis: list[dict[str, Any]], stats: Stats, what: str
) -> tuple[dict[FactField, float], int] | None:
    """Values of one version: newest revision, fields that differ between revisions dropped.

    None when the version is not a BEV (a non-electric energy row) or has no energy row.
    """
    if not energy:
        stats.no_energy_row += 1
        return None
    if any(_s(r.get("codeenergiebron")) != "E" for r in energy):
        stats.not_bev += 1
        stats.note("not_bev", what)
        return None
    per_rev: dict[int, dict[FactField, float]] = {}
    nedc_copies: set[str] = set()
    for rev in sorted({_rev(r) for r in energy}):
        vals = energy_values([r for r in energy if _rev(r) == rev], stats)
        nedc_copies |= drop_nedc_copy_of_wltp(vals)  # A-05 F4, per revision
        b = [r for r in basis if _rev(r) == rev]
        if b:
            for fact, v in basis_values(b[0], stats).items():
                if fact == FactField.top_speed_kmh and fact in vals:
                    continue
                vals[fact] = v
        per_rev[rev] = vals
    if nedc_copies:
        stats.nedc_equals_wltp.update(nedc_copies)
        stats.note("nedc_equals_wltp", what)
    newest = max(per_rev)
    out = dict(per_rev[newest])
    for fact in list(out):
        others = {vals[fact] for rev, vals in per_rev.items() if rev != newest and fact in vals}
        if others - {out[fact]}:
            stats.revision_conflict[fact.value] += 1
            stats.note(f"revision_conflict:{fact.value}", f"{what} {sorted(others)} -> {out[fact]}")
            del out[fact]
    for fact in list(out):
        lo, hi = PLAUSIBLE[fact]
        if not lo <= out[fact] <= hi:
            stats.implausible[fact.value] += 1
            stats.note(f"implausible:{fact.value}", f"{what} {out[fact]}")
            del out[fact]
    return out, newest


def evidence_name(names: list[str], vals: dict[FactField, float]) -> str | None:
    """Matcher evidence: maker trade names, 30-min power and running-order mass.

    No "<n> kW": the matcher reads that as peak power (Decision 023: 30-min never fills peak).
    """
    parts = [" / ".join(names[:3])] if names else []
    if FactField.power_30min_kw in vals:
        parts.append(f"30-min {vals[FactField.power_30min_kw]:g}")
    if FactField.mass_running_order_kg in vals:
        parts.append(f"{vals[FactField.mass_running_order_kg]:g} kg")
    return " · ".join(parts) or None


def normalise(raw_dir: Path, retrieved_at: date, stats: Stats | None = None) -> list[SourceRecord]:
    stats = stats if stats is not None else Stats()

    def load(name: str) -> list[dict[str, Any]]:
        path = raw_dir / name
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []

    versions = load_versions(load(VERSIONS_FILE))
    energy = _by_key(load(ENERGY_FILE))
    basis = _by_key(load(BASIS_FILE))
    names = _by_key(load(NAMES_FILE), "codevariantgk")
    out: list[SourceRecord] = []
    for k in sorted(versions):
        v = versions[k]
        stats.versions += 1
        stats.cars_total += v.cars
        if not v.names:
            continue
        what = "|".join(k)
        got = version_values(energy.get(k, []), basis.get(k, []), stats, what)
        if got is None:
            continue
        vals, rev = got
        for f in drop_nedc_on_wltp_era_approval(k[0], v.first_year, vals):
            stats.nedc_wltp_era[f] += 1
        if not vals:
            stats.no_specs += 1
            continue
        (make, model), _ = v.names.most_common(1)[0]
        trade = sorted(
            {_s(r.get("handelsbenamingfabrikant")) for r in names.get(k, []) if _rev(r) == rev}
            - {""}
        )
        stats.cars_covered += v.cars
        stats.emitted.update(f.value for f in vals)
        out.append(
            SourceRecord(
                source=SOURCE,
                record_key=f"{ENERGY}+{BASIS}[{GROUPING}]:{what}|{rev}",
                kind="spec",
                make=make,
                model=model,
                variant_name=evidence_name(trade, vals),
                year=v.first_year,
                specs={
                    f: SpecValue(value=int(x) if float(x).is_integer() else x, unit=UNITS[f])
                    for f, x in vals.items()
                },
                retrieved_at=retrieved_at,
                confidence=Confidence.high,
            )
        )
    return out


# --- commands ---------------------------------------------------------------------------


def fetch_cmd(client: httpx.Client | None = None) -> int:
    target = c.raw_dir(NAME)
    own = client is None
    client = client or net.safe_client(NAME, timeout=120)
    try:
        versions = fetch(client, target)
    except (httpx.HTTPError, LicenceChanged) as exc:
        print(f"fetch {NAME}: failed: {exc}")
        return 1
    finally:
        if own:
            client.close()
    meta = c.read_fetch_meta(target)
    c.log_step(
        step="fetch",
        source=NAME,
        input_=f"{BASE_URL}/resource/{{{','.join(DATASETS)}}}.json (grouped plate query + "
        f"TGK rows in batches of {BATCH} TANs)",
        output=c.rel(target),
        rows_out=versions,
        tans=meta.get("tans"),
        tgk_requests=meta.get("tgk_requests"),
        tgk_rows_fetched=meta.get("tgk_rows_fetched"),
        tgk_rows_kept=meta.get("tgk_rows_kept"),
    )
    return 0


def normalise_cmd(from_fixtures: bool) -> int:
    src = c.FIXTURES_DIR / DIR if from_fixtures else c.raw_dir(NAME)
    if not (src / VERSIONS_FILE).exists():
        print(f"normalise {NAME}: no data in {src} (run `ev fetch {NAME}` first)")
        return 1
    stats = Stats()
    records = normalise(src, c.retrieved_at_for(src), stats)
    out = c.staging_dir() / f"{NAME}.records.jsonl"
    rows = c.write_records(records, out)
    c.log_step(
        step="normalise",
        source=NAME,
        input_=c.rel(src),
        output=c.rel(out),
        rows_out=rows,
        from_fixtures=from_fixtures,
        versions=stats.versions,
        cars_total=stats.cars_total,
        cars_covered=stats.cars_covered,
        no_energy_row=stats.no_energy_row,
        not_bev=stats.not_bev,
        no_specs=stats.no_specs,
        fields_emitted=dict(stats.emitted),
        dropped_revision_conflict=dict(stats.revision_conflict),
        dropped_bounds_differ=dict(stats.bounds_differ),
        dropped_implausible=dict(stats.implausible),
        wltp_bounds_swapped=stats.wltp_swapped,
        dropped_nedc_equals_wltp=dict(stats.nedc_equals_wltp),
        dropped_nedc_wltp_era=dict(stats.nedc_wltp_era),
        multi_drivetrain_power_skipped=stats.multi_drivetrain_power_skipped,
        massaledig_filled=stats.massaledig_filled,
        rules="newest revision; field dropped if revisions differ; dims/mass/seats only when "
        "lower == upper bound; WLTP best = max range / min consumption; NEDC never WLTP",
        examples=dict(stats.examples),
    )
    return 0
