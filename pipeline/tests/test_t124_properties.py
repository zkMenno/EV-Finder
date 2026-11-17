"""T-124: property tests for the pipeline (Hypothesis). Generated inputs try to break rules
we think always hold: idempotency, round-trips, invariants, equivalence. Every failing
example Hypothesis finds is also pinned as a plain regression test at the bottom."""

from __future__ import annotations

import json
import math
import re
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from ev_pipeline.derive.metrics import (
    BODY_RATIOS,
    WALL_PER_BATTERY_WLTP,
    LadderInput,
    RealObservation,
    ac_km_per_h,
    consumption_estimate,
    km_in_minutes,
    net_from_gross,
    real_range,
)
from ev_pipeline.derive.shortlist import band_for
from ev_pipeline.match.matcher import _contains_run, normalise_unit, priority_of
from ev_pipeline.match.normalise import key, prefix_keys, slug, strip_accents
from ev_pipeline.merge.merge import merge_facts
from ev_pipeline.records import SpecValue

ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")  # packages/schema Id
# Model names as sources write them: Latin letters with accents, digits, punctuation.
NAME_CHARS = st.sampled_from(
    list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    + list("éèëêáàäâíïóöôúüçñøåÉÖÜ")
    + list(" -._/()&'")
)
names = st.text(NAME_CHARS, min_size=0, max_size=30)
pos = st.floats(min_value=0.1, max_value=1e4, allow_nan=False, allow_infinity=False)


# --- name normalisation ----------------------------------------------------------------


@given(names)
def test_key_is_idempotent_and_ignores_case_accents_punctuation(s: str) -> None:
    k = key(s)
    assert key(k) == k
    assert key(s.upper()) == key(s.lower()) == k
    assert key(strip_accents(s)) == k
    assert key(re.sub(r"[ \-._/()&']+", " ", s)) == k
    assert re.fullmatch(r"[a-z0-9]*", k)


@given(names)
def test_slug_is_a_schema_id_or_empty(s: str) -> None:
    sl = slug(s)
    assert sl == "" or ID.match(sl)
    assert slug(sl) == sl and key(sl) == key(s)


@given(st.lists(st.text("abc12", min_size=1, max_size=3), max_size=6))
def test_prefix_keys_equal_a_naive_scan(toks: list[str]) -> None:
    """Equivalence: the matcher's prefix-key index lookup = scanning every token prefix."""
    naive = ["".join(toks[:k]) for k in range(1, len(toks) + 1)]
    assert prefix_keys(toks) == naive[::-1]  # longest first


@given(st.lists(st.sampled_from(["e", "4", "gt", "plus"]), max_size=7),
       st.lists(st.sampled_from(["e", "4", "gt", "plus"]), min_size=1, max_size=3))  # fmt: skip
def test_contains_run_equals_string_search(toks: list[str], run: list[str]) -> None:
    """Equivalence: the token-run test = a naive substring search on space-joined tokens."""
    naive = f" {' '.join(run)} " in f" {' '.join(toks)} "
    assert _contains_run(toks, run) == naive


@pytest.mark.xfail(
    strict=True,
    reason="WS3 ask (T-068 handoff): normalise.key drops '+', so 'P7+' == 'P7'. Remove this "
    "marker when '+' is tokenised as 'plus'.",
)
@given(st.text("abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=8))
def test_plus_suffix_makes_a_different_key(s: str) -> None:
    assert key(s + "+") != key(s)


# --- unit round-trips ------------------------------------------------------------------


@given(st.floats(min_value=50, max_value=600))
def test_wh_per_km_round_trips_to_kwh_per_100km(wh_km: float) -> None:
    v, unit, problem = normalise_unit("consumption_kwh_100km", SpecValue(value=wh_km, unit="Wh/km"))
    assert problem == "" and unit == "kWh/100km"
    assert math.isclose(v * 10, wh_km, rel_tol=1e-12)


@given(st.sampled_from(["wltp_range_km", "epa_range_km", "real_range_km"]),
       st.sampled_from(["mi", "miles", "MI"]), st.floats(min_value=10, max_value=1000))  # fmt: skip
def test_miles_round_trip_to_km(fname: str, unit: str, miles: float) -> None:
    v, canon, problem = normalise_unit(fname, SpecValue(value=miles, unit=unit))
    assert problem == "" and canon == "km"
    assert math.isclose(v / 1.609344, miles, rel_tol=1e-12)


@given(st.floats(min_value=1, max_value=400), st.floats(min_value=8, max_value=40))
def test_km_per_20_min_is_a_third_of_km_per_hour(kw: float, cons: float) -> None:
    """Without the battery cap, km in 20 min x 3 = km in 60 min = the km/h rate."""
    per20 = km_in_minutes(kw, 20, cons)
    per60 = km_in_minutes(kw, 60, cons)
    assert math.isclose(per20 * 3, per60, rel_tol=1e-12)
    assert math.isclose(per60, ac_km_per_h(kw, cons), rel_tol=1e-12)


@given(st.floats(min_value=1, max_value=400), st.floats(min_value=8, max_value=40),
       st.floats(min_value=10, max_value=150), st.integers(min_value=1, max_value=180))  # fmt: skip
def test_battery_cap_never_adds_km(kw: float, cons: float, kwh: float, minutes: int) -> None:
    capped = km_in_minutes(kw, minutes, cons, kwh)
    assert capped <= km_in_minutes(kw, minutes, cons) + 1e-9
    assert capped <= kwh * 0.7 / cons * 100 + 1e-9  # never more than the 10->80 % window


@given(st.floats(min_value=10, max_value=150), st.floats(min_value=50, max_value=1000))
def test_consumption_estimate_round_trips(kwh: float, km: float) -> None:
    c = consumption_estimate(kwh, km)
    # T-071: the estimate is wall basis; dividing out the charging-loss factor gives net kWh.
    assert math.isclose(c * km / 100 / WALL_PER_BATTERY_WLTP, kwh, rel_tol=1e-12)


# --- invariants ------------------------------------------------------------------------


@given(st.floats(min_value=10, max_value=200))
def test_net_never_above_gross(gross: float) -> None:
    assert 0 < net_from_gross(gross) <= gross


@given(
    st.sampled_from(sorted(BODY_RATIOS)),
    st.sampled_from([None, "fwd", "rwd", "awd"]),
    st.floats(min_value=100, max_value=1000),
    st.floats(min_value=20, max_value=120),
)
def test_body_ratio_real_range_between_zero_and_wltp(
    body: str, drive: str | None, wltp: float, kwh: float
) -> None:
    li = LadderInput("v", "g", "make", body, drive, kwh, wltp, ["openev"], ["f1"])
    r = real_range(li, [li], {}, {})
    assert r is not None and 0 < r.km <= wltp * 1.1
    assert r.source_ids == ["openev"]  # the estimate keeps its inputs' source


@st.composite
def generation(draw: st.DrawFn) -> tuple[list[LadderInput], dict[str, RealObservation]]:
    """A generation of 2-5 variants with plausible numbers: efficiency within a band, real
    range observed at 60-100 % of WLTP."""
    n = draw(st.integers(min_value=2, max_value=5))
    eff = draw(st.floats(min_value=5.0, max_value=7.5))  # WLTP km per kWh, shared
    out, obs = [], {}
    for i in range(n):
        kwh = draw(st.floats(min_value=40, max_value=100))
        wltp = kwh * eff * draw(st.floats(min_value=0.95, max_value=1.05))
        li = LadderInput(f"v{i}", "g", "make", "suv", "rwd", kwh, wltp, ["openev"], [f"f{i}"])
        out.append(li)
        if draw(st.booleans()):
            share = draw(st.floats(min_value=0.6, max_value=1.0))
            obs[li.variant_id] = RealObservation(wltp * share, "exact-test", ["t"], ["x"], "high")
    return out, obs


@given(generation())
def test_any_rung_real_range_positive_and_within_wltp(
    gen: tuple[list[LadderInput], dict[str, RealObservation]],
) -> None:
    inputs, obs = gen
    for li in inputs:
        r = real_range(li, inputs, obs)
        assert r is not None and r.km > 0
        assert r.km <= li.wltp_km * 1.1, (r.rung, r.note)
        assert r.source_ids  # every published number keeps a source


@given(st.floats(min_value=0, max_value=100), st.floats(min_value=0, max_value=100),
       st.floats(min_value=1, max_value=100), st.floats(min_value=0, max_value=100))  # fmt: skip
def test_band_matches_score_and_is_monotonic(a: float, b: float, cons: float, gap: float) -> None:
    bands = {"default": {"consider": cons, "shortlist": min(cons + gap, 100)}}
    order = {"fallback": 0, "consider": 1, "shortlist": 2}
    lo, hi = sorted((a, b))
    assert order[band_for(lo, bands, None)] <= order[band_for(hi, bands, None)]
    got = band_for(hi, bands, None)
    if got == "shortlist":
        assert hi >= bands["default"]["shortlist"]
    elif got == "consider":
        assert cons <= hi < bands["default"]["shortlist"]
    else:
        assert hi < cons


def _mf(source: str, value: float, i: int, year: int | None, retrieved: date):  # noqa: ANN202
    from ev_pipeline.match.matcher import MatchedFact
    from ev_pipeline.schema_models import Fact

    fact = Fact(
        id=f"{source}:r{i}:battery_kwh_net", subject_type="variant", subject_id="x-gen1-base",
        field="battery_kwh_net", value=value, unit="kWh",
        source={"id": source, "name": source, "licence": "CC-BY-4.0"},
        retrieved_at=retrieved, confidence="medium",
    )  # fmt: skip
    return MatchedFact(fact, source, priority_of(source), year)


facts_lists = st.lists(
    st.tuples(
        st.sampled_from(["openev", "kilowatt-openev", "rdw", "eea"]),
        st.floats(min_value=20, max_value=120).map(lambda v: round(v, 1)),
        st.sampled_from([None, 2021, 2023]),
        st.sampled_from([date(2026, 11, 1), date(2026, 11, 14)]),
    ),
    min_size=1,
    max_size=6,
)


@given(facts_lists, st.randoms(use_true_random=False))
def test_merge_is_order_independent_and_picks_a_real_value(facts, rnd) -> None:  # noqa: ANN001
    mfs = [_mf(s, v, i, y, d) for i, (s, v, y, d) in enumerate(facts)]
    a = merge_facts(mfs)
    shuffled = list(mfs)
    rnd.shuffle(shuffled)
    b = merge_facts(shuffled)
    assert (a.value, a.winner.fact.id, sorted(a.source_ids)) == (
        b.value, b.winner.fact.id, sorted(b.source_ids),
    )  # fmt: skip
    assert a.value in {m.fact.value for m in mfs}  # never an invented number
    assert a.source_ids and set(a.source_ids) <= {m.source_id for m in mfs}
    assert merge_facts(mfs).value == a.value  # idempotent


# --- idempotency of a whole release ----------------------------------------------------


FIX = Path(__file__).parent / "fixtures" / "release"
NOW = datetime(2026, 11, 15, 1, tzinfo=UTC)


def _data(root: Path) -> Path:
    d = root / "data"
    (d / "seed").mkdir(parents=True)
    shutil.copytree(FIX / "staging", d / "staging")
    shutil.copytree(FIX / "taxonomy", d / "taxonomy")
    for n in ("models", "variants", "platforms", "battery_packs", "variant_links"):
        shutil.copy(FIX / f"{n}.yaml", d / "seed" / f"{n}.yaml")
    for n in ("sources", "field_sources"):
        shutil.copy(FIX / f"{n}.yaml", d / f"{n}.yaml")
    return d


def test_release_twice_on_same_staging_is_byte_equal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from ev_pipeline.release.build import release_cmd

    monkeypatch.delenv("EV_RUNS_DIR", raising=False)
    outs = []
    for name in ("a", "b"):
        d = _data(tmp_path / name)
        monkeypatch.setenv("EV_DATA_DIR", str(d))
        assert release_cmd(False, data_dir=d, now=NOW) == 0
        outs.append(d / "releases" / "1")
    for f in ("catalogue.json", "qa.json", "open/variants.csv", "open/variants.json"):
        a, b = (o / f for o in outs)
        if f.endswith(".json") and f != "catalogue.json":
            ja, jb = json.loads(a.read_text()), json.loads(b.read_text())
            assert _strip_paths(ja, str(outs[0].parents[2])) == _strip_paths(
                jb, str(outs[1].parents[2])
            )
        else:
            assert a.read_bytes() == b.read_bytes(), f


def _strip_paths(o: object, root: str) -> object:
    if isinstance(o, dict):
        return {k: _strip_paths(v, root) for k, v in o.items()}
    if isinstance(o, list):
        return [_strip_paths(v, root) for v in o]
    return o.replace(root, "<root>") if isinstance(o, str) else o


def test_normalise_twice_is_byte_equal(tmp_path: Path) -> None:
    """Idempotent normalise: the openev adapter run twice on its fixture gives the same file."""
    from ev_pipeline.cli import main

    outs = []
    for name in ("a", "b"):
        import os

        os.environ["EV_DATA_DIR"] = str(tmp_path / name)
        try:
            assert main(["normalise", "openev", "--from-fixtures"]) == 0
        finally:
            os.environ.pop("EV_DATA_DIR")
        outs.append((tmp_path / name / "staging" / "openev.records.jsonl").read_bytes())
    assert outs[0] == outs[1] and outs[0]


# --- invariants on the committed release (real rows, no network) ------------------------


def test_committed_release_rows_keep_the_invariants() -> None:
    from ev_pipeline.qa.checks import row_values
    from ev_pipeline.release.build import REPO_ROOT

    rel = REPO_ROOT / "data" / "releases"
    n = (rel / "latest").read_text().strip()
    cat = json.loads((rel / n / "catalogue.json").read_text(encoding="utf-8"))
    src = {s["id"]: s for s in cat["sources"]}
    bad = []
    for r in cat["rows"]:
        prov = r.get("provenance") or {}
        for k, _v in row_values(r):
            p = prov.get(k.split(".")[0]) or prov.get(k) or {}
            if not p.get("source_ids"):
                bad.append(f"{r['variant_id']} {k}: no source")
                continue
            if any(s not in src or not src[s].get("licence") for s in p["source_ids"]):
                bad.append(f"{r['variant_id']} {k}: source without licence")
            if "model-estimate" in p["source_ids"] and not p.get("estimate"):
                bad.append(f"{r['variant_id']} {k}: model estimate not labelled")
        w, rr = r.get("wltp_range_km"), r.get("real_range_km")
        if rr is not None and (not rr > 0 or (w and rr > w * 1.1)):
            bad.append(f"{r['variant_id']}: real range {rr} vs WLTP {w}")
    assert bad == [], bad[:10]


# --- regressions pinned from Hypothesis finds ------------------------------------------


def test_regression_same_pack_sibling_scales_by_wltp_not_battery() -> None:
    """Hypothesis (nightly, 2026-11-17): same 40 kWh pack, WLTP 209.8 vs 190.6 km (wheels or
    trim); scaling by battery gave v1 a real range of 209.8 km, above its own WLTP x 1.1."""
    v0 = LadderInput("v0", "g", "make", "suv", "rwd", 40.0, 209.765625, ["openev"], ["f0"])
    v1 = LadderInput("v1", "g", "make", "suv", "rwd", 40.0, 190.625, ["openev"], ["f1"])
    obs = {"v0": RealObservation(209.765625, "exact-test", ["t"], ["x"], "high")}
    r = real_range(v1, [v0, v1], obs)
    assert r is not None and r.rung == "sibling-variant"
    assert math.isclose(r.km, 190.625) and r.note.endswith("by WLTP ratio")
    no_wltp = LadderInput("v2", "g", "make", "suv", "rwd", 60.0, None)
    r2 = real_range(no_wltp, [v0, no_wltp], obs)
    assert r2 is not None and r2.note.endswith("by battery ratio")
    assert math.isclose(r2.km, 209.765625 * 60 / 40)
