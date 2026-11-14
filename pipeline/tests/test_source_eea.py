"""EEA adapter on a recorded sample of the grouped Discodata response. No network."""

import json
from datetime import date
from pathlib import Path

import httpx
import pytest

from ev_pipeline.schema_models import Confidence, Country, FactField
from ev_pipeline.sources.eea import adapter

FIXTURE = Path(__file__).parent / "fixtures" / "eea"


def test_counts_and_type_approval_specs() -> None:
    records = adapter.normalise(FIXTURE, date(2026, 11, 15))
    for rec in records:
        assert rec.source.licence == "CC-BY-4.0"
        assert "DG CLIMA" in (rec.source.attribution or "")
        assert rec.country in {Country.NL, Country.DE, Country.FR, Country.BE}
        for spec in rec.specs.values():
            assert spec.unit in {"count", "kg", "kWh/100km", "km"}
    key = "[CO2Emission].[latest].[co2cars_2025Pv31]:NL|TESLA|MODEL 3|2025"
    [count] = [r for r in records if r.record_key == key]
    assert count.kind == "registration_count"
    assert count.confidence == Confidence.medium
    assert count.specs[FactField.registered_count].value == 5828
    [spec] = [r for r in records if r.record_key == key + "#type_approval_avg"]
    assert spec.kind == "spec"
    assert spec.confidence == Confidence.low
    assert spec.specs[FactField.weight_kg].value == 1841
    assert spec.specs[FactField.consumption_kwh_100km].value == pytest.approx(13.52)  # Wh/km / 10
    assert spec.specs[FactField.wltp_range_km].value == 583


def test_missing_averages_give_no_spec_record() -> None:
    records = adapter.normalise(FIXTURE, date(2026, 11, 15))
    be = [r for r in records if "BE|TESLA|MODEL 3|" in r.record_key]
    spec = next(r for r in be if r.kind == "spec")
    assert set(spec.specs) == {FactField.weight_kg}  # BE has no Z / Zr for this model


def test_fetch_posts_query_and_checks_licence(tmp_path: Path) -> None:
    posted: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if "sdi.eea.europa.eu" in str(request.url):
            limit = [{"default": "License CC-BY 4.0 (https://...). Copyright holder: DG-CLIMA."}]
            return httpx.Response(
                200,
                json={
                    "hits": {"hits": [{"_source": {"MD_ConstraintsUseLimitationObject": limit}}]}
                },
            )
        assert request.method == "POST"  # GET trips the WAF
        posted.append(request.content)
        return httpx.Response(200, json={"results": [{"MS": "NL"}]})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        assert adapter.fetch(client, tmp_path) == 1
    assert b"electric" in posted[0]
    assert json.loads((tmp_path / "_fetch.json").read_text())["licence_metadata"].startswith(
        "License CC-BY 4.0"
    )


def test_fetch_refuses_without_licence(tmp_path: Path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"hits": {"hits": []}})

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(RuntimeError),
    ):
        adapter.fetch(client, tmp_path)
