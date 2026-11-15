"""T-033: per-variant consumption matrix (3 road bands x 5 temperature bands) for Trip fit.

Inputs: the release rows (WLTP `consumption_kwh_100km`, usable kWh, weight, body, heat pump),
the condition-tagged tests from staging (T-032: today EPA city/highway from fueleconomy.gov,
attached to a variant through the release fact of the same source record), and the
parameters in `consumption_params.yaml` (all estimates, see that file).

Per variant, a reference figure per road band at 20 °C (battery basis, auxiliaries in):
- `measured`: the variant's own test for that band (EPA city -> town, highway -> rural;
  median when several US records match);
- `physics`: motorway from the variant's EPA highway figure x a drag-based speed factor;
- `wltp-ratio`: WLTP combined x a body-class ratio per band (no test for the band).
(`platform` rung: not built yet; needs pack/platform-level tests.)

Then each temperature band: traction x (1 + k (20 - T)) + (aux + heating / COP + cooling) / v.
Heating is time-based, so it costs more per km in town than on the motorway. Heat pump
`option` gives two cell sets (heater_type_id on the cells); unknown fitment uses `unknown`.
A car's own test at that temperature would replace a cell (no licence-clean winter tests yet).

Output: `consumption_matrix.json`, `estimate: true` at the top: every cell is a model output.
"""

from __future__ import annotations

import gzip
import json
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

PARAMS_FILE = Path(__file__).with_name("consumption_params.yaml")
TESTS_GLOB = "*.consumption_tests.jsonl"
FILE_NAME = "consumption_matrix.json"
BANDS = ("town", "rural", "motorway")
HEATERS_FOR_FITMENT = {
    "standard": ["heat-pump"],
    "none": ["resistive"],
    "option": ["heat-pump", "resistive"],
}
REFERENCE_C = 20.0


@dataclass
class MatrixResult:
    document: dict[str, Any] | None = None
    inputs: list[dict[str, Any]] = field(default_factory=list)
    log: dict[str, Any] = field(default_factory=dict)


def load_params(path: Path = PARAMS_FILE, taxonomy_dir: Path | None = None) -> dict[str, Any]:
    p = yaml.safe_load(path.read_text(encoding="utf-8"))
    for table in ("temperature_bands", "heater_types"):  # WS3 taxonomy rows win (same ids)
        f = taxonomy_dir / f"{table}.yaml" if taxonomy_dir else None
        if f and f.exists():
            rows = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
            rows = rows.get(table) or rows.get("rows") or rows if isinstance(rows, dict) else rows
            if isinstance(rows, list) and rows:
                p[table] = rows
                p.setdefault("_from_taxonomy", []).append(table)
    return p


def load_tests(staging: Path) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    """source_record -> tests; plus input log entries."""
    by_record: dict[str, list[dict[str, Any]]] = defaultdict(list)
    inputs = []
    for path in sorted(staging.glob(TESTS_GLOB)) if staging.is_dir() else []:
        n = 0
        for ln in path.read_text(encoding="utf-8").splitlines():
            if ln.strip():
                t = json.loads(ln)
                by_record[str(t["source_record"])].append(t)
                n += 1
        inputs.append({"path": str(path), "records": n})
    return by_record, inputs


def tests_by_variant(
    facts: list[dict[str, Any]],
    tests: dict[str, list[dict[str, Any]]],
    releasable: Any,
) -> dict[str, list[dict[str, Any]]]:
    """Attach tests to variants: a test's source record was matched to a variant when the
    release holds a variant fact from the same source and record."""
    record_to_variant: dict[tuple[str, str], str] = {}
    for f in facts:
        if f.get("subject_type") == "variant" and f.get("source_record"):
            src = (f.get("source") or {}).get("id") or f.get("source_id")
            record_to_variant.setdefault((str(src), str(f["source_record"])), f["subject_id"])
    out: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for rec, ts in tests.items():
        for t in ts:
            sid = str(t["source"]["id"])
            vid = record_to_variant.get((sid, rec))
            if vid and releasable(sid):
                out[vid].append({**t, "variant_id": vid})
    return out


def _ratio_key(body: Any, params: dict[str, Any]) -> str:
    return str((params.get("body_class") or {}).get(str(body or "").lower(), "default"))


def _wltp_ok(row: dict[str, Any]) -> bool:
    prov = (row.get("provenance") or {}).get("consumption_kwh_100km") or {}
    ids = set(prov.get("source_ids") or [])
    return bool(row.get("consumption_kwh_100km")) and bool(ids - {"model-estimate"})


def reference(
    row: dict[str, Any], tests: list[dict[str, Any]], params: dict[str, Any]
) -> dict[str, tuple[float, str, list[str]]] | None:
    """band -> (battery Wh/km at 20 °C, rung, test ids). None when nothing to start from."""
    w2b = float(params["wall_to_battery"])
    key = _ratio_key(row.get("body"), params)
    out: dict[str, tuple[float, str, list[str]]] = {}
    for band in ("town", "rural"):
        ts = [t for t in tests if t.get("road_band") == band]
        if ts:
            wh = statistics.median(float(t["consumption_wh_km"]) for t in ts)
            basis = w2b if ts[0].get("energy_basis") == "wall" else 1.0
            out[band] = (wh * basis, "measured", sorted(str(t["id"]) for t in ts))
    if "rural" in out:
        f = params["epa_motorway_over_highway"]
        out["motorway"] = (out["rural"][0] * float(f.get(key, f["default"])), "physics",
                           out["rural"][2])  # fmt: skip
    if len(out) < 3:
        if not _wltp_ok(row):
            return None  # no complete reference without WLTP
        comb = float(row["consumption_kwh_100km"]) * 10 * w2b  # kWh/100km -> Wh/km, battery
        ratios = params["wltp_band_ratio"].get(key, params["wltp_band_ratio"]["default"])
        for band in BANDS:
            out.setdefault(band, (comb * float(ratios[band]), "wltp-ratio", []))
    return out


def cell_wh_km(ref_wh: float, band: str, temp_c: float, heater: str, p: dict[str, Any]) -> float:
    v = float(p["band_speed_kmh"][band])
    aux = float(p["aux_w"])
    traction = max(ref_wh - aux / v, 0.5 * ref_wh)
    h = p["heating"]
    heat_w = float(h["resistive_w_per_c"]) * max(0.0, float(h["comfort_c"]) - temp_c)
    heat_w /= float(h["cop"].get(heater, h["cop"]["unknown"]))
    cool_w = float(h["cooling_w_per_c"]) * max(0.0, temp_c - float(h["cooling_from_c"]))
    factor = 1 + float(p["traction_per_c"]) * max(0.0, REFERENCE_C - temp_c)
    return traction * factor + (aux + heat_w + cool_w) / v


def variant_model(
    row: dict[str, Any],
    tests: list[dict[str, Any]],
    params: dict[str, Any],
    release: int,
    generated_at: str,
) -> dict[str, Any] | None:
    ref = reference(row, tests, params)
    if ref is None:
        return None
    fitment = row.get("heat_pump") or "not-disclosed"
    heaters = HEATERS_FOR_FITMENT.get(str(fitment), ["unknown"])
    cells = []
    for heater in heaters:
        for tb in sorted(params["temperature_bands"], key=lambda t: t.get("order", 0)):
            for band in BANDS:
                ref_wh, rung, ids = ref[band]
                wh = cell_wh_km(ref_wh, band, float(tb["representative_c"]), heater, params)
                sp = float(params["spread"][rung])
                cell: dict[str, Any] = {
                    "road_band": band,
                    "temperature_band_id": tb["id"],
                    "wh_km": round(wh, 1),
                    "p10_wh_km": round(wh * (1 - sp), 1),
                    "p90_wh_km": round(wh * (1 + sp), 1),
                    "rung": rung,
                    "confidence": params["confidence"][rung],
                }
                if len(heaters) > 1:
                    cell["heater_type_id"] = heater
                if ids:
                    cell["test_ids"] = ids
                cells.append(cell)
    heater_rows = {h["id"]: h for h in params["heater_types"]}
    warm = heater_rows.get(heaters[0] if len(heaters) == 1 else "unknown", {}).get("warm_up_kwh")
    return {
        "variant_id": row["variant_id"],
        "release": release,
        "model_version": str(params["model_version"]),
        "heat_pump": fitment if fitment in HEATERS_FOR_FITMENT else "not-disclosed",
        "usable_kwh": row.get("battery_kwh_net"),
        "mass_kg": row.get("weight_kg"),
        "warm_up_kwh": warm,
        "regen_recovery": float(params["climb_regen_recovery"]),
        "drivetrain_efficiency": float(params["drivetrain_efficiency"]),
        "cells": cells,
        "generated_at": generated_at,
    }


def build_matrix(
    rows: list[dict[str, Any]],
    facts: list[dict[str, Any]],
    staging: Path,
    releasable: Any,
    sources: dict[str, dict[str, Any]],
    release: int,
    generated_at: str,
    taxonomy_dir: Path | None = None,
) -> MatrixResult:
    out = MatrixResult()
    params = load_params(taxonomy_dir=taxonomy_dir)
    tests, out.inputs = load_tests(staging)
    by_variant = tests_by_variant(facts, tests, releasable)
    models = []
    rungs: Counter[str] = Counter()
    skipped = 0
    used_tests: dict[str, dict[str, Any]] = {}
    for row in sorted(rows, key=lambda r: r["variant_id"]):
        m = variant_model(row, by_variant.get(row["variant_id"], []), params, release,
                          generated_at)  # fmt: skip
        if m is None:
            skipped += 1
            continue
        models.append(m)
        for cell in m["cells"]:
            rungs[cell["rung"]] += 1
        for t in by_variant.get(row["variant_id"], []):
            used_tests[t["id"]] = t
    if not models:
        out.log = {"status": "nothing to model", "variants_skipped": skipped}
        return out
    cited = sorted({str(t["source"]["id"]) for t in used_tests.values()})
    wltp_sources = sorted(
        {
            s
            for r in rows
            for s in ((r.get("provenance") or {}).get("consumption_kwh_100km") or {}).get(
                "source_ids"
            )
            or []
            if s != "model-estimate"
        }
    )
    doc = {
        "release": release,
        "generated_at": generated_at,
        "model_version": str(params["model_version"]),
        "estimate": True,
        "note": "Model output: every cell is an estimate (rung + confidence per cell). "
        "Parameters: pipeline/ev_pipeline/derive/consumption_params.yaml.",
        "road_bands": list(BANDS),
        "band_speed_kmh": params["band_speed_kmh"],
        "temperature_bands": params["temperature_bands"],
        "heater_types": params["heater_types"],
        "params": {
            "wall_to_battery": params["wall_to_battery"],
            "climb_regen_recovery": params["climb_regen_recovery"],
            "drivetrain_efficiency": params["drivetrain_efficiency"],
        },
        "sources": [sources[s] for s in sorted(set(cited) | set(wltp_sources)) if s in sources]
        + [{"id": "model-estimate", "name": "EV Finder estimate models", "licence": "CC-BY-4.0"}],
        "tests": [
            {k: v for k, v in t.items() if k != "source_record"}
            | {"source": {"id": t["source"]["id"]}}
            for t in sorted(used_tests.values(), key=lambda t: t["id"])
        ],
        "variants": models,
    }
    raw = json.dumps(doc, separators=(",", ":"), ensure_ascii=False).encode()
    out.document = doc
    out.log = {
        "status": "shipped",
        "variants": len(models),
        "variants_skipped": skipped,
        "cells_by_rung": dict(sorted(rungs.items())),
        "tests_used": len(used_tests),
        "bytes": len(raw),
        "gzip_bytes": len(gzip.compress(raw, mtime=0)),
        "params_from_taxonomy": params.get("_from_taxonomy", []),
    }
    return out
