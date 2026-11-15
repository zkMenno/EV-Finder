"""KBA FZ10 adapter on a trimmed copy of the real October 2026 workbook. No network."""

import io
import json
from datetime import date
from pathlib import Path

import httpx
import openpyxl
import pytest

from ev_pipeline.schema_models import Confidence, Country, FactField
from ev_pipeline.sources.kba_fz10 import adapter

FIXTURE = Path(__file__).parent / "fixtures" / "kba_fz10"
XLSX = FIXTURE / "fz10_2026_10.xlsx"


def _by_key(records):
    return {(r.make, r.model): r for r in records}


def test_fixture_is_a_small_sample() -> None:
    wb = openpyxl.load_workbook(XLSX, read_only=True)
    assert wb["FZ 10.1"].max_row <= 100


def test_parse_and_totals() -> None:
    table = adapter.parse_fz10(XLSX)
    assert (table.year, table.month) == (2026, 10)
    assert table.grand_total_ytd == 698230  # NEUZULASSUNGEN INSGESAMT, BEV, Jan-Oct 2026
    makes = {m for m, *_ in table.rows}
    assert not any("ZUSAMMEN" in m for m in makes)  # subtotal rows skipped
    assert not any(model == "SONSTIGE" for _, model, *_ in table.rows)
    # make is carried down from its first row
    assert ("TESLA", "MODEL Y", 2534, 31998) in table.rows
    assert ("VW", "ID.4, ID.5", 3188, 21772) in table.rows


def test_normalise_records() -> None:
    records = adapter.normalise(FIXTURE, date(2026, 11, 15))
    assert records
    for rec in records:
        assert rec.kind == "registration_count"
        assert rec.country == Country.DE
        assert rec.year == 2026
        assert rec.confidence == Confidence.high
        assert rec.source.licence == "dl-de/by-2-0"
        assert "Kraftfahrt-Bundesamt, Flensburg" in rec.source.attribution
        assert rec.specs[FactField.registered_count].unit == "count"
        assert "YTD 2026-01..10" in rec.record_key
        assert rec.specs[FactField.registered_count].value > 0  # "-" rows (=0) dropped
    got = _by_key(records)
    assert got[("TESLA", "MODEL 3")].specs[FactField.registered_count].value == 15466
    assert got[("ALFA ROMEO", "JUNIOR")].specs[FactField.registered_count].value == 495
    assert ("ALFA ROMEO", "GIULIA") not in got  # BEV cell is "-"
    assert ("VW", "UP") in got  # "-" this month but 1 YTD


def test_sum_matches_subtotals() -> None:
    """Per make, emitted + SONSTIGE rows = the make's ZUSAMMEN row (checked in the sheet)."""
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    subtotal = {
        r[1].removesuffix(" ZUSAMMEN"): r[37]
        for r in wb["FZ 10.1"].iter_rows(values_only=True)
        if r[1] and str(r[1]).endswith(" ZUSAMMEN")
    }
    table = adapter.parse_fz10(XLSX)
    others = {"TESLA": 5, "VW": 293, "BYD": 26, "XPENG": 36}
    for make in ("TESLA", "VW", "BYD", "XPENG", "ZEEKR", "ALFA ROMEO"):
        emitted = sum(ytd for m, _, _, ytd in table.rows if m == make)
        assert emitted + others.get(make, 0) == subtotal[make]


def test_cell_int() -> None:
    assert adapter._cell_int("-") == 0
    assert adapter._cell_int(None) == 0
    assert adapter._cell_int(12) == 12


def test_licence_check() -> None:
    assert "Datenlizenz Deutschland" in adapter.check_licence(XLSX)


def _workbook_bytes(licence_line: str) -> bytes:
    wb = openpyxl.load_workbook(XLSX)
    ws = wb["Impressum"]
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and "Datenlizenz" in str(cell.value):
                cell.value = licence_line
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


XLSX_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def test_fetch_falls_back_and_takes_previous_december(tmp_path: Path) -> None:
    body = XLSX.read_bytes()
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        name = request.url.path.rsplit("/", 1)[-1]
        seen.append(name)
        if name in ("fz10_2026_10.xlsx", "fz10_2025_12.xlsx"):
            return httpx.Response(200, content=body, headers={"content-type": XLSX_TYPE})
        return httpx.Response(404, text="<html>nicht gefunden</html>")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        files = adapter.fetch(client, tmp_path, today=date(2026, 11, 15))
    assert seen == ["fz10_2026_11.xlsx", "fz10_2026_10.xlsx", "fz10_2025_12.xlsx"]
    assert [f["file"] for f in files] == ["fz10_2026_10.xlsx", "fz10_2025_12.xlsx"]
    meta = json.loads((tmp_path / "_fetch.json").read_text())
    assert all("Datenlizenz Deutschland" in f["licence_line"] for f in meta["files"])


def test_fetch_refuses_changed_licence(tmp_path: Path) -> None:
    body = _workbook_bytes("Alle Rechte vorbehalten")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=body, headers={"content-type": XLSX_TYPE})

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(adapter.LicenceChanged),
    ):
        adapter.fetch(client, tmp_path, today=date(2026, 11, 15))
    assert not list(tmp_path.glob("*.xlsx"))


def test_normalise_cmd_from_fixtures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EV_DATA_DIR", str(tmp_path))
    assert adapter.normalise_cmd(from_fixtures=True) == 0
    lines = (tmp_path / "staging" / "kba-fz10.records.jsonl").read_text().splitlines()
    assert len(lines) == len(adapter.normalise(FIXTURE, date(2026, 11, 15)))
    log = json.loads((tmp_path / "staging" / "runlog.jsonl").read_text().splitlines()[-1])
    assert log["files"][0]["bev_ytd_grand_total"] == 698230
