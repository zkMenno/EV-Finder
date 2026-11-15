"""DfT vehicle licensing data files adapter (OGL-UK-3.0): licensed BEV cars in the UK.

df_VEH0120_UK ("Vehicles at the end of the quarter by licence status, body type, make,
generic model and model", United Kingdom) is a wide CSV: `BodyType, Make, GenModel, Model,
Fuel, LicenceStatus` and one column per quarter ("2026 Q2", newest first). We keep
BodyType = Cars, Fuel = Battery electric, LicenceStatus = Licensed (SORN excluded), and read
the newest quarter column only.

One record per Make x GenModel x Model: `model` = GenModel (DfT's grouping, e.g.
"TESLA MODEL 3"), `variant_name` = Model (the DVLA model text, e.g. "MODEL 3 LONG RANGE
AWD"). Summing the records of one GenModel gives the GenModel total; nothing is counted
twice. GenModel "<MAKE> MODEL MISSING" rows are dropped (no model to match) and their count
goes to the run log.

These are fleet (stock) counts at quarter end, not registrations in a year, so `year` is
left empty (the matcher then keeps the count on the model) and the quarter is in
`record_key`.

The asset URL changes every release, so fetch resolves it through the gov.uk content API.
The UK file (about 41 MB, from 2014 Q3) is preferred over GB (about 67 MB, from 1994): the
country is UK and it is smaller. Streamed to data/raw/dft_veh/; never committed.
"""

from __future__ import annotations

import csv
import re
import time
from collections import Counter
from datetime import date
from pathlib import Path

import httpx

from ev_pipeline.records import SourceRecord, SpecValue
from ev_pipeline.schema_models import Confidence, Country, FactField, Source
from ev_pipeline.sources import _common as c

NAME = "dft-veh"
DIR = "dft_veh"
CONTENT_API = (
    "https://www.gov.uk/api/content/government/statistical-data-sets/"
    "vehicle-licensing-statistics-data-files"
)
PAGE_URL = (
    "https://www.gov.uk/government/statistical-data-sets/vehicle-licensing-statistics-data-files"
)
FILE_PREFERENCE = ["df_VEH0120_UK.csv", "df_VEH0120_GB.csv"]
MAX_DOWNLOAD_SECONDS = 300
QUARTER_RE = re.compile(r"^(\d{4}) Q([1-4])$")
MISSING = "MODEL MISSING"

FILTER = {"BodyType": "Cars", "Fuel": "Battery electric", "LicenceStatus": "Licensed"}

SOURCE = Source(
    id="dft-veh",
    name="DfT vehicle licensing statistics: df_VEH0120 (licensed vehicles by make and model)",
    url=PAGE_URL,
    licence="OGL-UK-3.0",
    attribution="Contains public sector information licensed under the Open Government "
    "Licence v3.0 (Department for Transport, vehicle licensing statistics).",
)


class DownloadTooSlow(RuntimeError):
    pass


def latest_quarter(header: list[str]) -> str:
    quarters = [h for h in header if QUARTER_RE.match(h)]
    if not quarters:
        raise ValueError("no quarter columns in VEH0120 header")
    return max(quarters, key=lambda h: tuple(int(x) for x in QUARTER_RE.match(h).groups()))


def data_file(raw_dir: Path) -> Path | None:
    for name in FILE_PREFERENCE:
        if (raw_dir / name).exists():
            return raw_dir / name
    return None


def aggregate(path: Path) -> tuple[str, Counter[tuple[str, str, str]], int]:
    """Stream the CSV. Returns (quarter, counts per Make x GenModel x Model, missing count)."""
    counts: Counter[tuple[str, str, str]] = Counter()
    missing = 0
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        quarter = latest_quarter(reader.fieldnames or [])
        for row in reader:
            if any(row[k].strip() != v for k, v in FILTER.items()):
                continue
            raw = row[quarter].strip()
            n = int(raw) if raw.isdigit() else 0  # suppressed/blank cells count as 0
            if n <= 0:
                continue
            make, gen, model = row["Make"].strip(), row["GenModel"].strip(), row["Model"].strip()
            if gen.endswith(MISSING) or not gen:
                missing += n
                continue
            counts[(make, gen, model)] += n
    return quarter, counts, missing


def normalise(raw_dir: Path, retrieved_at: date) -> list[SourceRecord]:
    path = data_file(raw_dir)
    if path is None:
        return []
    quarter, counts, _missing = aggregate(path)
    table = path.stem.removeprefix("df_")
    records = []
    for (make, gen, model), n in counts.items():
        records.append(
            SourceRecord(
                source=SOURCE,
                record_key=f"{table}:{quarter}:Licensed:{make}|{gen}|{model}",
                kind="registration_count",
                make=make,
                model=gen,
                variant_name=model,
                year=None,
                country=Country.UK,
                specs={FactField.registered_count: SpecValue(value=n, unit="count")},
                retrieved_at=retrieved_at,
                confidence=Confidence.high,
            )
        )
    return records


# --------------------------------------------------------------------------- fetch


def resolve_url(client: httpx.Client) -> tuple[str, dict]:
    resp = client.get(CONTENT_API)
    resp.raise_for_status()
    doc = resp.json()
    attachments = doc.get("details", {}).get("attachments", [])
    for name in FILE_PREFERENCE:
        for att in attachments:
            if str(att.get("url", "")).endswith("/" + name):
                return att["url"], {
                    "title": att.get("title"),
                    "file_size": att.get("file_size"),
                    "public_updated_at": doc.get("public_updated_at"),
                }
    raise FileNotFoundError("df_VEH0120 not listed in the gov.uk content API")


def fetch(client: httpx.Client, target: Path, max_seconds: float = MAX_DOWNLOAD_SECONDS) -> int:
    """Stream the VEH0120 CSV into `target`. Returns bytes written."""
    url, info = resolve_url(client)
    name = url.rsplit("/", 1)[-1]
    target.mkdir(parents=True, exist_ok=True)
    part = target / (name + ".part")
    start = time.monotonic()
    size = 0
    with client.stream("GET", url) as resp:
        resp.raise_for_status()
        with part.open("wb") as fh:
            for chunk in resp.iter_bytes(1 << 20):
                fh.write(chunk)
                size += len(chunk)
                if time.monotonic() - start > max_seconds:
                    fh.close()
                    part.unlink(missing_ok=True)
                    raise DownloadTooSlow(f"{name}: over {max_seconds:.0f}s, aborted")
    for other in FILE_PREFERENCE:
        (target / other).unlink(missing_ok=True)
    part.rename(target / name)
    c.write_fetch_meta(
        target,
        {
            "content_api": CONTENT_API,
            "url": url,
            "file": name,
            "bytes": size,
            "seconds": round(time.monotonic() - start, 1),
            "licence_basis": "gov.uk: 'All content is available under the Open Government "
            "Licence v3.0, except where otherwise stated' (no exception on this page)",
            **info,
        },
    )
    return size


def fetch_cmd(client: httpx.Client | None = None) -> int:
    target = c.raw_dir(DIR)
    own = client is None
    client = client or httpx.Client(
        timeout=120, headers={"User-Agent": c.USER_AGENT}, follow_redirects=True
    )
    try:
        size = fetch(client, target)
    except (httpx.HTTPError, FileNotFoundError, DownloadTooSlow) as exc:
        print(f"fetch {NAME}: failed: {exc}")
        return 1
    finally:
        if own:
            client.close()
    meta = c.read_fetch_meta(target)
    c.log_step(
        step="fetch",
        source=NAME,
        input_=meta.get("url", CONTENT_API),
        output=c.rel(target),
        rows_out=size,
        unit="bytes",
        seconds=meta.get("seconds"),
    )
    return 0


def normalise_cmd(from_fixtures: bool) -> int:
    src = c.FIXTURES_DIR / DIR if from_fixtures else c.raw_dir(DIR)
    path = data_file(src)
    if path is None:
        print(f"normalise {NAME}: no data in {src} (run `ev fetch {NAME}` first)")
        return 1
    quarter, counts, missing = aggregate(path)
    records = normalise(src, c.retrieved_at_for(src))
    out = c.staging_dir() / f"{NAME}.records.jsonl"
    rows = c.write_records(records, out)
    c.log_step(
        step="normalise",
        source=NAME,
        input_=c.rel(path),
        output=c.rel(out),
        rows_out=rows,
        from_fixtures=from_fixtures,
        quarter=quarter,
        licensed_bev_cars=sum(counts.values()),
        dropped_model_missing=missing,
        genmodels=len({(mk, g) for mk, g, _ in counts}),
    )
    return 0
