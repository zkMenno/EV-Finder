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


def test_fixture_is_a_small_sample() -> None:
    for name in ("page-000.json", adapter.PRICE_FILE, adapter.SAMPLE_FILE):
        assert len(json.loads((FIXTURE / name).read_text())) <= 200, name


def test_fixture_holds_no_plates() -> None:
    for name in ("page-000.json", adapter.PRICE_FILE, adapter.SAMPLE_FILE):
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
    for key, rec in specs.items():
        assert "[merk|handelsbenaming|jaar]:" in key  # the grouping is in the key
        assert rec.confidence == Confidence.medium
        assert rec.source.licence == "CC0-1.0" and rec.source.attribution
        fields = set(rec.specs) - {FactField.registered_count}
        assert len(fields) == 1  # one field per record, with its own count
        assert rec.specs[FactField.registered_count].value >= adapter.MIN_SAMPLE
        if FactField.price_new in fields:
            assert rec.country == Country.NL and rec.specs[FactField.price_new].unit == "EUR"
            assert rec.source.url.endswith(adapter.DATASET)
        else:
            assert rec.source.url.endswith(adapter.FUEL_DATASET)


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
    [g] = [e for e in sample if (e["handelsbenaming"], e["jaar"]) == ("MODEL 3", "2019")]
    for col in ("range_km", "price_eur"):
        s = adapter.spread_of([(v, n) for v, n in g[col]])
        assert s is not None and s.n >= adapter.MIN_SAMPLE and s.iqr_ratio > adapter.MAX_IQR_RATIO
    assert drops.wide["wltp_range_km"] > 0 and drops.wide["price_new"] > 0


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
            else "price"
            if "median" in p["$select"]
            else "sample"
            if "kenteken" in p["$select"]
            else "count"
        )
        seen.append((kind, offset, p.get("$where", "")))
        if kind == "count":
            return httpx.Response(200, json=[row, row] if offset == "0" else [])
        if kind == "price":
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
        ("count", "0"), ("count", "2"), ("price", "0"), ("sample", "0"), ("fuel", "0"),
    ]  # fmt: skip
    assert all(adapter.SAMPLE_WHERE in w for k, _, w in seen if k in ("sample", "fuel"))
    meta = json.loads((tmp_path / "_fetch.json").read_text())
    assert meta["licence_metadata"]["custom_fields.Licentie"] == "CC0"
    assert meta["fuel_dataset"]["licence_metadata"]["custom_fields.Licentie"] == "CC0"
    assert "cilinderinhoud IS NULL" in meta["query"]["$where"]
    assert meta["sample"]["joined_plates"] == 1
    for name in (adapter.SAMPLE_FILE, adapter.PRICE_FILE, "page-000.json"):
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
    assert set(log["spec_fields_emitted"]) <= {
        "wltp_range_km",
        "consumption_kwh_100km",
        "price_new",
    }
