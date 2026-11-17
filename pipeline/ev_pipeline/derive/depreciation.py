"""T-113 (Decision 064): depreciation curve fitted on our own used price samples.

A point = one sample row (data/manual/prices, gated by derive/used_price.gate_samples) whose
generation (or variant) has a new list price for that country and build year
(used_price.pick_list_price: same rules as the bands). Its value is the share of the list
price the cars still ask: sample median / median list price of the generation's variants.

Curve: value kept = a x exp(-k x age), least squares on ln(share) against age (years since
the middle of the build year, used_price.age_at). Two parameters, smooth, never rises with
age; `a` < 1 is the first-registration drop. One fit for all cars, plus one per segment where
that segment alone has enough points and generations (`fit` thresholds in
used_price_params.yaml). The fitted table goes into used_price_params.yaml (a gate file) via
`ev used-price fit`; releases read it from there and never refit silently.

Back-test (rule G-10): leave one generation out and run exactly what a visitor would see for
it: fit_curves on the other generations (with the same thresholds, so a thin fold falls back
to the published curve) -> choose_curve (segment curve if that fold has one) -> kept_share on
the rounded yearly table -> each variant's list price -> rounded median and P25/P75
(used_price.shown_band). Reported: median and worst errors of the shown median, and the share
of real sample medians inside the shown P25-P75 band; next to the published curve on the same
points. That is the honest error of an estimate for a car we have no samples for.
"""

from __future__ import annotations

import math
import statistics
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any

from ev_pipeline.derive.used_price import (
    age_at,
    choose_curve,
    kept_share,
    pick_list_price,
    shown_band,
)

# Used only when used_price_params.yaml has no `fit:` block (the gate PR adds it).
DEFAULT_FIT = {
    "min_points": 20,
    "min_generations": 8,
    "segment_min_points": 15,
    "segment_min_generations": 5,
    "max_age": 12,
    "worst_listed": 5,
}
METHOD = "least squares on ln(share of list price kept) vs age; one point per sample row"


@dataclass
class Point:
    subject: str  # generation id (or variant id for a variant sample)
    generation_id: str
    segment: str
    country: str
    build_year: int
    age: float
    share: float
    samples: int
    sample_median: float
    list_price: float  # median over the variants below
    # Each matching variant's list price for this country and year (what its row would use).
    variant_list_prices: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def fit_settings(p: dict[str, Any]) -> dict[str, Any]:
    return {**DEFAULT_FIT, **(p.get("fit") or {})}


def fit_points(
    samples: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    prices: dict[tuple[str, str], dict[int, tuple[float, set[str], str]]],
    as_of: date,
    p: dict[str, Any],
) -> list[Point]:
    """Points where a (gated) sample row and a list price both exist, same currency."""
    by_gen: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_id: dict[str, dict[str, Any]] = {}
    for r in rows:
        by_gen[str(r.get("generation_id"))].append(r)
        by_id[str(r["variant_id"])] = r
    out = []
    for s in samples:
        if s["variant_id"]:
            vs = [by_id[s["variant_id"]]] if s["variant_id"] in by_id else []
        else:
            vs = by_gen.get(str(s["generation_id"]), [])
        if not vs:
            continue
        amounts: dict[str, float] = {}
        for v in vs:
            lp = pick_list_price(prices, str(v["variant_id"]), s["country"], s["build_year"], p)
            if lp is not None and lp["currency"] == s["currency"]:
                amounts[str(v["variant_id"])] = float(lp["amount"])
        if not amounts or s["median"] <= 0:
            continue
        lpm = statistics.median(amounts.values())
        out.append(
            Point(
                subject=str(s["variant_id"] or s["generation_id"]),
                generation_id=str(vs[0].get("generation_id")),
                segment=str(vs[0].get("segment")),
                country=s["country"],
                build_year=s["build_year"],
                age=round(age_at(s["build_year"], as_of, int(p["mid_year_month"])), 3),
                share=s["median"] / lpm,
                samples=s["n"],
                sample_median=s["median"],
                list_price=lpm,
                variant_list_prices=amounts,
            )
        )
    return out


def fit_exponential(points: list[Point]) -> tuple[float, float] | None:
    """(a, k) for share = a x exp(-k x age); None without two distinct ages."""
    xs = [pt.age for pt in points]
    ys = [math.log(pt.share) for pt in points]
    if len(set(xs)) < 2:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=True)) / sxx
    return math.exp(my - slope * mx), -slope


def predict(ak: tuple[float, float], age: float) -> float:
    a, k = ak
    return min(1.0, a * math.exp(-k * age))


def _quality(points: list[Point], ak: tuple[float, float]) -> dict[str, Any]:
    ys = [math.log(pt.share) for pt in points]
    my = statistics.fmean(ys)
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - math.log(predict(ak, pt.age))) ** 2 for y, pt in zip(ys, points, strict=True))
    errs = [predict(ak, pt.age) / pt.share - 1 for pt in points]
    return {
        "points": len(points),
        "generations": len({pt.generation_id for pt in points}),
        "countries": sorted({pt.country for pt in points}),
        "age_range": [
            round(min(pt.age for pt in points), 1),
            round(max(pt.age for pt in points), 1),
        ],
        "r2_log": round(1 - ss_res / ss_tot, 3) if ss_tot > 0 else None,
        "in_sample_median_abs_error": round(statistics.median(abs(e) for e in errs), 3),
    }


def curve_table(ak: tuple[float, float], max_age: int, observed_max_age: float) -> dict[str, Any]:
    """The fitted curve in the params' `curves` shape (yearly points; used_price.kept_share)."""
    return {
        "points": {y: round(predict(ak, y), 3) for y in range(0, max_age + 1)},
        "extrapolated_from_age": math.floor(observed_max_age) + 1,
        "max_age": max_age,
        "a": round(ak[0], 4),
        "k": round(ak[1], 4),
    }


def _enough(points: list[Point], n: int, gens: int) -> bool:
    return len(points) >= n and len({pt.generation_id for pt in points}) >= gens


def fit_curves(points: list[Point], p: dict[str, Any]) -> dict[str, Any]:
    """{'default': curve | None, 'by_segment': {...}, 'note': ...} with quality per curve."""
    fs = fit_settings(p)
    out: dict[str, Any] = {"default": None, "by_segment": {}}
    if not _enough(points, int(fs["min_points"]), int(fs["min_generations"])):
        out["note"] = (
            f"{len(points)} points, {len({pt.generation_id for pt in points})} generations:"
            f" below {fs['min_points']} / {fs['min_generations']}; the published curve stays"
        )
        return out
    ak = fit_exponential(points)
    if ak is None:
        out["note"] = "points cover one age only"
        return out
    obs = max(pt.age for pt in points)
    out["default"] = {
        **curve_table(ak, int(fs["max_age"]), obs),
        "quality": _quality(points, ak),
    }
    by_seg: dict[str, list[Point]] = defaultdict(list)
    for pt in points:
        by_seg[pt.segment].append(pt)
    for seg, pts in sorted(by_seg.items()):
        if not _enough(pts, int(fs["segment_min_points"]), int(fs["segment_min_generations"])):
            continue
        sak = fit_exponential(pts)
        if sak is None:
            continue
        out["by_segment"][seg] = {
            **curve_table(sak, int(fs["max_age"]), max(pt.age for pt in pts)),
            "quality": _quality(pts, sak),
        }
    return out


def _errors(rows: list[dict[str, Any]], worst_n: int) -> dict[str, Any]:
    errs = [r["error"] for r in rows]
    if not errs:
        return {
            "rows_compared": 0,
            "median_abs_error": None,
            "median_error": None,
            "in_band": None,
            "worst": [],
        }
    worst = sorted(rows, key=lambda r: -abs(r["error"]))[:worst_n]
    return {
        "rows_compared": len(rows),
        "median_abs_error": round(statistics.median(abs(e) for e in errs), 3),
        "median_error": round(statistics.median(errs), 3),
        "within_15pct": round(sum(abs(e) <= 0.15 for e in errs) / len(errs), 3),
        # Share of real sample medians inside the P25-P75 band the visitor is shown.
        "in_band": round(sum(r["in_band"] for r in rows) / len(rows), 3),
        "worst": worst,
    }


def _shown(pt: Point, curve: dict[str, Any], p: dict[str, Any]) -> dict[str, float] | None:
    """What the visitor sees for this point: each variant's rounded band (shown_band), then
    the median across the generation's variants (one variant for a variant sample)."""
    share = kept_share(pt.age, curve)
    if share is None:
        return None
    bands = [shown_band(a, share, p) for a in pt.variant_list_prices.values()] or [
        shown_band(pt.list_price, share, p)
    ]
    return {k: statistics.median(b[k] for b in bands) for k in ("p25", "median", "p75")}


def holdout_backtest(points: list[Point], p: dict[str, Any]) -> dict[str, Any]:
    """Leave one generation out through the visitor's path (module docstring): the error of
    the shown estimate on cars the fit never saw, vs the published curve on the same points
    (G-10: median error, band coverage and worst cases)."""
    fs = fit_settings(p)
    worst_n = int(fs["worst_listed"])
    published_p = {**p, "fitted": None}
    fitted_rows: list[dict[str, Any]] = []
    published_rows: list[dict[str, Any]] = []
    curves_used: dict[str, int] = defaultdict(int)
    for gid in sorted({pt.generation_id for pt in points}):
        train = [pt for pt in points if pt.generation_id != gid]
        fold = fit_curves(train, p)
        fold_p = {
            **p,
            "fitted": (
                {**(p.get("fitted") or {}), "default": fold["default"],
                 "by_segment": fold["by_segment"]}
                if fold["default"]
                else None
            ),
        }  # fmt: skip
        for pt in (x for x in points if x.generation_id == gid):
            base = {
                "subject": pt.subject,
                "country": pt.country,
                "build_year": pt.build_year,
                "samples": pt.samples,
                "sample_median": round(pt.sample_median),
            }
            for which, pp, out in (
                ("fitted", fold_p, fitted_rows),
                ("published", published_p, published_rows),
            ):
                curve, info = choose_curve(pp, pt.country, pt.segment)
                shown = _shown(pt, curve, p)
                if shown is None:
                    continue
                if which == "fitted":
                    curves_used[info["curve"]] += 1
                out.append(
                    {
                        **base,
                        "curve": info["curve"],
                        **shown,
                        "error": round(shown["median"] / pt.sample_median - 1, 3),
                        "in_band": shown["p25"] <= pt.sample_median <= shown["p75"],
                    }
                )
    return {
        "method": "leave one generation out: fit on the other generations, then the visitor's"
        " path (choose_curve, kept_share on the yearly table, rounded band per variant)",
        "error": "shown median / sample median - 1 (asking prices); in_band = sample median"
        " inside the shown P25-P75",
        "fitted": {
            **_errors(fitted_rows, worst_n),
            "curves_used": dict(sorted(curves_used.items())),
        },
        "published": _errors(published_rows, worst_n),
    }


def fit_block(
    points: list[Point],
    p: dict[str, Any],
    fitted_at: str,
    release: int | None,
) -> dict[str, Any]:
    """The `fitted:` block for used_price_params.yaml (written by `ev used-price fit`)."""
    curves = fit_curves(points, p)
    return {
        "method": METHOD,
        "fitted_at": fitted_at,
        "on_release": release,
        "samples_observed": sorted({str(pt.country) for pt in points}),
        "default": curves["default"],
        "by_segment": curves["by_segment"],
        **({"note": curves["note"]} if "note" in curves else {}),
        "holdout": {
            k: (v if k == "method" else {kk: vv for kk, vv in v.items() if kk != "worst"})
            for k, v in holdout_backtest(points, p).items()
            if k in ("method", "fitted", "published")
        },
    }
