"""T-081: used price band per variant, build year and country (model estimate + manual samples).

Model: list price at registration x share of value kept at that age (curve in
used_price_params.yaml, anchors in research/R-40). P25/P75 = median x (1 -/+ spread).
Every model band is an estimate with `samples: 0`. A manual sample aggregate (layer 2,
data/manual/prices/*.yaml, aggregates only, Decision 004) with enough cars replaces the model
band for that variant and build year, and every sample row is back-tested against the model.

List price per country and build year, in this order: a price_new fact for that year; the
nearest year within `max_year_gap`; for DE/FR/BE the Dutch price moved to local VAT (low
confidence). No list price → no band ("not enough data"), never a guess.

Source gate (T-111, QA A-35 S2): every sample file must resolve to a data/sources.yaml entry
(`source.id`, else the URL host in an entry's `site_hosts`) that may feed our aggregates
(`Registry.aggregate_input_problem`: releasable, or `use: aggregates-only` with a logged owner
decision, Decision 060). Other samples are dropped and listed in the run log; a missing
registry drops them all (fail closed).
"""

from __future__ import annotations

import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from ev_pipeline.release.gate import Registry, load_registry

FILE_NAME = "used_prices.json"
PARAMS_FILE = Path(__file__).with_name("used_price_params.yaml")


@dataclass
class UsedPriceResult:
    document: dict[str, Any] | None = None
    log: dict[str, Any] = field(default_factory=dict)
    inputs: list[dict[str, Any]] = field(default_factory=list)


def load_params(path: Path = PARAMS_FILE) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


# --- curve -----------------------------------------------------------------------------------


def kept_share(age: float, curve: dict[str, Any]) -> float | None:
    """Share of the list price kept at `age` years (linear between whole years)."""
    pts = {int(k): float(v) for k, v in curve["points"].items()}
    if age < 0 or age > float(curve.get("max_age", max(pts))):
        return None
    ages = sorted(pts)
    if age >= ages[-1]:  # beyond the table: keep the last yearly step
        last, prev = pts[ages[-1]], pts[ages[-2]]
        return last * (last / prev) ** (age - ages[-1])
    lo = max(a for a in ages if a <= age)
    hi = min(a for a in ages if a >= age)
    if lo == hi:
        return pts[lo]
    t = (age - lo) / (hi - lo)
    return pts[lo] + t * (pts[hi] - pts[lo])


def age_at(build_year: int, as_of: date, mid_month: int) -> float:
    start = date(build_year, mid_month, 1)
    return max(0.0, (as_of - start).days / 365.25)


# --- list prices ------------------------------------------------------------------------------


def list_prices(
    facts: list[dict[str, Any]], years: list[int | None]
) -> dict[tuple[str, str], dict[int, tuple[float, set[str], str]]]:
    """(variant, country) -> record year -> (median amount, source ids, currency)."""
    raw: dict[tuple[str, str], dict[int, list[tuple[float, str, str]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for f, y in zip(facts, years, strict=True):
        if f.get("field") != "price_new" or y is None or f.get("subject_type") != "variant":
            continue
        cc, v = f.get("country"), f.get("value")
        if not cc or not isinstance(v, int | float) or isinstance(v, bool) or v <= 0:
            continue
        raw[(f["subject_id"], cc)][int(y)].append(
            (float(v), str(f["source"]["id"]), str(f.get("unit") or ""))
        )
    out: dict[tuple[str, str], dict[int, tuple[float, set[str], str]]] = {}
    for key, by_year in raw.items():
        out[key] = {
            y: (
                statistics.median(a for a, _, _ in vals),
                {s for _, s, _ in vals},
                Counter(u for _, _, u in vals).most_common(1)[0][0],
            )
            for y, vals in by_year.items()
        }
    return out


def pick_list_price(
    prices: dict[tuple[str, str], dict[int, tuple[float, set[str], str]]],
    vid: str,
    cc: str,
    year: int,
    p: dict[str, Any],
) -> dict[str, Any] | None:
    own = prices.get((vid, cc)) or {}
    if year in own:
        a, src, cur = own[year]
        return {
            "amount": a,
            "basis": "year",
            "sources": src,
            "currency": cur,
            "confidence": "medium",
        }
    near = [y for y in own if abs(y - year) <= int(p["max_year_gap"])]
    if near:
        y = min(near, key=lambda y: (abs(y - year), -y))
        a, src, cur = own[y]
        return {
            "amount": a,
            "basis": "nearest_year",
            "from_year": y,
            "sources": src,
            "currency": cur,
            "confidence": "low",
        }
    base = str(p["cross_country_from"])
    if cc in p.get("cross_country_to", []) and cc != base:
        lp = pick_list_price(prices, vid, base, year, {**p, "cross_country_to": []})
        if lp and lp["currency"] == "EUR":
            vat = p["vat"]
            amount = lp["amount"] / (1 + float(vat[base])) * (1 + float(vat[cc]))
            return {
                "amount": amount,
                "basis": f"from_{base.lower()}_vat_adjusted",
                "from_year": lp.get("from_year", year),
                "sources": lp["sources"],
                "currency": "EUR",
                "confidence": "low",
            }
    return None


# --- manual samples ---------------------------------------------------------------------------


def load_samples(dir_: Path) -> tuple[list[dict[str, Any]], list[str]]:
    """Aggregate rows from data/manual/prices/*.yaml; problems are reported, never fatal."""
    rows: list[dict[str, Any]] = []
    problems: list[str] = []
    if not dir_.exists():
        return rows, problems
    for path in sorted(dir_.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        need = ("country", "observed_at", "currency", "source", "rows")
        miss = [k for k in need if not doc.get(k)]
        if miss or not (doc.get("generation_id") or doc.get("variant_id")):
            problems.append(f"{path.name}: missing {miss or ['generation_id or variant_id']}")
            continue
        src = doc["source"]
        if not isinstance(src, dict) or not src.get("url") or not src.get("name"):
            problems.append(f"{path.name}: source needs name and url")
            continue
        for r in doc["rows"]:
            ok = all(isinstance(r.get(k), int | float) for k in ("build_year", "n", "median"))
            if not ok:
                problems.append(f"{path.name}: row needs build_year, n, median: {r}")
                continue
            rows.append(
                {
                    "file": path.name,
                    "country": str(doc["country"]).upper(),
                    "generation_id": doc.get("generation_id"),
                    "variant_id": doc.get("variant_id"),
                    "observed_at": str(doc["observed_at"]),
                    "currency": doc["currency"],
                    "source": {"name": src["name"], "url": src["url"]},
                    "source_id": src.get("id"),
                    "build_year": int(r["build_year"]),
                    "n": int(r["n"]),
                    "p25": r.get("p25"),
                    "median": float(r["median"]),
                    "p75": r.get("p75"),
                }
            )
    return rows, problems


def gate_samples(
    samples: list[dict[str, Any]], registry: Registry
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """Keep samples whose source may feed our aggregates; dropped file -> reason (A-35 S2).
    Each kept sample gets `source_id` set to its registry id."""
    kept: list[dict[str, Any]] = []
    dropped: dict[str, str] = {}
    for s in samples:
        sid = s.get("source_id") or registry.source_for_url(s["source"]["url"])
        if not sid:
            dropped[s["file"]] = "source not in data/sources.yaml (no id, URL host not listed)"
            continue
        why = registry.aggregate_input_problem(str(sid))
        if why is not None:
            dropped[s["file"]] = f"{sid}: {why}"
            continue
        kept.append({**s, "source_id": str(sid)})
    return kept, dropped


# --- build ------------------------------------------------------------------------------------


def _round(x: float, step: int) -> float:
    return float(round(x / step) * step)


def build_years(row: dict[str, Any], as_of: date) -> list[int]:
    ys, ye = row.get("year_start"), row.get("year_end")
    if ys is None:
        return []
    end = min(int(ye) if ye is not None else as_of.year, as_of.year)
    return list(range(int(ys), end + 1))


def build_used_prices(
    rows: list[dict[str, Any]],
    facts: list[dict[str, Any]],
    fact_years: list[int | None],
    data_dir: Path,
    release: int,
    generated_at: str,
    params_path: Path = PARAMS_FILE,
    registry: Registry | None = None,
) -> UsedPriceResult:
    out = UsedPriceResult()
    p = load_params(params_path)
    as_of = date.fromisoformat(generated_at[:10])
    prices = list_prices(facts, fact_years)
    samples, problems = load_samples(data_dir / p["samples_dir"])
    if registry is None:
        registry = load_registry(data_dir / "sources.yaml")
    samples_read = len(samples)
    samples, dropped = gate_samples(samples, registry)
    if samples:
        out.inputs.append(
            {
                "path": str(data_dir / p["samples_dir"]),
                "kind": "manual price aggregates",
                "rows": len(samples),
            }
        )
    step = int(p["rounding"])
    spread = float(p["spread"])
    curve = p["curves"].get("default")
    fresh = {
        (s["variant_id"], s["country"], s["build_year"]): s
        for s in samples
        if s["variant_id"]
        and s["n"] >= int(p["min_samples"])
        and (as_of - date.fromisoformat(s["observed_at"][:10])).days
        <= int(p["max_sample_age_days"])
    }
    variants = []
    counts: Counter[str] = Counter()
    used_sources: set[str] = set()
    model_medians: dict[tuple[str, str, int], float] = {}
    for row in sorted(rows, key=lambda r: r["variant_id"]):
        vid = row["variant_id"]
        bands: dict[str, list[dict[str, Any]]] = {}
        for cc in p["countries"]:
            cur_curve = p["curves"].get(cc, curve)
            out_rows = []
            for y in build_years(row, as_of):
                lp = pick_list_price(prices, vid, cc, y, p)
                age = age_at(y, as_of, int(p["mid_year_month"]))
                share = kept_share(age, cur_curve)
                if lp is not None and share is not None:  # kept for the back-test too
                    model_medians[(vid, cc, y)] = lp["amount"] * share
                s = fresh.get((vid, cc, y))
                if s:
                    out_rows.append(
                        {
                            "build_year": y,
                            "p25": s["p25"],
                            "median": s["median"],
                            "p75": s["p75"],
                            "samples": s["n"],
                            "method": "samples",
                            "estimate": False,
                            "observed_at": s["observed_at"],
                            "source": s["source"],
                            "source_id": s["source_id"],
                            "confidence": "medium",
                        }
                    )
                    counts[f"{cc} samples"] += 1
                    continue
                if lp is None or share is None:
                    counts[f"{cc} not enough data"] += 1
                    continue
                med = model_medians[(vid, cc, y)]
                conf = lp["confidence"]
                if age >= float(cur_curve.get("extrapolated_from_age", 99)):
                    conf = "low"
                used_sources |= lp["sources"]
                out_rows.append(
                    {
                        "build_year": y,
                        "p25": _round(med * (1 - spread), step),
                        "median": _round(med, step),
                        "p75": _round(med * (1 + spread), step),
                        "samples": 0,
                        "method": "model",
                        "estimate": True,
                        "age_years": round(age, 1),
                        "kept_share": round(share, 3),
                        "list_price": _round(lp["amount"], step),
                        "list_basis": lp["basis"],
                        "list_source_ids": sorted(lp["sources"]),
                        "confidence": conf,
                    }
                )
                counts[f"{cc} model"] += 1
            if out_rows:
                cur = p["currency"][cc]
                bands[cc] = [r | {"currency": cur} for r in out_rows]
        if bands:
            variants.append(
                {"variant_id": vid, "generation_id": row.get("generation_id"), "bands": bands}
            )
    gen_of = {r["variant_id"]: r.get("generation_id") for r in rows}
    bt = backtest(samples, model_medians, gen_of)
    gen_bands = generation_bands(samples, p, as_of)
    out.document = {
        "release": release,
        "generated_at": generated_at,
        "model_version": str(p["model_version"]),
        "estimate": True,
        "note": "Used asking-price bands. method 'model' = list price at registration x share of"
        " value kept at that age (estimate, samples 0); method 'samples' = manual sample"
        " aggregates."
        " Amounts in each country's currency; convert at display time.",
        "anchors_as_of": p["anchors_as_of"],
        "method_ref": "research/R-40-used-ev-price-anchors.md",
        "spread": spread,
        "list_price_source_ids": sorted(used_sources),
        "variants": variants,
        "generation_bands": gen_bands,
        "backtest": bt,
    }
    out.log = {
        "status": "shipped",
        "variants_with_a_band": len(variants),
        "variants": len(rows),
        "bands": dict(sorted(counts.items())),
        "sample_rows": len(samples),
        "sample_rows_read": samples_read,
        "sample_files_dropped_by_source_gate": dict(sorted(dropped.items())),
        "sample_problems": problems,
        "backtest": {k: v for k, v in bt.items() if k != "rows"},
    }
    return out


def generation_bands(
    samples: list[dict[str, Any]], p: dict[str, Any], as_of: date
) -> list[dict[str, Any]]:
    """Sampled generation-level bands (schema UsedPriceBand shape), fresh and big enough only."""
    out = []
    for s in samples:
        if s["variant_id"] or s["n"] < int(p["min_samples"]):
            continue
        if (as_of - date.fromisoformat(s["observed_at"][:10])).days > int(p["max_sample_age_days"]):
            continue
        out.append(
            {
                "generation_id": s["generation_id"],
                "country": s["country"],
                "currency": s["currency"],
                "p25": s["p25"],
                "median": s["median"],
                "p75": s["p75"],
                "samples": s["n"],
                "period": s["observed_at"][:7],
                "age_band_years": None,
                "build_year": s["build_year"],
                "source": s["source"],
                "source_id": s["source_id"],
            }
        )
    return out


def backtest(
    samples: list[dict[str, Any]],
    model: dict[tuple[str, str, int], float],
    gen_of: dict[str, str | None],
) -> dict[str, Any]:
    """Model median vs sample median per sample row (all rows, stale ones too)."""
    by_gen: dict[tuple[str, str, int], list[float]] = defaultdict(list)
    for (vid, cc, y), m in model.items():
        if gen_of.get(vid):
            by_gen[(str(gen_of[vid]), cc, y)].append(m)
    rows = []
    for s in samples:
        if s["variant_id"]:
            m = model.get((s["variant_id"], s["country"], s["build_year"]))
        else:
            ms = by_gen.get((str(s["generation_id"]), s["country"], s["build_year"]))
            m = statistics.median(ms) if ms else None
        if m is None:
            continue
        err = m / s["median"] - 1
        rows.append(
            {
                "subject": s["variant_id"] or s["generation_id"],
                "country": s["country"],
                "build_year": s["build_year"],
                "sample_median": s["median"],
                "samples": s["n"],
                "model_median": round(m),
                "error": round(err, 3),
            }
        )
    errs = [r["error"] for r in rows]
    return {
        "rows_compared": len(rows),
        "median_abs_error": round(statistics.median(abs(e) for e in errs), 3) if errs else None,
        "median_error": round(statistics.median(errs), 3) if errs else None,
        "gate": False,
        "note": "No manual samples yet" if not samples else None,
        "rows": rows,
    }


def coverage_lines(log: dict[str, Any]) -> list[str]:
    if not log or log.get("status") != "shipped":
        return []
    lines = ["", "## Used price bands (T-081, estimates)", ""]
    lines.append(
        f"{log['variants_with_a_band']} of {log['variants']} variants have a band"
        " in at least one country."
    )
    lines += [
        "",
        "| Country | Model bands | Sampled bands | Not enough data |",
        "|---|---|---|---|",
    ]
    b = log["bands"]
    for cc in sorted({k.split(" ")[0] for k in b}):
        lines.append(
            f"| {cc} | {b.get(f'{cc} model', 0)} | {b.get(f'{cc} samples', 0)}"
            f" | {b.get(f'{cc} not enough data', 0)} |"
        )
    bt = log.get("backtest") or {}
    lines.append("")
    if bt.get("rows_compared"):
        lines.append(
            f"Back-test against manual samples: {bt['rows_compared']} rows, median absolute error"
            f" {bt['median_abs_error']:.0%}, median error {bt['median_error']:+.0%} (not a gate)."
        )
    else:
        lines.append("Back-test against manual samples: no samples yet.")
    return lines
