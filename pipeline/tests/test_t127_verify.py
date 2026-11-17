"""T-127: `ev verify` on the release fixture (no network, no pytest recursion)."""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

import pytest

from ev_pipeline.release.build import release_cmd
from ev_pipeline.verify.run import check_claims, load_tricky, report_md, spot_checks, verify

FIX = Path(__file__).parent / "fixtures" / "release"
NOW = datetime(2026, 11, 15, 1, tzinfo=UTC)
TRICKY = [{"id": "citroen-e-c4*", "why": "test"}, {"id": "xpeng-p7*", "why": "absent"}]


@pytest.fixture
def data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    d = tmp_path / "data"
    (d / "seed").mkdir(parents=True)
    shutil.copytree(FIX / "staging", d / "staging")
    shutil.copytree(FIX / "taxonomy", d / "taxonomy")
    for n in ("models", "variants", "platforms", "battery_packs", "variant_links"):
        shutil.copy(FIX / f"{n}.yaml", d / "seed" / f"{n}.yaml")
    for n in ("sources", "field_sources"):
        shutil.copy(FIX / f"{n}.yaml", d / f"{n}.yaml")
    monkeypatch.setenv("EV_DATA_DIR", str(d))
    monkeypatch.delenv("EV_RUNS_DIR", raising=False)
    assert release_cmd(False, data_dir=d, now=NOW) == 0
    return d


def test_same_inputs_pass_with_zero_blocking(data_dir: Path, tmp_path: Path) -> None:
    rep = verify(data_dir, repo=tmp_path, skip_tests=True, tricky=TRICKY, now=NOW)
    assert rep.status == "pass", rep.failures
    assert rep.sections["rebuild"]["release"] == 2
    assert rep.numbers["release_diff_blocking"] == 0 and rep.numbers["variants"] == 7
    assert rep.numbers["variants_previous"] == 7
    assert not (data_dir / "releases" / "2").exists()  # scratch only, data/ untouched
    assert rep.sections["changed_rules"]["files"] is None  # not a git repo
    md = report_md(rep)
    assert "verify-pipeline report: **pass**" in md and "variants: 7" in md
    assert "`xpeng-p7*`: no rows" in md and "Verified: verify-pipeline" in md


def test_changed_input_fails_on_release_diff(data_dir: Path, tmp_path: Path) -> None:
    p = data_dir / "staging" / "openev.records.jsonl"
    p.write_text(p.read_text().replace('"value": 46.3', '"value": 48.0'))
    rep = verify(data_dir, repo=tmp_path, skip_tests=True, tricky=TRICKY, now=NOW)
    assert rep.status == "fail" and rep.numbers["release_diff_blocking"] == 1
    assert any("release diff" in f for f in rep.failures)
    row = next(r for r in rep.sections["spot_checks"]["rows"] if r.get("changed"))
    assert row["values"]["battery_kwh_net"] == (46.3, 48.0)
    assert "**46.3 -> 48**" in report_md(rep)


def test_pr_body_claims_are_checked(data_dir: Path, tmp_path: Path) -> None:
    body = "Evidence:\n- variants: 8\n- release_diff_blocking: 0\n- other_thing: 3\n"
    rep = verify(data_dir, repo=tmp_path, skip_tests=True, tricky=TRICKY, pr_body=body, now=NOW)
    assert rep.status == "fail"
    assert rep.sections["claims"]["mismatches"] == ["variants: PR body says 8, report says 7"]


def test_no_staging_fails(data_dir: Path, tmp_path: Path) -> None:
    shutil.rmtree(data_dir / "staging")
    (data_dir / "staging").mkdir()
    rep = verify(data_dir, repo=tmp_path, skip_tests=True, tricky=TRICKY, now=NOW)
    assert rep.status == "fail" and "no recorded staging" in rep.failures[0]


def test_check_claims_formats() -> None:
    n = {"variants": 226, "backtest_epa_median_abs_pct": 8.9}
    assert check_claims("variants: 226\n* `backtest_epa_median_abs_pct` = 8.9", n) == []
    assert check_claims("> variants = 225", n) == ["variants: PR body says 225, report says 226"]
    assert check_claims("226 variants", n) == []  # prose isn't a claim


def test_spot_checks_notes() -> None:
    old = {"rows": [{"variant_id": "kia-ev6-a", "wltp_range_km": 400}]}
    new = {"rows": [{"variant_id": "kia-ev6-a", "wltp_range_km": 400, "real_range_km": 500},
                    {"variant_id": "kia-ev6-b", "battery_kwh_net": 77}]}  # fmt: skip
    rows = spot_checks(new, old, [{"id": "kia-ev6*", "why": ""}])
    a, b = rows
    assert "real range > WLTP x 1.1" in a["notes"] and "no battery" in a["notes"]
    assert a["changed"] == ["real_range_km", "battery_kwh_net"] or "real_range_km" in a["changed"]
    assert b["notes"] == ["new"]


def test_repo_tricky_list_loads() -> None:
    ids = [c["id"] for c in load_tricky()]
    assert {"kia-ev6*", "hyundai-ioniq-5*", "mg-mg4*", "tesla-model-y*", "xpeng-p7*"} <= set(ids)


def test_cli_writes_report(data_dir: Path, tmp_path: Path) -> None:
    from ev_pipeline.cli import main

    out = tmp_path / "r.md"
    rc = main(["verify", "--skip-tests", "--data-dir", str(data_dir), "--out", str(out)])
    assert rc == 0 and out.read_text().startswith("# verify-pipeline report: **pass**")
