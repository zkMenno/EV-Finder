"""Seed dedup (2026-11-15): OpenEV rows that duplicate a seed variant join it by alias.

Release 1 had rows like `renault-megane-e-tech-gen1-40-kwh` (OpenEV "40 kWh": 38 / 40 kWh,
96 kW, MY2023-25) next to seed `renault-megane-e-tech-gen1-ev40` (40 kWh, 96 kW, 2022-24).
`source_names` in variants.yaml joins them; these tests cover what that needed:

- year-scoped source names (OpenEV e-208 "Base" is the 50 kWh car to MY2023, the 51 kWh car
  from MY2024), with overlap checks;
- a power gate on alias joins (an alias never joins a different motor);
- seed facts don't anchor year bands on an aliased variant (seed DC 85 vs OpenEV DC 130 is a
  disagreement for merge, not a model-year change);
- `source_holds`: records that go to review by name and year (OpenEV's mis-modelled Q4 e-tron).
"""

from __future__ import annotations

import importlib.util
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from ev_pipeline.match.matcher import (
    NO_BATTERY_MATCH,
    NO_SEED_POWER_MATCH,
    SOURCE_HOLD,
    MatchResult,
    UnmatchedRow,
    match_records,
)
from ev_pipeline.match.review import unmatched_rows
from ev_pipeline.match.seed import (
    parse_manual_variants,
    parse_seed,
    parse_source_holds,
    span_covers,
)
from ev_pipeline.records import SourceRecord, SpecValue

REPO = Path(__file__).resolve().parents[2]
OPENEV = {"id": "openev", "name": "Open EV Data", "licence": "CDLA-Permissive-2.0"}
KW = {"id": "kilowatt-openev", "name": "KilowattApp", "licence": "MIT-with-attribution"}

P208 = "peugeot-e-208-p21"
MEG = "renault-megane-e-tech-gen1"
Q4 = "audi-q4-e-tron-gen1"


def _model(mid: str, name: str, gid: str, start: int) -> dict[str, Any]:
    return {"id": mid, "name": name, "generations": [{"id": gid, "years": [start, None]}]}


SEED = {
    "makes": [
        {
            "id": "peugeot",
            "name": "Peugeot",
            "models": [_model("peugeot-e-208", "e-208", P208, 2019)],
        },
        {
            "id": "renault",
            "name": "Renault",
            "models": [_model("renault-megane", "Megane E-Tech", MEG, 2022)],
        },
        {
            "id": "audi",
            "name": "Audi",
            "models": [_model("audi-q4-e-tron", "Q4 e-tron", Q4, 2021)],
        },
    ]
}


def _v(gen: str, vid: str, name: str, years: list[int | None], names: Any = None, **specs: float):
    v: dict[str, Any] = {"generation_id": gen, "id": vid, "name": name, "years": years}
    v["specs"] = specs
    if names is not None:
        v["source_names"] = names
    return v


def _manual(*variants: dict[str, Any]):
    mv, problems = parse_manual_variants({"variants": list(variants)}, date(2026, 11, 14))
    assert problems == []
    return mv


def _rec(model: str, variant: str, year: int | None, source: dict = OPENEV, **specs: float):
    return SourceRecord(
        source=source,
        record_key=f"{source['id']}:{model}/{variant}/{year}",
        kind="spec",
        make=model.split()[0] if model.startswith("Audi") else "",
        model=model,
        variant_name=variant,
        year=year,
        specs={
            k: SpecValue(value=v, unit="kWh" if "kwh" in k else ("km" if "km" in k else "kW"))
            for k, v in specs.items()
        },
        retrieved_at=date(2026, 11, 14),
        confidence="medium",
    )


def _peugeot(model: str, variant: str, year: int | None, **specs: float) -> SourceRecord:
    r = _rec(model, variant, year, **specs)
    return r.model_copy(update={"make": "Peugeot"})


def _renault(variant: str, year: int, **specs: float) -> SourceRecord:
    return _rec("Megane E-Tech", variant, year, **specs).model_copy(update={"make": "Renault"})


def _audi(variant: str, year: int, **specs: float) -> SourceRecord:
    return _rec("Q4 e-tron", variant, year, **specs).model_copy(update={"make": "Audi"})


def _on(res: MatchResult, vid: str) -> set[str]:
    return {str(mf.fact.source_record) for mf in res.spec_facts if mf.fact.subject_id.root == vid}


def _reasons(res: MatchResult) -> list[str]:
    return [u.reason for u in res.unmatched]


E208 = [
    _v(
        P208,
        f"{P208}-50kwh",
        "50 kWh / 100 kW",
        [2019, 2023],
        {"openev": [{"name": "Base", "years": [None, 2023]}]},
        battery_kwh_gross=50,
        power_kw=100,
    ),
    _v(
        P208,
        f"{P208}-51kwh",
        "51 kWh / 115 kW",
        [2023, None],
        {"openev": [{"name": "Base", "years": [2024, None]}]},
        battery_kwh_gross=51,
        power_kw=115,
    ),
]


# --- year-scoped source names ------------------------------------------------------------


def test_year_scoped_name_joins_the_variant_of_that_model_year() -> None:
    seed = parse_seed(SEED)
    recs = [
        _peugeot("e-208", "Base", 2023, battery_kwh_net=46, battery_kwh_gross=50, power_kw=100),
        _peugeot("e-208", "Base", 2024, battery_kwh_net=50, battery_kwh_gross=54, power_kw=115),
        _peugeot("e-208", "Base", 2025, battery_kwh_net=50, battery_kwh_gross=54, power_kw=115),
    ]
    res = match_records(recs, seed, _manual(*E208), scoped_aliases=True)
    assert sorted(res.variants) == [f"{P208}-50kwh", f"{P208}-51kwh"]  # no "-base" row
    assert _on(res, f"{P208}-50kwh") == {f"{P208}-50kwh", "openev:e-208/Base/2023"}
    assert _on(res, f"{P208}-51kwh") == {
        f"{P208}-51kwh",
        "openev:e-208/Base/2024",
        "openev:e-208/Base/2025",
    }


def test_year_scoped_name_does_not_cover_a_record_without_year() -> None:
    assert span_covers(None, None) and span_covers((2024, None), 2030)
    assert not span_covers((2024, None), None) and not span_covers((None, 2023), 2024)


def test_overlapping_year_scoped_names_on_two_variants_are_an_error() -> None:
    seed = parse_seed(SEED)
    upto, later = (
        [{"name": "Base", "years": [None, 2023]}],
        [{"name": "Base", "years": [2023, None]}],
    )
    bad = [
        _v(P208, f"{P208}-a", "A", [2019, 2023], {"openev": upto}),
        _v(P208, f"{P208}-b", "B", [2023, None], {"openev": later}),
    ]
    with pytest.raises(ValueError, match="source_names"):
        match_records([], seed, _manual(*bad))
    backwards = [{"name": "X", "years": [2025, 2024]}]
    with pytest.raises(ValueError, match="years"):
        parse_manual_variants(
            {"variants": [_v(P208, f"{P208}-c", "C", [2019, None], {"openev": backwards})]},
            date(2026, 11, 14),
        )


# --- gates on alias joins ----------------------------------------------------------------


def test_alias_join_with_contradicting_power_goes_to_review() -> None:
    seed = parse_seed(SEED)
    rec = _peugeot("e-208", "Base", 2022, battery_kwh_gross=50, power_kw=136)  # e-208 GT motor
    res = match_records([rec], seed, _manual(*E208), scoped_aliases=True)
    assert sorted(res.variants) == [f"{P208}-50kwh", f"{P208}-51kwh"]
    assert len(res.unmatched) == 1
    assert res.unmatched[0].reason.startswith(f"{NO_SEED_POWER_MATCH} {P208}-50kwh (136 vs 100")


def test_alias_join_within_five_percent_power_joins() -> None:
    seed = parse_seed(SEED)
    rec = _peugeot("e-208", "Base", 2022, battery_kwh_gross=50, power_kw=104)
    res = match_records([rec], seed, _manual(*E208), scoped_aliases=True)
    assert res.unmatched == [] and "openev:e-208/Base/2022" in _on(res, f"{P208}-50kwh")


def test_same_name_join_is_not_power_gated() -> None:
    """Only aliases are power-gated: a same-name record of a later year with a stronger motor
    stays on the variant (and may become a year band), as before."""
    seed = parse_seed(SEED)
    rec = _peugeot("e-208", "50 kWh / 100 kW", 2023, battery_kwh_gross=50, power_kw=115)
    res = match_records([rec], seed, _manual(*E208), scoped_aliases=True)
    assert res.unmatched == [] and "openev:e-208/50 kWh / 100 kW/2023" in _on(res, f"{P208}-50kwh")


def test_alias_join_still_passes_the_battery_gate() -> None:
    seed = parse_seed(SEED)
    rec = _peugeot("e-208", "Base", 2022, battery_kwh_gross=77, power_kw=100)
    res = match_records([rec], seed, _manual(*E208), scoped_aliases=True)
    assert len(res.unmatched) == 1 and res.unmatched[0].reason.startswith(NO_BATTERY_MATCH)


# --- year bands on aliased variants ------------------------------------------------------

MEGANE = [
    _v(
        MEG,
        f"{MEG}-ev40",
        "EV40 (40 kWh)",
        [2022, 2024],
        {"openev": ["40 kWh"]},
        battery_kwh_net=40,
        power_kw=96,
        dc_peak_kw=85,
    ),
    _v(
        MEG,
        f"{MEG}-ev60",
        "EV60 (60 kWh)",
        [2022, None],
        battery_kwh_net=60,
        power_kw=160,
        dc_peak_kw=130,
    ),
]


def test_seed_facts_do_not_anchor_year_bands_on_an_aliased_variant() -> None:
    """Seed DC 85 (2022) vs OpenEV DC 130 (2023+) made `-ev40-2023`, the same duplicate
    under a new id. On an aliased variant only the source's own years can make a band."""
    seed = parse_seed(SEED)
    recs = [
        _renault("40 kWh", y, battery_kwh_net=38, battery_kwh_gross=40, power_kw=96, dc_peak_kw=130)
        for y in (2023, 2024, 2025)
    ]
    res = match_records(recs, seed, _manual(*MEGANE), scoped_aliases=True)
    assert sorted(res.variants) == [f"{MEG}-ev40", f"{MEG}-ev60"]
    assert res.year_bands == []
    assert len(_on(res, f"{MEG}-ev40")) == 4  # seed record + three OpenEV years


def test_aliased_variant_still_splits_on_the_sources_own_year_change() -> None:
    seed = parse_seed(SEED)
    recs = [
        _renault("40 kWh", 2023, battery_kwh_net=38, power_kw=96, wltp_range_km=300),
        _renault("40 kWh", 2025, battery_kwh_net=38, power_kw=96, wltp_range_km=340),
    ]
    res = match_records(recs, seed, _manual(*MEGANE), scoped_aliases=True)
    assert [b["new_ids"] for b in res.year_bands] == [[f"{MEG}-ev40-2025"]]


def test_same_name_join_keeps_the_seed_as_band_anchor() -> None:
    seed = parse_seed(SEED)
    recs = [_renault("EV60 (60 kWh)", 2024, battery_kwh_net=60, power_kw=160, dc_peak_kw=150)]
    res = match_records(recs, seed, _manual(*MEGANE), scoped_aliases=True)
    assert [b["new_ids"] for b in res.year_bands] == [[f"{MEG}-ev60-2024"]]


# --- source holds ------------------------------------------------------------------------

Q4_SEED = [
    _v(Q4, f"{Q4}-40", "40 e-tron", [2021, 2023], battery_kwh_net=77, power_kw=150),
    _v(Q4, f"{Q4}-50-quattro", "50 e-tron quattro", [2021, 2023], battery_kwh_net=77, power_kw=220),
]
HOLDS = {
    "source_holds": [
        {
            "generation_id": Q4,
            "source": "openev",
            "names": ["50", "quattro"],
            "years": [2024, None],
            "reason": "MY2024+ records repeat MY2023 figures",
        }
    ]
}


def test_held_records_go_to_review_and_make_no_row() -> None:
    seed = parse_seed(SEED)
    holds = parse_source_holds(HOLDS)
    recs = [
        _audi("50", 2024, battery_kwh_net=73, power_kw=150),
        _audi("quattro", 2025, battery_kwh_net=73, power_kw=220),
        _audi("50", 2023, battery_kwh_net=73, power_kw=150),  # outside the hold's years
    ]
    res = match_records(recs, seed, _manual(*Q4_SEED), scoped_aliases=True, holds=holds)
    assert sorted(res.variants) == [f"{Q4}-40", f"{Q4}-50", f"{Q4}-50-quattro"]
    assert _reasons(res) == [f"{SOURCE_HOLD}: MY2024+ records repeat MY2023 figures"] * 2
    assert _on(res, f"{Q4}-50") == {"openev:Q4 e-tron/50/2023"}


def test_hold_is_scoped_to_its_source() -> None:
    seed = parse_seed(SEED)
    holds = parse_source_holds(HOLDS)
    rec = _rec("Q4 e-tron", "50", 2024, source=KW, battery_kwh_net=77, power_kw=150)
    rec = rec.model_copy(update={"make": "Audi"})
    res = match_records([rec], seed, _manual(*Q4_SEED), scoped_aliases=True, holds=holds)
    assert not any(SOURCE_HOLD in r for r in _reasons(res))


def _hold(**kw: Any) -> dict[str, Any]:
    return {"source_holds": [{"generation_id": Q4, "source": "openev", **kw}]}


@pytest.mark.parametrize(
    "bad, msg",
    [
        ({"source_holds": {"a": 1}}, "must be a list"),
        (_hold(names=["x"]), "reason"),
        (_hold(names=[], reason="r"), "names"),
        (_hold(names=["x"], reason="r", why=1), "unknown"),
        (_hold(names=["x"], reason="r", years=[2025, 2024]), "years"),
    ],
)
def test_bad_holds_are_rejected(bad: dict, msg: str) -> None:
    with pytest.raises(ValueError, match=msg):
        parse_source_holds(bad)


def test_hold_rows_survive_the_review_file_cap() -> None:
    res = MatchResult()
    res.unmatched = [
        UnmatchedRow("ademe", f"k{i}", "Audi", "Q4", "", "2024", "no variant") for i in range(30)
    ]
    res.unmatched.append(
        UnmatchedRow("openev", "q", "Audi", "Q4", "50", "2024", f"{SOURCE_HOLD}: r")
    )
    rows = unmatched_rows(res, max_rows=5)
    assert any(SOURCE_HOLD in r.reason for r in rows)


# --- variants.yaml validator ---------------------------------------------------------------


def _validator():
    spec = importlib.util.spec_from_file_location(
        "validate_variants", REPO / "data" / "seed" / "validate_variants.py"
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_validator_accepts_year_scoped_names_and_rejects_overlaps() -> None:
    mod = _validator()
    base = {"generation_id": "g", "drivetrain": "fwd", "specs": {}, "confidence": "low"}
    doc = {
        "source": {"id": "seed-manual", "name": "s", "licence": "CC-BY-4.0", "attribution": "a"},
        "variants": [
            {
                **base,
                "id": "g-a",
                "name": "A",
                "years": [2019, 2023],
                "source_names": {"openev": [{"name": "Base", "years": [None, 2023]}]},
            },
            {
                **base,
                "id": "g-b",
                "name": "B",
                "years": [2023, None],
                "source_names": {"openev": [{"name": "Base", "years": [2024, None]}]},
            },
            {
                **base,
                "id": "g-c",
                "name": "C",
                "years": [2023, None],
                "source_names": {"openev": [{"name": "BASE", "years": [2025, None]}]},
            },
            {
                **base,
                "id": "g-d",
                "name": "D",
                "years": [2023, None],
                "source_names": {"openev": [{"name": "X", "years": [2025, 2024]}]},
            },
        ],
        "source_holds": [
            {"generation_id": "g", "source": "openev", "names": ["Y"], "reason": "r"},
            {"generation_id": "nope", "source": "openev", "names": ["Y"], "reason": "r"},
        ],
    }
    errors = mod.validate(doc, {"g": (2019, None)})
    assert any("g-c" in e and "also on g-b" in e for e in errors)
    assert any("g-d" in e and "end before start" in e for e in errors)
    assert any("source_holds[1]" in e and "not in models.yaml" in e for e in errors)
    assert not any("g-a)" in e or "g-b)" in e or "source_holds[0]" in e for e in errors)


def test_real_variants_file_validates() -> None:
    mod = _validator()
    assert mod.main(["x"]) == 0
