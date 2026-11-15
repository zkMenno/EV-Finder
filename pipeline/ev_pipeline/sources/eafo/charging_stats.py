"""Shared helpers for the charging-statistics loaders (T-025, Decision 012).

Used by the `eafo`, `bnetza` and `dft-charging` adapters. It lives in the eafo folder only
because the builder lane was limited to the five new source folders; the coordinator may move
it to `sources/_common.py` when integrating.

Output is not SourceRecords: each loader writes `data/staging/<source>.charging_stats.jsonl`,
one schema `$defs/ChargingStat` row per line, validated with jsonschema against
packages/schema/schemas/ev.schema.json. A sidecar `<source>.charging_stats.meta.json` records
the licence, attribution, download URL and licence text seen for that download, and the
source status from data/sources.yaml (only `active` sources may reach a release).

Rules enforced here, so every loader gets them:

- metric, power band and definition ids must exist in data/taxonomy (config, not code);
- a row outside its definition's `valid_from` / `valid_to` window is dropped, so a series
  never mixes definitions (spec "Definition rules" 2); the loaders log how many;
- aggregates only: there is no field for a location, operator or charger id.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from functools import cache
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from ev_pipeline.sources import _common as c

SCHEMA_FILE = c.REPO_DIR / "packages" / "schema" / "schemas" / "ev.schema.json"


def taxonomy_dir() -> Path:
    """`taxonomy/` in the data dir (the /data mount in the image), else the repo copy."""
    path = c.data_dir() / "taxonomy"
    return path if path.exists() else c.REPO_DIR / "data" / "taxonomy"


@dataclass(frozen=True)
class Taxonomy:
    metrics: dict[str, dict[str, Any]]
    power_bands: dict[str, dict[str, Any]]
    definitions: dict[str, dict[str, Any]]

    def check(self, metric_id: str, power_band_id: str | None, definition_id: str) -> None:
        if metric_id not in self.metrics:
            raise ValueError(f"unknown charging metric {metric_id!r} (data/taxonomy)")
        if power_band_id is not None and power_band_id not in self.power_bands:
            raise ValueError(f"unknown power band {power_band_id!r} (data/taxonomy)")
        if definition_id not in self.definitions:
            raise ValueError(f"unknown charging definition {definition_id!r} (data/taxonomy)")

    def in_validity(self, definition_id: str, period_end: date) -> bool:
        d = self.definitions[definition_id]
        lo, hi = d.get("valid_from"), d.get("valid_to")
        if lo and period_end < date.fromisoformat(str(lo)):
            return False
        return not (hi and period_end > date.fromisoformat(str(hi)))


def load_taxonomy(path: Path | None = None) -> Taxonomy:
    root = path or taxonomy_dir()

    def rows(name: str, key: str) -> dict[str, dict[str, Any]]:
        data = yaml.safe_load((root / name).read_text(encoding="utf-8")) or {}
        return {str(r["id"]): r for r in data.get(key) or []}

    return Taxonomy(
        metrics=rows("charging_metrics.yaml", "charging_metrics"),
        power_bands=rows("power_bands.yaml", "power_bands"),
        definitions=rows("charging_definitions.yaml", "charging_definitions"),
    )


@cache
def _validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    root = {
        "$schema": schema.get("$schema"),
        "$defs": schema["$defs"],
        "$ref": "#/$defs/ChargingStat",
    }
    return Draft202012Validator(root, format_checker=FormatChecker())


def validate(row: dict[str, Any]) -> None:
    """Raise jsonschema.ValidationError unless `row` is a valid ChargingStat."""
    _validator().validate(row)


@dataclass
class StatBuilder:
    """Builds ChargingStat rows for one source and keeps the drop counts for the run log."""

    source_id: str
    taxonomy: Taxonomy
    retrieved_at: date
    confidence: str
    source_record: str | None = None
    report_date: str | None = None
    """The source's own as-of label (e.g. BNetzA "Stand"), for the run log."""
    rows: dict[str, dict[str, Any]] = field(default_factory=dict)
    dropped_out_of_validity: int = 0
    duplicates: int = 0

    def add(
        self,
        *,
        country: str,
        period_end: date,
        metric_id: str,
        value: float,
        unit: str,
        definition_id: str,
        power_band_id: str | None = None,
        region: str | None = None,
        source_label: str | None = None,
        notes: str | None = None,
    ) -> dict[str, Any] | None:
        self.taxonomy.check(metric_id, power_band_id, definition_id)
        if not self.taxonomy.in_validity(definition_id, period_end):
            self.dropped_out_of_validity += 1
            return None
        sid = ":".join(
            [
                self.source_id,
                country.lower(),
                (region or "").lower(),
                period_end.isoformat(),
                metric_id,
                power_band_id or "all",
            ]
        )
        row: dict[str, Any] = {
            "id": sid,
            "country": country,
            "region": region,
            "period_end": period_end.isoformat(),
            "metric_id": metric_id,
            "power_band_id": power_band_id,
            "value": value,
            "unit": unit,
            "source_id": self.source_id,
            "definition_id": definition_id,
            "confidence": self.confidence,
            "entered_by": "pipeline",
            "retrieved_at": self.retrieved_at.isoformat(),
        }
        if self.source_record:
            row["source_record"] = self.source_record
        if source_label:
            row["source_label"] = source_label
        if notes:
            row["notes"] = notes
        validate(row)
        if sid in self.rows:
            self.duplicates += 1
        self.rows[sid] = row
        return row

    def sorted_rows(self) -> list[dict[str, Any]]:
        return [self.rows[k] for k in sorted(self.rows)]


def write_stats(rows: Iterable[dict[str, Any]], out_path: Path) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out_path.open("w", encoding="utf-8") as fh:
        for row in sorted(rows, key=lambda r: r["id"]):
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            n += 1
    return n


def source_status(source_id: str, path: Path | None = None) -> str:
    """The `status` of a source in data/sources.yaml ('missing' if it isn't listed)."""
    from ev_pipeline import net  # local import: net imports _common too

    path = path or net.sources_yaml_path()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for entry in data.get("sources") or []:
        if entry.get("id") == source_id:
            return str(entry.get("status", "missing"))
    return "missing"


def write_meta(out_path: Path, meta: dict[str, Any]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def staging_paths(name: str) -> tuple[Path, Path]:
    base = c.staging_dir()
    return base / f"{name}.charging_stats.jsonl", base / f"{name}.charging_stats.meta.json"
