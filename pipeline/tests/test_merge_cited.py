"""Rule `cited` (merge.py, field_sources.yaml `cited_wins`): a cited value beats a lone source.

Cases from the battery-gate work (2026-11-15): OpenEV's Mustang Mach-E GT at 82 kWh net
against Ford's own "88 kWh (useable)" (median mode), and one KilowattApp `ac_kw` against a
maker's figure (priority mode).
"""

from __future__ import annotations

from datetime import date

from ev_pipeline.match.matcher import MatchedFact, priority_of
from ev_pipeline.merge.merge import is_cited, merge_facts
from ev_pipeline.merge.policy import FieldPolicy, parse_policies
from ev_pipeline.schema_models import Fact

NET = FieldPolicy(
    order=("openev", "maker-docs", "kilowatt-openev", "seed-manual"), mode="median", tol_pct=2
)
AC = FieldPolicy(
    order=("openev", "kilowatt-openev", "maker-docs", "seed-manual"), mode="priority", tol_pct=2
)
LIC = {"openev": "MIT", "kilowatt-openev": "CC-BY-4.0", "seed-manual": "CC-BY-4.0"}


def _mf(
    source: str,
    value: float,
    key: str,
    fname: str = "battery_kwh_net",
    cited: bool = False,
    confidence: str = "medium",
    year: int = 2023,
) -> MatchedFact:
    record = f"x-gen1-gt#cited:{fname}" if cited else key
    fact = Fact(
        id=f"{source}:{record}:{fname}",
        subject_type="variant",
        subject_id="x-gen1-gt",
        field=fname,
        value=value,
        unit="kW" if fname == "ac_kw" else "kWh",
        source={"id": source, "name": source, "licence": LIC.get(source, "CC0-1.0")},
        source_record=record,
        retrieved_at=date(2026, 11, 15),
        confidence=confidence,
    )
    return MatchedFact(fact, source, priority_of(source), year)


def test_is_cited_needs_the_cited_record_and_medium_confidence() -> None:
    assert is_cited(_mf("seed-manual", 88, "s", cited=True))
    assert not is_cited(_mf("seed-manual", 88, "x-gen1-gt"))  # unchecked seed spec
    assert not is_cited(_mf("seed-manual", 88, "s", cited=True, confidence="low"))
    assert is_cited(_mf("manual", 88, "m"))
    assert not is_cited(_mf("openev", 88, "o"))


def test_cited_value_beats_one_source_in_median_mode() -> None:
    """Mach-E GT: OpenEV 82 alone vs Ford 88 (cited) + KilowattApp 88 and 91."""
    facts = [
        _mf("openev", 82, "o"),
        _mf("kilowatt-openev", 88, "k1", year=2022),
        _mf("kilowatt-openev", 91, "k2", year=2024),
        _mf("seed-manual", 88, "s", cited=True, year=2022),
    ]
    mg = merge_facts(facts, NET)
    assert mg.value == 88 and mg.rule == "cited"
    assert {c.source_id for c in mg.conflicts} == {"openev", "kilowatt-openev"}
    assert "cited source outvotes" in (mg.note() or "")
    # A citation is not an independent confirmation: KilowattApp is the one agreeing origin.
    assert mg.independent_agreeing == 1 and mg.confidence == "medium"


def test_cited_value_beats_one_attach_only_source_in_priority_mode() -> None:
    facts = [_mf("kilowatt-openev", 11, "k", "ac_kw"), _mf("seed-manual", 22, "s", "ac_kw", True)]
    mg = merge_facts(facts, AC)
    assert mg.value == 22 and mg.rule == "cited"
    assert [c.source_id for c in mg.conflicts] == ["kilowatt-openev"]


def test_unchecked_seed_value_does_not_win() -> None:
    facts = [_mf("kilowatt-openev", 11, "k", "ac_kw"), _mf("seed-manual", 22, "x-gen1-gt", "ac_kw")]
    assert merge_facts(facts, AC).value == 11


def test_two_agreeing_origins_beat_a_citation() -> None:
    facts = [
        _mf("openev", 82, "o"),
        _mf("kilowatt-openev", 82, "k"),
        _mf("seed-manual", 88, "s", cited=True),
    ]
    mg = merge_facts(facts, NET)
    assert mg.value == 82 and mg.rule == "median"
    assert [c.source_id for c in mg.conflicts] == ["seed-manual"]  # to review


def test_one_source_with_several_records_is_still_one_origin() -> None:
    facts = [
        _mf("kilowatt-openev", 11, "k1", "ac_kw"),
        _mf("kilowatt-openev", 11, "k2", "ac_kw"),
        _mf("seed-manual", 22, "s", "ac_kw", True),
    ]
    assert merge_facts(facts, AC).value == 22


def test_disagreeing_citations_win_nothing() -> None:
    facts = [
        _mf("openev", 82, "o"),
        _mf("seed-manual", 88, "s", cited=True),
        _mf("manual", 91, "m"),
    ]
    assert merge_facts(facts, NET).value == 82


def test_citation_that_agrees_with_the_winner_changes_nothing() -> None:
    facts = [_mf("openev", 88, "o"), _mf("seed-manual", 88.5, "s", cited=True)]
    mg = merge_facts(facts, NET)
    assert mg.winner.source_id == "openev" and mg.rule == "median"


def test_cited_wins_can_be_turned_off_per_field() -> None:
    off = FieldPolicy(order=AC.order, mode="priority", tol_pct=2, cited_wins=False)
    facts = [_mf("kilowatt-openev", 11, "k", "ac_kw"), _mf("seed-manual", 22, "s", "ac_kw", True)]
    assert merge_facts(facts, off).value == 11
    p = parse_policies({"fields": {"ac_kw": {"cited_wins": False}, "x": {}}})
    assert p.for_field("ac_kw").cited_wins is False
    assert p.for_field("x").cited_wins is True


def test_newest_mode_ignores_citations() -> None:
    newest = FieldPolicy(order=("rdw",), mode="newest")
    facts = [_mf("rdw", 30000, "r"), _mf("manual", 32000, "m")]
    assert merge_facts(facts, newest).rule == "newest"
