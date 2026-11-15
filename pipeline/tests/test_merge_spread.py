"""Same-source versions (rdw-tgk): one vote per source, spread is not a conflict."""

from __future__ import annotations

from datetime import date

from ev_pipeline.match.matcher import MatchedFact, priority_of
from ev_pipeline.merge.merge import SPREAD_NOTE, merge_facts
from ev_pipeline.schema_models import Fact

_LIC = {"rdw-tgk": "CC0-1.0", "openev": "CDLA-Permissive-2.0", "kilowatt-openev": "MIT"}


def _mf(source: str, value: float, key: str, year: int) -> MatchedFact:
    fact = Fact(
        id=f"{source}:{key}:nedc_range_km",
        subject_type="variant",
        subject_id="volkswagen-e-golf-mk7-24kwh",
        field="nedc_range_km",
        value=value,
        unit="km",
        source={"id": source, "name": source, "licence": _LIC[source]},
        retrieved_at=date(2026, 11, 15),
        confidence="high",
    )
    return MatchedFact(fact, source, priority_of(source), year)


def test_earliest_version_is_the_value_and_later_versions_are_spread() -> None:
    """e-Golf mk7: 190 km NEDC (2014 approvals), 175 km on a 2017 version of the same car."""
    facts = [_mf("rdw-tgk", 190, "a", 2014), _mf("rdw-tgk", 190, "b", 2015)]
    facts.append(_mf("rdw-tgk", 175, "c", 2017))
    mg = merge_facts(facts)
    assert mg.value == 190
    assert mg.conflicts == [] and mg.overruled == 0
    assert [f.fact.value for f in mg.spread] == [175]
    assert len(mg.fact_ids) == 2  # both 190 versions back the value
    note = mg.note() or ""
    assert SPREAD_NOTE in note and "rdw-tgk 175-190 km" in note


def test_versions_of_one_source_do_not_make_a_majority() -> None:
    """Three agreeing TGK versions are one source: they no longer outvote other sources."""
    tgk = [_mf("rdw-tgk", 300, k, 2017) for k in "abc"]
    mg = merge_facts([*tgk, _mf("openev", 280, "o", 2017)])
    assert mg.rule == "priority" and mg.value == 280  # openev outranks a 0-priority source
    # The losing source's versions are ordinary conflicts, not spread.
    assert {f.source_id for f in mg.conflicts} == {"rdw-tgk"} and mg.spread == []


def test_spread_version_agreeing_with_another_source_joins_the_value() -> None:
    facts = [_mf("rdw-tgk", 190, "a", 2014), _mf("rdw-tgk", 175, "c", 2017)]
    facts.append(_mf("kilowatt-openev", 176, "k", 2017))
    mg = merge_facts(facts)
    # Priority (both 0): earliest model year wins -> 190; kilowatt 176 is a real conflict.
    assert mg.value == 190
    assert [f.source_id for f in mg.conflicts] == ["kilowatt-openev"]
    assert [f.fact.value for f in mg.spread] == [175]
