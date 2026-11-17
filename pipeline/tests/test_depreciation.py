"""T-113 (Decision 064): depreciation fit on our own samples. Fixtures only, no network."""

from __future__ import annotations

import json
import math
from datetime import date
from pathlib import Path
from typing import Any

import pytest
import yaml

from ev_pipeline.derive import depreciation as dep
from ev_pipeline.derive import used_price as up

AS_OF = date(2026, 11, 17)
GEN = "2026-11-17T01:00:00Z"
A, K = 0.9, 0.12  # the "true" curve the synthetic samples follow
PUBLISHED = up.load_params()["curves"]["default"]
REGISTRY = {
    "sources": [
        {"id": "test-market", "name": "t", "licence": "none", "status": "active",
         "use": "aggregates-only", "decision": "060", "site_hosts": ["www.market.example"]}
    ]
}  # fmt: skip


def params(**over: Any) -> dict[str, Any]:
    p = up.load_params()
    p.pop("fitted", None)
    p.update(over)
    return p


def _rows(n_gens: int, segment: str = "C") -> list[dict[str, Any]]:
    return [
        {"variant_id": f"g{i}-a", "generation_id": f"g{i}", "segment": segment,
         "year_start": 2016, "year_end": 2025}
        for i in range(n_gens)
    ]  # fmt: skip


def _prices(rows: list[dict[str, Any]], amount: float = 40000.0) -> tuple[list, list]:
    facts, years = [], []
    for r in rows:
        for y in range(2016, 2026):
            facts.append({"field": "price_new", "subject_type": "variant",
                          "subject_id": r["variant_id"], "country": "NL", "value": amount,
                          "unit": "EUR", "source": {"id": "rdw"}})  # fmt: skip
            years.append(y)
    return facts, years


def _samples(rows: list[dict[str, Any]], noise: float = 0.0) -> list[dict[str, Any]]:
    out = []
    for i, r in enumerate(rows):
        for y in (2018, 2020, 2022, 2024):
            age = up.age_at(y, AS_OF, 7)
            wobble = 1 + noise * (1 if (i + y) % 2 else -1)
            out.append({"file": f"{r['generation_id']}.yaml", "country": "NL",
                        "generation_id": r["generation_id"], "variant_id": None,
                        "observed_at": "2026-11-15", "currency": "EUR",
                        "source": {"name": "t", "url": "https://www.market.example/"},
                        "source_id": "test-market", "build_year": y, "n": 10,
                        "p25": None, "median": 40000 * A * math.exp(-K * age) * wobble,
                        "p75": None})  # fmt: skip
    return out


def _points(n_gens: int = 10, noise: float = 0.0, segment: str = "C") -> list[dep.Point]:
    rows = _rows(n_gens, segment)
    facts, years = _prices(rows)
    return dep.fit_points(
        _samples(rows, noise), rows, up.list_prices(facts, years), AS_OF, params()
    )


def test_points_pair_samples_with_list_prices() -> None:
    pts = _points(3)
    assert len(pts) == 12
    pt = pts[0]
    assert pt.list_price == 40000
    assert pt.share == pytest.approx(A * math.exp(-K * pt.age), rel=1e-3)  # age rounded


def test_points_skip_missing_list_price_or_other_currency() -> None:
    rows = _rows(2)
    facts, years = _prices(rows[:1])  # g1 has no list price
    samples = _samples(rows)
    samples[0]["currency"] = "GBP"  # g0 2018: list price is EUR
    pts = dep.fit_points(samples, rows, up.list_prices(facts, years), AS_OF, params())
    assert {pt.generation_id for pt in pts} == {"g0"} and len(pts) == 3


def test_fit_recovers_the_curve() -> None:
    ak = dep.fit_exponential(_points(10))
    assert ak is not None
    assert ak[0] == pytest.approx(A, rel=1e-3) and ak[1] == pytest.approx(K, rel=1e-3)


def test_fitted_curve_table_and_quality() -> None:
    curves = dep.fit_curves(_points(10, noise=0.05), params())
    c = curves["default"]
    assert c is not None and set(c["points"]) == set(range(13))
    assert all(c["points"][y] >= c["points"][y + 1] for y in range(12))  # never rises
    assert c["quality"]["points"] == 40 and c["quality"]["generations"] == 10
    assert c["extrapolated_from_age"] == math.floor(c["quality"]["age_range"][1]) + 1
    assert up.kept_share(3, c) == pytest.approx(c["points"][3])


def test_too_few_points_keep_the_published_curve() -> None:
    curves = dep.fit_curves(_points(3), params())  # 12 points, 3 generations
    assert curves["default"] is None and "published curve stays" in curves["note"]


def test_segment_curve_only_with_enough_of_its_own() -> None:
    pts = _points(10, segment="C") + [
        dep.Point(**{**pt.to_dict(), "generation_id": f"s-{pt.generation_id}", "segment": "S"})
        for pt in _points(2)
    ]
    curves = dep.fit_curves(pts, params())
    assert set(curves["by_segment"]) == {"C"}  # S has 8 points, 2 generations


def test_holdout_reports_fitted_and_published_with_worst_cases() -> None:
    ho = dep.holdout_backtest(_points(10, noise=0.05), params())
    f, pub = ho["fitted"], ho["published"]
    assert f["rows_compared"] == 40 and pub["rows_compared"] == 40
    assert f["median_abs_error"] == pytest.approx(0.05, abs=0.01)  # the noise, no more
    assert f["in_band"] == 1.0  # 5 % noise sits inside the shown +-12 % band
    assert 0 <= pub["in_band"] <= 1
    assert f["curves_used"] == {"fitted:C": 40}  # each fold: 9 C generations, own curve
    assert len(f["worst"]) == 5 and abs(f["worst"][0]["error"]) >= abs(f["worst"][-1]["error"])
    assert all(r["median"] % 100 == 0 and r["p25"] % 100 == 0 for r in f["worst"])  # rounded


def test_holdout_uses_the_curve_choose_curve_gives_each_segment() -> None:
    pts = _points(10, segment="C") + [
        dep.Point(**{**pt.to_dict(), "generation_id": f"s-{pt.generation_id}", "segment": "S"})
        for pt in _points(2)
    ]
    ho = dep.holdout_backtest(pts, params())
    # C keeps its own curve in every fold; S (2 generations) gets the all-cars curve
    assert ho["fitted"]["curves_used"] == {"fitted": 8, "fitted:C": 40}


def test_holdout_thin_fold_falls_back_to_the_published_curve() -> None:
    # 8 generations: each fold has 7 (< min_generations 8), so a visitor gets the published curve
    ho = dep.holdout_backtest(_points(8), params())
    assert ho["fitted"]["curves_used"] == {"published": 32}
    assert ho["fitted"]["median_abs_error"] == ho["published"]["median_abs_error"]


def test_holdout_shows_exactly_what_the_release_shows(tmp_path: Path) -> None:
    """The hold-out's shown band for g0 == the band build_used_prices publishes for g0 when the
    fitted curve is the fold's (fit without g0)."""
    pts = _points(10, noise=0.05)
    p = params(fit={**dep.DEFAULT_FIT, "worst_listed": 99})  # list every row
    ho = dep.holdout_backtest(pts, p)
    fold = dep.fit_curves([pt for pt in pts if pt.generation_id != "g0"], p)
    fitted = {"samples_observed": ["NL"], "fitted_at": "2026-11-17", **fold}
    shown = _bands(_run(tmp_path, params(fitted=fitted)))
    rows = {r["build_year"]: r for r in ho["fitted"]["worst"] if r["subject"] == "g0"}
    assert set(rows) == {2018, 2020, 2022, 2024}
    for y, r in rows.items():
        assert (r["p25"], r["median"], r["p75"]) == (
            shown[y]["p25"], shown[y]["median"], shown[y]["p75"]
        )  # fmt: skip


# --- release-time use (used_price.build_used_prices) ---------------------------------------


def _run(tmp_path: Path, p: dict[str, Any], samples_doc: dict[str, Any] | None = None) -> Any:
    pf = tmp_path / "params.yaml"
    pf.write_text(yaml.safe_dump(p))
    (tmp_path / "sources.yaml").write_text(yaml.safe_dump(REGISTRY))
    if samples_doc:
        d = tmp_path / "manual" / "prices"
        d.mkdir(parents=True)
        (d / "s.yaml").write_text(yaml.safe_dump(samples_doc))
    rows = _rows(1)
    facts, years = _prices(rows)
    return up.build_used_prices(rows, facts, years, tmp_path, 2, GEN, pf)


def _bands(res: Any) -> dict[int, dict[str, Any]]:
    return {b["build_year"]: b for b in res.document["variants"][0]["bands"]["NL"]}


def test_published_curve_rows_carry_basis_source_and_date(tmp_path: Path) -> None:
    b = _bands(_run(tmp_path, params()))[2022]
    assert b["basis"] == "estimate" and b["method"] == "model" and b["curve"] == "published"
    assert b["source"]["url"].startswith("https://www.autohaus.de/")
    assert b["date"] == "2026-09-28"


def test_fitted_curve_is_used_when_params_have_one(tmp_path: Path) -> None:
    fitted = dep.fit_block(_points(10), params(), "2026-11-17", 1)
    fitted["by_segment"] = {}  # the all-cars curve
    res = _run(tmp_path, params(fitted=fitted))
    b = _bands(res)[2022]
    assert b["curve"] == "fitted" and b["date"] == "2026-11-17"
    assert b["kept_share"] == pytest.approx(
        up.kept_share(up.age_at(2022, AS_OF, 7), fitted["default"]), abs=1e-3
    )
    assert res.document["curves"]["fitted"] is True
    assert res.document["backtest"]["model_curve"] == "fitted"


def test_segment_curve_wins_for_its_segment(tmp_path: Path) -> None:
    fitted = dep.fit_block(_points(10), params(), "2026-11-17", 1)
    fitted["by_segment"] = {"C": {**fitted["default"], "points": {y: 0.5 for y in range(13)}}}
    b = _bands(_run(tmp_path, params(fitted=fitted)))[2022]
    assert b["curve"] == "fitted:C" and b["kept_share"] == 0.5


def test_estimate_never_replaces_a_real_band(tmp_path: Path) -> None:
    doc = {"country": "NL", "variant_id": "g0-a", "observed_at": "2026-11-15",
           "currency": "EUR", "source": {"name": "t", "url": "https://www.market.example/q"},
           "rows": [{"build_year": 2022, "n": 9, "p25": 1000, "median": 1234,
                     "p75": 1500}]}  # fmt: skip
    fitted = dep.fit_block(_points(10), params(), "2026-11-17", 1)
    res = _run(tmp_path, params(fitted=fitted), doc)
    bands = _bands(res)
    assert bands[2022]["basis"] == "band" and bands[2022]["median"] == 1234
    assert bands[2022]["date"] == "2026-11-15" and "curve" not in bands[2022]
    assert bands[2021]["basis"] == "estimate"


def test_fitted_rows_say_which_countries_the_curve_was_fitted_on(tmp_path: Path) -> None:
    fitted = dep.fit_block(_points(10), params(), "2026-11-17", 1)
    assert fitted["samples_observed"] == ["NL"]
    b = _bands(_run(tmp_path, params(fitted=fitted)))[2022]
    assert b["curve_fitted_on"] == ["NL"]
    (tmp_path / "pub").mkdir()
    pub = _bands(_run(tmp_path / "pub", params()))[2022]
    assert pub["curve"] == "published" and "curve_fitted_on" not in pub


def test_ages_below_the_fitted_range_are_low_confidence(tmp_path: Path) -> None:
    fitted = dep.fit_block(_points(10), params(), "2026-11-17", 1)
    lo = fitted["default"]["quality"]["age_range"][0]  # 2024 build: 1.4 years
    bands = _bands(_run(tmp_path, params(fitted=fitted)))
    assert bands[2025]["age_years"] < lo and bands[2025]["confidence"] == "low"
    assert bands[2022]["confidence"] == "medium"


def test_backtest_section_has_holdout(tmp_path: Path) -> None:
    res = _run(tmp_path, params())
    bt = res.document["backtest"]
    assert {"holdout", "fit_points", "model_curve", "worst"} <= set(bt)
    assert bt["holdout"]["fitted"]["rows_compared"] == 0  # one generation: nothing to hold out


# --- `ev used-price fit` -----------------------------------------------------------------


def test_fit_command_on_a_release_folder(tmp_path: Path) -> None:
    import pyarrow as pa
    import pyarrow.parquet as pq

    from ev_pipeline.commands.used_price import run_fit

    rows = _rows(10)
    facts, years = _prices(rows)
    rel = tmp_path / "releases" / "1"
    rel.mkdir(parents=True)
    (tmp_path / "releases" / "latest").write_text("1\n")
    (rel / "catalogue.json").write_text(json.dumps({"rows": rows}))
    pq.write_table(
        pa.Table.from_pylist([
            {"field": "price_new", "subject_type": "variant", "subject_id": f["subject_id"],
             "country": "NL", "value_num": f["value"], "unit": "EUR", "source_id": "rdw",
             "record_year": y}
            for f, y in zip(facts, years, strict=True)
        ]),
        rel / "facts.parquet",
    )  # fmt: skip
    d = tmp_path / "manual" / "prices"
    d.mkdir(parents=True)
    for s in _samples(rows):
        (d / f"{s['generation_id']}-{s['build_year']}.yaml").write_text(yaml.safe_dump({
            "country": "NL", "generation_id": s["generation_id"], "observed_at": "2026-11-15",
            "currency": "EUR", "source": s["source"],
            "rows": [{"build_year": s["build_year"], "n": 10,
                      "median": s["median"]}]}))  # fmt: skip
    (tmp_path / "sources.yaml").write_text(yaml.safe_dump(REGISTRY))
    pf = tmp_path / "p.yaml"
    pf.write_text(yaml.safe_dump(params()))
    res = run_fit(tmp_path, None, AS_OF, pf)
    assert res["release"] == 1 and res["sample_rows"] == 40 and not res["dropped_by_source_gate"]
    assert res["fitted"]["default"]["k"] == pytest.approx(K, abs=1e-3)
    # exact curve; what is left is the yearly table (linear between years) and rounding to 100
    assert res["holdout"]["fitted"]["median_abs_error"] == pytest.approx(0, abs=5e-3)
