"""Back-test edge cases (overnight coverage pass): tests the ladder cannot predict are listed,
not scored. SYNTHETIC BackTest rows built here (invented `testcar` make). No network.
"""

from __future__ import annotations

from ev_pipeline.backtest import harness as h


def _t(tid: str, vid: str, body: str | None, wltp: float | None, km: float) -> h.BackTest:
    return h.BackTest(
        test_id=tid,
        variant_id=vid,
        generation_id="testcar-gen1",
        make_id="testcar",
        body=body,
        drivetrain="fwd",
        battery_kwh_net=None,  # no battery: the sibling rung never applies
        wltp_km=wltp,
        measured_km=km,
        condition=h.MODEL_CONDITION,
        source_id="testsrc",
        model_id="testcar-a",
        model_year=2022,
        fixture=True,
    )


def test_unpredictable_tests_are_listed_not_scored() -> None:
    tests = [
        _t("t1", "v1", None, None, 300),  # no WLTP, no battery: nothing to go on
        _t("t2", "v2", "spaceship", 400, 320),  # unknown body, no brand ratio from others
    ]
    out = h.run_backtest(tests)
    assert out["status"] == "skipped"
    assert out["unpredictable"] == ["t1", "t2"]


def test_mixed_predictable_and_unpredictable() -> None:
    tests = [
        _t("t1", "v1", None, None, 300),
        _t("t2", "v2", "suv", 400, 330),
        _t("t3", "v3", "suv", 500, 410),
    ]
    out = h.run_backtest(tests)
    assert out["scored"] == 2 and out["unpredictable"] == ["t1"]
    assert set(out["by_rung"]) == {"brand-body-drivetrain-ratio"}
