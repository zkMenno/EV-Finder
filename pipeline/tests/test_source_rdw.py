"""RDW adapter on a recorded sample of the grouped SoQL response. No network."""

import json
from datetime import date
from pathlib import Path

import httpx
import pytest

from ev_pipeline.schema_models import Confidence, Country, FactField
from ev_pipeline.sources.rdw import adapter

FIXTURE = Path(__file__).parent / "fixtures" / "rdw"


def test_fixture_is_a_small_sample() -> None:
    assert len(json.loads((FIXTURE / "page-000.json").read_text())) <= 200


def test_normalise_counts() -> None:
    records = adapter.normalise(FIXTURE, date(2026, 11, 15))
    assert records
    for rec in records:
        assert rec.kind == "registration_count"
        assert rec.country == Country.NL
        assert rec.confidence == Confidence.high
        assert rec.source.licence == "CC0-1.0"
        assert rec.source.attribution
        assert list(rec.specs) == [FactField.registered_count]
        assert rec.specs[FactField.registered_count].unit == "count"
    [m3_2019] = [r for r in records if r.record_key == "m9d7-ebf2:TESLA|MODEL 3|2019"]
    assert (m3_2019.make, m3_2019.model, m3_2019.year) == ("TESLA", "MODEL 3", 2019)
    assert m3_2019.specs[FactField.registered_count].value == 25235


def test_fetch_paginates_and_records_licence(tmp_path: Path) -> None:
    row = {"merk": "X", "handelsbenaming": "M", "jaar": "2024", "n": "1"}
    pages = [[row, row], []]
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.startswith("/api/views/"):
            return httpx.Response(
                200,
                json={
                    "name": "Gekentekende_voertuigen",
                    "license": {"name": "Public Domain"},
                    "metadata": {"custom_fields": {"Licentie": {"Licentie": "CC0"}}},
                },
            )
        seen.append(request.url.params["$offset"])
        return httpx.Response(200, json=pages[len(seen) - 1])

    adapter.PAGE_SIZE, old = 2, adapter.PAGE_SIZE
    try:
        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            assert adapter.fetch(client, tmp_path) == 2
    finally:
        adapter.PAGE_SIZE = old
    assert seen == ["0", "2"]
    meta = json.loads((tmp_path / "_fetch.json").read_text())
    assert meta["licence_metadata"]["custom_fields.Licentie"] == "CC0"
    assert "cilinderinhoud IS NULL" in meta["query"]["$where"]


def test_normalise_cmd_from_fixtures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EV_DATA_DIR", str(tmp_path))
    assert adapter.normalise_cmd(from_fixtures=True) == 0
    assert (tmp_path / "staging" / "rdw.records.jsonl").read_text().count("\n") == 118
