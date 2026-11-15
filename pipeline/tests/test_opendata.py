"""Decision 016 open data bundle: fields, units, licence gate, ODbL exclusion, attribution."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any

import pytest

from ev_pipeline.opendata import bundle as ob
from ev_pipeline.release.gate import load_registry

QA = Path(__file__).parent / "fixtures" / "qa"
REGISTRY = load_registry(QA / "sources.yaml")
A50, A60, B40 = "testcar-alpha-gen1-50", "testcar-alpha-gen1-60", "testcar-beta-gen1-40"


@pytest.fixture
def cat() -> dict[str, Any]:
    return json.loads((QA / "catalogue.json").read_text())


def _row(cat: dict[str, Any], vid: str) -> dict[str, Any]:
    return next(r for r in cat["rows"] if r["variant_id"] == vid)


def _out(b: ob.Bundle, vid: str) -> dict[str, Any]:
    return next(r for r in b.rows if r["variant_id"] == vid)


def _poison_with_odbl(cat: dict[str, Any]) -> None:
    """An ODbL source behind a value, a price and a registration count."""
    cat["sources"].append({"id": "testosm", "name": "ODbL map data", "licence": "ODbL-1.0"})
    r = _row(cat, A50)
    r["provenance"]["wltp_range_km"]["source_ids"] = ["testsrc", "testosm"]
    r["provenance"]["price_new.NL"]["source_ids"] = ["testosm"]
    r["registrations"]["NL"].append(
        {
            "count": 4242,
            "kind": "fleet",
            "period": "2026-12-01",
            "level": "generation",
            "source_id": "testosm",
        }
    )
    r["wltp_range_km"] = 777.0


def test_one_flat_row_per_variant_with_documented_units(cat) -> None:
    b = ob.build_bundle(cat, REGISTRY)
    assert [r["variant_id"] for r in b.rows] == [A50, A60, B40]
    docs = {d["name"]: d for d in ob.field_docs(b)}
    assert set(docs) == set(b.columns)
    assert all(d["description"] for d in docs.values())
    assert docs["battery_kwh_net"]["unit"] == "kWh"
    assert docs["wltp_range_km"]["unit"] == "km"
    assert docs["reg_nl_fleet"]["unit"] == "vehicles"


def test_sources_and_confidence_columns_and_seed_manual_flag(cat) -> None:
    r = _out(ob.build_bundle(cat, REGISTRY), A50)
    assert r["battery_kwh_net"] == 50.0
    assert r["battery_kwh_net_sources"] == "testsrc"
    assert r["battery_kwh_net_confidence"] == "medium"
    assert r["real_range_km_confidence"] == "estimate"
    assert r["boot_l"] == 350 and r["boot_l_sources"] == "seed-manual"
    assert "boot_l" in r["seed_manual_fields"].split(";")
    assert "real_range_km" in r["estimate_fields"].split(";")
    assert r["real_range_rung"] == "body-ratio"  # companion follows real_range_km
    assert r["price_new_nl"] == 35000 and r["price_new_nl_currency"] == "EUR"


def test_odbl_values_never_reach_the_bundle(cat, tmp_path: Path) -> None:
    _poison_with_odbl(cat)
    b = ob.build_bundle(cat, REGISTRY)
    r = _out(b, A50)
    assert r["wltp_range_km"] is None and r["wltp_range_km_sources"] is None
    assert r["price_new_nl"] is None and r["price_new_nl_currency"] is None
    assert r["reg_nl_fleet"] == 5000  # the ODbL count (newer) is dropped, RDW-like one stays
    assert "testosm" not in r["registrations_json"]
    assert "testosm" not in b.sources_used
    assert b.withheld["testosm"] == 3
    ob.write_open_bundle(cat, REGISTRY, tmp_path)
    for p in (tmp_path / "open").iterdir():
        text = p.read_text()
        assert "777" not in text and "4242" not in text, p.name
        if p.name != "README.md":  # README names what the gate withheld, never the values
            assert "testosm" not in text, p.name
    assert (
        "withheld by the licence gate: testosm 3" in (tmp_path / "open" / "README.md").read_text()
    )


def test_non_releasable_source_is_withheld_with_companion(cat) -> None:
    _row(cat, B40)["provenance"]["real_range_km"]["source_ids"] = ["testpending"]
    r = _out(ob.build_bundle(cat, REGISTRY), B40)
    assert r["real_range_km"] is None and r["real_range_rung"] is None


def test_value_without_provenance_is_not_published(cat) -> None:
    del _row(cat, B40)["provenance"]["boot_l"]
    assert _out(ob.build_bundle(cat, REGISTRY), B40)["boot_l"] is None


def test_registrations_newest_period_then_source_order(cat) -> None:
    r = _row(cat, A50)
    r["registrations"]["DE"] = [
        {
            "count": 10,
            "kind": "new_registrations",
            "period": "2025",
            "level": "generation",
            "source_id": "testsrc",
        },
        {
            "count": 11,
            "kind": "new_registrations",
            "period": "2025-01..12",
            "level": "generation",
            "source_id": "testreg",
        },
        {
            "count": 5,
            "kind": "new_registrations",
            "period": "2026-01..10",
            "level": "model",
            "source_id": "testsrc",
        },
    ]
    r["provenance"]["registrations.DE"] = {
        "source_ids": ["testsrc", "testreg"],
        "confidence": "high",
    }
    b = ob.build_bundle(cat, REGISTRY, ("testreg", "testsrc"))
    o = _out(b, A50)
    assert (o["reg_de_new_registrations"], o["reg_de_new_registrations_period"]) == (
        5,
        "2026-01..10",
    )
    assert o["reg_de_new_registrations_level"] == "model"
    assert len(json.loads(o["registrations_json"])) == 4  # NL + 3 DE, never summed
    # Same period end: the registration source order decides.
    r["registrations"]["DE"].pop()
    o = _out(ob.build_bundle(cat, REGISTRY, ("testreg", "testsrc")), A50)
    assert o["reg_de_new_registrations"] == 11
    assert (
        _out(ob.build_bundle(cat, REGISTRY, ("testsrc", "testreg")), A50)[
            "reg_de_new_registrations"
        ]
        == 10
    )


@pytest.mark.parametrize(
    ("period", "key"),
    [
        ("2026-11-14", (2026, 11, 14)),
        ("2026-Q2", (2026, 6, 31)),
        ("2025", (2025, 12, 31)),
        ("2026-01..10", (2026, 10, 31)),
        ("2026-03", (2026, 3, 31)),
        ("??", (0, 0, 0)),
    ],
)
def test_period_key(period: str, key: tuple[int, int, int]) -> None:
    assert ob._period_key(period) == key


def test_written_files(cat, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(ob.BRAND_ENV, "Brand From Config")
    summary = ob.write_open_bundle(cat, REGISTRY, tmp_path)
    d = tmp_path / "open"
    assert set(summary["files"]) == {
        "variants.csv",
        "variants.json",
        "ATTRIBUTION.md",
        "LICENSE",
        "README.md",
    }
    rows = list(csv.DictReader(io.StringIO((d / "variants.csv").read_text())))
    doc = json.loads((d / "variants.json").read_text())
    assert len(rows) == len(doc["rows"]) == 3
    assert list(rows[0]) == [f["name"] for f in doc["fields"]]
    assert rows[0]["generation_uncertain"] == "false" and rows[0]["year_end"] == ""
    assert doc["release"] == 1 and doc["licence"] == "CC-BY-4.0"
    lic = (d / "LICENSE").read_text()
    assert ob.CC_BY_LEGAL in lic and "Brand From Config" in lic
    readme = (d / "README.md").read_text()
    assert "release 1" in readme and "2026-11-15" in readme
    assert "Source: Brand From Config (data release 1, 2026-11-15), CC BY 4.0" in readme
    assert "| `battery_kwh_net` | kWh |" in readme
    att = (d / "ATTRIBUTION.md").read_text()
    assert "Test source credit" in att and "CC0-1.0" in att
    assert "Brand From Config" in att


def test_brand_comes_from_config_brand_yaml(monkeypatch) -> None:
    # Decision 018: the working title lives in config/brand.yaml, not in code.
    monkeypatch.delenv(ob.BRAND_ENV, raising=False)
    assert ob.brand_name() == "EV Shortlist"


def test_attribution_carries_required_notices_and_rdw_interim_wording(cat) -> None:
    for sid, lic in (("kilowatt-openev", "MIT-with-attribution"), ("rdw", "CC0-1.0")):
        credit = "Bron: RDW" if sid == "rdw" else "Open EV Data (KilowattApp)"
        cat["sources"].append({"id": sid, "name": sid, "licence": lic, "attribution": credit})
    b = ob.build_bundle(cat, REGISTRY)
    b.sources_used = sorted({*b.sources_used, "kilowatt-openev", "rdw"})
    att = ob.attribution_md(cat, REGISTRY, b)
    assert "Copyright (c) 2024 Tijs Teulings" in att
    assert "Q-037" in att and "Bron: RDW" not in att
