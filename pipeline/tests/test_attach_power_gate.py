"""Q-086: the attach-only power gate for RDW records ("<kW> kW" evidence)."""

from __future__ import annotations

from datetime import date

from ev_pipeline.match import matcher
from ev_pipeline.match.matcher import NO_POWER_MATCH, match_records, power_close
from ev_pipeline.match.seed import parse_manual_variants, parse_seed
from ev_pipeline.records import SourceRecord, SpecValue

RDW = {"id": "rdw", "name": "RDW", "licence": "CC0-1.0"}
ADEME = {"id": "ademe", "name": "ADEME", "licence": "Licence Ouverte 2.0"}

SEED = {
    "makes": [
        {
            "id": "tesla",
            "name": "Tesla",
            "models": [
                {
                    "id": "tesla-model-y",
                    "name": "Model Y",
                    "generations": [{"id": "tesla-model-y-juniper", "years": [2025, None]}],
                }
            ],
        },
        {
            "id": "audi",
            "name": "Audi",
            "models": [
                {
                    "id": "audi-q6-e-tron",
                    "name": "Q6 e-tron",
                    "generations": [{"id": "audi-q6-e-tron-gen1", "years": [2024, None]}],
                }
            ],
        },
        {
            "id": "volkswagen",
            "name": "Volkswagen",
            "models": [
                {
                    "id": "volkswagen-id4",
                    "name": "ID.4",
                    "generations": [{"id": "volkswagen-id4-gen1", "years": [2021, None]}],
                }
            ],
        },
    ]
}


def _v(gen: str, vid: str, name: str, kw: float | None, wltp: float, start: int = 2021):
    specs: dict[str, float] = {"wltp_range_km": wltp}
    if kw is not None:
        specs["power_kw"] = kw
    return {"generation_id": gen, "id": vid, "name": name, "years": [start, None], "specs": specs}


def _manual(rows: list[dict]):
    return parse_manual_variants({"variants": rows}, date(2026, 11, 14))[0]


def _rdw(make: str, model: str, kw: float | None, year: int, wltp: float, key: str = "r1"):
    return SourceRecord(
        source=RDW,
        record_key=key,
        make=make,
        model=model,
        variant_name=f"{kw:g} kW" if kw is not None else None,
        year=year,
        country="NL",
        specs={
            "wltp_range_km": SpecValue(value=wltp, unit="km"),
            "price_new": SpecValue(value=55590, unit="EUR"),
        },
        retrieved_at=date(2026, 11, 15),
        confidence="medium",
    )


def _placed(res, key: str = "r1") -> set[str]:
    return {
        mf.fact.subject_id.root
        for mf in res.spec_facts
        if mf.source_id == "rdw" and mf.fact.source_record == key
    }


def _reasons(res) -> list[str]:
    return [u.reason for u in res.unmatched if u.source_id == "rdw"]


MY = "tesla-model-y-juniper"
MODEL_Y = [
    _v(MY, f"{MY}-rwd", "RWD", 220, 500, 2025),
    _v(MY, f"{MY}-long-range-rwd", "Long Range RWD", 208, 610, 2025),
]


def test_tolerance_is_two_percent_or_three_kw_whichever_larger() -> None:
    assert power_close(100, 103) and not power_close(100, 103.5)  # 3 kW floor
    assert power_close(300, 306) and not power_close(300, 307)  # 2 % of the larger
    assert not power_close(210, 220)


def test_model_y_2025_378kw_does_not_land_on_long_range_rwd() -> None:
    """WLTP 600 is within 2 % of LR RWD's 610, but 378 kW is not 208 kW: review."""
    seed = parse_seed(SEED)
    rec = _rdw("TESLA", "MODEL Y", 378, 2025, 600)
    res = match_records([rec], seed, _manual(MODEL_Y))
    assert _placed(res) == set()
    [why] = _reasons(res)
    assert NO_POWER_MATCH in why and "378 kW" in why
    # No RDW NL price lands on a variant either.
    assert not any(mf.source_id == "rdw" for mf in res.spec_facts)


def test_model_y_power_match_wins_over_wltp() -> None:
    seed = parse_seed(SEED)
    rec = _rdw("TESLA", "MODEL Y", 209, 2025, 500)  # WLTP points at RWD, power at LR RWD
    res = match_records([rec], seed, _manual(MODEL_Y))
    assert _placed(res) == {"tesla-model-y-juniper-long-range-rwd"}


def test_q6_performance_does_not_land_on_quattro() -> None:
    seed = parse_seed(SEED)
    rows = [
        _v("audi-q6-e-tron-gen1", "audi-q6-e-tron-gen1-quattro", "quattro", 285, 625, 2024),
        _v("audi-q6-e-tron-gen1", "audi-q6-e-tron-gen1-sq6", "SQ6", 380, 598, 2024),
    ]
    rec = _rdw("AUDI", "Q6 E-TRON QUATTRO", 225, 2025, 630)  # name word + WLTP: quattro
    res = match_records([rec], seed, _manual(rows))
    assert _placed(res) == set()
    assert any(NO_POWER_MATCH in r for r in _reasons(res))


def test_q6_only_variant_with_contradicting_power_goes_to_review() -> None:
    """The 'generation's only variant' shortcut does not bypass the gate."""
    seed = parse_seed(SEED)
    rows = [_v("audi-q6-e-tron-gen1", "audi-q6-e-tron-gen1-quattro", "quattro", 285, 625, 2024)]
    res = match_records([_rdw("AUDI", "Q6 E-TRON", 225, 2025, 640)], seed, _manual(rows))
    assert _placed(res) == set()
    assert any(NO_POWER_MATCH in r for r in _reasons(res))


def test_id4_pro_4motion_does_not_land_on_gtx_by_name_words() -> None:
    seed = parse_seed(SEED)
    rows = [
        _v("volkswagen-id4-gen1", "volkswagen-id4-gen1-pro", "Pro", 150, 520),
        _v("volkswagen-id4-gen1", "volkswagen-id4-gen1-gtx", "GTX 4MOTION", 220, 480),
    ]
    rec = _rdw("VOLKSWAGEN", "ID.4 PRO 4MOTION", 210, 2024, 700)  # "4motion" matches GTX
    res = match_records([rec], seed, _manual(rows))
    assert _placed(res) == set()
    assert any(NO_POWER_MATCH in r for r in _reasons(res))
    # Before the gate the name word alone placed it on the GTX.
    old = matcher.POWER_GATE_SOURCES
    try:
        matcher.POWER_GATE_SOURCES = frozenset()
        res = match_records([rec], seed, _manual(rows))
        assert len(_placed(res)) == 1
    finally:
        matcher.POWER_GATE_SOURCES = old


def test_unknown_power_candidate_needs_other_evidence() -> None:
    seed = parse_seed(SEED)
    rows = [
        _v("volkswagen-id4-gen1", "volkswagen-id4-gen1-pro", "Pro", 150, 520),
        _v("volkswagen-id4-gen1", "volkswagen-id4-gen1-pure", "Pure", None, 360),
    ]
    # 125 kW contradicts Pro; Pure (power unknown) has WLTP evidence: placed.
    res = match_records([_rdw("VOLKSWAGEN", "ID.4", 125, 2022, 362)], seed, _manual(rows))
    assert _placed(res) == {"volkswagen-id4-gen1-pure"}
    # Same, but without any evidence for Pure: review, never a guess.
    res = match_records([_rdw("VOLKSWAGEN", "ID.4", 125, 2022, 900)], seed, _manual(rows))
    assert _placed(res) == set()
    assert any("no variant evidence" in r for r in _reasons(res))


def test_wltp_only_tie_goes_to_review() -> None:
    seed = parse_seed(SEED)
    rows = [
        _v("volkswagen-id4-gen1", "volkswagen-id4-gen1-pro", "Pro", None, 520),
        _v("volkswagen-id4-gen1", "volkswagen-id4-gen1-pro-perf", "Pro Performance", None, 522),
    ]
    res = match_records([_rdw("VOLKSWAGEN", "ID.4", None, 2022, 521)], seed, _manual(rows))
    assert _placed(res) == set()
    assert any("ambiguous evidence: WLTP fits" in r for r in _reasons(res))


def test_record_without_power_keeps_old_behaviour() -> None:
    seed = parse_seed(SEED)
    res = match_records([_rdw("TESLA", "MODEL Y", None, 2025, 600)], seed, _manual(MODEL_Y))
    assert _placed(res) == {"tesla-model-y-juniper-long-range-rwd"}


def test_ademe_is_not_gated() -> None:
    assert "ademe" not in matcher.POWER_GATE_SOURCES
    seed = parse_seed(SEED)
    rec = SourceRecord(
        source=ADEME,
        record_key="a1",
        make="TESLA",
        model="MODEL Y",
        variant_name="Long Range RWD (378Kw)",
        year=None,
        specs={"wltp_range_km": SpecValue(value=600, unit="km")},
        retrieved_at=date(2026, 11, 15),
        confidence="medium",
    )
    res = match_records([rec], seed, _manual(MODEL_Y))
    placed = {mf.fact.subject_id.root for mf in res.spec_facts if mf.source_id == "ademe"}
    assert placed == {"tesla-model-y-juniper-long-range-rwd"}


def test_gate_rows_survive_the_unmatched_cap() -> None:
    from ev_pipeline.match.matcher import MatchResult, UnmatchedRow
    from ev_pipeline.match.review import unmatched_rows

    res = MatchResult()
    res.unmatched = [
        UnmatchedRow("eea", f"e{i}", "AUDI", f"M{i}", "", "2024", "model not in seed")
        for i in range(30)
    ]
    gate = f"attach-only: {NO_POWER_MATCH} (378 kW) in tesla-model-y-juniper"
    res.unmatched.append(UnmatchedRow("rdw", "r1", "TESLA", "MODEL Y", "378 kW", "2025", gate))
    rows = unmatched_rows(res, max_rows=10)
    assert rows[0].source_id == "rdw" and NO_POWER_MATCH in rows[0].reason
