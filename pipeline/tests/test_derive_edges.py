"""Derive edge cases (overnight coverage pass): missing inputs, not-disclosed values, bad
curves, year bands, rung selection and link-file shapes.

All inputs are small SYNTHETIC fixtures built in this file (plus the shared test seed in
fixtures/release/models.yaml). No network.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from ev_pipeline.derive import metrics as m
from ev_pipeline.derive.links import Links, _items, inherited_for, load_links, pack_facts
from ev_pipeline.derive.rows import build_rows
from ev_pipeline.match.matcher import CLAIM_SOURCES, MatchedFact, VariantInfo, priority_of
from ev_pipeline.match.seed import load_seed
from ev_pipeline.merge.merge import merge_variant_facts
from ev_pipeline.release.validate import provenance_errors
from ev_pipeline.schema_models import ChargeCurve, Fact

FIX = Path(__file__).parent / "fixtures" / "release"
TODAY = date(2026, 11, 15)
VID = "tesla-model-3-gen1-lr"
GEN = "tesla-model-3-gen1"


def _fact(
    field: str,
    value: object,
    unit: str,
    source: str = "openev",
    country: str | None = None,
) -> MatchedFact:
    """SYNTHETIC fact on the test seed's Model 3 gen1 Long Range."""
    f = Fact(
        id=f"{source}:k:{field}",
        subject_type="variant",
        subject_id=VID,
        field=field,
        value=value,
        unit=unit,
        country=country,
        source={"id": source, "name": source, "licence": "CC-BY-4.0"},
        retrieved_at=date(2026, 11, 14),
        confidence="medium",
        claim=True if source in CLAIM_SOURCES else None,
    )
    return MatchedFact(f, source, priority_of(source), 2022, GEN, "tesla-model-3")


def _curve_fact(value: object, source: str = "kilowatt-openev") -> MatchedFact:
    """A dc_curve fact; `value` is set without validation so tests can feed broken shapes."""
    c = _fact("dc_curve", 0, "kW", source=source)
    c.fact = c.fact.model_copy(update={"value": value})
    return c


def _rows(facts, vid=VID, gen=GEN, **info_kw):
    seed = load_seed(FIX / "models.yaml")
    info = VariantInfo(vid, gen, "Long Range", **info_kw)
    return build_rows({info.id: info}, {info.id: merge_variant_facts(facts)}, seed, {}, TODAY, 1)


def _row(facts, **info_kw):
    info_kw.setdefault("years", {2022})
    rows, problems = _rows(facts, **info_kw)
    return rows[0], problems


# --- missing and not-a-number inputs ------------------------------------------------------


def test_variant_without_merged_facts_gets_no_row() -> None:
    seed = load_seed(FIX / "models.yaml")
    info = VariantInfo(VID, GEN, "Long Range", years={2022})
    rows, problems = build_rows({info.id: info}, {}, seed, {}, TODAY, 1)
    assert rows == [] and problems == []


def test_not_disclosed_number_is_dropped_not_published() -> None:
    row, problems = _row(
        [_fact("battery_kwh_net", "not-disclosed", "kWh"), _fact("wltp_range_km", 500, "km")]
    )
    assert row["battery_kwh_net"] is None
    assert "battery_kwh_net" not in row["provenance"]
    assert [(p.field, p.reason) for p in problems] == [("battery_kwh_net", "not a number")]
    # Nothing is derived from a missing battery: no consumption estimate.
    assert row["consumption_kwh_100km"] is None
    assert provenance_errors([row]) == []


def test_boolean_value_is_not_a_number() -> None:
    row, problems = _row([_fact("ac_kw", True, "kW")])
    assert row["ac_kw"] is None
    assert [p.field for p in problems] == ["ac_kw"]


def test_price_that_is_not_a_number_is_dropped() -> None:
    row, problems = _row(
        [
            _fact("battery_kwh_net", 60, "kWh"),
            _fact("price_new", "on request", "EUR", country="NL"),
            _fact("price_new", 45000, "EUR", country="DE"),
        ]
    )
    assert row["price_new"] == {"DE": {"amount": 45000.0, "currency": "EUR"}}
    assert "price_new.NL" not in row["provenance"]
    assert [(p.field, p.reason) for p in problems] == [("price_new.NL", "not a number")]


def test_gross_too_big_gives_no_net_estimate() -> None:
    # 200 kWh gross x 0.93 = 186 kWh net, above the 150 kWh range limit: dropped.
    row, problems = _row([_fact("battery_kwh_gross", 200, "kWh")])
    assert row["battery_kwh_net"] is None
    assert [p.field for p in problems] == ["battery_kwh_net"]


def test_no_battery_no_range_leaves_derived_fields_empty() -> None:
    row, problems = _row([_fact("ac_kw", 11, "kW")])
    assert problems == []
    for f in (
        "consumption_kwh_100km",
        "ac_km_per_h",
        "real_range_km",
        "dc_avg_10_80_kw",
        "dc_km_per_10min",
    ):
        assert row[f] is None, f
    assert row["real_range_rung"] is None
    assert "dc_curve_status" not in row and "dc_peak_kw_is_claim" not in row


def test_string_id_fields_are_copied_with_provenance() -> None:
    row, _ = _row([_fact("battery_kwh_net", 60, "kWh"), _fact("chemistry_id", "lfp", "id")])
    assert row["chemistry_id"] == "lfp"
    assert row["provenance"]["chemistry_id"]["source_ids"] == ["openev"]


# --- charging ----------------------------------------------------------------------------


def test_claim_fact_fills_peak_when_no_plain_peak() -> None:
    row, _ = _row([_fact("battery_kwh_net", 60, "kWh"), _fact("dc_peak_kw_claim", 170, "kW")])
    assert row["dc_peak_kw"] == 170.0
    assert row["dc_peak_kw_is_claim"] is True
    assert row["dc_curve_status"] == "default"  # default curve built on the claimed peak


def test_out_of_range_claim_is_ignored() -> None:
    row, _ = _row([_fact("dc_peak_kw_claim", 999, "kW")])
    assert row["dc_peak_kw"] is None and "dc_peak_kw_is_claim" not in row


def test_unusable_curve_is_reported_and_default_curve_used() -> None:
    curve = ChargeCurve.model_validate({"points": [[10, 0], [80, 0]], "status": "measured"})
    row, problems = _row(
        [
            _fact("battery_kwh_net", 60, "kWh"),
            _fact("dc_peak_kw", 100, "kW", source="eea"),
            _curve_fact(curve),
        ]
    )
    assert ("dc_curve", "unusable charge curve (zero or negative kW)") in [
        (p.field, p.reason) for p in problems
    ]
    assert row["dc_curve_status"] == "default"
    assert row["dc_avg_10_80_kw"] == pytest.approx(67.4, abs=0.2)


@pytest.mark.parametrize(
    "broken",
    [
        "not a curve",  # not a dict at all
        {"status": "measured"},  # no points
        {"points": [[10]], "status": "measured"},  # point without kW
        {"points": [["x", "y"]], "status": "measured"},  # not numbers
    ],
)
def test_malformed_curve_value_is_ignored(broken: object) -> None:
    row, _ = _row(
        [
            _fact("battery_kwh_net", 60, "kWh"),
            _fact("dc_avg_10_80_kw", 80, "kW"),
            _curve_fact(broken),
        ]
    )
    # The sourced average stays; no curve status because no usable curve.
    assert row["dc_avg_10_80_kw"] == 80.0
    assert "dc_curve_status" not in row


def test_curve_with_out_of_range_average_is_dropped() -> None:
    # A flat 5 kW curve averages 5 kW, below the 10 kW floor for dc_avg_10_80_kw.
    curve = ChargeCurve.model_validate({"points": [[0, 5], [100, 5]], "status": "estimated"})
    row, problems = _row([_fact("battery_kwh_net", 60, "kWh"), _curve_fact(curve)])
    assert row["dc_avg_10_80_kw"] is None
    assert "dc_avg_10_80_kw" in [p.field for p in problems]
    assert row["dc_curve_status"] == "estimated"


def test_estimated_curve_note_names_its_source() -> None:
    curve = ChargeCurve.model_validate({"points": [[10, 100], [80, 100]], "status": "estimated"})
    row, problems = _row(
        [
            _fact("battery_kwh_net", 70, "kWh"),
            _fact("wltp_range_km", 500, "km"),
            _curve_fact(curve),
        ]
    )
    assert problems == []
    assert row["dc_curve_status"] == "estimated"
    assert row["dc_avg_10_80_kw"] == 100.0
    pv = row["provenance"]
    assert pv["dc_avg_10_80_kw"]["estimate"] is True  # estimated curves are not measured
    assert "estimated charge curve (kilowatt-openev)" in pv["dc_km_per_10min"]["note"]
    assert provenance_errors([row]) == []


def test_sourced_average_without_battery_gives_no_minutes() -> None:
    row, _ = _row([_fact("dc_avg_10_80_kw", 80, "kW")])
    assert row["dc_avg_10_80_kw"] == 80.0
    assert row["dc_minutes_10_80"] is None


def test_default_curve_without_battery_has_no_minutes_but_uncapped_km() -> None:
    row, _ = _row(
        [
            _fact("dc_peak_kw", 100, "kW", source="eea"),
            _fact("consumption_kwh_100km", 16, "kWh/100km"),
        ]
    )
    assert row["dc_curve_status"] == "default"
    assert row["dc_minutes_10_80"] is None and row["dc_peak_held_min"] is None
    assert "uncapped" in row["provenance"]["dc_km_per_10min"]["note"]


# --- real range --------------------------------------------------------------------------


def test_real_range_fact_is_the_exact_test_rung() -> None:
    row, _ = _row(
        [
            _fact("battery_kwh_net", 75, "kWh"),
            _fact("wltp_range_km", 600, "km"),
            _fact("real_range_km", 455, "km", source="eea"),
        ]
    )
    assert row["real_range_km"] == 455.0 and row["real_range_rung"] == "exact-test"
    p = row["provenance"]["real_range_km"]
    assert "derived" not in p and "estimate" not in p


def test_real_range_fact_that_is_not_a_number_is_not_an_observation() -> None:
    row, _ = _row(
        [
            _fact("battery_kwh_net", 75, "kWh"),
            _fact("wltp_range_km", 600, "km"),
            _fact("real_range_km", "n/a", "km", source="eea"),
        ]
    )
    assert row["real_range_rung"] == "body-ratio"


# --- year bands --------------------------------------------------------------------------


def test_explicit_end_beats_observed_years() -> None:
    row, _ = _row([_fact("battery_kwh_net", 60, "kWh")], years={2020, 2021}, explicit_end=2023)
    assert (row["year_start"], row["year_end"]) == (2020, 2023)
    assert row["era"] == "2018-20"


def test_open_end_on_open_generation_is_on_sale() -> None:
    rows, _ = _rows(
        [_fact("battery_kwh_net", 60, "kWh")],
        vid="tesla-model-3-highland-lr",
        gen="tesla-model-3-highland",
        years={2024},
        open_end=True,
    )
    assert rows[0]["year_end"] is None and rows[0]["on_sale_new"] is True


def test_no_years_falls_back_to_generation_span() -> None:
    row, _ = _row([_fact("battery_kwh_net", 60, "kWh")], years=set())
    assert (row["year_start"], row["year_end"]) == (2019, 2023)
    assert row["on_sale_new"] is False


def test_open_end_on_closed_generation_is_not_on_sale() -> None:
    # Seed says the generation ended (2023): never "on sale new", even with an open span.
    row, _ = _row([_fact("battery_kwh_net", 60, "kWh")], years={2022}, open_end=True)
    assert row["year_end"] is None and row["on_sale_new"] is False


@pytest.mark.parametrize(("year", "era"), [(2017, "pre-2018"), (2018, "2018-20")])
def test_era_band_edges_in_rows(year: int, era: str) -> None:
    row, _ = _row([_fact("battery_kwh_net", 60, "kWh")], years={year})
    assert row["era"] == era


# --- rung selection ----------------------------------------------------------------------


def _li(vid, gen="g1", battery=60.0, wltp=400.0, body="suv", drivetrain="fwd", make="acme"):
    return m.LadderInput(vid, gen, make, body, drivetrain, battery, wltp, ["src"], [f"f:{vid}"])


def _obs(km, rung="exact-test", src="test"):
    return m.RealObservation(km, rung, [src], [f"{src}:real"], "medium")


def test_sibling_tie_on_battery_prefers_owner_data() -> None:
    a, b, c = _li("a", battery=60), _li("b", battery=70), _li("c", battery=50)
    r = m.real_range(a, [a, b, c], {"b": _obs(350, "exact-test"), "c": _obs(300, "owner-data")})
    assert r.rung == "sibling-variant"
    assert "from c" in r.note  # both 10 kWh away; owner data ranks first
    assert r.km == pytest.approx(300 * 60 / 50)


def test_sibling_tie_on_battery_and_rung_is_alphabetical() -> None:
    a, b, c = _li("a", battery=60), _li("z", battery=70), _li("m", battery=50)
    r = m.real_range(a, [a, b, c], {"z": _obs(350), "m": _obs(300)})
    assert "from m" in r.note


def test_sibling_without_battery_is_skipped() -> None:
    a, b = _li("a", battery=60), _li("b", battery=None)
    r = m.real_range(a, [a, b], {"b": _obs(350)})
    assert r.rung == "brand-body-drivetrain-ratio"  # b still feeds the brand ratio


def test_no_battery_skips_the_sibling_rung() -> None:
    a, b = _li("a", battery=None), _li("b", battery=60)
    r = m.real_range(a, [a, b], {"b": _obs(320)})
    assert r.rung == "brand-body-drivetrain-ratio"
    assert r.km == pytest.approx(400 * 320 / 400)


def test_no_wltp_and_no_sibling_gives_nothing() -> None:
    a = _li("a", wltp=None)
    assert m.real_range(a, [a], {}) is None


def test_unknown_body_gives_nothing() -> None:
    a = _li("a", body="spaceship")
    assert m.real_range(a, [a], {}) is None
    b = _li("b", body=None)
    assert m.real_range(b, [b], {}) is None


def test_ratio_ignores_observations_without_wltp() -> None:
    a, b = _li("a", gen="g1"), _li("b", gen="g2", wltp=None)
    ratios = m.brand_body_drivetrain_ratios([a, b], {"b": _obs(300)})
    assert ratios == {}


def test_curve_before_first_and_after_last_point_holds_end_values() -> None:
    # Points only from 20 to 50 %: below 20 % it holds 100 kW, above 50 % it holds 50 kW.
    s = m.integrate_curve([(20, 100), (50, 50)], 70)
    t = m.integrate_curve([(10, 100), (20, 100), (50, 50), (80, 50)], 70)
    assert s.avg_kw == pytest.approx(t.avg_kw)
    assert s.minutes == pytest.approx(t.minutes)


# --- link files --------------------------------------------------------------------------


def test_items_shapes() -> None:
    assert _items(None, "x") == []
    assert _items([{"id": "a"}], "x") == [{"id": "a"}]
    assert _items({"packs": [{"id": "p"}]}, "battery_packs") == [{"id": "p"}]
    assert _items({"something": "else"}, "x") == []


def test_voltage_class_edges() -> None:
    links = Links(
        taxonomy={"voltage_classes": [{"id": "400v", "min_v": 200, "max_v": 550}]},
    )
    assert links.voltage_class(None) is None
    assert links.voltage_class(200) == "400v"  # lower bound is inclusive
    assert links.voltage_class(550) is None  # upper bound is exclusive
    assert links.voltage_class(100) is None


def test_load_links_with_empty_and_missing_files(tmp_path: Path) -> None:
    (tmp_path / "seed").mkdir()
    (tmp_path / "seed" / "platforms.yaml").write_text("", encoding="utf-8")  # empty file
    links = load_links(tmp_path)
    assert links.taxonomy is None
    assert links.platforms == {} and links.packs == {} and links.by_variant == {}
    assert links.retrieved_at is None
    assert pack_facts(links) == []  # no dated input, no facts


def test_pack_facts_skip_not_disclosed_numbers_and_warranty(tmp_path: Path) -> None:
    (tmp_path / "seed").mkdir()
    (tmp_path / "seed" / "battery_packs.yaml").write_text(
        "# SYNTHETIC test pack\n"
        "battery_packs:\n"
        "  - id: test-pack\n"
        "    usable_kwh: not-disclosed\n"
        "    gross_kwh: 64\n"
        "    chemistry_id: not-disclosed\n"
        "    warranty: {years: not-disclosed, km: 160000}\n",
        encoding="utf-8",
    )
    facts = {f["field"]: f["value"] for f in pack_facts(load_links(tmp_path))}
    assert facts == {
        "battery_kwh_gross": 64,
        "chemistry_id": "not-disclosed",  # ids keep the not-disclosed marker
        "warranty_km": 160000,
    }


def test_seed_file_source_block_names_the_pack_facts(tmp_path: Path) -> None:
    (tmp_path / "seed").mkdir()
    (tmp_path / "seed" / "battery_packs.yaml").write_text(
        "# SYNTHETIC test pack with its own source block\n"
        "source: {id: test-seed, name: Test seed, licence: CC0-1.0, extra: ignored}\n"
        "battery_packs:\n"
        "  - {id: p1, usable_kwh: 50}\n",
        encoding="utf-8",
    )
    links = load_links(tmp_path)
    assert links.source == {"id": "test-seed", "name": "Test seed", "licence": "CC0-1.0"}
    (fact,) = pack_facts(links)
    assert fact["id"] == "test-seed:battery_pack/p1:battery_kwh_net"
    assert fact["source"]["licence"] == "CC0-1.0"


def test_link_voltage_labels_and_charger_kw() -> None:
    links = Links()
    links.by_variant["v"] = {
        "variant_id": "v",
        "voltage": {"marketing_label": "800 V", "switchable": 1, "nominal_v": "not-disclosed"},
        "charger_400v": {"mode": "booster", "kw": 50},
    }
    inh = inherited_for(links, "v", "g", {})
    assert inh["labels"]["voltage_label"] == "800 V"
    assert inh["labels"]["voltage_switchable"] is True
    assert inh["labels"]["charger_400v_mode"] == "booster"
    assert inh["numbers"]["charger_400v_kw"][0] == 50.0
    assert "voltage_nominal_v" not in inh["numbers"] and "voltage_nominal_v" not in inh["labels"]


# --- DC average never above the DC peak (A-06 QA flag: e-Golf 24 kWh, avg 41.8 > peak 40) --


def test_estimated_curve_above_the_peak_is_capped_at_the_peak() -> None:
    # SYNTHETIC: the e-Golf shape: an estimated curve peaking at 44 kW, a 40 kW peak from
    # another source (KilowattApp's own 44 kW peak was taken out by a guard).
    curve = ChargeCurve.model_validate(
        {"points": [[0, 40], [76, 44], [81, 25], [93, 16], [100, 8]], "status": "estimated"}
    )
    row, problems = _row(
        [
            _fact("battery_kwh_net", 21.2, "kWh"),
            _fact("dc_peak_kw", 40, "kW", source="seed-manual"),
            _curve_fact(curve),
        ]
    )
    assert problems == []
    assert row["dc_peak_kw"] == 40.0
    assert row["dc_avg_10_80_kw"] is not None and row["dc_avg_10_80_kw"] <= 40.0
    assert (
        "capped at dc_peak_kw 40 kW (curve peak 44 kW)"
        in (row["provenance"]["dc_avg_10_80_kw"]["note"])
    )
    assert provenance_errors([row]) == []


def test_curve_at_or_below_the_peak_is_not_capped() -> None:
    curve = ChargeCurve.model_validate({"points": [[10, 100], [80, 100]], "status": "estimated"})
    row, _ = _row(
        [
            _fact("battery_kwh_net", 70, "kWh"),
            _fact("dc_peak_kw", 100, "kW", source="eea"),
            _curve_fact(curve),
        ]
    )
    assert row["dc_avg_10_80_kw"] == 100.0
    assert "capped" not in row["provenance"]["dc_avg_10_80_kw"]["note"]


def test_measured_curve_average_above_the_peak_goes_to_review() -> None:
    # A measured curve is not reshaped; an average above the published peak is withheld.
    curve = ChargeCurve.model_validate({"points": [[10, 60], [80, 60]], "status": "measured"})
    row, problems = _row(
        [
            _fact("battery_kwh_net", 50, "kWh"),
            _fact("dc_peak_kw", 50, "kW", source="eea"),
            _curve_fact(curve),
        ]
    )
    assert row["dc_avg_10_80_kw"] is None
    assert row["dc_peak_kw"] == 50.0
    [p] = [p for p in problems if p.field == "dc_avg_10_80_kw"]
    assert "DC average above the published DC peak" in p.reason


def test_sourced_average_above_the_peak_goes_to_review() -> None:
    row, problems = _row(
        [
            _fact("battery_kwh_net", 60, "kWh"),
            _fact("dc_peak_kw", 50, "kW", source="eea"),
            _fact("dc_avg_10_80_kw", 80, "kW"),
        ]
    )
    assert row["dc_avg_10_80_kw"] is None and row["dc_minutes_10_80"] is None
    assert "dc_avg_10_80_kw" in [p.field for p in problems]
    assert provenance_errors([row]) == []


# --- a value a citation withheld is not re-estimated (A-06 follow-up) -----------------------


def _rows_cited(facts, citations):
    seed = load_seed(FIX / "models.yaml")
    info = VariantInfo(VID, GEN, "Long Range", years={2022})
    merged = {info.id: merge_variant_facts(facts)}
    return build_rows({info.id: info}, merged, seed, {}, TODAY, 1, citations=citations)


def test_net_estimate_from_gross_that_a_citation_contradicts_is_dropped() -> None:
    # SYNTHETIC: usable was withheld (a citation says 66.5); gross 66.5 x 0.93 = 61.8.
    rows, problems = _rows_cited(
        [_fact("battery_kwh_gross", 66.5, "kWh")], {VID: {"battery_kwh_net": [66.5]}}
    )
    assert rows[0]["battery_kwh_net"] is None
    [p] = [p for p in problems if p.field == "battery_kwh_net"]
    assert "contradicted by a citation" in p.reason


def test_net_estimate_that_a_citation_agrees_with_is_kept() -> None:
    rows, problems = _rows_cited(
        [_fact("battery_kwh_gross", 82, "kWh")],
        {VID: {"battery_kwh_net": [round(82 * m.NET_PER_GROSS, 1)]}},
    )
    assert rows[0]["battery_kwh_net"] is not None
    assert "battery_kwh_net" not in [p.field for p in problems]
