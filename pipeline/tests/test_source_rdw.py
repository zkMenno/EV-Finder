"""RDW adapter on recorded samples of the grouped SoQL responses. No network."""

import json
from datetime import date
from pathlib import Path

import httpx
import pytest

from ev_pipeline.schema_models import Confidence, Country, FactField
from ev_pipeline.sources.rdw import adapter

FIXTURE = Path(__file__).parent / "fixtures" / "rdw"
DAY = date(2026, 11, 15)
FIXTURE_FILES = (
    "page-000.json",
    adapter.PRICE_FILE,
    adapter.SAMPLE_FILE,
    *adapter.PRICE_FILES.values(),
)


def test_fixture_is_a_small_sample() -> None:
    for name in FIXTURE_FILES:
        assert len(json.loads((FIXTURE / name).read_text())) <= 200, name


def test_fixture_holds_no_plates() -> None:
    for name in FIXTURE_FILES:
        assert "kenteken" not in (FIXTURE / name).read_text(), name


def test_normalise_counts() -> None:
    records = [r for r in adapter.normalise(FIXTURE, DAY) if r.kind == "registration_count"]
    assert len(records) == 118
    for rec in records:
        assert rec.country == Country.NL
        assert rec.confidence == Confidence.high
        assert rec.source.licence == "CC0-1.0"
        assert rec.source.attribution
        assert list(rec.specs) == [FactField.registered_count]
        assert rec.specs[FactField.registered_count].unit == "count"
    [m3_2019] = [r for r in records if r.record_key == "m9d7-ebf2:TESLA|MODEL 3|2019"]
    assert (m3_2019.make, m3_2019.model, m3_2019.year) == ("TESLA", "MODEL 3", 2019)
    assert m3_2019.specs[FactField.registered_count].value == 25235


def _specs() -> dict[str, object]:
    return {r.record_key: r for r in adapter.normalise(FIXTURE, DAY) if r.kind == "spec"}


def test_spec_records_carry_provenance_and_weight() -> None:
    specs = _specs()
    assert specs
    fine_grouping = "[merk|handelsbenaming|jaar|type|variant"
    for key, rec in specs.items():
        assert rec.confidence == Confidence.medium
        assert rec.source.licence == "CC0-1.0" and rec.source.attribution
        fields = set(rec.specs) - {FactField.registered_count}
        assert rec.specs[FactField.registered_count].value >= adapter.MIN_SAMPLE
        assert FactField.power_kw not in fields  # RDW power is matcher evidence only
        if FactField.price_new in fields:
            assert rec.country == Country.NL and rec.specs[FactField.price_new].unit == "EUR"
            assert rec.source.url.endswith(adapter.DATASET)
        else:
            assert rec.source.url.endswith(adapter.FUEL_DATASET)
        if fine_grouping in key:  # T-054: one record per type-approval group, codes in the key
            assert key.startswith(f"{adapter.DATASET}+{adapter.FUEL_DATASET}{fine_grouping}")
            assert fields and "#" not in key
            continue
        assert "[merk|handelsbenaming|jaar]:" in key  # the grouping is in the key
        assert len(fields) == 1  # one field per coarse record, with its own count
        assert rec.variant_name is None


def test_wltp_values_and_units() -> None:
    specs = _specs()
    k = "8ys7-d773+m9d7-ebf2[merk|handelsbenaming|jaar]:TESLA|MODEL 3|2024"
    rng = specs[f"{k}#wltp_range_km"].specs[FactField.wltp_range_km]
    cons = specs[f"{k}#consumption_kwh_100km"].specs[FactField.consumption_kwh_100km]
    assert (rng.value, rng.unit) == (513, "km")
    assert (cons.value, cons.unit) == (13.2, "kWh/100km")  # 132 Wh/km


def test_wide_spread_group_emits_nothing() -> None:
    # Model 3 2019 mixes Standard Range Plus and Long Range: range and price are too wide.
    drops = adapter.Drops()
    records = adapter.normalise(FIXTURE, DAY, drops)
    keys = {r.record_key for r in records}
    assert not any("TESLA|MODEL 3|2019#" in k for k in keys if "wltp" in k or "price" in k)
    sample = json.loads((FIXTURE / adapter.SAMPLE_FILE).read_text())
    g = adapter._rollup(sample, 0)[("TESLA", "MODEL 3", "2019")]  # sample is per code group
    for col in ("range_km", "price_eur"):
        s = adapter.spread_of(g[col])
        assert s is not None and s.n >= adapter.MIN_SAMPLE and s.iqr_ratio > adapter.MAX_IQR_RATIO
    assert drops.wide["wltp_range_km"] > 0 and drops.wide["price_new"] > 0


def test_fixture_wide_group_is_recovered_per_type_approval_variant() -> None:
    """T-054 on real data: Model 3 2019 splits into SR+ (E1R), LR AWD (E3D) and E3R."""
    specs = _specs()
    pre = f"{adapter.DATASET}+{adapter.FUEL_DATASET}[merk|handelsbenaming|jaar|type|variant]:"
    got = {
        k.removeprefix(pre + "TESLA|MODEL 3|2019|003|"): {
            f.value: s.value for f, s in r.specs.items()
        }
        for k, r in specs.items()
        if k.startswith(pre + "TESLA|MODEL 3|2019|")
    }
    assert set(got) == {"E1R", "E3D", "E3R"}
    assert (got["E1R"]["wltp_range_km"], got["E1R"]["price_new"]) == (409, 49930)
    assert (got["E3D"]["wltp_range_km"], got["E3D"]["price_new"]) == (560, 60980)
    assert specs[pre + "TESLA|MODEL 3|2019|003|E3D"].variant_name == "158 kW"


def test_small_price_group_is_dropped() -> None:
    keys = set(_specs())
    # Model 3 2017/2018: 1 and 3 cars sold new in NL, min = max, but too few to be a price.
    assert not any("TESLA|MODEL 3|2017#price" in k or "TESLA|MODEL 3|2018#price" in k for k in keys)


def test_spread_rule_on_synthetic_groups(tmp_path: Path) -> None:
    (tmp_path / "page-000.json").write_text("[]")
    sample = [
        # 10 cars, one value: IQR 0 -> kept.
        {"merk": "X", "handelsbenaming": "A", "jaar": "2024", "n": 10,
         "range_km": [[400, 10]], "wh_km": [[150, 10]], "price_eur": [[40000, 10]]},
        # Two equal halves 400 / 500 km: IQR 25 % of median -> dropped.
        {"merk": "X", "handelsbenaming": "B", "jaar": "2024", "n": 10,
         "range_km": [[400, 5], [500, 5]], "wh_km": [[150, 5], [152, 5]], "price_eur": []},
        # 4 cars: below MIN_SAMPLE -> dropped.
        {"merk": "X", "handelsbenaming": "C", "jaar": "2024", "n": 4,
         "range_km": [[300, 4]], "wh_km": [], "price_eur": []},
    ]  # fmt: skip
    prices = [
        {"merk": "X", "handelsbenaming": "A", "jaar": "2024", "n": "50", "med": "40000.5",
         "mn": "30000", "mx": "60000"},
        # Sample has no prices, but the full group's min/max are within 5 %: kept.
        {"merk": "X", "handelsbenaming": "B", "jaar": "2024", "n": "8", "med": "50000",
         "mn": "49500", "mx": "51000"},
    ]  # fmt: skip
    (tmp_path / adapter.SAMPLE_FILE).write_text(json.dumps(sample))
    (tmp_path / adapter.PRICE_FILE).write_text(json.dumps(prices))
    drops = adapter.Drops()
    got = {r.record_key.split(":", 1)[1]: r for r in adapter.spec_records(tmp_path, DAY, drops)}
    assert set(got) == {
        "X|A|2024#wltp_range_km",
        "X|A|2024#consumption_kwh_100km",
        "X|A|2024#price_new:NL",
        "X|B|2024#consumption_kwh_100km",  # 150 vs 152 Wh/km is narrow
        "X|B|2024#price_new:NL",
    }
    assert got["X|A|2024#price_new:NL"].specs[FactField.price_new].value == 40000
    assert got["X|A|2024#price_new:NL"].specs[FactField.registered_count].value == 50
    assert got["X|A|2024#consumption_kwh_100km"].specs[FactField.consumption_kwh_100km].value == 15
    assert drops.wide == {"wltp_range_km": 1}
    assert drops.small == {"wltp_range_km": 1}


def test_weighted_quantile_matches_linear_interpolation() -> None:
    hist = [(1.0, 1), (2.0, 1), (3.0, 1), (4.0, 1)]
    assert adapter.weighted_quantile(hist, 0.5) == 2.5
    assert adapter.weighted_quantile(hist, 0.25) == 1.75
    assert adapter.weighted_quantile([(7.0, 3)], 0.75) == 7.0


def test_sample_histograms_join_in_memory_and_drop_plates() -> None:
    main = [
        {"kenteken": "AB7C1D", "merk": "X", "handelsbenaming": "M", "jaar": "2024",
         "catalogusprijs": "40000", "nieuw_nl": True},
        {"kenteken": "AB7C2D", "merk": "X", "handelsbenaming": "M", "jaar": "2024",
         "catalogusprijs": "41000", "nieuw_nl": False},  # import: price not used
        {"kenteken": "AB7C3D", "merk": "X", "handelsbenaming": "M", "jaar": "2024"},
    ]  # fmt: skip
    fuel = [
        {"kenteken": "AB7C1D", "range_km": "400", "wh_km": "150.00"},
        {"kenteken": "AB7C2D", "range_km": "400"},
        {"kenteken": "ZZ7Z9Z", "range_km": "999"},  # not a sampled passenger BEV
    ]
    [g] = adapter.sample_histograms(main, fuel)
    assert g["n"] == 3
    assert g["range_km"] == [[400.0, 2]]
    assert g["wh_km"] == [[150.0, 1]]
    assert g["price_eur"] == [[40000.0, 1]]
    assert "kenteken" not in json.dumps(g)


def test_fetch_paginates_and_records_licence(tmp_path: Path) -> None:
    row = {"merk": "X", "handelsbenaming": "M", "jaar": "2024", "n": "1"}
    seen: list[tuple[str, str, str]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.startswith("/api/views/"):
            return httpx.Response(
                200,
                json={
                    "name": "Gekentekende_voertuigen",
                    "license": {"name": "Public Domain"},
                    "metadata": {"custom_fields": {"Licentie": {"Licentie": "CC0"}}},
                },
            )
        p = request.url.params
        offset = p["$offset"]
        kind = (
            "fuel"
            if adapter.FUEL_DATASET in request.url.path
            else "price-uitvoering"
            if "median" in p["$select"] and "uitvoering" in p["$group"]
            else "price-variant"
            if "median" in p["$select"] and "variant" in p["$group"]
            else "price"
            if "median" in p["$select"]
            else "sample"
            if "kenteken" in p["$select"]
            else "count"
        )
        seen.append((kind, offset, p.get("$where", "")))
        if kind == "count":
            return httpx.Response(200, json=[row, row] if offset == "0" else [])
        if kind.startswith("price"):
            return httpx.Response(200, json=[{**row, "med": "40000", "mn": "1", "mx": "2"}])
        if kind == "sample":
            car = {**row, "kenteken": "AB7C1D", "catalogusprijs": "40000", "nieuw_nl": True}
            return httpx.Response(200, json=[car])
        return httpx.Response(200, json=[{"kenteken": "AB7C1D", "range_km": "400"}])

    adapter.PAGE_SIZE, old = 2, adapter.PAGE_SIZE
    try:
        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            assert adapter.fetch(client, tmp_path, sleep_s=0) == 2
    finally:
        adapter.PAGE_SIZE = old
    assert [(k, o) for k, o, _ in seen] == [
        ("count", "0"), ("count", "2"), ("price", "0"), ("price-variant", "0"),
        ("price-uitvoering", "0"), ("sample", "0"), ("fuel", "0"),
    ]  # fmt: skip
    assert all(adapter.SAMPLE_WHERE in w for k, _, w in seen if k in ("sample", "fuel"))
    meta = json.loads((tmp_path / "_fetch.json").read_text())
    assert meta["licence_metadata"]["custom_fields.Licentie"] == "CC0"
    assert meta["fuel_dataset"]["licence_metadata"]["custom_fields.Licentie"] == "CC0"
    assert "cilinderinhoud IS NULL" in meta["query"]["$where"]
    assert meta["sample"]["joined_plates"] == 1
    assert meta["price_groups_variant"] == meta["price_groups_uitvoering"] == 1
    files = (
        adapter.SAMPLE_FILE,
        adapter.PRICE_FILE,
        "page-000.json",
        *adapter.PRICE_FILES.values(),
    )
    for name in files:
        assert "AB7C1D" not in (tmp_path / name).read_text()  # plates never stored
    [g] = json.loads((tmp_path / adapter.SAMPLE_FILE).read_text())
    assert g["range_km"] == [[400.0, 1]]


def test_normalise_cmd_from_fixtures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EV_DATA_DIR", str(tmp_path))
    assert adapter.normalise_cmd(from_fixtures=True) == 0
    lines = (tmp_path / "staging" / "rdw.records.jsonl").read_text().splitlines()
    kinds = [json.loads(line)["kind"] for line in lines]
    assert kinds.count("registration_count") == 118
    assert kinds.count("spec") == len(_specs())
    log = json.loads((tmp_path / "staging" / "runlog.jsonl").read_text().splitlines()[-1])
    assert log["count_records"] == 118
    assert log["dropped_wide_spread"]["price_new"] > 0
    assert log["wide_recovered_by_split"]["price_new"] > 0
    assert log["spec_fields_emitted_fine"]["price_new"] > 0
    assert set(log["spec_fields_emitted"]) <= {
        "wltp_range_km",
        "consumption_kwh_100km",
        "price_new",
    }


# --- probe_unchanged (ev refresh hook) ------------------------------------------------------

LICENCE_VIEW = {
    "license": {"name": "Public Domain"},
    "licenseId": "PUBLIC_DOMAIN",
    "metadata": {"custom_fields": {"Licentie": {"Licentie": "Creative Commons 0 (CC0)"}}},
}
LICENCE_META = {
    "license": {"name": "Public Domain"},
    "licenseId": "PUBLIC_DOMAIN",
    "custom_fields.Licentie": "Creative Commons 0 (CC0)",
}


def _prev_meta(main: object = 1794641309, fuel: object = 1794641147) -> dict[str, object]:
    """What fetch() records in _fetch.json (only the keys the probe reads)."""
    return {
        "query": adapter.QUERY,
        "price_query": adapter.PRICE_QUERY,
        "price_variant_query": adapter.PRICE_FINE_QUERIES["variant"],
        "price_uitvoering_query": adapter.PRICE_FINE_QUERIES["uitvoering"],
        "sample_main_query": adapter.SAMPLE_MAIN_QUERY,
        "sample_fuel_query": adapter.SAMPLE_FUEL_QUERY,
        "dataset_rows_updated_at": main,
        "licence_metadata": LICENCE_META,
        "fuel_dataset": {"dataset_rows_updated_at": fuel, "licence_metadata": LICENCE_META},
    }


def _views(updated: dict[str, object], licence: dict | None = None, status: int = 200):
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.startswith("/api/views/"), "the probe never queries rows"
        dataset = request.url.path.rsplit("/", 1)[-1].removesuffix(".json")
        calls.append(dataset)
        if status != 200:
            return httpx.Response(status, json={})
        return httpx.Response(
            200,
            json={"name": dataset, "rowsUpdatedAt": updated[dataset], **(licence or LICENCE_VIEW)},
        )

    return handler, calls


def _probe(meta: dict[str, object], **kw: object) -> tuple[bool | None, list[str]]:
    updated = kw.pop("updated", {adapter.DATASET: 1794641309, adapter.FUEL_DATASET: 1794641147})
    handler, calls = _views(updated, **kw)  # type: ignore[arg-type]
    with httpx.Client(transport=httpx.MockTransport(handler), base_url=adapter.BASE_URL) as c:
        return adapter.probe_unchanged(c, meta), calls


def test_probe_unchanged_when_both_datasets_kept_their_rows_updated_at() -> None:
    verdict, calls = _probe(_prev_meta())
    assert verdict is True
    assert calls == [adapter.DATASET, adapter.FUEL_DATASET]  # two metadata calls, no rows


def test_probe_changed_when_either_dataset_moved() -> None:
    moved_main = {adapter.DATASET: 1794700000, adapter.FUEL_DATASET: 1794641147}
    assert _probe(_prev_meta(), updated=moved_main)[0] is False
    moved_fuel = {adapter.DATASET: 1794641309, adapter.FUEL_DATASET: 1794700000}
    assert _probe(_prev_meta(), updated=moved_fuel)[0] is False


def test_probe_changed_when_licence_metadata_moved() -> None:
    other = {**LICENCE_VIEW, "licenseId": "CC_BY_4"}
    assert _probe(_prev_meta(), licence=other)[0] is False


def test_probe_changed_when_our_queries_changed_without_calling_rdw() -> None:
    meta = {**_prev_meta(), "price_query": {"$select": "an older query"}}
    verdict, calls = _probe(meta)
    assert verdict is False and calls == []
    # A raw folder fetched before T-054 lacks the per-code price queries: refetch once.
    old = {k: v for k, v in _prev_meta().items() if k != "price_uitvoering_query"}
    assert _probe(old)[0] is False


def test_probe_unknown_without_recorded_timestamps_or_on_errors() -> None:
    assert _probe({**_prev_meta(), "dataset_rows_updated_at": None})[0] is None
    assert _probe({**_prev_meta(), "fuel_dataset": {}})[0] is None
    assert _probe(_prev_meta(), status=503)[0] is None
    gone = {adapter.DATASET: None, adapter.FUEL_DATASET: 1794641147}
    assert _probe(_prev_meta(), updated=gone)[0] is None


def test_probe_matches_what_fetch_records(tmp_path: Path) -> None:
    """Round trip: the meta written by fetch() is what the probe compares against."""
    stamps = {adapter.DATASET: 111, adapter.FUEL_DATASET: 222}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.startswith("/api/views/"):
            ds = request.url.path.rsplit("/", 1)[-1].removesuffix(".json")
            return httpx.Response(200, json={"rowsUpdatedAt": stamps[ds], **LICENCE_VIEW})
        return httpx.Response(200, json=[])

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        adapter.fetch(client, tmp_path, sleep_s=0)
        meta = json.loads((tmp_path / "_fetch.json").read_text())
        assert adapter.probe_unchanged(client, meta) is True
        stamps[adapter.FUEL_DATASET] = 333
        assert adapter.probe_unchanged(client, meta) is False


# --- T-054: finer split by type-approval codes -------------------------------------------


def _e(model: str, t: str, v: str, u: str, n: int, **cols: list) -> dict[str, object]:
    base = {"merk": "X", "handelsbenaming": model, "jaar": "2024", "type": t, "variant": v,
            "uitvoering": u, "n": n}  # fmt: skip
    return {**base, **{c: cols.get(c, []) for c in adapter.HIST_COLS}}


def _p(model: str, n: int, med: float, mn: float, mx: float, **codes: str) -> dict[str, str]:
    return {"merk": "X", "handelsbenaming": model, "jaar": "2024", **codes,
            "n": str(n), "med": str(med), "mn": str(mn), "mx": str(mx)}  # fmt: skip


def _split_dir(tmp_path: Path) -> Path:
    (tmp_path / "page-000.json").write_text("[]")
    sample = [
        # Model A: two type-approval variants, Standard (400 km, 150 kW) and Long (500 km,
        # 210 kW): coarse is wide, each variant is narrow -> two fine records, no coarse one.
        _e("A", "T1", "STD", "U1", 10, range_km=[[400, 10]], wh_km=[[150, 10]],
           price_eur=[[40000, 10]], kw=[[150, 10]]),
        _e("A", "T1", "LR", "U1", 6, range_km=[[500, 6]], wh_km=[[152, 6]],
           price_eur=[[50000, 6]], kw=[[210, 6]]),
        _e("A", "T1", "LR", "U2", 4, range_km=[[500, 4]], wh_km=[[152, 4]],
           price_eur=[[50500, 4]], kw=[[210, 4]]),
        # Model B: one variant code whose uitvoeringen differ (wide at variant level), one
        # uitvoering narrow (kept), one too small (dropped).
        _e("B", "T2", "V", "U1", 8, range_km=[[300, 8]], kw=[[100, 8]]),
        _e("B", "T2", "V", "U2", 3, range_km=[[380, 3]], kw=[[100, 3]]),
        _e("B", "T2", "W", "U9", 2, range_km=[[380, 2]]),
        # Model C: narrow coarse group, has codes: never split (coarse record only).
        _e("C", "T3", "V1", "U1", 6, range_km=[[250, 6]]),
        _e("C", "T3", "V2", "U1", 6, range_km=[[251, 6]]),
    ]  # fmt: skip
    prices = [_p("A", 40, 40000, 39000, 51000)]
    pv = [_p("A", 24, 40000, 39500, 40500, type="T1", variant="STD"),
          _p("A", 16, 50000, 49800, 50600, type="T1", variant="LR")]  # fmt: skip
    pu = [_p("A", 24, 40000, 39500, 40500, type="T1", variant="STD", uitvoering="U1"),
          _p("A", 10, 50000, 49800, 50000, type="T1", variant="LR", uitvoering="U1"),
          _p("A", 6, 50500, 50500, 50600, type="T1", variant="LR", uitvoering="U2")]  # fmt: skip
    (tmp_path / adapter.SAMPLE_FILE).write_text(json.dumps(sample))
    (tmp_path / adapter.PRICE_FILE).write_text(json.dumps(prices))
    (tmp_path / adapter.PRICE_FILES["variant"]).write_text(json.dumps(pv))
    (tmp_path / adapter.PRICE_FILES["uitvoering"]).write_text(json.dumps(pu))
    return tmp_path


def test_wide_coarse_group_is_split_by_type_and_variant(tmp_path: Path) -> None:
    drops = adapter.Drops()
    got = {r.record_key: r for r in adapter.spec_records(_split_dir(tmp_path), DAY, drops)}
    a = [k for k in got if ":X|A|" in k]
    vgrp = "m9d7-ebf2+8ys7-d773[merk|handelsbenaming|jaar|type|variant]"
    assert sorted(a) == [
        # 150 vs 152 Wh/km is narrow: consumption stays on the coarse record (per field).
        "8ys7-d773+m9d7-ebf2[merk|handelsbenaming|jaar]:X|A|2024#consumption_kwh_100km",
        f"{vgrp}:X|A|2024|T1|LR",
        f"{vgrp}:X|A|2024|T1|STD",
    ]
    std = got[f"{vgrp}:X|A|2024|T1|STD"]
    # Every field that passed sits on one record, so the price brings its WLTP evidence.
    assert {f.value: s.value for f, s in std.specs.items()} == {
        "wltp_range_km": 400, "price_new": 40000, "registered_count": 24,
    }  # fmt: skip
    assert std.country == Country.NL and std.source.url.endswith(adapter.DATASET)
    assert std.variant_name == "150 kW"  # power: matcher evidence only, never a fact
    assert FactField.power_kw not in std.specs
    lr = got[f"{vgrp}:X|A|2024|T1|LR"]
    assert lr.specs[FactField.price_new].value == 50000  # variant passed: not split further
    assert drops.wide["wltp_range_km"] == 2 and drops.recovered["wltp_range_km"] == 2
    assert drops.recovered["price_new"] == 1
    assert drops.fine_kept["variant:price_new"] == 2


def test_still_wide_variant_is_split_by_uitvoering(tmp_path: Path) -> None:
    drops = adapter.Drops()
    got = {r.record_key: r for r in adapter.spec_records(_split_dir(tmp_path), DAY, drops)}
    b = sorted(k for k in got if ":X|B|" in k)
    assert b == ["m9d7-ebf2+8ys7-d773[merk|handelsbenaming|jaar|type|variant|uitvoering]"
                 ":X|B|2024|T2|V|U1"]  # fmt: skip
    rec = got[b[0]]
    assert rec.specs[FactField.wltp_range_km].value == 300
    assert rec.specs[FactField.registered_count].value == 8  # sampled cars, no price here
    assert rec.country is None and rec.source.url.endswith(adapter.FUEL_DATASET)
    assert drops.fine_small["uitvoering:wltp_range_km"] == 1  # U2: 3 cars
    assert drops.fine_small["variant:wltp_range_km"] == 1  # W: 2 cars


def test_split_never_counts_a_car_twice(tmp_path: Path) -> None:
    records = adapter.spec_records(_split_dir(tmp_path), DAY)
    # Narrow coarse group C keeps its coarse record and gets no fine record.
    c_keys = sorted(r.record_key for r in records if "|C|" in r.record_key)
    assert c_keys == ["8ys7-d773+m9d7-ebf2[merk|handelsbenaming|jaar]:X|C|2024#wltp_range_km"]
    # Per field, the groups behind emitted records are disjoint (no prefix of another).
    for fname in (FactField.wltp_range_km, FactField.price_new):
        groups = [r.record_key.split("]:", 1)[1].split("#")[0].split("|")
                  for r in records if fname in r.specs]  # fmt: skip
        for g in groups:
            assert not any(h != g and h[: len(g)] == g for h in groups), (fname, g)
    # Wide coarse fields are replaced by the split, narrow ones stay coarse.
    assert {r.record_key.rsplit("#", 1)[1] for r in records if ":X|A|2024#" in r.record_key} == {
        "consumption_kwh_100km"
    }


def test_old_sample_without_codes_gives_the_coarse_result(tmp_path: Path) -> None:
    """Raw folders from before T-054 (no codes in the sample) normalise as before."""
    (tmp_path / "page-000.json").write_text("[]")
    sample = [{"merk": "X", "handelsbenaming": "B", "jaar": "2024", "n": 10,
               "range_km": [[400, 5], [500, 5]], "wh_km": [], "price_eur": []}]  # fmt: skip
    (tmp_path / adapter.SAMPLE_FILE).write_text(json.dumps(sample))
    drops = adapter.Drops()
    assert adapter.spec_records(tmp_path, DAY, drops) == []
    assert drops.wide == {"wltp_range_km": 1} and not drops.fine_wide and not drops.recovered


def test_sample_histograms_keep_codes_and_power() -> None:
    main = [
        {"kenteken": "AB7C1D", "merk": "X", "handelsbenaming": "M", "jaar": "2024",
         "type": "T", "variant": "V", "uitvoering": "U1"},
        {"kenteken": "AB7C2D", "merk": "X", "handelsbenaming": "M", "jaar": "2024",
         "type": "T", "variant": "V"},  # no uitvoering -> ""
    ]  # fmt: skip
    fuel = [{"kenteken": "AB7C1D", "range_km": "400", "kw": "150.00"},
            {"kenteken": "AB7C2D", "range_km": "410"}]  # fmt: skip
    g1, g2 = adapter.sample_histograms(main, fuel)
    assert (g1["uitvoering"], g2["uitvoering"]) == ("", "U1")
    assert g2["kw"] == [[150.0, 1]] and g2["range_km"] == [[400.0, 1]]
    assert "kenteken" not in json.dumps([g1, g2])


def test_fine_records_attach_by_power_and_wltp_evidence(tmp_path: Path) -> None:
    """The attach-only matcher places fine records on seed variants by kW / WLTP evidence,
    with no code -> variant table; a record without evidence goes to review."""
    from ev_pipeline.match.matcher import match_records
    from ev_pipeline.match.seed import parse_manual_variants, parse_seed

    seed = parse_seed({"makes": [{"id": "x", "name": "X", "models": [
        {"id": "x-a", "name": "A", "generations": [{"id": "x-a-g1", "years": [2020, None]}]},
    ]}]})  # fmt: skip
    base = {"generation_id": "x-a-g1", "years": [2020, None]}
    manual = parse_manual_variants({"variants": [
        {**base, "id": "x-a-g1-standard", "name": "Standard",
         "specs": {"power_kw": 150, "wltp_range_km": 402}},
        {**base, "id": "x-a-g1-long-range", "name": "Long Range",
         "specs": {"power_kw": 210, "wltp_range_km": 498}},
    ]}, DAY)[0]  # fmt: skip
    records = adapter.spec_records(_split_dir(tmp_path), DAY)
    res = match_records([r for r in records if r.model == "A"], seed, manual)
    placed = {
        mf.fact.source_record.rsplit("|", 1)[-1]: mf.fact.subject_id.root
        for mf in res.spec_facts
        if mf.source_id == "rdw" and mf.fact.field.value == "price_new"
    }
    assert placed == {"STD": "x-a-g1-standard", "LR": "x-a-g1-long-range"}
