"""T-007 derived metrics: formulas with worked numbers, ladder rungs, era, tier, rows."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from ev_pipeline.derive import metrics as m
from ev_pipeline.derive.links import finish_voltage, inherited_for, load_links
from ev_pipeline.derive.rows import build_rows
from ev_pipeline.match.matcher import CLAIM_SOURCES, MatchedFact, VariantInfo, priority_of
from ev_pipeline.match.seed import load_seed
from ev_pipeline.merge.merge import merge_variant_facts
from ev_pipeline.release.validate import provenance_errors
from ev_pipeline.schema_models import Fact

FIX = Path(__file__).parent / "fixtures" / "release"
TODAY = date(2026, 11, 15)


# --- formulas (worked numbers) -----------------------------------------------------------


def test_consumption_estimate() -> None:
    # 75 kWh / 629 km * 100 = 11.92 kWh/100km
    assert m.consumption_estimate(75, 629) == pytest.approx(11.9237, abs=1e-4)


def test_ac_km_per_h() -> None:
    # 11 kW / 16 kWh/100km * 100 = 68.75 km per hour of AC charging
    assert m.ac_km_per_h(11, 16) == pytest.approx(68.75)


def test_net_from_gross_and_epa() -> None:
    assert m.net_from_gross(24) == pytest.approx(22.32)  # 0.93 x gross
    assert m.wltp_from_epa(500) == pytest.approx(560)  # EPA x 1.12


def test_flat_curve_integration() -> None:
    # Flat 100 kW, 70 kWh net: window 49 kWh -> 0.49 h = 29.4 min, avg 100 kW, all at peak.
    s = m.integrate_curve([(0, 100), (100, 100)], 70)
    assert s.avg_kw == pytest.approx(100)
    assert s.minutes == pytest.approx(29.4)
    assert s.peak_held_min == pytest.approx(29.4)


def test_linear_curve_integration() -> None:
    # 150 kW at 10% falling to 50 kW at 80%, 70 kWh: t = 0.7*70/100 * ln(3)/... closed form:
    # hours = 70/100 * 70 / (150-50) * ln(150/50) = 0.5383 h -> 32.3 min; avg = 49/0.5383.
    import math

    s = m.integrate_curve([(10, 150), (80, 50)], 70)
    hours = 0.7 * 70 / 100 * math.log(3)
    assert s.minutes == pytest.approx(hours * 60, rel=1e-3)
    assert s.avg_kw == pytest.approx(49 / hours, rel=1e-3)
    # >= 135 kW (90% of 150) until SoC 20.5%: about 10.5% of 70 kWh at ~142.5 kW.
    assert s.peak_held_min == pytest.approx(70 * 0.105 / 142.5 * 60, rel=0.02)


def test_default_curve_shape() -> None:
    # Flat at peak 10-25%, linear down to 35% of peak at 80%: average ~0.674 x peak.
    s = m.integrate_curve(m.default_curve(100), None)
    assert s.avg_kw == pytest.approx(67.4, abs=0.2)
    assert s.minutes is None  # no battery size, no minutes
    s = m.integrate_curve(m.default_curve(250), 75)
    assert s.avg_kw == pytest.approx(168.5, abs=0.3)
    assert s.minutes == pytest.approx(75 * 0.7 / s.avg_kw * 60)


def test_unusable_curve() -> None:
    assert m.integrate_curve([(0, 0), (100, 0)], 50) is None
    assert m.integrate_curve([(10, 50)], 50) is None


def test_motorway_and_km_in_minutes() -> None:
    assert m.motorway_consumption(16) == pytest.approx(20.8)  # x 1.30
    # 110 kW for 10 min = 18.33 kWh at 20.8 kWh/100km = 88.1 km
    assert m.km_in_minutes(110, 10, 20.8) == pytest.approx(88.14, abs=0.01)
    # Capped by the 10->80% window: 40 kWh x 0.7 = 28 kWh max -> 134.6 km, not 176.3 km.
    assert m.km_in_minutes(110, 20, 20.8, 40) == pytest.approx(28 / 20.8 * 100)
    assert m.km_in_minutes(110, 20, 20.8) == pytest.approx(176.28, abs=0.01)
    assert m.minutes_from_avg(75, 110) == pytest.approx(75 * 0.7 / 110 * 60)


@pytest.mark.parametrize(
    ("year", "era"),
    [
        (2011, "pre-2018"),
        (2017, "pre-2018"),
        (2018, "2018-20"),
        (2020, "2018-20"),
        (2021, "2021-22"),
        (2022, "2021-22"),
        (2023, "2023-24"),
        (2024, "2023-24"),
        (2025, "2025+"),
        (2030, "2025+"),
    ],
)
def test_era(year: int, era: str) -> None:
    assert m.era(year) == era


def test_quality_tier() -> None:
    assert m.quality_tier(2, 2) == "sourced"
    assert m.quality_tier(2, 1) == "single-source"
    assert m.quality_tier(0, 0) == "single-source"
    assert m.quality_tier(0, 0, checked=True) == "checked"


# --- real-range ladder -------------------------------------------------------------------


def _li(
    vid: str,
    gen: str = "g1",
    battery: float | None = 60,
    wltp: float | None = 400,
    body: str | None = "suv",
    drivetrain: str | None = "fwd",
    make: str = "acme",
):
    return m.LadderInput(vid, gen, make, body, drivetrain, battery, wltp, ["openev"], [f"f:{vid}"])


def _obs(km: float, rung: str = "exact-test") -> m.RealObservation:
    return m.RealObservation(km, rung, ["test"], ["test:1:real_range_km"], "medium")


def test_ladder_own_data_wins() -> None:
    a = _li("a")
    r = m.real_range(a, [a], {"a": _obs(333, "owner-data")})
    assert (r.km, r.rung) == (333, "owner-data")


def test_ladder_sibling_variant_scales_by_battery() -> None:
    a, b, c = _li("a", battery=60), _li("b", battery=80), _li("c", battery=40)
    obs = {"b": _obs(400), "c": _obs(250)}
    r = m.real_range(a, [a, b, c], obs)
    # Closest battery is b (80, |20|) vs c (40, |20|): tie -> same rung -> variant id "b".
    assert r.rung == "sibling-variant"
    assert r.km == pytest.approx(400 * 60 / 80)  # 300 km
    assert "scaled from b" in r.note


def test_ladder_sibling_must_share_generation() -> None:
    a, b = _li("a", gen="g1"), _li("b", gen="g2", drivetrain="rwd")
    r = m.real_range(a, [a, b], {"b": _obs(400)})
    assert r.rung == "body-ratio"


def test_ladder_brand_body_drivetrain_ratio() -> None:
    # Same make/body/drivetrain, other generation, measured 320 of 400 WLTP -> ratio 0.8.
    a, b = _li("a", gen="g1", wltp=500), _li("b", gen="g2", wltp=400)
    r = m.real_range(a, [a, b], {"b": _obs(320)})
    assert r.rung == "brand-body-drivetrain-ratio"
    assert r.km == pytest.approx(400)  # 500 x 0.8


def test_ladder_body_ratio_with_awd_adjustment() -> None:
    # sedan 0.88, awd -0.02 -> 0.86 x 629 = 540.94
    r = m.real_range(_li("a", body="sedan", drivetrain="awd", wltp=629), [], {})
    assert r.rung == "body-ratio"
    assert r.km == pytest.approx(540.94)
    assert "PROVISIONAL" in r.note
    r = m.real_range(_li("a", body="hatchback", drivetrain="fwd", wltp=300), [], {})
    assert r.km == pytest.approx(255)


def test_ladder_needs_wltp_or_body() -> None:
    assert m.real_range(_li("a", wltp=None), [], {}) is None
    assert m.real_range(_li("a", body=None), [], {}) is None


def test_body_ratios_documented() -> None:
    assert m.BODY_RATIOS["hatchback"] == 0.85
    assert m.BODY_RATIOS["suv"] == 0.80
    assert m.DRIVETRAIN_ADJ["awd"] == -0.02


# --- rows --------------------------------------------------------------------------------


def _fact(
    field: str,
    value: float,
    unit: str,
    source: str = "openev",
    key: str = "k",
    country: str | None = None,
) -> MatchedFact:
    f = Fact(
        id=f"{source}:{key}:{field}",
        subject_type="variant",
        subject_id="tesla-model-3-gen1-lr",
        field=field,
        value=value,
        unit=unit,
        country=country,
        source={"id": source, "name": source, "licence": "CC-BY-4.0"},
        retrieved_at=date(2026, 11, 14),
        confidence="medium",
        claim=True if source in CLAIM_SOURCES else None,
    )
    return MatchedFact(f, source, priority_of(source), 2022, "tesla-model-3-gen1", "tesla-model-3")


def _row(facts: list[MatchedFact], drivetrain: str | None = "awd", **info_kw):
    seed = load_seed(FIX / "models.yaml")
    info = VariantInfo(
        "tesla-model-3-gen1-lr", "tesla-model-3-gen1", "Long Range", years={2022}, **info_kw
    )
    if drivetrain:
        info.drivetrains.append((30, drivetrain, "openev"))
    rows, problems = build_rows(
        {info.id: info}, {info.id: merge_variant_facts(facts)}, seed, {}, TODAY, 1
    )
    return rows[0], problems


def test_row_derived_values_and_provenance() -> None:
    row, problems = _row(
        [
            _fact("battery_kwh_net", 75, "kWh"),
            _fact("wltp_range_km", 629, "km"),
            _fact("ac_kw", 11, "kW"),
            _fact("dc_peak_kw", 250, "kW"),
            _fact("price_new", 56990, "EUR", country="NL"),
        ]
    )
    assert problems == []
    assert row["consumption_kwh_100km"] == 11.9
    assert row["ac_km_per_h"] == 92.3  # 11 / 11.9237 * 100
    # Default curve from 250 kW peak: avg 168.5 kW; 75 kWh -> 18.7 min.
    assert row["dc_avg_10_80_kw"] == 168.5
    assert row["dc_curve_status"] == "default"
    assert row["dc_minutes_10_80"] == 18.7
    # Motorway 11.9237 x 1.3 = 15.5; 168.5 kW x 10/60 = 28.1 kWh -> 181.2 km
    assert row["consumption_motorway_kwh_100km"] == 15.5
    assert row["dc_km_per_10min"] == 181.2
    # 20 min = 56.2 kWh, capped at 75 x 0.7 = 52.5 kWh -> 338.7 km
    assert row["dc_km_per_20min"] == 338.7
    assert row["dc_peak_kw_is_claim"] is True  # openev = claim tonight
    assert row["real_range_km"] == 540.9 and row["real_range_rung"] == "body-ratio"
    assert row["price_new"] == {"NL": {"amount": 56990.0, "currency": "EUR"}}
    pv = row["provenance"]
    assert pv["consumption_kwh_100km"]["derived"] is True
    assert pv["consumption_kwh_100km"]["confidence"] == "low"
    assert pv["dc_avg_10_80_kw"]["estimate"] is True
    assert "model-estimate" in pv["dc_avg_10_80_kw"]["source_ids"]
    assert pv["consumption_motorway_kwh_100km"]["estimate"] is True
    assert (
        pv["dc_avg_10_80_kw"]["derived"] is True and "PROVISIONAL" in pv["dc_avg_10_80_kw"]["note"]
    )
    assert pv["ac_km_per_h"]["fact_ids"][0] == "openev:k:ac_kw"
    assert "derived" not in pv["battery_kwh_net"]
    assert row["segment"] == "D" and row["body"] == "sedan" and row["drivetrain"] == "awd"
    assert row["change_markers"] == [{"year": 2021, "text": "Refresh: heat pump"}]
    assert row["era"] == "2021-22"
    assert row["on_sale_new"] is False  # generation ended 2023
    assert provenance_errors([row]) == []


def test_given_consumption_is_not_overwritten() -> None:
    row, _ = _row(
        [
            _fact("battery_kwh_net", 75, "kWh"),
            _fact("wltp_range_km", 547, "km"),
            _fact("consumption_kwh_100km", 16, "kWh/100km"),
            _fact("ac_kw", 11, "kW"),
            _fact("dc_avg_10_80_kw", 110, "kW"),
        ]
    )
    assert row["consumption_kwh_100km"] == 16.0
    assert "derived" not in row["provenance"]["consumption_kwh_100km"]
    assert row["ac_km_per_h"] == 68.8
    # Motorway 16 x 1.3 = 20.8; 110 kW x 10/60 = 18.33 kWh -> 88.1 km
    assert row["dc_km_per_10min"] == 88.1
    assert "derived" not in row["provenance"]["dc_avg_10_80_kw"]
    assert row.get("dc_curve_status") is None  # sourced average, no curve
    assert row["dc_minutes_10_80"] == pytest.approx(75 * 0.7 / 110 * 60, abs=0.05)


def test_net_from_gross_fallback() -> None:
    row, _ = _row([_fact("battery_kwh_gross", 24, "kWh"), _fact("wltp_range_km", 200, "km")])
    assert row["battery_kwh_net"] == 22.3
    p = row["provenance"]["battery_kwh_net"]
    assert p["derived"] is True and p["confidence"] == "low" and "gross" in p["note"]
    assert row["consumption_kwh_100km"] == pytest.approx(11.2, abs=0.05)
    assert p["estimate"] is True


def test_epa_only_gives_wltp_equivalent_for_real_range() -> None:
    row, _ = _row([_fact("battery_kwh_net", 75, "kWh"), _fact("epa_range_km", 500, "km")])
    assert row["wltp_range_km"] is None  # never publish an EPA-derived figure as WLTP
    assert row["real_range_km"] == pytest.approx(560 * 0.86, abs=0.05)
    assert "EPA" in row["provenance"]["consumption_kwh_100km"]["note"]


def test_derived_out_of_range_is_dropped() -> None:
    # 75 kWh / 200 km -> 37.5 kWh/100km, above 35: dropped, and nothing built on it.
    row, problems = _row(
        [
            _fact("battery_kwh_net", 75, "kWh"),
            _fact("wltp_range_km", 200, "km"),
            _fact("ac_kw", 11, "kW"),
        ]
    )
    assert row["consumption_kwh_100km"] is None and row["ac_km_per_h"] is None
    assert [p.field for p in problems] == ["consumption_kwh_100km"]


def test_on_sale_new_rules() -> None:
    seed = load_seed(FIX / "models.yaml")
    facts = [_fact("battery_kwh_net", 60, "kWh")]
    for years, expected in [({2025}, True), ({2026}, True), ({2023}, False)]:
        info = VariantInfo("tesla-model-3-highland-x", "tesla-model-3-highland", "X", years=years)
        rows, _ = build_rows(
            {info.id: info}, {info.id: merge_variant_facts(facts)}, seed, {}, TODAY, 1
        )
        assert rows[0]["on_sale_new"] is expected, years


def test_quality_tier_sourced_in_row() -> None:
    row, _ = _row(
        [
            _fact("battery_kwh_net", 75, "kWh"),
            _fact("battery_kwh_net", 75, "kWh", source="eea"),
            _fact("wltp_range_km", 629, "km"),
            _fact("wltp_range_km", 625, "km", source="eea"),
        ]
    )
    assert row["quality_tier"] == "sourced"
    assert row["provenance"]["battery_kwh_net"]["confidence"] == "high"
    row, _ = _row(
        [
            _fact("battery_kwh_net", 75, "kWh"),
            _fact("battery_kwh_net", 75, "kWh", source="seed-manual"),
            _fact("wltp_range_km", 629, "km"),
            _fact("wltp_range_km", 625, "km", source="eea"),
        ]
    )
    assert row["quality_tier"] == "single-source"  # seed-manual does not confirm


def test_measured_curve_wins_and_is_not_an_estimate() -> None:
    import json

    curve = {"points": [[10, 100], [80, 100]], "status": "measured"}
    f = _fact("dc_avg_10_80_kw", 60, "kW")
    c = _fact("dc_curve", 0, "kW")
    c.fact = c.fact.model_copy(update={"value": json.loads(json.dumps(curve))})
    from ev_pipeline.schema_models import ChargeCurve

    c.fact = c.fact.model_copy(update={"value": ChargeCurve.model_validate(curve)})
    row, _ = _row([_fact("battery_kwh_net", 70, "kWh"), _fact("wltp_range_km", 500, "km"), f, c])
    assert row["dc_curve_status"] == "measured"
    assert row["dc_avg_10_80_kw"] == 100.0  # measured curve beats the maker average
    assert row["dc_minutes_10_80"] == 29.4
    assert row["dc_peak_held_min"] == 29.4
    assert "estimate" not in row["provenance"]["dc_avg_10_80_kw"]


def test_peak_not_claim_for_non_claim_source() -> None:
    row, _ = _row([_fact("dc_peak_kw", 100, "kW", source="eea")])
    assert row["dc_peak_kw_is_claim"] is False


# --- platforms, packs, voltage (Decision 010) ----------------------------------------------


def _links():
    import shutil
    import tempfile

    d = Path(tempfile.mkdtemp())
    (d / "seed").mkdir()
    for n in ("platforms", "battery_packs", "variant_links"):
        shutil.copy(FIX / f"{n}.yaml", d / "seed" / f"{n}.yaml")
    shutil.copytree(FIX / "taxonomy", d / "taxonomy")
    return load_links(d)


def test_pack_values_are_inherited_unless_own_fact() -> None:
    links = _links()
    inh = inherited_for(links, "tesla-model-3-gen1-lr", "tesla-model-3-gen1", {})
    net, p = inh["numbers"]["battery_kwh_net"]
    assert net == 57.5 and p["note"] == "inherited from pack tesla-lfp-60"
    assert p["fact_ids"] == ["seed-manual:battery_pack/tesla-lfp-60:battery_kwh_net"]
    assert inh["labels"]["chemistry_id"] == "lfp"
    assert inh["numbers"]["voltage_nominal_v"][0] == 340  # pack beats platform (350)
    assert inh["labels"]["platform_id"] == "tesla-3y"  # from the generation link
    own = inherited_for(
        links,
        "tesla-model-3-gen1-lr",
        "tesla-model-3-gen1",
        {"battery_kwh_net": 75, "chemistry_id": "nmc"},
    )
    assert "battery_kwh_net" not in own["numbers"] and "chemistry_id" not in own["labels"]


def test_variant_link_beats_generation_link() -> None:
    links = _links()
    link = links.link_for("tesla-model-3-gen1-lr", "tesla-model-3-gen1")
    assert link["platform_id"] == "tesla-3y" and link["battery_pack_id"] == "tesla-lfp-60"


@pytest.mark.parametrize(
    ("row", "cls", "fast"),
    [
        ({"voltage_nominal_v": 350.0}, "400v", True),
        ({"voltage_nominal_v": 800.0}, "800v", None),
        (
            {"voltage_nominal_v": 800.0, "charger_400v_mode": "booster", "charger_400v_kw": 50.0},
            "800v",
            True,
        ),
        (
            {"voltage_nominal_v": 800.0, "charger_400v_mode": "limited", "charger_400v_kw": 40.0},
            "800v",
            False,
        ),
        ({"voltage_nominal_v": 800.0, "charger_400v_mode": "native"}, "800v", True),
        ({"voltage_label": "not-disclosed"}, "not-disclosed", None),
        ({}, None, None),
    ],
)
def test_voltage_class_and_fast_on_400v(row, cls, fast) -> None:
    finish_voltage(_links(), row, None)
    assert row.get("voltage_class_id") == cls
    assert row.get("fast_on_400v") == fast


def test_voltage_class_from_platform_when_no_nominal() -> None:
    row: dict = {}
    finish_voltage(_links(), row, "tesla-3y")
    assert row["voltage_class_id"] == "400v"


def test_charge_100_daily_from_chemistry() -> None:
    links = _links()
    for chem, expected in (("lfp", True), ("nmc", False), ("unknown", None)):
        row = {"chemistry_id": chem}
        finish_voltage(links, row, None)
        assert row.get("charge_100_daily") == expected


def test_not_disclosed_numbers_stay_empty_and_class_override() -> None:
    links = _links()
    links.platforms["tesla-3y"]["nominal_v"] = "not-disclosed"
    links.packs.pop("tesla-lfp-60")
    links.by_variant["tesla-model-3-gen1-x"] = {
        "variant_id": "tesla-model-3-gen1-x",
        "voltage": {"class_id": "800v", "class_override_note": "small pack"},
    }
    inh = inherited_for(links, "tesla-model-3-gen1-x", "tesla-model-3-gen1", {})
    assert "voltage_nominal_v" not in inh["numbers"]
    assert "voltage_nominal_v" not in inh["labels"]
    assert inh["labels"]["voltage_class_id"] == "800v"
    row = {"voltage_nominal_v": 400.0, **inh["labels"]}
    finish_voltage(links, row, "tesla-3y")
    assert row["voltage_class_id"] == "800v"  # explicit override beats 400 V derivation
