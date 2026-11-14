#!/usr/bin/env python3
"""Validate data/seed/variants.yaml against data/seed/models.yaml.

Usage:
    python3 -I data/seed/validate_variants.py [variants.yaml] [models.yaml]

Defaults to the files next to this script. Stdlib + PyYAML only.
Exit code 0 = valid, 1 = errors found.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

HERE = Path(__file__).resolve().parent
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DRIVETRAINS = {"fwd", "rwd", "awd"}
CONFIDENCE = {"low", "medium", "high"}
YEAR_TOLERANCE = 1
TOP_KEYS = {"generation_id", "id", "name", "years", "drivetrain", "specs", "notes", "confidence"}
REQUIRED_KEYS = {"generation_id", "id", "name", "years", "drivetrain", "specs", "confidence"}
SOURCE_KEYS = {"id", "name", "licence", "attribution"}

# Allowed spec keys -> plausible (min, max), None = no range check beyond > 0.
SPEC_RANGES: dict[str, tuple[float, float] | None] = {
    "battery_kwh_net": (10, 150),
    "battery_kwh_gross": (10, 150),
    "wltp_range_km": (80, 900),
    "epa_range_km": (50, 900),
    "consumption_kwh_100km": (8, 40),
    "ac_kw": (2, 22),
    "dc_peak_kw": (20, 400),
    "dc_avg_10_80_kw": (15, 350),
    "power_kw": (20, 1100),
    "accel_0_100_s": (1.5, 25),
    "top_speed_kmh": (80, 350),
    "boot_l": (0, 2000),
    "frunk_l": (0, 300),
    "length_mm": (2500, 5500),
    "width_mm": (1400, 2300),
    "height_mm": (1200, 2200),
    "wheelbase_mm": (1500, 3500),
    "weight_kg": (600, 3500),
    "towing_kg": (0, 3500),
    "seats": (1, 9),
}
# Renault Zoe Q-motor (Chameleon charger) does 43 kW AC: the only known exception to the 22 kW cap.
AC_EXCEPTIONS = {"renault-zoe-ph1-q210", "renault-zoe-ph1-q90"}
AC_EXCEPTION_MAX = 43
PRICE_RE = re.compile(r"price|eur|gbp|msrp|cost", re.IGNORECASE)


def load_generations(models_path: Path) -> dict[str, tuple[int, int | None]]:
    data = yaml.safe_load(models_path.read_text(encoding="utf-8"))
    gens: dict[str, tuple[int, int | None]] = {}
    for make in data.get("makes", []):
        for model in make.get("models", []):
            for gen in model.get("generations", []):
                y0, y1 = gen["years"]
                gens[gen["id"]] = (y0, y1)
    return gens


def find_price_keys(obj: Any, path: str, errors: list[str]) -> None:
    if isinstance(obj, dict):
        for k, val in obj.items():
            if isinstance(k, str) and PRICE_RE.search(k):
                errors.append(f"{path}.{k}: price-like key not allowed")
            find_price_keys(val, f"{path}.{k}", errors)
    elif isinstance(obj, list):
        for i, val in enumerate(obj):
            find_price_keys(val, f"{path}[{i}]", errors)


def is_num(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def validate(variants_doc: Any, gens: dict[str, tuple[int, int | None]]) -> list[str]:
    errors: list[str] = []
    if not isinstance(variants_doc, dict):
        return ["top level must be a mapping"]
    src = variants_doc.get("source")
    if not isinstance(src, dict) or set(src) != SOURCE_KEYS:
        errors.append(f"source must have exactly keys {sorted(SOURCE_KEYS)}")
    elif src.get("id") != "seed-manual":
        errors.append("source.id must be 'seed-manual'")
    variants = variants_doc.get("variants")
    if not isinstance(variants, list) or not variants:
        return errors + ["variants must be a non-empty list"]
    find_price_keys(variants_doc, "$", errors)

    seen: set[str] = set()
    for i, v in enumerate(variants):
        where = f"variants[{i}]"
        if not isinstance(v, dict):
            errors.append(f"{where}: must be a mapping")
            continue
        vid = v.get("id")
        where = f"variants[{i}] ({vid})"
        missing = REQUIRED_KEYS - set(v)
        if missing:
            errors.append(f"{where}: missing keys {sorted(missing)}")
        extra = set(v) - TOP_KEYS
        if extra:
            errors.append(f"{where}: unknown keys {sorted(extra)}")

        gid = v.get("generation_id")
        if gid not in gens:
            errors.append(f"{where}: generation_id {gid!r} not in models.yaml")
        if not isinstance(vid, str) or not ID_RE.match(vid):
            errors.append(f"{where}: id must be lowercase-hyphen")
        elif isinstance(gid, str) and not vid.startswith(gid + "-"):
            errors.append(f"{where}: id must start with '{gid}-'")
        if vid in seen:
            errors.append(f"{where}: duplicate id")
        seen.add(vid)

        if not isinstance(v.get("name"), str) or not v.get("name", "").strip():
            errors.append(f"{where}: name must be a non-empty string")
        if v.get("drivetrain") not in DRIVETRAINS:
            errors.append(f"{where}: drivetrain must be one of {sorted(DRIVETRAINS)}")
        if v.get("confidence") not in CONFIDENCE:
            errors.append(f"{where}: confidence must be one of {sorted(CONFIDENCE)}")
        if "notes" in v and v["notes"] is not None and not isinstance(v["notes"], str):
            errors.append(f"{where}: notes must be a string")

        years = v.get("years")
        if not (isinstance(years, list) and len(years) == 2 and isinstance(years[0], int)
                and (years[1] is None or isinstance(years[1], int))):
            errors.append(f"{where}: years must be [start, end|null]")
        else:
            y0, y1 = years
            if y1 is not None and y1 < y0:
                errors.append(f"{where}: years end before start")
            if gid in gens:
                g0, g1 = gens[gid]
                if y0 < g0 - YEAR_TOLERANCE or (g1 is not None and y0 > g1 + YEAR_TOLERANCE):
                    errors.append(f"{where}: start {y0} outside generation span {g0}-{g1}")
                if y1 is not None:
                    if y1 < g0 - YEAR_TOLERANCE or (g1 is not None and y1 > g1 + YEAR_TOLERANCE):
                        errors.append(f"{where}: end {y1} outside generation span {g0}-{g1}")
                elif g1 is not None:
                    errors.append(f"{where}: open end but generation ended {g1}")

        specs = v.get("specs")
        if not isinstance(specs, dict):
            errors.append(f"{where}: specs must be a mapping")
            continue
        for k, val in specs.items():
            if k not in SPEC_RANGES:
                errors.append(f"{where}: spec key {k!r} not allowed")
                continue
            if val is None:
                continue
            if not is_num(val):
                errors.append(f"{where}: spec {k} must be a number or null")
                continue
            lo, hi = SPEC_RANGES[k]
            if k == "ac_kw" and vid in AC_EXCEPTIONS:
                hi = AC_EXCEPTION_MAX
            if not lo <= val <= hi:
                errors.append(f"{where}: spec {k}={val} outside plausible range {lo}-{hi}")
        net, gross = specs.get("battery_kwh_net"), specs.get("battery_kwh_gross")
        if is_num(net) and is_num(gross) and net > gross:
            errors.append(f"{where}: battery_kwh_net > battery_kwh_gross")
        if specs.get("seats") is not None and not isinstance(specs.get("seats"), int):
            errors.append(f"{where}: seats must be an integer")
    return errors


def main(argv: list[str]) -> int:
    variants_path = Path(argv[1]) if len(argv) > 1 else HERE / "variants.yaml"
    models_path = Path(argv[2]) if len(argv) > 2 else HERE / "models.yaml"
    gens = load_generations(models_path)
    doc = yaml.safe_load(variants_path.read_text(encoding="utf-8"))
    errors = validate(doc, gens)
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        print(f"{len(errors)} error(s)")
        return 1
    covered = {v["generation_id"] for v in doc["variants"]}
    uncovered = sorted(g for g in gens if g not in covered)
    print(f"OK: {len(doc['variants'])} variants across {len(covered)} of {len(gens)} generations")
    if uncovered:
        print("Generations without variants: " + ", ".join(uncovered))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
