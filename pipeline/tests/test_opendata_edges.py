"""Open data bundle edge cases (overnight coverage pass): column flattening per country and
registration kind, empty catalogues, CSV cell formatting, field docs fallbacks and the brand
fallback.

Uses the SYNTHETIC QA fixture in fixtures/qa/ (invented `testcar` make, invented sources).
No network.
"""

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


def _reg(count: int, kind: str, period: str, source: str = "testreg") -> dict[str, Any]:
    return {
        "count": count,
        "kind": kind,
        "period": period,
        "level": "generation",
        "source_id": source,
    }


def test_column_layout_value_triples_and_companions(cat) -> None:
    b = ob.build_bundle(cat, REGISTRY)
    cols = b.columns
    assert cols[: len(ob.IDENTITY_FIELDS)] == [f for f, _, _ in ob.IDENTITY_FIELDS]
    i = cols.index("battery_kwh_net")
    assert cols[i : i + 3] == [
        "battery_kwh_net",
        "battery_kwh_net_sources",
        "battery_kwh_net_confidence",
    ]
    for comp in ob.COMPANION_OF:  # companions are a single column
        assert comp in cols and f"{comp}_sources" not in cols
    assert cols[-3:] == ["registrations_json", "seed_manual_fields", "estimate_fields"]
    assert len(cols) == len(set(cols))
    assert all(set(r) == set(cols) for r in b.rows)


def test_price_columns_per_country_sorted_and_empty_where_missing(cat) -> None:
    r = _row(cat, A60)
    r["price_new"] = {"DE": {"amount": 41000, "currency": "EUR"}}
    r["provenance"]["price_new.DE"] = {"source_ids": ["testsrc"], "confidence": "medium"}
    r["provenance"].pop("price_new.NL", None)
    b = ob.build_bundle(cat, REGISTRY)
    price_cols = [c for c in b.columns if c.startswith("price_new_") and c.count("_") == 2]
    assert price_cols == ["price_new_de", "price_new_nl"]  # sorted by country
    o = _out(b, A60)
    assert (o["price_new_de"], o["price_new_de_currency"]) == (41000, "EUR")
    assert o["price_new_nl"] is None and o["price_new_nl_currency"] is None
    a = _out(b, A50)
    assert a["price_new_de"] is None and a["price_new_nl"] == 35000


def test_registration_columns_per_country_and_kind(cat) -> None:
    r = _row(cat, A50)
    r["registrations"]["DE"] = [
        _reg(300, "fleet", "2026-Q2"),
        _reg(40, "new_registrations", "2025"),
        _reg(55, "new_registrations", "2026-03"),
    ]
    b = ob.build_bundle(cat, REGISTRY)
    for cc in ("de", "nl"):
        for kind in ob.REGISTRATION_KINDS:
            base = f"reg_{cc}_{kind}"
            assert [base, f"{base}_period", f"{base}_level", f"{base}_source"] == b.columns[
                b.columns.index(base) : b.columns.index(base) + 4
            ]
    o = _out(b, A50)
    assert (o["reg_de_fleet"], o["reg_de_fleet_period"]) == (300, "2026-Q2")
    assert (o["reg_de_new_registrations"], o["reg_de_new_registrations_source"]) == (55, "testreg")
    assert o["reg_nl_new_registrations"] is None  # no NL new-registration count at all
    assert {e["country"] for e in json.loads(o["registrations_json"])} == {"NL", "DE"}


def test_blocked_registration_source_is_dropped_from_columns_and_json(cat) -> None:
    r = _row(cat, A50)
    r["registrations"]["NL"].append(_reg(9999, "fleet", "2027-01-01", source="testpending"))
    b = ob.build_bundle(cat, REGISTRY)
    o = _out(b, A50)
    assert o["reg_nl_fleet"] == 5000  # the newer count is from a non-releasable source
    assert "testpending" not in o["registrations_json"]
    assert b.withheld["testpending"] == 1


def test_source_without_licence_in_catalogue_is_withheld(cat) -> None:
    for s in cat["sources"]:
        if s["id"] == "testsrc":
            s["licence"] = ""
    b = ob.build_bundle(cat, REGISTRY)
    assert _out(b, A50)["battery_kwh_net"] is None
    assert "testsrc" not in b.sources_used and b.withheld["testsrc"] > 0


def test_empty_catalogue_gives_header_only(tmp_path: Path) -> None:
    empty = {"release": 9, "generated_at": "2026-11-15T01:00:00Z", "sources": [], "rows": []}
    b = ob.build_bundle(empty, REGISTRY)
    assert b.rows == [] and b.sources_used == [] and b.withheld == {}
    assert not any(c.startswith(("price_new_", "reg_")) for c in b.columns)
    assert ob.variants_csv(b).splitlines() == [",".join(b.columns)]


@pytest.mark.parametrize(
    ("value", "cell"),
    [(None, ""), (True, "true"), (False, "false"), (0, "0"), (12.5, "12.5"), ("a,b", "a,b")],
)
def test_csv_cell(value: object, cell: str) -> None:
    assert ob._csv_cell(value) == cell


def test_csv_quotes_cells_with_separators(cat) -> None:
    _row(cat, A50)["variant_name"] = 'Alpha, "long" 50'
    b = ob.build_bundle(cat, REGISTRY)
    rows = list(csv.DictReader(io.StringIO(ob.variants_csv(b))))
    assert rows[0]["variant_name"] == 'Alpha, "long" 50'


def test_field_docs_fallbacks() -> None:
    b = ob.Bundle(
        columns=[
            "battery_kwh_net",
            "price_new_nl",
            "price_new_nl_currency",
            "price_new_nl_sources",
            "reg_de_fleet",
            "reg_de_new_registrations",
            "reg_de_fleet_period",
            "reg_de_fleet_level",
            "reg_de_fleet_source",
            "mystery_column",
        ],
        rows=[],
        sources_used=[],
    )
    docs = {d["name"]: d for d in ob.field_docs(b)}
    assert docs["price_new_nl"]["unit"] == "currency"
    assert docs["price_new_nl_currency"]["description"].startswith("ISO 4217")
    assert docs["price_new_nl_sources"]["description"].startswith("Source id(s)")
    assert "cars on the road" in docs["reg_de_fleet"]["description"]
    assert "first registrations" in docs["reg_de_new_registrations"]["description"]
    assert docs["reg_de_fleet_period"]["description"].startswith("Period")
    assert docs["reg_de_fleet_level"]["description"].startswith("generation | model")
    assert docs["reg_de_fleet_source"]["description"].startswith("Source id(s)")
    assert docs["mystery_column"] == {"name": "mystery_column", "unit": "", "description": ""}


def test_brand_falls_back_when_config_unreadable_or_empty(monkeypatch) -> None:
    # Regression (overnight coverage pass): a whitespace-only name in config/brand.yaml
    # used to return "" and publish an empty brand in LICENSE / README.md.
    monkeypatch.delenv(ob.BRAND_ENV, raising=False)

    def unreadable(self, *a, **kw):
        raise OSError("no config")

    monkeypatch.setattr(ob.Path, "read_text", unreadable)
    assert ob.brand_name() == ob.BRAND_FALLBACK
    monkeypatch.undo()
    monkeypatch.delenv(ob.BRAND_ENV, raising=False)
    monkeypatch.setattr(ob.yaml, "safe_load", lambda text: {"name": "  "})
    assert ob.brand_name() == ob.BRAND_FALLBACK
    monkeypatch.setenv(ob.BRAND_ENV, "  From Env  ")
    assert ob.brand_name() == "From Env"
