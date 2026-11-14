"""EEA CO2 monitoring of new passenger cars, Regulation (EU) 2019/631 (CC BY 4.0).

Pulls new battery-electric registrations (Ft = 'electric') per country x make x commercial
name for NL/DE/FR/BE (the UK is not in the EU data), aggregated server-side through the
Discodata SQL endpoint. Alongside each count we keep registration-weighted averages of the
type-approval mass (M, kg), electric consumption (Z, Wh/km) and electric range (Zr, km)
as low-confidence spec facts.

Discodata sits behind an Azure WAF that rejects many GET queries (e.g. `... AND ...` with
quoted literals) with HTTP 403; POSTing the same query as a form body works.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import httpx

from ev_pipeline.records import SourceRecord, SpecValue
from ev_pipeline.schema_models import Confidence, Country, FactField, Source
from ev_pipeline.sources import _common as c

NAME = "eea"
SQL_URL = "https://discodata.eea.europa.eu/sql"
# Latest table on the EEA datahub item "Monitoring of CO2 emissions from passenger cars
# Regulation (EU) 2019/631": 2025 provisional (v31, published 2026-06-25). Bump when the
# final 2025 table or provisional 2026 table appears.
TABLE = "[CO2Emission].[latest].[co2cars_2025Pv31]"
METADATA_UUID = "b4044b06-2e6b-4f8e-a6e6-66e0e98bb0dd"  # SDI record of that 2025 dataset
SDI_SEARCH = "https://sdi.eea.europa.eu/catalogue/srv/api/search/records/_search"
DATAHUB_URL = (
    "https://www.eea.europa.eu/en/datahub/datahubitem-view/fa8b1229-3db6-495d-b18e-9c9b3267c02b"
)
COUNTRIES = ("NL", "DE", "FR", "BE")
PAGE_SIZE = 1000


def _wavg(column: str) -> str:
    return (
        f"SUM(CAST(R AS float) * {column}) / "
        f"NULLIF(SUM(CASE WHEN {column} IS NOT NULL THEN R END), 0)"
    )


QUERY = (
    "SELECT MS, Mk, Cn, Year, SUM(R) AS registrations, "
    f"{_wavg('[M (kg)]')} AS mass_kg, "
    f"{_wavg('[Z (Wh/km)]')} AS z_wh_km, "
    f"{_wavg('Zr')} AS zr_km "
    f"FROM {TABLE} "
    "WHERE Ft = 'electric' AND MS IN (" + ", ".join(f"'{m}'" for m in COUNTRIES) + ") "
    "GROUP BY MS, Mk, Cn, Year ORDER BY MS, Mk, Cn, Year"
)

SOURCE = Source(
    id="eea",
    name="EEA CO2 monitoring of new cars (Reg. 2019/631)",
    url=DATAHUB_URL,
    licence="CC-BY-4.0",
    attribution=(
        "Contains data from the European Environment Agency, CO2 emissions from new "
        "passenger cars (Regulation (EU) 2019/631). Copyright holder: Directorate-General "
        "for Climate Action (DG CLIMA). CC BY 4.0."
    ),
)


def fetch_licence(client: httpx.Client) -> str | None:
    """Use-limitation text of the dataset's SDI metadata record (where the licence lives)."""
    resp = client.post(
        SDI_SEARCH,
        json={"query": {"term": {"uuid": METADATA_UUID}}, "size": 1},
        headers={"Accept": "application/json"},
    )
    resp.raise_for_status()
    hits = resp.json().get("hits", {}).get("hits", [])
    if not hits:
        return None
    limits = hits[0]["_source"].get("MD_ConstraintsUseLimitationObject", [])
    return limits[0].get("default") if limits else None


def fetch(client: httpx.Client, target: Path) -> int:
    licence_text = fetch_licence(client)
    if not licence_text or "CC-BY 4.0" not in licence_text:
        raise RuntimeError(f"EEA licence not confirmed in metadata: {licence_text!r}")
    target.mkdir(parents=True, exist_ok=True)
    for old in target.glob("page-*.json"):
        old.unlink()
    rows = 0
    page = 1
    while True:
        resp = client.post(
            SQL_URL, data={"query": QUERY, "p": str(page), "nrOfHits": str(PAGE_SIZE)}
        )
        resp.raise_for_status()
        body = resp.json()
        if "errors" in body:
            raise RuntimeError(f"Discodata error: {body['errors']}")
        batch = body.get("results", [])
        (target / f"page-{page:03d}.json").write_text(
            json.dumps(batch, ensure_ascii=False, indent=0) + "\n", encoding="utf-8"
        )
        rows += len(batch)
        if len(batch) < PAGE_SIZE:
            break
        page += 1
    c.write_fetch_meta(
        target,
        {
            "url": SQL_URL,
            "table": TABLE,
            "query": QUERY,
            "metadata_record": METADATA_UUID,
            "licence_metadata": licence_text,
            "pages": page,
            "rows": rows,
        },
    )
    return rows


def _round(value: float | None, digits: int) -> float | None:
    if value is None or value <= 0:
        return None
    return round(float(value), digits)


def normalise(raw_dir: Path, retrieved_at: date) -> list[SourceRecord]:
    records: list[SourceRecord] = []
    for page in sorted(raw_dir.glob("page-*.json")):
        for row in json.loads(page.read_text(encoding="utf-8")):
            ms, make, model = row.get("MS"), row.get("Mk"), row.get("Cn")
            count = int(row.get("registrations") or 0)
            if ms not in COUNTRIES or not make or not model or count <= 0:
                continue
            year = int(row["Year"]) if row.get("Year") else None
            key = f"{TABLE}:{ms}|{make}|{model}|{year or ''}"
            common = {
                "source": SOURCE,
                "make": make,
                "model": model,
                "year": year,
                "country": Country(ms),
                "retrieved_at": retrieved_at,
            }
            # Counts are the official monitoring data, but this table is provisional.
            records.append(
                SourceRecord(
                    record_key=key,
                    kind="registration_count",
                    specs={FactField.registered_count: SpecValue(value=count, unit="count")},
                    confidence=Confidence.medium,
                    **common,
                )
            )
            specs: dict[FactField, SpecValue] = {}
            if (mass := _round(row.get("mass_kg"), 0)) is not None:
                specs[FactField.weight_kg] = SpecValue(value=mass, unit="kg")
            if (wh_km := _round(row.get("z_wh_km"), 1)) is not None:
                specs[FactField.consumption_kwh_100km] = SpecValue(
                    value=round(wh_km / 10, 2), unit="kWh/100km"
                )
            if (rng := _round(row.get("zr_km"), 0)) is not None:
                specs[FactField.wltp_range_km] = SpecValue(value=rng, unit="km")
            if specs:
                # Registration-weighted type-approval averages across all versions sold.
                records.append(
                    SourceRecord(
                        record_key=key + "#type_approval_avg",
                        kind="spec",
                        specs=specs,
                        confidence=Confidence.low,
                        **common,
                    )
                )
    return records


def fetch_cmd(client: httpx.Client | None = None) -> int:
    target = c.raw_dir(NAME)
    own = client is None
    client = client or httpx.Client(timeout=300, headers={"User-Agent": c.USER_AGENT})
    try:
        rows = fetch(client, target)
    except (httpx.HTTPError, RuntimeError) as exc:
        print(f"fetch {NAME}: failed: {exc}")
        return 1
    finally:
        if own:
            client.close()
    c.log_step(
        step="fetch",
        source=NAME,
        input_=f"{SQL_URL} {TABLE} (grouped SQL)",
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
    )
    return 0
