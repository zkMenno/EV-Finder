"""START §3 item 6: profile-field quality report and the out-of-sample consumption check."""

from __future__ import annotations

import pytest

from ev_pipeline.backtest.epa import consumption_oos
from ev_pipeline.derive import consumption as cm
from ev_pipeline.qa import profile_fields as pf

CFG = pf.load_config()
PARAMS = cm.load_params()


def _cells(wh: dict[str, float], heater: str | None = None) -> list[dict]:
    out = []
    for tb, k in (("t1", 1.5), ("t5", 1.0)):
        for road, w in wh.items():
            c = {"road_band": road, "temperature_band_id": tb, "wh_km": w * k, "rung": "wltp-ratio"}
            if heater:
                c["heater_type_id"] = heater
            out.append(c)
    return out


def _model(vid: str, kwh: float = 60.0, **kw) -> dict:
    cells = _cells({"town": 150, "rural": 150, "motorway": 150})
    return {"variant_id": vid, "usable_kwh": kwh, "cells": cells, "heat_pump": None} | kw


def test_matrix_view_ranges_and_motorway() -> None:
    v = pf.matrix_view(_model("a"), CFG)
    assert v["mild_range_km"] == 400 and v["winter_range_km"] == round(60000 / 225)
    assert v["motorway_mild_wh_km"] == 150 and v["rungs"] == ["wltp-ratio"]


def test_heat_pump_option_reads_the_worse_heater() -> None:
    cells = _cells({"town": 150, "rural": 150, "motorway": 150}, "heat-pump") + _cells(
        {"town": 200, "rural": 200, "motorway": 200}, "resistive"
    )
    opt = pf.matrix_view(_model("a", cells=cells, heat_pump="option"), CFG)
    std = pf.matrix_view(_model("a", cells=cells, heat_pump="standard"), CFG)
    assert opt["heater"] == "resistive" and opt["mild_range_km"] == 300
    assert std["heater"] == "heat-pump" and std["mild_range_km"] == 400


def test_section_flags_catalogue_vs_matrix_gaps() -> None:
    rows = [
        {"variant_id": "a", "real_range_km": 400, "dc_km_per_20min": 300, "dc_avg_10_80_kw": 135,
         "battery_kwh_net": 100, "dc_curve_status": "default"},
        {"variant_id": "b", "real_range_km": 520, "dc_km_per_20min": 400, "dc_avg_10_80_kw": 135,
         "battery_kwh_net": 100, "dc_curve_status": "estimated"},
        {"variant_id": "c", "real_range_km": 300},
    ]  # fmt: skip
    matrix = {"variants": [_model("a"), _model("b")]}
    sec = pf.profile_fields_section({"rows": rows}, matrix, None, CFG)
    rr = sec["real_range_km"]["vs_matrix_mild_range"]
    assert rr["n"] == 2 and rr["outside_tolerance"] == 1 and rr["worst"][0]["variant_id"] == "b"
    dc = sec["dc_km_per_20min"]["consumption_vs_matrix_motorway"]
    # a: 45 kWh in 20 min / 300 km = 150 Wh/km = matrix; b: 112.5 Wh/km = 0.75
    assert dc["worst"][0] == {"variant_id": "b", "ratio": 0.75}
    assert sec["winter_range_km"]["coverage"] == 2 and sec["dc_km_per_20min"]["proxy"] is None
    md = "\n".join(pf.profile_fields_md(sec))
    assert "1 of 2 differ by more than 10 %" in md and "not validated" in md


def test_section_without_matrix_or_backtest() -> None:
    sec = pf.profile_fields_section({"rows": [{"variant_id": "a"}]}, None, None, CFG)
    assert sec["winter_range_km"]["coverage"] == 0
    assert sec["real_range_km"]["vs_matrix_mild_range"] == {"n": 0}
    assert "no pairs" in "\n".join(pf.profile_fields_md(sec))


def _res(model: str, body: str, pred: float, meas: float, band: str = "town") -> dict:
    return {"variant_id": f"{model}-v", "model_id": model, "body": body, "band": band,
            "predicted_wh_km": pred, "measured_wh_km": meas}  # fmt: skip


def test_oos_scales_by_the_ratio_fitted_without_the_model() -> None:
    res = [_res(f"m{i}", "sedan", 100, 100) for i in range(5)] + [_res("odd", "sedan", 100, 150)]
    out = {r["model_id"]: r for r in consumption_oos(res, PARAMS, min_models=3)}
    # all models: median ratio 1.0; without "odd" also 1.0 -> odd keeps its 100 (error -33 %)
    assert out["odd"]["error_pct"] == pytest.approx(-33.33, abs=0.01)
    # without m0 the median of the rest (1,1,1,1,1.5) is still 1 -> unchanged
    assert out["m0"]["error_pct"] == 0


def test_oos_falls_back_to_band_wide_for_small_classes() -> None:
    res = [_res(f"s{i}", "sedan", 100, 120) for i in range(4)] + [_res("v", "van", 100, 100)]
    out = {r["model_id"]: r for r in consumption_oos(res, PARAMS, min_models=3)}
    # van has no other van model -> band-wide pool; without v: ratio 1.2, all: 1.2 -> pred 100
    assert out["v"]["predicted_wh_km"] == 100.0
    assert len(out) == 5
