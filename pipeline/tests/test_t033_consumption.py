"""T-032 (EPA consumption tests) + T-033 (consumption matrix with fallback ladder)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from ev_pipeline.derive import consumption as cm
from ev_pipeline.sources import _common as c
from ev_pipeline.sources.fueleconomy import adapter as fe

FIX = Path(__file__).parent / "fixtures"
PARAMS = cm.load_params()


# --- T-032: EPA tests --------------------------------------------------------------------


def test_epa_tests_are_condition_tagged() -> None:
    tests = fe.consumption_tests(FIX / "fueleconomy", c.retrieved_at_for(FIX / "fueleconomy"))
    assert tests and len({t["id"] for t in tests}) == len(tests)
    t = next(x for x in tests if x["id"].endswith(":cityE"))
    assert t["road_band"] == "town" and t["speed_kmh"] == 31.5 and t["test_kind"] == "cycle"
    assert t["temperature_c"] == 23.9 and t["energy_basis"] == "wall"
    assert t["tyre_season"] == "not-disclosed" and "5-cycle adjusted" in t["conditions"]["notes"]
    assert t["source"]["id"] == "fueleconomy" and t["retrieved_at"] and t["confidence"]
    hw = next(x for x in tests if x["id"].endswith(":highwayE"))
    assert hw["road_band"] == "rural" and hw["speed_kmh"] == 77.7
    # Tesla Model S 85 2014: cityE 38 kWh/100 mi -> 236.1 Wh/km
    s85 = [x for x in tests if x["id"].endswith(":cityE") and x["consumption_wh_km"] == 236.1]
    assert s85


def test_epa_tests_match_the_schema_minus_variant_id() -> None:
    from jsonschema import Draft202012Validator

    from ev_pipeline.release.validate import _schema

    schema = dict(_schema())
    schema["$ref"] = "#/$defs/ConsumptionTest"
    v = Draft202012Validator(schema)
    for t in fe.consumption_tests(FIX / "fueleconomy", c.retrieved_at_for(FIX / "fueleconomy")):
        row = {k: x for k, x in t.items() if k != "source_record"} | {"variant_id": "x-y"}
        assert list(v.iter_errors(row)) == [], t["id"]


def test_normalise_writes_the_tests_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EV_DATA_DIR", str(tmp_path))
    assert fe.normalise_cmd(from_fixtures=True) == 0
    lines = (tmp_path / "staging" / "fueleconomy.consumption_tests.jsonl").read_text().splitlines()
    assert lines and all(json.loads(x)["source_record"] for x in lines)


# --- T-033: model ------------------------------------------------------------------------


def _row(**kw: Any) -> dict[str, Any]:
    base = {
        "variant_id": "make-model-gen-v",
        "body": "hatchback",
        "consumption_kwh_100km": 16.0,
        "battery_kwh_net": 58.0,
        "weight_kg": 1800,
        "provenance": {"consumption_kwh_100km": {"source_ids": ["eea"], "confidence": "high"}},
    }
    return base | kw


def _test(band: str, wh: float, i: int = 1) -> dict[str, Any]:
    return {
        "id": f"fueleconomy:r{i}:{band}",
        "road_band": band,
        "consumption_wh_km": wh,
        "energy_basis": "wall",
        "source": {"id": "fueleconomy"},
    }


def _cells(m: dict[str, Any], heater: str | None = None) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (x["road_band"], x["temperature_band_id"]): x
        for x in m["cells"]
        if heater is None or x.get("heater_type_id") == heater
    }


def test_wltp_ratio_rung_and_shape() -> None:
    m = cm.variant_model(_row(), [], PARAMS, 3, "t")
    assert m is not None and len(m["cells"]) == 15
    cells = _cells(m)
    assert {x["rung"] for x in m["cells"]} == {"wltp-ratio"}
    assert {x["confidence"] for x in m["cells"]} == {"low"}
    # 20 °C: town < rural < motorway; cold costs more, and more in town than on the motorway
    assert cells[("town", "t5")]["wh_km"] < cells[("rural", "t5")]["wh_km"]
    assert cells[("rural", "t5")]["wh_km"] < cells[("motorway", "t5")]["wh_km"]
    town = cells[("town", "t1")]["wh_km"] / cells[("town", "t5")]["wh_km"]
    mway = cells[("motorway", "t1")]["wh_km"] / cells[("motorway", "t5")]["wh_km"]
    assert town > mway > 1.0
    assert 1.4 < town < 2.0 and 1.1 < mway < 1.4  # within published winter-loss ranges (🟡)
    c5 = cells[("rural", "t5")]
    assert c5["p10_wh_km"] < c5["wh_km"] < c5["p90_wh_km"]


def test_20c_cell_reproduces_the_reference() -> None:
    m = cm.variant_model(_row(), [], PARAMS, 3, "t")
    assert m is not None
    comb = 160 * PARAMS["wall_to_battery"]
    want = comb * PARAMS["wltp_band_ratio"]["default"]["rural"]
    assert _cells(m)[("rural", "t5")]["wh_km"] == pytest.approx(want, abs=0.1)


def test_measured_rungs_from_tests_and_physics_motorway() -> None:
    tests = [_test("town", 150, 1), _test("town", 170, 2), _test("rural", 180, 1)]
    m = cm.variant_model(_row(), tests, PARAMS, 3, "t")
    assert m is not None
    cells = _cells(m)
    assert cells[("town", "t5")]["rung"] == "measured"
    assert cells[("town", "t5")]["confidence"] == "medium"
    assert cells[("town", "t5")]["test_ids"] == ["fueleconomy:r1:town", "fueleconomy:r2:town"]
    assert cells[("motorway", "t3")]["rung"] == "physics"
    town_ref = 160 * PARAMS["wall_to_battery"]  # median of 150/170, wall -> battery
    assert cells[("town", "t5")]["wh_km"] == pytest.approx(town_ref, abs=0.1)


def test_town_test_only_falls_back_per_band() -> None:
    m = cm.variant_model(_row(), [_test("town", 150)], PARAMS, 3, "t")
    assert m is not None
    cells = _cells(m)
    assert cells[("town", "t1")]["rung"] == "measured"
    assert cells[("rural", "t1")]["rung"] == "wltp-ratio"
    assert cells[("motorway", "t1")]["rung"] == "wltp-ratio"


def test_no_wltp_and_no_tests_means_no_model() -> None:
    assert cm.variant_model(_row(consumption_kwh_100km=None), [], PARAMS, 3, "t") is None
    est = _row(provenance={"consumption_kwh_100km": {"source_ids": ["model-estimate"]}})
    assert cm.variant_model(est, [], PARAMS, 3, "t") is None  # never model from an estimate
    full = [_test("town", 150), _test("rural", 180)]
    assert cm.variant_model(_row(consumption_kwh_100km=None), full, PARAMS, 3, "t") is not None


@pytest.mark.parametrize(
    ("fitment", "heaters"),
    [("standard", {None}), ("none", {None}), ("not-disclosed", {None}),
     ("option", {"heat-pump", "resistive"})],
)  # fmt: skip
def test_heat_pump_fitment_sets(fitment: str, heaters: set[str | None]) -> None:
    m = cm.variant_model(_row(heat_pump=fitment), [], PARAMS, 3, "t")
    assert m is not None
    assert {x.get("heater_type_id") for x in m["cells"]} == heaters
    assert len(m["cells"]) == 15 * len(heaters)


def test_heat_pump_beats_resistive_in_the_cold_only() -> None:
    m = cm.variant_model(_row(heat_pump="option"), [], PARAMS, 3, "t")
    assert m is not None
    hp, rs = _cells(m, "heat-pump"), _cells(m, "resistive")
    assert hp[("town", "t1")]["wh_km"] < rs[("town", "t1")]["wh_km"]
    assert hp[("town", "t5")]["wh_km"] == rs[("town", "t5")]["wh_km"]


def test_suv_motorway_ratio_is_higher() -> None:
    a = cm.variant_model(_row(), [], PARAMS, 3, "t")
    b = cm.variant_model(_row(body="suv"), [], PARAMS, 3, "t")
    assert a is not None and b is not None
    assert _cells(b)[("motorway", "t5")]["wh_km"] > _cells(a)[("motorway", "t5")]["wh_km"]


def test_models_validate_against_the_schema() -> None:
    from jsonschema import Draft202012Validator

    from ev_pipeline.release.validate import _schema

    schema = dict(_schema())
    schema["$ref"] = "#/$defs/ConsumptionModel"
    v = Draft202012Validator(schema)
    for row in (_row(), _row(heat_pump="option")):
        m = cm.variant_model(row, [_test("town", 150), _test("rural", 170)], PARAMS, 3, "t")
        assert list(v.iter_errors(m)) == []


def test_tests_attach_through_matched_facts_and_respect_the_gate() -> None:
    facts = [
        {"subject_type": "variant", "subject_id": "v1", "source": {"id": "fueleconomy"},
         "source_record": "rec-1"},
        {"subject_type": "variant", "subject_id": "v2", "source": {"id": "eea"},
         "source_record": "rec-2"},
    ]  # fmt: skip
    tests = {
        "rec-1": [{**_test("town", 150), "source_record": "rec-1"}],
        "rec-2": [{**_test("town", 150), "source_record": "rec-2"}],  # other source's record
        "rec-3": [{**_test("town", 150), "source_record": "rec-3"}],  # never matched
    }
    got = cm.tests_by_variant(facts, tests, lambda s: True)
    assert set(got) == {"v1"} and got["v1"][0]["variant_id"] == "v1"
    assert cm.tests_by_variant(facts, tests, lambda s: False) == {}


def test_taxonomy_rows_override_default_bands(tmp_path: Path) -> None:
    tb = [{"id": "x1", "label": {"en": "cold"}, "representative_c": -20, "order": 1}]
    (tmp_path / "temperature_bands.yaml").write_text(json.dumps({"temperature_bands": tb}))
    p = cm.load_params(taxonomy_dir=tmp_path)
    assert [t["id"] for t in p["temperature_bands"]] == ["x1"]
    m = cm.variant_model(_row(), [], p, 3, "t")
    assert m is not None and len(m["cells"]) == 3


def test_params_are_all_flagged_estimates() -> None:
    text = cm.PARAMS_FILE.read_text(encoding="utf-8")
    assert "EVERY value here is an estimate" in text
    assert {h["confidence"] for h in PARAMS["heater_types"]} == {"low"}
    assert all(h["warm_up_kwh"] > 0 for h in PARAMS["heater_types"])


def test_release_ships_the_matrix(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from datetime import UTC, datetime

    from ev_pipeline.release.build import release_cmd

    fix = FIX / "release"
    d = tmp_path / "data"
    (d / "seed").mkdir(parents=True)
    shutil.copytree(fix / "staging", d / "staging")
    shutil.copytree(fix / "taxonomy", d / "taxonomy")
    for n in ("models", "variants", "platforms", "battery_packs", "variant_links"):
        shutil.copy(fix / f"{n}.yaml", d / "seed" / f"{n}.yaml")
    for n in ("sources", "field_sources"):
        shutil.copy(fix / f"{n}.yaml", d / f"{n}.yaml")
    monkeypatch.setenv("EV_DATA_DIR", str(d))
    monkeypatch.delenv("EV_RUNS_DIR", raising=False)
    assert release_cmd(False, data_dir=d, now=datetime(2026, 11, 15, 1, tzinfo=UTC)) == 0
    doc = json.loads((d / "releases" / "1" / "consumption_matrix.json").read_text())
    assert doc["estimate"] is True and doc["variants"]
    assert [t["id"] for t in doc["temperature_bands"]] == ["t1", "t2", "t3", "t4", "t5"]
    assert all(len(v["cells"]) >= 15 for v in doc["variants"])
    cov = (d / "releases" / "1" / "coverage.md").read_text()
    assert "Consumption matrix" in cov and "KB gzip" in cov
