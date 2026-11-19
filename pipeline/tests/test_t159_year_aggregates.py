"""T-159: RDW model-year aggregates (`...[merk|handelsbenaming|jaar]...` records).

- Own WLTP: an aggregate whose only evidence is its own WLTP, while 2+ variants' years hold
  its year, goes to review (the 2021 Model Y aggregate, 507 km, sat on the Performance row).
- Year only: no evidence at all, rows split only by year (no overlap): the one variant whose
  years hold the record's year gets it (the 2026 E-Tourneo Courier price).
"""

from __future__ import annotations

from datetime import date

from ev_pipeline.match.matcher import (
    NO_EVIDENCE,
    YEAR_AGG_OWN_WLTP,
    is_year_aggregate,
    match_records,
)
from ev_pipeline.match.seed import parse_manual_variants, parse_seed
from ev_pipeline.records import SourceRecord, SpecValue

RDW = {"id": "rdw", "name": "RDW", "licence": "CC0-1.0"}
AGG = "8ys7-d773+m9d7-ebf2[merk|handelsbenaming|jaar]:"

SEED = parse_seed(
    {
        "makes": [
            {
                "id": "tesla",
                "name": "Tesla",
                "models": [
                    {
                        "id": "tesla-model-y",
                        "name": "Model Y",
                        "generations": [{"id": "tesla-model-y-gen1", "years": [2021, 2024]}],
                    }
                ],
            },
            {
                "id": "ford",
                "name": "Ford",
                "models": [
                    {
                        "id": "ford-e-tourneo-courier",
                        "name": "Tourneo Courier",
                        "generations": [
                            {"id": "ford-e-tourneo-courier-gen1", "years": [2024, None]}
                        ],
                    }
                ],
            },
        ]
    }
)


def _v(gen: str, vid: str, name: str, years: list, **specs: float) -> dict:
    return {"generation_id": gen, "id": vid, "name": name, "years": years, "specs": specs}


def _manual(rows: list[dict]):
    return parse_manual_variants({"variants": rows}, date(2026, 11, 19))[0]


MODEL_Y = [
    _v("tesla-model-y-gen1", "y-lr", "Long Range", [2021, 2024], wltp_range_km=533),
    _v("tesla-model-y-gen1", "y-perf", "Performance", [2021, 2024], wltp_range_km=514),
]
COURIER = [
    _v("ford-e-tourneo-courier-gen1", "c-base", "Base", [2024, 2025], battery_kwh_net=43),
    _v("ford-e-tourneo-courier-gen1", "c-46", "46 kWh", [2026, None], battery_kwh_net=46),
]


def _rec(make: str, model: str, year: int, key: str, **specs: tuple[float, str]) -> SourceRecord:
    return SourceRecord(
        source=RDW,
        record_key=key,
        make=make,
        model=model,
        year=year,
        country="NL",
        specs={f: SpecValue(value=v, unit=u) for f, (v, u) in specs.items()},
        retrieved_at=date(2026, 11, 19),
        confidence="medium",
    )


def _where(rec: SourceRecord, rows: list[dict]) -> str:
    res = match_records([rec], SEED, _manual(rows))
    placed = {
        mf.fact.subject_id.root
        for mf in res.spec_facts
        if mf.source_id == "rdw" and mf.fact.source_record == rec.record_key
    }
    if placed:
        [vid] = placed
        return vid
    [why] = [u.reason for u in res.unmatched if u.record_key == rec.record_key]
    return why


def test_only_aggregate_keys_count():
    assert is_year_aggregate(_rec("TESLA", "MODEL Y", 2021, AGG + "TESLA|MODEL Y|2021#wltp"))
    variant_key = "m9d7-ebf2+8ys7-d773[merk|handelsbenaming|jaar|type|variant]:T|Y|2022|003|Y5LD"
    assert not is_year_aggregate(_rec("TESLA", "MODEL Y", 2022, variant_key))


def test_own_wltp_is_no_evidence_when_two_variants_hold_the_year():
    key = AGG + "TESLA|MODEL Y|2021#wltp_range_km"
    rec = _rec("TESLA", "MODEL Y", 2021, key, wltp_range_km=(507, "km"))
    why = _where(rec, MODEL_Y)
    assert YEAR_AGG_OWN_WLTP in why and "y-perf" in why
    # The same record keyed per type / variant is real evidence and still places.
    vkey = "m9d7-ebf2+8ys7-d773[merk|handelsbenaming|jaar|type|variant]:TESLA|MODEL Y|2021|003|X"
    assert _where(_rec("TESLA", "MODEL Y", 2021, vkey, wltp_range_km=(507, "km")), MODEL_Y) == (
        "y-perf"
    )


def test_own_wltp_still_places_when_only_one_variant_holds_the_year():
    rows = [MODEL_Y[0], {**MODEL_Y[1], "years": [2022, 2024]}]
    key = AGG + "TESLA|MODEL Y|2021#wltp_range_km"
    rec = _rec("TESLA", "MODEL Y", 2021, key, wltp_range_km=(533, "km"))
    assert _where(rec, rows) == "y-lr"


def test_year_only_split_places_by_year():
    key = AGG + "FORD|TOURNEO COURIER|2026#price_new:NL"
    rec = _rec("FORD", "TOURNEO COURIER", 2026, key, price_new=(42048, "EUR"))
    assert _where(rec, COURIER) == "c-46"
    old = _rec("FORD", "TOURNEO COURIER", 2025, key.replace("2026", "2025"), price_new=(1, "EUR"))
    assert _where(old, COURIER) == "c-base"


def test_year_only_needs_rows_that_do_not_overlap():
    rows = [COURIER[0], {**COURIER[1], "years": [2025, None]}]  # 2025 in both
    key = AGG + "FORD|TOURNEO COURIER|2026#price_new:NL"
    rec = _rec("FORD", "TOURNEO COURIER", 2026, key, price_new=(42048, "EUR"))
    assert NO_EVIDENCE in _where(rec, rows)
