"""T-035 back-test harness skeleton: leave-one-out over the real-range ratio ladder."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from ev_pipeline.backtest import harness as h
from ev_pipeline.backtest.__main__ import main

FIX = Path(__file__).parent / "fixtures" / "backtest"
TESTS = FIX / "synthetic-tests.jsonl"


def _tests() -> list[h.BackTest]:
    return h.load_tests([TESTS])


def test_fixture_rows_are_visibly_synthetic() -> None:
    for t in _tests():
        assert t.fixture is True
        assert t.source_id == "fixture-synthetic"
        assert "SYNTHETIC FIXTURE" in t.note
        assert t.make_id in {"testcar", "fixturemotors"}


def test_only_the_model_condition_is_scored() -> None:
    out = h.run_backtest(_tests())
    assert out["condition"] == h.MODEL_CONDITION
    assert out["scored"] == 8
    assert out["other_conditions"] == {"motorway-120": 1, "winter-mixed": 1}


def test_leave_one_out_never_uses_the_cars_own_test() -> None:
    out = h.run_backtest(_tests())
    rungs = {r["rung"] for r in out["worst"]} | set(out["by_rung"])
    assert not rungs & {"exact-test", "owner-data"}
    # alpha-50 is predicted from its sibling alpha-60 (mean of its two tests: 400 km), scaled
    # by WLTP 400/470 (T-124; battery 50/60 gave 333.3 km, -2.0 %, vs 340.4 km, +0.1 %).
    alpha50 = next(r for r in out["worst"] if r["variant_id"] == "testcar-alpha-gen1-50")
    assert alpha50["rung"] == "sibling-variant"
    assert alpha50["predicted_km"] == round(400 * 400 / 470, 1)


def test_report_groups_and_worst_ten() -> None:
    out = h.run_backtest(_tests())
    assert set(out["by_body"]) == {"hatchback", "sedan", "suv"}
    assert set(out["by_brand"]) == {"testcar", "fixturemotors"}
    assert "by_year_band" in out and "by_model" in out
    errs = [abs(r["error_pct"]) for r in out["worst"]]
    assert errs == sorted(errs, reverse=True) and len(errs) <= h.WORST_N
    assert out["median_abs_pct"] >= 0


def test_gate_flags_a_median_error_above_ten_percent() -> None:
    bad = [
        h.BackTest(
            f"t{i}",
            f"v{i}",
            f"g{i}",
            f"testmake{i}",
            "hatchback",
            "fwd",
            50,
            400,
            200,
            h.MODEL_CONDITION,
            "fixture-synthetic",
            fixture=True,
        )
        for i in range(3)
    ]
    out = h.run_backtest(bad)
    assert out["status"] == "flag" and out["median_abs_pct"] > 10
    # Body-ratio 0.85 x 400 = 340 vs 200 measured -> +70 %.
    assert out["worst"][0]["error_pct"] == 70.0


def test_nothing_to_score_is_skipped() -> None:
    assert h.run_backtest([])["status"] == "skipped"


def test_regression_guard() -> None:
    cur = {"by_model": {"m1": {"median_abs_pct": 9.0}, "m2": {"median_abs_pct": 5.0}}}
    prev = {"by_model": {"m1": {"median_abs_pct": 5.0}, "m2": {"median_abs_pct": 4.0}}}
    assert h.regressions(cur, prev) == [{"model_id": "m1", "previous": 5.0, "now": 9.0}]
    assert h.regressions(cur, None) == []


def test_release_section_skips_fixture_rows(tmp_path: Path) -> None:
    (tmp_path / "backtest").mkdir()
    shutil.copy(TESTS, tmp_path / "backtest" / "x.jsonl")
    out = h.release_backtest(tmp_path, lambda s: True)
    assert out["status"] == "skipped"
    assert out["left_out"] == {"fixture_rows": 10, "not_releasable_source": 0}


def test_release_section_without_tests_is_skipped(tmp_path: Path) -> None:
    out = h.release_backtest(tmp_path, lambda s: True)
    assert out["status"] == "skipped" and "no real" in out["note"]


def _as_real(tmp_path: Path, source_id: str) -> None:
    (tmp_path / "backtest").mkdir()
    lines = []
    for line in TESTS.read_text().splitlines():
        d = json.loads(line)
        d.update(fixture=False, source_id=source_id)
        lines.append(json.dumps(d))
    (tmp_path / "backtest" / "real.jsonl").write_text("\n".join(lines) + "\n")


def test_release_section_leaves_out_non_releasable_sources(tmp_path: Path) -> None:
    _as_real(tmp_path, "naf")
    out = h.release_backtest(tmp_path, lambda s: s != "naf")
    assert out["status"] == "skipped"
    assert out["left_out"]["not_releasable_source"] == 10


def test_release_section_runs_on_releasable_tests_and_checks_regressions(tmp_path: Path) -> None:
    _as_real(tmp_path, "cleared")
    prev = {"by_model": {"fixturemotors-three": {"median_abs_pct": 1.0}}}
    out = h.release_backtest(tmp_path, lambda s: True, prev)
    assert out["scored"] == 8
    assert out["regressions"] and out["regressions"][0]["model_id"] == "fixturemotors-three"
    assert out["status"] == "flag"


def test_cli_prints_report(capsys) -> None:
    assert main([str(TESTS)]) == 0
    assert json.loads(capsys.readouterr().out)["scored"] == 8
    assert main([]) == 2
