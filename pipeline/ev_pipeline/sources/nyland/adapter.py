"""Bjørn Nyland range/charging test sheet: importer skeleton. PERMISSION PENDING.

Until permission is logged in DECISIONS.md:
- the sheet URL comes only from the env var NYLAND_SHEET_CSV_URL (never in the repo);
- fetches go to data/local/nyland/ (git-ignored), never data/raw/ or object storage;
- normalised output goes to data/local/nyland/, never data/staging/, so nothing from this
  source can reach a release;
- tests use a synthetic CSV with invented cars (tests/fixtures/nyland/), never real rows.

The real sheet's column headers are not known yet: COLUMNS maps our expected CSV headers
to fact fields, and gets adjusted once permission is granted and the sheet is seen.
"""

from __future__ import annotations

import csv
import os
from datetime import date
from pathlib import Path

import httpx

from ev_pipeline import net
from ev_pipeline.records import SourceRecord, SpecValue
from ev_pipeline.schema_models import Confidence, FactField, Source
from ev_pipeline.sources import _common as c

NAME = "nyland"
ENV_URL = "NYLAND_SHEET_CSV_URL"
SHEET_FILE = "sheet.csv"

SOURCE = Source(
    id="nyland",
    name="Bjørn Nyland range/charging tests",
    licence="none",
    attribution="Bjørn Nyland test results (permission pending; local use only).",
)

# CSV header -> (fact field, unit). Placeholder headers until the real sheet is mapped.
COLUMNS: dict[str, tuple[FactField, str]] = {
    "range_km": (FactField.real_range_km, "km"),
    "consumption_kwh_100km": (FactField.consumption_kwh_100km, "kWh/100km"),
    "usable_kwh": (FactField.battery_kwh_net, "kWh"),
    "dc_avg_10_80_kw": (FactField.dc_avg_10_80_kw, "kW"),
}


def _number(text: str | None) -> float | None:
    if text is None or not text.strip():
        return None
    try:
        value = float(text.strip().replace(",", "."))
    except ValueError:
        return None
    return value if value > 0 else None


def normalise(raw_dir: Path, retrieved_at: date) -> list[SourceRecord]:
    records: list[SourceRecord] = []
    for path in sorted(raw_dir.glob("*.csv")):
        with path.open(newline="", encoding="utf-8") as fh:
            for line_no, row in enumerate(csv.DictReader(fh), start=2):
                make, model = (row.get("make") or "").strip(), (row.get("model") or "").strip()
                if not make or not model:
                    continue
                specs = {
                    field: SpecValue(value=value, unit=unit)
                    for header, (field, unit) in COLUMNS.items()
                    if (value := _number(row.get(header))) is not None
                }
                if not specs:
                    continue
                year = _number(row.get("year"))
                records.append(
                    SourceRecord(
                        source=SOURCE,
                        record_key=f"{path.name}:{line_no}",
                        make=make,
                        model=model,
                        variant_name=(row.get("variant") or "").strip() or None,
                        year=int(year) if year else None,
                        specs=specs,
                        retrieved_at=retrieved_at,
                        confidence=Confidence.high,  # exact-variant measured tests
                    )
                )
    return records


def scrub_error(exc: httpx.HTTPError) -> str:
    """A log-safe description of a fetch error: no URL, no host, no query string."""
    if isinstance(exc, httpx.HTTPStatusError):
        return f"HTTP {exc.response.status_code}"
    return type(exc).__name__


def fetch_cmd(client: httpx.Client | None = None) -> int:
    url = os.environ.get(ENV_URL, "").strip()
    if not url:
        print(f"fetch {NAME}: set {ENV_URL} (see .env.example); permission is still pending")
        return 1
    target = c.local_dir(NAME)
    target.mkdir(parents=True, exist_ok=True)
    own = client is None
    client = client or net.safe_client(NAME, timeout=120)
    try:
        resp = client.get(url)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        # Never print the exception text: httpx puts the full URL in it, and the URL is
        # private (T-004 review). Status code or error class only.
        print(f"fetch {NAME}: failed: {scrub_error(exc)}")
        return 1
    finally:
        if own:
            client.close()
    (target / SHEET_FILE).write_bytes(resp.content)
    # Deliberately no URL in the metadata or run log: it stays in the env only.
    c.write_fetch_meta(target, {"url_env": ENV_URL, "bytes": len(resp.content)})
    c.log_step(
        step="fetch",
        source=NAME,
        input_=f"${ENV_URL}",
        output=c.rel(target / SHEET_FILE),
        rows_out=max(resp.text.count("\n") - 1, 0),
        runlog=target / "runlog.jsonl",
    )
    return 0


def normalise_cmd(from_fixtures: bool) -> int:
    src = c.FIXTURES_DIR / NAME if from_fixtures else c.local_dir(NAME)
    if not any(src.glob("*.csv")):
        print(f"normalise {NAME}: no CSV in {src} (run `ev fetch {NAME}` first)")
        return 1
    records = normalise(src, c.retrieved_at_for(src))
    out_dir = c.local_dir(NAME)
    # Never data/staging/: the synthetic fixture output gets its own file name too.
    out = out_dir / ("fixture.records.jsonl" if from_fixtures else "records.jsonl")
    rows = c.write_records(records, out)
    c.log_step(
        step="normalise",
        source=NAME,
        input_=c.rel(src),
        output=c.rel(out),
        rows_out=rows,
        from_fixtures=from_fixtures,
        runlog=out_dir / "runlog.jsonl",
    )
    return 0
