"""KBA FZ10 adapter (dl-de/by-2-0): new BEV registrations in DE by Marke x Modellreihe.

FZ10 ("Neuzulassungen von Personenkraftwagen nach Marken und Modellreihen") is a monthly
.xlsx. Sheet `FZ 10.1` has one row per Marke x Modellreihe; for each drive type there are
three columns: the month, Jan.-to-month (YTD) and share. We read the YTD column of
"mit Elektroantrieb (BEV)" so one record = new BEV registrations in that calendar year up to
and including the file's month. `year` is the data year; the period is in `record_key`.

Fetch takes the newest file that exists (current month, then back up to 6 months) plus the
December file of every earlier year from HISTORY_FROM (T-053; its YTD = that full year).
Each file is one data year and one period ("YTD 2019-01..12"), so `registrations[]` gets one
entry per year; years are never summed together. One request at a time, FETCH_SLEEP_S apart.

**Older files (T-053).** Remote names differ by year: `fz10_2021_12.xlsx` from 2021,
`fz10_2018_12_xlsx.xlsx` for 2018-2020 (REMOTE_SUFFIXES are tried in order); they are saved
locally as `fz10_<year>_<month>.xlsx` either way. Files before 2018 are `.xls`
(`fz10_2017_12_xls.xls`, BIFF): not supported (no xlrd), and out of T-053's range. Up to 2020
the BEV group is headed "mit Elektroantrieb" (BEV only then: hybrids incl. plug-ins have their
own group; the 2018-2020 totals 36,062 / 63,281 / 194,163 are KBA's published BEV figures);
from 2021 "mit Elektroantrieb (BEV)". In 2019 and earlier the "others" make is a bare
"SONSTIGE" row, not "SONSTIGE ZUSAMMEN".

Layout gotchas (R-01): the make is only on its model's first row; "-" means 0; "<MARKE>
ZUSAMMEN" rows are subtotals; "SONSTIGE" model rows (and the "SONSTIGE ZUSAMMEN" make) are
"others" and cannot be matched; "NEUZULASSUNGEN INSGESAMT" is the grand total, which we keep
in the run log as a check. Modellreihe is coarser than a commercial name and sometimes joins
two models ("ID.4, ID.5").

Licence check: fetch refuses to keep a file whose Impressum sheet (or, in files without one,
any other non-data sheet: 2019 has the line in "Inhaltsverzeichnis") no longer names the
"Datenlizenz Deutschland". The newest file and the previous year's December must pass or the
fetch fails; an older history file without the line is skipped and listed under `skipped` in
`_fetch.json` (the 2018 file carries only "© Kraftfahrt-Bundesamt"; QUESTIONS.md Q-082).
"""

from __future__ import annotations

import re
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path

import httpx
import openpyxl

from ev_pipeline import net
from ev_pipeline.records import SourceRecord, SpecValue
from ev_pipeline.schema_models import Confidence, Country, FactField, Source
from ev_pipeline.sources import _common as c

NAME = "kba-fz10"
DIR = "kba_fz10"
URL_TEMPLATE = (
    "https://www.kba.de/SharedDocs/Downloads/DE/Statistik/Fahrzeuge/FZ10/"
    "fz10_{year}_{month:02d}{suffix}?__blob=publicationFile"
)
PAGE_URL = "https://www.kba.de/DE/Statistik/Produktkatalog/produkte/Fahrzeuge/fz10/fz10_gentab.html"
REMOTE_SUFFIXES = (".xlsx", "_xlsx.xlsx")
"""Remote file name endings, tried in order (2018-2020 files are `fz10_2019_12_xlsx.xlsx`)."""
LOOKBACK_MONTHS = 6
HISTORY_FROM = 2018
"""First data year fetched (T-053: 'used' = first registered 2018-2024, Q-074)."""
FETCH_SLEEP_S = 1.0
"""Pause between KBA downloads (fair use; one request at a time)."""
LICENCE_MARKER = "Datenlizenz Deutschland"
BEV_HEADERS = ("mit Elektroantrieb (BEV)", "mit Elektroantrieb")
"""BEV group header, newest wording first ("mit Elektroantrieb" up to 2020)."""
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
    suppressed: list[str] = field(default_factory=list)  # "make|model" with a "/" or "." YTD


SUPPRESSED = frozenset({"/", ".", "X", "x"})
"""KBA signs (Zeichenerklärung): "/" not reliable enough (2021-2024 files), "." unknown or
secret, "X" not meaningful / not comparable (MG ROEWE YTD 2021: the make was only shown from
November). Such a cell is no count at all (not 0): the model row is skipped and listed."""


def _suppressed(value: object) -> bool:
    return isinstance(value, str) and value.strip() in SUPPRESSED


def _cell_int(value: object) -> int:
    """'-' (and empty) mean 0 in KBA tables; "/" and "." (no reliable value) count as 0 here,
    callers that emit a count check `_suppressed` first."""
    if value is None or _suppressed(value):
        return 0
    if isinstance(value, int | float):
        return int(value)
    text = str(value).strip().replace(".", "")
    if text in ("", "-"):
        return 0
    return int(text)


def _text(value: object) -> str:
    return " ".join(str(value).split()) if value is not None else ""


def _is_data_sheet(name: str) -> bool:
    return name.replace(" ", "").startswith("FZ10.")


def impressum_text(path: Path) -> str:
    """Text of the Impressum sheet; files without one (2019 and older): every non-data sheet."""
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        names = ["Impressum"] if "Impressum" in wb.sheetnames else wb.sheetnames
        parts = [
            _text(v)
            for name in names
            if not _is_data_sheet(name)
            for row in wb[name].iter_rows(values_only=True)
            for v in row
            if v is not None
        ]
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
        sheet = next(n for n in wb.sheetnames if _is_data_sheet(n))
        rows = list(wb[sheet].iter_rows(values_only=True))
    finally:
        wb.close()

    head, bev_col = _bev_header(rows, path)
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
        if label == OTHERS and not model:  # 2019 and older: the "others" make, one bare row
            table.others_ytd += _cell_int(r[bev_col + 1])
            make = None
            continue
        if label:
            make = label
        if not make or not model:
            continue
        if _suppressed(r[bev_col + 1]):
            table.suppressed.append(f"{make}|{model}")
            continue
        mon, ytd = _cell_int(r[bev_col]), _cell_int(r[bev_col + 1])
        if model == OTHERS:
            table.others_ytd += ytd
            continue
        table.rows.append((make, model, mon, ytd))
    if table.grand_total_ytd is None:
        raise ValueError(f"{path.name}: no 'NEUZULASSUNGEN INSGESAMT' row")
    return table


def _bev_header(rows: list[tuple[object, ...]], path: Path) -> tuple[int, int]:
    """(row, column) of the BEV group header; the newest wording wins if both appear."""
    for header in BEV_HEADERS:
        for i, r in enumerate(rows):
            for j, v in enumerate(r):
                if _text(v) == header:
                    return i, j
    raise ValueError(f"{path.name}: no BEV column ({' / '.join(BEV_HEADERS)})")


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


def remote_urls(year: int, month: int) -> list[str]:
    """Candidate download URLs for one month, in REMOTE_SUFFIXES order."""
    return [URL_TEMPLATE.format(year=year, month=month, suffix=s) for s in REMOTE_SUFFIXES]


def _download(
    client: httpx.Client,
    year: int,
    month: int,
    target: Path,
    sleep: Callable[[], None] | None = None,
) -> tuple[Path, str] | None:
    """Try each remote name; save the first spreadsheet as `fz10_<year>_<month>.xlsx`."""
    for i, url in enumerate(remote_urls(year, month)):
        if i and sleep is not None:
            sleep()
        resp = client.get(url)
        ctype = resp.headers.get("content-type", "")
        if resp.status_code == 404 or "spreadsheetml" not in ctype:
            continue  # KBA answers missing files with an HTML 404 page
        resp.raise_for_status()
        path = target / f"fz10_{year}_{month:02d}.xlsx"
        path.write_bytes(resp.content)
        return path, url
    return None


def fetch(
    client: httpx.Client,
    target: Path,
    today: date | None = None,
    sleep_s: float = FETCH_SLEEP_S,
    history_from: int = HISTORY_FROM,
) -> list[dict]:
    """Download the newest FZ10 file and the December file of every earlier year since
    `history_from` into `target`. Returns the kept files (newest first)."""
    today = today or datetime.now(UTC).date()
    target.mkdir(parents=True, exist_ok=True)
    for old in target.glob("fz10_*.xlsx"):
        old.unlink()
    calls = 0

    def pause() -> None:
        nonlocal calls
        if calls and sleep_s:
            time.sleep(sleep_s)
        calls += 1

    def get(y: int, m: int) -> tuple[Path, str] | None:
        pause()
        return _download(client, y, m, target, pause)

    latest: tuple[int, int] | None = None
    files: list[dict] = []
    for y, m in _months_back(today, LOOKBACK_MONTHS):
        got = get(y, m)
        if got is not None:
            latest = (y, m)
            files.append({"file": got[0].name, "url": got[1], "year": y, "month": m})
            break
    if latest is None:
        raise FileNotFoundError(f"no FZ10 file in the last {LOOKBACK_MONTHS} months")
    missing: list[int] = []
    last_dec = latest[0] if latest[1] == 12 else latest[0] - 1
    for y in range(last_dec, history_from - 1, -1):
        if (y, 12) == latest:
            continue
        got = get(y, 12)
        if got is None:
            missing.append(y)
            continue
        files.append({"file": got[0].name, "url": got[1], "year": y, "month": 12})

    # Licence: the newest file and the previous December must pass (else nothing is kept);
    # an older history file without the line is dropped and listed under `skipped`.
    strict = {latest, (last_dec, 12)}
    kept: list[dict] = []
    skipped: list[dict] = []
    for f in files:
        try:
            f["licence_line"] = check_licence(target / f["file"])
        except LicenceChanged as exc:
            if (f["year"], f["month"]) in strict:
                for g in files:
                    (target / g["file"]).unlink(missing_ok=True)
                raise
            (target / f["file"]).unlink(missing_ok=True)
            skipped.append({**f, "reason": str(exc)})
            continue
        kept.append(f)
    c.write_fetch_meta(
        target,
        {
            "page": PAGE_URL,
            "history_from": history_from,
            "files": kept,
            "skipped": skipped,
            "missing_years": sorted(missing),
        },
    )
    return kept


def fetch_cmd(client: httpx.Client | None = None) -> int:
    target = c.raw_dir(DIR)
    own = client is None
    client = client or net.safe_client(NAME, timeout=120)
    try:
        files = fetch(client, target)
    except (httpx.HTTPError, FileNotFoundError, LicenceChanged) as exc:
        print(f"fetch {NAME}: failed: {exc}")
        return 1
    finally:
        if own:
            client.close()
    meta = c.read_fetch_meta(target)
    c.log_step(
        step="fetch",
        source=NAME,
        input_=", ".join(f["url"] for f in files),
        output=c.rel(target),
        rows_out=len(files),
        licence_lines=[f["licence_line"] for f in files],
        skipped=[{"file": f["file"], "reason": f["reason"]} for f in meta.get("skipped", [])],
        missing_years=meta.get("missing_years", []),
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
                "period": f"{table.year}-01..{table.month:02d}",
                "records": len(recs),
                "bev_ytd_emitted": emitted,
                "bev_ytd_others": table.others_ytd,
                "bev_ytd_grand_total": table.grand_total_ytd,
                "sums_match": emitted + table.others_ytd == table.grand_total_ytd,
                "suppressed_rows": len(table.suppressed),
                # Cars behind "/" / "X" cells (2021-2024): grand total - emitted - others.
                "bev_ytd_unaccounted": (table.grand_total_ytd or 0) - emitted - table.others_ytd,
                "suppressed_examples": table.suppressed[:10],
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
