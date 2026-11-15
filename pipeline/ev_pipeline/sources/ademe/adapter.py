"""ADEME Car Labelling adapter (Licence Ouverte 2.0): specs and FR list prices of BEVs on sale.

One `;`-separated CSV (decimal commas, UTF-8 with BOM; some descriptions are double-encoded,
"Ã©" for "é", which we repair). We keep `Energie = ELECTRIC` only: "ELEC+ESSENC HR" and
"ELEC+GAZOLE HR" are plug-in hybrids and "ESS+ELEC HNR" / "GAZ+ELEC HNR" are full hybrids.

One spec record per distinct version: make = Marque, model = Modèle, variant_name =
Description Commerciale. There is no model-year column, so `year` is empty.

Values (all checked on the 2026-11-15 file):
- WLTP values come as Min/Max over the version's interpolation family (test vehicle low vs
  high, i.e. options and wheels). These are two ends of one homologation, not two cars, so we
  never average them. We emit the best case only, which is the figure makers quote:
  `consumption_kwh_100km` = lowest "Conso elec" (Wh/km / 10) and `wltp_range_km` = highest
  "Autonomie elec". When only one value is given (the Min cells are empty on 30 of 134 BEV
  rows) that value is used. The worst case has no field in the schema yet (Q-043).
- `weight_kg` = "Poids à vide": mass in running order WITHOUT the 75 kg driver. On every
  electric row "Masse OM Min" = "Poids à vide" + 75, and we only emit the weight on rows where
  that holds, so the meaning is checked per row (Q-044 on which mass the schema means).
- `power_kw` is NOT emitted: the only BEV power column is "Puissance nominale électrique",
  the rated (30-minute) power, e.g. 57 kW for a 100 kW Corsa-e; "Puissance maximale" is
  empty for every BEV (Q-045).
- `price_new` = "Prix véhicule" in EUR, as a separate record with country FR (the openev
  pattern), because a price only means something per country.

The same Marque x Modèle x Description can appear on several rows. Identical rows are
deduplicated. Rows that differ (e.g. "MEGANE (55Kw)" covers both 40 and 60 kWh batteries,
310 vs 486 km) are different cars under one name: each gets its own record (`#1`, `#2`...
in record_key, in sorted order), and the merge step sees the conflict.
"""

from __future__ import annotations

import contextlib
import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import httpx

from ev_pipeline.records import SourceRecord, SpecValue
from ev_pipeline.schema_models import Confidence, Country, FactField, Source
from ev_pipeline.sources import _common as c

NAME = "ademe"
DIR = "ademe"
DATASET = "ademe-car-labelling"
API = f"https://data.ademe.fr/data-fair/api/v1/datasets/{DATASET}"
RAW_URL = f"{API}/raw"
PAGE_URL = f"https://data.ademe.fr/datasets/{DATASET}"
FILE = "ademe-car-labelling.csv"
LICENCE_MARKER = "Licence Ouverte"
BEV_ENERGIE = "ELECTRIC"
DRIVER_KG = 75

SOURCE = Source(
    id="ademe",
    name="ADEME – Car Labelling",
    url=PAGE_URL,
    licence="Licence-Ouverte-2.0",
    attribution="ADEME – Car Labelling, Licence Ouverte",
)


class LicenceChanged(RuntimeError):
    pass


def fix_text(value: str) -> str:
    """Repair UTF-8 that was decoded as Latin-1 once ("Ã©lectrique" -> "électrique")."""
    text = value
    if "Ã" in text or "Â" in text:
        # Repair before collapsing whitespace: "Â\xa0" is a mis-decoded no-break space.
        with contextlib.suppress(UnicodeEncodeError, UnicodeDecodeError):
            text = text.encode("latin-1").decode("utf-8")
    return " ".join(text.split())


def _num(value: str | None) -> float | None:
    if value is None:
        return None
    text = value.strip().replace(",", ".")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


@dataclass(frozen=True, order=True)
class Version:
    make: str
    model: str
    description: str
    consumption_wh_km: float | None
    range_km: float | None
    weight_kg: float | None
    price_eur: float | None


def _best(values: list[float | None], pick) -> float | None:
    present = [v for v in values if v is not None]
    return pick(present) if present else None


def read_versions(path: Path) -> tuple[list[Version], int]:
    """BEV rows as deduplicated Versions, plus the number of BEV rows read."""
    seen: set[Version] = set()
    rows = 0
    with path.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh, delimiter=";"):
            if (row.get("Energie") or "").strip().upper() != BEV_ENERGIE:
                continue
            rows += 1
            make, model = fix_text(row["Marque"]), fix_text(row["Modèle"])
            desc = fix_text(row["Description Commerciale"])
            if not make or not model:
                continue
            weight = _num(row.get("Poids à vide"))
            mass_om = _num(row.get("Masse OM Min"))
            if weight is None or mass_om is None or mass_om - weight != DRIVER_KG:
                weight = None  # meaning not confirmed on this row: don't emit
            seen.add(
                Version(
                    make=make,
                    model=model,
                    description=desc,
                    consumption_wh_km=_best(
                        [_num(row.get("Conso elec Min")), _num(row.get("Conso elec Max"))], min
                    ),
                    range_km=_best(
                        [_num(row.get("Autonomie elec Min")), _num(row.get("Autonomie elec Max"))],
                        max,
                    ),
                    weight_kg=weight,
                    price_eur=_num(row.get("Prix véhicule")),
                )
            )
    return sorted(seen), rows


def records_from_versions(versions: list[Version], retrieved_at: date) -> list[SourceRecord]:
    groups: dict[tuple[str, str, str], list[Version]] = {}
    for v in versions:
        groups.setdefault((v.make, v.model, v.description), []).append(v)
    out: list[SourceRecord] = []
    for (make, model, desc), group in groups.items():
        for i, v in enumerate(group, 1):
            key = f"{DATASET}:{make}|{model}|{desc}" + (f"#{i}" if len(group) > 1 else "")
            common = {
                "source": SOURCE,
                "make": make,
                "model": model,
                "variant_name": desc or None,
                "retrieved_at": retrieved_at,
                "confidence": Confidence.medium,
            }
            specs: dict[FactField, SpecValue] = {}
            if v.consumption_wh_km is not None:
                specs[FactField.consumption_kwh_100km] = SpecValue(
                    value=round(v.consumption_wh_km / 10, 2), unit="kWh/100km"
                )
            if v.range_km is not None:
                specs[FactField.wltp_range_km] = SpecValue(value=v.range_km, unit="km")
            if v.weight_kg is not None:
                specs[FactField.weight_kg] = SpecValue(value=v.weight_kg, unit="kg")
            if specs:
                out.append(SourceRecord(record_key=key, specs=specs, **common))
            if v.price_eur is not None and v.price_eur > 0:
                out.append(
                    SourceRecord(
                        record_key=f"{key}#price_new:FR",
                        country=Country.FR,
                        specs={FactField.price_new: SpecValue(value=v.price_eur, unit="EUR")},
                        **common,
                    )
                )
    return out


def normalise(raw_dir: Path, retrieved_at: date) -> list[SourceRecord]:
    path = raw_dir / FILE
    if not path.exists():
        return []
    versions, _rows = read_versions(path)
    return records_from_versions(versions, retrieved_at)


# --------------------------------------------------------------------------- fetch


def fetch(client: httpx.Client, target: Path) -> int:
    """Check the licence in the dataset metadata, then download the CSV. Returns bytes."""
    meta = client.get(API)
    meta.raise_for_status()
    info = meta.json()
    licence = info.get("license") or {}
    if LICENCE_MARKER not in str(licence.get("title", "")):
        raise LicenceChanged(f"dataset licence is now {licence!r}")
    resp = client.get(RAW_URL)
    resp.raise_for_status()
    target.mkdir(parents=True, exist_ok=True)
    (target / FILE).write_bytes(resp.content)
    c.write_fetch_meta(
        target,
        {
            "url": RAW_URL,
            "metadata_url": API,
            "licence_metadata": licence,
            "dataset_title": info.get("title"),
            "data_updated_at": info.get("dataUpdatedAt"),
            "rows_total": info.get("count"),
            "file_md5": (info.get("file") or {}).get("md5"),
            "bytes": len(resp.content),
        },
    )
    return len(resp.content)


def fetch_cmd(client: httpx.Client | None = None) -> int:
    target = c.raw_dir(DIR)
    own = client is None
    client = client or httpx.Client(
        timeout=120, headers={"User-Agent": c.USER_AGENT}, follow_redirects=True
    )
    try:
        size = fetch(client, target)
    except (httpx.HTTPError, LicenceChanged) as exc:
        print(f"fetch {NAME}: failed: {exc}")
        return 1
    finally:
        if own:
            client.close()
    c.log_step(
        step="fetch", source=NAME, input_=RAW_URL, output=c.rel(target), rows_out=size, unit="bytes"
    )
    return 0


def normalise_cmd(from_fixtures: bool) -> int:
    src = c.FIXTURES_DIR / DIR if from_fixtures else c.raw_dir(DIR)
    path = src / FILE
    if not path.exists():
        print(f"normalise {NAME}: no data in {src} (run `ev fetch {NAME}` first)")
        return 1
    versions, bev_rows = read_versions(path)
    records = records_from_versions(versions, c.retrieved_at_for(src))
    out = c.staging_dir() / f"{NAME}.records.jsonl"
    rows = c.write_records(records, out)
    c.log_step(
        step="normalise",
        source=NAME,
        input_=c.rel(path),
        output=c.rel(out),
        rows_out=rows,
        from_fixtures=from_fixtures,
        bev_rows=bev_rows,
        distinct_versions=len(versions),
        price_records=sum(1 for r in records if r.country == Country.FR),
    )
    return 0
