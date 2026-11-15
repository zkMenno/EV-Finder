"""fueleconomy.gov adapter (US public domain): EPA figures for battery-electric cars, market US.

Source: the "vehicles" dataset, `https://www.fueleconomy.gov/feg/epadata/vehicles.csv.zip`
(about 2.2 MB zipped, 50,000+ rows, 1984 onward, updated continuously). The download page
states no licence; the data.gov record (publisher EPA) links the EPA Data License: "all data
produced by the U.S EPA is by default in the public domain ... 17 U.S.C. § 105" (R-06).

BEVs only: `atvType = "EV"` and `fuelType1 = "Electricity"` (PHEV, FCV and hybrids drop out).
Per row (one row = make x model text x model year x EPA options):

- `epa_range_km`: `range` (miles) x 1.609344, 1 decimal.
- `consumption_kwh_100km`: `combE` (combined kWh/100 mi, measured from the wall, so charging
  losses are included) / 1.609344, 2 decimals. EPA 5-cycle basis: not the same test as WLTP,
  so these are cross-check values for agreement counts, not replacements for EU figures.
- `battery_kwh_gross`: only where the EPA text names a pack size, e.g. "(85 kW-hr battery
  pack)" (about 56 rows, mostly older Teslas). That is a nominal pack size, not a usable
  figure, so it goes in a separate `#battery` record with confidence low.

SourceRecord kind spec, `country` None (the schema Country enum has no US); the market is in
`record_key` (`...;market=us`). Confidence medium. `model` is EPA's model text (it carries
options such as "w/21in All-Season Tires"); `body` is left empty.
"""

from __future__ import annotations

import csv
import io
import re
import zipfile
from collections import Counter
from datetime import date
from pathlib import Path

import httpx

from ev_pipeline import net
from ev_pipeline.records import SourceRecord, SpecValue
from ev_pipeline.schema_models import Confidence, FactField, Source
from ev_pipeline.sources import _common as c

NAME = "fueleconomy"
DIR = "fueleconomy"
URL = "https://www.fueleconomy.gov/feg/epadata/vehicles.csv.zip"
ZIP_NAME = "vehicles.csv.zip"
CSV_NAME = "vehicles.csv"
MARKET = "us"
KM_PER_MILE = 1.609344
BATTERY_RE = re.compile(r"(\d+(?:\.\d+)?)\s*kW-?hr?\s+battery", re.I)
DRIVE = {
    "front-wheel drive": "fwd",
    "rear-wheel drive": "rwd",
    "all-wheel drive": "awd",
    "4-wheel drive": "awd",
    "4-wheel or all-wheel drive": "awd",
    "part-time 4-wheel drive": "awd",
}
LICENCE_BASIS = (
    "No licence on the download page. data.gov record 'www.fueleconomy.gov' (publisher EPA) "
    "links the EPA Data License: 'all data produced by the U.S EPA is by default in the "
    "public domain' (17 U.S.C. 105), https://edg.epa.gov/EPA_Data_License.htm"
)

SOURCE = Source(
    id="fueleconomy",
    name="fueleconomy.gov vehicles dataset (US DOE / EPA)",
    url="https://www.fueleconomy.gov/feg/download.shtml",
    licence="US-Government-Public-Domain",
    attribution="Data from fueleconomy.gov (U.S. Department of Energy and U.S. Environmental "
    "Protection Agency), public domain.",
)


def _num(v: str | None) -> float | None:
    try:
        x = float(v) if v not in (None, "") else None
    except ValueError:
        return None
    return x if x and x > 0 else None


def read_rows(raw_dir: Path) -> list[dict[str, str]]:
    zpath, cpath = raw_dir / ZIP_NAME, raw_dir / CSV_NAME
    if zpath.exists():
        with zipfile.ZipFile(zpath) as zf:
            name = next(n for n in zf.namelist() if n.lower().endswith(".csv"))
            text = zf.read(name).decode("utf-8-sig")
    else:
        text = cpath.read_text(encoding="utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def is_bev(row: dict[str, str]) -> bool:
    return row.get("atvType", "").strip() == "EV" and row.get("fuelType1", "") == "Electricity"


def normalise(
    raw_dir: Path, retrieved_at: date, stats: Counter[str] | None = None
) -> list[SourceRecord]:
    stats = stats if stats is not None else Counter()
    records: list[SourceRecord] = []
    for row in read_rows(raw_dir):
        if not is_bev(row):
            continue
        stats["bev_rows"] += 1
        make, model = row.get("make", "").strip(), row.get("model", "").strip()
        year = int(row["year"]) if row.get("year", "").isdigit() else None
        if not make or not model:
            stats["dropped_no_name"] += 1
            continue
        key = f"vehicles.csv:id={row.get('id')};market={MARKET}"
        common = {
            "source": SOURCE,
            "make": make,
            "model": model,
            "year": year,
            "country": None,
            "drivetrain": DRIVE.get(row.get("drive", "").strip().lower()),
            "retrieved_at": retrieved_at,
        }
        specs: dict[FactField, SpecValue] = {}
        rng = _num(row.get("range"))
        if rng is not None:
            specs[FactField.epa_range_km] = SpecValue(value=round(rng * KM_PER_MILE, 1), unit="km")
        comb = _num(row.get("combE"))
        if comb is not None:
            specs[FactField.consumption_kwh_100km] = SpecValue(
                value=round(comb / KM_PER_MILE, 2), unit="kWh/100km"
            )
        if specs:
            records.append(
                SourceRecord(
                    record_key=key,
                    kind="spec",
                    specs=specs,
                    confidence=Confidence.medium,
                    **common,
                )
            )
        else:
            stats["dropped_no_values"] += 1
        m = BATTERY_RE.search(f"{row.get('evMotor', '')} {model}")
        if m:
            stats["battery_from_text"] += 1
            records.append(
                SourceRecord(
                    record_key=f"{key}#battery",
                    kind="spec",
                    specs={
                        FactField.battery_kwh_gross: SpecValue(value=float(m.group(1)), unit="kWh")
                    },
                    confidence=Confidence.low,
                    **common,
                )
            )
    return records


# --- fetch ------------------------------------------------------------------------------


def fetch(client: httpx.Client, target: Path) -> int:
    """Stream vehicles.csv.zip into `target`. Returns bytes written."""
    target.mkdir(parents=True, exist_ok=True)
    part = target / (ZIP_NAME + ".part")
    size = 0
    with client.stream("GET", URL) as resp:
        resp.raise_for_status()
        last_modified = resp.headers.get("last-modified")
        with part.open("wb") as fh:
            for chunk in resp.iter_bytes(1 << 20):
                fh.write(chunk)
                size += len(chunk)
    with zipfile.ZipFile(part) as zf:  # fail early on a broken download
        if not any(n.lower().endswith(".csv") for n in zf.namelist()):
            raise zipfile.BadZipFile("no CSV inside vehicles.csv.zip")
    part.replace(target / ZIP_NAME)
    c.write_fetch_meta(
        target,
        {
            "url": URL,
            "file": ZIP_NAME,
            "bytes": size,
            "last_modified": last_modified,
            "licence": SOURCE.licence,
            "licence_basis": LICENCE_BASIS,
        },
    )
    return size


def fetch_cmd(client: httpx.Client | None = None) -> int:
    target = c.raw_dir(DIR)
    own = client is None
    client = client or net.safe_client(NAME, timeout=120)
    try:
        size = fetch(client, target)
    except (httpx.HTTPError, zipfile.BadZipFile) as exc:
        print(f"fetch {NAME}: failed: {exc}")
        return 1
    finally:
        if own:
            client.close()
    meta = c.read_fetch_meta(target)
    c.log_step(
        step="fetch",
        source=NAME,
        input_=URL,
        output=c.rel(target),
        rows_out=size,
        unit="bytes",
        last_modified=meta.get("last_modified"),
    )
    return 0


def normalise_cmd(from_fixtures: bool) -> int:
    src = c.FIXTURES_DIR / DIR if from_fixtures else c.raw_dir(DIR)
    if not ((src / ZIP_NAME).exists() or (src / CSV_NAME).exists()):
        print(f"normalise {NAME}: no data in {src} (run `ev fetch {NAME}` first)")
        return 1
    stats: Counter[str] = Counter()
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
        market=MARKET,
        **dict(stats),
    )
    return 0
