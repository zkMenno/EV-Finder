"""A-05 overnight review: regression tests for findings (audits/A-05-overnight-review.md).

The F1 and F6 tests were xfail(strict=True) until the fixes landed (2026-11-15); they are
plain regression tests now. The A-05 fix tests for the other findings follow below.
"""

from __future__ import annotations

from datetime import date

from ev_pipeline.match.matcher import YEAR_AGG_OWN_WLTP, VariantInfo, match_records
from ev_pipeline.match.seed import parse_manual_variants, parse_seed
from ev_pipeline.records import SourceRecord, SpecValue

RDW = {"id": "rdw", "name": "RDW", "licence": "CC0-1.0"}

SEED = {
    "makes": [
        {
            "id": "volvo",
            "name": "Volvo",
            "models": [
                {
                    "id": "volvo-ex30",
                    "name": "EX30",
                    "generations": [{"id": "volvo-ex30-gen1", "years": [2023, None]}],
                }
            ],
        }
    ]
}
GEN = "volvo-ex30-gen1"


def _v(vid: str, name: str, kw: float, wltp: float) -> dict:
    return {
        "generation_id": GEN,
        "id": f"{GEN}-{vid}",
        "name": name,
        "years": [2023, None],
        "specs": {"power_kw": kw, "wltp_range_km": wltp},
    }


ROWS = [
    _v("base", "base", 200, 344),  # OpenEV names the entry trim "base"
    _v("69-kwh", "69 kWh", 200, 476),
    _v("twin-motor", "Twin Motor", 315, 449),
]


def _coarse_rdw(wltp: float) -> SourceRecord:
    """An RDW make|model|year group record: no variant name, no power evidence (its WLTP is
    the median of a plate sample over all trims of that year)."""
    return SourceRecord(
        source=RDW,
        record_key="8ys7-d773+m9d7-ebf2[merk|handelsbenaming|jaar]:VOLVO|EX30|2024#wltp_range_km",
        make="VOLVO",
        model="EX30",
        variant_name=None,
        year=2024,
        specs={"wltp_range_km": SpecValue(value=wltp, unit="km")},
        retrieved_at=date(2026, 11, 15),
        confidence="medium",
    )


def _placed(res) -> set[str]:
    return {mf.fact.subject_id.root for mf in res.spec_facts if mf.source_id == "rdw"}


def test_named_never_treats_missing_name_as_base() -> None:
    """Root cause (fixed): a record without a variant name is no exact name match for a
    variant called "base"."""
    info = VariantInfo(id=f"{GEN}-base", generation_id=GEN, name="base")
    assert info.named("rdw", None) is False
    assert info.named("rdw", "") is False
    assert info.named("rdw", "Base") is True


def test_nameless_rdw_group_does_not_land_on_base_by_name() -> None:
    """475 km is the Extended Range figure (69 kWh variant, 476 km); it must never become
    the 51 kWh base car's WLTP. Either 69 kWh (WLTP evidence) or review is acceptable."""
    seed = parse_seed(SEED)
    manual = parse_manual_variants({"variants": ROWS}, date(2026, 11, 14))[0]
    res = match_records([_coarse_rdw(475)], seed, manual)
    assert f"{GEN}-base" not in _placed(res)


# --- F (merge): a SPREAD_SOURCES source whose own vote conflicts still lifts confidence -----

from ev_pipeline.match.matcher import MatchedFact, priority_of  # noqa: E402
from ev_pipeline.merge.merge import merge_facts  # noqa: E402
from ev_pipeline.schema_models import Fact  # noqa: E402

_LIC = {"rdw-tgk": "CC0-1.0", "openev": "CDLA-Permissive-2.0"}


def _mf(source: str, value: float, key: str, year: int) -> MatchedFact:
    fact = Fact(
        id=f"{source}:{key}:wltp_range_km",
        subject_type="variant",
        subject_id="x-gen1-base",
        field="wltp_range_km",
        value=value,
        unit="km",
        source={"id": source, "name": source, "licence": _LIC[source]},
        retrieved_at=date(2026, 11, 15),
        confidence="medium",
    )
    return MatchedFact(fact, source, priority_of(source), year)


def test_tgk_whose_vote_conflicts_does_not_confirm_the_value() -> None:
    """openev 400 wins; TGK's own vote (earliest version) says 340, a later TGK version says
    400. TGK disagrees as a source, so the value must not reach `high` on TGK's account."""
    facts = [_mf("openev", 400, "o", 2021), _mf("rdw-tgk", 340, "a", 2020)]
    facts.append(_mf("rdw-tgk", 400, "b", 2022))
    mg = merge_facts(facts)
    assert mg.value == 400
    assert any(f.source_id == "rdw-tgk" for f in mg.conflicts)  # the vote is a conflict...
    assert mg.confidence != "high"  # ...so TGK must not also confirm the value


# --- A-05 fixes: regression tests ----------------------------------------------------------

import json  # noqa: E402
import os  # noqa: E402
import shutil  # noqa: E402
from datetime import UTC, datetime  # noqa: E402
from pathlib import Path  # noqa: E402

import pytest  # noqa: E402

from ev_pipeline.commands.releases import ReleaseOpError, rollback  # noqa: E402
from ev_pipeline.health.state import release_sources_doc  # noqa: E402
from ev_pipeline.match.matcher import _distinct_tokens, name_score  # noqa: E402
from ev_pipeline.merge.policy import FieldPolicy, Policies, parse_policies  # noqa: E402
from ev_pipeline.qa.value_guard import guard_impossible, guard_needs_backing  # noqa: E402
from ev_pipeline.release import build  # noqa: E402
from ev_pipeline.sources.rdw_tgk.adapter import Stats, version_values  # noqa: E402

FUELECO = {"id": "fueleconomy", "name": "fueleconomy.gov", "licence": "US-PD"}
WLTP_POLICY = FieldPolicy(order=("eea", "rdw", "rdw-tgk", "openev"), mode="priority", tol_pct=2)


def _fe(model: str, epa: float, key: str = "1") -> SourceRecord:
    return SourceRecord(
        source=FUELECO,
        record_key=f"vehicles.csv:id={key};market=us",
        make="Volvo",
        model=model,
        variant_name=None,
        year=2025,
        specs={"epa_range_km": SpecValue(value=epa, unit="km")},
        retrieved_at=date(2026, 11, 15),
        confidence="high",
    )


def _placed_by(res, sid: str) -> set[str]:
    return {mf.fact.subject_id.root for mf in res.spec_facts if mf.source_id == sid}


def _match(recs: list[SourceRecord], rows: list[dict] = ROWS):
    manual = parse_manual_variants({"variants": rows}, date(2026, 11, 14))[0]
    return match_records(recs, parse_seed(SEED), manual)


def test_f1_nameless_epa_record_goes_to_review_without_evidence() -> None:
    """A nameless EPA row with no trim words is no evidence for any of three variants."""
    res = _match([_fe("EX30", 402)])
    assert _placed_by(res, "fueleconomy") == set()
    assert any("attach-only" in u.reason for u in res.unmatched)


def test_f1_nameless_record_attaches_to_the_only_variant() -> None:
    res = _match([_fe("EX30", 402)], ROWS[:1])
    assert _placed_by(res, "fueleconomy") == {f"{GEN}-base"}


def test_f1_nameless_record_with_unique_evidence_attaches_there() -> None:
    """RDW year group at 475 km: only the 69 kWh variant (476 km) fits; never 'base'.
    T-159: the group's WLTP is a median over all trims of that year, so with 2+ variants
    whose years hold 2024 it is no evidence for one of them: review. With only the 69 kWh
    variant holding the year, it attaches there as before."""
    res = _match([_coarse_rdw(475)])
    assert _placed(res) == set()
    assert any(YEAR_AGG_OWN_WLTP in u.reason and "69-kwh" in u.reason for u in res.unmatched)
    later = [r if r["id"].endswith("69-kwh") else {**r, "years": [2025, None]} for r in ROWS]
    assert _placed(_match([_coarse_rdw(475)], later)) == {f"{GEN}-69-kwh"}


def test_f1_no_word_variant_does_not_win_a_tie_on_nothing() -> None:
    """Equal evidence (kWh fits both), record words shared with neither: the fewest-words
    tie-break would hand it to 'base' (no words). It goes to review instead."""
    rows = [_v("base", "base", 200, 344), _v("ultra", "Ultra", 200, 344)]
    for r in rows:
        r["specs"]["battery_kwh_net"] = 49
    rec = SourceRecord(
        source={"id": "kilowatt-openev", "name": "KilowattApp", "licence": "CC-BY-4.0"},
        record_key="k#1",
        make="Volvo",
        model="EX30",
        variant_name="Single Motor",
        year=2024,
        specs={"battery_kwh_net": SpecValue(value=49, unit="kWh")},
        retrieved_at=date(2026, 11, 15),
        confidence="medium",
    )
    res = _match([rec], rows)
    assert _placed_by(res, "kilowatt-openev") == set()


def test_f1c_agreeing_sources_outvote_one_priority_value() -> None:
    """The EX30 shape: one RDW year-group value (475) against OpenEV 344 and TGK 342."""
    facts = [
        _mf_src("rdw", 475, "coarse", 2024),
        _mf_src("openev", 344, "o", 2023),
        _mf_src("rdw-tgk", 342, "t", 2023),
    ]
    mg = merge_facts(facts, WLTP_POLICY)
    assert mg.value == 342 and mg.rule == "agreement"  # rdw-tgk ranks above openev
    assert [c.source_id for c in mg.conflicts] == ["rdw"]
    assert "outvote" in (mg.note() or "")
    off = FieldPolicy(order=WLTP_POLICY.order, mode="priority", tol_pct=2, agreement_wins=False)
    assert merge_facts(facts, off).value == 475


def test_f1c_one_other_source_does_not_outvote() -> None:
    facts = [_mf_src("rdw", 475, "coarse", 2024), _mf_src("openev", 344, "o", 2023)]
    assert merge_facts(facts, WLTP_POLICY).value == 475


def test_f1c_seed_manual_never_outvotes() -> None:
    facts = [
        _mf_src("rdw", 475, "coarse", 2024),
        _mf_src("openev", 344, "o", 2023),
        _mf_src("seed-manual", 344, "s", 2023),
    ]
    assert merge_facts(facts, WLTP_POLICY).value == 475


def test_policy_keys_parse() -> None:
    p = parse_policies(
        {
            "fields": {
                "dc_peak_kw": {"merge": "priority", "needs_backing": ["kilowatt-openev"]},
                "x": {"agreement_wins": False},
            }
        }  # fmt: skip
    )
    assert p.for_field("dc_peak_kw").needs_backing == ("kilowatt-openev",)
    assert p.for_field("dc_peak_kw").agreement_wins is True
    assert p.for_field("x").agreement_wins is False


def test_f6_followers_of_a_conflicting_vote_add_no_independence() -> None:
    facts = [_mf("openev", 400, "o", 2021), _mf("rdw-tgk", 340, "a", 2020)]
    facts.append(_mf("rdw-tgk", 400, "b", 2022))
    mg = merge_facts(facts)
    assert mg.independent_agreeing == 1
    assert "rdw-tgk:b:wltp_range_km" in mg.fact_ids  # still backs the value as a fact


def test_f8_generic_words_are_no_evidence_on_their_own() -> None:
    std = _distinct_tokens("Model S Standard Range", set())
    raven = _distinct_tokens("Raven Long Range", set())
    assert std & raven == set()  # "range" no longer shared; phrases are distinct tokens
    assert "standardrange" in std and "longrange" in raven
    assert name_score({"long", "plus"}, {"long", "plus", "awd"}) == 0
    assert name_score({"long", "awd"}, {"long", "awd"}) == 2  # with a distinctive word
    assert name_score({"plus"}, {"plus"}, numeric=2) == 1  # with numeric evidence


def test_f8_standard_range_epa_does_not_land_on_long_range() -> None:
    rows = [_v("long-range", "Raven Long Range", 300, 600), _v("plaid", "Plaid", 750, 600)]
    res = _match([_fe("EX30 Standard Range", 458.7)], rows)
    assert _placed_by(res, "fueleconomy") == set()


def _energy(nedc_km: float, nedc_wh: float, wltp_km: float, wltp_wh: float) -> list[dict]:
    return [
        {
            "codeenergiebron": "E",
            "volgnummerrevisieuitvoering": "1",
            "elektrischeactieradiusnedc": str(nedc_km),
            "elekverbruikgecombineerdnedc": str(nedc_wh),
            "actieradiusvolledigelekwltpogr": str(wltp_km),
            "verbruikvolledigelekwltpogr": str(wltp_wh),
        }
    ]


def test_f4_nedc_column_holding_the_wltp_figure_is_dropped() -> None:
    """Kona 64 kWh: TGK "NEDC 484 km" is the WLTP figure (real NEDC about 546 km)."""
    stats = Stats()
    out = version_values(_energy(484, 147, 484, 147), [], stats, "kona")
    assert out is not None
    vals = {f.value: v for f, v in out[0].items()}
    assert vals["wltp_range_km"] == 484
    assert "nedc_range_km" not in vals and "nedc_consumption_kwh_100km" not in vals
    assert stats.nedc_equals_wltp == {"nedc_range_km": 1, "nedc_consumption_kwh_100km": 1}
    within = version_values(_energy(485, 150, 484, 147), [], Stats(), "kona+1")
    assert within is not None and "nedc_range_km" not in {f.value for f in within[0]}


def test_f4_real_nedc_is_kept() -> None:
    out = version_values(_energy(546, 143, 484, 147), [], Stats(), "kona real")
    assert out is not None
    vals = {f.value: v for f, v in out[0].items()}
    assert vals["nedc_range_km"] == 546 and vals["nedc_consumption_kwh_100km"] == 14.3


def _mf_src(source: str, value: float, key: str, year: int, fname: str = "wltp_range_km"):
    unit = {"wltp_range_km": "km", "dc_peak_kw": "kW"}.get(fname, "kWh")
    lic = {"seed-manual": "CC-BY-4.0", "rdw": "CC0-1.0", "kilowatt-openev": "CC-BY-4.0"}
    fact = Fact(
        id=f"{source}:{key}:{fname}",
        subject_type="variant",
        subject_id="x-gen1-base",
        field=fname,
        value=value,
        unit=unit,
        source={
            "id": source,
            "name": source,
            "licence": lic.get(source, _LIC.get(source, "CC0-1.0")),
        },
        retrieved_at=date(2026, 11, 15),
        confidence="medium",
    )
    return MatchedFact(fact, source, priority_of(source), year)


POLICIES = Policies(
    {
        "wltp_range_km": WLTP_POLICY,
        "battery_kwh_net": FieldPolicy(order=("openev",), mode="median", tol_pct=2),
        "dc_peak_kw": FieldPolicy(
            order=("openev", "kilowatt-openev"),
            mode="priority",
            tol_pct=5,
            needs_backing=("kilowatt-openev",),
        ),  # fmt: skip
    }
)


def _merged(facts):
    from ev_pipeline.merge.merge import merge_variant_facts

    return {"x-gen1-base": merge_variant_facts(facts, POLICIES)}, {"x-gen1-base": facts}


def test_f7_impossible_wltp_goes_to_review_and_the_other_value_stays() -> None:
    """Megane 40 kWh shape: 467 km (the 60 kWh car's WLTP, one source) on 40 kWh (two)."""
    facts = [
        _mf_src("rdw", 467, "uitv", 2022),
        _mf_src("openev", 40, "o", 2022, "battery_kwh_net"),
        _mf_src("kilowatt-openev", 40, "k", 2022, "battery_kwh_net"),
    ]
    merged, by_v = _merged(facts)
    rows = guard_impossible(merged, by_v, POLICIES)
    mv = merged["x-gen1-base"]
    assert "wltp_range_km" not in mv and mv["battery_kwh_net"].value == 40
    assert [(r["field"], r["value"]) for r in rows] == [("wltp_range_km", 467)]
    assert rows[0]["tolerance"].startswith("impossible")


def test_f7_remaining_facts_are_merged_again() -> None:
    facts = [
        _mf_src("rdw", 467, "uitv", 2022),
        _mf_src("openev", 300, "o", 2022),
        _mf_src("openev", 40, "o", 2022, "battery_kwh_net"),
        _mf_src("kilowatt-openev", 40, "k", 2022, "battery_kwh_net"),
    ]
    merged, by_v = _merged(facts)
    guard_impossible(merged, by_v, POLICIES)
    assert merged["x-gen1-base"]["wltp_range_km"].value == 300


def test_f7_equal_support_takes_both_halves_out() -> None:
    facts = [_mf_src("rdw", 467, "u", 2022), _mf_src("openev", 40, "o", 2022, "battery_kwh_net")]
    merged, by_v = _merged(facts)
    rows = guard_impossible(merged, by_v, POLICIES)
    assert merged["x-gen1-base"] == {} and len(rows) == 2


def test_f7_usable_above_gross_goes_to_review() -> None:
    facts = [
        _mf_src("kilowatt-openev", 80, "k", 2022, "battery_kwh_net"),
        _mf_src("openev", 77.4, "o", 2022, "battery_kwh_gross"),
        _mf_src("seed-manual", 77.4, "s", 2022, "battery_kwh_gross"),
    ]
    merged, by_v = _merged(facts)
    # gross has 1 independent source (seed never counts), net 1: equal, both out.
    rows = guard_impossible(merged, by_v, POLICIES)
    assert {r["field"] for r in rows} == {"battery_kwh_net", "battery_kwh_gross"}


def test_f9_kilowatt_dc_peak_alone_is_withheld() -> None:
    """Zoe Ph1 R110: KilowattApp's 150 kW (the car has no DC socket) is the only value."""
    facts = [
        _mf_src("kilowatt-openev", 150, "k1", 2018, "dc_peak_kw"),
        _mf_src("kilowatt-openev", 46, "k2", 2019, "dc_peak_kw"),
    ]
    merged, by_v = _merged(facts)
    rows = guard_needs_backing(merged, by_v, POLICIES)
    assert "dc_peak_kw" not in merged["x-gen1-base"]
    assert sorted(r["value"] for r in rows) == [46, 150]
    assert rows[0]["tolerance"] == "needs backing: only kilowatt-openev"


def test_f9_backed_kilowatt_dc_peak_stays() -> None:
    facts = [
        _mf_src("kilowatt-openev", 150, "k1", 2022, "dc_peak_kw"),
        _mf_src("openev", 150, "o", 2022, "dc_peak_kw"),
    ]
    merged, by_v = _merged(facts)
    assert guard_needs_backing(merged, by_v, POLICIES) == []
    assert merged["x-gen1-base"]["dc_peak_kw"].value == 150


# --- L1 / L2 / L5 ----------------------------------------------------------------------------

FIX = Path(__file__).parent / "fixtures" / "release"
NOW = datetime(2026, 11, 15, 1, 0, tzinfo=UTC)


@pytest.fixture
def data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    d = tmp_path / "data"
    (d / "seed").mkdir(parents=True)
    shutil.copytree(FIX / "staging", d / "staging")
    shutil.copytree(FIX / "taxonomy", d / "taxonomy")
    for n in ("models", "variants", "platforms", "battery_packs", "variant_links"):
        shutil.copy(FIX / f"{n}.yaml", d / "seed" / f"{n}.yaml")
    for n in ("sources", "field_sources"):
        shutil.copy(FIX / f"{n}.yaml", d / f"{n}.yaml")
    monkeypatch.setenv("EV_DATA_DIR", str(d))
    monkeypatch.delenv("EV_RUNS_DIR", raising=False)
    return d


def _two(d: Path) -> None:
    assert build.release_cmd(False, data_dir=d, now=NOW) == 0
    assert build.release_cmd(False, data_dir=d, now=NOW) == 0


def test_l1_rollback_refuses_unknown_qa_status(data_dir: Path) -> None:
    _two(data_dir)
    (data_dir / "releases" / "1" / "qa.json").write_text("{}")
    with pytest.raises(ReleaseOpError, match="'unknown'"):
        rollback(data_dir, 1)
    assert (data_dir / "releases" / "latest").read_text() == "2\n"


def test_l1_rollback_rechecks_the_licence_gate(data_dir: Path) -> None:
    _two(data_dir)
    reg = data_dir / "sources.yaml"
    text = reg.read_text()
    reg.write_text(text.replace("status: active", "status: blocked", 1))  # openev blocked now
    with pytest.raises(ReleaseOpError, match="licence"):
        rollback(data_dir, 1)
    reg.write_text(text)
    assert rollback(data_dir, 1)["recheck"] == "pass"


def test_l2_write_latest_fsyncs_file_and_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[int] = []
    real = os.fsync
    monkeypatch.setattr(build.os, "fsync", lambda fd: (calls.append(fd), real(fd))[1])
    build.write_latest(tmp_path, 7)
    assert (tmp_path / "latest").read_text() == "7\n" and len(calls) >= 2


def test_l5_sources_json_lists_charging_sources(tmp_path: Path) -> None:
    charging = {
        "sources": [{"id": "bnetza-ladesaeulenregister"}],
        "source_aliases": {"bnetza-ladesaeulenregister": "bnetza"},
        "stats": [{"source_id": "dft-ev-charging-infrastructure"}],
    }
    charging["source_aliases"]["dft-ev-charging-infrastructure"] = "dft-charging"
    reg = [{"id": "bnetza", "name": "BNetzA", "licence": "CC-BY-4.0", "status": "active"}]
    doc = release_sources_doc(tmp_path, {"sources": []}, reg, charging)
    assert {"bnetza", "dft-charging"} <= set(doc["sources"])
    assert doc["sources"]["bnetza"]["in_charging_stats"] is True
    assert doc["sources"]["bnetza"]["in_catalogue"] is False


def test_l5_taxonomy_labels_do_not_name_eafo() -> None:
    root = Path(__file__).resolve().parents[2] / "data" / "taxonomy"
    import yaml

    for fname, table in (("charging_definitions.yaml", None), ("power_bands.yaml", None)):
        doc = yaml.safe_load((root / fname).read_text(encoding="utf-8"))
        rows = next(v for v in doc.values() if isinstance(v, list)) if table is None else doc
        for row in rows:
            if row.get("source_id") != "eafo":
                continue
            text = json.dumps({k: row.get(k) for k in ("label", "technical", "short", "explainer")})
            assert "EAFO" not in text and "Alternative Fuels Observatory" not in text, row["id"]


def test_f4_no_nedc_on_a_2018_858_approval_after_2020() -> None:
    from ev_pipeline.schema_models import FactField
    from ev_pipeline.sources.rdw_tgk.adapter import drop_nedc_on_wltp_era_approval

    vals = {FactField.nedc_range_km: 384.0, FactField.wltp_range_km: 400.0}
    assert drop_nedc_on_wltp_era_approval("e9*2018/858*11054*01", 2021, vals) == ["nedc_range_km"]
    assert vals == {FactField.wltp_range_km: 400.0}
    old = {FactField.nedc_range_km: 300.0}
    assert drop_nedc_on_wltp_era_approval("e2*2007/46*0251*10", 2021, old) == []
    assert drop_nedc_on_wltp_era_approval("e9*2018/858*1*01", 2020, old) == []
    assert old == {FactField.nedc_range_km: 300.0}
