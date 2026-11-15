"""T-051: the 8 top-40 models added to the real seed place the source names they were built from.

Records are built in memory from the names seen in staging (RDW, EEA, KBA, DfT, KilowattApp);
no network, no staging files. Generations are picked by year, as in the release.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from ev_pipeline.match.matcher import find_generation, find_model_noted, match_view
from ev_pipeline.match.seed import load_seed
from ev_pipeline.records import SourceRecord, SpecValue

REAL_SEED = Path(__file__).parents[2] / "data" / "seed" / "models.yaml"
SOURCES = {
    "rdw": {"id": "rdw", "name": "RDW", "licence": "CC0-1.0"},
    "eea": {"id": "eea", "name": "EEA", "licence": "CC-BY-4.0"},
    "kba-fz10": {"id": "kba-fz10", "name": "KBA", "licence": "DL-DE-BY-2.0"},
    "dft-veh": {"id": "dft-veh", "name": "DfT", "licence": "OGL-UK-3.0"},
    "kilowatt-openev": {"id": "kilowatt-openev", "name": "KilowattApp", "licence": "MIT"},
}
NEW_MODELS = {
    "volvo-ex30",
    "bmw-ix1",
    "bmw-ix3",
    "opel-mokka",
    "mercedes-eqb",
    "porsche-taycan",
    "bmw-ix",
    "ford-explorer",
}


@pytest.fixture(scope="module")
def seed():
    return load_seed(REAL_SEED)


def _rec(sid: str, make: str, model: str, year: int | None, variant: str | None = None):
    return SourceRecord(
        source=SOURCES[sid],
        record_key=f"{sid}:{make}|{model}|{variant}|{year}",
        kind="registration_count",
        make=make,
        model=model,
        variant_name=variant,
        year=year,
        country="NL",
        specs={"registered_count": SpecValue(value=10, unit="count")},
        retrieved_at=date(2026, 11, 15),
        confidence="high",
    )


def _place(seed, rec):
    view = match_view(rec)
    make_id = seed.make_id_for(rec.make, rec.source.id.root, True)
    assert make_id is not None, rec.make
    model, why, _ = find_model_noted(seed, make_id, view, True)
    if model is None:
        return None, None, why
    gen, why = find_generation(model, rec.year)
    return model.id, gen.id if gen else None, why


def test_all_eight_models_in_seed(seed):
    assert set(seed.models) >= NEW_MODELS


@pytest.mark.parametrize(
    ("sid", "make", "model", "year", "variant", "model_id", "gen_id"),
    [
        ("rdw", "VOLVO", "EX30 CROSS COUNTRY", 2025, None, "volvo-ex30", "volvo-ex30-gen1"),
        ("dft-veh", "VOLVO", "VOLVO EX30", None, "EX30 PLUS AWD", "volvo-ex30", "volvo-ex30-gen1"),
        ("rdw", "BMW", "IX1 EDRIVE20", 2024, None, "bmw-ix1", "bmw-ix1-gen1"),
        ("kba-fz10", "BMW", "X1", 2025, None, "bmw-ix1", "bmw-ix1-gen1"),
        # iX3: plain name = first car; power-number names from 2026 = second car (year picks)
        ("rdw", "BMW", "IX3", 2025, None, "bmw-ix3", "bmw-ix3-gen1"),
        ("rdw", "BMW", "IX3 50 XDRIVE", 2026, None, "bmw-ix3", "bmw-ix3-gen2"),
        ("rdw", "BMW", "IX3-40", 2026, None, "bmw-ix3", "bmw-ix3-gen2"),
        ("kba-fz10", "BMW", "X3", 2026, None, "bmw-ix3", "bmw-ix3-gen2"),
        ("eea", "BMW AG", "IX3 50 XDRIVE", 2025, None, "bmw-ix3", "bmw-ix3-gen1"),
        # iX must not take iX1 / iX3 names, and the reverse
        ("rdw", "BMW", "IX XDRIVE40", 2022, None, "bmw-ix", "bmw-ix-gen1"),
        ("rdw", "BMW", "IX M70 XDRIVE", 2025, None, "bmw-ix", "bmw-ix-gen1"),
        ("rdw", "OPEL", "MOKKA", 2021, None, "opel-mokka", "opel-mokka-gen1"),
        ("rdw", "OPEL", "MOKKA ULTIMATE EV", 2021, None, "opel-mokka", "opel-mokka-gen1"),
        ("dft-veh", "VAUXHALL", "VAUXHALL MOKKA", None, "MOKKA GS EV", "opel-mokka", "opel-mokka-gen1"),  # noqa: E501
        ("kba-fz10", "OPEL", "MOKKA", 2026, None, "opel-mokka", "opel-mokka-gen1"),
        ("rdw", "MERCEDES-BENZ", "EQB 250+", 2024, None, "mercedes-eqb", "mercedes-eqb-gen1"),
        ("eea", "MERCEDES-BENZ", "CLASSE EQB", 2025, None, "mercedes-eqb", "mercedes-eqb-gen1"),
        ("rdw", "MERCEDES-BENZ", "GLB 250+", 2026, None, "mercedes-eqb", "mercedes-eqb-glb"),
        ("kba-fz10", "MERCEDES", "GLB", 2025, None, "mercedes-eqb", "mercedes-eqb-gen1"),
        ("kba-fz10", "MERCEDES", "GLB", 2026, None, "mercedes-eqb", "mercedes-eqb-glb"),
        ("rdw", "PORSCHE", "TAYCAN 4S", 2020, None, "porsche-taycan", "porsche-taycan-gen1"),
        ("rdw", "FORD", "EXPLORER", 2024, None, "ford-explorer", "ford-explorer-gen1"),
        ("dft-veh", "FORD", "FORD EXPLORER", None, "EXPLORER SELECT EV", "ford-explorer", "ford-explorer-gen1"),  # noqa: E501
        ("kilowatt-openev", "Ford", "Explorer Extended Range AWD", 2024, None, "ford-explorer", "ford-explorer-gen1"),  # noqa: E501
    ],
)  # fmt: skip
def test_source_names_place(seed, sid, make, model, year, variant, model_id, gen_id):
    rec = _rec(sid, make, model, year, variant)
    mid, gid, why = _place(seed, rec)
    if year is None:  # no year (DfT): model level; only the model is checked
        assert mid == model_id, why
        return
    assert (mid, gid) == (model_id, gen_id), why


@pytest.mark.parametrize(
    ("make", "model", "year"),
    [
        ("OPEL", "MOKKA X", 2018),  # ICE predecessor name: outside the generation
        ("VOLVO", "EX30", 2022),  # before the first evidence year
        ("FORD", "EXPLORER", 2010),  # single stray car
    ],
)
def test_out_of_range_stays_unplaced(seed, make, model, year):
    _, gid, why = _place(seed, _rec("rdw", make, model, year))
    assert gid is None
    assert "outside every generation" in why or "not in seed" in why


def test_bare_x1_x3_only_for_kba(seed):
    # KBA's series name means the BEV column there; RDW 'X1' cars stay unmatched.
    for name in ("X1", "X3"):
        mid, _, _ = _place(seed, _rec("rdw", "BMW", name, 2022))
        assert mid is None
