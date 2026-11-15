"""EEA adapter on a recorded sample of the grouped Discodata response. No network."""

import json
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs

import httpx
import pytest

from ev_pipeline.schema_models import Confidence, Country, FactField
from ev_pipeline.sources.eea import adapter

FIXTURE = Path(__file__).parent / "fixtures" / "eea"


def test_counts_only_no_averaged_specs() -> None:
    records = adapter.normalise(FIXTURE, date(2026, 11, 15))
    assert records
    for rec in records:
        assert rec.source.licence == "CC-BY-4.0"
        assert "DG CLIMA" in (rec.source.attribution or "")
        assert rec.country in {Country.NL, Country.DE, Country.FR, Country.BE}
        # Registration-weighted averages across type approvals are never spec facts, and EEA
        # mass in running order (incl. 75 kg driver) must never become weight_kg.
        assert rec.kind in {"registration_count", "corroboration"}
        assert FactField.weight_kg not in rec.specs
        if rec.kind == "registration_count":
            assert set(rec.specs) == {FactField.registered_count}
        assert not rec.record_key.endswith("#type_approval_avg")
    key = "[CO2Emission].[latest].[co2cars_2025Pv31]:NL|TESLA|MODEL 3|2025"
    [count] = [r for r in records if r.record_key == key]
    assert count.confidence == Confidence.medium
    assert count.specs[FactField.registered_count].value == 5828


def _sdi(limit_text: str = "License CC-BY 4.0 (https://...). Copyright holder: DG-CLIMA."):
    limit = [{"default": limit_text}]
    return {"hits": {"hits": [{"_source": {"MD_ConstraintsUseLimitationObject": limit}}]}}


def test_fetch_posts_query_and_checks_licence(tmp_path: Path) -> None:
    posted: list[str] = []
    sdi: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if "sdi.eea.europa.eu" in str(request.url):
            sdi.append(json.loads(request.content)["query"]["term"]["uuid"])
            return httpx.Response(200, json=_sdi())
        assert request.method == "POST"  # GET trips the WAF
        query = parse_qs(request.content.decode())["query"][0]
        posted.append(query)
        year = int(query.split("Year = ")[1].split()[0])
        return httpx.Response(200, json={"results": [{"MS": "NL", "Year": year}]})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        assert adapter.fetch(client, tmp_path, sleep_s=0) == len(adapter.TABLES)
    # one licence check per dataset record, one grouped query per data year
    assert sdi == [t.metadata_uuid for t in adapter.TABLES]
    assert len(posted) == len(adapter.TABLES)
    assert all("Ft = 'electric'" in q and "GROUP BY MS, Mk, Cn, Year" in q for q in posted)
    meta = json.loads((tmp_path / "_fetch.json").read_text())
    assert meta["licence_metadata"].startswith("License CC-BY 4.0")
    assert [t["year"] for t in meta["tables"]] == list(range(2018, 2026))
    rows = [r for p in sorted(tmp_path.glob("page-*.json")) for r in json.loads(p.read_text())]
    assert [r["table"] for r in rows] == [t.table for t in adapter.TABLES]


def test_tables_cover_2018_to_2024_final_and_pick_one_release_per_year() -> None:
    by_year = {t.year: t for t in adapter.TABLES}
    assert set(range(2018, 2025)) <= set(by_year)
    assert all(by_year[y].status == "F" for y in range(2018, 2025))
    assert len({t.year for t in adapter.TABLES}) == len(adapter.TABLES)  # one table per year
    # the all-years table holds every release: the filter must pin year, status and version
    q2019 = adapter.query_for(by_year[2019])
    assert "[co2cars]" in q2019
    assert "Year = 2019 AND Status = 'F' AND Version_file = 'v20'" in q2019
    q2024 = adapter.query_for(by_year[2024])
    assert "[co2cars_2024Fv30]" in q2024 and "Year = 2024" in q2024
    assert "Status" not in q2024


def test_fetch_pauses_between_requests(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sleeps: list[float] = []
    monkeypatch.setattr(adapter.time, "sleep", sleeps.append)

    def handler(request: httpx.Request) -> httpx.Response:
        if "sdi.eea.europa.eu" in str(request.url):
            return httpx.Response(200, json=_sdi())
        return httpx.Response(200, json={"results": []})

    tables = adapter.TABLES[:2]
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        adapter.fetch(client, tmp_path, tables=tables, sleep_s=2.0)
    assert sleeps == [2.0] * 3  # 4 requests (2 licence checks, 2 queries), 3 pauses


def test_fetch_refuses_if_one_year_lost_its_licence(tmp_path: Path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if "sdi.eea.europa.eu" in str(request.url):
            uuid = json.loads(request.content)["query"]["term"]["uuid"]
            text = "All rights reserved" if uuid == adapter.TABLES[3].metadata_uuid else None
            return httpx.Response(200, json=_sdi(text) if text else _sdi())
        raise AssertionError("no query before every licence is confirmed")

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(RuntimeError, match="2021"),
    ):
        adapter.fetch(client, tmp_path, sleep_s=0)


def test_history_rows_one_record_per_year_final_is_high(tmp_path: Path) -> None:
    rows = [
        {"MS": "NL", "Mk": "TESLA", "Cn": "MODEL 3", "Year": 2019, "registrations": 15000,
         "table": adapter.ALL_YEARS},
        {"MS": "NL", "Mk": "TESLA", "Cn": "MODEL 3", "Year": 2024, "registrations": 4000,
         "table": "[CO2Emission].[latest].[co2cars_2024Fv30]"},
        {"MS": "NL", "Mk": "TESLA", "Cn": "MODEL 3", "Year": 2025, "registrations": 5828,
         "table": adapter.TABLE},
    ]  # fmt: skip
    (tmp_path / "page-001.json").write_text(json.dumps(rows))
    recs = adapter.normalise(tmp_path, date(2026, 11, 15))
    got = {r.year: r for r in recs}
    assert sorted(got) == [2019, 2024, 2025]
    assert got[2019].record_key == "[CO2Emission].[latest].[co2cars]:NL|TESLA|MODEL 3|2019"
    assert got[2019].confidence == Confidence.high
    assert got[2024].confidence == Confidence.high
    assert got[2025].confidence == Confidence.medium  # provisional
    assert [got[y].specs[FactField.registered_count].value for y in (2019, 2024, 2025)] == [
        15000, 4000, 5828
    ]  # fmt: skip


def test_fetch_refuses_without_licence(tmp_path: Path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"hits": {"hits": []}})

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(RuntimeError),
    ):
        adapter.fetch(client, tmp_path, sleep_s=0)


def test_corroboration_records_from_averages() -> None:
    """Q-019 (a): range and consumption averages ride along as corroboration only."""
    records = adapter.normalise(FIXTURE, date(2026, 11, 15))
    corro = {r.record_key: r for r in records if r.kind == "corroboration"}
    assert corro
    de = corro["[CO2Emission].[latest].[co2cars_2025Pv31]:DE|TESLA|MODEL 3|2025#corroboration"]
    assert de.confidence == Confidence.low
    assert de.specs[FactField.wltp_range_km].unit == "km"
    assert round(de.specs[FactField.wltp_range_km].value) == 597
    assert de.specs[FactField.consumption_kwh_100km].unit == "Wh/km"
    assert de.specs[FactField.registered_count].value == 6848  # the average's weight
    assert set(de.specs) == {
        FactField.wltp_range_km,
        FactField.consumption_kwh_100km,
        FactField.registered_count,
    }
    # BE Model 3 has no Zr/Z average: no corroboration record, the count stays.
    assert not any("BE|TESLA|MODEL 3|" in k for k in corro)
    assert any(r.record_key.endswith("BE|TESLA|MODEL 3|2025") for r in records)
