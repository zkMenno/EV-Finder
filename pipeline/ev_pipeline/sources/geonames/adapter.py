"""GeoNames adapter (CC BY 4.0): towns for Trip fit search and climate lookup (T-034).

Source: `cities5000.zip` from download.geonames.org (every populated place with 5,000+
people; readme: "licensed under a Creative Commons Attribution 4.0 License"; fetch refuses
when that sentence is gone from readme.txt). Credit: "GeoNames (geonames.org), CC BY 4.0".

Kept: populated places (feature class P, not PPLX = parts of a place, not PPLH/PPLQ/PPLW =
historical/abandoned/destroyed) in the launch countries (config/countries/*.yaml; `uk` is
GeoNames `GB`). Coordinates are rounded to 2 decimals (~1 km); towns are search targets, not
addresses. Names in our six UI languages (en, nl, de, fr, es, it) come from the per-country
`alternatenames/<CC>.zip` files (same licence): `names: {lang: name}`, preferred names first,
no colloquial or historic names. So "Brussel", "Bruxelles" and "Brüssel" all find Brussels.

Output: `data/staging/geonames.towns.jsonl`, one town per line, sorted by id.
"""

from __future__ import annotations

import hashlib
import io
import json
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

import httpx

from ev_pipeline import net
from ev_pipeline.sources import _common as c

NAME = "geonames"
DIR = "geonames"
STAGING_SUFFIX = ".towns.jsonl"
URL = "https://download.geonames.org/export/dump/cities5000.zip"
README_URL = "https://download.geonames.org/export/dump/readme.txt"
LICENCE_SENTENCE = "Creative Commons Attribution 4.0 License"
LICENCE = "CC-BY-4.0"
ATTRIBUTION = "GeoNames (geonames.org), CC BY 4.0"
FILE_NAME = "cities5000.zip"
MEMBER = "cities5000.txt"

ISO_OVERRIDES = {"uk": "GB"}  # our country id -> ISO 3166-1 alpha-2 where they differ
SKIP_FEATURES = {"PPLX", "PPLH", "PPLQ", "PPLW", "PPLCH"}
UI_LANGUAGES = ("en", "nl", "de", "fr", "es", "it")
ALT_URL = "https://download.geonames.org/export/dump/alternatenames/{cc}.zip"
COORD_DECIMALS = 2

COLUMNS = [
    "geonameid", "name", "asciiname", "alternatenames", "latitude", "longitude",
    "feature_class", "feature_code", "country_code", "cc2", "admin1", "admin2", "admin3",
    "admin4", "population", "elevation", "dem", "timezone", "modified",
]  # fmt: skip


def launch_countries(config_dir: Path | None = None) -> dict[str, str]:
    """ISO code -> our country id, from config/countries/*.yaml file names."""
    d = config_dir or c.REPO_DIR / "config" / "countries"
    out = {}
    for p in sorted(d.glob("*.yaml")):
        ours = p.stem
        out[ISO_OVERRIDES.get(ours, ours.upper())] = ours
    return out


def parse_alternates(text: str, ids: set[str]) -> dict[str, dict[str, str]]:
    """alternatenames rows -> {geonameid: {lang: name}} for our UI languages.
    Columns: id, geonameid, isolanguage, name, isPreferredName, isShortName, isColloquial,
    isHistoric, from, to. Preferred names win; colloquial and historic names are skipped."""
    best: dict[str, dict[str, tuple[int, str]]] = {}
    for line in text.splitlines():
        f = line.split("\t")
        if len(f) < 8 or f[1] not in ids or f[2] not in UI_LANGUAGES:
            continue
        if f[6] == "1" or f[7] == "1" or not f[3].strip():
            continue
        rank = 0 if f[4] == "1" else (1 if f[5] != "1" else 2)
        cur = best.setdefault(f[1], {}).get(f[2])
        if cur is None or rank < cur[0]:
            best[f[1]][f[2]] = (rank, f[3].strip())
    return {gid: {lang: v[1] for lang, v in sorted(m.items())} for gid, m in best.items()}


def parse(text: str, countries: dict[str, str], log: Counter[str]) -> list[dict[str, Any]]:
    out = []
    for line in text.splitlines():
        if not line.strip():
            continue
        f = dict(zip(COLUMNS, line.split("\t"), strict=False))
        if f.get("feature_class") != "P":
            continue
        cc = countries.get(f.get("country_code", ""))
        if cc is None:
            continue
        if f.get("feature_code") in SKIP_FEATURES:
            log["skipped: not a town (PPLX/historical)"] += 1
            continue
        try:
            lat, lon = float(f["latitude"]), float(f["longitude"])
            pop = int(f.get("population") or 0)
        except (KeyError, ValueError):
            log["skipped: bad coordinates or population"] += 1
            continue
        elev_raw = f.get("elevation") or f.get("dem") or ""
        try:
            elevation = int(float(elev_raw)) if elev_raw not in ("", "-9999") else None
        except ValueError:
            elevation = None
        town: dict[str, Any] = {
            "id": f"geonames:{f['geonameid']}",
            "name": f["name"],
            "ascii": f.get("asciiname") or f["name"],
            "country": cc,
            "admin1": f.get("admin1") or None,
            "lat": round(lat, COORD_DECIMALS),
            "lon": round(lon, COORD_DECIMALS),
            "population": pop,
            "elevation_m": elevation,
        }
        out.append(town)
        log[f"town {cc}"] += 1
    out.sort(key=lambda t: t["id"])
    return out


def read_zip(path: Path, member: str = MEMBER) -> str:
    with zipfile.ZipFile(path) as z:
        return z.read(member).decode("utf-8")


def add_names(towns: list[dict[str, Any]], alt_texts: list[str]) -> None:
    ids = {t["id"].removeprefix("geonames:") for t in towns}
    names: dict[str, dict[str, str]] = {}
    for text in alt_texts:
        for gid, m in parse_alternates(text, ids).items():
            names.setdefault(gid, {}).update(m)
    for t in towns:
        m = names.get(t["id"].removeprefix("geonames:"))
        if m:
            t["names"] = m


def fetch(client: httpx.Client, target: Path) -> int:
    readme = client.get(README_URL)
    readme.raise_for_status()
    if LICENCE_SENTENCE not in readme.text:
        raise ValueError(f"GeoNames readme no longer says '{LICENCE_SENTENCE}'; check the licence")
    resp = client.get(URL)
    resp.raise_for_status()
    zipfile.ZipFile(io.BytesIO(resp.content)).getinfo(MEMBER)  # fail early on a broken zip
    target.mkdir(parents=True, exist_ok=True)
    (target / FILE_NAME).write_bytes(resp.content)
    total = len(resp.content)
    for iso in sorted(launch_countries()):
        alt = client.get(ALT_URL.format(cc=iso))
        alt.raise_for_status()
        zipfile.ZipFile(io.BytesIO(alt.content)).getinfo(f"{iso}.txt")
        (target / f"alternatenames-{iso}.zip").write_bytes(alt.content)
        total += len(alt.content)
    c.write_fetch_meta(
        target,
        {
            "url": URL,
            "bytes": total,
            "sha256": hashlib.sha256(resp.content).hexdigest(),
            "last_modified": resp.headers.get("last-modified"),
            "licence": LICENCE,
            "licence_seen": LICENCE_SENTENCE,
            "licence_url": README_URL,
        },
    )
    return total


def staging_path() -> Path:
    return c.staging_dir() / f"{NAME}{STAGING_SUFFIX}"


def write_towns(towns: list[dict[str, Any]], meta: dict[str, Any]) -> int:
    out = staging_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for t in towns:
            fh.write(json.dumps(t, ensure_ascii=False, sort_keys=True) + "\n")
    out.with_name(f"{NAME}.towns.meta.json").write_text(
        json.dumps(meta, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return len(towns)


def fetch_cmd(client: httpx.Client | None = None) -> int:
    target = c.raw_dir(DIR)
    own = client is None
    client = client or net.safe_client(NAME, timeout=120)
    try:
        size = fetch(client, target)
    except (httpx.HTTPError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print(f"fetch {NAME}: failed: {exc}")
        return 1
    finally:
        if own:
            client.close()
    c.log_step(step="fetch", source=NAME, input_=URL, output=c.rel(target), rows_out=size,
               unit="bytes")  # fmt: skip
    return 0


def normalise_cmd(from_fixtures: bool) -> int:
    src = c.FIXTURES_DIR / DIR if from_fixtures else c.raw_dir(DIR)
    if not (src / FILE_NAME).exists():
        print(f"normalise {NAME}: no data in {src} (run `ev fetch {NAME}` first)")
        return 1
    log: Counter[str] = Counter()
    countries = launch_countries()
    towns = parse(read_zip(src / FILE_NAME), countries, log)
    alts = [
        read_zip(p, f"{p.stem.removeprefix('alternatenames-')}.txt")
        for p in sorted(src.glob("alternatenames-*.zip"))
    ]
    add_names(towns, alts)
    log["towns with names in UI languages"] = sum(1 for t in towns if t.get("names"))
    retrieved = c.retrieved_at_for(src).isoformat()
    meta = {
        "source": NAME,
        "licence": LICENCE,
        "attribution": ATTRIBUTION,
        "retrieved_at": retrieved,
        "download": {k: c.read_fetch_meta(src).get(k) for k in ("url", "sha256", "fetched_at")},
        "from_fixtures": from_fixtures,
        "counts": dict(sorted(log.items())),
    }
    n = write_towns(towns, meta)
    c.log_step(step="normalise", source=NAME, input_=c.rel(src), output=c.rel(staging_path()),
               rows_out=n, counts=dict(sorted(log.items())))  # fmt: skip
    return 0
