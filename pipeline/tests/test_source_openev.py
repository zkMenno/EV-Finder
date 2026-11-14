"""OpenEV adapter on the recorded fixture subset. No network."""

from datetime import date
from pathlib import Path

import pytest

from ev_pipeline.records import SourceRecord
from ev_pipeline.schema_models import Confidence, Country, FactField
from ev_pipeline.sources.openev import adapter

FIXTURE = Path(__file__).parent / "fixtures" / "openev"
UNITS = {
    FactField.battery_kwh_net: "kWh",
    FactField.battery_kwh_gross: "kWh",
    FactField.wltp_range_km: "km",
    FactField.epa_range_km: "km",
    FactField.ac_kw: "kW",
    FactField.dc_peak_kw: "kW",
    FactField.dc_avg_10_80_kw: "kW",
    FactField.dc_minutes_10_80: "min",
    FactField.power_kw: "kW",
    FactField.accel_0_100_s: "s",
    FactField.top_speed_kmh: "km/h",
    FactField.boot_l: "l",
    FactField.frunk_l: "l",
    FactField.length_mm: "mm",
    FactField.width_mm: "mm",
    FactField.height_mm: "mm",
    FactField.wheelbase_mm: "mm",
    FactField.weight_kg: "kg",
    FactField.towing_kg: "kg",
    FactField.seats: "count",
    FactField.voltage_nominal_v: "V",
    FactField.voltage_max_v: "V",
    FactField.warranty_years: "years",
    FactField.warranty_km: "km",
    FactField.chemistry_id: "id",
    FactField.cooling_id: "id",
}


@pytest.fixture(scope="module")
def records() -> list[SourceRecord]:
    return adapter.normalise(FIXTURE, date(2026, 11, 15))


def by_key(records: list[SourceRecord], suffix: str) -> SourceRecord:
    [rec] = [r for r in records if r.record_key.endswith(suffix)]
    return rec


def test_licence_file_is_shipped_with_fixture() -> None:
    assert "Community Data License Agreement - Permissive" in (FIXTURE / "LICENCE").read_text()


def test_every_record_has_source_licence_and_units(records: list[SourceRecord]) -> None:
    assert len(records) > 30
    for rec in records:
        assert rec.source.id.root == "openev"
        assert rec.source.licence == "CDLA-Permissive-2.0"
        assert rec.retrieved_at == date(2026, 11, 15)
        assert rec.specs
        for field, spec in rec.specs.items():
            expected = rec.country and field == FactField.price_new
            assert spec.unit == ("EUR" if expected else UNITS[field]), (rec.record_key, field)


def test_variant_deep_merges_base_and_year_file(records: list[SourceRecord]) -> None:
    leaf62 = by_key(records, "src/nissan/leaf/2024/leaf_62_kwh.json")
    assert leaf62.record_key == (
        "src/nissan/leaf/base.json+src/nissan/leaf/2024/leaf.json"
        "+src/nissan/leaf/2024/leaf_62_kwh.json"
    )
    assert (leaf62.make, leaf62.model, leaf62.variant_name) == ("Nissan", "LEAF", "62 kWh")
    assert leaf62.specs[FactField.battery_kwh_net].value == 62  # from the variant
    assert leaf62.specs[FactField.wltp_range_km].value == 385  # array replaced by the variant
    assert leaf62.specs[FactField.length_mm].value == 4490  # from base.json
    assert leaf62.specs[FactField.ac_kw].value == 6.6  # from the year file
    assert leaf62.body == "hatchback"
    assert leaf62.drivetrain == "fwd"
    assert leaf62.confidence == Confidence.medium  # OEM + regulatory sources


def test_eur_price_becomes_country_record(records: list[SourceRecord]) -> None:
    price = by_key(records, "src/tesla/model_3/2025/model_3.json#price_new:DE")
    assert price.country == Country.DE
    assert price.specs == {FactField.price_new: price.specs[FactField.price_new]}
    assert (price.specs[FactField.price_new].value, price.specs[FactField.price_new].unit) == (
        42990,
        "EUR",
    )
    # USD prices are dropped.
    assert not any(r.record_key.endswith("#price_new:US") for r in records)


def test_dc_average_from_10_80_time(records: list[SourceRecord]) -> None:
    p7 = by_key(records, "src/xpeng/p7_plus/2025/p7_plus.json")
    # 60.7 kWh net x 0.7 / (16 min / 60)
    assert p7.specs[FactField.dc_minutes_10_80].value == 16
    assert p7.specs[FactField.dc_avg_10_80_kw].value == pytest.approx(159.3)


def test_dc_average_from_curve() -> None:
    rec = {
        "battery": {"pack_capacity_kwh_net": 70},
        "charging": {
            "dc_charge_curve": {
                "curve_type": "power_by_soc",
                "points": [
                    {"soc_percent": 0, "power_kw": 100},
                    {"soc_percent": 100, "power_kw": 100},
                ],
            }
        },
    }
    assert adapter.dc_avg_10_80(rec) == pytest.approx(100)


def test_battery_taxonomy_fields(records: list[SourceRecord]) -> None:
    m3 = by_key(records, "src/tesla/model_3/2025/model_3.json")
    assert m3.specs[FactField.chemistry_id].value == "lfp"
    assert m3.specs[FactField.cooling_id].value == "liquid"
    leaf = by_key(records, "src/nissan/leaf/2024/leaf.json")
    assert leaf.specs[FactField.chemistry_id].value == "nmc"  # cathode beats generic li-ion
    assert leaf.specs[FactField.warranty_years].value == 8
    assert leaf.specs[FactField.warranty_km].value == 160000
    assert adapter.chemistry_id({"chemistry": "li-ion"}) is None


def test_misnamed_variant_merges_onto_year_base(records: list[SourceRecord]) -> None:
    # Upstream file name breaks <vehicle>_<variant> (slug "sportback" vs file "sportback_50").
    rec = by_key(records, "src/audi/q4_e_tron/2024/q4_e_tron_sportback_50.json")
    assert "src/audi/q4_e_tron/2024/q4_e_tron.json" in rec.record_key
    assert rec.specs[FactField.battery_kwh_net].value == 73


def test_deep_merge_rules() -> None:
    low = {"a": {"x": 1, "y": 2}, "arr": [1, 2], "s": "low"}
    high = {"a": {"y": 3}, "arr": [9], "s": "high"}
    assert adapter.deep_merge(low, high) == {"a": {"x": 1, "y": 3}, "arr": [9], "s": "high"}


def test_normalise_cmd_writes_staging_and_runlog(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("EV_DATA_DIR", str(tmp_path))
    assert adapter.normalise_cmd(from_fixtures=True) == 0
    out = (tmp_path / "staging" / "openev.records.jsonl").read_text().splitlines()
    assert len(out) == len(adapter.normalise(FIXTURE, date(2026, 11, 15)))
    SourceRecord.model_validate_json(out[0])
    assert '"source": "openev"' in (tmp_path / "staging" / "runlog.jsonl").read_text()
