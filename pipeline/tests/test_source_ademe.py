"""ADEME Car Labelling adapter on a recorded sample of the CSV. No network."""

import json
from datetime import date
from pathlib import Path

import httpx
import pytest

from ev_pipeline.schema_models import Confidence, Country, FactField
from ev_pipeline.sources.ademe import adapter

FIXTURE = Path(__file__).parent / "fixtures" / "ademe"
CSV = FIXTURE / adapter.FILE


def _records():
    return adapter.normalise(FIXTURE, date(2026, 11, 15))


def test_fixture_is_a_small_sample() -> None:
    assert CSV.read_text(encoding="utf-8-sig").count("\n") <= 101


def test_bev_filter() -> None:
    versions, rows = adapter.read_versions(CSV)
    assert rows == 53  # ELECTRIC rows only; plug-in and full hybrids are skipped
    text = CSV.read_text(encoding="utf-8-sig")
    assert "ELEC+ESSENC HR" in text and "ESS+ELEC HNR" in text  # present in the sample
    assert all(r.source.id.root == "ademe" for r in _records())
    assert not any("hybride" in (r.variant_name or "").lower() for r in _records())


def test_licence_and_confidence() -> None:
    for rec in _records():
        assert rec.kind == "spec"
        assert rec.source.licence == "Licence-Ouverte-2.0"
        assert rec.source.attribution == "ADEME – Car Labelling, Licence Ouverte"
        assert rec.confidence == Confidence.medium
        assert rec.year is None


def test_units_and_known_values() -> None:
    got = {r.record_key: r for r in _records()}
    ix = got["ademe-car-labelling:B.M.W.|IX|iX xDrive40"]
    # 193.1 Wh/km -> 19.31 kWh/100km; range is the best end of the WLTP family
    assert ix.specs[FactField.consumption_kwh_100km].value == 19.31
    assert ix.specs[FactField.consumption_kwh_100km].unit == "kWh/100km"
    assert ix.specs[FactField.wltp_range_km].value == 426
    assert ix.specs[FactField.wltp_range_km].unit == "km"
    assert ix.specs[FactField.weight_kg].value == 2365  # Poids à vide (no driver)
    assert FactField.power_kw not in ix.specs  # only nominal power in the source
    price = got["ademe-car-labelling:B.M.W.|IX|iX xDrive40#price_new:FR"]
    assert price.country == Country.FR
    assert price.specs[FactField.price_new].value == 93607
    assert price.specs[FactField.price_new].unit == "EUR"


def test_best_case_never_averaged() -> None:
    corsa = [r for r in _records() if r.model == "CORSA" and FactField.wltp_range_km in r.specs]
    # Two homologations under one name: kept apart, each at its own best value
    assert sorted(r.specs[FactField.wltp_range_km].value for r in corsa) == [362, 373]
    assert sorted(r.specs[FactField.consumption_kwh_100km].value for r in corsa) == [14.98, 15.22]


def test_single_value_used_when_min_missing() -> None:
    [m3] = [
        r
        for r in _records()
        if r.variant_name == "MODEL 3 (88Kw)" and FactField.wltp_range_km in r.specs
    ]
    assert m3.specs[FactField.wltp_range_km].value == 491
    assert m3.specs[FactField.consumption_kwh_100km].value == 14.4


def test_mojibake_repaired() -> None:
    assert adapter.fix_text("500e berline Ã©lectrique") == "500e berline électrique"
    # Mis-decoded no-break spaces (Nissan Ariya rows in the live file)
    assert adapter.fix_text("87kWh\u00c2\u00a0ENGAGE\u00c2\u00a0\u00c2\u00a0") == "87kWh ENGAGE"
    assert any("électrique" in (r.variant_name or "") for r in _records())
    assert not any("Ã" in (r.variant_name or "") for r in _records())


def test_fetch_checks_licence(tmp_path: Path) -> None:
    body = CSV.read_bytes()
    licence = {"title": "Licence Ouverte / Open Licence"}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/raw"):
            return httpx.Response(200, content=body)
        return httpx.Response(200, json={"license": licence, "count": 3604})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        assert adapter.fetch(client, tmp_path) == len(body)
        meta = json.loads((tmp_path / "_fetch.json").read_text())
        assert meta["licence_metadata"]["title"].startswith("Licence Ouverte")
        licence = {"title": "Tous droits réservés"}
        with pytest.raises(adapter.LicenceChanged):
            adapter.fetch(client, tmp_path / "x")


def test_normalise_cmd_from_fixtures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EV_DATA_DIR", str(tmp_path))
    assert adapter.normalise_cmd(from_fixtures=True) == 0
    lines = (tmp_path / "staging" / "ademe.records.jsonl").read_text().splitlines()
    assert len(lines) == len(_records())
