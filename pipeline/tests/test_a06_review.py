"""A-06 review (audits/A-06-merge-rules-review.md): confirmed bugs in how the Decision 025-030
rules interact. Each test states the intended behaviour and is a strict xfail until fixed;
remove the marker in the fix PR.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from ev_pipeline.match.matcher import MatchedFact, priority_of
from ev_pipeline.merge.merge import merge_facts, merge_variant_facts
from ev_pipeline.merge.policy import load_policies
from ev_pipeline.qa.value_guard import guard_impossible, guard_needs_backing
from ev_pipeline.release.build import _fact_dict, _flat_facts
from ev_pipeline.schema_models import Fact

REPO_POLICIES = load_policies(Path(__file__).resolve().parents[2] / "data" / "field_sources.yaml")
VID = "x-gen1-base"
UNITS = {
    "dc_peak_kw": "kW",
    "ac_kw": "kW",
    "battery_kwh_net": "kWh",
    "battery_kwh_gross": "kWh",
}
LIC = {
    "openev": "CDLA-Permissive-2.0",
    "kilowatt-openev": "MIT",
    "seed-manual": "CC-BY-4.0",
    "maker-docs": "none",
    "manual": "none",
}
_n = [0]


def _mf(
    source: str,
    fname: str,
    value: float,
    *,
    cited: bool = False,
    confidence: str = "medium",
    year: int = 2021,
    url: str | None = None,
) -> MatchedFact:
    _n[0] += 1
    record = f"{VID}#cited:{fname}" if cited else f"{source}-rec-{_n[0]}"
    src: dict[str, str] = {"id": source, "name": source, "licence": LIC[source]}
    if url:
        src["url"] = url
    fact = Fact(
        id=f"{source}:{record}:{fname}:{_n[0]}",
        subject_type="variant",
        subject_id=VID,
        field=fname,
        value=value,
        unit=UNITS[fname],
        source=src,
        source_record=record,
        retrieved_at=date(2026, 11, 15),
        confidence=confidence,
    )
    return MatchedFact(fact, source, priority_of(source), year)


@pytest.mark.xfail(strict=True, reason="A-06 F1")
def test_needs_backing_keeps_a_backed_value_when_the_winner_is_unbacked() -> None:
    """Audi Q4 40 in release 1: KilowattApp 143 (earliest year, wins) and 125, seed 125.
    The 125 group is backed (seed counts as backing per Q-091 default), but the guard
    deletes the whole field because only the winner is checked."""
    facts = [
        _mf("kilowatt-openev", "dc_peak_kw", 143, year=2021),
        _mf("kilowatt-openev", "dc_peak_kw", 125, year=2022),
        _mf("seed-manual", "dc_peak_kw", 125, confidence="low"),
    ]
    merged = {VID: merge_variant_facts(facts, REPO_POLICIES)}
    guard_needs_backing(merged, {VID: facts}, REPO_POLICIES)
    assert merged[VID].get("dc_peak_kw") is not None
    assert merged[VID]["dc_peak_kw"].value == 125


@pytest.mark.xfail(strict=True, reason="A-06 F1")
def test_needs_backing_does_not_drop_another_sources_value() -> None:
    """A lone KilowattApp DC peak outranks a maker-docs figure; withholding it must not
    also withhold the maker figure (the field should be merged again without it)."""
    facts = [
        _mf("kilowatt-openev", "dc_peak_kw", 150),
        _mf("maker-docs", "dc_peak_kw", 50),
    ]
    merged = {VID: merge_variant_facts(facts, REPO_POLICIES)}
    guard_needs_backing(merged, {VID: facts}, REPO_POLICIES)
    assert merged[VID].get("dc_peak_kw") is not None
    assert merged[VID]["dc_peak_kw"].value == 50


@pytest.mark.xfail(strict=True, reason="A-06 F2")
def test_impossible_guard_does_not_undo_a_cited_win() -> None:
    """Rule `cited` sets usable 88 (Ford) over OpenEV's lone 82. A lone, uncited OpenEV gross
    of 85 then makes usable > gross; the guard ranks the cited value at 0 support, drops it,
    and the overruled 82 comes back: a lone source beats the citation after all."""
    facts = [
        _mf("openev", "battery_kwh_net", 82),
        _mf("openev", "battery_kwh_gross", 85),
        _mf("seed-manual", "battery_kwh_net", 88, cited=True),
    ]
    merged = {VID: merge_variant_facts(facts, REPO_POLICIES)}
    assert merged[VID]["battery_kwh_net"].rule == "cited"
    guard_impossible(merged, {VID: facts}, REPO_POLICIES)
    net = merged[VID].get("battery_kwh_net")
    assert net is None or net.value != 82


@pytest.mark.xfail(strict=True, reason="A-06 F3")
def test_published_facts_keep_the_citation_url() -> None:
    """A seed `cited:` fact's only real provenance is its URL; facts.parquet drops it."""
    url = "https://www.fordpers.be/editor/files/ford_mustang_mach_e_2020_techspecs_eu_2.pdf"
    mf = _mf("seed-manual", "battery_kwh_net", 88, cited=True, url=url)
    flat = _flat_facts([_fact_dict(mf)], [mf.year])[0]
    assert url in flat.values()


@pytest.mark.xfail(strict=True, reason="A-06 F6")
def test_a_manual_citation_is_not_an_independent_confirmation() -> None:
    """merge.py: 'A cited fact still never counts as an independent confirmation'. A `manual`
    fact is cited by definition, yet it is counted as a second independent origin."""
    facts = [
        _mf("openev", "battery_kwh_net", 88),
        _mf("manual", "battery_kwh_net", 88),
    ]
    mg = merge_facts(facts, REPO_POLICIES.for_field("battery_kwh_net"))
    assert mg.independent_agreeing == 1
    assert mg.confidence != "high"
