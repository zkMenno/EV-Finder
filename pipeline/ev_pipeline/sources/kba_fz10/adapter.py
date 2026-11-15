"""KBA FZ10 adapter (dl-de/by-2-0): new BEV registrations in DE by Marke x Modellreihe.

FZ10 ("Neuzulassungen von Personenkraftwagen nach Marken und Modellreihen") is a monthly
.xlsx. Sheet `FZ 10.1` has one row per Marke x Modellreihe; for each drive type there are
three columns: the month, Jan.-to-month (YTD) and share. We read the YTD column of
"mit Elektroantrieb (BEV)" so one record = new BEV registrations in that calendar year up to
and including the file's month. `year` is the data year; the period is in `record_key`.

Fetch takes the newest file that exists (current month, then back up to 6 months) plus the
December file of the previous year (its YTD = the full previous year). Different years never
overlap, so counts from both files can be summed per model without double counting.

Layout gotchas (R-01): the make is only on its model's first row; "-" means 0; "<MARKE>
ZUSAMMEN" rows are subtotals; "SONSTIGE" model rows (and the "SONSTIGE ZUSAMMEN" make) are
"others" and cannot be matched; "NEUZULASSUNGEN INSGESAMT" is the grand total, which we keep
in the run log as a check. Modellreihe is coarser than a commercial name and sometimes joins
two models ("ID.4, ID.5").

Licence check: fetch refuses to keep a file whose Impressum sheet no longer names the
"Datenlizenz Deutschland".
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path

import httpx
import openpyxl

from ev_pipeline.records import SourceRecord, SpecValue
from ev_pipeline.schema_models import Confidence, Country, FactField, Source
from ev_pipeline.sources import _common as c

NAME = "kba-fz10"
DIR = "kba_fz10"
URL_TEMPLATE = (
    "https://www.kba.de/SharedDocs/Downloads/DE/Statistik/Fahrzeuge/FZ10/"
    "fz10_{year}_{month:02d}.xlsx?__blob=publicationFile"
)
PAGE_URL = "https://www.kba.de/DE/Statistik/Produktkatalog/produkte/Fahrzeuge/fz10/fz10_gentab.html"
LOOKBACK_MONTHS = 6
LICENCE_MARKER = "Datenlizenz Deutschland"
BEV_HEADER = "mit Elektroantrieb (BEV)"
FILE_RE = re.compile(r"^fz10_(\d{4})_(\d{2})\.xlsx$")
OTHERS = "SONSTIGE"

SOURCE = Source(
    id="kba-fz10",
    name="KBA FZ10 new registrations by make and model series",
    url=PAGE_URL,
    licence="dl-de/by-2-0",
    attribution="© Kraftfahrt-Bundesamt, Flensburg. Datenlizenz Deutschland – Namensnennung "
    "– Version 2.0 (FZ10, Neuzulassungen nach Marken und Modellreihen).",
)


class LicenceChanged(RuntimeError):
    """The Impressum no longer names the Datenlizenz Deutschland."""


@dataclass
class Fz10Table:
    year: int
    month: int
    rows: list[tuple[str, str, int, int]] = field(default_factory=list)  # make, model, mon, ytd
    others_ytd: int = 0  # SONSTIGE model rows and makes without model rows
    grand_total_ytd: int | None = None


def _cell_int(value: object) -> int:
    """'-' (and empty) mean 0 in KBA tables."""
    if value is None:
        return 0
    if isinstance(value, int | float):
        return int(value)
    text = str(value).strip().replace(".", "")
    if text in ("", "-"):
        return 0
    return int(text)


def _text(value: object) -> str:
    return " ".join(str(value).split()) if value is not None else ""


def impressum_text(path: Path) -> str:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        ws = wb["Impressum"]
        parts = [_text(v) for row in ws.iter_rows(values_only=True) for v in row if v is not None]
    finally:
        wb.close()
    return "\n".join(parts)


def check_licence(path: Path) -> str:
    """Return the licence line from the Impressum; raise LicenceChanged if it is gone."""
    text = impressum_text(path)
    for line in text.splitlines():
        if LICENCE_MARKER in line:
            return line
    raise LicenceChanged(f"{path.name}: Impressum does not mention '{LICENCE_MARKER}'")


def parse_fz10(path: Path) -> Fz10Table:
    m = FILE_RE.match(path.name)
    if not m:
        raise ValueError(f"unexpected FZ10 file name: {path.name}")
    table = Fz10Table(year=int(m.group(1)), month=int(m.group(2)))
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        sheet = next(n for n in wb.sheetnames if n.replace(" ", "").startswith("FZ10."))
        rows = list(wb[sheet].iter_rows(values_only=True))
    finally:
        wb.close()

    head = next(i for i, r in enumerate(rows) if any(_text(v) == BEV_HEADER for v in r))
    bev_col = next(j for j, v in enumerate(rows[head]) if _text(v) == BEV_HEADER)
    sub = rows[head + 1]
    if "Anteil" not in _text(sub[bev_col + 2]):
        raise ValueError(f"{path.name}: unexpected sub-header next to the BEV column")
    # 'Marke' sits in the group header row in some years and the sub-header row in others.
    make_col = next(j for r in (rows[head], sub) for j, v in enumerate(r) if _text(v) == "Marke")
    model_col = make_col + 1

    make: str | None = None
    for r in rows[head + 2 :]:
        label = _text(r[make_col]) if len(r) > make_col else ""
        model = _text(r[model_col]) if len(r) > model_col else ""
        if label.startswith("NEUZULASSUNGEN INSGESAMT"):
            table.grand_total_ytd = _cell_int(r[bev_col + 1])
            break
        if label.endswith(" ZUSAMMEN"):
            if label == f"{OTHERS} ZUSAMMEN":
                table.others_ytd += _cell_int(r[bev_col + 1])
            make = None
            continue
        if label:
            make = label
        if not make or not model:
            continue
        mon, ytd = _cell_int(r[bev_col]), _cell_int(r[bev_col + 1])
        if model == OTHERS:
            table.others_ytd += ytd
            continue
        table.rows.append((make, model, mon, ytd))
    if table.grand_total_ytd is None:
        raise ValueError(f"{path.name}: no 'NEUZULASSUNGEN INSGESAMT' row")
    return table


def records_from_table(table: Fz10Table, retrieved_at: date) -> list[SourceRecord]:
    period = f"YTD {table.year}-01..{table.month:02d}"
    out: list[SourceRecord] = []
    for make, model, _mon, ytd in table.rows:
        if ytd <= 0:
            continue
        out.append(
            SourceRecord(
                source=SOURCE,
                record_key=f"fz10_{table.year}_{table.month:02d}:{period}:{make}|{model}",
                kind="registration_count",
                make=make,
                model=model,
                year=table.year,
                country=Country.DE,
                specs={FactField.registered_count: SpecValue(value=ytd, unit="count")},
                retrieved_at=retrieved_at,
                confidence=Confidence.high,
            )
        )
    return out


def normalise(raw_dir: Path, retrieved_at: date) -> list[SourceRecord]:
    records: list[SourceRecord] = []
    for path in sorted(raw_dir.glob("fz10_*.xlsx")):
        records.extend(records_from_table(parse_fz10(path), retrieved_at))
    return records


# --------------------------------------------------------------------------- fetch


def _months_back(today: date, n: int) -> list[tuple[int, int]]:
    y, m = today.year, today.month
    out = []
    for _ in range(n + 1):
        out.append((y, m))
        y, m = (y, m - 1) if m > 1 else (y - 1, 12)
    return out


def _download(client: httpx.Client, year: int, month: int, target: Path) -> Path | None:
    url = URL_TEMPLATE.format(year=year, month=month)
    resp = client.get(url)
    ctype = resp.headers.get("content-type", "")
    if resp.status_code == 404 or "spreadsheetml" not in ctype:
        return None  # KBA answers missing files with an HTML 404 page
    resp.raise_for_status()
    path = target / f"fz10_{year}_{month:02d}.xlsx"
    path.write_bytes(resp.content)
    return path


def fetch(client: httpx.Client, target: Path, today: date | None = None) -> list[dict]:
    """Download the newest FZ10 file and the previous year's December file into `target`."""
    today = today or datetime.now(UTC).date()
    target.mkdir(parents=True, exist_ok=True)
    for old in target.glob("fz10_*.xlsx"):
        old.unlink()
    latest: tuple[int, int] | None = None
    files: list[dict] = []
    for y, m in _months_back(today, LOOKBACK_MONTHS):
        path = _download(client, y, m, target)
        if path is not None:
            latest = (y, m)
            files.append({"file": path.name, "url": URL_TEMPLATE.format(year=y, month=m)})
            break
    if latest is None:
        raise FileNotFoundError(f"no FZ10 file in the last {LOOKBACK_MONTHS} months")
    if latest[1] != 12:
        prev = (latest[0] - 1, 12)
        path = _download(client, *prev, target)
        if path is not None:
            files.append({"file": path.name, "url": URL_TEMPLATE.format(year=prev[0], month=12)})
    for f in files:
        try:
            f["licence_line"] = check_licence(target / f["file"])
        except LicenceChanged:
            for g in files:
                (target / g["file"]).unlink(missing_ok=True)
            raise
    c.write_fetch_meta(target, {"page": PAGE_URL, "files": files})
    return files


def fetch_cmd(client: httpx.Client | None = None) -> int:
    target = c.raw_dir(DIR)
    own = client is None
    client = client or httpx.Client(timeout=120, headers={"User-Agent": c.USER_AGENT})
    try:
        files = fetch(client, target)
    except (httpx.HTTPError, FileNotFoundError, LicenceChanged) as exc:
        print(f"fetch {NAME}: failed: {exc}")
        return 1
    finally:
        if own:
            client.close()
    c.log_step(
        step="fetch",
        source=NAME,
        input_=", ".join(f["url"] for f in files),
        output=c.rel(target),
        rows_out=len(files),
        licence_lines=[f["licence_line"] for f in files],
    )
    return 0


def normalise_cmd(from_fixtures: bool) -> int:
    src = c.FIXTURES_DIR / DIR if from_fixtures else c.raw_dir(DIR)
    files = sorted(src.glob("fz10_*.xlsx"))
    if not files:
        print(f"normalise {NAME}: no data in {src} (run `ev fetch {NAME}` first)")
        return 1
    retrieved = c.retrieved_at_for(src)
    records: list[SourceRecord] = []
    checks = []
    for path in files:
        table = parse_fz10(path)
        recs = records_from_table(table, retrieved)
        records.extend(recs)
        emitted = sum(int(r.specs[FactField.registered_count].value) for r in recs)
        checks.append(
            {
                "file": path.name,
                "records": len(recs),
                "bev_ytd_emitted": emitted,
                "bev_ytd_others": table.others_ytd,
                "bev_ytd_grand_total": table.grand_total_ytd,
                "sums_match": emitted + table.others_ytd == table.grand_total_ytd,
            }
        )
    out = c.staging_dir() / f"{NAME}.records.jsonl"
    rows = c.write_records(records, out)
    c.log_step(
        step="normalise",
        source=NAME,
        input_=c.rel(src),
        output=c.rel(out),
        rows_out=rows,
        from_fixtures=from_fixtures,
        files=checks,
    )
    return 0
