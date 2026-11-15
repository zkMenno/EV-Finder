"""T-034: towns + January climate for Trip fit -> releases/<n>/towns/<country>.json.

Inputs (staging): `geonames.towns.jsonl` (+ meta) and `meteostat.climate.jsonl` (+ meta).
Both sources must pass the licence gate; without towns nothing ships, without climate the
towns ship with `climate: null`.

Each town points at its nearest station with data (`station_id`, `station_km`), within
MAX_TOWN_KM and with an elevation gap under MAX_ELEVATION_GAP_M (meteostat adapter
constants). Station figures are listed once per file under `stations`; `provenance.climate`
gives their source, retrieval date, licence, confidence (medium: station data, nearest
station, provider per row unknown), period, method and definitions, and `provenance.towns`
does the same for the town rows. Nothing is interpolated: a town without a station in range
has `station_id: null` and the app uses its country default.

One file per country (page speed: the trip module loads only the visitor's country):
`{"release", "generated_at", "country", "sources", "provenance", "stations", "towns"}`. 🟡 No schema
def yet (requested from WS0: TownsRelease).
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ev_pipeline.release.gate import Registry
from ev_pipeline.sources.meteostat.adapter import (
    MAX_ELEVATION_GAP_M,
    MAX_TOWN_KM,
    haversine_km,
)

DIR_NAME = "towns"
TOWNS_FILE = "geonames.towns.jsonl"
CLIMATE_FILE = "meteostat.climate.jsonl"


@dataclass
class TownsResult:
    documents: dict[str, dict[str, Any]] = field(default_factory=dict)  # country -> doc
    inputs: list[dict[str, Any]] = field(default_factory=list)
    log: dict[str, Any] = field(default_factory=dict)


def _read(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def _meta(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def nearest(
    town: dict[str, Any], stations: list[dict[str, Any]]
) -> tuple[dict[str, Any], float] | None:
    """Nearest station in range that has a P10; else the nearest with a January mean."""
    hits = []
    for s in stations:
        if abs(s["lat"] - town["lat"]) > 0.6:
            continue
        km = haversine_km(town["lat"], town["lon"], s["lat"], s["lon"])
        if km > MAX_TOWN_KM:
            continue
        te, se = town.get("elevation_m"), s.get("elevation_m")
        if te is not None and se is not None and abs(te - se) > MAX_ELEVATION_GAP_M:
            continue
        hits.append((s.get("jan_p10_c") is None, km, s["station_id"], s))
    if not hits:
        return None
    _, km, _, s = min(hits, key=lambda h: h[:3])
    return s, km


def build_towns(staging: Path, registry: Registry, release: int, generated_at: str) -> TownsResult:
    out = TownsResult()
    towns = _read(staging / TOWNS_FILE)
    if not towns:
        out.log = {"status": "no input"}
        return out
    out.inputs.append({"path": str(staging / TOWNS_FILE), "records": len(towns)})
    why = registry.reason_blocked("geonames")
    if why:
        out.log = {"status": "not shipped", "gated": {"geonames": why}}
        return out
    tmeta = _meta(staging / "geonames.towns.meta.json")
    stations = _read(staging / CLIMATE_FILE)
    cmeta = _meta(staging / "meteostat.climate.meta.json")
    gated: dict[str, str] = {}
    if stations:
        out.inputs.append({"path": str(staging / CLIMATE_FILE), "records": len(stations)})
        cwhy = registry.reason_blocked("meteostat")
        if cwhy:
            gated["meteostat"] = cwhy
            stations = []
    sources = [
        {"id": "geonames", "name": registry.sources["geonames"].name,
         "licence": tmeta.get("licence", "CC-BY-4.0"), "attribution": tmeta.get("attribution"),
         "url": "https://www.geonames.org/"}
    ]  # fmt: skip
    if stations:
        sources.append(
            {"id": "meteostat", "name": registry.sources["meteostat"].name,
             "licence": cmeta.get("licence", "CC-BY-4.0"),
             "attribution": cmeta.get("attribution"), "url": "https://meteostat.net/"}
        )  # fmt: skip
    counts: Counter[str] = Counter()
    by_country: dict[str, list[dict[str, Any]]] = {}
    used: dict[str, dict[str, set[str]]] = {}  # country -> station ids
    st_by_id = {s["station_id"]: s for s in stations}
    for t in towns:
        row = {k: t[k] for k in ("id", "name", "country", "lat", "lon", "population") if k in t}
        for k in ("names", "admin1", "elevation_m"):
            if t.get(k) is not None:
                row[k] = t[k]
        hit = nearest(t, stations) if stations else None
        if hit:
            s, km = hit
            row["station_id"], row["station_km"] = s["station_id"], round(km, 1)
            used.setdefault(t["country"], {}).setdefault("ids", set()).add(s["station_id"])
            counts["with climate"] += 1
            if s.get("jan_p10_c") is None:
                counts["climate without P10"] += 1
        else:
            row["station_id"] = None
            counts["no station in range"] += 1
        by_country.setdefault(t["country"], []).append(row)
    provenance = {
        "towns": {"source_id": "geonames", "retrieved_at": tmeta.get("retrieved_at"),
                  "licence": tmeta.get("licence", "CC-BY-4.0"), "confidence": "high"},
        "climate": None if not stations else {
            "source_id": "meteostat", "retrieved_at": cmeta.get("retrieved_at"),
            "licence": cmeta.get("licence", "CC-BY-4.0"),
            "confidence": cmeta.get("confidence", "medium"), "unit": "°C",
            "period": stations[0].get("period"),
            "method": "town -> nearest station with 1991-2020 data within "
                      f"{MAX_TOWN_KM:.0f} km and {MAX_ELEVATION_GAP_M} m elevation; no "
                      "interpolation",
            "definitions": {
                "months_mean_c": "mean of daily mean temperature per month, Jan..Dec",
                "jan_mean_c": "January mean of daily mean temperature",
                "jan_p10_c": "10th percentile of January daily mean temperature",
            },
        },
    }  # fmt: skip
    keep = ("name", "lat", "lon", "elevation_m", "months_mean_c", "jan_mean_c",
            "jan_mean_method", "jan_p10_c", "jan_years")  # fmt: skip
    for cc, rows in sorted(by_country.items()):
        rows.sort(key=lambda r: (-int(r.get("population") or 0), r["id"]))
        ids = sorted((used.get(cc) or {}).get("ids") or [])
        out.documents[cc] = {
            "release": release,
            "generated_at": generated_at,
            "country": cc,
            "sources": sources,
            "provenance": provenance,
            "stations": {sid: {k: st_by_id[sid].get(k) for k in keep} for sid in ids},
            "towns": rows,
        }
        counts[f"towns {cc}"] = len(rows)
    out.log = {"status": "shipped", "gated": gated, **dict(sorted(counts.items()))}
    return out
