"""Bundesnetzagentur loader on a trimmed copy of 'Ladeinfrastruktur in Zahlen'. No network."""

import json
from collections import Counter
from datetime import date
from pathlib import Path

import httpx
import pytest

from ev_pipeline.sources.bnetza import adapter
from ev_pipeline.sources.eafo import charging_stats as cs

FIXTURE = Path(__file__).parent / "fixtures" / "bnetza"
SID = "bnetza-ladesaeulenregister:de"


def rows() -> dict[str, dict]:
    return adapter.normalise(FIXTURE, date(2026, 11, 15)).rows


def test_national_points_by_band() -> None:
    r = rows()
    assert r[f"{SID}::2026-10-01:public-points:all"]["value"] == 218113
    assert r[f"{SID}::2026-10-01:public-points:de-bnetza-normal"]["value"] == 160376
    assert r[f"{SID}::2026-10-01:public-points:de-bnetza-fast"]["value"] == 57737
    assert r[f"{SID}::2017-01-01:public-points:all"]["value"] == 6746
    kw = r[f"{SID}::2026-10-01:installed-kw:all"]
    assert kw["value"] == 9574698.9 and kw["unit"] == "kW"


def test_states_use_iso_codes_and_sum_to_national() -> None:
    log: Counter[str] = Counter()
    b = adapter.normalise(FIXTURE, date(2026, 11, 15), log)
    assert log["state_sum_mismatch"] == 0 and log["unknown_state"] == 0
    by = b.rows[f"{SID}:de-by:2026-10-01:public-points:de-bnetza-fast"]
    assert by["region"] == "DE-BY" and by["value"] == 11062
    assert "Bayern" in by["source_label"]
    states = [
        v for k, v in b.rows.items() if k.endswith(":2026-10-01:public-points:all") and v["region"]
    ]
    assert len(states) == 16
    assert sum(s["value"] for s in states) == 218113
    assert not any(v["region"] == "Summe" for v in b.rows.values())


def test_rows_valid_and_aggregate_only() -> None:
    b = adapter.normalise(FIXTURE, date(2026, 11, 15))
    assert b.report_date == "01. Oktober 2026"
    # 4 quarters x (3 point bands + kW) nationally, + 16 states x (3 bands + kW)
    assert len(b.rows) == 4 * 4 + 4 * 16 * 4
    for row in b.rows.values():
        cs.validate(row)
        assert row["definition_id"] == "de-bnetza-ladepunkt"
        assert row["confidence"] == "high"
        assert row["country"] == "DE"


def test_unknown_band_id_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(adapter.POINT_ROWS, "Schnellladepunkte", "no-such-band")
    with pytest.raises(ValueError, match="unknown power band"):
        adapter.normalise(FIXTURE, date(2026, 11, 15))


def test_fetch_checks_licence_and_downloads_aggregate_only(tmp_path: Path) -> None:
    body = (FIXTURE / adapter.FILE_NAME).read_bytes()
    page = (
        "<p>Die Daten sind durch eine Creative Commons Namensnennung 4.0 International Lizenz "
        "lizenziert.</p>"
        '<a href="/DE/Fachthemen/ElektrizitaetundGas/E-Mobilitaet/_DL/'
        'Ladesaeuleninfrastruktur.xlsx?__blob=publicationFile&amp;v=37">x</a>'
        '<a href="https://data.bundesnetzagentur.de/x/Ladesaeulenregister_BNetzA.csv">list</a>'
    )
    requested: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requested.append(str(request.url))
        if request.url.path.endswith("start.html"):
            return httpx.Response(200, text=page)
        return httpx.Response(200, content=body)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        assert adapter.fetch(client, tmp_path) == len(body)
    assert not any("data.bundesnetzagentur.de" in u for u in requested)  # no point list
    meta = json.loads((tmp_path / "_fetch.json").read_text())
    assert meta["licence"] == "CC-BY-4.0"
    assert "Namensnennung 4.0" in meta["licence_text_seen"]


def test_fetch_refuses_without_licence_sentence(tmp_path: Path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="<p>Alle Rechte vorbehalten</p>")

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(adapter.LicenceChanged),
    ):
        adapter.fetch(client, tmp_path)


def test_normalise_cmd_from_fixtures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EV_DATA_DIR", str(tmp_path))
    assert adapter.normalise_cmd(from_fixtures=True) == 0
    lines = (tmp_path / "staging" / "bnetza.charging_stats.jsonl").read_text().splitlines()
    assert len(lines) == len(rows())
    meta = json.loads((tmp_path / "staging" / "bnetza.charging_stats.meta.json").read_text())
    assert meta["status"] == "active" and meta["attribution"] == "Bundesnetzagentur.de"
