"""DfT EV charging infrastructure statistics adapter (OGL v3): UK public chargers, aggregates.

Source: "Electric vehicle charging infrastructure statistics: data tables (EVCI)" on gov.uk,
quarterly (1 Jan / 1 Apr / 1 Jul / 1 Oct). Asset URLs change each release, so fetch
resolves them through the gov.uk content API, like `dft-veh`. Two small ODS tables:

- EVCI0101 "Public EV chargers by country and region" (machine-readable sheet `...e`):
  per UK / GB / nation / English region (ONS codes): `EV chargers`, `50kW+ EV chargers`,
  `EV chargers per 100k`, `50kW+ EV chargers per 100k`. From 2025-01-01.
- EVCI0201 "Public EV chargers by power band" (sheet `...b`): Standard (3-<8 kW),
  Standard plus (8-<50 kW), Rapid (50-<150 kW), Ultra-rapid (150 kW+). From 2026-01-01.

Licence: the release page says "licensed under the terms of the Open Government Licence v3.0
except where otherwise stated"; the tables carry no third-party marking. The figures are
operators' open data "collated by Zapmap for use by DfT" and labelled "official statistics in
development", hence confidence medium.

Output (definition `uk-dft-evse-2026`, which counts EV chargers = points):

- `public-points` all bands, per area (UK = region null; others region = ONS code);
- `public-points-dc` for "50kW+ EV chargers" (rapid + ultra-rapid; DC below 50 kW is not in
  this figure, said in `notes`);
- `points-per-100k-people` from "EV chargers per 100k" (ONS mid-year population, DfT's own);
- `public-points-dc` per band for Rapid (`uk-dft-rapid`) and Ultra-rapid
  (`uk-dft-ultra-rapid`). Standard and Standard plus have no power_bands row (T-024) and
  "50kW+ per 100k" no metric, so they're skipped and counted in the run log.

Rows outside the definition's validity window (the taxonomy says from 2026-01-01; EVCI0101
also has 2025 quarters) are dropped and counted, so the series never mixes definitions.
DfT's note markers ("[note 4]") are resolved to the note text from the Notes sheet.
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

import httpx

from ev_pipeline import net
from ev_pipeline.release.gate import RELEASABLE_STATUSES
from ev_pipeline.sources import _common as c
from ev_pipeline.sources.dft_charging import ods
from ev_pipeline.sources.eafo import charging_stats as cs

NAME = "dft-charging"
DIR = "dft_charging"
SOURCE_ID = "dft-ev-charging-infrastructure"  # taxonomy source id
CONTENT_API = (
    "https://www.gov.uk/api/content/government/statistical-data-sets/"
    "electric-vehicle-charging-infrastructure-statistics-data-tables-evci"
)
PAGE_URL = CONTENT_API.replace("/api/content", "")
TABLES = {"evci0101": "evci0101.ods", "evci0201": "evci0201.ods"}
DEFINITION = "uk-dft-evse-2026"
LICENCE = "OGL-UK-3.0"
ATTRIBUTION = (
    "Contains public sector information licensed under the Open Government Licence v3.0 "
    "(Department for Transport, EV charging infrastructure statistics; data collated by Zapmap)."
)
LICENCE_BASIS = (
    "Release page: 'This publication is licensed under the terms of the Open Government "
    "Licence v3.0 except where otherwise stated'; no third-party marking on the EVCI tables."
)
UK_CODE = "K02000001"
NOTE_RE = re.compile(r"note (\d+)")

AREA_KEYS: dict[str, tuple[str, str] | None] = {  # EVCI0101 Key -> (metric, unit)
    "EV chargers": ("public-points", "count"),
    "50kW+ EV chargers": ("public-points-dc", "count"),
    "EV chargers per 100k": ("points-per-100k-people", "per 100k people"),
    "50kW+ EV chargers per 100k": None,  # no metric for it yet
}
BANDS: dict[str, str | None] = {  # EVCI0201 Power Band -> power_bands id
    "Standard": None,
    "Standard plus": None,
    "Rapid": "uk-dft-rapid",
    "Ultra-rapid": "uk-dft-ultra-rapid",
}
DC50_NOTE = "DfT '50kW+' = rapid + ultra-rapid; DC chargers below 50 kW are not in this figure."


def _table(sheets: dict[str, list[list[Any]]], header: list[str]) -> list[dict[str, Any]]:
    """Rows of the first sheet whose header row starts with `header` (machine-readable)."""
    for rows in sheets.values():
        for i, row in enumerate(rows):
            if [str(v).strip() if v is not None else "" for v in row[: len(header)]] == header:
                names = [str(v).strip() for v in row]
                return [dict(zip(names, r, strict=False)) for r in rows[i + 1 :] if r]
    raise ValueError(f"no sheet with header {header}")


def _notes(sheets: dict[str, list[list[Any]]]) -> dict[str, str]:
    try:
        rows = _table(sheets, ["Note number", "Description"])
    except ValueError:
        return {}
    return {
        str(int(float(r["Note number"]))): str(r["Description"]).strip()
        for r in rows
        if r.get("Note number") not in (None, "")
    }


def _date(v: Any) -> date:
    return date.fromisoformat(str(v)[:10])


def _note_text(marker: Any, notes: dict[str, str]) -> str | None:
    nums = NOTE_RE.findall(str(marker or ""))
    texts = [f"[note {n}] {notes[n]}" for n in nums if n in notes]
    return " ".join(texts) or None


def normalise(
    raw_dir: Path,
    retrieved_at: date,
    log: Counter[str] | None = None,
    taxonomy: cs.Taxonomy | None = None,
) -> cs.StatBuilder:
    log = log if log is not None else Counter()
    meta = c.read_fetch_meta(raw_dir)
    files = meta.get("files") or {}
    b = cs.StatBuilder(
        source_id=SOURCE_ID,
        taxonomy=taxonomy or cs.load_taxonomy(),
        retrieved_at=retrieved_at,
        confidence="medium",
        source_record=" + ".join(
            f"{v.get('name', k)} sha256:{str(v.get('sha256', ''))[:12]}"
            for k, v in sorted(files.items())
        )
        or None,
    )
    s0101 = ods.read_sheets(raw_dir / TABLES["evci0101"])
    notes = _notes(s0101)
    for r in _table(
        s0101, ["Date", "Notes", "Country / region code", "Country / region", "Key", "Value"]
    ):
        key, value = str(r.get("Key") or "").strip(), r.get("Value")
        if key not in AREA_KEYS:
            log["evci0101_unknown_key"] += 1
            continue
        target = AREA_KEYS[key]
        if target is None:
            log["evci0101_skipped_no_metric"] += 1
            continue
        if not isinstance(value, float):
            log["evci0101_not_available"] += 1  # "[x]"
            continue
        metric, unit = target
        code, area = str(r["Country / region code"]).strip(), str(r["Country / region"]).strip()
        note = (
            " ".join(
                t
                for t in (
                    DC50_NOTE if metric == "public-points-dc" else None,
                    _note_text(r.get("Notes"), notes),
                )
                if t
            )
            or None
        )
        b.add(
            country="UK",
            region=None if code == UK_CODE else code,
            period_end=_date(r["Date"]),
            metric_id=metric,
            value=round(value, 2) if unit != "count" else value,
            unit=unit,
            definition_id=DEFINITION,
            source_label=f"EVCI0101 {key}: {area}",
            notes=note,
        )

    s0201 = ods.read_sheets(raw_dir / TABLES["evci0201"])
    notes = _notes(s0201)
    for r in _table(s0201, ["Date", "Notes", "Power Band", "Value"]):
        label, value = str(r.get("Power Band") or "").strip(), r.get("Value")
        if label not in BANDS:
            log["evci0201_unknown_band"] += 1
            continue
        band = BANDS[label]
        if band is None:
            log["evci0201_skipped_no_band"] += 1
            continue
        if not isinstance(value, float):
            log["evci0201_not_available"] += 1
            continue
        b.add(
            country="UK",
            period_end=_date(r["Date"]),
            metric_id="public-points-dc",
            value=value,
            unit="count",
            definition_id=DEFINITION,
            power_band_id=band,
            source_label=f"EVCI0201 {label}: United Kingdom",
            notes=_note_text(r.get("Notes"), notes),
        )
    return b


# --- fetch ------------------------------------------------------------------------------


def resolve(client: httpx.Client) -> tuple[dict[str, str], dict[str, Any]]:
    resp = client.get(CONTENT_API)
    resp.raise_for_status()
    doc = resp.json()
    urls: dict[str, str] = {}
    for att in doc.get("details", {}).get("attachments", []):
        name = str(att.get("url", "")).rsplit("/", 1)[-1]
        for table in TABLES:
            if name.lower().startswith(table + "_") and name.lower().endswith(".ods"):
                urls.setdefault(table, att["url"])
    missing = set(TABLES) - set(urls)
    if missing:
        raise FileNotFoundError(f"EVCI tables not listed in the content API: {sorted(missing)}")
    return urls, {"public_updated_at": doc.get("public_updated_at"), "title": doc.get("title")}


def fetch(client: httpx.Client, target: Path) -> int:
    urls, info = resolve(client)
    target.mkdir(parents=True, exist_ok=True)
    files: dict[str, dict[str, Any]] = {}
    total = 0
    for table, url in sorted(urls.items()):
        resp = client.get(url)
        resp.raise_for_status()
        (target / TABLES[table]).write_bytes(resp.content)
        total += len(resp.content)
        files[table] = {
            "url": url,
            "name": url.rsplit("/", 1)[-1],
            "bytes": len(resp.content),
            "sha256": hashlib.sha256(resp.content).hexdigest(),
        }
    c.write_fetch_meta(
        target,
        {
            "content_api": CONTENT_API,
            "page": PAGE_URL,
            "files": files,
            "licence": LICENCE,
            "licence_basis": LICENCE_BASIS,
            "attribution": ATTRIBUTION,
            **info,
        },
    )
    return total


# --- commands ---------------------------------------------------------------------------


def fetch_cmd(client: httpx.Client | None = None) -> int:
    target = c.raw_dir(DIR)
    own = client is None
    client = client or net.safe_client(NAME, timeout=60)
    try:
        size = fetch(client, target)
    except (httpx.HTTPError, FileNotFoundError) as exc:
        print(f"fetch {NAME}: failed: {exc}")
        return 1
    finally:
        if own:
            client.close()
    meta = c.read_fetch_meta(target)
    c.log_step(
        step="fetch",
        source=NAME,
        input_=CONTENT_API,
        output=c.rel(target),
        rows_out=size,
        unit="bytes",
        public_updated_at=meta.get("public_updated_at"),
    )
    return 0


def normalise_cmd(from_fixtures: bool) -> int:
    src = c.FIXTURES_DIR / DIR if from_fixtures else c.raw_dir(DIR)
    if not all((src / f).exists() for f in TABLES.values()):
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
                k: fm.get(k) for k in ("files", "fetched_at", "public_updated_at", "licence_basis")
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
