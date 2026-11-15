"""START §3 item 6: quality of the fields the usage profiles lean on (qa.json `profile_fields`).

Report only, never blocks. Per field: coverage, how the value was made (rung, curve status,
agreeing sources), the licence-clean proxy error where one exists (EPA, T-035), and whether the
catalogue figure agrees with the calibrated consumption matrix (T-033). The catalogue's
`real_range_km` and `dc_km_per_20min` are computed in derive/metrics.py with their own
provisional ratios; the matrix was calibrated later. Where the two disagree, the shortlist (which
reads the matrix for winter) and the catalogue tell a user different stories.

What no check here can show: the winter temperature step. Winter cells = 20 °C reference x the
heating and traction model in consumption_params.yaml; validating it needs winter road tests
(Nyland / El Prix, Q-059).
"""

from __future__ import annotations

import statistics
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

CONFIG_FILE = Path(__file__).with_name("profile_fields.yaml")
WORST_N = 5


def load_config(path: Path = CONFIG_FILE) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _cells(m: dict[str, Any], tb: str, cfg: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """road band -> cell for one temperature band, picking the heater row by preference
    (heat_pump option -> the worst row)."""
    rows = [c for c in m.get("cells") or [] if c.get("temperature_band_id") == tb]
    heaters = {c.get("heater_type_id") for c in rows}
    pick: str | None = None
    if len(heaters) > 1:
        prefs = list(cfg["heater_preference"])
        if m.get("heat_pump") == "option":
            prefs = prefs[::-1]
        pick = next((h for h in prefs if h in heaters), None)
    return {c["road_band"]: c for c in rows if pick is None or c.get("heater_type_id") == pick}


def _blend(cells: dict[str, dict[str, Any]], mix: dict[str, float]) -> float | None:
    if not all(b in cells for b in mix):
        return None
    return sum(float(cells[b]["wh_km"]) * w for b, w in mix.items()) / sum(mix.values())


def matrix_view(m: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    kwh = m.get("usable_kwh")
    winter = _cells(m, cfg["winter_temperature_band"], cfg)
    mild = _cells(m, cfg["mild_temperature_band"], cfg)
    out: dict[str, Any] = {
        "rungs": sorted({str(c.get("rung")) for c in winter.values()}),
        "heater": next(iter({c.get("heater_type_id") for c in winter.values()}), None),
    }
    for name, cells in (("winter", winter), ("mild", mild)):
        wh = _blend(cells, cfg["road_mix"])
        out[f"{name}_range_km"] = round(float(kwh) * 1000 / wh) if kwh and wh else None
    out["motorway_mild_wh_km"] = (mild.get("motorway") or {}).get("wh_km")
    return out


def _ratio_report(pairs: list[tuple[str, float]], tol: float) -> dict[str, Any]:
    if not pairs:
        return {"n": 0}
    vals = [r for _, r in pairs]
    q = statistics.quantiles(vals, n=10) if len(vals) >= 2 else [vals[0]] * 9
    return {
        "n": len(vals),
        "ratio_p10": round(q[0], 3),
        "ratio_median": round(statistics.median(vals), 3),
        "ratio_p90": round(q[8], 3),
        "outside_tolerance": sum(abs(r - 1) > tol for r in vals),
        "tolerance": tol,
        "worst": [
            {"variant_id": v, "ratio": round(r, 3)}
            for v, r in sorted(pairs, key=lambda p: (-abs(p[1] - 1), p[0]))[:WORST_N]
        ],
    }


def _provenance(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
    c: Counter[str] = Counter()
    for r in rows:
        p = (r.get("provenance") or {}).get(field)
        if r.get(field) is None or p is None:
            c["missing"] += 1
        elif p.get("estimate"):
            c["estimate"] += 1
        elif p.get("agreeing_sources", 1) >= 2:
            c["2+ agreeing sources"] += 1
        else:
            c["1 source"] += 1
    return dict(sorted(c.items()))


def _epa(bt: dict[str, Any] | None, part: str) -> dict[str, Any] | None:
    r = (bt or {}).get(part) or {}
    if r.get("status") in (None, "skipped"):
        return None
    return {k: r[k] for k in ("n", "median_abs_pct", "mean_signed_pct", "status")}


def profile_fields_section(
    catalogue: dict[str, Any],
    matrix: dict[str, Any] | None,
    backtest_epa: dict[str, Any] | None,
    cfg: dict[str, Any] | None = None,
) -> dict[str, Any]:
    cfg = cfg or load_config()
    rows = catalogue.get("rows") or []
    n = len(rows)
    views = {
        str(m["variant_id"]): matrix_view(m, cfg) for m in (matrix or {}).get("variants") or []
    }
    tol = float(cfg["consistency_tolerance"])
    range_pairs, dc_pairs = [], []
    for r in rows:
        v = views.get(str(r["variant_id"]))
        if not v:
            continue
        if r.get("real_range_km") and v.get("mild_range_km"):
            range_pairs.append((r["variant_id"], float(r["real_range_km"]) / v["mild_range_km"]))
        dc, avg, kwh = r.get("dc_km_per_20min"), r.get("dc_avg_10_80_kw"), r.get("battery_kwh_net")
        if dc and avg and kwh and v.get("motorway_mild_wh_km"):
            implied = min(float(avg) * 20 / 60, float(kwh) * 0.7) * 1000 / float(dc)
            dc_pairs.append((r["variant_id"], implied / float(v["motorway_mild_wh_km"])))
    winter = [v for v in views.values() if v.get("winter_range_km")]
    return {
        "note": "Report only. Ratios compare the catalogue figure with the calibrated consumption"
        " matrix (1.0 = same). The winter temperature step is unvalidated (needs winter road"
        " tests, Q-059).",
        "definitions": {
            k: cfg[k] for k in ("winter_temperature_band", "mild_temperature_band", "road_mix")
        },  # fmt: skip
        "variants": n,
        "winter_range_km": {
            "coverage": len(winter),
            "rungs": dict(Counter("+".join(v["rungs"]) for v in winter).most_common()),
            "heater": dict(Counter(str(v["heater"]) for v in winter).most_common()),
            "proxy_20c_consumption": _epa(backtest_epa, "consumption_oos"),
            "unvalidated": "temperature step (heating, traction) from consumption_params.yaml",
        },
        "real_range_km": {
            "coverage": sum(1 for r in rows if r.get("real_range_km")),
            "rungs": dict(
                Counter(
                    str(r.get("real_range_rung")) for r in rows if r.get("real_range_km")
                ).most_common()
            ),  # fmt: skip
            "proxy_epa_range": _epa(backtest_epa, "range"),
            "vs_matrix_mild_range": _ratio_report(range_pairs, tol),
        },
        "dc_km_per_20min": {
            "coverage": sum(1 for r in rows if r.get("dc_km_per_20min")),
            "curve_status": dict(
                Counter(
                    str(r.get("dc_curve_status")) for r in rows if r.get("dc_km_per_20min")
                ).most_common()
            ),  # fmt: skip
            "dc_avg_10_80_kw": _provenance(rows, "dc_avg_10_80_kw"),
            "proxy": None,
            "proxy_note": "No licence-clean charging test yet (Nyland / El Prix, Q-059).",
            "consumption_vs_matrix_motorway": _ratio_report(dc_pairs, tol),
        },
        "consumption_kwh_100km": {
            "coverage": sum(1 for r in rows if r.get("consumption_kwh_100km")),
            "provenance": _provenance(rows, "consumption_kwh_100km"),
            "proxy_epa_in_sample": _epa(backtest_epa, "consumption"),
            "proxy_epa_out_of_sample": _epa(backtest_epa, "consumption_oos"),
        },
    }


def profile_fields_md(sec: dict[str, Any] | None) -> list[str]:
    if not sec:
        return []
    w, rr, dc = sec["winter_range_km"], sec["real_range_km"], sec["dc_km_per_20min"]
    cons = sec["consumption_kwh_100km"]

    def ratio(x: dict[str, Any]) -> str:
        if not x.get("n"):
            return "no pairs"
        return (
            f"median {x['ratio_median']} (P10 {x['ratio_p10']}, P90 {x['ratio_p90']}),"
            f" {x['outside_tolerance']} of {x['n']} differ by more than"
            f" {100 * x['tolerance']:.0f} %"
        )

    def epa(x: dict[str, Any] | None) -> str:
        return "no data" if not x else f"{x['median_abs_pct']} % median abs error (n {x['n']})"

    n = sec["variants"] or 1
    return [
        "",
        "## Profile fields (winter range, real range, DC km in 20 min)",
        "",
        sec["note"],
        "",
        f"- **Winter range** (matrix, {sec['definitions']['winter_temperature_band']}):"
        f" {w['coverage']} of {n} variants; 20 °C consumption out of sample:"
        f" {epa(w['proxy_20c_consumption'])}; the temperature step is not validated.",
        f"- **Real range** (catalogue): {rr['coverage']} variants; vs EPA:"
        f" {epa(rr['proxy_epa_range'])}; vs matrix mild range:"
        f" {ratio(rr['vs_matrix_mild_range'])}.",
        f"- **DC km in 20 min** (catalogue): {dc['coverage']} variants; curves "
        + ", ".join(f"{k} {v}" for k, v in dc["curve_status"].items())
        + "; its motorway consumption vs the matrix:"
        f" {ratio(dc['consumption_vs_matrix_motorway'])}. No licence-clean charging test yet.",
        f"- **WLTP consumption**: {cons['coverage']} variants; EPA in sample"
        f" {epa(cons['proxy_epa_in_sample'])}, out of sample"
        f" {epa(cons['proxy_epa_out_of_sample'])}.",
    ]
