"""EAFO AFIR recharging points loader on a synthetic-values fixture. No network.

The fixture keeps EAFO's real layout and labels but invents every number: EAFO's licence is
unclear (third-party data), so no real figures are committed.
"""

import json
from collections import Counter
from datetime import date
from pathlib import Path

import httpx
import pytest

from ev_pipeline.sources.eafo import adapter
from ev_pipeline.sources.eafo import charging_stats as cs

FIXTURE = Path(__file__).parent / "fixtures" / "eafo"


def rows_by_id() -> dict[str, dict]:
    return {r["id"]: r for r in adapter.normalise(FIXTURE, date(2026, 11, 15)).sorted_rows()}


def test_latest_period_from_title() -> None:
    assert adapter.latest_period("dataset (2020 - May 2026).xlsx") == date(2026, 5, 31)
    with pytest.raises(ValueError):
        adapter.latest_period("dataset.xlsx")


def test_totals_dc_and_bands() -> None:
    rows = rows_by_id()
    de25 = "eafo:de::2025-12-31"
    assert rows[f"{de25}:public-points:all"]["value"] == 28000  # 1000 x (1+...+7)
    assert rows[f"{de25}:public-points-dc:all"]["value"] == 22000  # four DC categories
    assert rows[f"{de25}:public-points-dc:eafo-dc-150-349"]["value"] == 6000
    assert rows["eafo:de::2026-05-31:public-points-dc:eafo-dc-350-plus"]["value"] == 7001
    # no band rows for AC or slow DC: they have no taxonomy band yet
    assert {r["power_band_id"] for r in rows.values()} == {
        None,
        "eafo-dc-50-149",
        "eafo-dc-150-349",
        "eafo-dc-350-plus",
    }


def test_missing_category_counts_as_zero_and_is_noted() -> None:
    log: Counter[str] = Counter()
    b = adapter.normalise(FIXTURE, date(2026, 11, 15), log)
    be = b.rows["eafo:be::2025-12-31:public-points:all"]
    assert be["value"] == 210
    assert "1 AFIR categories absent" in be["notes"]
    assert log["category_cells_missing_counted_as_0"] == 1
    assert log["unknown_country"] == 1  # 'Atlantis'


def test_every_row_is_a_valid_charging_stat() -> None:
    for row in rows_by_id().values():
        cs.validate(row)
        assert row["definition_id"] == "afir-recharging-point"
        assert row["source_id"] == "eafo"
        assert row["entered_by"] == "pipeline"
        assert row["confidence"] == "medium"
        assert "sha256:" in row["source_record"]
        assert set(row) <= {
            "id",
            "country",
            "region",
            "period_end",
            "metric_id",
            "power_band_id",
            "value",
            "unit",
            "source_id",
            "definition_id",
            "confidence",
            "entered_by",
            "source_url",
            "source_record",
            "source_label",
            "retrieved_at",
            "notes",
        }  # aggregates only: no location, operator or charger fields


def test_find_download_and_legal_check() -> None:
    page = (
        '<a href="/system/files/documents/2026-04/BEV%20M1%20reg.xls">x</a>'
        '<a href="https://alternative-fuels-observatory.ec.europa.eu/system/files/documents/'
        "2026-06/Recharging%20points%20per%20power%20level%20%28AFIR%29%20dataset%20"
        '%282020%20-%20May%202026%29.xlsx">Download</a>'
    )
    url, label = adapter.find_download(page)
    assert url.endswith("%29.xlsx") and label.startswith(adapter.LINK_MARK)
    with pytest.raises(FileNotFoundError):
        adapter.find_download("<a href='/other.xlsx'>")
    check = adapter.legal_notice_check(
        "<p>licensed under the Creative Commons Attribution 4.0 International</p>"
        "<p>includes third-party works</p>"
    )
    assert check == {"states_cc_by_4_for_eu_owned_content": True, "third_party_exclusion": True}


def test_fetch_with_mock_transport(tmp_path: Path) -> None:
    body = (FIXTURE / adapter.FILE_NAME).read_bytes()
    link = (
        "/system/files/documents/2026-06/Recharging%20points%20per%20power%20level%20"
        "%28AFIR%29%20dataset%20%282020%20-%20May%202026%29.xlsx"
    )

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("frequently-asked-questions"):
            return httpx.Response(200, text=f'<a href="{link}">Download</a>')
        if request.url.host == "commission.europa.eu":
            return httpx.Response(
                200, text="Creative Commons Attribution 4.0 ... third-party works"
            )
        return httpx.Response(200, content=body)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        assert adapter.fetch(client, tmp_path) == len(body)
    meta = json.loads((tmp_path / "_fetch.json").read_text())
    assert meta["legal_notice"]["third_party_exclusion"] is True
    assert "active_pending_confirmation" in meta["status_note"]  # Decision 037
    assert len(adapter.normalise(tmp_path, date(2026, 11, 15)).rows) == len(rows_by_id())


def test_normalise_cmd_writes_stats_and_pending_meta(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("EV_DATA_DIR", str(tmp_path))
    assert adapter.normalise_cmd(from_fixtures=True) == 0
    lines = (tmp_path / "staging" / "eafo.charging_stats.jsonl").read_text().splitlines()
    assert len(lines) == len(rows_by_id())
    meta = json.loads((tmp_path / "staging" / "eafo.charging_stats.meta.json").read_text())
    # Decision 037: in use now, credited, confirmation pending.
    assert meta["status"] == "active_pending_confirmation" and meta["releasable"] is True
    assert meta["licence"] == "CC-BY-4.0"
    assert meta["attribution"].startswith(
        "Source: European Alternative Fuels Observatory (European Commission), 20"
    )
