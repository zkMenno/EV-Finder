"""T-063 (Decision 034): `ac_kw` is the standard on-board charger, `ac_kw_optional` the bigger
option. A source's single max-AC figure moves to `ac_kw_optional` only when a citation says so.

Cases from A-06: Peugeot e-2008 54 kWh (Stellantis 04-05-2023: 7.4 kW standard, 11 kW
optional; OpenEV and KilowattApp both give 11), Megane EV40 (7.4 / 22).
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path

from ev_pipeline.match.matcher import MatchedFact, priority_of
from ev_pipeline.match.seed import CANONICAL_UNITS
from ev_pipeline.merge.ac_route import ROUTE_NOTE, route_optional_ac
from ev_pipeline.merge.merge import merge_variant_facts
from ev_pipeline.merge.policy import load_policies
from ev_pipeline.opendata.bundle import VALUE_FIELDS
from ev_pipeline.qa.checks import impossible_values
from ev_pipeline.qa.value_guard import run_guards
from ev_pipeline.release.validate import RANGES, ROW_NUMBER_FIELDS
from ev_pipeline.schema_models import Fact, FactField

REPO = Path(__file__).resolve().parents[2]
POLICIES = load_policies(REPO / "data" / "field_sources.yaml")
AC = POLICIES.for_field("ac_kw")
VID = "peugeot-e-2008-p24-54kwh"
LIC = {"openev": "CDLA-Permissive-2.0", "kilowatt-openev": "MIT", "maker-docs": "none"}
STELLANTIS = "https://www.media.stellantis.com/em-en/peugeot/press/e-2008-2023"
_n = [0]


def _mf(source: str, fname: str, value: float, *, cited: bool = False) -> MatchedFact:
    _n[0] += 1
    record = f"{VID}#cited:{fname}" if cited else f"{source}-rec-{_n[0]}"
    src = {"id": source, "name": source, "licence": LIC[source]}
    if cited:
        src["url"] = STELLANTIS
    fact = Fact(
        id=f"{source}:{record}:{fname}:{_n[0]}",
        subject_type="variant",
        subject_id=VID,
        field=fname,
        value=value,
        unit="kW",
        source=src,
        source_record=record,
        retrieved_at=date(2026, 11, 15),
        confidence="medium",
    )
    return MatchedFact(fact, source, priority_of(source), 2023)


def _fields(facts: list[MatchedFact]) -> list[tuple[str, str, float]]:
    return sorted((mf.source_id, mf.fact.field.value, mf.fact.value) for mf in facts)


def _e2008() -> tuple[dict[str, list[MatchedFact]], dict[str, list[MatchedFact]]]:
    shipping = [_mf("openev", "ac_kw", 11), _mf("kilowatt-openev", "ac_kw", 11)]
    evidence = [  # maker-docs is blocked (Q-008): evidence only
        _mf("maker-docs", "ac_kw", 7.4, cited=True),
        _mf("maker-docs", "ac_kw_optional", 11, cited=True),
    ]
    return {VID: shipping}, {VID: evidence}


def test_source_figure_that_a_citation_calls_optional_moves_to_the_optional_field() -> None:
    by_variant, evidence = _e2008()
    out, routed, problems = route_optional_ac(by_variant, evidence, AC)
    assert _fields(out[VID]) == [
        ("kilowatt-openev", "ac_kw_optional", 11),
        ("openev", "ac_kw_optional", 11),
    ]
    assert not problems
    assert {(r.source_id, r.value, r.cited_optional, r.cited_standard) for r in routed} == {
        ("openev", 11.0, 11.0, 7.4),
        ("kilowatt-openev", 11.0, 11.0, 7.4),
    }
    assert all(ROUTE_NOTE in (mf.note or "") for mf in out[VID])
    # Source, licence, record and date stay with the fact: only its field changes.
    assert {mf.fact.source.id.root for mf in out[VID]} == {"openev", "kilowatt-openev"}


def test_routing_never_mutates_the_input_facts() -> None:
    by_variant, evidence = _e2008()
    route_optional_ac(by_variant, evidence, AC)
    assert {mf.fact.field for mf in by_variant[VID]} == {FactField.ac_kw}


def test_without_a_citation_for_the_option_nothing_moves() -> None:
    """Decision 034: no citation, no guess. The merged ac_kw stays what the sources say."""
    by_variant = {VID: [_mf("openev", "ac_kw", 11)]}
    evidence = {VID: [_mf("maker-docs", "ac_kw", 7.4, cited=True)]}
    out, routed, problems = route_optional_ac(by_variant, evidence, AC)
    assert _fields(out[VID]) == [("openev", "ac_kw", 11)]
    assert routed == [] and problems == []


def test_a_source_figure_equal_to_the_cited_standard_stays_standard() -> None:
    by_variant = {VID: [_mf("openev", "ac_kw", 7.4), _mf("kilowatt-openev", "ac_kw", 11)]}
    _, evidence = _e2008()
    out, routed, _ = route_optional_ac(by_variant, evidence, AC)
    assert _fields(out[VID]) == [
        ("kilowatt-openev", "ac_kw_optional", 11),
        ("openev", "ac_kw", 7.4),
    ]
    assert len(routed) == 1


def test_a_figure_matching_neither_citation_stays_for_the_guards() -> None:
    """Megane EV40 cited 7.4 / 22; a source 11 is neither: it stays on ac_kw, where
    guard_contradicted handles it as before."""
    by_variant = {VID: [_mf("openev", "ac_kw", 11)]}
    evidence = {
        VID: [
            _mf("maker-docs", "ac_kw", 7.4, cited=True),
            _mf("maker-docs", "ac_kw_optional", 22, cited=True),
        ]
    }
    out, routed, _ = route_optional_ac(by_variant, evidence, AC)
    assert _fields(out[VID]) == [("openev", "ac_kw", 11)]
    assert routed == []


def test_cited_optional_not_above_cited_standard_is_a_problem_and_moves_nothing() -> None:
    by_variant = {VID: [_mf("openev", "ac_kw", 11)]}
    evidence = {
        VID: [
            _mf("maker-docs", "ac_kw", 11, cited=True),
            _mf("maker-docs", "ac_kw_optional", 11, cited=True),
        ]
    }
    out, routed, problems = route_optional_ac(by_variant, evidence, AC)
    assert _fields(out[VID]) == [("openev", "ac_kw", 11)]
    assert routed == []
    assert [p.variant_id for p in problems] == [VID]


def test_a_citation_is_never_routed_itself() -> None:
    cite = _mf("maker-docs", "ac_kw", 11, cited=True)  # shipping citation (Q-008 answered)
    by_variant = {VID: [cite]}
    evidence = {VID: [_mf("maker-docs", "ac_kw_optional", 11, cited=True)]}
    out, _, problems = route_optional_ac(by_variant, evidence, AC)
    # 11 cited as both is caught as a problem; the citation keeps its field either way.
    assert problems and _fields(out[VID]) == [("maker-docs", "ac_kw", 11)]


def test_after_routing_the_merge_publishes_the_option_and_withholds_nothing_extra() -> None:
    """e-2008: ac_kw_optional 11 (OpenEV + KilowattApp) ships; ac_kw has no releasable
    value left (7.4 waits for Q-008), so it is empty rather than wrong."""
    by_variant, evidence = _e2008()
    routed, _, _ = route_optional_ac(by_variant, evidence, AC)
    merged = {VID: merge_variant_facts(routed[VID], POLICIES)}
    run_guards(merged, routed, POLICIES, evidence)
    assert merged[VID]["ac_kw_optional"].value == 11
    assert merged[VID]["ac_kw_optional"].winner.source_id == "openev"
    assert "ac_kw" not in merged[VID]


def test_the_field_is_wired_everywhere_it_must_be() -> None:
    schema = json.loads((REPO / "packages/schema/schemas/ev.schema.json").read_text())
    assert "ac_kw_optional" in schema["$defs"]["FactField"]["enum"]
    assert CANONICAL_UNITS["ac_kw_optional"] == "kW"
    assert RANGES["ac_kw_optional"] == RANGES["ac_kw"]
    assert "ac_kw_optional" in ROW_NUMBER_FIELDS
    assert "ac_kw_optional" in [f for f, _, _ in VALUE_FIELDS]
    pol = POLICIES.for_field("ac_kw_optional")
    assert pol.order[:2] == ("openev", "kilowatt-openev") and pol.tol_pct == 2


def test_qa_flags_an_optional_charger_not_above_the_standard_one() -> None:
    row = {"variant_id": VID, "generation_id": "g", "ac_kw": 11, "ac_kw_optional": 7.4}
    found = impossible_values({"rows": [row]}, [])
    assert [(f["rule"], f["field"]) for f in found] == [("ac_optional_not_above", "ac_kw_optional")]
    row["ac_kw_optional"] = 50
    assert {f["rule"] for f in impossible_values({"rows": [row]}, [])} == {"ac_gt_43"}


def test_a_manual_citation_can_name_the_optional_charger(tmp_path: Path) -> None:
    """data/manual is where WS3 enters the citations that drive the routing."""
    import yaml

    from ev_pipeline.manual.facts import parse_manual_file

    fact = {
        "variant_id": VID,
        "field": "ac_kw_optional",
        "value": 11,
        "unit": "kW",
        "source_url": STELLANTIS,
        "retrieved": "2026-11-15",
        "locator": "Technical data, charging",
        "entered_by": "test",
        "confidence": "medium",
    }
    p = tmp_path / "t.yaml"
    p.write_text(yaml.safe_dump({"schema": "manual-facts/v1", "facts": [fact]}))
    facts, issues, _ = parse_manual_file(p, "data/manual/specs/t.yaml", "specs", date(2026, 11, 17))
    assert issues == []
    assert facts[0].fact.field == FactField.ac_kw_optional and facts[0].fact.unit == "kW"


def test_release_build_routes_with_a_blocked_manual_citation(tmp_path: Path) -> None:
    """End to end on the release fixtures: OpenEV gives the Model 3 LR 11 kW AC. A blocked
    manual citation says 11 is the option and 7.4 the standard (made-up figures for the
    fixture car). The row ships ac_kw_optional 11 led by OpenEV, no ac_kw, no manual fact,
    and the run log lists the move."""
    import shutil

    import yaml
    from test_manual import BLOCKED, RELEASE_FIX, _set_manual_registry

    from ev_pipeline.release.build import build_release

    d = tmp_path / "data"
    (d / "seed").mkdir(parents=True)
    shutil.copytree(RELEASE_FIX / "staging", d / "staging")
    shutil.copytree(RELEASE_FIX / "taxonomy", d / "taxonomy")
    for n in ("models", "variants", "platforms", "battery_packs", "variant_links"):
        shutil.copy(RELEASE_FIX / f"{n}.yaml", d / "seed" / f"{n}.yaml")
    for n in ("sources", "field_sources"):
        shutil.copy(RELEASE_FIX / f"{n}.yaml", d / f"{n}.yaml")
    _set_manual_registry(d, BLOCKED)
    vid = "tesla-model-3-gen1-lr"
    base = {
        "variant_id": vid,
        "unit": "kW",
        "source_url": "https://example.org/fixture/charging.pdf",
        "retrieved": "2026-11-01",
        "locator": "p. 1",
        "entered_by": "test",
        "confidence": "medium",
    }
    facts = [
        {**base, "field": "ac_kw", "value": 7.4},
        {**base, "field": "ac_kw_optional", "value": 11},
    ]
    (d / "manual" / "specs").mkdir(parents=True)
    (d / "manual" / "specs" / "t063.yaml").write_text(
        yaml.safe_dump({"schema": "manual-facts/v1", "facts": facts})
    )
    res = build_release(d, now=datetime(2026, 11, 17, 1, 0, tzinfo=UTC))
    row = next(r for r in res.catalogue["rows"] if r["variant_id"] == vid)
    assert row["ac_kw_optional"] == 11
    # The uncited seed spec (also 11) means the option too: it moves and agrees.
    assert row["provenance"]["ac_kw_optional"]["source_ids"][0] == "openev"
    assert "manual" not in row["provenance"]["ac_kw_optional"]["source_ids"]
    assert row.get("ac_kw") is None
    assert not any(f["source"]["id"] == "manual" for f in res.facts)
    routed = res.sections["ac_kw_optional"]["routed"]
    assert {(r["variant_id"], r["source_id"], r["value"]) for r in routed} >= {
        (vid, "openev", 11.0)
    }
    assert {r["variant_id"] for r in routed} == {vid}
    # Other Model 3 rows have no citation: their ac_kw is untouched.
    others = [r for r in res.catalogue["rows"] if r["variant_id"] != vid and r.get("ac_kw")]
    assert others and all(r.get("ac_kw_optional") is None for r in others)
