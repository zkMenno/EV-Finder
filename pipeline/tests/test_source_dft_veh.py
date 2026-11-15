"""DfT VEH0120 adapter on a recorded sample of df_VEH0120_UK. No network."""

import json
from datetime import date
from pathlib import Path

import httpx
import pytest

from ev_pipeline.schema_models import Confidence, Country, FactField
from ev_pipeline.sources.dft_veh import adapter

FIXTURE = Path(__file__).parent / "fixtures" / "dft_veh"
CSV = FIXTURE / "df_VEH0120_UK.csv"


def test_fixture_is_a_small_sample() -> None:
    assert CSV.read_text().count("\n") <= 101


def test_latest_quarter() -> None:
    assert adapter.latest_quarter(["Make", "2025 Q4", "2026 Q2", "2026 Q1"]) == "2026 Q2"


def test_bev_filter_and_counts() -> None:
    quarter, counts, missing = adapter.aggregate(CSV)
    assert quarter == "2026 Q2"
    gens = {g for _, g, _ in counts}
    assert "HYUNDAI KONA" not in gens  # only diesel Kona rows in the sample
    assert not any("MODEL MISSING" in g for g in gens)
    assert missing == 2  # AION + ARIEL licensed BEVs without a model
    # Licensed only: SORN rows are not added
    assert counts[("TESLA", "TESLA MODEL 3", "MODEL 3 LONG RANGE AWD")] == 53576
    model3 = sum(n for (_, g, _), n in counts.items() if g == "TESLA MODEL 3")
    assert model3 == 146205  # every Model 3 BEV car row is in the sample
    assert not any(mk == "ADDAX" for mk, _, _ in counts)  # light goods vehicles dropped
    assert not any(g == "FIAT PANDA" for _, g, _ in counts)  # fuel cell dropped


def test_normalise_records() -> None:
    records = adapter.normalise(FIXTURE, date(2026, 11, 15))
    assert records
    for rec in records:
        assert rec.kind == "registration_count"
        assert rec.country == Country.UK
        assert rec.year is None
        assert rec.confidence == Confidence.high
        assert rec.source.licence == "OGL-UK-3.0"
        assert "Open Government Licence v3.0" in rec.source.attribution
        assert rec.specs[FactField.registered_count].unit == "count"
        assert rec.record_key.startswith("VEH0120_UK:2026 Q2:Licensed:")
    [leaf] = [r for r in records if r.variant_name == "LEAF ACENTA"]
    assert (leaf.make, leaf.model) == ("NISSAN", "NISSAN LEAF")
    assert leaf.specs[FactField.registered_count].value == 9714


def test_fetch_resolves_url_and_streams(tmp_path: Path) -> None:
    body = CSV.read_bytes()
    url = "https://assets.publishing.service.gov.uk/media/abc/df_VEH0120_UK.csv"

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "www.gov.uk":
            return httpx.Response(
                200,
                json={
                    "public_updated_at": "2026-09-23T09:30:04+01:00",
                    "details": {
                        "attachments": [
                            {"url": url.replace("UK", "GB"), "title": "GB"},
                            {"url": url, "title": "UK", "file_size": len(body)},
                        ]
                    },
                },
            )
        assert str(request.url) == url
        return httpx.Response(200, content=body)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        assert adapter.fetch(client, tmp_path) == len(body)
    assert (tmp_path / "df_VEH0120_UK.csv").read_bytes() == body
    meta = json.loads((tmp_path / "_fetch.json").read_text())
    assert meta["url"] == url
    assert "Open Government Licence" in meta["licence_basis"]


def test_normalise_cmd_from_fixtures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EV_DATA_DIR", str(tmp_path))
    assert adapter.normalise_cmd(from_fixtures=True) == 0
    lines = (tmp_path / "staging" / "dft-veh.records.jsonl").read_text().splitlines()
    assert len(lines) == len(adapter.normalise(FIXTURE, date(2026, 11, 15)))
