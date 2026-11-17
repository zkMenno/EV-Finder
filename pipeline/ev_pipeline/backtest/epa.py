"""T-035: back-test the range and consumption models on licence-clean EPA figures.

Until the real-world test sources give permission (Nyland, NAF El Prix, ADAC: Q-059), the
only licence-clean measurements are EPA label values from fueleconomy.gov (public domain):
the adjusted combined range and the city / highway consumption. They are a PROXY, not a road
test: US cycles, US-market cars, 5-cycle adjusted (cold, hot and A/C blended in). They test
whether WLTP-based estimates land near an independent measurement; they say nothing about
winter motorway driving. The launch gate (median error < 10 % on El Prix / Nyland, spec §5)
still needs those tests.

Two checks, per variant that has both a WLTP figure and EPA data:
- **range**: the release's `real_range_km` (WLTP x body ratio today) vs the median EPA
  adjusted range of the variant's matched EPA records.
- **consumption**: the consumption model with the variant's own tests hidden (so its town
  and rural cells fall to the wltp-ratio rung) vs the EPA city / highway figure (battery
  basis), both at the 20 °C reference.
Leakage guard: a variant whose WLTP range or consumption came from fueleconomy (or is an
estimate) is left out of that check.

Reports median absolute % error and mean signed error overall, per model, per body and for
the top-40 used models (data/seed/top40.yaml), the worst cases, and regressions (> 3 points
worse per model than the previous release).
"""

from __future__ import annotations

import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

from ev_pipeline.derive import consumption as cm

GATE_MEDIAN_ABS_PCT = 10.0
REGRESSION_POINTS = 3.0
WORST_N = 10
LEAK_SOURCES = {"fueleconomy", "model-estimate"}


def _sources(row: dict[str, Any], fieldname: str) -> set[str]:
    return set(((row.get("provenance") or {}).get(fieldname) or {}).get("source_ids") or [])


def _clean(row: dict[str, Any], fieldname: str) -> bool:
    ids = _sources(row, fieldname)
    return bool(row.get(fieldname)) and bool(ids) and not (ids & LEAK_SOURCES)


def _summary(results: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    g: dict[str, list[float]] = defaultdict(list)
    for r in results:
        g[str(r[key])].append(r["error_pct"])
    return {
        k: {
            "n": len(v),
            "median_abs_pct": round(statistics.median(abs(e) for e in v), 2),
            "mean_signed_pct": round(statistics.mean(v), 2),
        }
        for k, v in sorted(g.items())
    }


def _report(results: list[dict[str, Any]], top40: list[str]) -> dict[str, Any]:
    if not results:
        return {"status": "skipped", "note": "no variant with both a clean WLTP and EPA figure"}
    errs = [r["error_pct"] for r in results]
    overall = round(statistics.median(abs(e) for e in errs), 2)
    by_model = _summary(results, "model_id")
    return {
        "status": "pass" if overall < GATE_MEDIAN_ABS_PCT else "flag",
        "gate": f"median absolute error < {GATE_MEDIAN_ABS_PCT:g}% (proxy, not the launch gate)",
        "n": len(results),
        "variants": len({r["variant_id"] for r in results}),
        "median_abs_pct": overall,
        "mean_signed_pct": round(statistics.mean(errs), 2),
        "by_body": _summary(results, "body"),
        "by_model": by_model,
        "top40": {
            "models_with_data": sum(1 for m in top40 if m in by_model),
            "models": len(top40),
            "by_model": {m: by_model[m] for m in top40 if m in by_model},
            "missing": [m for m in top40 if m not in by_model],
        },
        "worst": sorted(results, key=lambda r: (-abs(r["error_pct"]), r["variant_id"]))[:WORST_N],
    }


def epa_by_variant(facts: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """variant -> {range_km: median EPA range, records: [...]} from fueleconomy facts."""
    acc: dict[str, list[float]] = defaultdict(list)
    recs: dict[str, set[str]] = defaultdict(set)
    for f in facts:
        src = (f.get("source") or {}).get("id") or f.get("source_id")
        if src != "fueleconomy" or f.get("subject_type") != "variant":
            continue
        if f.get("field") == "epa_range_km":
            v = f.get("value") if "value" in f else f.get("value_num")
            if isinstance(v, int | float):
                acc[f["subject_id"]].append(float(v))
                recs[f["subject_id"]].add(str(f.get("source_record")))
    return {
        vid: {"range_km": statistics.median(v), "records": sorted(recs[vid])}
        for vid, v in acc.items()
    }


def range_check(rows: list[dict[str, Any]], facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    epa = epa_by_variant(facts)
    out = []
    for r in rows:
        e = epa.get(r["variant_id"])
        if not e or not r.get("real_range_km") or not _clean(r, "wltp_range_km"):
            continue
        err = 100 * (float(r["real_range_km"]) - e["range_km"]) / e["range_km"]
        out.append(
            {
                "variant_id": r["variant_id"],
                "model_id": r.get("model_id"),
                "body": r.get("body") or "unknown",
                "rung": r.get("real_range_rung"),
                "predicted_km": round(float(r["real_range_km"]), 1),
                "measured_km": round(e["range_km"], 1),
                "error_pct": round(err, 2),
                "epa_records": len(e["records"]),
            }
        )
    return out


def consumption_check(
    rows: list[dict[str, Any]],
    tests_by_variant: dict[str, list[dict[str, Any]]],
    params: dict[str, Any],
) -> list[dict[str, Any]]:
    w2b = float(params["wall_to_battery"])
    out = []
    for r in rows:
        tests = tests_by_variant.get(r["variant_id"]) or []
        if not tests or not _clean(r, "consumption_kwh_100km"):
            continue
        model = cm.variant_model(r, [], params, 0, "")  # own tests hidden -> wltp-ratio
        if model is None:
            continue
        ref_tb = max(params["temperature_bands"], key=lambda t: t["representative_c"])["id"]
        cells = {
            c["road_band"]: c["wh_km"]
            for c in model["cells"]
            if c["temperature_band_id"] == ref_tb and c.get("heater_type_id") in (None, "unknown")
        }
        for band in ("town", "rural"):
            ts = [t for t in tests if t.get("road_band") == band]
            if not ts or band not in cells:
                continue
            measured = statistics.median(float(t["consumption_wh_km"]) for t in ts) * w2b
            err = 100 * (cells[band] - measured) / measured
            out.append(
                {
                    "variant_id": r["variant_id"],
                    "model_id": r.get("model_id"),
                    "body": r.get("body") or "unknown",
                    "band": band,
                    "predicted_wh_km": round(cells[band], 1),
                    "measured_wh_km": round(measured, 1),
                    "error_pct": round(err, 2),
                    "tests": len(ts),
                }
            )
    return out


def consumption_oos(
    results: list[dict[str, Any]], params: dict[str, Any], min_models: int = 5
) -> list[dict[str, Any]]:
    """Leave-one-model-out version of `consumption_check` results (START §3 item 6).

    The wltp-ratio multipliers were fitted on these same EPA figures (in-sample, A-30). Refitting
    them without model M is, for a median fit, the same as scaling M's prediction by
    median(measured / predicted over the other models) / median(over all models), per road band
    and body class (band-wide when a class has fewer than `min_models` other models).
    """
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for r in results:
        groups[(r["band"], cm._ratio_key(r["body"], params))].append(r)
        groups[(r["band"], "*")].append(r)

    def ratio(rows: list[dict[str, Any]]) -> float:
        return statistics.median(r["measured_wh_km"] / r["predicted_wh_km"] for r in rows)

    out = []
    for r in results:
        key = (r["band"], cm._ratio_key(r["body"], params))
        pool = groups[key]
        others = [o for o in pool if o["model_id"] != r["model_id"]]
        if len({o["model_id"] for o in others}) < min_models:
            pool = groups[(r["band"], "*")]
            others = [o for o in pool if o["model_id"] != r["model_id"]]
        if not others:
            continue
        pred = r["predicted_wh_km"] * ratio(others) / ratio(pool)
        err = 100 * (pred - r["measured_wh_km"]) / r["measured_wh_km"]
        out.append(r | {"predicted_wh_km": round(pred, 1), "error_pct": round(err, 2)})
    return out


def regressions(current: dict[str, Any], previous: dict[str, Any] | None) -> list[dict[str, Any]]:
    prev = (previous or {}).get("by_model") or {}
    out = []
    for mid, c in (current.get("by_model") or {}).items():
        p = prev.get(mid)
        if p and c["median_abs_pct"] - p["median_abs_pct"] > REGRESSION_POINTS:
            out.append(
                {"model_id": mid, "previous": p["median_abs_pct"], "now": c["median_abs_pct"]}
            )
    return out


def top40_models(data_dir: Path) -> list[str]:
    p = data_dir / "seed" / "top40.yaml"
    if not p.exists():
        return []
    doc = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return [str(m["model_id"]) for m in doc.get("models") or [] if m.get("model_id")]


def epa_backtest(
    catalogue: dict[str, Any],
    facts: list[dict[str, Any]],
    data_dir: Path,
    releasable: Any,
    previous: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """qa.json `backtest_epa`: proxy back-test on EPA figures (see module docstring)."""
    if not releasable("fueleconomy"):
        return {"status": "skipped", "note": "fueleconomy is not releasable"}
    rows = catalogue.get("rows") or []
    params = cm.load_params(taxonomy_dir=data_dir / "taxonomy")
    tests, _ = cm.load_tests(data_dir / "staging")
    by_variant = cm.tests_by_variant(facts, tests, releasable)
    top40 = top40_models(data_dir)
    out: dict[str, Any] = {
        "kind": "proxy",
        "note": "EPA label values (fueleconomy.gov, public domain): US cycles, 5-cycle adjusted. "
        "A check that WLTP-based estimates land near an independent measurement, not the "
        "launch gate (independent real-world tests, spec §5).",
        "range": _report(range_check(rows, facts), top40),
        "consumption": _report(cons := consumption_check(rows, by_variant, params), top40),
    }
    oos = _report(consumption_oos(cons, params), top40)
    if oos.get("status") != "skipped":
        oos["note"] = (
            "Leave-one-model-out: each model's prediction uses ratios fitted without it. This is"
            " the honest error of the calibrated wltp-ratio rung on an unseen model."
        )
    out["consumption_oos"] = oos
    regs = []
    for part in ("range", "consumption", "consumption_oos"):
        r = regressions(out[part], (previous or {}).get(part))
        for x in r:
            x["check"] = part
        regs += r
        if r and out[part].get("status") == "pass":
            out[part]["status"] = "flag"
    out["regressions"] = regs
    return out


def audit_md(bt: dict[str, Any], release: int, generated_at: str) -> str:
    """Human report for audits/ (A-30)."""
    lines = [
        "# A-30 Back-test on EPA figures (proxy)",
        "",
        f"Release {release}, generated {generated_at} by `ev_pipeline.backtest.epa` (T-035).",
        "",
        bt.get("note", ""),
        "",
    ]
    parts = (
        ("range", "Real range vs EPA adjusted range"),
        ("consumption", "Consumption (wltp-ratio rung) vs EPA city/highway"),
        ("consumption_oos", "Consumption, out of sample (leave one model out)"),
    )
    for part, label in parts:
        r = bt.get(part) or {}
        lines += [f"## {label}", ""]
        if r.get("status") in (None, "skipped"):
            lines += [f"Skipped: {r.get('note', 'no data')}", ""]
            continue
        lines += [
            f"- **Median absolute error:** {r['median_abs_pct']} % over {r['n']} comparisons"
            f" ({r['variants']} variants); mean signed {r['mean_signed_pct']:+} %"
            f" ({'model reads high' if r['mean_signed_pct'] > 0 else 'model reads low'}).",
            f"- Status against a 10 % proxy gate: **{r['status']}**.",
            f"- Top-40 used models with data: {r['top40']['models_with_data']} of"
            f" {r['top40']['models']}.",
            "",
            "| Body | n | median abs % | mean signed % |",
            "|---|---:|---:|---:|",
        ]
        for k, v in r["by_body"].items():
            lines.append(f"| {k} | {v['n']} | {v['median_abs_pct']} | {v['mean_signed_pct']:+} |")
        lines += ["", "| Top-40 model | n | median abs % | mean signed % |"]
        lines += ["|---|---:|---:|---:|"]
        for k, v in r["top40"]["by_model"].items():
            lines.append(f"| {k} | {v['n']} | {v['median_abs_pct']} | {v['mean_signed_pct']:+} |")
        if r["top40"]["missing"]:
            lines += ["", "No data: " + ", ".join(r["top40"]["missing"]) + "."]
        lines += ["", "Worst cases:", ""]
        for w in r["worst"][:5]:
            what = w.get("band", "range")
            lines.append(f"- {w['variant_id']} ({what}): {w['error_pct']:+} %")
        lines.append("")
    if bt.get("regressions"):
        lines += ["## Regressions vs previous release", ""]
        for x in bt["regressions"]:
            lines.append(f"- {x['check']} {x['model_id']}: {x['previous']} % → {x['now']} %")
        lines.append("")
    lines += [
        "## What this does not show",
        "",
        "- Winter or motorway error: EPA cycles are mild-weather lab cycles (adjusted).",
        "- EU-market differences (wheels, software, packs) between matched US and EU cars.",
        "- The launch gate needs licence-cleared road tests (Q-059): this is a proxy only.",
        "",
    ]
    return "\n".join(lines)
