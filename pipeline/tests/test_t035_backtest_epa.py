"""T-035: proxy back-test on EPA figures (range + consumption), regressions, audit report."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ev_pipeline.backtest import epa
from ev_pipeline.derive import consumption as cm

PARAMS = cm.load_params()


def _row(vid: str, **kw: Any) -> dict[str, Any]:
    base = {
        "variant_id": vid,
        "model_id": vid.rsplit("-", 1)[0],
        "body": "sedan",
        "wltp_range_km": 500,
        "real_range_km": 400.0,
        "real_range_rung": "body-ratio",
        "consumption_kwh_100km": 15.0,
        "battery_kwh_net": 60,
        "provenance": {
            "wltp_range_km": {"source_ids": ["eea"]},
            "consumption_kwh_100km": {"source_ids": ["eea"]},
        },
    }
    return base | kw


def _fact(vid: str, rec: str, km: float) -> dict[str, Any]:
    return {"subject_type": "variant", "subject_id": vid, "field": "epa_range_km",
            "value": km, "source": {"id": "fueleconomy"}, "source_record": rec}  # fmt: skip


def test_range_check_error_and_leak_guard() -> None:
    rows = [
        _row("a-m-1"),
        _row("b-m-1", provenance={"wltp_range_km": {"source_ids": ["fueleconomy"]}}),  # leak
        _row("c-m-1", real_range_km=None),
    ]
    facts = [_fact("a-m-1", "r1", 380), _fact("a-m-1", "r2", 420), _fact("b-m-1", "r3", 300),
             _fact("c-m-1", "r4", 300)]  # fmt: skip
    res = epa.range_check(rows, facts)
    assert [r["variant_id"] for r in res] == ["a-m-1"]
    assert res[0]["measured_km"] == 400 and res[0]["error_pct"] == 0 and res[0]["epa_records"] == 2


def test_consumption_check_hides_own_tests() -> None:
    rows = [_row("a-m-1")]
    model = cm.variant_model(rows[0], [], PARAMS, 0, "")
    assert model is not None
    town_pred = next(
        c["wh_km"] for c in model["cells"]
        if c["road_band"] == "town" and c["temperature_band_id"] == "t5"
    )  # fmt: skip
    wall = town_pred / PARAMS["wall_to_battery"]
    tests = {"a-m-1": [{"id": "x", "road_band": "town", "consumption_wh_km": wall,
                        "energy_basis": "wall", "source": {"id": "fueleconomy"}}]}  # fmt: skip
    res = epa.consumption_check(rows, tests, PARAMS)
    assert len(res) == 1 and res[0]["band"] == "town" and abs(res[0]["error_pct"]) < 0.1


def test_report_groups_top40_and_gate() -> None:
    results = [
        {"variant_id": f"m{i}-g-v", "model_id": "m1" if i < 3 else "m2", "body": "suv",
         "error_pct": e}
        for i, e in enumerate([5.0, -4.0, 6.0, 30.0, 25.0])
    ]  # fmt: skip
    r = epa._report(results, ["m1", "m3"])
    assert r["median_abs_pct"] == 6.0 and r["status"] == "pass"
    assert r["top40"]["models_with_data"] == 1 and r["top40"]["missing"] == ["m3"]
    assert r["worst"][0]["error_pct"] == 30.0
    assert epa._report([], [])["status"] == "skipped"


def test_regressions_flag_models_that_got_worse() -> None:
    cur = {"by_model": {"m1": {"median_abs_pct": 9.0}, "m2": {"median_abs_pct": 5.0}}}
    prev = {"by_model": {"m1": {"median_abs_pct": 5.5}, "m2": {"median_abs_pct": 4.0}}}
    assert epa.regressions(cur, prev) == [{"model_id": "m1", "previous": 5.5, "now": 9.0}]
    assert epa.regressions(cur, None) == []


def test_epa_backtest_end_to_end_and_audit(tmp_path: Path) -> None:
    (tmp_path / "seed").mkdir()
    (tmp_path / "seed" / "top40.yaml").write_text("models:\n- model_id: a-m\n- model_id: z-z\n")
    cat = {"rows": [_row("a-m-1")]}
    facts = [_fact("a-m-1", "r1", 380)]
    prev = {"range": {"by_model": {"a-m": {"median_abs_pct": 0.0}}}}
    bt = epa.epa_backtest(cat, facts, tmp_path, lambda s: True, prev)
    assert bt["kind"] == "proxy" and bt["range"]["n"] == 1
    assert bt["range"]["top40"]["models_with_data"] == 1
    assert bt["regressions"] and bt["regressions"][0]["check"] == "range"
    assert bt["range"]["status"] == "flag"  # regression flips a pass
    assert bt["consumption"]["status"] == "skipped"  # no staged tests
    md = epa.audit_md(bt, 1, "t")
    assert "A-30" in md and "proxy" in md and "Regressions" in md
    assert epa.epa_backtest(cat, facts, tmp_path, lambda s: False)["status"] == "skipped"


def test_qa_json_carries_the_section(tmp_path: Path, monkeypatch: Any) -> None:
    import shutil
    from datetime import UTC, datetime

    from ev_pipeline.release.build import release_cmd

    fix = Path(__file__).parent / "fixtures" / "release"
    d = tmp_path / "data"
    (d / "seed").mkdir(parents=True)
    shutil.copytree(fix / "staging", d / "staging")
    shutil.copytree(fix / "taxonomy", d / "taxonomy")
    for n in ("models", "variants", "platforms", "battery_packs", "variant_links"):
        shutil.copy(fix / f"{n}.yaml", d / "seed" / f"{n}.yaml")
    for n in ("sources", "field_sources"):
        shutil.copy(fix / f"{n}.yaml", d / f"{n}.yaml")
    monkeypatch.setenv("EV_DATA_DIR", str(d))
    monkeypatch.delenv("EV_RUNS_DIR", raising=False)
    assert release_cmd(False, data_dir=d, now=datetime(2026, 11, 15, 1, tzinfo=UTC)) == 0
    qa = json.loads((d / "releases" / "1" / "qa.json").read_text())
    assert "backtest_epa" in qa and qa["backtest_epa"].get("kind") in ("proxy", None)
    from ev_pipeline.backtest.__main__ import main

    assert main(["epa-report", str(d / "releases" / "1")]) == 0
