"""KilowattApp Open EV Data adapter on the recorded fixture subset. No network."""

from datetime import date
from pathlib import Path

import pytest

from ev_pipeline.records import SourceRecord
from ev_pipeline.schema_models import ChargeCurve, Confidence, FactField
from ev_pipeline.sources.kilowatt_openev import adapter

FIXTURE = Path(__file__).parent / "fixtures" / "kilowatt_openev"
UNITS = {
    FactField.battery_kwh_net: "kWh",
    FactField.ac_kw: "kW",
    FactField.dc_peak_kw: "kW",
    FactField.consumption_kwh_100km: "kWh/100km",
    FactField.dc_curve: "kW",
}
DAY = date(2026, 11, 15)


@pytest.fixture(scope="module")
def result() -> tuple[list[SourceRecord], dict[str, int]]:
    records, stats = adapter.normalise_with_stats(FIXTURE, DAY)
    return records, dict(stats)


@pytest.fixture(scope="module")
def records(result: tuple[list[SourceRecord], dict[str, int]]) -> list[SourceRecord]:
    return result[0]


def by_key(records: list[SourceRecord], suffix: str) -> SourceRecord:
    [rec] = [r for r in records if r.record_key.endswith(suffix)]
    return rec


def keys(records: list[SourceRecord]) -> set[str]:
    return {r.record_key for r in records}


def test_licence_file_is_shipped_with_fixture() -> None:
    text = " ".join((FIXTURE / "LICENSE").read_text().split())
    assert text.startswith("MIT License with Attribution Requirement")
    assert adapter.ATTRIBUTION in text


def test_every_record_has_source_licence_attribution_and_units(
    records: list[SourceRecord],
) -> None:
    assert records
    for rec in records:
        assert rec.source.id.root == "kilowatt-openev"
        assert rec.source.licence == "MIT-with-attribution"
        assert rec.source.attribution == (
            "Open EV Data (https://github.com/KilowattApp/open-ev-data)"
        )
        assert rec.retrieved_at == DAY
        assert rec.kind == "spec"
        assert rec.specs
        for field, spec in rec.specs.items():
            assert spec.unit == UNITS[field], (rec.record_key, field)
        assert FactField.voltage_nominal_v not in rec.specs  # 400/800 is a label, not a voltage


def test_spec_record_fields(records: list[SourceRecord]) -> None:
    id3 = by_key(records, "volkswagen.json#a3568004-5350-923a-9e4e-f85678d0746c")
    assert (id3.make, id3.model, id3.variant_name, id3.year) == ("Volkswagen", "ID.3", "Pro", 2023)
    assert id3.confidence == Confidence.medium
    values = {f: s.value for f, s in id3.specs.items()}
    assert values == {
        FactField.battery_kwh_net: 58.0,
        FactField.ac_kw: 11.0,
        FactField.dc_peak_kw: 120.0,
        FactField.consumption_kwh_100km: 16.6,
    }
    leaf = by_key(records, "nissan.json#f9ab0b23-29cf-4deb-98b1-e3de3dd23716")
    assert leaf.variant_name is None  # empty upstream variant


def test_default_curves_are_dropped(result: tuple[list[SourceRecord], dict[str, int]]) -> None:
    records, stats = result
    # Leaf e+ 62 kWh, ID.3 Pro S, EV6 LR carry is_default_charging_curve: true.
    for vid in ("78b14a0f", "0461072e", "776644a5"):
        assert not any(vid in k and k.endswith("#dc_curve") for k in keys(records))
        assert any(vid in k and not k.endswith("#dc_curve") for k in keys(records))  # specs kept
    assert stats["curves_default_dropped"] == 4  # incl. the DS outlier
    assert stats["curves_kept"] == 5


def test_curve_points_are_valid_and_low_confidence(records: list[SourceRecord]) -> None:
    curves = [r for r in records if FactField.dc_curve in r.specs]
    assert len(curves) == 5
    for rec in curves:
        assert rec.record_key.endswith("#dc_curve")
        assert list(rec.specs) == [FactField.dc_curve]
        assert rec.confidence == Confidence.low
        curve = rec.specs[FactField.dc_curve].value
        assert isinstance(curve, ChargeCurve)
        assert curve.status.value == "estimated"
        points = [p.root for p in curve.points]
        assert len(points) >= 2
        socs = [soc for soc, _ in points]
        assert socs == sorted(socs) and len(set(socs)) == len(socs)
        assert all(0 <= soc <= 100 and kw >= 0 for soc, kw in points)
    ioniq = by_key(records, "hyundai.json#b58bc94d-d929-ad71-d95b-08b877bf76ba#dc_curve")
    assert len(ioniq.specs[FactField.dc_curve].value.points) == 9


def test_curve_survives_json_roundtrip(records: list[SourceRecord]) -> None:
    rec = by_key(records, "tesla.json#df6a7df8-1b86-8eea-b6b9-19a51055e648#dc_curve")
    back = SourceRecord.model_validate_json(rec.model_dump_json(exclude_none=True))
    assert isinstance(back.specs[FactField.dc_curve].value, ChargeCurve)
    assert back.specs[FactField.dc_curve].value.points[0].root == [0.0, 250.0]


def test_template_curve_is_dropped(
    result: tuple[list[SourceRecord], dict[str, int]],
) -> None:
    records, stats = result
    # Kona Electric 48 kWh 2023: unflagged, but shaped exactly like a generic template.
    assert not any("21442a76" in k and k.endswith("#dc_curve") for k in keys(records))
    kona = by_key(records, "hyundai.json#21442a76-9bde-4723-b35e-3c6179d20b36")
    assert kona.specs[FactField.dc_peak_kw].value == 75
    assert stats["curves_template_dropped"] == 1


def test_dc_placeholder_is_dropped(records: list[SourceRecord]) -> None:
    # Model 3 2023: dc max_power 57.5 == usable battery 57.5 (1C placeholder).
    m3 = by_key(records, "tesla.json#fbffc80f-062d-ed16-d6df-5f621bb35848")
    assert FactField.dc_peak_kw not in m3.specs
    assert m3.specs[FactField.battery_kwh_net].value == 57.5
    assert not any("fbffc80f" in k and k.endswith("#dc_curve") for k in keys(records))


def test_implausible_values_and_non_cars_dropped(
    result: tuple[list[SourceRecord], dict[str, int]],
) -> None:
    records, stats = result
    ds = by_key(records, "ds.json#a88f1ef2-5604-4401-8412-bc41c8b016eb")
    assert FactField.consumption_kwh_100km not in ds.specs  # upstream says 81.1 kWh/100km
    assert not any("zero_motorcycles" in k for k in keys(records))
    assert not any("ebabe01b" in k for k in keys(records))  # Renault Twizy (microcar)
    assert stats["vehicles_in"] == 14
    assert stats["skipped_motorbike"] == 1 and stats["skipped_microcar"] == 1


@pytest.mark.parametrize(
    ("dc", "ok"),
    [
        (
            {
                "is_default_charging_curve": True,
                "charging_curve": [{"percentage": 0, "power": 1}] * 2,
            },
            False,
        ),
        (
            {"charging_curve": [{"percentage": 80, "power": 20}, {"percentage": 0, "power": 50}]},
            True,
        ),
        ({"charging_curve": [{"percentage": 0, "power": 50}]}, False),
        (
            {"charging_curve": [{"percentage": 0, "power": 50}, {"percentage": 120, "power": 5}]},
            False,
        ),
        (
            {"charging_curve": [{"percentage": 0, "power": 50}, {"percentage": 50, "power": -1}]},
            False,
        ),
        (
            {"charging_curve": [{"percentage": 0, "power": 50}, {"percentage": 0, "power": 40}]},
            False,
        ),
    ],
)
def test_charge_curve_rules(dc: dict, ok: bool) -> None:
    curve = adapter.charge_curve(dc)
    assert (curve is not None) == ok
    if curve is not None:
        assert [p.root for p in curve.points] == [[0.0, 50.0], [80.0, 20.0]]  # sorted


def test_normalise_cmd_writes_staging_and_runlog(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("EV_DATA_DIR", str(tmp_path))
    assert adapter.normalise_cmd(from_fixtures=True) == 0
    out = (tmp_path / "staging" / "kilowatt-openev.records.jsonl").read_text().splitlines()
    assert len(out) == len(adapter.normalise(FIXTURE, DAY)) == 17
    for line in out:
        SourceRecord.model_validate_json(line)
    runlog = (tmp_path / "staging" / "runlog.jsonl").read_text()
    assert '"source": "kilowatt-openev"' in runlog and '"curves_kept": 5' in runlog
