"""T-005 merge rules: priority, majority, recency, confidence, provenance ids."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from ev_pipeline.match.matcher import MatchedFact, priority_of
from ev_pipeline.merge.merge import agree, merge_drivetrain, merge_facts, merge_variant_facts
from ev_pipeline.merge.policy import FieldPolicy, load_policies, parse_policies
from ev_pipeline.schema_models import Fact

_SOURCES = {
    "openev": "CDLA-Permissive-2.0",
    "eea": "CC-BY-4.0",
    "seed-manual": "CC-BY-4.0",
}


def mf(
    source: str,
    value: float,
    key: str,
    *,
    year: int | None = 2022,
    field: str = "battery_kwh_net",
    retrieved: date = date(2026, 11, 14),
    confidence: str = "medium",
    country: str | None = None,
) -> MatchedFact:
    fact = Fact(
        id=f"{source}:{key}:{field}",
        subject_type="variant",
        subject_id="x-gen1-base",
        field=field,
        value=value,
        unit="EUR" if field == "price_new" else "kWh",
        country=country,
        source={"id": source, "name": source, "licence": _SOURCES[source]},
        retrieved_at=retrieved,
        confidence=confidence,
    )
    return MatchedFact(fact, source, priority_of(source), year)


def test_agree_within_three_percent() -> None:
    assert agree(100, 103)
    assert agree(103, 100)
    assert not agree(100, 103.5)
    assert agree("awd", "awd") and not agree("awd", "fwd")


def test_priority_openev_over_eea_over_seed_manual() -> None:
    m = merge_facts([mf("seed-manual", 40, "s"), mf("eea", 50, "e"), mf("openev", 60, "o")])
    assert m.value == 60 and m.rule == "priority"
    assert m.overruled == 2
    m = merge_facts([mf("seed-manual", 40, "s"), mf("eea", 50, "e")])
    assert m.value == 50


def test_majority_beats_priority() -> None:
    # Three values agree within 3% (75, 76, 75.5); openev's 60 is outvoted.
    facts = [
        mf("openev", 60, "o"),
        mf("eea", 75, "e1"),
        mf("eea", 76, "e2"),
        mf("seed-manual", 75.5, "s"),
    ]
    m = merge_facts(facts)
    assert m.rule == "majority"
    # Within the majority group, priority then recency: eea beats seed-manual; e1/e2 have
    # the same date and year, so the fact id breaks the tie (e2 > e1).
    assert m.value == 76
    assert m.fact_ids == [
        "eea:e2:battery_kwh_net",
        "eea:e1:battery_kwh_net",
        "seed-manual:s:battery_kwh_net",
    ]
    assert m.overruled == 1


def test_two_agreeing_is_not_a_majority() -> None:
    m = merge_facts([mf("openev", 60, "o"), mf("eea", 75, "e1"), mf("seed-manual", 75, "s")])
    assert m.value == 60 and m.rule == "priority"


def test_recency_breaks_ties_within_a_source() -> None:
    newer_year = merge_facts([mf("openev", 602, "a", year=2022), mf("openev", 629, "b", year=2023)])
    assert newer_year.value == 629
    newer_fetch = merge_facts(
        [
            mf("openev", 602, "a", year=2023, retrieved=date(2026, 11, 15)),
            mf("openev", 629, "b", year=2023, retrieved=date(2026, 1, 1)),
        ]
    )
    assert newer_fetch.value == 602


def test_confidence_high_needs_two_independent_sources() -> None:
    m = merge_facts([mf("openev", 75, "o"), mf("eea", 74, "e", confidence="low")])
    assert m.confidence == "high"
    assert m.source_ids == ["openev", "eea"]
    # seed-manual is unchecked: it never confirms a value on its own.
    m = merge_facts([mf("openev", 75, "o"), mf("seed-manual", 75, "s", confidence="low")])
    assert m.confidence == "medium"
    assert m.independent_agreeing == 1
    assert m.source_ids == ["openev", "seed-manual"]
    # Disagreeing second source: winner's own confidence.
    m = merge_facts([mf("openev", 75, "o"), mf("eea", 50, "e")])
    assert m.confidence == "medium" and m.fact_ids == ["openev:o:battery_kwh_net"]


def test_single_fact() -> None:
    m = merge_facts([mf("eea", 75, "e", confidence="low")])
    assert m.rule == "single" and m.confidence == "low" and m.note() is None


def test_merge_variant_facts_splits_prices_by_country() -> None:
    facts = [
        mf("openev", 75, "o"),
        mf("openev", 50000, "p-nl", field="price_new", country="NL"),
        mf("openev", 45000, "p-uk", field="price_new", country="UK"),
    ]
    out = merge_variant_facts(facts)
    assert set(out) == {"battery_kwh_net", "price_new.NL", "price_new.UK"}
    assert out["price_new.UK"].value == 45000


def test_merge_drivetrain_priority() -> None:
    assert merge_drivetrain([(10, "fwd", "seed-manual"), (30, "awd", "openev")]) == (
        "awd",
        ["openev"],
    )
    assert merge_drivetrain([]) == (None, [])


def test_empty_merge_raises() -> None:
    with pytest.raises(ValueError):
        merge_facts([])


# --- field policies from data/field_sources.yaml (Decision 009) ----------------------------


def test_policies_parse_order_tolerance_mode() -> None:
    pol = parse_policies(
        {
            "fields": {
                "wltp_range_km": {
                    "primary": ["eea", "rdw"],
                    "fallbacks": ["openev", "seed-manual"],
                    "tolerance": {"pct": 2},
                    "merge": "priority",
                },
                "length_mm": {"primary": ["rdw"], "tolerance": {"abs": 10, "unit": "mm"}},
                "price_new_nl": {"primary": ["rdw"], "merge": "newest"},
            }
        }
    )
    w = pol.for_field("wltp_range_km")
    assert w.order == ("eea", "rdw", "openev", "seed-manual") and w.tol_pct == 2
    assert w.priority("eea") > w.priority("openev") > w.priority("seed-manual")
    assert w.priority("unlisted") < w.priority("seed-manual")
    assert pol.for_field("length_mm").agree(4690, 4700)
    assert not pol.for_field("length_mm").agree(4690, 4701)
    assert pol.for_field("price_new.NL").mode == "newest"
    assert pol.for_field("price_new.DE").mode == "default"  # no price_new_other given
    assert pol.for_field("boot_l").mode == "default"


def test_repo_field_sources_file_loads() -> None:
    pol = load_policies(Path(__file__).parents[2] / "data" / "field_sources.yaml")
    if not pol.fields:
        pytest.skip("data/field_sources.yaml not present")
    assert pol.for_field("battery_kwh_net").mode == "median"


def test_policy_priority_order_overrides_default() -> None:
    pol = FieldPolicy(order=("eea", "openev"), mode="priority", tol_pct=2)
    m = merge_facts([mf("openev", 602, "o"), mf("eea", 629, "e")], pol)
    assert m.value == 629 and m.rule == "priority"
    # No majority under an explicit policy: three openev values do not outvote eea.
    m = merge_facts(
        [
            mf("openev", 602, "a"),
            mf("openev", 602, "b"),
            mf("openev", 602, "c"),
            mf("eea", 629, "e"),
        ],
        pol,
    )
    assert m.value == 629


def test_policy_median_is_a_real_value_never_an_average() -> None:
    pol = FieldPolicy(order=("openev", "eea"), mode="median", tol_pct=2)
    facts = [
        mf("openev", 75.0, "a"),
        mf("eea", 74.0, "b"),
        mf("eea", 75.5, "c"),
        mf("eea", 60, "x"),
    ]
    m = merge_facts(facts, pol)
    # agreeing with the anchor (75.0): 74.0, 75.0, 75.5 -> median 75.0; 60 is a conflict.
    assert m.value == 75.0 and m.rule == "median"
    assert [c.fact.value for c in m.conflicts] == [60]
    # Even count: low median, still one of the inputs.
    m = merge_facts([mf("openev", 75.0, "a"), mf("eea", 74.0, "b")], pol)
    assert m.value == 74.0


def test_policy_newest() -> None:
    pol = FieldPolicy(order=("rdw", "openev"), mode="newest")
    m = merge_facts(
        [
            mf("openev", 50000, "o", retrieved=date(2026, 11, 14)),
            mf("eea", 52000, "e", retrieved=date(2026, 11, 15)),
        ],
        pol,
    )
    assert m.value == 52000 and m.rule == "newest"


def test_agreeing_sources_and_conflicts() -> None:
    pol = FieldPolicy(order=("openev", "eea"), mode="priority", tol_pct=2)
    m = merge_facts([mf("openev", 75, "o"), mf("eea", 74, "e"), mf("seed-manual", 60, "s")], pol)
    assert m.agreeing_sources == 2 and m.confidence == "high"
    assert [c.source_id for c in m.conflicts] == ["seed-manual"]
    assert m.tolerance == "±2%"
    single = merge_facts([mf("seed-manual", 60, "s")], pol)
    assert single.agreeing_sources == 1  # at least the winner itself
