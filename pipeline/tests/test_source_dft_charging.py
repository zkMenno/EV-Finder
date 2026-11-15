"""DfT EVCI charging statistics loader on recorded (trimmed) tables. No network."""

import json
from collections import Counter
from datetime import date
from pathlib import Path

import httpx
import pytest

from ev_pipeline.sources.dft_charging import adapter, ods
from ev_pipeline.sources.eafo import charging_stats as cs

FIXTURE = Path(__file__).parent / "fixtures" / "dft_charging"
SID = "dft-ev-charging-infrastructure:uk"


def build(log: Counter[str] | None = None) -> cs.StatBuilder:
    return adapter.normalise(FIXTURE, date(2026, 11, 15), log)


def test_ods_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "t.ods"
    ods.write_sheets(path, {"S": [["Date", "Value"], ["2026-07-01T00:00:00", 3.0], [], ["x"]]})
    assert ods.read_sheets(path) == {
        "S": [["Date", "Value"], ["2026-07-01T00:00:00", 3.0], [], ["x"]]
    }


def test_headline_figures_1_july_2026() -> None:
    r = build().rows
    assert r[f"{SID}::2026-07-01:public-points:all"]["value"] == 121171
    dc = r[f"{SID}::2026-07-01:public-points-dc:all"]
    assert dc["value"] == 28887 and "below 50 kW" in dc["notes"]
    per100k = r[f"{SID}::2026-07-01:points-per-100k-people:all"]
    assert per100k["value"] == 174.9 and per100k["unit"] == "per 100k people"
    assert r[f"{SID}::2026-07-01:public-points-dc:uk-dft-rapid"]["value"] == 14891
    assert r[f"{SID}::2026-07-01:public-points-dc:uk-dft-ultra-rapid"]["value"] == 13996


def test_regions_use_ons_codes() -> None:
    r = build().rows
    london = r[f"{SID}:e12000007:2026-07-01:public-points:all"]
    assert london["region"] == "E12000007" and london["value"] == 31371
    assert "London" in london["source_label"]


def test_definition_window_and_skips() -> None:
    log: Counter[str] = Counter()
    b = build(log)
    # 2025 quarters are outside uk-dft-evse-2026 (valid_from 2026-01-01): 4 dates x 4 areas x 3
    assert b.dropped_out_of_validity == 48
    assert all(row["period_end"] >= "2026-01-01" for row in b.rows.values())
    assert log["evci0201_skipped_no_band"] == 6  # Standard + Standard plus, 3 dates
    assert log["evci0101_skipped_no_metric"] == 28  # 50kW+ per 100k, 7 dates x 4 areas


def test_note_markers_resolved_and_rows_valid() -> None:
    rows = build().rows
    april = rows[f"{SID}::2026-04-01:public-points-dc:uk-dft-rapid"]
    assert april["notes"].startswith("[note 3] A reduction in chargers")
    for row in rows.values():
        cs.validate(row)
        assert row["definition_id"] == "uk-dft-evse-2026"
        assert row["confidence"] == "medium"
        assert row["country"] == "UK"


def test_fetch_resolves_via_content_api(tmp_path: Path) -> None:
    base = "https://assets.publishing.service.gov.uk/media/abc/"
    urls = {
        "evci0101": base + "evci0101_2026-07_EV_chargers_by_region_and_country_UK.ods",
        "evci0201": base + "evci0201_2026-07_EV_chargers_by_power_band_UK.ods",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "www.gov.uk":
            return httpx.Response(
                200,
                json={
                    "public_updated_at": "2026-08-27T09:30:03+01:00",
                    "details": {
                        "attachments": [
                            {"url": base + "evci0102_2026-07_by_local_authority_UK.ods"},
                            *({"url": u} for u in urls.values()),
                        ]
                    },
                },
            )
        name = "evci0101.ods" if "evci0101" in request.url.path else "evci0201.ods"
        return httpx.Response(200, content=(FIXTURE / name).read_bytes())

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        assert adapter.fetch(client, tmp_path) > 0
    meta = json.loads((tmp_path / "_fetch.json").read_text())
    assert meta["files"]["evci0101"]["url"] == urls["evci0101"]
    assert meta["licence"] == "OGL-UK-3.0"
    assert len(adapter.normalise(tmp_path, date(2026, 11, 15)).rows) == len(build().rows)


def test_fetch_fails_when_table_missing(tmp_path: Path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"details": {"attachments": []}})

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(FileNotFoundError),
    ):
        adapter.fetch(client, tmp_path)


def test_normalise_cmd_from_fixtures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EV_DATA_DIR", str(tmp_path))
    assert adapter.normalise_cmd(from_fixtures=True) == 0
    lines = (tmp_path / "staging" / "dft-charging.charging_stats.jsonl").read_text().splitlines()
    assert len(lines) == len(build().rows)
    meta = json.loads((tmp_path / "staging" / "dft-charging.charging_stats.meta.json").read_text())
    assert meta["licence"] == "OGL-UK-3.0" and meta["releasable"] is True
