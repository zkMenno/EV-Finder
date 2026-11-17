"""Release QA (R-05 §1): one test per rule, on the synthetic fixture in fixtures/qa/."""

from __future__ import annotations

import copy
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from ev_pipeline.merge.policy import load_policies
from ev_pipeline.qa import checks as qc
from ev_pipeline.qa import report
from ev_pipeline.qa.checks import Check
from ev_pipeline.qa.report import overall_status, qa_document, qa_md, run_qa
from ev_pipeline.release.build import release_cmd
from ev_pipeline.release.gate import load_registry

QA = Path(__file__).parent / "fixtures" / "qa"
REL = Path(__file__).parent / "fixtures" / "release"
NOW = datetime(2026, 11, 15, 1, 0, tzinfo=UTC)
REGISTRY = load_registry(QA / "sources.yaml")
POLICIES = load_policies(QA / "field_sources.yaml")


@pytest.fixture
def cat() -> dict[str, Any]:
    return json.loads((QA / "catalogue.json").read_text())


@pytest.fixture
def facts() -> list[dict[str, Any]]:
    return json.loads((QA / "facts.json").read_text())


def _row(cat: dict[str, Any], vid: str) -> dict[str, Any]:
    return next(r for r in cat["rows"] if r["variant_id"] == vid)


A50, A60, B40 = "testcar-alpha-gen1-50", "testcar-alpha-gen1-60", "testcar-beta-gen1-40"


def test_fixture_is_labelled_synthetic(cat) -> None:
    assert "SYNTHETIC" in cat["_fixture"]
    assert {r["make_id"] for r in cat["rows"]} == {"testcar"}


def test_clean_fixture_passes_blocking_checks(cat, facts) -> None:
    checks = run_qa(cat, facts, REGISTRY, POLICIES)
    by = {c.id: c for c in checks}
    assert by["provenance"].status == "pass", by["provenance"].details["errors"]
    assert by["licence_gate"].status == "pass", by["licence_gate"].details["errors"]
    assert by["diff"].status == "skipped"
    assert overall_status(checks) in {"pass", "review"}


# --- provenance (blocking) ---------------------------------------------------------------


def test_provenance_missing_entry_fails(cat, facts) -> None:
    del _row(cat, A50)["provenance"]["wltp_range_km"]
    c = qc.check_provenance(cat, facts)
    assert c.status == "fail" and c.blocking
    assert any("wltp_range_km has no provenance" in e for e in c.details["errors"])


def test_provenance_missing_confidence_fails(cat, facts) -> None:
    del _row(cat, A50)["provenance"]["ac_kw"]["confidence"]
    assert qc.check_provenance(cat, facts).status == "fail"


def test_provenance_unknown_fact_id_fails(cat, facts) -> None:
    _row(cat, A50)["provenance"]["ac_kw"]["fact_ids"] = ["testsrc:nope:ac_kw"]
    c = qc.check_provenance(cat, facts)
    assert any("unknown fact" in e for e in c.details["errors"])


def test_provenance_source_without_licence_fails(cat, facts) -> None:
    cat["sources"] = [s for s in cat["sources"] if s["id"] != "testreg"]
    c = qc.check_provenance(cat, facts)
    assert any("testreg has no licence" in e for e in c.details["errors"])


def test_provenance_fact_without_date_fails(cat, facts) -> None:
    del facts[0]["retrieved_at"]
    assert qc.check_provenance(cat, facts).status == "fail"


def test_provenance_value_without_facts_is_dated_by_source(cat, facts) -> None:
    c = qc.check_provenance(cat, facts)
    assert c.details["dated_by_source"] == 3  # price_new.NL on each row (no fact ids)
    # A source with no dated fact anywhere cannot date a value: blocking.
    cat["sources"].append({"id": "undated", "name": "x", "licence": "CC0-1.0"})
    _row(cat, A50)["provenance"]["price_new.NL"]["source_ids"] = ["undated"]
    c = qc.check_provenance(cat, facts)
    assert any("price_new.NL has no date" in e for e in c.details["errors"])


def test_provenance_registrations_need_provenance(cat, facts) -> None:
    del _row(cat, B40)["provenance"]["registrations.NL"]
    c = qc.check_provenance(cat, facts)
    assert any("registrations.NL has no provenance" in e for e in c.details["errors"])


# --- licence gate (blocking) -------------------------------------------------------------


def test_licence_gate_blocks_pending_source_in_provenance(cat, facts) -> None:
    _row(cat, A50)["provenance"]["boot_l"]["source_ids"] = ["testpending"]
    c = qc.check_licence_gate(cat, facts, REGISTRY)
    assert c.status == "fail" and c.blocking
    assert any("testpending" in e for e in c.details["errors"])


def test_licence_gate_blocks_odbl_source(cat, facts) -> None:
    cat["sources"].append({"id": "testosm", "name": "map", "licence": "ODbL-1.0"})
    c = qc.check_licence_gate(cat, facts, REGISTRY)
    assert any("ODbL" in e for e in c.details["errors"])


def _with_cited_facts_source(use: str, decision: str) -> Any:
    from ev_pipeline.release.gate import parse_registry

    doc = {
        "sources": [
            *[
                {"id": e.id, "name": e.name, "licence": e.licence, "status": e.status}
                for e in REGISTRY.sources.values()
            ],
            {
                "id": "testcited",
                "name": "Cited maker facts (fixture)",
                "licence": "facts cited, no licence (Decision 068)",
                "access": "manual",
                "status": "active",
                "use": use,
                "decision": decision,
            },
        ]
    }
    return parse_registry(doc)


def test_licence_gate_recheck_admits_cited_facts_source(cat, facts) -> None:
    """Regression (T-116): the release gate admits a `use: cited-facts` source (Decision 068),
    but the QA re-check re-read its licence text and blocked the whole release."""
    reg = _with_cited_facts_source("cited-facts", "068")
    assert reg.releasable("testcited")
    cat["sources"].append(
        {"id": "testcited", "name": "cited", "licence": "facts cited, no licence (Decision 068)"}
    )
    facts[0]["source"] = {
        "id": "testcited",
        "name": "cited",
        "licence": "facts cited, no licence (Decision 068)",
    }
    c = qc.check_licence_gate(cat, facts, reg)
    assert c.status == "pass", c.details["errors"]


def test_licence_gate_recheck_still_blocks_unlicensed_source_without_decision(cat, facts) -> None:
    reg = _with_cited_facts_source("cited-facts", "")
    facts[0]["source"] = {"id": "testcited", "name": "cited", "licence": "facts cited, no licence"}
    c = qc.check_licence_gate(cat, facts, reg)
    assert c.status == "fail"
    fid = str(facts[0]["id"])
    assert any(fid in e and "no named licence" in e for e in c.details["errors"])


def test_licence_gate_recheck_blocks_odbl_even_for_cited_facts(cat, facts) -> None:
    reg = _with_cited_facts_source("cited-facts", "068")
    facts[0]["source"] = {"id": "testcited", "name": "cited", "licence": "ODbL-1.0"}
    c = qc.check_licence_gate(cat, facts, reg)
    assert any("ODbL" in e for e in c.details["errors"])


def test_licence_gate_blocks_odbl_fact(cat, facts) -> None:
    facts[0]["source"] = {"id": "testosm", "name": "map", "licence": "ODbL-1.0"}
    assert qc.check_licence_gate(cat, facts, REGISTRY).status == "fail"


def test_licence_gate_blocks_unregistered_registration_source(cat, facts) -> None:
    _row(cat, A50)["registrations"]["NL"][0]["source_id"] = "nowhere"
    c = qc.check_licence_gate(cat, facts, REGISTRY)
    assert any("registrations.NL" in e for e in c.details["errors"])


def test_licence_gate_blocks_nyland_whatever_the_registry(cat, facts) -> None:
    _row(cat, A50)["provenance"]["ac_kw"]["fact_ids"].append("nyland:x:ac_kw")
    assert qc.check_licence_gate(cat, facts, REGISTRY).status == "fail"


# --- diff vs previous release ------------------------------------------------------------


def test_diff_flags_lost_variants(cat) -> None:
    cur = copy.deepcopy(cat)
    cur["rows"] = [r for r in cur["rows"] if r["variant_id"] != B40]
    c = qc.check_diff(cat, cur, POLICIES)
    assert c.status == "flag" and not c.blocking
    assert c.details["lost"] == [B40]
    assert any("variants lost" in f for f in c.details["flags"])


def _many(cat: dict[str, Any], n: int) -> dict[str, Any]:
    out = copy.deepcopy(cat)
    base = out["rows"][0]
    out["rows"] = []
    for i in range(n):
        r = copy.deepcopy(base)
        r["variant_id"] = f"testcar-many-{i:02d}"
        out["rows"].append(r)
    return out


def test_diff_flags_headline_changes_beyond_tolerance_on_more_than_20(cat) -> None:
    prev = _many(cat, 25)
    cur = copy.deepcopy(prev)
    for r in cur["rows"][:21]:
        r["wltp_range_km"] = r["wltp_range_km"] * 1.05  # tolerance 2 %
    c = qc.check_diff(prev, cur, POLICIES)
    assert c.details["beyond_tolerance_counts"]["wltp_range_km"] == 21
    assert any("wltp_range_km: 21 variants" in f for f in c.details["flags"])
    # 20 changed variants is still fine; changes inside tolerance never count.
    cur2 = copy.deepcopy(prev)
    for r in cur2["rows"][:20]:
        r["wltp_range_km"] *= 1.05
    for r in cur2["rows"][20:]:
        r["wltp_range_km"] *= 1.01
    c2 = qc.check_diff(prev, cur2, POLICIES)
    assert c2.details["beyond_tolerance_counts"]["wltp_range_km"] == 20
    assert c2.status == "pass"


def test_diff_abs_tolerance_and_coverage_drop(cat) -> None:
    cur = copy.deepcopy(cat)
    _row(cur, A50)["boot_l"] = 354  # abs tolerance 5 l: agrees
    _row(cur, A60)["boot_l"] = 380  # beyond
    _row(cur, B40)["ac_kw"] = None  # 100 % -> 67 % filled
    c = qc.check_diff(cat, cur, POLICIES)
    assert c.details["beyond_tolerance_counts"]["boot_l"] == 1
    assert c.details["coverage"]["ac_kw"]["filled_pct"] == pytest.approx(66.7)
    assert any("ac_kw: filled share fell" in f for f in c.details["flags"])


# --- outliers ----------------------------------------------------------------------------


def _rules(cat, facts) -> set[tuple[str, str]]:
    return {(i["variant_id"], i["rule"]) for i in qc.impossible_values(cat, facts)}


def test_clean_fixture_has_no_impossible_values(cat, facts) -> None:
    assert _rules(cat, facts) == set()


def test_usable_above_gross_is_flagged(cat, facts) -> None:
    _row(cat, A50)["battery_kwh_net"] = 56.0  # pack gross 55
    assert (A50, "usable_gt_gross") in _rules(cat, facts)


def test_usable_vs_gross_allows_rounding(cat, facts) -> None:
    cat["battery_packs"][0]["gross_kwh"] = 49.98  # row rounds to 1 decimal: 50.0
    assert (A50, "usable_gt_gross") not in _rules(cat, facts)


def test_usable_above_gross_fact_without_pack(cat, facts) -> None:
    facts.append(
        {**facts[0], "id": "g", "subject_id": B40, "field": "battery_kwh_gross", "value": 38}
    )
    assert (B40, "usable_gt_gross") in _rules(cat, facts)


def test_wltp_efficiency_above_10_km_per_kwh(cat, facts) -> None:
    _row(cat, B40)["wltp_range_km"] = 401.0  # 40 kWh -> 10.03 km/kWh
    assert (B40, "wltp_efficiency") in _rules(cat, facts)
    _row(cat, B40)["wltp_range_km"] = 400.0  # exactly 10: allowed
    assert (B40, "wltp_efficiency") not in _rules(cat, facts)


def test_dc_average_above_peak(cat, facts) -> None:
    _row(cat, B40)["dc_avg_10_80_kw"] = 51.0
    assert (B40, "dc_avg_gt_peak") in _rules(cat, facts)


def test_ac_above_43_kw(cat, facts) -> None:
    _row(cat, B40)["ac_kw"] = 43.0
    assert (B40, "ac_gt_43") not in _rules(cat, facts)
    _row(cat, B40)["ac_kw"] = 44.0
    assert (B40, "ac_gt_43") in _rules(cat, facts)


def test_negative_values(cat, facts) -> None:
    _row(cat, B40)["boot_l"] = -1
    _row(cat, A50)["price_new"]["NL"]["amount"] = -5
    _row(cat, A60)["registrations"]["NL"][0]["count"] = -3
    got = [
        (i["variant_id"], i["field"])
        for i in qc.impossible_values(cat, facts)
        if i["rule"] == "negative"
    ]
    assert sorted(got) == [(A50, "price_new.NL"), (A60, "registrations.NL"), (B40, "boot_l")]


def test_percentile_outliers_per_segment(cat) -> None:
    big = _many(cat, 40)  # all segment C
    for i, r in enumerate(big["rows"]):
        r["wltp_range_km"] = 400.0 + i
    big["rows"][-1]["wltp_range_km"] = 900.0
    out, meta = qc.percentile_outliers(big, None)
    flagged = {(o["variant_id"], o["field"]) for o in out}
    assert ("testcar-many-39", "wltp_range_km") in flagged
    assert meta["reference"] == "this release"
    # Against a previous release: a value inside its P1-P99 is not flagged.
    cur = copy.deepcopy(big)
    cur["rows"] = [cur["rows"][5]]
    out2, meta2 = qc.percentile_outliers(cur, big)
    assert out2 == [] and meta2["reference"] == "release 1"


def test_percentile_skips_small_segments(cat) -> None:
    out, meta = qc.percentile_outliers(cat, None)
    assert out == [] and meta["segment_fields_checked"] == 0
    assert meta["segment_fields_skipped_small"] > 0


def test_outlier_check_flags_but_does_not_block(cat, facts) -> None:
    _row(cat, B40)["dc_avg_10_80_kw"] = 60.0
    c = qc.check_outliers(cat, None, facts)
    assert c.status == "flag" and not c.blocking
    assert c.details["impossible_by_rule"] == {"dc_avg_gt_peak": 1}


# --- top-40 coverage ---------------------------------------------------------------------


def test_top_models_ranked_by_nl_fleet_once_per_generation(cat) -> None:
    top = qc.top_models(cat["rows"])
    # alpha has two variants of one generation (5000 each): counted once, still first.
    assert [m["model_id"] for m in top] == ["testcar-alpha", "testcar-beta"]


def test_top40_coverage_counts_majority_two_plus_never_estimates(cat) -> None:
    for vid in (A50, A60):
        _row(cat, vid)["provenance"]["battery_kwh_net"]["agreeing_sources"] = 2
        p = _row(cat, vid)["provenance"]["real_range_km"]
        p["agreeing_sources"] = 2  # still an estimate: never counts
    c = qc.check_top40_coverage(cat)
    assert c.status == "info"
    alpha = next(m for m in c.details["models"] if m["model_id"] == "testcar-alpha")
    assert alpha["fields"]["battery_kwh_net"]["covered"] is True
    assert alpha["fields"]["real_range_km"]["covered"] is False
    assert c.details["share_two_plus_by_field"]["battery_kwh_net"] == 0.5


# --- report + release hook ---------------------------------------------------------------


def test_qa_document_and_markdown(cat, facts) -> None:
    checks = run_qa(cat, facts, REGISTRY, POLICIES)
    doc = qa_document(cat, checks, {"status": "skipped", "note": "none"})
    assert set(doc["checks"]) == {
        "provenance",
        "licence_gate",
        "diff",
        "outliers",
        "top40_coverage",
        "sections",
        "plausibility",  # T-111
    }
    md = qa_md(doc)
    assert "Release QA, release 1" in md and "Back-test" in md


def test_blocking_status_wins(cat) -> None:
    ok = Check("a", "A", False, "flag", "")
    bad = Check("b", "B", True, "fail", "")
    assert overall_status([ok]) == "review"
    assert overall_status([ok, bad]) == "fail"


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    d = tmp_path / "data"
    (d / "seed").mkdir(parents=True)
    shutil.copytree(REL / "staging", d / "staging")
    shutil.copytree(REL / "taxonomy", d / "taxonomy")
    for n in ("models", "variants", "platforms", "battery_packs", "variant_links"):
        shutil.copy(REL / f"{n}.yaml", d / "seed" / f"{n}.yaml")
    for n in ("sources", "field_sources"):
        shutil.copy(REL / f"{n}.yaml", d / f"{n}.yaml")
    return d


def test_release_writes_qa_and_open_bundle(data_dir: Path) -> None:
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 0
    out = data_dir / "releases" / "1"
    doc = json.loads((out / "qa.json").read_text())
    assert doc["release"] == 1 and doc["status"] in {"pass", "review"}
    assert doc["checks"]["provenance"]["status"] == "pass"
    assert doc["checks"]["licence_gate"]["status"] == "pass"
    assert doc["backtest"]["status"] == "skipped"
    assert set(doc["open_data"]["files"]) == {
        "ATTRIBUTION.md",
        "LICENSE",
        "README.md",
        "variants.csv",
        "variants.json",
    }
    assert (out / "qa.md").read_text().startswith("# Release QA, release 1")
    # Second release: the diff check now compares with release 1.
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 0
    doc2 = json.loads((data_dir / "releases" / "2" / "qa.json").read_text())
    assert doc2["checks"]["diff"]["details"]["previous_release"] == 1
    assert doc2["checks"]["diff"]["status"] == "pass"


def test_blocking_qa_failure_fails_the_release(data_dir: Path, monkeypatch) -> None:
    def failing(*a: Any, **kw: Any) -> Check:
        return Check(
            "provenance", "Provenance completeness", True, "fail", "x", {"errors": ["boom"]}
        )

    monkeypatch.setattr(report, "check_provenance", failing)
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 1
    releases = data_dir / "releases"
    assert not (releases / "1").exists()
    assert not (releases / "latest").exists()
    assert [p.name for p in releases.iterdir()] == []  # tmp folder removed
    assert "boom" in (data_dir / "review" / "qa.md").read_text()


def test_non_blocking_flags_do_not_fail_the_release(data_dir: Path, monkeypatch) -> None:
    def flagged(*a: Any, **kw: Any) -> Check:
        return Check("outliers", "Outliers", False, "flag", "x", {"impossible": []})

    monkeypatch.setattr(report, "check_outliers", flagged)
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 0
    doc = json.loads((data_dir / "releases" / "1" / "qa.json").read_text())
    assert doc["status"] == "review"
