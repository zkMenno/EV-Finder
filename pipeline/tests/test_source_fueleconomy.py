"""fueleconomy.gov adapter on a recorded sample of vehicles.csv. No network."""

import io
import json
import zipfile
from collections import Counter
from datetime import date
from pathlib import Path

import httpx
import pytest

from ev_pipeline.schema_models import Confidence, FactField
from ev_pipeline.sources.fueleconomy import adapter

FIXTURE = Path(__file__).parent / "fixtures" / "fueleconomy"
CSV = FIXTURE / "vehicles.csv"


def test_fixture_is_a_small_sample() -> None:
    assert CSV.read_text().count("\n") <= 201


def test_bev_filter_drops_phev_fcv_and_petrol() -> None:
    stats: Counter[str] = Counter()
    records = adapter.normalise(FIXTURE, date(2026, 11, 15), stats)
    assert stats["bev_rows"] == 77  # the fixture's other 20 rows are PHEV, FCV, petrol
    assert {r.make for r in records} == {
        "Tesla",
        "Nissan",
        "Hyundai",
        "Volkswagen",
        "Porsche",
        "Kia",
    }


def test_units_converted_to_metric() -> None:
    records = adapter.normalise(FIXTURE, date(2026, 11, 15))
    [ioniq] = [r for r in records if r.record_key == "vehicles.csv:id=44922;market=us"]
    assert (ioniq.make, ioniq.model, ioniq.year) == ("Hyundai", "Ioniq 5 AWD (Long Range)", 2022)
    assert ioniq.country is None
    assert ioniq.drivetrain == "awd"
    assert ioniq.confidence == Confidence.medium
    assert ioniq.specs[FactField.epa_range_km].value == round(256 * 1.609344, 1) == 412.0
    assert ioniq.specs[FactField.epa_range_km].unit == "km"
    assert ioniq.specs[FactField.consumption_kwh_100km].value == round(34.3285 / 1.609344, 2)
    assert ioniq.specs[FactField.consumption_kwh_100km].unit == "kWh/100km"
    assert ioniq.source.licence == "US-Government-Public-Domain"


def test_battery_only_from_explicit_pack_text_with_low_confidence() -> None:
    records = adapter.normalise(FIXTURE, date(2026, 11, 15))
    batteries = [r for r in records if r.record_key.endswith("#battery")]
    assert batteries and {r.make for r in batteries} <= {"Tesla", "Nissan"}
    for r in batteries:
        assert r.confidence == Confidence.low
        assert set(r.specs) == {FactField.battery_kwh_gross}
        assert r.specs[FactField.battery_kwh_gross].value in {
            24.0,
            30.0,
            40.0,
            60.0,
            62.0,
            70.0,
            75.0,
            85.0,
            90.0,
            100.0,
        }
    assert all(";market=us" in r.record_key for r in records)


def test_fetch_streams_zip(tmp_path: Path) -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("vehicles.csv", CSV.read_text())
    body = buf.getvalue()

    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == adapter.URL
        return httpx.Response(200, content=body, headers={"last-modified": "Wed, 04 Nov 2026"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        assert adapter.fetch(client, tmp_path) == len(body)
    meta = json.loads((tmp_path / "_fetch.json").read_text())
    assert meta["licence"] == "US-Government-Public-Domain"
    assert len(adapter.normalise(tmp_path, date(2026, 11, 15))) == len(
        adapter.normalise(FIXTURE, date(2026, 11, 15))
    )


def test_fetch_rejects_non_zip(tmp_path: Path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"<html>maintenance</html>")

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(zipfile.BadZipFile),
    ):
        adapter.fetch(client, tmp_path)
    assert not (tmp_path / adapter.ZIP_NAME).exists()


def test_normalise_cmd_from_fixtures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EV_DATA_DIR", str(tmp_path))
    assert adapter.normalise_cmd(from_fixtures=True) == 0
    lines = (tmp_path / "staging" / "fueleconomy.records.jsonl").read_text().splitlines()
    assert len(lines) == len(adapter.normalise(FIXTURE, date(2026, 11, 15)))
