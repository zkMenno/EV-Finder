"""T-155: popularity back-test for qa.json (`backtest_popularity`, REVIEW D3, rule G-10).

The release field `generations[].popularity` (derive/popularity.py, T-149) replaces the web
build's own ranking. This back-test compares the two on the same release rows, so a change in
either shows up as a number:

- **release**: `generations[].popularity.score` as shipped (what the web reads once WS2 switches
  `apps/web/scripts/popularity.mjs` to the release field: the ranking the visitor sees).
- **reference**: the web build's ranking before that switch, ported 1:1 from
  `apps/web/src/lib/popularity.ts` `rankGenerations`: model scores from
  `data/seed/top40.yaml` (`score_pct`, ranked and outside-top models), split over a model's
  generations by `registered_count_nl` (evenly when none has a count), blended with the same
  owner picks and weights (`config/popularity.yaml`).

Reported: Spearman rank correlation over the generations both rank (average ranks for ties),
the median and worst absolute rank moves, and the top-10 / top-20 overlap. Report only: there
is no gate (a gate is a QA threshold, its own PR). The previous release's Spearman is carried
for comparison when it had this section.
"""

from __future__ import annotations

import math
import re
from pathlib import Path
from statistics import median
from typing import Any

import yaml

from ev_pipeline.derive.popularity import CONFIG_FILE, PICKS_FILE, parse_config, pick_scores

TOP40_FILE = Path("seed") / "top40.yaml"  # under data/
WORST_LISTED = 10
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")  # popularity.mjs ID_RE


def js_round1(x: float) -> float:
    """One decimal as JavaScript's Math.round(x * 10) / 10 (half rounds up, not to even)."""
    return math.floor(x * 10 + 0.5) / 10


def _load(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def model_scores(top40: dict[str, Any] | None) -> dict[str, float]:
    """model id -> registration score (% share), as popularity.mjs registrationScores."""
    out: dict[str, float] = {}
    doc = top40 or {}
    for m in [*(doc.get("models") or []), *(doc.get("seed_models_outside_top") or [])]:
        mid, s = (m or {}).get("model_id"), (m or {}).get("score_pct")
        if not isinstance(mid, str) or not ID_RE.match(mid):
            continue
        if isinstance(s, bool) or not isinstance(s, int | float) or not math.isfinite(s):
            continue
        if s < 0:
            continue
        out[mid] = max(out.get(mid, 0.0), float(s))
    return out


def web_ranking(
    rows: list[dict[str, Any]], models: dict[str, float], picks: dict[str, float], cfg: dict
) -> dict[str, float]:
    """generation id -> score, as apps/web/src/lib/popularity.ts rankGenerations."""
    gens: dict[str, dict[str, Any]] = {}
    for r in rows:
        c = r.get("registered_count_nl")
        c = c if isinstance(c, int | float) and not isinstance(c, bool) and c >= 0 else None
        g = gens.get(r["generation_id"])
        if g is None:
            gens[r["generation_id"]] = {"model": r["model_id"], "count": c}
        elif c is not None:
            g["count"] = max(g["count"] or 0, c)
    by_model: dict[str, list[str]] = {}
    for gid, g in gens.items():
        by_model.setdefault(g["model"], []).append(gid)
    shares: dict[str, float] = {}
    for mid, ids in by_model.items():
        reg = models.get(mid)
        if reg is None:
            continue
        total = sum(gens[i]["count"] or 0 for i in ids)
        for i in ids:
            shares[i] = reg * (gens[i]["count"] or 0) / total if total > 0 else reg / len(ids)
    top = max([0.0, *shares.values()])
    wr, wp = cfg["registrations"], cfg["owner_picks"]
    out: dict[str, float] = {}
    for gid in gens:
        share, pick = shares.get(gid), picks.get(gid)
        if share is None and pick is None:
            continue
        s = 100 * (wr * (share / top if share is not None and top > 0 else 0) + wp * (pick or 0))
        out[gid] = js_round1(s / (wr + wp))
    return out


def ranks(scores: dict[str, float]) -> dict[str, float]:
    """1 = highest score; ties share their average rank."""
    order = sorted(scores, key=lambda g: (-scores[g], g))
    out: dict[str, float] = {}
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and scores[order[j + 1]] == scores[order[i]]:
            j += 1
        for g in order[i : j + 1]:
            out[g] = (i + j) / 2 + 1
        i = j + 1
    return out


def spearman(a: dict[str, float], b: dict[str, float]) -> float | None:
    """Spearman's rho of two score maps over their shared keys (Pearson on average ranks)."""
    keys = sorted(set(a) & set(b))
    if len(keys) < 3:
        return None
    ra, rb = ranks({k: a[k] for k in keys}), ranks({k: b[k] for k in keys})
    xa, xb = [ra[k] for k in keys], [rb[k] for k in keys]
    ma, mb = sum(xa) / len(xa), sum(xb) / len(xb)
    cov = sum((x - ma) * (y - mb) for x, y in zip(xa, xb, strict=True))
    va = sum((x - ma) ** 2 for x in xa)
    vb = sum((y - mb) ** 2 for y in xb)
    if va == 0 or vb == 0:
        return None
    return round(cov / (va * vb) ** 0.5, 3)


def _top(scores: dict[str, float], n: int) -> set[str]:
    return set(sorted(scores, key=lambda g: (-scores[g], g))[:n])


def popularity_backtest(
    catalogue: dict[str, Any], data_dir: Path, previous: dict[str, Any] | None = None
) -> dict[str, Any]:
    release = {
        g["id"]: float(g["popularity"]["score"])
        for g in catalogue.get("generations") or []
        if isinstance(g.get("popularity"), dict) and "score" in g["popularity"]
    }
    top40 = _load(data_dir / TOP40_FILE)
    from ev_pipeline.release.build import config_dir

    cfg_doc = _load(config_dir(data_dir) / CONFIG_FILE)
    note = (
        "Report only (no gate). release = generations[].popularity (T-149); reference = the web"
        " build's ranking (apps/web/src/lib/popularity.ts on data/seed/top40.yaml), same picks"
        " and weights. Spearman over generations both rank; ties take their average rank."
    )
    if not release or top40 is None or cfg_doc is None:
        missing = [
            n
            for n, ok in (("release field", release), ("top40.yaml", top40), ("config", cfg_doc))
            if not ok
        ]
        return {"status": "skipped", "note": note, "missing": missing}
    cfg = parse_config(cfg_doc)
    picks = pick_scores(_load(data_dir / PICKS_FILE), cfg)
    ref = web_ranking(catalogue.get("rows") or [], model_scores(top40), picks, cfg)
    both = sorted(set(release) & set(ref))
    rr = ranks({g: release[g] for g in both})
    rf = ranks({g: ref[g] for g in both})
    moves = sorted(both, key=lambda g: (-abs(rr[g] - rf[g]), g))
    prev_rho = (previous or {}).get("spearman") if isinstance(previous, dict) else None
    return {
        "status": "ok",
        "note": note,
        "generations_release": len(release),
        "generations_reference": len(ref),
        "generations_both": len(both),
        "spearman": spearman(release, ref),
        "spearman_previous": prev_rho,
        "median_abs_rank_move": median(abs(rr[g] - rf[g]) for g in both) if both else None,
        "top10_overlap": len(_top(release, 10) & _top(ref, 10)),
        "top20_overlap": len(_top(release, 20) & _top(ref, 20)),
        "worst": [
            {
                "generation_id": g,
                "rank_release": rr[g],
                "rank_reference": rf[g],
                "score_release": release[g],
                "score_reference": ref[g],
            }
            for g in moves[:WORST_LISTED]
        ],
    }


def popularity_md(section: dict[str, Any] | None) -> list[str]:
    """qa.md lines for the section (empty when there is none)."""
    if not section or section.get("status") != "ok":
        return []
    prev = section.get("spearman_previous")
    return [
        "",
        "## Popularity back-test (T-155, report only)",
        "",
        f"Spearman {section['spearman']} over {section['generations_both']} generations"
        + (f" (previous release {prev})" if prev is not None else "")
        + f"; median rank move {section['median_abs_rank_move']}; top 10 overlap"
        f" {section['top10_overlap']}/10, top 20 {section['top20_overlap']}/20.",
    ]
