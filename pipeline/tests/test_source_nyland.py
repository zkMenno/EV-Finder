"""Nyland importer skeleton on a synthetic CSV (invented cars). No network, no real data."""

from datetime import date
from pathlib import Path

import httpx
import pytest

from ev_pipeline.schema_models import Confidence, FactField
from ev_pipeline.sources.nyland import adapter

FIXTURE = Path(__file__).parent / "fixtures" / "nyland"


def test_normalise_synthetic_csv() -> None:
    records = adapter.normalise(FIXTURE, date(2026, 11, 15))
    assert [r.model for r in records] == ["Testcar Alpha", "Testcar Alpha", "Testcar Beta"]
    alpha = records[0]
    assert alpha.confidence == Confidence.high
    assert alpha.source.licence == "none"  # permission pending
    assert alpha.specs[FactField.real_range_km].value == 412
    assert alpha.specs[FactField.real_range_km].unit == "km"
    assert records[1].specs[FactField.consumption_kwh_100km].value == 16.9  # decimal comma
    assert set(records[2].specs) == {FactField.dc_avg_10_80_kw}


def test_normalise_cmd_never_writes_staging(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("EV_DATA_DIR", str(tmp_path))
    assert adapter.normalise_cmd(from_fixtures=True) == 0
    assert (tmp_path / "local" / "nyland" / "fixture.records.jsonl").exists()
    assert not (tmp_path / "staging").exists()


def test_fetch_needs_env_and_saves_locally(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EV_DATA_DIR", str(tmp_path))
    monkeypatch.delenv(adapter.ENV_URL, raising=False)
    assert adapter.fetch_cmd() == 1

    monkeypatch.setenv(adapter.ENV_URL, "https://example.invalid/sheet.csv")
    transport = httpx.MockTransport(lambda req: httpx.Response(200, text="make,model\nA,B\n"))
    with httpx.Client(transport=transport) as client:
        assert adapter.fetch_cmd(client) == 0
    local = tmp_path / "local" / "nyland"
    assert (local / "sheet.csv").read_text() == "make,model\nA,B\n"
    assert "example.invalid" not in (local / "_fetch.json").read_text()
    assert "example.invalid" not in (local / "runlog.jsonl").read_text()
    assert not (tmp_path / "staging").exists()
