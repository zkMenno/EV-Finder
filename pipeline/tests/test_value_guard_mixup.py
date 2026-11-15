"""qa/value_guard.guard_mixups: a value that repeats another field (ac_kw = battery kWh) goes to
review unless another independent source or a citation backs it (fixture: value_guard/)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
import yaml

from ev_pipeline.match.matcher import MatchedFact, priority_of
from ev_pipeline.merge.merge import merge_variant_facts
from ev_pipeline.merge.policy import FieldPolicy, Policies, load_policies, parse_policies
from ev_pipeline.qa.value_guard import guard_mixups
from ev_pipeline.schema_models import Fact

FIXTURE = Path(__file__).parent / "fixtures" / "value_guard" / "ac_mixups.yaml"
CASES = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))["cases"]
VID = "x-gen1-base"
UNITS = {"ac_kw": "kW", "battery_kwh_net": "kWh", "battery_kwh_gross": "kWh"}
LIC = {"seed-manual": "CC-BY-4.0", "kilowatt-openev": "CC-BY-4.0", "openev": "CC-BY-4.0"}
BATTERY = ("battery_kwh_net", "battery_kwh_gross")
POLICIES = Policies(
    {
        "ac_kw": FieldPolicy(
            order=("openev", "kilowatt-openev", "seed-manual"),
            mode="priority",
            tol_pct=2,
            mixup_with=BATTERY,
        ),
        "battery_kwh_net": FieldPolicy(order=("openev",), mode="median", tol_pct=2),
        "battery_kwh_gross": FieldPolicy(order=("openev",), mode="median", tol_pct=2),
    }
)


def _mf(i: int, f: dict) -> MatchedFact:
    src = f["source"]
    fact = Fact(
        id=f"{src}:{f['record']}:{f['field']}:{i}",
        subject_type="variant",
        subject_id=VID,
        field=f["field"],
        value=f["value"],
        unit=UNITS[f["field"]],
        source={"id": src, "name": src, "licence": LIC[src]},
        source_record=f["record"],
        retrieved_at=date(2026, 11, 15),
        confidence=f.get("confidence", "medium"),
    )
    return MatchedFact(fact, src, priority_of(src), 2018)


def _run(facts: list[MatchedFact]):
    merged = {VID: merge_variant_facts(facts, POLICIES)}
    rows = guard_mixups(merged, {VID: facts}, POLICIES)
    return merged[VID], rows


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_mixup_cases(case: dict) -> None:
    facts = [_mf(i, f) for i, f in enumerate(case["facts"])]
    mv, rows = _run(facts)
    want = case["expect"]
    got = mv["ac_kw"].value if "ac_kw" in mv else None
    assert got == want["ac_kw"]
    assert sorted(r["value"] for r in rows) == sorted(want["reviewed"])
    assert all(r["field"] == "ac_kw" and "field mix-up" in r["tolerance"] for r in rows)


def test_review_row_names_the_fact_and_the_field_it_repeats() -> None:
    facts = [_mf(i, f) for i, f in enumerate(CASES[0]["facts"])]
    _, rows = _run(facts)
    (row,) = rows
    assert row["variant_id"] == VID and row["source_id"] == "kilowatt-openev"
    assert row["fact_id"] == facts[1].fact.id
    assert "battery_kwh_gross" in row["tolerance"]


def test_fields_without_mixup_with_are_untouched() -> None:
    plain = Policies({"ac_kw": FieldPolicy(order=("kilowatt-openev",), mode="priority")})
    facts = [_mf(i, f) for i, f in enumerate(CASES[1]["facts"])]
    merged = {VID: merge_variant_facts(facts, plain)}
    before = merged[VID]["ac_kw"].value
    assert guard_mixups(merged, {VID: facts}, plain) == []
    assert merged[VID]["ac_kw"].value == before


def test_policy_parses_mixup_with() -> None:
    p = parse_policies({"fields": {"ac_kw": {"mixup_with": list(BATTERY)}, "x": {}}})
    assert p.for_field("ac_kw").mixup_with == BATTERY
    assert p.for_field("x").mixup_with == ()


def test_repo_field_sources_guards_ac_kw_against_the_battery() -> None:
    repo = Path(__file__).resolve().parents[2] / "data" / "field_sources.yaml"
    assert set(load_policies(repo).for_field("ac_kw").mixup_with) == set(BATTERY)
