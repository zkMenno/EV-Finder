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
XLSX_2019 = FIXTURE / "fz10_2019_12.xlsx"  # T-053: old layout, trimmed from the real file


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
    records = [r for r in adapter.normalise(FIXTURE, date(2026, 11, 15)) if r.year == 2026]
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


def _serve(available: dict[str, bytes], seen: list[str]):
    def handler(request: httpx.Request) -> httpx.Response:
        name = request.url.path.rsplit("/", 1)[-1]
        seen.append(name)
        if name in available:
            return httpx.Response(200, content=available[name], headers={"content-type": XLSX_TYPE})
        return httpx.Response(404, text="<html>nicht gefunden</html>")

    return handler


def test_fetch_falls_back_and_takes_every_december_since_history_from(tmp_path: Path) -> None:
    body, old = XLSX.read_bytes(), XLSX_2019.read_bytes()
    seen: list[str] = []
    available = {
        "fz10_2026_10.xlsx": body,
        "fz10_2025_12.xlsx": body,
        "fz10_2021_12.xlsx": body,
        "fz10_2020_12_xlsx.xlsx": old,  # 2018-2020: other remote name
        "fz10_2019_12_xlsx.xlsx": old,
    }
    with httpx.Client(transport=httpx.MockTransport(_serve(available, seen))) as client:
        files = adapter.fetch(client, tmp_path, today=date(2026, 11, 15), sleep_s=0)
    assert seen[:3] == ["fz10_2026_11.xlsx", "fz10_2026_11_xlsx.xlsx", "fz10_2026_10.xlsx"]
    assert seen[3:5] == ["fz10_2025_12.xlsx", "fz10_2024_12.xlsx"]
    assert [(f["year"], f["month"]) for f in files] == [
        (2026, 10), (2025, 12), (2021, 12), (2020, 12), (2019, 12)
    ]  # fmt: skip
    # saved under one local name pattern whatever the remote name was
    assert sorted(p.name for p in tmp_path.glob("fz10_*.xlsx")) == [
        "fz10_2019_12.xlsx", "fz10_2020_12.xlsx", "fz10_2021_12.xlsx",
        "fz10_2025_12.xlsx", "fz10_2026_10.xlsx",
    ]  # fmt: skip
    assert files[3]["url"].split("?")[0].endswith("fz10_2020_12_xlsx.xlsx")
    meta = json.loads((tmp_path / "_fetch.json").read_text())
    assert all("Datenlizenz Deutschland" in f["licence_line"] for f in meta["files"])
    assert meta["missing_years"] == [2018, 2022, 2023, 2024]
    assert meta["history_from"] == adapter.HISTORY_FROM == 2018


def test_fetch_pauses_between_requests(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sleeps: list[float] = []
    monkeypatch.setattr(adapter.time, "sleep", sleeps.append)
    seen: list[str] = []
    available = {"fz10_2026_10.xlsx": XLSX.read_bytes()}
    with httpx.Client(transport=httpx.MockTransport(_serve(available, seen))) as client:
        adapter.fetch(client, tmp_path, today=date(2026, 10, 15), sleep_s=1.0, history_from=2025)
    assert len(seen) == 3 and sleeps == [1.0, 1.0]  # 2026_10 hit, 2025_12 tried twice


def test_fetch_skips_old_file_without_licence_line(tmp_path: Path) -> None:
    """An old history file with no licence text (the real 2018 file) is dropped, not fatal."""
    seen: list[str] = []
    available = {
        "fz10_2026_10.xlsx": XLSX.read_bytes(),
        "fz10_2025_12.xlsx": XLSX.read_bytes(),
        "fz10_2024_12.xlsx": _workbook_bytes("© Kraftfahrt-Bundesamt, Flensburg"),
    }
    with httpx.Client(transport=httpx.MockTransport(_serve(available, seen))) as client:
        files = adapter.fetch(client, tmp_path, today=date(2026, 11, 15), sleep_s=0)
    assert [f["year"] for f in files] == [2026, 2025]
    assert not (tmp_path / "fz10_2024_12.xlsx").exists()
    meta = json.loads((tmp_path / "_fetch.json").read_text())
    assert [s["year"] for s in meta["skipped"]] == [2024]


def test_fetch_refuses_when_previous_december_lost_its_licence(tmp_path: Path) -> None:
    seen: list[str] = []
    available = {
        "fz10_2026_10.xlsx": XLSX.read_bytes(),
        "fz10_2025_12.xlsx": _workbook_bytes("Alle Rechte vorbehalten"),
    }
    with (
        httpx.Client(transport=httpx.MockTransport(_serve(available, seen))) as client,
        pytest.raises(adapter.LicenceChanged),
    ):
        adapter.fetch(client, tmp_path, today=date(2026, 11, 15), sleep_s=0)
    assert not list(tmp_path.glob("*.xlsx"))


# --- T-053: the 2018-2020 layout ------------------------------------------------------------


def test_old_layout_parses_with_plain_elektroantrieb_header() -> None:
    table = adapter.parse_fz10(XLSX_2019)
    assert (table.year, table.month) == (2019, 12)
    assert table.grand_total_ytd == 63281  # KBA's published BEV total for 2019
    assert ("NISSAN", "LEAF", 134, 2620) in table.rows
    assert ("RENAULT", "ZOE", 780, 9431) in table.rows
    assert ("TESLA", "MODEL 3", 926, 9013) in table.rows
    assert not any(model == "SONSTIGE" for _, model, *_ in table.rows)
    # TESLA SONSTIGE (1) + the bare "SONSTIGE" make row of 2019 (959)
    assert table.others_ytd == 1 + 959


def test_old_layout_licence_is_in_the_contents_sheet() -> None:
    wb = openpyxl.load_workbook(XLSX_2019, read_only=True)
    assert "Impressum" not in wb.sheetnames
    assert "Datenlizenz Deutschland" in adapter.check_licence(XLSX_2019)


def test_one_period_per_year() -> None:
    """Each December file is one data year and one period: registrations[] gets one entry
    per year, never a sum across years."""
    records = adapter.normalise(FIXTURE, date(2026, 11, 15))
    by_year: dict[int, set[str]] = {}
    for r in records:
        assert r.year is not None
        by_year.setdefault(r.year, set()).add(r.record_key.split(":")[1])
    assert by_year == {2019: {"YTD 2019-01..12"}, 2026: {"YTD 2026-01..10"}}
    zoe = [r for r in records if (r.make, r.model, r.year) == ("RENAULT", "ZOE", 2019)]
    assert [r.specs[FactField.registered_count].value for r in zoe] == [9431]


def test_bev_header_prefers_the_bev_wording() -> None:
    rows = [("x", "mit Elektroantrieb", None), (None, None, "mit Elektroantrieb (BEV)")]
    assert adapter._bev_header(rows, XLSX) == (1, 2)
    with pytest.raises(ValueError):
        adapter._bev_header([("Insgesamt",)], XLSX)


def test_fetch_refuses_changed_licence(tmp_path: Path) -> None:
    body = _workbook_bytes("Alle Rechte vorbehalten")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=body, headers={"content-type": XLSX_TYPE})

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(adapter.LicenceChanged),
    ):
        adapter.fetch(client, tmp_path, today=date(2026, 11, 15), sleep_s=0)
    assert not list(tmp_path.glob("*.xlsx"))


def test_normalise_cmd_from_fixtures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EV_DATA_DIR", str(tmp_path))
    assert adapter.normalise_cmd(from_fixtures=True) == 0
    lines = (tmp_path / "staging" / "kba-fz10.records.jsonl").read_text().splitlines()
    assert len(lines) == len(adapter.normalise(FIXTURE, date(2026, 11, 15)))
    log = json.loads((tmp_path / "staging" / "runlog.jsonl").read_text().splitlines()[-1])
    by_file = {f["file"]: f for f in log["files"]}
    assert by_file["fz10_2026_10.xlsx"]["bev_ytd_grand_total"] == 698230
    assert by_file["fz10_2019_12.xlsx"]["period"] == "2019-01..12"


def test_suppressed_cells_are_no_count(tmp_path: Path) -> None:
    """KBA "/" (not reliable), "." (secret) and "X" (not comparable) are skipped and listed,
    never read as 0 or as a number."""
    wb = openpyxl.load_workbook(XLSX_2019)
    ws = wb["FZ 10.1"]
    marks = {"LEAF": "/", "ZOE": "X", "MODEL S": "."}
    for row in ws.iter_rows():
        if row[2].value in marks:
            row[13].value = marks[row[2].value]  # BEV Jan.-Dez. column
    path = tmp_path / "fz10_2019_12.xlsx"
    wb.save(path)
    table = adapter.parse_fz10(path)
    assert sorted(table.suppressed) == ["NISSAN|LEAF", "RENAULT|ZOE", "TESLA|MODEL S"]
    models = {model for _, model, *_ in table.rows}
    assert not models & set(marks)
    assert ("TESLA", "MODEL 3", 926, 9013) in table.rows
