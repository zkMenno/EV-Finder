"""EAFO adapter: public recharging points per power level (AFIR) per EU country and year.

Source: the "Recharging points per power level (AFIR) dataset (2020 - <Month YYYY>)" XLSX in
the Downloads section of EAFO's FAQ page (European Commission, DG MOVE). One sheet, columns
`Country, AC/DC, Category, Year, Total Recharging Points`; 27 EU countries, years 2020 to the
current year. AFIR categories (FAQ): slow/medium/fast AC, slow DC < 50 kW, fast DC 50-149 kW,
Level 1 ultra-fast 150-349 kW, Level 2 ultra-fast >= 350 kW.

**Licence: blocked.** The file and page state no dataset licence. The footer links the EC
legal notice: EU-owned content is CC BY 4.0, but "You may be required to clear additional
rights if a specific content ... includes third-party works", and EAFO's FAQ names
Eco-Movement (commercial, data from charge point operators) as its main source. So the
source is `status: blocked` in data/sources.yaml: this loader runs and writes staging, the
sidecar meta says blocked, and nothing may reach a release until the licence is confirmed.
The test fixture therefore has the real layout and labels with **invented numbers**.

**Dates.** A year row is a stock count. For past years we use 31 December (🟡: the file
does not say "end of year"; EAFO's charts label them by year). The newest year is "up to"
the month in the file title, so its period_end is the last day of that month.

**Output** (definition `afir-recharging-point`, confidence medium), per country and date:

- `public-points`, all bands (sum of all seven categories present);
- `public-points-dc`, all DC bands (sum of the four DC categories);
- `public-points-dc` per band for the three DC bands that have a taxonomy id
  (`eafo-dc-50-149`, `eafo-dc-150-349`, `eafo-dc-350-plus`).

AC sub-bands and slow DC have no power_bands row yet (T-024 gap), so they only count in the
totals. Categories missing for a country-year count as 0 in the totals (logged).
"""

from __future__ import annotations

import calendar
import hashlib
import html
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urljoin

import httpx
import openpyxl

from ev_pipeline import net
from ev_pipeline.sources import _common as c
from ev_pipeline.sources.eafo import charging_stats as cs

NAME = "eafo"
DIR = "eafo"
SOURCE_ID = "eafo"  # taxonomy source id (charging_definitions, power_bands)
BASE = "https://alternative-fuels-observatory.ec.europa.eu"
FAQ_URL = f"{BASE}/general-information/frequently-asked-questions"
LEGAL_NOTICE_URL = "https://commission.europa.eu/legal-notice_en"
LINK_MARK = "Recharging points per power level (AFIR) dataset"
FILE_NAME = "eafo_afir_points.xlsx"
DEFINITION = "afir-recharging-point"
LICENCE = "EC reuse policy CC-BY-4.0 for EU-owned content; third-party content unclear"
ATTRIBUTION = "European Alternative Fuels Observatory (European Commission), data from Eco-Movement"
TITLE_RE = re.compile(r"\((\d{4})\s*-\s*([A-Za-z]+)\s+(\d{4})\)")

# AFIR category label prefix -> (current, our power band id or None)
CATEGORIES: dict[str, tuple[str, str | None]] = {
    "Slow AC recharging point": ("ac", None),
    "Medium-speed AC recharging point": ("ac", None),
    "Fast AC recharging point": ("ac", None),
    "Slow DC recharging point": ("dc", None),
    "Fast DC recharging point": ("dc", "eafo-dc-50-149"),
    "Level 1 - Ultra-fast DC recharging point": ("dc", "eafo-dc-150-349"),
    "Level 2 - Ultra-fast DC recharging point": ("dc", "eafo-dc-350-plus"),
}
COUNTRIES = {
    "Austria": "AT",
    "Belgium": "BE",
    "Bulgaria": "BG",
    "Croatia": "HR",
    "Cyprus": "CY",
    "Czech Republic": "CZ",
    "Czechia": "CZ",
    "Denmark": "DK",
    "Estonia": "EE",
    "Finland": "FI",
    "France": "FR",
    "Germany": "DE",
    "Greece": "GR",
    "Hungary": "HU",
    "Ireland": "IE",
    "Italy": "IT",
    "Latvia": "LV",
    "Lithuania": "LT",
    "Luxembourg": "LU",
    "Malta": "MT",
    "Netherlands": "NL",
    "Poland": "PL",
    "Portugal": "PT",
    "Romania": "RO",
    "Slovakia": "SK",
    "Slovenia": "SI",
    "Spain": "ES",
    "Sweden": "SE",
    "United Kingdom": "UK",
    "Norway": "NO",
    "Switzerland": "CH",
    "Iceland": "IS",
    "Liechtenstein": "LI",
    "Turkey": "TR",
    "Türkiye": "TR",
}
MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}


def category(label: str) -> tuple[str, str | None] | None:
    for prefix, info in CATEGORIES.items():
        if label.strip().startswith(prefix):
            return info
    return None


def latest_period(title: str) -> date:
    """'(2020 - May 2026)' -> 2026-05-31."""
    m = TITLE_RE.search(title)
    if not m:
        raise ValueError(f"no '(YYYY - Month YYYY)' range in EAFO file title {title!r}")
    month, year = MONTHS[m.group(2).lower()], int(m.group(3))
    return date(year, month, calendar.monthrange(year, month)[1])


def read_rows(path: Path) -> list[tuple[str, str, str, int, float]]:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        ws = wb.worksheets[0]
        it = ws.iter_rows(values_only=True)
        header = [str(h).strip() if h is not None else "" for h in next(it)]
        need = ["Country", "AC/DC", "Category", "Year", "Total Recharging Points"]
        if header[: len(need)] != need:
            raise ValueError(f"unexpected EAFO header {header[:5]}")
        out = []
        for row in it:
            if not row or row[0] is None or row[4] is None:
                continue
            out.append(
                (
                    str(row[0]).strip(),
                    str(row[1]).strip(),
                    str(row[2]).strip(),
                    int(row[3]),
                    float(row[4]),
                )
            )
        return out
    finally:
        wb.close()


def normalise(
    raw_dir: Path,
    retrieved_at: date,
    log: Counter[str] | None = None,
    taxonomy: cs.Taxonomy | None = None,
) -> cs.StatBuilder:
    log = log if log is not None else Counter()
    meta = c.read_fetch_meta(raw_dir)
    latest = latest_period(meta.get("title") or "")
    path = raw_dir / FILE_NAME
    b = cs.StatBuilder(
        source_id=SOURCE_ID,
        taxonomy=taxonomy or cs.load_taxonomy(),
        retrieved_at=retrieved_at,
        confidence="medium",
        source_record=f"{meta.get('file_label', FILE_NAME)} sha256:{meta.get('sha256', '')[:12]}",
    )
    totals: dict[tuple[str, int], float] = defaultdict(float)
    dc_totals: dict[tuple[str, int], float] = defaultdict(float)
    seen_cats: dict[tuple[str, int], set[str]] = defaultdict(set)
    bands: dict[tuple[str, int, str], tuple[float, str]] = {}
    for country, _acdc, label, year, value in read_rows(path):
        code = COUNTRIES.get(country)
        info = category(label)
        if code is None:
            log["unknown_country"] += 1
            continue
        if info is None:
            log["unknown_category"] += 1
            continue
        current, band = info
        totals[(code, year)] += value
        seen_cats[(code, year)].add(label)
        if current == "dc":
            dc_totals[(code, year)] += value
        if band:
            bands[(code, year, band)] = (value, label)

    def period(year: int) -> date:
        return latest if year == latest.year else date(year, 12, 31)

    note_year = "Year rows read as 31 December; the newest year is as of the file title month."
    for (code, year), total in sorted(totals.items()):
        missing = len(CATEGORIES) - len(seen_cats[(code, year)])
        log["country_years"] += 1
        if missing:
            log["category_cells_missing_counted_as_0"] += missing
        note = note_year + (
            f" {missing} AFIR categories absent in the file, counted as 0." if missing else ""
        )
        b.add(
            country=code,
            period_end=period(year),
            metric_id="public-points",
            value=total,
            unit="count",
            definition_id=DEFINITION,
            source_label="Total Recharging Points (all AFIR categories)",
            notes=note,
        )
        b.add(
            country=code,
            period_end=period(year),
            metric_id="public-points-dc",
            value=dc_totals.get((code, year), 0.0),
            unit="count",
            definition_id=DEFINITION,
            source_label="Total Recharging Points (Category 2, DC)",
            notes=note,
        )
    for (code, year, band), (value, label) in sorted(bands.items()):
        b.add(
            country=code,
            period_end=period(year),
            metric_id="public-points-dc",
            value=value,
            unit="count",
            definition_id=DEFINITION,
            power_band_id=band,
            source_label=label,
            notes=note_year,
        )
    return b


# --- fetch ------------------------------------------------------------------------------


def find_download(page_html: str) -> tuple[str, str]:
    """(absolute URL, decoded file label) of the AFIR points dataset on the FAQ page."""
    for href in re.findall(r'href="([^"]+\.xlsx)"', page_html):
        label = unquote(html.unescape(href)).rsplit("/", 1)[-1]
        if LINK_MARK in label:
            return urljoin(BASE, html.unescape(href)), label
    raise FileNotFoundError("EAFO AFIR recharging points dataset link not found on the FAQ page")


def legal_notice_check(text: str) -> dict[str, Any]:
    plain = " ".join(re.sub(r"<[^>]+>", " ", html.unescape(text)).split())
    return {
        "states_cc_by_4_for_eu_owned_content": "Creative Commons Attribution 4.0" in plain,
        "third_party_exclusion": "third-party works" in plain,
    }


def fetch(client: httpx.Client, target: Path) -> int:
    faq = client.get(FAQ_URL)
    faq.raise_for_status()
    url, label = find_download(faq.text)
    latest_period(label)  # refuse a file whose title we can't date
    legal = client.get(LEGAL_NOTICE_URL)
    legal.raise_for_status()
    check = legal_notice_check(legal.text)
    resp = client.get(url)
    resp.raise_for_status()
    target.mkdir(parents=True, exist_ok=True)
    (target / FILE_NAME).write_bytes(resp.content)
    c.write_fetch_meta(
        target,
        {
            "url": url,
            "file_label": label,
            "title": label,
            "bytes": len(resp.content),
            "sha256": hashlib.sha256(resp.content).hexdigest(),
            "last_modified": resp.headers.get("last-modified"),
            "licence": LICENCE,
            "licence_basis": "No dataset licence on EAFO. Footer -> EC legal notice: content "
            "owned by the EU is CC BY 4.0; third-party works may need permission. EAFO FAQ: "
            "main data provider Eco-Movement (data from CPOs).",
            "legal_notice": {"url": LEGAL_NOTICE_URL, **check},
            "status_note": "blocked: third-party rights unclear (R-02 red flag)",
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
    except (httpx.HTTPError, FileNotFoundError, ValueError) as exc:
        print(f"fetch {NAME}: failed: {exc}")
        return 1
    finally:
        if own:
            client.close()
    meta = c.read_fetch_meta(target)
    c.log_step(
        step="fetch",
        source=NAME,
        input_=meta.get("url", FAQ_URL),
        output=c.rel(target),
        rows_out=size,
        unit="bytes",
        title=meta.get("title"),
        legal_notice=meta.get("legal_notice"),
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
    fetch_meta = c.read_fetch_meta(src)
    cs.write_meta(
        meta_path,
        {
            "source": NAME,
            "taxonomy_source_id": SOURCE_ID,
            "status": status,
            "releasable": status == "active",
            "licence": LICENCE,
            "attribution": ATTRIBUTION,
            "download": {
                k: fetch_meta.get(k)
                for k in ("url", "title", "fetched_at", "sha256", "licence_basis", "legal_notice")
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
        dropped_out_of_validity=b.dropped_out_of_validity,
        **dict(log),
    )
    return 0
