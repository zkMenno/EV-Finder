"""T-071 (Decision 047): derived WLTP consumption includes charging losses."""

from __future__ import annotations

from typing import Any

import pytest

from ev_pipeline.derive import metrics as m
from ev_pipeline.qa.profile_fields import derived_consumption_backtest, profile_fields_md


def _row(vid: str, cons: float | None, net: float, wltp: float, **prov: Any) -> dict[str, Any]:
    return {
        "variant_id": vid,
        "consumption_kwh_100km": cons,
        "battery_kwh_net": net,
        "wltp_range_km": wltp,
        "provenance": {
            "consumption_kwh_100km": {"derived": prov.get("cons_derived", False)},
            "wltp_range_km": {"estimate": prov.get("wltp_estimate", False)},
        },
    }


def test_estimate_is_wall_basis_not_battery_basis() -> None:
    # Model Y LR AWD 2022 type approval (RDW TGK, PR #60): 79 kWh net, WLTP 533 km, 16.9 kWh/100 km.
    battery_basis = 79 / 533 * 100
    est = m.consumption_estimate(79, 533)
    assert est == pytest.approx(battery_basis * m.WALL_PER_BATTERY_WLTP)
    assert abs(est - 16.9) / 16.9 < 0.03  # the old battery-basis figure was 12 % low


def test_factor_is_a_plausible_charging_loss() -> None:
    # 8-20 % AC charging losses are physically plausible; outside that the fit is broken.
    assert 1.08 <= m.WALL_PER_BATTERY_WLTP <= 1.20


def test_backtest_uses_only_official_consumption_with_a_real_wltp() -> None:
    rows = [
        _row("official", 16.9, 79, 533),
        _row("derived", 14.0, 79, 533, cons_derived=True),
        _row("epa-wltp", 16.9, 79, 533, wltp_estimate=True),
        _row("no-cons", None, 79, 533),
    ]
    bt = derived_consumption_backtest(rows)
    assert bt["n"] == 1
    assert bt["worst"][0]["variant_id"] == "official"
    assert bt["median_abs_pct"] < 3


def test_backtest_without_pairs_is_skipped_and_the_report_still_renders() -> None:
    assert derived_consumption_backtest([]) == {"n": 0, "status": "skipped"}
    sec = {
        "note": "n",
        "definitions": {"winter_temperature_band": "x"},
        "variants": 0,
        "winter_range_km": {"coverage": 0, "proxy_20c_consumption": None},
        "real_range_km": {"coverage": 0, "proxy_epa_range": None, "vs_matrix_mild_range": {}},
        "dc_km_per_20min": {
            "coverage": 0,
            "curve_status": {},
            "consumption_vs_matrix_motorway": {},
        },
        "consumption_kwh_100km": {
            "coverage": 0,
            "proxy_epa_in_sample": None,
            "proxy_epa_out_of_sample": None,
            "estimate_vs_official_wltp": {"n": 0, "status": "skipped"},
        },
    }
    assert "official WLTP: no data" in "\n".join(profile_fields_md(sec))
