"""T-153 checks: G-48 (seed vs built), G-49 (verify refuses during refresh), G-50
(validate_variants warns on `cited:` values from a blocked source). No network."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import pytest

from ev_pipeline.refresh import lock, runner
from ev_pipeline.verify.run import report_md, seed_mismatches, verify

REPO = Path(__file__).resolve().parents[2]

SEED = {
    "variants": [
        {"id": "kia-ev3-gen1-standard", "drivetrain": "fwd",
         "cited": {"wltp_range_km": {"value": 436}}},
        {"id": "kia-ev3-gen1-long", "drivetrain": "fwd"},
    ]
}  # fmt: skip


def _cat(*rows: dict) -> dict:
    return {"rows": list(rows)}


# --- G-48 -------------------------------------------------------------------------------


def test_seed_check_flags_drivetrain_and_wltp_off_cited() -> None:
    cat = _cat(
        {"variant_id": "kia-ev3-gen1-standard", "drivetrain": "awd", "wltp_range_km": 583},
        {"variant_id": "kia-ev3-gen1-long", "drivetrain": "fwd", "wltp_range_km": 600},
    )
    bad = seed_mismatches(cat, SEED)
    assert bad == [
        "kia-ev3-gen1-standard: drivetrain awd, seed says fwd",
        "kia-ev3-gen1-standard: WLTP 583 km, its cited WLTP is 436 km (> 10 % off)",
    ]


def test_seed_check_covers_year_bands_and_passes_within_10_percent() -> None:
    cat = _cat(
        {"variant_id": "kia-ev3-gen1-standard", "drivetrain": "fwd", "wltp_range_km": 470},
        {"variant_id": "kia-ev3-gen1-standard-2026", "drivetrain": "awd", "wltp_range_km": 436},
        # another variant whose id merely starts with the seed id is not a band
        {"variant_id": "kia-ev3-gen1-standard-plus", "drivetrain": "awd"},
    )
    assert seed_mismatches(cat, SEED) == [
        "kia-ev3-gen1-standard-2026: drivetrain awd, seed says fwd"
    ]
    assert seed_mismatches(None, SEED) == [] and seed_mismatches(cat, None) == []


# --- G-49 -------------------------------------------------------------------------------


def test_lock_held_during_block_and_removed_after(tmp_path: Path) -> None:
    assert lock.holder(tmp_path) is None
    with lock.hold(tmp_path) as p:
        assert p == tmp_path / "staging" / ".refresh.lock"
        h = lock.holder(tmp_path)
        assert h is not None and h["pid"] == os.getpid()
        assert "ev refresh is still writing data/staging" in (lock.refusal(tmp_path) or "")
    assert not p.exists() and lock.refusal(tmp_path) is None


def test_stale_lock_is_not_held(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    p = lock.lock_path(tmp_path)
    p.parent.mkdir(parents=True)
    p.write_text(json.dumps({"pid": 4242, "started": "2026-11-19T01:00:00+00:00"}))
    monkeypatch.setattr(lock, "_alive", lambda pid: False)
    assert lock.holder(tmp_path) is None
    monkeypatch.setattr(lock, "_alive", lambda pid: True)
    assert "process 4242 since 2026-11-19T01:00:00+00:00" in (lock.refusal(tmp_path) or "")


def test_verify_refuses_while_refresh_holds_staging(tmp_path: Path) -> None:
    with lock.hold(tmp_path):
        rep = verify(tmp_path, repo=tmp_path, skip_tests=True, tricky=[])
    assert rep.status == "fail" and rep.sections["rebuild"]["status"] == "refused"
    assert "Wait for it to finish" in rep.failures[0]
    assert "refused" in report_md(rep)


def test_refresh_holds_lock_except_dry_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(runner.c, "data_dir", lambda: tmp_path)
    seen: list[bool] = []

    def fake(opts: runner.RefreshOptions, deps: object = None) -> tuple[int, dict]:
        seen.append(lock.holder(tmp_path) is not None)
        return 0, {}

    monkeypatch.setattr(runner, "_refresh", fake)
    runner.refresh(runner.RefreshOptions())
    runner.refresh(runner.RefreshOptions(dry_run=True))
    assert seen == [True, False]
    assert not lock.lock_path(tmp_path).exists()


# --- G-50 -------------------------------------------------------------------------------


def _validator():
    spec = importlib.util.spec_from_file_location(
        "validate_variants", REPO / "data" / "seed" / "validate_variants.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_validator_warns_on_cited_from_blocked_source(tmp_path: Path) -> None:
    sources = tmp_path / "sources.yaml"
    sources.write_text(
        "sources:\n  - {id: maker-docs, status: blocked}\n  - {id: rdw, status: active}\n"
    )
    doc = {
        "variants": [
            {"id": "a", "cited": {"power_kw": {"value": 1}, "wltp_range_km": {"value": 2}}},
            {"id": "b", "cited": {"power_kw": {"value": 1, "source_id": "rdw"}}},
            {"id": "c"},
        ]
    }
    w = _validator().blocked_cited(doc, sources)
    assert len(w) == 1 and w[0].startswith("a: cited power_kw, wltp_range_km use blocked")
    assert "data/manual" in w[0]
