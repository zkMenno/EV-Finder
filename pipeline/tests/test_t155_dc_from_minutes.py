"""T-155 item 1: DC fields from a sourced 10-80 % time when a variant has no charge curve.

Repro (G-51): Hyundai Ioniq 5 facelift base / AWD lost the pre-facelift car's 220 kW curve
(T-151) and kept only Hyundai UK's cited "18 minutes" 10-80 %, so dc_avg / km per 10-20 min
were empty and road-tripper said not-enough-data. SYNTHETIC facts on the test seed's Model 3.
"""

from __future__ import annotations

import pytest

from ev_pipeline.derive import metrics as m
from ev_pipeline.derive.rows import MINUTES_NOTE
from ev_pipeline.release.validate import provenance_errors
from ev_pipeline.schema_models import ChargeCurve
from tests.test_derive_edges import _curve_fact, _fact, _row


def test_avg_from_minutes_is_the_inverse_of_minutes_from_avg() -> None:
    for net, avg in ((84.0, 196.0), (46.3, 70.0), (62.0, 45.5)):
        assert m.avg_from_minutes(net, m.minutes_from_avg(net, avg)) == pytest.approx(avg)
    assert m.avg_from_minutes(84, 18) == pytest.approx(196.0)


def test_cited_minutes_without_curve_or_peak_give_average_and_km() -> None:
    row, problems = _row(
        [
            _fact("battery_kwh_net", 84, "kWh"),
            _fact("wltp_range_km", 507, "km"),
            _fact("dc_minutes_10_80", 18, "min", source="manual"),
        ]
    )
    assert problems == []
    assert row["dc_minutes_10_80"] == 18.0
    assert row["dc_avg_10_80_kw"] == 196.0
    assert row["dc_km_per_20min"] is not None and row["dc_km_per_20min"] > 0
    assert "dc_curve_status" not in row  # no curve was used
    pv = row["provenance"]
    assert pv["dc_avg_10_80_kw"]["derived"] is True
    assert pv["dc_avg_10_80_kw"]["note"] == MINUTES_NOTE
    assert "manual" in pv["dc_avg_10_80_kw"]["source_ids"]
    assert "10-80% time (manual" in pv["dc_km_per_20min"]["note"]
    assert provenance_errors([row]) == []


def test_cited_minutes_beat_the_default_curve_from_a_peak() -> None:
    row, _ = _row(
        [
            _fact("battery_kwh_net", 84, "kWh"),
            _fact("wltp_range_km", 507, "km"),
            _fact("dc_peak_kw", 250, "kW", source="eea"),
            _fact("dc_minutes_10_80", 18, "min", source="manual"),
        ]
    )
    assert row["dc_avg_10_80_kw"] == 196.0
    assert "dc_curve_status" not in row
    assert row["provenance"]["dc_avg_10_80_kw"]["note"] == MINUTES_NOTE


def test_a_curve_still_beats_the_minutes() -> None:
    curve = ChargeCurve.model_validate({"points": [[10, 100], [80, 100]], "status": "estimated"})
    row, _ = _row(
        [
            _fact("battery_kwh_net", 70, "kWh"),
            _fact("wltp_range_km", 500, "km"),
            _fact("dc_minutes_10_80", 18, "min", source="manual"),
            _curve_fact(curve),
        ]
    )
    assert row["dc_avg_10_80_kw"] == 100.0
    assert row["dc_curve_status"] == "estimated"
    assert row["dc_minutes_10_80"] == 18.0  # the sourced time is kept as is


def test_minutes_above_the_peak_go_to_review_not_the_row() -> None:
    row, problems = _row(
        [
            _fact("battery_kwh_net", 84, "kWh"),
            _fact("dc_peak_kw", 150, "kW", source="eea"),
            _fact("dc_minutes_10_80", 18, "min", source="manual"),
        ]
    )
    assert row["dc_avg_10_80_kw"] is None and row["dc_km_per_20min"] is None
    assert [p.field for p in problems] == ["dc_avg_10_80_kw"]


def test_minutes_without_battery_give_nothing() -> None:
    row, problems = _row([_fact("dc_minutes_10_80", 18, "min", source="manual")])
    assert row["dc_avg_10_80_kw"] is None and problems == []
