"""Meteostat adapter (CC BY 4.0): January climate per weather station for Trip fit (T-034).

Licence (R-27, checked 2026-11-15): data redistributed by Meteostat is CC BY 4.0, commercial
use allowed; credit "Meteostat and its data providers". The bulk files are Meteostat's own
redistribution, so its licence covers them (the per-provider terms in R-27 apply to data
fetched straight from a weather service). fetch refuses when the licence page no longer names
CC BY 4.0. 🟡 The bulk files don't say which provider each row came from, so the credit is
the generic one and confidence is `medium`.

What we compute per station, period 1991–2020 (Decision 036 picks ERA5-Land as primary once
the CDS key arrives; this is the second source and today's only one):
- `months_mean_c`: 12 monthly mean temperatures: mean of daily means where at least
  MIN_YEARS years have MIN_DAYS days, else Meteostat's 1991–2020 normals ((tmin+tmax)/2).
- `jan_mean_c`: January of that (`jan_mean_method` says which).
- `jan_p10_c`: the 10th percentile of January *daily mean* temperature, 1991–2020 (R-27 §6
  definition: cold-snap day, matches how consumption tests quote ambient temperature).
  Needs at least MIN_YEARS Januaries with MIN_DAYS days each, else null.

Which stations: launch-country stations whose inventory covers 1991–2020 daily data or
normals, nearest to at least one GeoNames town (run `ev normalise geonames` first). Without
towns, every qualifying launch-country station.

Output: `data/staging/meteostat.climate.jsonl`, one station per line.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import math
import shutil
import statistics
import time
from collections import Counter
from pathlib import Path
from typing import Any

import httpx

from ev_pipeline import net
from ev_pipeline.sources import _common as c
from ev_pipeline.sources.geonames.adapter import launch_countries

NAME = "meteostat"
DIR = "meteostat"
STAGING_SUFFIX = ".climate.jsonl"
BASE = "https://bulk.meteostat.net/v2"
STATIONS_URL = f"{BASE}/stations/lite.json.gz"
LICENCE_URL = "https://dev.meteostat.net/license"
LICENCE_SENTENCE = "Creative Commons Attribution 4.0"
LICENCE = "CC-BY-4.0"
ATTRIBUTION = "Meteostat (meteostat.net) and its data providers (dev.meteostat.net/providers)"
PERIOD = (1991, 2020)
MIN_YEARS = 20
MIN_DAYS = 20
MAX_TOWN_KM = 60.0  # a town further than this from every usable station gets no climate
MAX_ELEVATION_GAP_M = 250


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(a))


def qualifying(stations: list[dict[str, Any]], countries: set[str]) -> list[dict[str, Any]]:
    """Launch-country stations whose inventory covers the period (daily or normals)."""
    out = []
    for s in stations:
        if s.get("country") not in countries:
            continue
        inv = s.get("inventory") or {}
        daily, normals = inv.get("daily") or {}, inv.get("normals") or {}
        d_ok = (daily.get("start") or "9999") <= f"{PERIOD[0]}-01-31" and (
            daily.get("end") or "0000"
        ) >= f"{PERIOD[1]}-01-01"
        n_ok = normals.get("start") == PERIOD[0] and normals.get("end") == PERIOD[1]
        loc = s.get("location") or {}
        if (d_ok or n_ok) and loc.get("latitude") is not None:
            out.append(s)
    return out


def nearest_station(
    town: dict[str, Any], stations: list[dict[str, Any]]
) -> tuple[dict[str, Any], float] | None:
    """Closest station within MAX_TOWN_KM whose elevation is within MAX_ELEVATION_GAP_M of
    the town's (when both are known)."""
    best: tuple[dict[str, Any], float] | None = None
    for s in stations:
        loc = s["location"]
        if abs(loc["latitude"] - town["lat"]) > 0.6:  # cheap pre-filter (0.6° lat ≈ 67 km)
            continue
        km = haversine_km(town["lat"], town["lon"], loc["latitude"], loc["longitude"])
        if km > MAX_TOWN_KM:
            continue
        te, se = town.get("elevation_m"), loc.get("elevation")
        if te is not None and se is not None and abs(te - se) > MAX_ELEVATION_GAP_M:
            continue
        if best is None or km < best[1]:
            best = (s, km)
    return best


def read_towns(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


# --- per-station maths -------------------------------------------------------------------


def _num(x: str) -> float | None:
    try:
        return float(x) if x not in ("", None) else None
    except ValueError:
        return None


def parse_normals(text: str) -> list[float | None] | None:
    """Rows: start,end,month,tmin,tmax,prcp,... (no header in v2 bulk, no tavg column):
    (tmin + tmax) / 2 for the 1991–2020 rows, month 1..12."""
    months: list[float | None] = [None] * 12
    found = False
    for row in csv.reader(io.StringIO(text)):
        if len(row) < 5 or row[0] != str(PERIOD[0]) or row[1] != str(PERIOD[1]):
            continue
        m = int(row[2])
        tmin, tmax = _num(row[3]), _num(row[4])
        if 1 <= m <= 12 and tmin is not None and tmax is not None:
            months[m - 1] = round((tmin + tmax) / 2, 1)
            found = True
    return months if found else None


def daily_means_by_month(text: str) -> dict[int, dict[int, list[float]]]:
    """Daily rows: date,tavg,tmin,tmax,... -> {month: {year: [daily means]}} within PERIOD.
    A day without tavg uses (tmin + tmax) / 2."""
    out: dict[int, dict[int, list[float]]] = {}
    for row in csv.reader(io.StringIO(text)):
        if len(row) < 4 or len(row[0]) != 10:
            continue
        y, m = int(row[0][:4]), int(row[0][5:7])
        if not PERIOD[0] <= y <= PERIOD[1]:
            continue
        tavg = _num(row[1])
        if tavg is None:
            tmin, tmax = _num(row[2]), _num(row[3])
            tavg = (tmin + tmax) / 2 if tmin is not None and tmax is not None else None
        if tavg is not None:
            out.setdefault(m, {}).setdefault(y, []).append(tavg)
    return out


def january_daily_means(text: str) -> dict[int, list[float]]:
    return daily_means_by_month(text).get(1, {})


def p10(values: list[float]) -> float:
    """10th percentile, inclusive method (same as numpy's default linear interpolation)."""
    return statistics.quantiles(values, n=10, method="inclusive")[0]


def station_climate(normals_text: str | None, daily_text: str | None) -> dict[str, Any]:
    """Daily data first (true daily means, same days as P10); Meteostat's normals file
    ((tmin + tmax) / 2 per month) fills months the daily data can't."""
    normals = parse_normals(normals_text) if normals_text else None
    by_month = daily_means_by_month(daily_text) if daily_text else {}
    months: list[float | None] = []
    methods: list[str | None] = []
    for m in range(1, 13):
        good = [v for v in by_month.get(m, {}).values() if len(v) >= MIN_DAYS]
        if len(good) >= MIN_YEARS:
            months.append(round(statistics.fmean(t for v in good for t in v), 1))
            methods.append("daily")
        elif normals and normals[m - 1] is not None:
            months.append(normals[m - 1])
            methods.append("normals-midrange")
        else:
            months.append(None)
            methods.append(None)
    jan_good = {y: v for y, v in by_month.get(1, {}).items() if len(v) >= MIN_DAYS}
    days = [t for v in jan_good.values() for t in v]
    return {
        "months_mean_c": months if any(x is not None for x in months) else None,
        "jan_mean_c": months[0],
        "jan_mean_method": methods[0],
        "jan_p10_c": round(p10(days), 1) if len(jan_good) >= MIN_YEARS else None,
        "jan_years": len(jan_good),
    }


# --- fetch / normalise -------------------------------------------------------------------


def _gunzip(data: bytes) -> str:
    return gzip.decompress(data).decode("utf-8")


MAX_CANDIDATES = 4  # stations tried per town before it goes without climate


def candidates(town: dict[str, Any], stations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Stations in range for a town (distance + elevation rules), nearest first."""
    hits = []
    for s in stations:
        loc = s["location"]
        if abs(loc["latitude"] - town["lat"]) > 0.6:  # cheap pre-filter (0.6° lat ≈ 67 km)
            continue
        km = haversine_km(town["lat"], town["lon"], loc["latitude"], loc["longitude"])
        te, se = town.get("elevation_m"), loc.get("elevation")
        if km <= MAX_TOWN_KM and not (
            te is not None and se is not None and abs(te - se) > MAX_ELEVATION_GAP_M
        ):
            hits.append((km, s["id"], s))
    return [s for _, _, s in sorted(hits, key=lambda h: (h[0], h[1]))[:MAX_CANDIDATES]]


# One fetch makes hundreds of small GETs (two per station tried). A single dropped connection
# ("Server disconnected without sending a response", run 44137008063) used to fail the whole
# source. Transient errors are retried after these waits; a policy refusal (net.FetchBlocked,
# ResponseTooLarge) is not a TransportError and is never retried.
RETRY_WAITS_S: tuple[float, ...] = (2.0, 5.0, 15.0)
RETRY_STATUS = frozenset({429, 500, 502, 503, 504})


def _get(client: httpx.Client, url: str) -> httpx.Response:
    """client.get with retries on transport errors and 429/5xx; the last failure is raised
    (or, for a status, returned for raise_for_status)."""
    for wait in (*RETRY_WAITS_S, None):
        try:
            r = client.get(url)
        except httpx.TransportError:
            if wait is None:
                raise
        else:
            if r.status_code not in RETRY_STATUS or wait is None:
                return r
        time.sleep(wait)
    raise AssertionError("unreachable")  # pragma: no cover


def fetch(client: httpx.Client, target: Path, towns: list[dict[str, Any]]) -> int:
    """Download normals + daily per station. With towns: for each town, try its nearest
    stations in turn until one has a full 1991-2020 January (mean and P10); keep the best
    one found. Inventory alone can't tell temperature stations from rain gauges."""
    lic = _get(client, LICENCE_URL)
    lic.raise_for_status()
    if LICENCE_SENTENCE not in lic.text:
        raise ValueError(f"Meteostat licence page no longer names '{LICENCE_SENTENCE}'")
    resp = _get(client, STATIONS_URL)
    resp.raise_for_status()
    q = qualifying(json.loads(_gunzip(resp.content)), set(launch_countries()))
    target.mkdir(parents=True, exist_ok=True)
    for kind in ("normals", "daily"):  # start clean: raw holds exactly this fetch
        shutil.rmtree(target / kind, ignore_errors=True)
        (target / kind).mkdir()
    total = len(resp.content)
    digest = hashlib.sha256()
    quality: dict[str, int] = {}  # station id -> 2 mean+P10, 1 mean only, 0 nothing

    def get(s: dict[str, Any]) -> int:
        nonlocal total
        sid = s["id"]
        if sid in quality:
            return quality[sid]
        texts: dict[str, str | None] = {}
        for kind in ("normals", "daily"):
            r = _get(client, f"{BASE}/{kind}/{sid}.csv.gz")
            if r.status_code == 404:
                texts[kind] = None
                continue
            r.raise_for_status()
            (target / kind / f"{sid}.csv.gz").write_bytes(r.content)
            digest.update(r.content)
            total += len(r.content)
            texts[kind] = _gunzip(r.content)
        clim = station_climate(texts["normals"], texts["daily"])
        quality[sid] = 2 if clim["jan_p10_c"] is not None else int(clim["jan_mean_c"] is not None)
        return quality[sid]

    chosen: dict[str, dict[str, Any]] = {}
    for t in towns or []:
        best = None
        for s in candidates(t, q):
            g = get(s)
            if g == 2:
                best = s
                break
            if g == 1 and best is None:
                best = s
        if best is not None:
            chosen[best["id"]] = best
    if not towns:
        for s in q:
            if get(s):
                chosen[s["id"]] = s
    stations = [chosen[k] for k in sorted(chosen)]
    (target / "stations.json").write_text(json.dumps(stations, ensure_ascii=False), "utf-8")
    c.write_fetch_meta(
        target,
        {
            "url": STATIONS_URL,
            "stations": len(stations),
            "stations_tried": len(quality),
            "bytes": total,
            "sha256": digest.hexdigest(),
            "licence": LICENCE,
            "licence_seen": LICENCE_SENTENCE,
            "licence_url": LICENCE_URL,
        },
    )
    return total


def normalise(src: Path, retrieved: str, log: Counter[str]) -> list[dict[str, Any]]:
    stations = json.loads((src / "stations.json").read_text(encoding="utf-8"))
    out = []
    for s in stations:
        sid = s["id"]

        def read(kind: str, sid: str = sid) -> str | None:
            p = src / kind / f"{sid}.csv.gz"
            return _gunzip(p.read_bytes()) if p.exists() else None

        clim = station_climate(read("normals"), read("daily"))
        if clim["jan_mean_c"] is None:
            log["station skipped: no 1991-2020 January data"] += 1
            continue
        if clim["jan_p10_c"] is None:
            log["station without P10 (too few full Januaries)"] += 1
        loc = s["location"]
        out.append(
            {
                "station_id": sid,
                "name": (s.get("name") or {}).get("en") or sid,
                "country": s["country"],
                "lat": loc["latitude"],
                "lon": loc["longitude"],
                "elevation_m": loc.get("elevation"),
                "period": f"{PERIOD[0]}-{PERIOD[1]}",
                "retrieved_at": retrieved,
                **clim,
            }
        )
        log["station"] += 1
    out.sort(key=lambda r: r["station_id"])
    return out


def staging_path() -> Path:
    return c.staging_dir() / f"{NAME}{STAGING_SUFFIX}"


def fetch_cmd(client: httpx.Client | None = None) -> int:
    from ev_pipeline.sources.geonames.adapter import staging_path as towns_path

    target = c.raw_dir(DIR)
    own = client is None
    client = client or net.safe_client(NAME, timeout=60, max_seconds=1800)
    try:
        size = fetch(client, target, read_towns(towns_path()))
    except (httpx.HTTPError, ValueError, OSError) as exc:
        print(f"fetch {NAME}: failed: {exc}")
        return 1
    finally:
        if own:
            client.close()
    c.log_step(step="fetch", source=NAME, input_=STATIONS_URL, output=c.rel(target),
               rows_out=size, unit="bytes")  # fmt: skip
    return 0


def normalise_cmd(from_fixtures: bool) -> int:
    src = c.FIXTURES_DIR / DIR if from_fixtures else c.raw_dir(DIR)
    if not (src / "stations.json").exists():
        print(f"normalise {NAME}: no data in {src} (run `ev fetch {NAME}` first)")
        return 1
    log: Counter[str] = Counter()
    rows = normalise(src, c.retrieved_at_for(src).isoformat(), log)
    out = staging_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    meta = {
        "source": NAME,
        "licence": LICENCE,
        "attribution": ATTRIBUTION,
        "confidence": "medium",
        "retrieved_at": c.retrieved_at_for(src).isoformat(),
        "from_fixtures": from_fixtures,
        "counts": dict(sorted(log.items())),
    }
    out.with_name(f"{NAME}.climate.meta.json").write_text(
        json.dumps(meta, indent=1) + "\n", encoding="utf-8"
    )
    c.log_step(step="normalise", source=NAME, input_=c.rel(src), output=c.rel(out),
               rows_out=len(rows), counts=dict(sorted(log.items())))  # fmt: skip
    return 0
