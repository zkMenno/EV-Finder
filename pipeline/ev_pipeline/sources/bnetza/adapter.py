"""Bundesnetzagentur adapter (CC BY 4.0): public charging points in Germany, aggregates only.

Source: "Ladeinfrastruktur (LIS) in Zahlen" (`Ladesaeuleninfrastruktur.xlsx`), linked from the
Bundesnetzagentur Ladesäulenkarte page. Quarterly history since 2017 (as-of dates 1 Jan / 1 Apr /
1 Jul / 1 Oct), built from operators' notifications under the Ladesäulenverordnung. The page
states: "Die Daten sind durch eine Creative Commons Namensnennung 4.0 International Lizenz
lizenziert ... Als Namensnennung für Daten dieser Internetseite ist Bundesnetzagentur.de zu
verwenden." fetch refuses to download if that sentence is gone.

Decision 012: aggregates only. We never fetch the point-level register (the CSV/XLSX list
on data.bundesnetzagentur.de); its host is not even in the allowlist.

Sheets read (found by their number prefix, so a renamed title still works):

- `3.1 Ladepunkte`: Normalladepunkte / Schnellladepunkte / Ladepunkte insgesamt per date;
- `3.2 Ladeleistung`: total rated power (kW) per date;
- `4.1 Ladepunkte je BL`: NLP / SLP / gesamt per Bundesland per date;
- `4.2 Ladeleistung je BL`: kW gesamt per Bundesland per date.

Output (definition `de-bnetza-ladepunkt`, confidence high): `public-points` for all bands,
`de-bnetza-normal` (≤ 22 kW) and `de-bnetza-fast` (> 22 kW); `installed-kw` for all bands.
Region = ISO 3166-2 code of the state (`DE-BY`), state name in `source_label`. The state
"Summe" row is checked against the national figure (run log) and not emitted twice.

Not read: `3.3 Leistungsklassen` (eight BNetzA power classes, no power_bands rows yet; see
QUESTIONS) and `4.3` (district level; more detail than the country page needs). Installed kW
is the summed rated power of the charging devices, not per point (BNetzA footnote).
"""

from __future__ import annotations

import hashlib
import html
import re
from collections import Counter
from collections.abc import Iterator
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx
import openpyxl

from ev_pipeline import net
from ev_pipeline.release.gate import RELEASABLE_STATUSES
from ev_pipeline.sources import _common as c
from ev_pipeline.sources.eafo import charging_stats as cs

NAME = "bnetza"
DIR = "bnetza"
STAGING_SUFFIX = ".charging_stats.jsonl"  # refresh runner: where normalise writes (T-025)
SOURCE_ID = "bnetza-ladesaeulenregister"  # taxonomy source id
PAGE_URL = (
    "https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/E-Mobilitaet/"
    "Ladesaeulenkarte/start.html"
)
BASE = "https://www.bundesnetzagentur.de"
LINK_RE = re.compile(r'href="([^"]*/Ladesaeuleninfrastruktur\.xlsx[^"]*)"')
FILE_NAME = "Ladesaeuleninfrastruktur.xlsx"
DEFINITION = "de-bnetza-ladepunkt"
LICENCE = "CC-BY-4.0"
ATTRIBUTION = "Bundesnetzagentur.de"
LICENCE_SENTENCE = "Creative Commons Namensnennung 4.0 International"

POINT_ROWS = {  # sheet 3.1 row label -> power band (None = all)
    "Normalladepunkte": "de-bnetza-normal",
    "Schnellladepunkte": "de-bnetza-fast",
    "Ladepunkte insgesamt": None,
}
STATE_COLS = {"NLP": "de-bnetza-normal", "SLP": "de-bnetza-fast", "gesamt": None}
STATES = {
    "Baden-Württemberg": "DE-BW",
    "Bayern": "DE-BY",
    "Berlin": "DE-BE",
    "Brandenburg": "DE-BB",
    "Bremen": "DE-HB",
    "Hamburg": "DE-HH",
    "Hessen": "DE-HE",
    "Mecklenburg-Vorpommern": "DE-MV",
    "Niedersachsen": "DE-NI",
    "Nordrhein-Westfalen": "DE-NW",
    "Rheinland-Pfalz": "DE-RP",
    "Saarland": "DE-SL",
    "Sachsen": "DE-SN",
    "Sachsen-Anhalt": "DE-ST",
    "Schleswig-Holstein": "DE-SH",
    "Thüringen": "DE-TH",
}
TOTAL_ROW = "Summe"


def _sheet(wb: openpyxl.Workbook, prefix: str):
    for ws in wb.worksheets:
        if ws.title.strip().startswith(prefix + " "):
            return ws
    raise ValueError(f"BNetzA workbook has no sheet starting with {prefix!r}")


def _rows(ws) -> list[tuple[Any, ...]]:
    return [tuple(r) for r in ws.iter_rows(values_only=True)]


def _is_date(v: object) -> bool:
    return isinstance(v, datetime | date)


def _date_header(rows: list[tuple[Any, ...]]) -> int:
    for i, row in enumerate(rows):
        if sum(1 for v in row if _is_date(v)) >= 2:
            return i
    raise ValueError("no date header row found")


def series_rows(rows: list[tuple[Any, ...]]) -> Iterator[tuple[str, date, float]]:
    """Sheets 3.x: (row label, date, value) for each labelled row under the date header."""
    h = _date_header(rows)
    dates = {
        j: v.date() if isinstance(v, datetime) else v for j, v in enumerate(rows[h]) if _is_date(v)
    }
    first = min(dates)
    label_col = first - 1
    for row in rows[h:]:
        label = row[label_col] if len(row) > label_col else None
        values = [(j, row[j]) for j in dates if j < len(row) and isinstance(row[j], int | float)]
        if not values:
            continue
        name = str(label).strip() if label is not None else ""
        for j, v in values:
            yield name, dates[j], float(v)


def state_rows(rows: list[tuple[Any, ...]]) -> Iterator[tuple[str, date, str, float]]:
    """Sheets 4.x: (state, date, sub-column label, value). Dates span their sub-columns."""
    h = _date_header(rows)
    head, sub = rows[h], rows[h + 1]
    col_date: dict[int, date] = {}
    current: date | None = None
    for j in range(len(sub)):
        v = head[j] if j < len(head) else None
        if _is_date(v):
            current = v.date() if isinstance(v, datetime) else v
        if current is not None and sub[j] is not None:
            col_date[j] = current
    label_col = min(col_date) - 1
    for row in rows[h + 2 :]:
        name = row[label_col] if len(row) > label_col else None
        if not isinstance(name, str) or not name.strip():
            continue
        for j, d in col_date.items():
            v = row[j] if j < len(row) else None
            if isinstance(v, int | float):
                yield name.strip(), d, str(sub[j]).strip(), float(v)


def stand(rows: list[tuple[Any, ...]]) -> str | None:
    for row in rows[:6]:
        for v in row:
            if isinstance(v, str) and v.startswith("Stand:"):
                return v.removeprefix("Stand:").strip()
    return None


def normalise(
    raw_dir: Path,
    retrieved_at: date,
    log: Counter[str] | None = None,
    taxonomy: cs.Taxonomy | None = None,
) -> cs.StatBuilder:
    log = log if log is not None else Counter()
    meta = c.read_fetch_meta(raw_dir)
    b = cs.StatBuilder(
        source_id=SOURCE_ID,
        taxonomy=taxonomy or cs.load_taxonomy(),
        retrieved_at=retrieved_at,
        confidence="high",
        source_record=f"{FILE_NAME} sha256:{meta.get('sha256', '')[:12]}",
    )
    wb = openpyxl.load_workbook(raw_dir / FILE_NAME, read_only=True, data_only=True)
    try:
        s31, s32 = _rows(_sheet(wb, "3.1")), _rows(_sheet(wb, "3.2"))
        s41, s42 = _rows(_sheet(wb, "4.1")), _rows(_sheet(wb, "4.2"))
    finally:
        wb.close()
    national: dict[tuple[date, str | None], float] = {}

    for label, d, v in series_rows(s31):
        if label not in POINT_ROWS:
            continue
        band = POINT_ROWS[label]
        national[(d, band)] = v
        b.add(
            country="DE",
            period_end=d,
            metric_id="public-points",
            value=v,
            unit="count",
            definition_id=DEFINITION,
            power_band_id=band,
            source_label=f"3.1 {label}",
        )
    kw_seen = False
    for label, d, v in series_rows(s32):
        if label == "Ladeleistung":
            kw_seen = True
            b.add(
                country="DE",
                period_end=d,
                metric_id="installed-kw",
                value=round(v, 1),
                unit="kW",
                definition_id=DEFINITION,
                source_label="3.2 Ladeleistung insgesamt",
                notes="Summed rated power of the charging devices (BNetzA), not per point.",
            )
    if not kw_seen:
        log["installed_kw_row_missing"] += 1

    for state, d, col, v in state_rows(s41):
        if col not in STATE_COLS:
            continue
        band = STATE_COLS[col]
        if state == TOTAL_ROW:
            nat = national.get((d, band))
            if nat is not None and nat != v:
                log["state_sum_mismatch"] += 1
            continue
        code = STATES.get(state)
        if code is None:
            log["unknown_state"] += 1
            continue
        b.add(
            country="DE",
            region=code,
            period_end=d,
            metric_id="public-points",
            value=v,
            unit="count",
            definition_id=DEFINITION,
            power_band_id=band,
            source_label=f"4.1 {state} {col}",
        )
    for state, d, col, v in state_rows(s42):
        if col != "kW gesamt" or state == TOTAL_ROW:
            continue
        code = STATES.get(state)
        if code is None:
            log["unknown_state"] += 1
            continue
        b.add(
            country="DE",
            region=code,
            period_end=d,
            metric_id="installed-kw",
            value=round(v, 1),
            unit="kW",
            definition_id=DEFINITION,
            source_label=f"4.2 {state} kW gesamt",
            notes="Summed rated power of the charging devices (BNetzA), not per point.",
        )
    b.report_date = stand(s31)
    return b


# --- fetch ------------------------------------------------------------------------------


def find_download(page_html: str) -> str:
    m = LINK_RE.search(page_html)
    if not m:
        raise FileNotFoundError("Ladesaeuleninfrastruktur.xlsx link not found on the BNetzA page")
    return urljoin(BASE, html.unescape(m.group(1)))


class LicenceChanged(RuntimeError):
    pass


def fetch(client: httpx.Client, target: Path) -> int:
    page = client.get(PAGE_URL)
    page.raise_for_status()
    plain = " ".join(re.sub(r"<[^>]+>", " ", html.unescape(page.text)).split())
    if LICENCE_SENTENCE not in plain:
        raise LicenceChanged("BNetzA page no longer states the CC BY 4.0 licence; not fetching")
    i = plain.find(LICENCE_SENTENCE)
    licence_text = plain[max(0, i - 60) : i + 260]
    url = find_download(page.text)
    resp = client.get(url)
    resp.raise_for_status()
    target.mkdir(parents=True, exist_ok=True)
    (target / FILE_NAME).write_bytes(resp.content)
    c.write_fetch_meta(
        target,
        {
            "page": PAGE_URL,
            "url": url,
            "file": FILE_NAME,
            "bytes": len(resp.content),
            "sha256": hashlib.sha256(resp.content).hexdigest(),
            "licence": LICENCE,
            "attribution": ATTRIBUTION,
            "licence_text_seen": licence_text,
        },
    )
    return len(resp.content)


# --- commands ---------------------------------------------------------------------------


def fetch_cmd(client: httpx.Client | None = None) -> int:
    target = c.raw_dir(DIR)
    own = client is None
    client = client or net.safe_client(NAME, timeout=60)
    try:
        size = fetch(client, target)
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
        input_=meta.get("url", PAGE_URL),
        output=c.rel(target),
        rows_out=size,
        unit="bytes",
        licence=LICENCE,
    )
    return 0


def normalise_cmd(from_fixtures: bool) -> int:
    src = c.FIXTURES_DIR / DIR if from_fixtures else c.raw_dir(DIR)
    if not (src / FILE_NAME).exists():
        print(f"normalise {NAME}: no data in {src} (run `ev fetch {NAME}` first)")
        return 1
    log: Counter[str] = Counter()
    b = normalise(src, c.retrieved_at_for(src), log)
    out, meta_path = cs.staging_paths(NAME)
    rows = cs.write_stats(b.sorted_rows(), out)
    status = cs.source_status(NAME)
    fm = c.read_fetch_meta(src)
    cs.write_meta(
        meta_path,
        {
            "source": NAME,
            "taxonomy_source_id": SOURCE_ID,
            "status": status,
            "releasable": status in RELEASABLE_STATUSES,
            "licence": LICENCE,
            "attribution": ATTRIBUTION,
            "download": {
                k: fm.get(k) for k in ("url", "fetched_at", "sha256", "licence_text_seen")
            },
            "definition_id": DEFINITION,
            "rows": rows,
            "from_fixtures": from_fixtures,
        },
    )
    c.log_step(
        step="normalise",
        source=NAME,
        input_=c.rel(src),
        output=c.rel(out),
        rows_out=rows,
        from_fixtures=from_fixtures,
        status=status,
        report_date=b.report_date,
        dropped_out_of_validity=b.dropped_out_of_validity,
        **dict(log),
    )
    return 0
