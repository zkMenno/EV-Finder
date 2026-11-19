"""T-155: popularity back-test (qa.json `backtest_popularity`). SYNTHETIC rows and scores."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from ev_pipeline.backtest.popularity import (
    js_round1,
    model_scores,
    popularity_backtest,
    popularity_md,
    ranks,
    spearman,
    web_ranking,
)

CFG = {"registrations": 0.8, "owner_picks": 0.2}


def test_spearman_known_values() -> None:
    a = {"a": 4, "b": 3, "c": 2, "d": 1}
    assert spearman(a, a) == 1.0
    assert spearman(a, {"a": 1, "b": 2, "c": 3, "d": 4}) == -1.0
    # one swap in five: rho = 1 - 6*2/(5*24) = 0.9
    assert spearman(
        {"a": 5, "b": 4, "c": 3, "d": 2, "e": 1}, {"a": 5, "b": 4, "c": 2, "d": 3, "e": 1}
    ) == pytest.approx(0.9)
    assert spearman({"a": 1, "b": 2}, {"a": 1, "b": 2}) is None  # too few to say anything
    assert spearman({"a": 1, "b": 1, "c": 1}, {"a": 1, "b": 2, "c": 3}) is None  # no spread


def test_ties_share_their_average_rank() -> None:
    assert ranks({"a": 10, "b": 5, "c": 5, "d": 1}) == {"a": 1, "b": 2.5, "c": 2.5, "d": 4}


def test_model_scores_take_ranked_and_outside_models() -> None:
    doc = {
        "models": [{"model_id": "m1", "score_pct": 8.0}, {"model_id": "m2", "score_pct": "x"}],
        "seed_models_outside_top": [{"model_id": "m3", "score_pct": 0.1}],
    }
    assert model_scores(doc) == {"m1": 8.0, "m3": 0.1}


def test_model_scores_filter_ids_like_the_web() -> None:
    """T-161 (T-155 nit 5): popularity.mjs drops ids that fail ID_RE and non-finite scores."""
    doc = {
        "models": [
            {"model_id": "Bad Id", "score_pct": 5.0},
            {"model_id": "m-1", "score_pct": 2.0},
            {"model_id": "m-", "score_pct": 1.0},
            {"model_id": "nan", "score_pct": float("nan")},
            {"model_id": "inf", "score_pct": float("inf")},
            {"model_id": "neg", "score_pct": -1.0},
            {"model_id": "flag", "score_pct": True},
        ]
    }
    assert model_scores(doc) == {"m-1": 2.0}


def test_scores_round_half_up_like_javascript() -> None:
    # Python's round() goes to even (and 0.25 is exact): Math.round(2.5) / 10 = 0.3
    assert round(0.25, 1) == 0.2
    assert js_round1(0.25) == 0.3
    assert js_round1(12.35) == pytest.approx(12.4)
    assert js_round1(12.34) == pytest.approx(12.3)
    # a 50/50 blend that lands on x.x5 exactly: wr = wp = 1, share 0.5 of top, no pick → 25.0;
    # share 0.0005 → 0.025 → 0.0 (JS: Math.round(0.25) = 0); share 0.001 → 0.05 → 0.1
    rows = [_row("a-g1", "a", None), _row("b-g1", "b", None), _row("c-g1", "c", None)]
    out = web_ranking(
        rows, {"a": 1000.0, "b": 1.0, "c": 0.5}, {}, {"registrations": 1, "owner_picks": 1}
    )
    assert out == {"a-g1": 50.0, "b-g1": 0.1, "c-g1": 0.0}


def _row(gen: str, model: str, count: float | None) -> dict:
    return {"generation_id": gen, "model_id": model, "registered_count_nl": count}


def test_web_ranking_splits_a_model_by_rdw_count_like_the_web() -> None:
    rows = [
        _row("m1-g1", "m1", 300),
        _row("m1-g1", "m1", 300),  # second variant of the same generation
        _row("m1-g2", "m1", 100),
        _row("m2-g1", "m2", None),
        _row("m2-g2", "m2", None),
        _row("m3-g1", "m3", None),  # no registration score, no pick: not ranked
    ]
    out = web_ranking(rows, {"m1": 8.0, "m2": 2.0}, {"m2-g2": 1.0}, {**CFG})
    # shares: m1-g1 6.0 (top), m1-g2 2.0, m2 split evenly 1.0 + 1.0
    assert out == {"m1-g1": 80.0, "m1-g2": 26.7, "m2-g1": 13.3, "m2-g2": 33.3}


def _data_dir(tmp_path: Path) -> Path:
    data = tmp_path / "data"
    (data / "seed").mkdir(parents=True)
    (data / "editorial").mkdir()
    (tmp_path / "config").mkdir()
    (data / "seed" / "top40.yaml").write_text(
        yaml.safe_dump({"models": [{"model_id": "m1", "score_pct": 8.0}]}), encoding="utf-8"
    )
    (data / "editorial" / "menno-picks.yaml").write_text("primary_car_picks: []\n")
    (tmp_path / "config" / "popularity.yaml").write_text(
        yaml.safe_dump(
            {
                "weights": {"registrations": 0.8, "owner_picks": 0.2},
                "pick_values": {"shortlist": 1, "consider": 0.6, "fallback": 0.3},
            }
        ),
        encoding="utf-8",
    )
    return data


def test_backtest_on_a_catalogue(tmp_path: Path) -> None:
    rows = [_row(f"m1-g{i}", "m1", 10 * i) for i in range(1, 5)]
    gens = [{"id": f"m1-g{i}", "popularity": {"score": float(i)}} for i in range(1, 5)]
    gens[0]["popularity"]["score"] = 3.5  # g1 jumps from last to 2nd
    cat = {"rows": rows, "generations": gens}
    out = popularity_backtest(cat, _data_dir(tmp_path), {"spearman": 0.5})
    assert out["status"] == "ok"
    assert out["generations_both"] == 4
    assert out["spearman"] == pytest.approx(0.4)
    assert out["spearman_previous"] == 0.5
    assert out["worst"][0]["generation_id"] == "m1-g1"
    assert out["worst"][0]["rank_release"] == 2 and out["worst"][0]["rank_reference"] == 4
    assert "Spearman 0.4 over 4 generations (previous release 0.5)" in "\n".join(popularity_md(out))


def test_backtest_skips_without_the_release_field(tmp_path: Path) -> None:
    out = popularity_backtest(
        {"rows": [_row("m1-g1", "m1", 1)], "generations": [{"id": "m1-g1"}]},
        _data_dir(tmp_path),
    )
    assert out["status"] == "skipped" and out["missing"] == ["release field"]
    assert popularity_md(out) == []
