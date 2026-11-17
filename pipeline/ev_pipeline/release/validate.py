"""Validation for releases (T-006): range checks, schema checks, provenance and licence guards.

Enum-valued facts (iso15118_20_support, heat_pump) and drag_coefficient are checked against
their allowed values the same way (Decision 020): a bad value is dropped and listed.
Range checks run twice: on every matched fact before merging (so one bad value cannot win a
field) and on every derived value in a row. Anything out of range is dropped and listed in
data/review/validation.csv.
"""

from __future__ import annotations

import csv
import json
from collections.abc import Callable, Iterable
from functools import cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from ev_pipeline.match.matcher import EXCLUDED_SOURCES, MatchedFact, Problem
from ev_pipeline.schema_models import Catalogue, Fact

# Inclusive plausible ranges, metric units. Prices apply to EUR and GBP alike.
RANGES: dict[str, tuple[float, float]] = {
    "battery_kwh_net": (10, 150),
    "wltp_range_km": (80, 900),
    "consumption_kwh_100km": (10, 35),
    "ac_kw": (2, 43),  # Renault Zoe Q210/Q90 charge at 43 kW AC (coordinator)
    "ac_kw_optional": (2, 43),  # T-063: same physical limit as ac_kw
    "dc_peak_kw": (20, 400),
    "dc_avg_10_80_kw": (10, 300),
    "price_new": (5_000, 250_000),
    "boot_l": (0, 2000),
    "length_mm": (2500, 5500),
    "towing_kg": (0, 3500),
}

# Numeric PublishedVariant fields that must carry provenance when non-null.
ROW_NUMBER_FIELDS = (
    "battery_kwh_net",
    "wltp_range_km",
    "epa_range_km",
    "consumption_kwh_100km",
    "ac_kw",
    "ac_kw_optional",
    "dc_peak_kw",
    "dc_avg_10_80_kw",
    "ac_km_per_h",
    "dc_km_per_10min",
    "real_range_km",
    "power_kw",
    "accel_0_100_s",
    "boot_l",
    "length_mm",
    "weight_kg",
    "towing_kg",
    "seats",
    "registered_count_nl",
    "dc_minutes_10_80",
    "dc_km_per_20min",
    "dc_peak_held_min",
    "consumption_motorway_kwh_100km",
    "voltage_nominal_v",
    "voltage_max_v",
    "charger_400v_kw",
)

VALIDATION_COLUMNS = [
    "stage",
    "source_id",
    "record_key",
    "subject_id",
    "field",
    "value",
    "unit",
    "reason",
]

SCHEMA_PATH = Path(__file__).resolve().parents[3] / "packages" / "schema" / "schemas"
SCHEMA_FILE = SCHEMA_PATH / "ev.schema.json"


class ReleaseError(Exception):
    """Raised when a release must not be published."""


def in_range(field: str, value: object) -> bool:
    base = field.split(".")[0]
    bounds = RANGES.get(base)
    if bounds is None or isinstance(value, bool) or not isinstance(value, int | float):
        return True
    return bounds[0] <= value <= bounds[1]


def range_reason(field: str, value: object) -> str:
    lo, hi = RANGES[field.split(".")[0]]
    return f"out of range {lo:g}-{hi:g}: {value}"


# Enum-valued facts checked at release time, not in the schema (Decision 020): the allowed
# values come from these schema $defs, so a new value is a schema change, not a code change.
ENUM_FACTS: dict[str, str] = {
    "iso15118_20_support": "Iso15118Support",
    "heat_pump": "HeatPumpFitment",
}
NOT_DISCLOSED = "not-disclosed"
DRAG_COEFFICIENT = "drag_coefficient"  # Cd, a number strictly between 0 and 1


def allowed_values(field: str) -> tuple[str, ...] | None:
    def_name = ENUM_FACTS.get(field)
    if def_name is None:
        return None
    return tuple(_schema()["$defs"][def_name]["enum"])


def value_reason(field: str, value: object) -> str | None:
    """None when an enum / Cd fact holds an allowed value (or the field is not checked)."""
    allowed = allowed_values(field)
    if allowed is not None:
        if isinstance(value, str) and value in allowed:
            return None
        return f"not an allowed value ({', '.join(allowed)}): {value!r}"
    if field == DRAG_COEFFICIENT:
        if value == NOT_DISCLOSED:
            return None
        if isinstance(value, bool) or not isinstance(value, int | float) or not 0 < value < 1:
            return f"drag coefficient must be a number between 0 and 1: {value!r}"
    return None


def enum_fact_errors(facts: list[dict[str, Any]]) -> list[str]:
    """Last guard on the published facts list (pack and derived facts included)."""
    out = []
    for fd in facts:
        why = value_reason(str(fd.get("field")), fd.get("value"))
        if why is not None:
            out.append(f"fact {fd.get('id')}: {fd.get('field')} {why}")
    return out


def check_fact_ranges(facts: list[MatchedFact]) -> tuple[list[MatchedFact], list[Problem]]:
    keep: list[MatchedFact] = []
    dropped: list[Problem] = []
    for mf in facts:
        f = mf.fact
        why = value_reason(f.field.value, f.value)
        if why is not None:
            dropped.append(
                Problem(
                    "fact",
                    mf.source_id,
                    f.source_record or "",
                    f.subject_id.root if hasattr(f.subject_id, "root") else str(f.subject_id),
                    f.field.value,
                    str(f.value),
                    f.unit,
                    why,
                )
            )
        elif in_range(f.field.value, f.value):
            keep.append(mf)
        else:
            dropped.append(
                Problem(
                    "fact",
                    mf.source_id,
                    f.source_record or "",
                    f.subject_id.root if hasattr(f.subject_id, "root") else str(f.subject_id),
                    f.field.value,
                    str(f.value),
                    f.unit,
                    range_reason(f.field.value, f.value),
                )
            )
    return keep, dropped


def write_validation(path: Path, problems: Iterable[Problem]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(VALIDATION_COLUMNS)
        for p in problems:
            w.writerow([getattr(p, c) for c in VALIDATION_COLUMNS])
            n += 1
    return n


# --- schema validation -------------------------------------------------------------------


@cache
def _schema(path: Path = SCHEMA_FILE) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validator(def_name: str) -> Draft202012Validator:
    schema = dict(_schema())
    schema["$ref"] = f"#/$defs/{def_name}"
    return Draft202012Validator(schema)


def schema_errors(catalogue: dict[str, Any], facts: list[dict[str, Any]]) -> list[str]:
    """JSON Schema + generated Pydantic checks. Empty list means valid."""
    errors: list[str] = []
    cat_v = _validator("Catalogue")
    for e in sorted(cat_v.iter_errors(catalogue), key=lambda e: list(e.path)):
        errors.append(f"catalogue {'/'.join(map(str, e.path))}: {e.message}")
    try:
        Catalogue.model_validate(catalogue)
    except Exception as exc:  # pydantic ValidationError; message is what matters
        errors.append(f"pydantic Catalogue: {exc}")
    fact_v = _validator("Fact")
    for fd in facts:
        for e in fact_v.iter_errors(fd):
            errors.append(f"fact {fd.get('id')}: {e.message}")
        try:
            Fact.model_validate(fd)
        except Exception as exc:
            errors.append(f"pydantic Fact {fd.get('id')}: {exc}")
        if len(errors) > 50:
            break
    return errors


def provenance_errors(rows: list[dict[str, Any]]) -> list[str]:
    """Every non-null number in a row has a provenance entry (prices per country)."""
    errors: list[str] = []
    for row in rows:
        prov = row.get("provenance") or {}
        for f in ROW_NUMBER_FIELDS:
            if row.get(f) is not None and f not in prov:
                errors.append(f"{row['variant_id']}: {f} has no provenance")
        for cc in row.get("price_new") or {}:
            if f"price_new.{cc}" not in prov:
                errors.append(f"{row['variant_id']}: price_new.{cc} has no provenance")
        for cc, entries in (row.get("registrations") or {}).items():
            p = prov.get(f"registrations.{cc}")
            if p is None:
                errors.append(f"{row['variant_id']}: registrations.{cc} has no provenance")
                continue
            for e in entries:
                if e.get("source_id") not in p.get("source_ids", []):
                    errors.append(
                        f"{row['variant_id']}: registrations.{cc} count from {e.get('source_id')}"
                        " not in its provenance"
                    )
        for f, p in prov.items():
            if not p.get("source_ids"):
                errors.append(f"{row['variant_id']}: provenance {f} has no source")
    return errors


def excluded_source_errors(
    catalogue: dict[str, Any],
    facts: list[dict[str, Any]],
    releasable: Callable[[str], bool] | None = None,
) -> list[str]:
    """Last guard: no excluded or non-releasable source anywhere in the release."""

    def blocked(sid: str) -> bool:
        return sid in EXCLUDED_SOURCES or (releasable is not None and not releasable(sid))

    errors: list[str] = []
    for s in catalogue.get("sources", []):
        if blocked(s["id"]):
            errors.append(f"excluded source {s['id']} listed in sources")
    for row in catalogue.get("rows", []):
        for f, p in (row.get("provenance") or {}).items():
            bad = {s for s in p.get("source_ids", []) if blocked(s)}
            bad |= {
                fid.split(":", 1)[0]
                for fid in p.get("fact_ids", []) or []
                if blocked(fid.split(":", 1)[0])
            }
            if bad:
                errors.append(f"{row['variant_id']}: {f} uses excluded source {sorted(bad)}")
    for fd in facts:
        if blocked(fd["source"]["id"]):
            errors.append(f"fact {fd['id']} from excluded source")
    return errors


def licence_errors(sources: list[dict[str, Any]]) -> list[str]:
    """ODbL inputs never go into the CC BY release (AGENTS.md data rule 3)."""
    return [
        f"source {s['id']} has licence {s['licence']}: ODbL data cannot go into a CC BY release"
        for s in sources
        if "odbl" in s.get("licence", "").lower()
    ]
