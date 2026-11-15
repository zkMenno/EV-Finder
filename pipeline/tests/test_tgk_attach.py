"""RDW type-approval (rdw-tgk) records: source-scoped aliases and the TGK evidence picker.

Fixture `fixtures/rdw_tgk/match_pre2020.jsonl` holds 17 real rdw-tgk staging records (CC0,
RDW Open Data, fetched 2026-11-15) for the e-Golf, i3, Leaf and Zoe. The seed below mirrors
the real seed's generations and variants (years, batteries) for those models.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from ev_pipeline.match.matcher import (
    TGK_MISFIT,
    TGK_TIE,
    match_records,
    tgk_energies,
)
from ev_pipeline.match.seed import parse_manual_variants, parse_seed
from ev_pipeline.records import SourceRecord, SpecValue

FIXTURE = Path(__file__).parent / "fixtures" / "rdw_tgk" / "match_pre2020.jsonl"

SEED = {
    "makes": [
        {
            "id": "volkswagen",
            "name": "Volkswagen",
            "models": [
                {
                    "id": "volkswagen-e-golf",
                    "name": "e-Golf",
                    "aliases_by_source": {"rdw,rdw-tgk": ["GOLF"]},
                    "generations": [
                        {"id": "volkswagen-e-golf-mk7", "years": [2014, 2017]},
                        {"id": "volkswagen-e-golf-mk75", "years": [2017, 2020]},
                    ],
                }
            ],
        },
        {
            "id": "bmw",
            "name": "BMW",
            "models": [
                {
                    "id": "bmw-i3",
                    "name": "i3",
                    "name_aliases": ["i3s"],
                    "generations": [{"id": "bmw-i3-i01", "years": [2013, 2022]}],
                }
            ],
        },
        {
            "id": "nissan",
            "name": "Nissan",
            "models": [
                {
                    "id": "nissan-leaf",
                    "name": "Leaf",
                    "name_aliases": ["LEAF"],
                    "generations": [
                        {"id": "nissan-leaf-ze0", "years": [2011, 2017]},
                        {"id": "nissan-leaf-ze1", "years": [2018, 2025]},
                    ],
                }
            ],
        },
        {
            "id": "renault",
            "name": "Renault",
            "models": [
                {
                    "id": "renault-zoe",
                    "name": "Zoe",
                    "generations": [
                        {"id": "renault-zoe-ph1", "years": [2013, 2019]},
                        {"id": "renault-zoe-ph2", "years": [2019, 2024]},
                    ],
                }
            ],
        },
    ]
}


def _v(gen: str, suffix: str, name: str, years: list, specs: dict, drive: str = "fwd"):
    return {
        "generation_id": gen,
        "id": f"{gen}-{suffix}",
        "name": name,
        "years": years,
        "drivetrain": drive,
        "specs": specs,
    }


VARIANTS = [
    _v("volkswagen-e-golf-mk7", "24kwh", "24.2 kWh", [2014, 2017], {"battery_kwh_gross": 24.2}),
    _v("volkswagen-e-golf-mk75", "36kwh", "35.8 kWh", [2017, 2020], {"battery_kwh_gross": 35.8}),
    _v("bmw-i3-i01", "60ah", "i3 60 Ah (22 kWh)", [2013, 2016], {"battery_kwh_net": 18.8}, "rwd"),
    _v("bmw-i3-i01", "94ah", "i3 94 Ah (33 kWh)", [2016, 2018], {"battery_kwh_net": 27.2}, "rwd"),
    _v("bmw-i3-i01", "120ah", "i3 120 Ah (42 kWh)", [2018, 2022], {"battery_kwh_net": 37.9}, "rwd"),
    _v("bmw-i3-i01", "i3s", "i3s (94 Ah / 120 Ah)", [2017, 2022], {"power_kw": 135}, "rwd"),
    _v("nissan-leaf-ze0", "24kwh", "24 kWh", [2011, 2015], {"battery_kwh_net": 21}),
    _v("nissan-leaf-ze0", "30kwh", "30 kWh", [2016, 2017], {"battery_kwh_net": 27}),
    _v("nissan-leaf-ze1", "40kwh", "40 kWh", [2018, 2025], {"battery_kwh_net": 39}),
    _v("renault-zoe-ph1", "q210", "Q210 (22 kWh)", [2013, 2015], {"battery_kwh_net": 22}),
    _v("renault-zoe-ph1", "r240", "R240 (22 kWh)", [2015, 2016], {"battery_kwh_net": 22}),
    _v("renault-zoe-ph1", "q90", "Q90 (Z.E. 40)", [2017, 2019], {"battery_kwh_net": 41}),
    _v("renault-zoe-ph1", "r90", "R90 (Z.E. 40)", [2017, 2019], {"battery_kwh_net": 41}),
    _v("renault-zoe-ph1", "r110", "R110 (Z.E. 40)", [2018, 2019], {"battery_kwh_net": 41}),
    _v("renault-zoe-ph2", "r110", "R110 Z.E. 50", [2019, 2024], {"battery_kwh_net": 52}),
]


def _records() -> dict[str, SourceRecord]:
    """Fixture records by "<TAN>|<variant>|<uitvoering>" (revision dropped)."""
    out = {}
    for line in FIXTURE.read_text(encoding="utf-8").splitlines():
        rec = SourceRecord.model_validate(json.loads(line))
        out[rec.record_key.split(":", 1)[1].rsplit("|", 1)[0]] = rec
    return out


def _run(recs: list[SourceRecord], variants: list[dict] | None = None):
    manual = parse_manual_variants({"variants": variants or VARIANTS}, date(2026, 11, 14))[0]
    return match_records(recs, parse_seed(SEED), manual, scoped_aliases=True)


def _placed(res, rec: SourceRecord) -> set[str]:
    return {
        mf.fact.subject_id.root
        for mf in res.spec_facts
        if mf.source_id == "rdw-tgk" and mf.fact.source_record == rec.record_key
    }


def _reason(res, rec: SourceRecord) -> str:
    [why] = [u.reason for u in res.unmatched if u.record_key == rec.record_key]
    return why


R = _records()
GOLF_2014 = R["e1*2007/46*0623*10|GAC4EAGAX0|FA1FA1CZ003E0GAON1ML01VR0"]  # 190 km NEDC
GOLF_2017_OLD = R["e1*2007/46*0623*21|GAC45EAGAX0|FA1FA1CZ003E0GAON1ML02VR0"]  # 175 km
GOLF_2017_NEW = R["e1*2007/46*0623*26|GAC4EAZAX0|FA1FA1MD001E0GAON1ML01VR0"]  # 300 km
I3_2013 = R["e1*2007/46*1213*01|1Z21|0A040000"]  # 190 km
I3_2016_94 = R["e1*2007/46*1213*05|1Z61|0A140000"]  # 312 km
I3S_2017 = R["e1*2007/46*1213*07|7Z61|0A040000"]  # I3S 280 km
I3_2017 = R["e1*2007/46*1213*07|7Z21|0A140000"]  # 300 km, 2017: 94 Ah or early 120 Ah
I3_2018_120 = R["e1*2007/46*1213*09|8P21|0AW40000"]  # WLTP 310 km
LEAF_2012 = R["e11*2007/46*0230*03|A|A01"]  # 175 km
LEAF_2013 = R["e11*2007/46*0230*05|A|A02"]  # 199 km
LEAF_2015 = R["e11*2007/46*0230*08|A|A02"]  # 199 km, 2015: 24 or 30 kWh by year
LEAF_30 = R["e11*2007/46*0230*10|A|A03"]  # "NISSAN LEAF 30KWH" 250 km
ZOE_Q210 = R["e2*2007/46*0251*00|AGV|AGVYA0"]  # 210 km, 2013
ZOE_R240 = R["e2*2007/46*0251*06|AGV|AGVYB0"]  # 240 km, 2015
ZOE_225 = R["e2*2007/46*0251*06|AGV|AGVYB1"]  # 225 km, 2015: Q210 or R240
ZOE_240_2013 = R["e2*2007/46*0251*08|V|YB0"]  # 240 km but first admitted 2013
ZOE_ZE40 = R["e2*2007/46*0251*10|V|YE0"]  # 403 km, 41 kWh: Q90 / R90 / R110


def test_energy_is_range_times_consumption() -> None:
    assert tgk_energies(GOLF_2014) == [24.1]  # 190 km x 12.7 kWh/100 km
    assert tgk_energies(I3_2018_120) == [47.1]  # WLTP 310 km x 15.2


def test_e_golf_alias_and_battery_split_the_shared_2017_year() -> None:
    res = _run([GOLF_2014, GOLF_2017_OLD, GOLF_2017_NEW])
    assert _placed(res, GOLF_2014) == {"volkswagen-e-golf-mk7-24kwh"}
    # 2017 is in both generations; the battery fit picks one, never a guess.
    assert _placed(res, GOLF_2017_OLD) == {"volkswagen-e-golf-mk7-24kwh"}
    assert _placed(res, GOLF_2017_NEW) == {"volkswagen-e-golf-mk75-36kwh"}


def test_e_golf_without_tgk_alias_is_not_in_seed() -> None:
    seed = json.loads(json.dumps(SEED))
    seed["makes"][0]["models"][0]["aliases_by_source"] = {"rdw": ["GOLF"]}
    manual = parse_manual_variants({"variants": VARIANTS}, date(2026, 11, 14))[0]
    res = match_records([GOLF_2014], parse_seed(seed), manual, scoped_aliases=True)
    assert "model not in seed" in _reason(res, GOLF_2014)


def test_i3_battery_years_and_name() -> None:
    res = _run([I3_2013, I3_2016_94, I3S_2017, I3_2017, I3_2018_120])
    assert _placed(res, I3_2013) == {"bmw-i3-i01-60ah"}
    assert _placed(res, I3_2016_94) == {"bmw-i3-i01-94ah"}  # 2016: 60 Ah too old for 312 km
    assert _placed(res, I3S_2017) == {"bmw-i3-i01-i3s"}  # "I3S" in the trade names
    assert _placed(res, I3_2018_120) == {"bmw-i3-i01-120ah"}
    # 2017, 39 kWh drawn: fits 94 Ah and 120 Ah (2018 - 1 year): review, not a guess.
    why = _reason(res, I3_2017)
    assert TGK_TIE in why and "bmw-i3-i01-94ah" in why and "bmw-i3-i01-120ah" in why


def test_leaf_by_battery_and_name_kwh() -> None:
    res = _run([LEAF_2012, LEAF_2013, LEAF_2015, LEAF_30])
    assert _placed(res, LEAF_2012) == {"nissan-leaf-ze0-24kwh"}
    assert _placed(res, LEAF_2013) == {"nissan-leaf-ze0-24kwh"}
    assert _placed(res, LEAF_30) == {"nissan-leaf-ze0-30kwh"}  # 37.5 kWh is no 21 kWh pack
    # 2015 with 30 kWh starting 2016 (+-1 year): 29.9 kWh fits both packs -> review.
    assert TGK_TIE in _reason(res, LEAF_2015)


def test_zoe_range_in_the_variant_name() -> None:
    res = _run([ZOE_Q210, ZOE_R240, ZOE_225, ZOE_240_2013, ZOE_ZE40])
    assert _placed(res, ZOE_Q210) == {"renault-zoe-ph1-q210"}
    assert _placed(res, ZOE_R240) == {"renault-zoe-ph1-r240"}
    assert TGK_TIE in _reason(res, ZOE_225)  # 225 km: no name, both 22 kWh packs fit
    # 240 km points at R240, but R240 starts in 2015: a contradiction goes to review.
    assert TGK_MISFIT in _reason(res, ZOE_240_2013) and "2013" in _reason(res, ZOE_240_2013)
    why = _reason(res, ZOE_ZE40)  # three Z.E. 40 variants share the 41 kWh pack
    assert TGK_TIE in why and "renault-zoe-ph1-q90" in why and "renault-zoe-ph1-r110" in why


def test_battery_misfit_goes_to_review_even_with_one_candidate() -> None:
    only_22 = [_v("renault-zoe-ph1", "22", "22 kWh", [2013, 2019], {"battery_kwh_net": 22})]
    res = _run([ZOE_ZE40], only_22)  # 53.6 kWh drawn is no 22 kWh pack
    assert TGK_MISFIT in _reason(res, ZOE_ZE40) and "battery" in _reason(res, ZOE_ZE40)


def _tgk(model: str, year: int, specs: dict, name: str | None = None) -> SourceRecord:
    return SourceRecord(
        source={"id": "rdw-tgk", "name": "RDW TGK", "licence": "CC0-1.0"},
        record_key=f"k:{model}|{year}|{sorted(specs.items())}",
        kind="spec",
        make="NISSAN",
        model=model,
        variant_name=name or model,
        year=year,
        specs={k: SpecValue(value=v, unit=u) for k, (v, u) in specs.items()},
        retrieved_at=date(2026, 11, 15),
        confidence="high",
    )


TWIN = [
    _v("nissan-leaf-ze1", "fwd", "40 kWh", [2018, 2025], {"battery_kwh_net": 39}),
    _v("nissan-leaf-ze1", "awd", "40 kWh 4x4", [2018, 2025], {"battery_kwh_net": 39}, "awd"),
]
RANGE = {"wltp_range_km": (270, "km"), "consumption_kwh_100km": (17.1, "kWh/100km")}


def test_no_30min_power_prefers_awd_as_tie_break_only() -> None:
    no_power = _tgk("LEAF", 2019, RANGE)
    single = _tgk("LEAF", 2019, RANGE | {"power_30min_kw": (90, "kW")})
    res = _run([no_power, single], TWIN)
    assert _placed(res, no_power) == {"nissan-leaf-ze1-awd"}
    # One 30-minute row is not proof of one motor (I-Pace): tie, review.
    assert TGK_TIE in _reason(res, single)


def test_unknown_battery_candidate_needs_name_evidence() -> None:
    rows = [_v("nissan-leaf-ze1", "base", "Base", [2018, 2025], {"power_kw": 110})]
    res = _run([_tgk("LEAF", 2019, RANGE)], rows)  # only candidate: kept (nothing contradicts)
    assert len(res.attached) == 1
    rows.append(_v("nissan-leaf-ze1", "tekna", "Tekna", [2018, 2025], {"power_kw": 110}))
    plain, tekna = _tgk("LEAF", 2019, RANGE), _tgk("LEAF TEKNA", 2019, RANGE, "TEKNA")
    res = _run([plain, tekna], rows)
    assert TGK_MISFIT in _reason(res, plain) and "no name evidence" in _reason(res, plain)
    assert _placed(res, tekna) == {"nissan-leaf-ze1-tekna"}
