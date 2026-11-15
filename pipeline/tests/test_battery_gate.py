"""Battery gate: a record whose battery contradicts the seed variant never lands on it.

Bug (release 1, 2026-11-15): renault-zoe-ph1-r90 (seed: Z.E. 40, 41 kWh) showed 23.3 kWh.
KilowattApp's "Zoe R90 Entry" / "Zoe R90" + "Entry" records (23.3 kWh, the Z.E. 22 pack)
attached to the R90 by the shared name word "r90", and KilowattApp ranks above seed-manual
for battery_kwh_net, so 23.3 won. The same class: OpenEV "Q4 e-tron 40" MY2023+ (48 kWh)
merged into the seed "40 e-tron" (77 kWh) because the made-up id equalled the seed's id.
"""

from __future__ import annotations

from datetime import date

from ev_pipeline.match.matcher import (
    NO_BATTERY_MATCH,
    battery_close,
    battery_contradicts,
    match_records,
)
from ev_pipeline.match.review import PRIORITY_REASONS
from ev_pipeline.match.seed import parse_manual_variants, parse_seed
from ev_pipeline.records import SourceRecord, SpecValue

KW = {"id": "kilowatt-openev", "name": "KilowattApp", "licence": "MIT-with-attribution"}
OPENEV = {"id": "openev", "name": "Open EV Data", "licence": "MIT"}

ZOE = "renault-zoe-ph1"
Q4 = "audi-q4-e-tron-gen1"
ENYAQ = "skoda-enyaq-gen1"
SEED = {
    "makes": [
        {
            "id": "renault",
            "name": "Renault",
            "models": [
                {
                    "id": "renault-zoe",
                    "name": "Zoe",
                    "generations": [{"id": ZOE, "years": [2013, 2019]}],
                }
            ],
        },
        {
            "id": "audi",
            "name": "Audi",
            "models": [
                {
                    "id": "audi-q4-e-tron",
                    "name": "Q4 e-tron",
                    "generations": [{"id": Q4, "years": [2021, None]}],
                }
            ],
        },
        {
            "id": "skoda",
            "name": "Skoda",
            "models": [
                {
                    "id": "skoda-enyaq",
                    "name": "Enyaq",
                    "generations": [{"id": ENYAQ, "years": [2020, None]}],
                }
            ],
        },
    ]
}


def _v(gen: str, vid: str, name: str, years: list[int | None], **specs: float) -> dict:
    return {"generation_id": gen, "id": vid, "name": name, "years": years, "specs": specs}


ZOE_ROWS = [
    _v(ZOE, f"{ZOE}-q210", "Q210 (22 kWh)", [2013, 2015], battery_kwh_net=22, ac_kw=43),
    _v(ZOE, f"{ZOE}-r240", "R240 (22 kWh)", [2015, 2016], battery_kwh_net=22, ac_kw=22),
    _v(ZOE, f"{ZOE}-q90", "Q90 (Z.E. 40)", [2017, 2019], battery_kwh_net=41, ac_kw=43),
    _v(ZOE, f"{ZOE}-r90", "R90 (Z.E. 40)", [2017, 2019], battery_kwh_net=41, ac_kw=22),
    _v(ZOE, f"{ZOE}-r110", "R110 (Z.E. 40)", [2018, 2019], battery_kwh_net=41, ac_kw=22),
]


def _manual(rows: list[dict]):
    return parse_manual_variants({"variants": rows}, date(2026, 11, 15))[0]


def _rec(
    source: dict,
    key: str,
    make: str,
    model: str,
    variant: str | None,
    year: int,
    **specs: float,
) -> SourceRecord:
    units = {"battery_kwh_net": "kWh", "battery_kwh_gross": "kWh", "ac_kw": "kW"}
    units |= {"power_kw": "kW", "wltp_range_km": "km"}
    return SourceRecord(
        source=source,
        record_key=key,
        make=make,
        model=model,
        variant_name=variant,
        year=year,
        specs={f: SpecValue(value=v, unit=units[f]) for f, v in specs.items()},
        retrieved_at=date(2026, 11, 15),
        confidence="medium",
    )


def _placed(res, key: str) -> set[str]:
    return {mf.fact.subject_id.root for mf in res.spec_facts if mf.fact.source_record == key}


def _reason(res, key: str) -> str:
    [why] = [u.reason for u in res.unmatched if u.record_key == key]
    return why


def test_tolerance_same_basis_15pct_cross_basis_20pct() -> None:
    assert battery_close((41, "net"), (36, "net"))  # 12 %
    assert not battery_close((41, "net"), (34, "net"))  # 17 %
    assert battery_close((20.5, "net"), (24.2, "gross"))  # e-Golf, 15.3 % across bases
    assert not battery_close((68, "net"), (98, "gross"))  # Mach-E SR vs ER
    assert not battery_contradicts(set(), {(41, "net")})  # unknown: no contradiction
    assert not battery_contradicts({(23.3, "net")}, set())


def test_zoe_r90_entry_23kwh_never_lands_on_r90_ze40() -> None:
    """The reported bug: name word "r90" pointed at the 41 kWh R90; the battery says no."""
    seed = parse_seed(SEED)
    recs = [
        _rec(KW, "k-entry", "Renault", "Zoe R90 Entry", None, 2017, battery_kwh_net=23.3),
        _rec(KW, "k-r90e", "Renault", "Zoe R90", "Entry", 2017, battery_kwh_net=23.3),
        _rec(KW, "k-r90", "Renault", "Zoe", "R90", 2017, battery_kwh_net=41.0),
    ]
    res = match_records(recs, seed, _manual(ZOE_ROWS))
    assert _placed(res, "k-entry") == set()
    assert _placed(res, "k-r90e") == set()
    assert "battery gate ruled out" in _reason(res, "k-entry")
    assert f"{ZOE}-r90" in _reason(res, "k-entry")
    # The 41 kWh R90 record still lands on the R90 (same name).
    assert _placed(res, "k-r90") == {f"{ZOE}-r90"}
    r90 = {
        mf.fact.value
        for mf in res.spec_facts
        if mf.fact.subject_id.root == f"{ZOE}-r90" and mf.fact.field.value == "battery_kwh_net"
    }
    assert r90 == {41.0}


def test_exact_name_does_not_bypass_the_gate() -> None:
    seed = parse_seed(SEED)
    rec = _rec(KW, "k1", "Renault", "Zoe", "R90 (Z.E. 40)", 2017, battery_kwh_net=23.3)
    res = match_records([rec], seed, _manual(ZOE_ROWS))
    assert _placed(res, "k1") == set()


def test_only_variant_with_contradicting_battery_goes_to_review() -> None:
    seed = parse_seed(SEED)
    rows = [_v(ZOE, f"{ZOE}-r90", "R90 (Z.E. 40)", [2017, 2019], battery_kwh_net=41)]
    rec = _rec(KW, "k1", "Renault", "Zoe", None, 2017, battery_kwh_net=23.3)
    res = match_records([rec], seed, _manual(rows))
    assert _placed(res, "k1") == set()
    why = _reason(res, "k1")
    assert NO_BATTERY_MATCH in why and "23.3 vs 41 kWh" in why
    assert any(p in why for p in PRIORITY_REASONS)  # never cut from unmatched.csv


def test_gate_leftover_needs_its_own_evidence() -> None:
    """Ruling out the 41 kWh cars leaves Q210 and R240 (22 kWh); nothing says which: review,
    not the 'only candidate left' shortcut."""
    seed = parse_seed(SEED)
    rows = [r for r in ZOE_ROWS if r["id"] in (f"{ZOE}-r240", f"{ZOE}-r90")]
    rec = _rec(KW, "k1", "Renault", "Zoe", None, 2017, battery_kwh_net=23.3)
    res = match_records([rec], seed, _manual(rows))
    assert _placed(res, "k1") == set()
    assert "battery gate ruled out" in _reason(res, "k1")


def test_kwh_evidence_still_places_after_gate() -> None:
    """A record with a fitting battery and its own evidence (kWh within 1 kWh) attaches."""
    seed = parse_seed(SEED)
    rows = [r for r in ZOE_ROWS if r["id"] in (f"{ZOE}-r240", f"{ZOE}-r90")]
    rec = _rec(KW, "k1", "Renault", "Zoe", None, 2016, battery_kwh_net=22.0)
    res = match_records([rec], seed, _manual(rows))
    assert _placed(res, "k1") == {f"{ZOE}-r240"}


def test_name_word_shared_with_ruled_out_variants_is_no_evidence() -> None:
    """KilowattApp "Enyaq iV 50" (52 kWh) is not the "60 (iV 60)" just because the 80 is out:
    "iv" is shared with the ruled-out 80 as well."""
    seed = parse_seed(SEED)
    rows = [
        _v(ENYAQ, f"{ENYAQ}-60", "60 (iV 60)", [2020, None], battery_kwh_net=58),
        _v(ENYAQ, f"{ENYAQ}-80", "80 (iV 80)", [2020, None], battery_kwh_net=77),
    ]
    rec = _rec(KW, "k1", "Skoda", "Enyaq iV 50", None, 2021, battery_kwh_net=52.0)
    res = match_records([rec], seed, _manual(rows))
    assert _placed(res, "k1") == set()
    assert NO_BATTERY_MATCH in _reason(res, "k1")


def test_main_pass_id_collision_with_seed_variant_is_gated() -> None:
    """OpenEV "40" (48 kWh) makes id <gen>-40, which is the seed "40 e-tron" (77 kWh)."""
    seed = parse_seed(SEED)
    rows = [_v(Q4, f"{Q4}-40", "40 e-tron", [2021, 2023], battery_kwh_net=77, power_kw=150)]
    bad = _rec(OPENEV, "o-40", "Audi", "Q4 e-tron", "40", 2023, battery_kwh_net=48.0)
    good = _rec(OPENEV, "o-40b", "Audi", "Q4 e-tron", "40", 2022, battery_kwh_net=76.6)
    res = match_records([bad, good], seed, _manual(rows))
    assert _placed(res, "o-40") == set()
    assert f"{NO_BATTERY_MATCH} {Q4}-40 (48 vs 77 kWh)" in _reason(res, "o-40")
    assert _placed(res, "o-40b") == {f"{Q4}-40"}


def test_main_pass_gross_record_fits_net_seed_across_bases() -> None:
    seed = parse_seed(SEED)
    rows = [_v(Q4, f"{Q4}-40", "40 e-tron", [2021, 2023], battery_kwh_net=77)]
    rec = _rec(OPENEV, "o1", "Audi", "Q4 e-tron", "40 e-tron", 2022, battery_kwh_gross=82.0)
    res = match_records([rec], seed, _manual(rows))
    assert _placed(res, "o1") == {f"{Q4}-40"}
