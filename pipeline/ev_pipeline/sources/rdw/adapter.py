"""RDW Open Data adapter (CC0-1.0): registered battery-electric passenger cars in NL.

Fuel type lives in `8ys7-d773` (brandstof) and make/model in `m9d7-ebf2` (gekentekende
voertuigen), and the Socrata API refuses joins ("joins are not supported"). So we count
server-side in `m9d7-ebf2` alone, with a proxy for "battery-electric":

    voertuigsoort = 'Personenauto' AND cilinderinhoud IS NULL
    AND datum_eerste_toelating >= 20100101

BEVs have no engine displacement; the date floor drops classic cars with missing data.
Checked on 2026-11-15 against 8ys7-d773 with 1000-row random samples each way: 998/1000
proxy hits were BEV (1 fuel-cell car, 1 petrol), and 554/554 BEV passenger cars from
8ys7-d773 were proxy hits. See data/SOURCES.md.

Never downloads row-level data: one grouped query (merk x handelsbenaming x year of first
admission), paginated. About 3,100 rows.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import httpx

from ev_pipeline.records import SourceRecord, SpecValue
from ev_pipeline.schema_models import Confidence, Country, FactField, Source
from ev_pipeline.sources import _common as c

NAME = "rdw"
BASE_URL = "https://opendata.rdw.nl"
DATASET = "m9d7-ebf2"
PAGE_SIZE = 5000

BEV_WHERE = (
    "voertuigsoort = 'Personenauto' AND cilinderinhoud IS NULL "
    "AND datum_eerste_toelating >= 20100101"
)
QUERY = {
    "$select": "merk, handelsbenaming, date_extract_y(datum_eerste_toelating_dt) AS jaar, "
    "count(*) AS n",
    "$where": BEV_WHERE,
    "$group": "merk, handelsbenaming, jaar",
    "$order": "merk, handelsbenaming, jaar",
}

SOURCE = Source(
    id="rdw",
    name="RDW Open Data",
    url=f"{BASE_URL}/d/{DATASET}",
    licence="CC0-1.0",
    attribution="Bron: RDW Open Data (opendata.rdw.nl), CC0.",
)


def fetch(client: httpx.Client, target: Path) -> int:
    """Fetch licence metadata + all aggregate pages into `target`. Returns rows fetched."""
    meta = client.get(f"{BASE_URL}/api/views/{DATASET}.json")
    meta.raise_for_status()
    view = meta.json()
    licence_custom = view.get("metadata", {}).get("custom_fields", {}).get("Licentie", {})

    target.mkdir(parents=True, exist_ok=True)
    for old in target.glob("page-*.json"):
        old.unlink()
    rows = 0
    page = 0
    while True:
        params = {**QUERY, "$limit": str(PAGE_SIZE), "$offset": str(page * PAGE_SIZE)}
        resp = client.get(f"{BASE_URL}/resource/{DATASET}.json", params=params)
        resp.raise_for_status()
        batch = resp.json()
        (target / f"page-{page:03d}.json").write_text(
            json.dumps(batch, ensure_ascii=False, indent=0) + "\n", encoding="utf-8"
        )
        rows += len(batch)
        page += 1
        if len(batch) < PAGE_SIZE:
            break
    c.write_fetch_meta(
        target,
        {
            "url": f"{BASE_URL}/resource/{DATASET}.json",
            "query": QUERY,
            "dataset_name": view.get("name"),
            "dataset_rows_updated_at": view.get("rowsUpdatedAt"),
            "licence_metadata": {
                "license": view.get("license"),
                "licenseId": view.get("licenseId"),
                "custom_fields.Licentie": licence_custom.get("Licentie"),
            },
            "pages": page,
            "rows": rows,
        },
    )
    return rows


def normalise(raw_dir: Path, retrieved_at: date) -> list[SourceRecord]:
    records: list[SourceRecord] = []
    for page in sorted(raw_dir.glob("page-*.json")):
        for row in json.loads(page.read_text(encoding="utf-8")):
            make, model = row.get("merk"), row.get("handelsbenaming")
            count = int(row.get("n", 0))
            if not make or not model or count <= 0:
                continue  # rows without make or trade name cannot be matched
            year = int(row["jaar"]) if row.get("jaar") else None
            records.append(
                SourceRecord(
                    source=SOURCE,
                    record_key=f"{DATASET}:{make}|{model}|{year or ''}",
                    kind="registration_count",
                    make=make,
                    model=model,
                    year=year,
                    country=Country.NL,
                    specs={FactField.registered_count: SpecValue(value=count, unit="count")},
                    retrieved_at=retrieved_at,
                    confidence=Confidence.high,
                )
            )
    return records


def fetch_cmd(client: httpx.Client | None = None) -> int:
    target = c.raw_dir(NAME)
    own = client is None
    client = client or httpx.Client(timeout=120, headers={"User-Agent": c.USER_AGENT})
    try:
        rows = fetch(client, target)
    except httpx.HTTPError as exc:
        print(f"fetch {NAME}: failed: {exc}")
        return 1
    finally:
        if own:
            client.close()
    c.log_step(
        step="fetch",
        source=NAME,
        input_=f"{BASE_URL}/resource/{DATASET}.json (grouped SoQL)",
        output=c.rel(target),
        rows_out=rows,
    )
    return 0


def normalise_cmd(from_fixtures: bool) -> int:
    src = c.FIXTURES_DIR / NAME if from_fixtures else c.raw_dir(NAME)
    if not any(src.glob("page-*.json")):
        print(f"normalise {NAME}: no data in {src} (run `ev fetch {NAME}` first)")
        return 1
    records = normalise(src, c.retrieved_at_for(src))
    out = c.staging_dir() / f"{NAME}.records.jsonl"
    rows = c.write_records(records, out)
    c.log_step(
        step="normalise",
        source=NAME,
        input_=c.rel(src),
        output=c.rel(out),
        rows_out=rows,
        from_fixtures=from_fixtures,
        registered_total=sum(int(r.specs[FactField.registered_count].value) for r in records),
    )
    return 0
