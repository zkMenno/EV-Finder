"""Release QA edge cases (overnight coverage pass): provenance and licence-gate blocking
paths, diff on empty releases, percentile edges, top-model ranking by the UK fleet, and the
end-of-release step (previous release lookup, registration order, blocking failure).

Uses the SYNTHETIC QA fixture in fixtures/qa/ (invented `testcar` make, invented sources)
plus small dicts built here. No network.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from ev_pipeline.merge.policy import load_policies
from ev_pipeline.qa import checks as qc
from ev_pipeline.qa.release_step import _previous, finish_release, registration_order
from ev_pipeline.qa.report import overall_status, qa_document, run_qa
from ev_pipeline.release.gate import load_registry
from ev_pipeline.release.validate import ReleaseError

QA = Path(__file__).parent / "fixtures" / "qa"
REGISTRY = load_registry(QA / "sources.yaml")
POLICIES = load_policies(QA / "field_sources.yaml")
A50 = "testcar-alpha-gen1-50"


@pytest.fixture
def cat() -> dict[str, Any]:
    return json.loads((QA / "catalogue.json").read_text())


@pytest.fixture
def facts() -> list[dict[str, Any]]:
    return json.loads((QA / "facts.json").read_text())


def _row(cat: dict[str, Any], vid: str = A50) -> dict[str, Any]:
    return next(r for r in cat["rows"] if r["variant_id"] == vid)


def _errors(check: qc.Check) -> list[str]:
    return check.details["errors"]


# --- provenance (blocking) ---------------------------------------------------------------


def test_fact_with_unknown_confidence_fails(cat, facts) -> None:
    facts[0]["confidence"] = "pretty sure"
    c = qc.check_provenance(cat, facts)
    assert c.status == "fail" and c.blocking
    assert f"fact {facts[0]['id']}: missing confidence" in _errors(c)


def test_provenance_entry_without_sources_or_confidence_fails(cat, facts) -> None:
    p = _row(cat)["provenance"]["battery_kwh_net"]
    p["source_ids"] = []
    p["confidence"] = None
    p.pop("fact_ids")
    errs = _errors(qc.check_provenance(cat, facts))
    assert f"{A50}: battery_kwh_net has no source" in errs
    assert f"{A50}: battery_kwh_net has no confidence" in errs
    assert f"{A50}: battery_kwh_net has no date (no facts and no dated source)" in errs


def test_price_needs_provenance(cat, facts) -> None:
    del _row(cat)["provenance"]["price_new.NL"]
    assert f"{A50}: price_new.NL has no provenance" in _errors(qc.check_provenance(cat, facts))


def test_error_list_is_capped_but_count_is_complete(cat, facts) -> None:
    for i in range(qc.MAX_LISTED + 10):
        facts.append({"id": f"bad:{i}"})  # no source, licence, date or confidence
    c = qc.check_provenance(cat, facts)
    assert len(c.details["errors"]) == qc.MAX_LISTED
    assert c.details["error_count"] == 2 * (qc.MAX_LISTED + 10)


# --- licence gate (blocking) -------------------------------------------------------------


def test_odbl_source_in_catalogue_sources_fails(cat, facts) -> None:
    cat["sources"].append({"id": "testosm", "name": "ODbL", "licence": "ODbL-1.0"})
    errs = _errors(qc.check_licence_gate(cat, facts, REGISTRY))
    assert any(e.startswith("source testosm: ODbL licence") for e in errs)


def test_fact_with_unconfirmed_licence_fails(cat, facts) -> None:
    facts[0]["source"]["licence"] = "CC0-1.0 (to confirm)"
    c = qc.check_licence_gate(cat, facts, REGISTRY)
    assert c.status == "fail"
    assert any("licence not confirmed" in e for e in _errors(c))


def test_fact_id_from_blocked_source_fails(cat, facts) -> None:
    _row(cat)["provenance"]["battery_kwh_net"]["fact_ids"].append("testpending:x:battery")
    errs = _errors(qc.check_licence_gate(cat, facts, REGISTRY))
    assert any("fact testpending:x:battery: status waiting_permission" in e for e in errs)


def test_values_per_source_counts_usage(cat, facts) -> None:
    c = qc.check_licence_gate(cat, facts, REGISTRY)
    assert c.status == "pass"
    assert c.details["values_per_source"]["testsrc"] > 0


# --- diff --------------------------------------------------------------------------------


def test_diff_against_empty_previous_release(cat) -> None:
    c = qc.check_diff({"release": 0, "rows": []}, cat, POLICIES)
    assert c.details["lost_share"] == 0.0 and c.details["lost"] == []
    assert c.details["coverage"]["battery_kwh_net"]["filled_pct_previous"] == 0.0
    assert c.details["coverage"]["battery_kwh_net"]["two_plus_pct_previous"] == 0.0
    assert c.status == "pass"


def test_diff_to_empty_current_release_flags_everything_lost(cat) -> None:
    c = qc.check_diff(cat, {"release": 2, "rows": []}, POLICIES)
    assert c.status == "flag"
    assert len(c.details["lost"]) == len(cat["rows"]) and c.details["lost_share"] == 1.0


def test_diff_skips_non_numeric_values(cat) -> None:
    import copy

    cur = copy.deepcopy(cat)
    _row(cur)["battery_kwh_net"] = "n/a"
    _row(cur)["wltp_range_km"] = float("nan")
    c = qc.check_diff(cat, cur, POLICIES)
    assert "battery_kwh_net" not in c.details["beyond_tolerance_counts"]
    assert "wltp_range_km" not in c.details["beyond_tolerance_counts"]


def test_two_plus_share_ignores_estimates() -> None:
    rows = [
        {"x": 1, "provenance": {"x": {"agreeing_sources": 2}}},
        {"x": 1, "provenance": {"x": {"agreeing_sources": 3, "estimate": True}}},
        {"x": None, "provenance": {"x": {"agreeing_sources": 2}}},
        {"x": 1},
    ]
    assert qc._two_plus_share(rows, "x") == 0.25
    assert qc._two_plus_share([], "x") == 0.0
    assert qc._filled_share([], "x") == 0.0


# --- outliers ----------------------------------------------------------------------------


def test_percentile_edges() -> None:
    with pytest.raises(ValueError, match="no values"):
        qc.percentile([], 50)
    assert qc.percentile([7.0], 1) == 7.0
    assert qc.percentile([3.0, 1.0, 2.0], 0) == 1.0
    assert qc.percentile([3.0, 1.0, 2.0], 100) == 3.0
    assert qc.percentile([0.0, 10.0], 25) == 2.5


# --- top models --------------------------------------------------------------------------


def _r(model: str, gen: str, regs: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    return {
        "variant_id": f"{gen}-v",
        "model_id": model,
        "generation_id": gen,
        "make_name": "Testcar",
        "model_name": model,
        "registrations": regs,
    }


def _e(count: int, source: str, kind: str = "fleet") -> dict[str, Any]:
    return {"count": count, "kind": kind, "source_id": source}


def test_top_models_fall_back_to_uk_fleet_and_ignore_non_rdw_nl() -> None:
    rows = [
        _r("a", "a1", {"UK": [_e(900, "dft")]}),
        _r("a", "a1", {"UK": [_e(1200, "dft")]}),  # max over variants, not a sum
        _r("b", "b1", {"UK": [_e(1000, "dft")], "NL": [_e(99999, "eea")]}),  # not RDW
        _r("c", "c1", {"NL": [_e(10, "rdw")]}),  # any RDW fleet ranks first
        _r("d", "d1", {"UK": [_e(5000, "dft", kind="new_registrations")]}),  # not fleet
    ]
    assert [m["model_id"] for m in qc.top_models(rows)] == ["c", "a", "b", "d"]


def test_top_models_sum_rdw_per_generation_once() -> None:
    rows = [
        _r("a", "a1", {"NL": [_e(100, "rdw")]}),
        _r("a", "a1", {"NL": [_e(100, "rdw")]}),  # same generation: counted once
        _r("a", "a2", {"NL": [_e(50, "rdw")]}),
        _r("b", "b1", {"NL": [_e(200, "rdw")]}),
    ]
    assert [m["model_id"] for m in qc.top_models(rows)] == ["b", "a"]  # 200 > 150
    assert len(qc.top_models(rows, n=1)) == 1


def test_top40_coverage_on_empty_release() -> None:
    c = qc.check_top40_coverage({"rows": []})
    assert c.status == "info" and c.details["models"] == []
    assert c.details["models_all_fields_two_plus"] == 0


# --- report and release step -------------------------------------------------------------


def test_qa_document_carries_open_data_only_when_given(cat, facts) -> None:
    checks = run_qa(cat, facts, REGISTRY, POLICIES)
    assert "open_data" not in qa_document(cat, checks, {"status": "skipped"})
    doc = qa_document(cat, checks, {"status": "skipped"}, {"files": ["x"]})
    assert doc["open_data"] == {"files": ["x"]}


def test_registration_order(tmp_path: Path) -> None:
    assert registration_order(tmp_path) == ()
    (tmp_path / "field_sources.yaml").write_text(
        "fields:\n  registered_count:\n    primary: [rdw]\n    fallbacks: [dft, kba]\n",
        encoding="utf-8",
    )
    assert registration_order(tmp_path) == ("rdw", "dft", "kba")
    (tmp_path / "field_sources.yaml").write_text("", encoding="utf-8")
    assert registration_order(tmp_path) == ()


def test_previous_release_lookup(tmp_path: Path) -> None:
    rel = tmp_path / "releases"
    assert _previous(tmp_path, 3) == (None, None)
    for n in ("1", "2", "5"):
        (rel / n).mkdir(parents=True)
        (rel / n / "catalogue.json").write_text(json.dumps({"release": int(n)}))
    (rel / ".tmp-3").mkdir()
    (rel / "latest").write_text("2\n")
    (rel / "2" / "qa.json").write_text(json.dumps({"backtest": {"status": "ok"}}))
    cat, bt = _previous(tmp_path, 3)
    assert cat == {"release": 2} and bt == {"status": "ok"}
    cat1, bt1 = _previous(tmp_path, 2)
    assert cat1 == {"release": 1} and bt1 is None  # no qa.json in release 1


def _qa_data_dir(tmp_path: Path) -> Path:
    d = tmp_path / "data"
    d.mkdir()
    shutil.copy(QA / "sources.yaml", d / "sources.yaml")
    shutil.copy(QA / "field_sources.yaml", d / "field_sources.yaml")
    return d


def test_finish_release_passes_and_writes_bundle(cat, facts, tmp_path: Path) -> None:
    d = _qa_data_dir(tmp_path)
    out = d / "releases" / ".tmp-1"
    out.mkdir(parents=True)
    doc = finish_release(cat, facts, out, d)
    assert doc["status"] in {"pass", "review"}
    assert (out / "qa.json").exists() and (out / "open" / "variants.csv").exists()
    assert not (d / "review").exists()


def test_finish_release_blocks_on_real_licence_failure(cat, facts, tmp_path: Path) -> None:
    d = _qa_data_dir(tmp_path)
    out = d / "releases" / ".tmp-1"
    out.mkdir(parents=True)
    _row(cat)["provenance"]["wltp_range_km"]["source_ids"].append("testosm")
    cat["sources"].append({"id": "testosm", "name": "ODbL", "licence": "ODbL-1.0"})
    with pytest.raises(ReleaseError, match="licence_gate"):
        finish_release(cat, facts, out, d)
    assert not out.exists()  # temporary release folder removed
    review = json.loads((d / "review" / "qa.json").read_text())
    assert review["status"] == "fail" and review["blocking_failures"] == ["licence_gate"]
    assert "ODbL" in (d / "review" / "qa.md").read_text()


def test_overall_status_pass_when_nothing_flags() -> None:
    assert (
        overall_status(
            [qc.Check("a", "A", True, "pass", ""), qc.Check("b", "B", False, "info", "")]
        )
        == "pass"
    )
    assert overall_status([]) == "pass"
