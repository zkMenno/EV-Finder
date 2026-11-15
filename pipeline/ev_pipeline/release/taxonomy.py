"""Optional taxonomy tables for the release (T-024, T-019 coordinator half; Decisions 011, 012).

Inputs (all optional; a missing file is skipped and the table is left out of the catalogue):
  data/taxonomy/{bidi_modes,bidi_routes,bidi_protocols,bidi_caveats,bidi_status,
                 connector_types,bidi_equipment,charging_metrics,charging_definitions,
                 power_bands}.yaml

The four base tables (voltage classes, chemistries, cooling, glossary) are loaded by
ev_pipeline.derive.links; these tables are only added when that base taxonomy ships, because
the schema `Taxonomy` object requires the base four.

Licence gate: `bidi_equipment` rows cite maker pages and press for prices and markets. A row
ships only when every one of its `source_ids` is releasable in data/sources.yaml; otherwise it is
held back and listed in the run log. The other tables are our own plain-language descriptions
and ship as they are. Full curation checks live in data/taxonomy/validate_taxonomy.py; the
release re-checks the cross-references it depends on.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

OPTIONAL_TABLES = (
    "bidi_modes",
    "bidi_routes",
    "bidi_protocols",
    "bidi_caveats",
    "bidi_status",
    "connector_types",
    "bidi_equipment",
    "charging_metrics",
    "charging_definitions",
    "power_bands",
)
GATED_TABLES = {"bidi_equipment": "source_ids"}


@dataclass
class OptionalTaxonomy:
    tables: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    inputs: list[str] = field(default_factory=list)
    # table -> {row id: reason}
    held_back: dict[str, dict[str, str]] = field(default_factory=dict)

    def counts(self) -> dict[str, int]:
        return {k: len(v) for k, v in self.tables.items()}


def _rows(path: Path, key: str) -> list[dict[str, Any]] | None:
    if not path.exists():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    rows = data.get(key) if isinstance(data, dict) else data
    if not isinstance(rows, list):
        return []
    return [r for r in rows if isinstance(r, dict)]


def load_optional_taxonomy(
    data_dir: Path, why_blocked: Callable[[str], str | None]
) -> OptionalTaxonomy:
    """`why_blocked(source_id)` is the licence gate: None = releasable, else the reason."""
    out = OptionalTaxonomy()
    for name in OPTIONAL_TABLES:
        path = data_dir / "taxonomy" / f"{name}.yaml"
        rows = _rows(path, name)
        if rows is None:
            continue
        out.inputs.append(str(path))
        ref_key = GATED_TABLES.get(name)
        if ref_key is None:
            out.tables[name] = rows
            continue
        keep = []
        for r in rows:
            reasons = {s: why_blocked(s) for s in r.get(ref_key) or []}
            bad = {s: w for s, w in reasons.items() if w is not None}
            if not reasons:
                bad = {"(none)": "no source"}
            if bad:
                out.held_back.setdefault(name, {})[str(r.get("id"))] = "; ".join(
                    f"{s}: {w}" for s, w in sorted(bad.items())
                )
            else:
                keep.append(r)
        out.tables[name] = keep
    return out


def optional_taxonomy_errors(
    tables: dict[str, list[dict[str, Any]]], platform_ids: set[str]
) -> list[str]:
    """Cross-references the shipped tables depend on. Empty list = fine."""
    errs: list[str] = []

    def ids(name: str) -> set[str]:
        return {r["id"] for r in tables.get(name, []) if "id" in r}

    for name, rows in tables.items():
        seen: set[str] = set()
        for r in rows:
            rid = r.get("id")
            if rid in seen:
                errs.append(f"taxonomy {name}: duplicate id {rid}")
            seen.add(rid)

    for r in tables.get("bidi_equipment", []):
        tag = f"taxonomy bidi_equipment {r.get('id')}"
        for key, table in (
            ("route_id", "bidi_routes"),
            ("mode_ids", "bidi_modes"),
            ("protocol_ids", "bidi_protocols"),
        ):
            vals = r.get(key)
            vals = [vals] if isinstance(vals, str) else vals or []
            if vals and table not in tables:
                errs.append(f"{tag}: {key} needs {table}.yaml")
                continue
            errs += [f"{tag}: unknown {key} {v!r}" for v in vals if v not in ids(table)]
        errs += [
            f"{tag}: unknown platform {p!r}"
            for p in r.get("compatible_platform_ids") or []
            if p not in platform_ids
        ]

    ours = {r["id"] for r in tables.get("power_bands", []) if r.get("ours")}
    for r in tables.get("power_bands", []):
        errs += [
            f"taxonomy power_bands {r.get('id')}: maps_to {m!r} is not one of our bands"
            for m in r.get("maps_to") or []
            if m not in ours
        ]

    defs = ids("charging_definitions")
    for r in tables.get("charging_definitions", []):
        rb = r.get("replaced_by")
        if rb is not None and rb not in defs:
            errs.append(f"taxonomy charging_definitions {r.get('id')}: unknown replaced_by {rb!r}")
    return errs
