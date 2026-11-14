"""Helpers shared by the source adapters: paths, fetch metadata, staging output, run log."""

from __future__ import annotations

import json
import os
from collections.abc import Iterable
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from ev_pipeline.records import SourceRecord

PIPELINE_DIR = Path(__file__).resolve().parents[2]
REPO_DIR = PIPELINE_DIR.parent
FIXTURES_DIR = PIPELINE_DIR / "tests" / "fixtures"

FETCH_META = "_fetch.json"
"""Written next to the raw data by every fetch: when, from where, and the licence seen."""

USER_AGENT = "ev-finder-pipeline/0.0 (open data importer)"


def data_dir() -> Path:
    """Repo `data/` folder. `EV_DATA_DIR` overrides it (tests point it at a tmp dir)."""
    override = os.environ.get("EV_DATA_DIR")
    return Path(override) if override else REPO_DIR / "data"


def raw_dir(source: str) -> Path:
    return data_dir() / "raw" / source


def local_dir(source: str) -> Path:
    return data_dir() / "local" / source


def staging_dir() -> Path:
    return data_dir() / "staging"


def now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def write_fetch_meta(target: Path, meta: dict[str, Any]) -> None:
    target.mkdir(parents=True, exist_ok=True)
    payload = {"fetched_at": now_utc(), **meta}
    (target / FETCH_META).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def read_fetch_meta(source_dir: Path) -> dict[str, Any]:
    path = source_dir / FETCH_META
    return json.loads(path.read_text()) if path.exists() else {}


def retrieved_at_for(source_dir: Path) -> date:
    """Retrieval date = the fetch date recorded next to the raw data (stable on re-runs)."""
    fetched = read_fetch_meta(source_dir).get("fetched_at")
    if fetched:
        return datetime.fromisoformat(fetched).date()
    return datetime.now(UTC).date()


def write_records(records: Iterable[SourceRecord], out_path: Path) -> int:
    """Write one SourceRecord JSON per line, sorted by record_key so output is deterministic."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(records, key=lambda r: r.record_key)
    with out_path.open("w", encoding="utf-8") as fh:
        for rec in rows:
            fh.write(rec.model_dump_json(exclude_none=True) + "\n")
    return len(rows)


def append_runlog(entry: dict[str, Any], runlog: Path | None = None) -> None:
    path = runlog or staging_dir() / "runlog.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def log_step(
    *,
    step: str,
    source: str,
    input_: str,
    output: str,
    rows_out: int,
    outcome: str = "ok",
    runlog: Path | None = None,
    **extra: Any,
) -> dict[str, Any]:
    """Print a one-line run log and append it to the run log file."""
    entry = {
        "step": step,
        "source": source,
        "input": input_,
        "output": output,
        "rows_out": rows_out,
        "outcome": outcome,
        "timestamp": now_utc(),
        **extra,
    }
    print(
        f"[{entry['timestamp']}] {step} {source}: {outcome}, {rows_out} rows "
        f"from {input_} -> {output}"
    )
    append_runlog(entry, runlog)
    return entry


def rel(path: Path) -> str:
    """Path relative to the repo when possible (keeps run logs machine-independent)."""
    try:
        return str(path.resolve().relative_to(REPO_DIR))
    except ValueError:
        return str(path)
