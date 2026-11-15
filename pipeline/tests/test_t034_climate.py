"""T-034: GeoNames towns, Meteostat January climate, towns/<cc>.json in the release."""

from __future__ import annotations

import gzip
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

import httpx
import pytest

from ev_pipeline.release.gate import load_registry, parse_registry
from ev_pipeline.release.towns import build_towns
from ev_pipeline.sources.geonames import adapter as gn
from ev_pipeline.sources.meteostat import adapter as ms

FIX = Path(__file__).parent / "fixtures"
REGISTRY = Path(__file__).resolve().parents[2] / "data" / "sources.yaml"


# --- geonames ----------------------------------------------------------------------------


def test_launch_countries_map_uk_to_gb() -> None:
    lc = gn.launch_countries()
    assert lc["GB"] == "uk" and lc["NL"] == "nl" and "UK" not in lc


def test_parse_keeps_launch_towns_and_rounds(tmp_path: Path) -> None:
    log: Counter[str] = Counter()
    towns = gn.parse(gn.read_zip(FIX / "geonames" / "cities5000.zip"), gn.launch_countries(), log)
    names = {t["name"] for t in towns}
    assert {"Brussels", "Berlin", "Amsterdam", "London", "Angoulême"} <= names
    assert "Madrid" not in names  # not a launch country
    assert log["skipped: not a town (PPLX/historical)"] == 1  # Zuidwijk
    bxl = next(t for t in towns if t["name"] == "Brussels")
    assert bxl["country"] == "be" and bxl["lat"] == 50.85 and bxl["id"] == "geonames:2800866"
    assert all(len(str(t["lat"]).split(".")[-1]) <= 2 for t in towns)


def test_names_in_ui_languages_from_alternates() -> None:
    log: Counter[str] = Counter()
    towns = gn.parse(gn.read_zip(FIX / "geonames" / "cities5000.zip"), gn.launch_countries(), log)
    gn.add_names(towns, [gn.read_zip(FIX / "geonames" / "alternatenames-BE.zip", "BE.txt")])
    bxl = next(t for t in towns if t["name"] == "Brussels")
    assert bxl["names"]["nl"] == "Brussel" and bxl["names"]["fr"] == "Bruxelles"
    assert bxl["names"]["de"] == "Brüssel" and set(bxl["names"]) <= set(gn.UI_LANGUAGES)


def test_alternates_skip_colloquial_historic_and_prefer_preferred() -> None:
    rows = "\n".join(
        [
            "1\t7\tnl\tOudnaam\t\t\t\t1\t\t",  # historic
            "2\t7\tnl\tBijnaam\t\t\t1\t\t\t",  # colloquial
            "3\t7\tnl\tGewoon\t\t\t\t\t\t",
            "4\t7\tnl\tVoorkeur\t1\t\t\t\t\t",
            "5\t7\tsv\tSvenska\t1\t\t\t\t\t",  # not a UI language
            "6\t8\tnl\tAnderDorp\t1\t\t\t\t\t",  # not one of our towns
        ]
    )
    assert gn.parse_alternates(rows, {"7"}) == {"7": {"nl": "Voorkeur"}}


def test_geonames_normalise_from_fixtures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EV_DATA_DIR", str(tmp_path))
    assert gn.normalise_cmd(from_fixtures=True) == 0
    lines = (tmp_path / "staging" / "geonames.towns.jsonl").read_text().splitlines()
    meta = json.loads((tmp_path / "staging" / "geonames.towns.meta.json").read_text())
    assert len(lines) == 6 and meta["licence"] == "CC-BY-4.0"
    assert meta["attribution"] == "GeoNames (geonames.org), CC BY 4.0"
    assert meta["retrieved_at"] == "2026-11-15"


def test_geonames_fetch_refuses_without_licence_sentence(tmp_path: Path) -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="readme without the licence line")

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(ValueError, match="licence"),
    ):
        gn.fetch(client, tmp_path)


def test_geonames_fetch_downloads_cities_and_alternates(tmp_path: Path) -> None:
    city = (FIX / "geonames" / "cities5000.zip").read_bytes()
    seen: list[str] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req.url.path)
        if req.url.path.endswith("readme.txt"):
            return httpx.Response(200, text="licensed under a " + gn.LICENCE_SENTENCE)
        if "alternatenames" in req.url.path:
            import io
            import zipfile

            cc = req.url.path.rsplit("/", 1)[1].removesuffix(".zip")
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as z:
                z.writestr(f"{cc}.txt", "")
            return httpx.Response(200, content=buf.getvalue())
        return httpx.Response(200, content=city)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        assert gn.fetch(client, tmp_path) > len(city)
    assert (tmp_path / "alternatenames-GB.zip").exists()
    assert sum("alternatenames" in p for p in seen) == len(gn.launch_countries())


# --- meteostat maths ---------------------------------------------------------------------


def _daily(rows: list[tuple[str, float | None]]) -> str:
    return "\n".join(f"{d},{'' if t is None else t},,,,,,,,," for d, t in rows)


def test_p10_inclusive_matches_known_values() -> None:
    assert ms.p10([float(x) for x in range(1, 11)]) == pytest.approx(1.9)
    assert ms.p10([0.0, 10.0]) == pytest.approx(1.0)


def test_station_climate_needs_enough_full_januaries() -> None:
    rows = [(f"{y}-01-{d:02d}", float(y - 2000)) for y in range(1991, 2021) for d in range(1, 26)]
    clim = ms.station_climate(None, _daily(rows))
    assert clim["jan_years"] == 30 and clim["jan_mean_method"] == "daily"
    assert clim["jan_mean_c"] == pytest.approx(5.5)  # mean of -9..20
    assert clim["jan_p10_c"] == pytest.approx(-6.1, abs=0.05)
    few = [(f"{y}-01-{d:02d}", 1.0) for y in range(1991, 2010) for d in range(1, 26)]  # 19 yrs
    assert ms.station_climate(None, _daily(few))["jan_p10_c"] is None
    short = [(f"{y}-01-{d:02d}", 1.0) for y in range(1991, 2021) for d in range(1, 15)]
    assert ms.station_climate(None, _daily(short))["jan_years"] == 0


def test_days_outside_the_period_and_tmin_tmax_fallback() -> None:
    rows = [f"{y}-01-{d:02d},,{-2.0},{4.0},,,,,,," for y in range(1991, 2021) for d in range(1, 21)]
    rows += [f"1985-01-{d:02d},-30,,,,,,,,," for d in range(1, 21)]
    clim = ms.station_climate(None, "\n".join(rows))
    assert clim["jan_mean_c"] == pytest.approx(1.0) and clim["jan_p10_c"] == pytest.approx(1.0)


def test_normals_fill_months_daily_lacks() -> None:
    normals = "1961,1990,1,-9,-9,1,1,1,1\n" + "\n".join(
        f"1991,2020,{m},{m},{m + 2},1,1,1,1" for m in range(1, 13)
    )
    clim = ms.station_climate(normals, None)
    assert clim["months_mean_c"][0] == 2.0 and clim["months_mean_c"][11] == 13.0
    assert clim["jan_mean_method"] == "normals-midrange" and clim["jan_p10_c"] is None


def test_qualifying_and_candidates() -> None:
    stations = json.loads((FIX / "meteostat" / "stations.json").read_text())
    q = ms.qualifying(stations, {"NL", "BE", "DE"})
    assert {s["id"] for s in q} >= {"06260", "06447", "10381", "XXXXX"}
    utrecht = {"lat": 52.09, "lon": 5.12, "elevation_m": 5}
    assert [s["id"] for s in ms.candidates(utrecht, q)][:2] == ["XXXXX", "06260"]
    high = {**utrecht, "elevation_m": 900}
    assert ms.candidates(high, q) == []


def test_meteostat_normalise_from_fixtures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EV_DATA_DIR", str(tmp_path))
    assert ms.normalise_cmd(from_fixtures=True) == 0
    rows = [json.loads(x) for x in (tmp_path / "staging" / "meteostat.climate.jsonl").open()]
    by = {r["station_id"]: r for r in rows}
    assert "XXXXX" not in by  # no files -> skipped
    bilt = by["06260"]
    assert bilt["jan_mean_c"] == 3.6 and bilt["jan_p10_c"] == -2.1 and bilt["jan_years"] == 30
    assert bilt["months_mean_c"][6] == 18.2  # July from daily
    assert bilt["months_mean_c"][3] is not None  # April from the normals file
    meta = json.loads((tmp_path / "staging" / "meteostat.climate.meta.json").read_text())
    assert meta["confidence"] == "medium" and meta["licence"] == "CC-BY-4.0"


def test_meteostat_fetch_tries_next_station_when_nearest_has_no_temperature(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(ms, "launch_countries", lambda: {"NL": "nl", "BE": "be", "DE": "de"})
    stations = json.loads((FIX / "meteostat" / "stations.json").read_text())
    calls: list[str] = []

    def handler(req: httpx.Request) -> httpx.Response:
        p = req.url.path
        calls.append(p)
        if req.url.host == "dev.meteostat.net":
            return httpx.Response(200, text=ms.LICENCE_SENTENCE + " International")
        if p.endswith("lite.json.gz"):
            return httpx.Response(200, content=gzip.compress(json.dumps(stations).encode()))
        kind, name = p.split("/")[-2:]
        f = FIX / "meteostat" / kind / name
        return httpx.Response(200, content=f.read_bytes()) if f.exists() else httpx.Response(404)

    towns = [{"lat": 52.09, "lon": 5.12, "elevation_m": 5}]  # nearest = the empty gauge
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        ms.fetch(client, tmp_path, towns)
    chosen = json.loads((tmp_path / "stations.json").read_text())
    assert [s["id"] for s in chosen] == ["06260"]
    assert any("XXXXX" in c for c in calls)
    meta = json.loads((tmp_path / "_fetch.json").read_text())
    assert meta["stations"] == 1 and meta["stations_tried"] == 2


def test_meteostat_fetch_refuses_without_licence(tmp_path: Path) -> None:
    transport = httpx.MockTransport(lambda r: httpx.Response(200, text="x"))
    with httpx.Client(transport=transport) as c, pytest.raises(ValueError, match="licence"):
        ms.fetch(c, tmp_path, [])


# --- release towns -----------------------------------------------------------------------


def _staging(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("EV_DATA_DIR", str(tmp_path))
    assert gn.normalise_cmd(from_fixtures=True) == 0
    assert ms.normalise_cmd(from_fixtures=True) == 0
    return tmp_path / "staging"


def test_build_towns_joins_nearest_station_with_provenance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    st = _staging(tmp_path, monkeypatch)
    res = build_towns(st, load_registry(REGISTRY), 3, "2026-11-15T01:00:00+00:00")
    assert res.log["status"] == "shipped"
    assert set(res.documents) == {"be", "de", "fr", "nl", "uk"}
    nl = res.documents["nl"]
    ams = next(t for t in nl["towns"] if t["name"] == "Amsterdam")
    assert ams["station_id"] == "06260" and 0 < ams["station_km"] < 60
    assert nl["stations"]["06260"]["jan_p10_c"] == -2.1
    prov = nl["provenance"]["climate"]
    assert prov["source_id"] == "meteostat" and prov["licence"] == "CC-BY-4.0"
    assert prov["retrieved_at"] == "2026-11-15" and prov["confidence"] == "medium"
    assert nl["provenance"]["towns"]["source_id"] == "geonames"
    assert {s["id"] for s in nl["sources"]} == {"geonames", "meteostat"}
    fr = res.documents["fr"]
    assert fr["towns"][0]["station_id"] is None and fr["stations"] == {}  # no FR station
    assert res.log["no station in range"] >= 2  # Angoulême, London


def test_build_towns_prefers_a_station_with_p10() -> None:
    from ev_pipeline.release.towns import nearest

    town = {"lat": 52.0, "lon": 5.0}
    near = {"station_id": "a", "lat": 52.0, "lon": 5.01, "jan_p10_c": None, "jan_mean_c": 3}
    far = {"station_id": "b", "lat": 52.1, "lon": 5.0, "jan_p10_c": -2, "jan_mean_c": 3}
    hit = nearest(town, [near, far])
    assert hit is not None and hit[0]["station_id"] == "b"
    hit = nearest(town, [near])
    assert hit is not None and hit[0]["station_id"] == "a"


def test_towns_gate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    st = _staging(tmp_path, monkeypatch)

    def reg(geo: str, met: str) -> Any:
        return parse_registry(
            {"sources": [
                {"id": "geonames", "name": "GeoNames", "licence": "CC-BY-4.0", "status": geo},
                {"id": "meteostat", "name": "Meteostat", "licence": "CC-BY-4.0", "status": met},
            ]}
        )  # fmt: skip

    blocked = build_towns(st, reg("blocked", "active"), 3, "t")
    assert blocked.documents == {} and blocked.log["gated"] == {"geonames": "status blocked"}
    no_climate = build_towns(st, reg("active", "blocked"), 3, "t")
    nl = no_climate.documents["nl"]
    assert nl["stations"] == {} and nl["provenance"]["climate"] is None
    assert all(t["station_id"] is None for t in nl["towns"])
    assert [s["id"] for s in nl["sources"]] == ["geonames"]


def test_release_writes_town_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from datetime import UTC, datetime

    from ev_pipeline.release.build import release_cmd
    from ev_pipeline.release.publish import read_manifest

    fix = FIX / "release"
    d = tmp_path / "data"
    (d / "seed").mkdir(parents=True)
    shutil.copytree(fix / "staging", d / "staging")
    shutil.copytree(fix / "taxonomy", d / "taxonomy")
    for n in ("models", "variants", "platforms", "battery_packs", "variant_links"):
        shutil.copy(fix / f"{n}.yaml", d / "seed" / f"{n}.yaml")
    shutil.copy(fix / "field_sources.yaml", d / "field_sources.yaml")
    import yaml

    reg = yaml.safe_load((fix / "sources.yaml").read_text())
    for sid in ("geonames", "meteostat"):
        reg["sources"].append({"id": sid, "name": sid, "licence": "CC-BY-4.0", "status": "active"})
    (d / "sources.yaml").write_text(yaml.safe_dump(reg))
    monkeypatch.setenv("EV_DATA_DIR", str(d))
    monkeypatch.delenv("EV_RUNS_DIR", raising=False)
    assert gn.normalise_cmd(from_fixtures=True) == 0
    assert ms.normalise_cmd(from_fixtures=True) == 0
    assert release_cmd(False, data_dir=d, now=datetime(2026, 11, 15, 1, tzinfo=UTC)) == 0
    out = d / "releases" / "1" / "towns"
    assert sorted(p.name for p in out.iterdir()) == [
        "be.json", "de.json", "fr.json", "nl.json", "uk.json"
    ]  # fmt: skip
    nl = json.loads((out / "nl.json").read_text())
    assert nl["release"] == 1 and nl["towns"]
    m = read_manifest(d / "releases" / "1")
    assert m is not None and any(e["asset"] == "towns.nl.json" for e in m["files"])
    assert "Towns + climate" in (d / "releases" / "1" / "coverage.md").read_text()


# --- ERA5-Land stub + refresh --------------------------------------------------------------


def test_era5_land_is_skipped_without_the_cds_key(tmp_path: Path) -> None:
    from datetime import UTC, datetime

    from ev_pipeline.refresh.plan import plan

    shutil.copy(REGISTRY, tmp_path / "sources.yaml")
    now = datetime(2026, 11, 16, 1, tzinfo=UTC)
    got = {p.id: (p.action, p.reason) for p in plan(tmp_path, {}, now, env={})}
    assert got["era5-land"] == ("skip", "needs CDSAPI_KEY")
    assert got["geonames"][0] == "run" and got["meteostat"][0] == "run"
    order = [p.id for p in plan(tmp_path, {}, now, env={})]
    assert order.index("geonames") < order.index("meteostat")  # towns first: stations follow


def test_era5_land_stub_says_what_is_missing(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    from ev_pipeline.sources.era5_land import adapter as era5

    monkeypatch.delenv("CDSAPI_KEY", raising=False)
    assert era5.fetch_cmd() == 1 and "CDSAPI_KEY" in capsys.readouterr().out
