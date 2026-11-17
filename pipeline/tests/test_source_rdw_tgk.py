"""RDW TGK (type-approval register) adapter: recorded subset of the 2026-11-15 fetch. No network."""

import json
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from ev_pipeline import net
from ev_pipeline.schema_models import Confidence, FactField
from ev_pipeline.sources.rdw_tgk import adapter

FIXTURE = Path(__file__).parent / "fixtures" / "rdw_tgk"
DAY = date(2026, 11, 15)
F = FactField


def _records() -> dict[str, adapter.SourceRecord]:
    recs = adapter.normalise(FIXTURE, DAY)
    return {r.record_key.split(":", 1)[1].rsplit("|", 1)[0]: r for r in recs}


def _v(rec: adapter.SourceRecord, field: FactField) -> float | None:
    s = rec.specs.get(field)
    return None if s is None else float(s.value)  # type: ignore[arg-type]


def test_fixture_is_small_and_has_no_plates() -> None:
    total = 0
    for name in ("versions.json", "energy.json", "basis.json", "names.json"):
        text = (FIXTURE / name).read_text()
        total += len(json.loads(text))
        assert '"kenteken"' not in text
    assert total <= 200


def test_records_carry_licence_source_and_high_confidence() -> None:
    recs = adapter.normalise(FIXTURE, DAY)
    assert recs
    for r in recs:
        assert r.source.id.root == "rdw-tgk"
        assert r.source.licence == "CC0-1.0"
        assert r.source.attribution
        assert r.kind == "spec"
        assert r.confidence == Confidence.high
        assert r.retrieved_at == DAY
        assert "[typegoedkeuringsnummer|variant|uitvoering|revisie]" in r.record_key
        assert r.make and r.model and r.year


def test_units_are_metric_and_canonical() -> None:
    for r in adapter.normalise(FIXTURE, DAY):
        for field, spec in r.specs.items():
            assert spec.unit == adapter.UNITS[field]
            lo, hi = adapter.PLAUSIBLE[field]
            assert lo <= float(spec.value) <= hi  # type: ignore[arg-type]


def test_nedc_never_fills_wltp() -> None:
    recs = _records()
    zoe22 = recs["e2*2007/46*0251*00|AGV|AGVYA0"]  # Zoe ph1, NEDC era
    assert _v(zoe22, F.nedc_range_km) == 210
    assert _v(zoe22, F.nedc_consumption_kwh_100km) == 14.6  # 146 Wh/km
    for f in (F.wltp_range_km, F.wltp_range_km_worst, F.consumption_kwh_100km):
        assert f not in zoe22.specs
    for r in recs.values():
        if F.nedc_range_km in r.specs and F.wltp_range_km in r.specs:
            # Both tests stated: the WLTP value must come from the WLTP columns, not NEDC.
            assert _v(r, F.wltp_range_km) != _v(r, F.nedc_range_km)


def test_wltp_best_and_worst_are_ordered() -> None:
    recs = adapter.normalise(FIXTURE, DAY)
    for r in recs:
        if F.wltp_range_km_worst in r.specs:
            assert _v(r, F.wltp_range_km) > _v(r, F.wltp_range_km_worst)  # type: ignore[operator]
        if F.wltp_consumption_kwh_100km_worst in r.specs:
            assert _v(r, F.consumption_kwh_100km) < _v(r, F.wltp_consumption_kwh_100km_worst)  # type: ignore[operator]
    ipace = _records()["e11*2007/46*4311*00|A|502"]
    assert (_v(ipace, F.wltp_range_km), _v(ipace, F.wltp_range_km_worst)) == (480, 420)


def test_swapped_bounds_are_reordered() -> None:
    stats = adapter.Stats()
    row = {
        "actieradiusvolledigelekwltpogr": "290",  # glossary: Ogr is the best case; swapped
        "actieradiusvolledigelekwltpbgr": "310",
        "verbruikvolledigelekwltpogr": "170",
        "verbruikvolledigelekwltpbgr": "160",
    }
    vals = adapter.energy_values([row], stats)
    assert vals[F.wltp_range_km] == 310 and vals[F.wltp_range_km_worst] == 290
    assert vals[F.consumption_kwh_100km] == 16.0
    assert vals[F.wltp_consumption_kwh_100km_worst] == 17.0
    assert stats.wltp_swapped == 1


def test_single_or_equal_wltp_bound_has_no_worst() -> None:
    vals = adapter.energy_values(
        [{"actieradiusvolledigelekwltpbgr": "285", "verbruikvolledigelekwltpogr": "194"}],
        adapter.Stats(),
    )
    assert vals[F.wltp_range_km] == 285 and F.wltp_range_km_worst not in vals
    assert vals[F.consumption_kwh_100km] == 19.4
    assert F.wltp_consumption_kwh_100km_worst not in vals


def test_running_order_mass_never_becomes_weight() -> None:
    for r in adapter.normalise(FIXTURE, DAY):
        assert F.weight_kg not in r.specs
        assert F.kerb_mass_kg not in r.specs
    zoe = _records()["e2*2007/46*0251*13|0V0Y|MALEA0400000"]
    assert _v(zoe, F.mass_running_order_kg) == 1548


def test_30min_power_never_becomes_peak_power_or_kw_evidence() -> None:
    for r in adapter.normalise(FIXTURE, DAY):
        assert F.power_kw not in r.specs
        assert "kW" not in (r.variant_name or "")  # the matcher reads "<n> kW" as peak power
    i3 = _records()["e1*2007/46*1213*05|1Z61|0A140000"]
    assert _v(i3, F.power_30min_kw) == 75
    assert i3.variant_name == "I3 · 30-min 75 · 1320 kg"


def test_dual_motor_version_has_no_30min_power() -> None:
    m3 = _records()["e4*2007/46*1293*00|E3D|BB1N"]  # Model 3 AWD: one energy row per motor
    assert F.power_30min_kw not in m3.specs
    assert _v(m3, F.wltp_range_km) == 560


def test_dimensions_only_when_bounds_agree() -> None:
    stats = adapter.Stats()
    vals = adapter.basis_values(
        {
            "lengteondergrens": "4085",
            "lengtebovengrens": "4085",
            "hoogteondergrens": "1540",
            "hoogtebovengrens": "1562",
            "massarijklaarondergrens": "1500",
        },
        stats,
    )
    assert vals[F.length_mm] == 4085
    assert F.height_mm not in vals
    assert vals[F.mass_running_order_kg] == 1500  # one bound only: the stated value
    assert stats.bounds_differ["height_mm"] == 1


def test_revision_conflict_drops_the_field() -> None:
    stats = adapter.Stats()
    recs = {
        r.record_key.split(":", 1)[1].rsplit("|", 1)[0]: r
        for r in adapter.normalise(FIXTURE, DAY, stats)
    }
    zeekr = recs["e9*2018/858*11470*01|A|1"]  # WLTP changed between revisions
    assert F.wltp_range_km not in zeekr.specs
    assert stats.revision_conflict["wltp_range_km"] == 1
    assert zeekr.record_key.endswith("|2")  # newest revision in the key


def test_non_bev_and_missing_versions_are_skipped() -> None:
    stats = adapter.Stats()
    keys = {r.record_key for r in adapter.normalise(FIXTURE, DAY, stats)}
    assert stats.not_bev == 1  # a version with a petrol row (proxy hit without cylinders)
    assert stats.no_energy_row == 1
    assert not any("e1*2001/116*0242*43" in k for k in keys)


def test_model_and_year_come_from_plates() -> None:
    v = adapter.load_versions(
        [
            {
                "typegoedkeuringsnummer": "T",
                "variant": "A",
                "uitvoering": "1",
                "merk": "X",
                "handelsbenaming": "ONE",
                "first": "20190301",
                "last": "20200101",
                "n": "3",
            },
            {
                "typegoedkeuringsnummer": "T",
                "variant": "A",
                "uitvoering": "1",
                "merk": "X",
                "handelsbenaming": "ONE PLUS",
                "first": "20180701",
                "last": "20210101",
                "n": "9",
            },
        ]
    )[("T", "A", "1")]
    assert v.names.most_common(1)[0][0] == ("X", "ONE PLUS")
    assert (v.first_year, v.last_year, v.cars) == (2018, 2021, 12)


def test_soql_in_escapes_quotes() -> None:
    assert adapter.soql_in(["a'b", "c"]) == "'a''b', 'c'"


def _meta(name: str) -> dict[str, object]:
    return {
        "name": name,
        "rowsUpdatedAt": 1794628529,
        "license": {"name": "Public Domain"},
        "licenseId": "PUBLIC_DOMAIN",
        "metadata": {"custom_fields": {"Licentie": {"Licentie": "Creative Commons 0 (CC0)"}}},
    }


def _transport(calls: list[httpx.Request], licence: str = "PUBLIC_DOMAIN") -> httpx.MockTransport:
    fixture = {
        name: json.loads((FIXTURE / f).read_text())
        for name, f in (
            (adapter.ENERGY, "energy.json"),
            (adapter.BASIS, "basis.json"),
            (adapter.NAMES, "names.json"),
            (adapter.PLATES, "versions.json"),
        )
    }

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        path = urlparse(str(request.url)).path
        ds = path.rsplit("/", 1)[-1].removesuffix(".json")
        if path.startswith("/api/views/"):
            m = _meta(ds)
            if licence != "PUBLIC_DOMAIN":
                m["licenseId"], m["metadata"] = licence, {}
            return httpx.Response(200, json=m)
        q = parse_qs(urlparse(str(request.url)).query)
        if int(q["$offset"][0]) > 0:
            return httpx.Response(200, json=[])
        rows = fixture[ds]
        if ds != adapter.PLATES:
            where = q["$where"][0]
            rows = [r for r in rows if f"'{r['typegoedkeuringsnummer']}'" in where]
        return httpx.Response(200, json=rows)

    return httpx.MockTransport(handler)


def test_fetch_batches_and_filters(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(adapter, "BATCH", 5)
    calls: list[httpx.Request] = []
    client = net.safe_client(adapter.NAME, transport=_transport(calls), hosts=["opendata.rdw.nl"])
    n = adapter.fetch(client, tmp_path, sleep_s=0)
    tans = {
        r["typegoedkeuringsnummer"] for r in json.loads((FIXTURE / "versions.json").read_text())
    }
    assert n == len(adapter.load_versions(json.loads((FIXTURE / "versions.json").read_text())))
    tgk_calls = [
        c for c in calls if "/resource/" in str(c.url) and adapter.PLATES not in str(c.url)
    ]
    assert len(tgk_calls) == 3 * -(-len(tans) // 5)  # 3 datasets per batch of 5 TANs
    meta = json.loads((tmp_path / "_fetch.json").read_text())
    assert set(meta["datasets"]) == set(adapter.DATASETS)
    assert meta["batch_tans"] == 5
    assert adapter.normalise(tmp_path, DAY) == adapter.normalise(FIXTURE, DAY)


def test_fetch_and_normalise_cmds_use_the_folder_refresh_snapshots(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regression (T-116): fetch wrote data/raw/rdw-tgk, `ev refresh` snapshots data/raw/rdw_tgk
    (raw_dir_name) -> SnapshotError, and the whole release was skipped."""
    from ev_pipeline.refresh.plan import raw_dir_name

    monkeypatch.setenv("EV_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(adapter, "SLEEP_S", 0)
    monkeypatch.setattr(adapter.fetch, "__defaults__", (0,))
    client = net.safe_client(adapter.NAME, transport=_transport([]), hosts=["opendata.rdw.nl"])
    assert adapter.fetch_cmd(client) == 0
    snap_dir = tmp_path / "raw" / raw_dir_name(adapter)
    assert (snap_dir / adapter.VERSIONS_FILE).exists()
    assert not (tmp_path / "raw" / adapter.NAME).exists()
    assert adapter.normalise_cmd(from_fixtures=False) == 0
    assert (tmp_path / "staging" / f"{adapter.NAME}.records.jsonl").stat().st_size > 0


def test_fetch_refuses_changed_licence(tmp_path: Path) -> None:
    client = net.safe_client(
        adapter.NAME, transport=_transport([], licence="OTHER"), hosts=["opendata.rdw.nl"]
    )
    with pytest.raises(adapter.LicenceChanged):
        adapter.fetch(client, tmp_path, sleep_s=0)


def test_probe_unchanged() -> None:
    meta = json.loads((FIXTURE / "_fetch.json").read_text())
    for ds in adapter.DATASETS:
        meta["datasets"][ds]["dataset_rows_updated_at"] = 1794628529
    client = net.safe_client(adapter.NAME, transport=_transport([]), hosts=["opendata.rdw.nl"])
    assert adapter.probe_unchanged(client, meta) is True
    meta["datasets"][adapter.ENERGY]["dataset_rows_updated_at"] = 1
    assert adapter.probe_unchanged(client, meta) is False
    assert adapter.probe_unchanged(client, {}) is None
