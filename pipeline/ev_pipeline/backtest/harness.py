"""Back-test the real-range ratio model (derive/metrics.py) against condition-tagged tests.

Input: JSON Lines, one measured test per line:
    {"test_id", "variant_id", "generation_id", "make_id", "body", "drivetrain",
     "battery_kwh_net", "wltp_km", "measured_km", "model_year", "condition",
     "source_id", "fixture": bool, "note"}
`condition` tags what the test measured. The ratio model predicts mild-weather mixed driving
(metrics.BODY_RATIOS), so only `MODEL_CONDITION` tests are scored; the others are counted and
reported as "no model for this condition yet".

Method (leave-one-out per variant, R-05 §2): for each scored test, hide every test of that
variant, build the ladder's observations from the remaining variants (mean measured km per
variant), predict with metrics.real_range and compare. Error = (predicted - measured) /
measured. Report: median absolute % error overall, per body type, per brand, per model-year
band and per ladder rung, plus the 10 worst. Gate: median < 10 % (spec Trip fit §5).

In a release (qa.json `backtest`): tests come from data/backtest/*.jsonl; fixture rows and
tests from sources that fail the licence gate are left out (qa.json is published), so tonight
the section is `skipped`. Fixture runs: `python -m ev_pipeline.backtest <file.jsonl>...`.
"""

from __future__ import annotations

import json
import statistics
from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ev_pipeline.derive import metrics as m

MODEL_CONDITION = "mild-mixed"
GATE_MEDIAN_ABS_PCT = 10.0
REGRESSION_POINTS = 3.0  # a model whose median error worsens by more -> review (R-05 §2)
WORST_N = 10


@dataclass
class BackTest:
    test_id: str
    variant_id: str
    generation_id: str
    make_id: str
    body: str | None
    drivetrain: str | None
    battery_kwh_net: float | None
    wltp_km: float | None
    measured_km: float
    condition: str
    source_id: str
    model_id: str = ""
    model_year: int | None = None
    fixture: bool = False
    note: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


_KNOWN = set(BackTest.__dataclass_fields__) - {"extra"}


def parse_test(d: dict[str, Any]) -> BackTest:
    kw = {k: d[k] for k in _KNOWN if k in d}
    kw["measured_km"] = float(kw["measured_km"])
    kw.setdefault("model_id", d.get("generation_id", "").rsplit("-", 1)[0])
    return BackTest(**kw, extra={k: v for k, v in d.items() if k not in _KNOWN})


def load_tests(paths: Iterable[Path]) -> list[BackTest]:
    out: list[BackTest] = []
    for p in sorted(paths):
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(parse_test(json.loads(line)))
    return out


def year_band(year: int | None) -> str:
    return m.era(year) if year else "unknown"


def _ladder_input(t: BackTest) -> m.LadderInput:
    return m.LadderInput(
        variant_id=t.variant_id,
        generation_id=t.generation_id,
        make_id=t.make_id,
        body=t.body,
        drivetrain=t.drivetrain,
        battery_kwh_net=t.battery_kwh_net,
        wltp_km=t.wltp_km,
    )


def _median_abs(errs: list[float]) -> float:
    return round(statistics.median(abs(e) for e in errs), 2)


def _group(results: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    g: dict[str, list[float]] = defaultdict(list)
    for r in results:
        g[str(r[key])].append(r["error_pct"])
    return {k: {"n": len(v), "median_abs_pct": _median_abs(v)} for k, v in sorted(g.items())}


def run_backtest(tests: list[BackTest], condition: str = MODEL_CONDITION) -> dict[str, Any]:
    scored = [t for t in tests if t.condition == condition]
    other: dict[str, int] = defaultdict(int)
    for t in tests:
        if t.condition != condition:
            other[t.condition] += 1
    inputs_by_variant: dict[str, m.LadderInput] = {}
    measured: dict[str, list[float]] = defaultdict(list)
    for t in scored:
        inputs_by_variant.setdefault(t.variant_id, _ladder_input(t))
        measured[t.variant_id].append(t.measured_km)
    inputs = list(inputs_by_variant.values())
    results: list[dict[str, Any]] = []
    unpredictable: list[str] = []
    for t in scored:
        obs = {
            vid: m.RealObservation(statistics.mean(kms), "exact-test", ["backtest"], [], "medium")
            for vid, kms in measured.items()
            if vid != t.variant_id
        }
        pred = m.real_range(inputs_by_variant[t.variant_id], inputs, obs)
        if pred is None:
            unpredictable.append(t.test_id)
            continue
        err = 100 * (pred.km - t.measured_km) / t.measured_km
        results.append(
            {
                "test_id": t.test_id,
                "variant_id": t.variant_id,
                "model_id": t.model_id,
                "make_id": t.make_id,
                "body": t.body or "unknown",
                "year_band": year_band(t.model_year),
                "rung": pred.rung,
                "measured_km": t.measured_km,
                "predicted_km": round(pred.km, 1),
                "error_pct": round(err, 2),
                "source_id": t.source_id,
                "note": pred.note,
            }
        )
    if not results:
        return {
            "status": "skipped",
            "note": f"no '{condition}' tests could be scored",
            "condition": condition,
            "tests": len(tests),
            "other_conditions": dict(other),
            "unpredictable": unpredictable,
        }
    overall = _median_abs([r["error_pct"] for r in results])
    worst = sorted(results, key=lambda r: (-abs(r["error_pct"]), r["test_id"]))[:WORST_N]
    return {
        "status": "pass" if overall < GATE_MEDIAN_ABS_PCT else "flag",
        "condition": condition,
        "method": "leave-one-out per variant over metrics.real_range (ratio ladder)",
        "gate": f"median absolute error < {GATE_MEDIAN_ABS_PCT:g}%",
        "tests": len(tests),
        "scored": len(results),
        "other_conditions": dict(sorted(other.items())),
        "unpredictable": unpredictable,
        "median_abs_pct": overall,
        "mean_signed_pct": round(statistics.mean(r["error_pct"] for r in results), 2),
        "by_body": _group(results, "body"),
        "by_brand": _group(results, "make_id"),
        "by_year_band": _group(results, "year_band"),
        "by_rung": _group(results, "rung"),
        "by_model": _group(results, "model_id"),
        "worst": worst,
    }


def regressions(current: dict[str, Any], previous: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Models whose median error worsened by more than REGRESSION_POINTS (T-035)."""
    prev = (previous or {}).get("by_model") or {}
    out = []
    for mid, c in (current.get("by_model") or {}).items():
        p = prev.get(mid)
        if p and c["median_abs_pct"] - p["median_abs_pct"] > REGRESSION_POINTS:
            out.append(
                {"model_id": mid, "previous": p["median_abs_pct"], "now": c["median_abs_pct"]}
            )
    return out


def release_backtest(
    data_dir: Path,
    releasable: Callable[[str], bool],
    previous: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """The qa.json `backtest` section for a release."""
    folder = data_dir / "backtest"
    paths = sorted(folder.glob("*.jsonl")) if folder.is_dir() else []
    tests = load_tests(paths)
    real = [t for t in tests if not t.fixture]
    usable = [t for t in real if releasable(t.source_id)]
    left_out = {
        "fixture_rows": len(tests) - len(real),
        "not_releasable_source": len(real) - len(usable),
    }
    if not usable:
        return {
            "status": "skipped",
            "note": "no real condition-tagged tests from licence-cleared sources yet "
            "(the measured-test sources are still waiting for permission); harness tested on "
            "fixtures only",
            "inputs": [p.name for p in paths],
            "left_out": left_out,
        }
    out = run_backtest(usable)
    out["inputs"] = [p.name for p in paths]
    out["left_out"] = left_out
    regs = regressions(out, previous)
    out["regressions"] = regs
    if regs and out["status"] == "pass":
        out["status"] = "flag"
    return out
