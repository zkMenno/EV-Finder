"""T-005 matching rules: normalisation, model/generation/variant matching, unmatched output."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

import pytest

from ev_pipeline.match.matcher import (
    aggregate_counts,
    find_generation,
    find_model,
    match_records,
    normalise_unit,
)
from ev_pipeline.match.normalise import key, slug, strip_accents, tokens
from ev_pipeline.match.review import unmatched_rows, write_unmatched
from ev_pipeline.match.seed import load_manual_variants, load_seed
from ev_pipeline.records import SourceRecord, SpecValue

FIX = Path(__file__).parent / "fixtures" / "release"


@pytest.fixture(scope="module")
def seed():
    return load_seed(FIX / "models.yaml")


def _rec(make: str, model: str, variant: str | None = None, year: int | None = None, **kw):
    src = kw.pop(
        "source", {"id": "openev", "name": "OpenEV Data", "licence": "CDLA-Permissive-2.0"}
    )
    return SourceRecord(
        source=src,
        record_key=kw.pop("record_key", f"{make}/{model}/{variant}/{year}"),
        make=make,
        model=model,
        variant_name=variant,
        year=year,
        specs=kw.pop("specs", {"battery_kwh_net": SpecValue(value=50, unit="kWh")}),
        retrieved_at=date(2026, 11, 14),
        confidence="medium",
        **kw,
    )


def _load_staging(name: str) -> list[SourceRecord]:
    path = FIX / "staging" / f"{name}.records.jsonl"
    return [SourceRecord.model_validate_json(x) for x in path.read_text().splitlines() if x]


# --- normalisation -----------------------------------------------------------------------


def test_normalise_accents_case_punctuation() -> None:
    assert strip_accents("ë-C4") == "e-C4"
    assert key("ë-C4") == key("e-C4") == key("E-C4") == "ec4"
    assert key("Mustang Mach-E") == key("MUSTANG MACH E") == "mustangmache"
    assert key("ID.3") == key("ID 3") == "id3"
    assert tokens("MODEL 3 LONG RANGE") == ["model", "3", "long", "range"]
    assert slug("Long Range AWD") == "long-range-awd"
    assert slug("50 kWh") == "50-kwh"


# --- make / model ------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("make", "model", "expected"),
    [
        ("Tesla", "Model 3", "tesla-model-3"),
        ("TESLA", "MODEL 3", "tesla-model-3"),  # RDW upper case
        ("TESLA", "MODEL 3 LONG RANGE", "tesla-model-3"),  # longest token prefix
        ("Tesla", "Tesla Model 3", "tesla-model-3"),  # make repeated in model name
        ("Citroën", "ë-C4", "citroen-e-c4"),
        ("CITROEN", "E-C4", "citroen-e-c4"),  # alias + accent-free make
        ("Ford", "Mustang Mach-E", "ford-mustang-mach-e"),
        ("Ford", "MACH-E", "ford-mustang-mach-e"),  # name_alias
        ("Nissan", "LEAF", "nissan-leaf"),
    ],
)
def test_model_matching(seed, make: str, model: str, expected: str) -> None:
    make_id = seed.make_id_for(make)
    assert make_id is not None
    found, why = find_model(seed, make_id, _rec(make, model))
    assert found is not None, why
    assert found.id == expected


def test_model_prefix_respects_token_boundaries(seed) -> None:
    # "Model 30" must not match "Model 3": prefixes are whole tokens.
    found, why = find_model(seed, "tesla", _rec("Tesla", "Model 30"))
    assert found is None and why == "model not in seed"


def test_make_aliases(seed) -> None:
    assert seed.make_id_for("CITROËN") == "citroen"
    assert seed.make_id_for("Polestar") is None


# --- generation --------------------------------------------------------------------------


def test_generation_by_year_and_open_end(seed) -> None:
    m3 = seed.models["tesla-model-3"]
    assert find_generation(m3, 2019)[0].id == "tesla-model-3-gen1"
    assert find_generation(m3, 2023)[0].id == "tesla-model-3-gen1"
    assert find_generation(m3, 2031)[0].id == "tesla-model-3-highland"  # end null = open
    gen, why = find_generation(m3, 2017)
    assert gen is None and "outside every generation" in why


def test_shared_boundary_year_goes_to_newer_generation(seed) -> None:
    assert find_generation(seed.models["renault-zoe"], 2019)[0].id == "renault-zoe-ph2"


def test_no_year_needs_single_generation(seed) -> None:
    assert find_generation(seed.models["citroen-e-c4"], None)[0].id == "citroen-e-c4-c41"
    gen, why = find_generation(seed.models["tesla-model-3"], None)
    assert gen is None and "2 generations" in why


# --- variants ----------------------------------------------------------------------------


def test_variant_ids_and_year_merge(seed) -> None:
    res = match_records(_load_staging("openev") + _load_staging("eea"), seed)
    lr = res.variants["tesla-model-3-gen1-long-range"]
    assert lr.years == {2022, 2023}  # two openev years + eea merge into one variant
    assert lr.source_ids == {"openev", "eea"}
    assert "tesla-model-3-gen1-performance" in res.variants  # RDW-style upper case
    assert "citroen-e-c4-c41-50-kwh" in res.variants
    assert res.variants["citroen-e-c4-c41-50-kwh"].source_ids == {"openev", "eea"}


def test_seed_manual_lends_its_id_to_same_named_variant(seed) -> None:
    manual, problems = load_manual_variants(FIX / "variants.yaml")
    assert problems == []
    res = match_records(_load_staging("openev"), seed, manual)
    assert "tesla-model-3-gen1-long-range" not in res.variants
    lr = res.variants["tesla-model-3-gen1-lr"]
    assert lr.source_ids == {"openev", "seed-manual"}
    assert lr.explicit_end == 2023


def test_base_variant_when_no_name(seed) -> None:
    res = match_records([_rec("Citroën", "e-C4", None, 2022)], seed)
    assert list(res.variants) == ["citroen-e-c4-c41-base"]


def test_fact_ids_and_units(seed) -> None:
    res = match_records(_load_staging("openev"), seed)
    ids = {mf.fact.id: mf.fact for mf in res.spec_facts}
    f = ids["openev:citroen/e-c4/2021-50:consumption_kwh_100km"]
    assert f.value == pytest.approx(15.5)  # 155 Wh/km -> kWh/100km
    assert f.unit == "kWh/100km"
    assert f.subject_type.value == "variant"
    assert f.subject_id.root == "citroen-e-c4-c41-50-kwh"
    assert str(f.retrieved_at) == "2026-11-14"


def test_unit_conversion_and_rejection() -> None:
    assert normalise_unit("wltp_range_km", SpecValue(value=100, unit="mi"))[0] == pytest.approx(
        160.9344
    )
    assert normalise_unit("price_new", SpecValue(value=1, unit="eur"))[1] == "EUR"
    assert normalise_unit("price_new", SpecValue(value=1, unit="USD"))[2]
    assert normalise_unit("battery_kwh_net", SpecValue(value=1, unit="Ah"))[2]


# --- registration counts -----------------------------------------------------------------


def test_registration_counts_aggregate_to_generation(seed) -> None:
    res = match_records(_load_staging("rdw"), seed)
    agg = aggregate_counts(res.count_facts, seed, "rdw", "NL")
    assert agg["tesla-model-3-gen1"].value == 3000  # 2020 + 2021
    assert agg["tesla-model-3-highland"].value == 500
    assert len(agg["tesla-model-3-gen1"].fact_ids) == 2
    # LEAF has no year and two generations: kept as a model-level fact, not split.
    assert "nissan-leaf-ze0" not in agg and "nissan-leaf-ze1" not in agg
    assert any(mf.fact.subject_type.value == "model" for mf in res.count_facts)


def test_model_level_count_used_for_single_generation_model(seed) -> None:
    rec = _rec(
        "CITROEN",
        "E-C4",
        None,
        None,
        source={"id": "rdw", "name": "RDW", "licence": "CC0-1.0"},
        kind="registration_count",
        country="NL",
        specs={"registered_count": SpecValue(value=42, unit="count")},
    )
    agg = aggregate_counts(match_records([rec], seed).count_facts, seed, "rdw", "NL")
    assert agg["citroen-e-c4-c41"].value == 42
    assert agg["citroen-e-c4-c41"].level == "model"


# --- unmatched ---------------------------------------------------------------------------


def test_unmatched_csv(seed, tmp_path: Path) -> None:
    res = match_records(_load_staging("openev") + _load_staging("rdw"), seed)
    reasons = {r.record_key: r.reason for r in res.unmatched}
    assert reasons["tesla/cybertruck/2024"] == "model not in seed"
    assert "outside every generation" in reasons["nissan/leaf/2010"]
    assert "no year" in reasons["tesla/model-3/no-year"]
    # Makes not in the seed are only counted, not listed one by one.
    assert res.other_makes[("rdw", "POLESTAR")] == 1
    assert res.other_makes[("openev", "POLESTAR")] == 1
    rows = unmatched_rows(res)
    out = tmp_path / "unmatched.csv"
    write_unmatched(out, rows)
    lines = list(csv.DictReader(out.open()))
    assert list(lines[0]) == [
        "source_id",
        "record_key",
        "make",
        "model",
        "variant_name",
        "year",
        "reason",
    ]
    assert sum(1 for r in lines if r["record_key"] == "(summary)") == 3
    assert len(lines) == 6


def test_unmatched_file_stays_small(seed) -> None:
    recs = [_rec("Tesla", f"Roadster {i}", None, 2022, record_key=f"k{i}") for i in range(3000)]
    recs += [_rec(f"Make{i}", "X", None, 2022, record_key=f"m{i}") for i in range(500)]
    res = match_records(recs, seed)
    rows = unmatched_rows(res)
    assert len(rows) < 2000
    assert rows[-1].make == "(other makes)"


def test_nyland_never_matches(seed) -> None:
    rec = _rec(
        "Tesla",
        "Model 3",
        "Long Range",
        2022,
        source={"id": "nyland", "name": "Nyland", "licence": "permission-pending"},
    )
    res = match_records([rec], seed)
    assert res.spec_facts == [] and res.variants == {}
    assert res.excluded["nyland"] == 1
