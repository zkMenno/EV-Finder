"""RDW APK defects adapter: recorded per-group aggregates + synthetic plates. No network."""

import json
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs

import httpx
import pytest

from ev_pipeline.sources.rdw_defects import adapter

FIXTURE = Path(__file__).parent / "fixtures" / "rdw_defects"


def test_fixture_is_small_and_has_no_plates() -> None:
    for name in ("groups.json", "codes.json"):
        text = (FIXTURE / name).read_text()
        assert len(json.loads(text)) <= 200
        assert '"kenteken"' not in text


def test_aggregate_joins_in_memory_without_plates() -> None:
    sample = [
        {"kenteken": "ZZ7AA1", "merk": "TESTCAR", "handelsbenaming": "ALPHA", "jaar": "2019"},
        {"kenteken": "ZZ7AA2", "merk": "TESTCAR", "handelsbenaming": "ALPHA", "jaar": "2019"},
        {"kenteken": "ZZ7AA3", "merk": "TESTCAR", "handelsbenaming": "BETA", "jaar": "2020"},
        {"kenteken": "ZZ7AA4", "merk": None, "handelsbenaming": "X", "jaar": "2020"},
    ]
    defects = [
        {
            "kenteken": "ZZ7AA1",
            "gebrek_identificatie": "205",
            "n": "2",
            "mn": "20240101",
            "mx": "20250101",
        },
        {
            "kenteken": "ZZ7AA1",
            "gebrek_identificatie": "516",
            "n": "1",
            "mn": "20240101",
            "mx": "20240101",
        },
        {
            "kenteken": "ZZ7AA2",
            "gebrek_identificatie": "205",
            "n": "1",
            "mn": "20230601",
            "mx": "20230601",
        },
        {"kenteken": "NOTSAMPLED", "gebrek_identificatie": "205", "n": "9"},
    ]
    groups, window = adapter.aggregate(sample, defects)
    assert window == {"from": "2023-06-01", "to": "2025-01-01"}
    alpha = next(g for g in groups if g["handelsbenaming"] == "ALPHA")
    assert alpha["sample_cars"] == 2
    assert alpha["cars_with_any_defect"] == 2
    assert alpha["codes"][0] == ["205", 2, 3]  # 2 cars, 3 defects
    beta = next(g for g in groups if g["handelsbenaming"] == "BETA")
    assert beta == {**beta, "sample_cars": 1, "cars_with_any_defect": 0, "codes": []}
    assert "ZZ7" not in json.dumps(groups)


def test_defects_query_refuses_malformed_plates() -> None:
    assert "kenteken in ('AB12CD')" in adapter.defects_query(["AB12CD"])["$where"]
    with pytest.raises(ValueError):
        adapter.defects_query(["AB' OR 1=1 --"])


def test_normalise_rows_and_drop_rules() -> None:
    drops: Counter[str] = Counter()
    rows = adapter.normalise(FIXTURE, date(2026, 11, 15), drops)
    assert rows
    assert drops["group_small_sample"] == 4  # Leaf 2018 (1), Abarth (8), two Aiways groups
    assert drops["code_few_cars"] > 0
    for r in rows:
        assert r["source"]["licence"] == "CC0-1.0"
        assert r["source"]["id"] == "rdw-defects"  # not the registrations source `rdw`
        assert r["country"] == "NL"
        assert r["confidence"] == "medium"
        assert r["retrieved_at"] == "2026-11-15"
        assert r["kind"] in ("defect_group", "defect_count")
        assert r["sample_cars"] >= adapter.MIN_SAMPLE_CARS
        if r["kind"] == "defect_count":
            assert r["cars_with_defect"] >= adapter.MIN_CARS_PER_CODE
            assert 0 < r["share_of_sample"] <= 1
    m3 = [r for r in rows if r["model"] == "MODEL 3" and r["year"] == 2019]
    group = next(r for r in m3 if r["kind"] == "defect_group")
    assert group["sample_cars"] == 2554
    assert group["reported_from"] == "2022-06-02"
    headlight = next(r for r in m3 if r.get("defect_code") == "516")
    assert headlight["defect_description"] == "Dimlicht onjuist afgesteld"
    assert headlight["cars_with_defect"] == 434
    assert headlight["share_of_sample"] == round(434 / 2554, 4)
    assert headlight["record_key"].endswith("TESLA|MODEL 3|2019#defect:516")


def test_fetch_with_mock_transport(tmp_path: Path) -> None:
    view = {
        "name": "x",
        "licenseId": "PUBLIC_DOMAIN",
        "license": {"name": "Public Domain"},
        "metadata": {"custom_fields": {"Licentie": {"Licentie": "Creative Commons 0 (CC0)"}}},
    }
    seen_in_lists: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.startswith("/api/views/"):
            return httpx.Response(200, json=view)
        q = {k: v[0] for k, v in parse_qs(request.url.query.decode()).items()}
        if path.endswith(f"{adapter.CODES}.json"):
            return httpx.Response(
                200,
                json=[
                    {
                        "gebrek_identificatie": "205",
                        "gebrek_omschrijving": "Band onvoldoende profiel",
                    }
                ],
            )
        if path.endswith(f"{adapter.MAIN}.json"):
            assert "datum_eerste_toelating < 20240101" in q["$where"]
            return httpx.Response(
                200,
                json=[
                    {
                        "kenteken": f"ZZ7A{i:02d}",
                        "merk": "TESTCAR",
                        "handelsbenaming": "ALPHA",
                        "jaar": "2019",
                    }
                    for i in range(25)
                ],
            )
        assert path.endswith(f"{adapter.DEFECTS}.json")
        seen_in_lists.append(q["$where"])
        return httpx.Response(
            200,
            json=[
                {
                    "kenteken": "ZZ7A01",
                    "gebrek_identificatie": "205",
                    "n": "1",
                    "mn": "20250102",
                    "mx": "20250102",
                }
            ],
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        n = adapter.fetch(client, tmp_path, sleep_s=0, today=date(2026, 11, 15))
    assert n == 1
    assert len(seen_in_lists) == 1  # 25 plates fit one batch
    for f in tmp_path.iterdir():
        assert "ZZ7A" not in f.read_text(), f"plate leaked into {f.name}"
    meta = json.loads((tmp_path / "_fetch.json").read_text())
    assert meta["licence"] == "CC0-1.0" and meta["sampled_cars"] == 25


def test_fetch_refuses_changed_licence(tmp_path: Path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"licenseId": "SOMETHING_ELSE", "metadata": {}})

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(adapter.LicenceChanged),
    ):
        adapter.fetch(client, tmp_path, sleep_s=0)


def test_normalise_cmd_from_fixtures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EV_DATA_DIR", str(tmp_path))
    assert adapter.normalise_cmd(from_fixtures=True) == 0
    lines = (tmp_path / "staging" / "rdw-defects.defects.jsonl").read_text().splitlines()
    assert len(lines) == len(adapter.normalise(FIXTURE, date(2026, 11, 15)))
