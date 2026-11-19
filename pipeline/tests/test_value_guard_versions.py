"""T-155: qa/value_guard.guard_versions. A TGK version's consumption and worst-case WLTP stay
only next to a best case they belong with. SYNTHETIC facts shaped like the real cases:
- ë-SpaceTourer: the 50 and 75 kWh versions carry the same names (best 238 vs 339 km);
- Leaf e+: the 2022 extension (best 449 / worst 410) next to the first versions' 385 km;
- Leaf 40 kWh: worst 287 km (2022, best 300) next to the 270 km best case.
"""

from __future__ import annotations

from datetime import date

from ev_pipeline.match.matcher import MatchedFact, priority_of
from ev_pipeline.merge.merge import merge_variant_facts
from ev_pipeline.merge.policy import load_policies
from ev_pipeline.qa.checks import impossible_values
from ev_pipeline.qa.value_guard import OTHER_FAMILY, WORST_ABOVE_BEST, run_guards
from ev_pipeline.release.build import REPO_ROOT
from ev_pipeline.schema_models import Fact

VID = "x-gen1-base"
UNITS = {"wltp_range_km": "km", "wltp_range_km_worst": "km", "consumption_kwh_100km": "kWh/100km"}
LIC = {"rdw-tgk": "CC0-1.0", "manual": "none", "openev": "CDLA-Permissive-2.0"}
POLICIES = load_policies(REPO_ROOT / "data" / "field_sources.yaml")


def _mf(src: str, record: str, field: str, value: float, year: int = 2020) -> MatchedFact:
    fact = Fact(
        id=f"{src}:{record}:{field}",
        subject_type="variant",
        subject_id=VID,
        field=field,
        value=value,
        unit=UNITS[field],
        source={"id": src, "name": src, "licence": LIC[src]},
        source_record=record,
        retrieved_at=date(2026, 11, 19),
        confidence="high" if src == "rdw-tgk" else "medium",
    )
    return MatchedFact(fact, src, priority_of(src), year)


def _version(rec: str, best: float, worst: float | None, cons: float, year: int = 2020):
    out = [
        _mf("rdw-tgk", rec, "wltp_range_km", best, year),
        _mf("rdw-tgk", rec, "consumption_kwh_100km", cons, year),
    ]
    if worst is not None:
        out.append(_mf("rdw-tgk", rec, "wltp_range_km_worst", worst, year))
    return out


def _run(facts: list[MatchedFact]):
    merged = {VID: merge_variant_facts(facts, POLICIES)}
    rows = run_guards(merged, {VID: facts}, POLICIES)
    return merged[VID], rows


def test_versions_of_the_other_battery_go_to_review() -> None:
    facts = [
        _mf("manual", "cited", "wltp_range_km", 230),
        *_version("v50a", 238, 196, 23.03),
        *_version("v50b", 234, 196, 22.35, 2024),
        *_version("v75", 339, 285, 24.68, 2019),  # earliest year: would win the spread
    ]
    mv, rows = _run(facts)
    assert mv["wltp_range_km"].value == 230
    assert mv["consumption_kwh_100km"].value == 23.03
    assert mv["wltp_range_km_worst"].value == 196
    held = {(r["field"], r["value"]) for r in rows if r["tolerance"].startswith(OTHER_FAMILY)}
    assert held == {("consumption_kwh_100km", 24.68), ("wltp_range_km_worst", 285)}
    assert all("339 km vs shipped 230 km" in r["tolerance"] for r in rows if r["value"] == 285)


def test_leaf_e_plus_extension_worst_case_is_held() -> None:
    facts = [
        _mf("manual", "cited", "wltp_range_km", 385),
        *_version("ext01", 385, None, 18.5, 2019),
        *_version("ext08", 449, 410, 14.7, 2022),
    ]
    mv, rows = _run(facts)
    assert mv["wltp_range_km"].value == 385
    assert "wltp_range_km_worst" not in mv
    assert mv["consumption_kwh_100km"].value == 18.5
    assert {r["field"] for r in rows} == {"wltp_range_km_worst", "consumption_kwh_100km"}


def test_worst_above_the_shipped_best_case_is_held() -> None:
    facts = [
        *_version("a02", 270, None, 20.6, 2019),
        *_version("a02b", 270, None, 17.1, 2020),
        *_version("a06", 300, 287, 14.6, 2022),  # 11 %: same battery, kept as a version
    ]
    mv, rows = _run(facts)
    assert mv["wltp_range_km"].value == 270
    assert "wltp_range_km_worst" not in mv
    assert [(r["field"], r["value"]) for r in rows] == [("wltp_range_km_worst", 287)]
    assert rows[0]["tolerance"].startswith(WORST_ABOVE_BEST)


def test_same_family_versions_are_untouched() -> None:
    facts = [
        _mf("manual", "cited", "wltp_range_km", 330),
        *_version("p78", 339, 285, 24.68, 2021),
        *_version("b0", 370, 313, 22.4, 2024),  # +12 %: newer version, same battery
    ]
    mv, rows = _run(facts)
    assert rows == []
    assert mv["wltp_range_km_worst"].value == 285


def test_qa_flags_worst_above_best() -> None:
    cat = {
        "rows": [
            {"variant_id": "a", "wltp_range_km": 385, "wltp_range_km_worst": 410},
            {"variant_id": "b", "wltp_range_km": 385, "wltp_range_km_worst": 385},
        ]
    }
    out = impossible_values(cat, [])
    assert [(o["variant_id"], o["rule"]) for o in out] == [("a", "wltp_worst_gt_best")]


def test_a_version_whose_wltp_another_guard_took_out_is_still_checked() -> None:
    from ev_pipeline.qa.value_guard import guard_versions

    facts = [
        _mf("manual", "cited", "wltp_range_km", 230),
        *_version("v50", 238, 196, 23.03),
        *_version("v75", 339, 285, 24.68, 2019),
    ]
    merged = {VID: merge_variant_facts(facts, POLICIES)}
    pool = {VID: [f for f in facts if f.fact.id != "rdw-tgk:v75:wltp_range_km"]}
    rows = guard_versions(merged, pool, POLICIES, {VID: facts})
    assert {(r["field"], r["value"]) for r in rows} == {
        ("consumption_kwh_100km", 24.68),
        ("wltp_range_km_worst", 285),
    }
