"""EEA new-car registrations per type-approval version, EU-wide (counts only, T-073).

Decision 049 (Q-039 default): EEA stays counts-only. This module pulls, per data year, the
number of new battery-electric registrations in every reporting country summed per
type-approval number (TAN) x variant (Va) x version (Ve) x make. No spec column is selected,
so nothing here can become a spec fact; the counts only

- corroborate a candidate variant built from RDW TGK versions ("sold in the EU, n cars"), and
- weight the "% of EU registrations" coverage figure (`ev variants propose`).

Join to RDW TGK: EEA `TAN` has the same format as RDW `typegoedkeuringsnummer`
(`e2*2007/46*0251*07`), and `Va` / `Ve` are the same maker codes as RDW `variant` /
`uitvoering`. The extension number (last `*NN`) changes when an approval is amended, so the
join key drops it (`tan_base`).

Years: 2010-2017 from the all-years table (final rows, `Version_file` per year; SDI records
from research/R-08), then the adapter's own TABLES (2018-2025). Licence checked per SDI
record before any data query, as in `adapter.fetch`. One request at a time, FETCH_SLEEP_S
apart.
"""

from __future__ import annotations

import json
import time
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from ev_pipeline.sources import _common as c
from ev_pipeline.sources.eea.adapter import (
    ALL_YEARS,
    FETCH_SLEEP_S,
    PAGE_SIZE,
    SQL_URL,
    TABLES,
    EeaTable,
    fetch_licence,
)

DIR = "eea_versions"
FILE_PREFIX = "versions-"

# Final data 2010-2017 in the all-years table; SDI record ids from research/R-08 (retrieved
# 2026-11-15). Version_file follows the 2018 (v18) / 2019 (v20) pattern: v2 for 2010, +2/year.
OLD_TABLES: tuple[EeaTable, ...] = (
    EeaTable(2010, ALL_YEARS, "F", "baa86df2-86b4-4339-b709-25d9b20f9301", "v2"),
    EeaTable(2011, ALL_YEARS, "F", "665f2a8b-2993-4071-92f5-dde5a47dfd42", "v4"),
    EeaTable(2012, ALL_YEARS, "F", "5380e9bd-18e9-4bf9-b26b-f985f2c5f99e", "v6"),
    EeaTable(2013, ALL_YEARS, "F", "b9de889e-1434-4a8f-a93a-c17ef6a07527", "v8"),
    EeaTable(2014, ALL_YEARS, "F", "af267be7-eebd-4c1a-ba24-b10a51201f47", "v10"),
    EeaTable(2015, ALL_YEARS, "F", "770aa0a5-83ce-4663-93fa-78507f1990d6", "v12"),
    EeaTable(2016, ALL_YEARS, "F", "1129c5fc-5af5-4c8f-b31e-dc740bd6e0f3", "v14"),
    EeaTable(2017, ALL_YEARS, "F", "0a8985f6-af2d-44b7-ac88-a749da19a155", "v16"),
)
VERSION_TABLES: tuple[EeaTable, ...] = OLD_TABLES + TABLES


def query_for(t: EeaTable) -> str:
    """Counts only: no spec column is selected (Decision 049). `Cn` (commercial name) is a
    label, used to measure model-level coverage through the seed matcher."""
    return (
        "SELECT Year, Mk, Cn, TAN, Va, Ve, SUM(R) AS registrations "
        f"FROM {t.table} WHERE Ft = 'electric' AND {t.where} "
        "GROUP BY Year, Mk, Cn, TAN, Va, Ve ORDER BY Mk, Cn, TAN, Va, Ve"
    )


def _s(v: object) -> str:
    return "" if v is None else str(v).strip()


def tan_base(tan: str) -> str:
    """`e2*2007/46*0251*07` -> `e2*2007/46*0251` (drop the extension number)."""
    s = _s(tan).lower().replace(" ", "").lstrip(":;.,")
    parts = s.split("*")
    if len(parts) >= 4 and parts[-1].isdigit():
        parts = parts[:-1]
    return "*".join(parts)


def version_key(tan: str, va: str, ve: str) -> tuple[str, str, str]:
    return tan_base(tan), _s(va).upper(), _s(ve).upper()


def fetch(
    client: httpx.Client,
    target: Path,
    tables: tuple[EeaTable, ...] = VERSION_TABLES,
    sleep_s: float = FETCH_SLEEP_S,
) -> int:
    """Licence per SDI record, then one grouped query per table (paged), one file per year.
    Returns the number of grouped rows."""
    calls = 0

    def pause() -> None:
        nonlocal calls
        if calls and sleep_s:
            time.sleep(sleep_s)
        calls += 1

    licences: dict[str, str] = {}
    for t in tables:
        if t.metadata_uuid in licences:
            continue
        pause()
        text = fetch_licence(client, t.metadata_uuid)
        if not text or "CC-BY 4.0" not in text:
            raise RuntimeError(f"EEA {t.year} licence not confirmed in metadata: {text!r}")
        licences[t.metadata_uuid] = text
    target.mkdir(parents=True, exist_ok=True)
    for old in target.glob(f"{FILE_PREFIX}*.json"):
        old.unlink()
    total = 0
    per_year: list[dict[str, object]] = []
    for t in tables:
        rows: list[dict[str, Any]] = []
        page = 0
        while True:
            page += 1
            pause()
            resp = client.post(
                SQL_URL, data={"query": query_for(t), "p": str(page), "nrOfHits": str(PAGE_SIZE)}
            )
            resp.raise_for_status()
            body = resp.json()
            if "errors" in body:
                raise RuntimeError(f"Discodata error ({t.year}): {body['errors']}")
            batch = body.get("results", [])
            rows += batch
            if len(batch) < PAGE_SIZE:
                break
        out = [{**r, "Year": t.year, "table": t.table, "status": t.status} for r in rows]
        (target / f"{FILE_PREFIX}{t.year}.json").write_text(
            json.dumps(out, ensure_ascii=False, indent=0) + "\n", encoding="utf-8"
        )
        total += len(out)
        per_year.append(
            {
                "year": t.year,
                "table": t.table,
                "where": t.where,
                "metadata_record": t.metadata_uuid,
                "pages": page,
                "rows": len(out),
                "registrations": sum(int(r.get("registrations") or 0) for r in out),
            }
        )
    c.write_fetch_meta(
        target,
        {
            "url": SQL_URL,
            "query": query_for(tables[-1]),
            "licence_metadata_by_record": licences,
            "tables": per_year,
            "rows": total,
        },
    )
    return total


@dataclass
class EeaVersionCounts:
    """EU registrations per (tan_base, Va, Ve), and the EU BEV total, over the years read."""

    by_version: dict[tuple[str, str, str], int]
    by_make: dict[str, int]
    by_name: dict[tuple[str, str], int]  # (make, commercial name) as reported, upper case
    total: int
    years: list[int]
    retrieved_at: str | None = None


def load(raw_dir: Path) -> EeaVersionCounts | None:
    """Read the yearly files written by `fetch`; None when there are none."""
    files = sorted(raw_dir.glob(f"{FILE_PREFIX}*.json"))
    if not files:
        return None
    return from_rows(
        (r for f in files for r in json.loads(f.read_text(encoding="utf-8"))),
        retrieved_at=_retrieved(raw_dir),
    )


def from_rows(rows: Iterable[dict[str, Any]], retrieved_at: str | None = None) -> EeaVersionCounts:
    by_version: dict[tuple[str, str, str], int] = {}
    by_make: dict[str, int] = {}
    by_name: dict[tuple[str, str], int] = {}
    years: set[int] = set()
    total = 0
    for r in rows:
        n = int(r.get("registrations") or 0)
        if n <= 0:
            continue
        total += n
        if r.get("Year"):
            years.add(int(r["Year"]))
        mk = _s(r.get("Mk")).upper()
        by_make[mk] = by_make.get(mk, 0) + n
        nk = (mk, _s(r.get("Cn")).upper())
        by_name[nk] = by_name.get(nk, 0) + n
        if not _s(r.get("Va")) and not _s(r.get("Ve")):
            continue  # no version codes: counts toward the EU total only
        k = version_key(_s(r.get("TAN")), _s(r.get("Va")), _s(r.get("Ve")))
        by_version[k] = by_version.get(k, 0) + n
    return EeaVersionCounts(by_version, by_make, by_name, total, sorted(years), retrieved_at)


def _retrieved(raw_dir: Path) -> str | None:
    meta = raw_dir / "_fetch.json"
    if not meta.exists():
        return None
    data = json.loads(meta.read_text(encoding="utf-8"))
    return str(data.get("fetched_at") or data.get("retrieved_at") or "") or None
