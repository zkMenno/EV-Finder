"""Winter range per variant in the release rows (T-072).

`real_range_winter_km` = usable kWh / winter mixed-driving Wh/km from the consumption
matrix (T-033, Decision 041). It uses the shortlist's own `derived_values` and params, so the
figure on a card and the one the shortlist scores with are always the same number.

Every value is an estimate: the matrix temperature step (heating, traction) is not validated
against winter road tests yet (Q-059). Rows without a matrix entry stay empty ("not known").
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ev_pipeline.derive.rows import ESTIMATE_SOURCE, prov
from ev_pipeline.derive.shortlist import PARAMS_FILE, derived_values, load_params

FIELD = "real_range_winter_km"
# Row fields the matrix reference reads; their sources become this value's sources.
INPUT_FIELDS = ("battery_kwh_net", "wltp_range_km", "epa_range_km", "consumption_kwh_100km")


def band_labels(taxonomy_dir: Path) -> dict[str, str]:
    """English labels of the temperature bands (data/taxonomy/temperature_bands.yaml)."""
    path = taxonomy_dir / "temperature_bands.yaml"
    if not path.exists():
        return {}
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    items = (
        doc.get("bands") or doc.get("temperature_bands") or (doc if isinstance(doc, list) else [])
    )
    return {
        str(b["id"]): str((b.get("label") or {}).get("en") or b["id"])
        for b in items
        if isinstance(b, dict) and "id" in b
    }


def _note(params: dict[str, Any], band_label: str) -> str:
    mix = params["derived"]["road_mix"]
    road = "/".join(f"{k} {round(100 * float(v))} %" for k, v in mix.items())
    return (
        f"usable kWh / consumption matrix winter Wh/km ({band_label}; {road});"
        " temperature step not validated by winter road tests yet (Q-059)"
    )


def attach_winter_range(
    rows: list[dict[str, Any]],
    matrix: dict[str, Any] | None,
    params_path: Path = PARAMS_FILE,
    band_labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Set `real_range_winter_km` + provenance on rows in place; return a run-log section."""
    params = load_params(params_path)
    band = str(params["derived"]["winter_temperature_band"])
    note = _note(params, (band_labels or {}).get(band, f"temperature band {band}"))
    models = {m["variant_id"]: m for m in (matrix or {}).get("variants", [])}
    filled = 0
    for row in rows:
        row.pop(FIELD, None)
        row.get("provenance", {}).pop(FIELD, None)
        km = derived_values(row, models.get(row["variant_id"]), params).get("winter_range_km")
        if km is None:
            continue
        rp = row.get("provenance") or {}
        inputs = [rp[f] for f in INPUT_FIELDS if row.get(f) is not None and f in rp]
        sources = [s for p in inputs for s in p["source_ids"] if s != ESTIMATE_SOURCE]
        fact_ids = [f for p in inputs for f in p.get("fact_ids", [])]
        row[FIELD] = float(km)
        row.setdefault("provenance", {})[FIELD] = prov(
            sources, "low", fact_ids, derived=True, note=note, estimate=True
        )
        filled += 1
    return {"variants": len(rows), "filled": filled, "band": band, "note": note}
