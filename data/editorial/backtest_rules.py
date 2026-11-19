"""Back-test shortlist_rules.yaml against Menno's own verdicts.

Usage: python3 -I data/editorial/backtest_rules.py [--markdown]

Scores every rated row of `primary_car_picks` with the `road-tripper` profile (the only one calibrated on real picks), using the
sheet's own values (internal calibration only), and reports how often the rule band matches his
colour (shortlist / consider / fallback). Unrated rows are scored and listed but not counted.
Exit code 1 if exact agreement falls below MIN_AGREEMENT, so CI notices when a rule edit breaks it.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
MIN_AGREEMENT = 0.60
ORDER = {"fallback": 0, "consider": 1, "shortlist": 2}


def lin(x: float | None, poor: float, great: float) -> float:
    if x is None:
        return 0.5  # unknown = neutral, never a guess
    t = (x - poor) / (great - poor)
    return max(0.0, min(1.0, t))


def one_pedal(notes: str | None) -> float:
    n = (notes or "").lower()
    if re.search(r"no one-pedal|weak regen", n):
        return 0.0
    if re.search(r"one-pedal|i-pedal|xpedal|1-pedal", n):
        return 1.0
    return 0.5


def boolish(v: object) -> float:
    if v is True:
        return 1.0
    if v is False:
        return 0.0
    return 0.5 if v is None else 0.7  # e.g. "10kW DC" = partial


def score(e: dict, prof: dict, newest: set, older: set) -> tuple[float | None, str, list[str]]:
    sv = e["sheet_values"]
    if sv.get("dc_km_per_h") is None and sv.get("range_winter_km") is None:
        return None, "no-data", []
    why: list[str] = []
    for g in prof["gates"]:
        v = sv.get(g["sheet_field"])
        lim = g.get("min_km_per_h", g.get("min_km"))
        if v is not None and v < lim:
            return 0.0, "ruled_out", [g["id"]]
    total = wsum = 0.0
    for f in prof["factors"]:
        fid, w = f["id"], f["weight"]
        if fid == "space":
            boot, frunk = sv.get("boot_l"), sv.get("frunk_l") or 0
            s = lin(None if boot is None else boot + frunk, f["poor"], f["great"])
        elif fid == "one-pedal":
            s = one_pedal(e.get("notes"))
        elif fid == "v2l":
            s = boolish(sv.get("v2l"))
        elif fid == "home-power":
            s = max(boolish(sv.get("v2h")), boolish(sv.get("v2g")))
            s = 0.0 if s == 0.5 and sv.get("v2l") is not None else s
        else:
            s = lin(sv.get(f["sheet_field"]), f["poor"], f["great"])
        total += s * w
        wsum += w
    pts = 100 * total / wsum
    key = line_key(e)
    if key in newest and e["model_year"] == max_year[key]:
        pts += 4
        why.append("newest-version")
    if key in older and e["model_year"] < max_year[key]:
        pts -= 6
        why.append("older-version")
    if (sv.get("chemistry") or "").upper() == "LFP":
        pts += 2
        why.append("lfp")
    if "chubby" in (e.get("notes") or "").lower():
        pts -= 16
        why.append("too-big")
    v = sv.get("voltage_v")
    b = prof["bands"]["800v" if v and v >= 600 else "400v" if v else "default"]
    band = (
        "shortlist" if pts >= b["shortlist"] else "consider" if pts >= b["consider"] else "fallback"
    )
    return round(pts, 1), band, why


max_year: dict[tuple[str, str, str], int] = {}


def line_key(e: dict) -> tuple[str, str, str]:
    """Trim line (Decision 088) as far as the sheet shows it: make + model + drivetrain read from
    the variant name (AWD vs RWD / 2WD). The sheet has no power column, so the pipeline's 15 %
    power split can't be mirrored here; pairs with unknown power stay one line."""
    v = f" {(e.get('variant') or '').lower()} "
    dt = "awd" if " awd" in v or "dual motor" in v else "2wd" if any(t in v for t in (" rwd", " 2wd", " fwd", "single motor")) else "?"
    return (e["make"].lower(), e["model"].lower(), dt)


SCHEMA = HERE.parent.parent / "packages" / "schema" / "schemas" / "ev.schema.json"


def check_structure(rules: dict) -> list[str]:
    """Every field a rule reads exists in PublishedVariant (or is marked a gap); steps name real factors."""
    import json

    known = set(json.loads(SCHEMA.read_text())["$defs"]["PublishedVariant"]["properties"])
    errs: list[str] = []
    factor_ids: set[str] = set()

    def fields(row: dict) -> list[str]:
        f = row.get("field")
        return [] if f is None else ([f] if isinstance(f, str) else list(f))

    groups = [("profile", p) for p in rules["profiles"]] + [("modifier", m) for m in rules.get("modifiers", [])]
    groups += [("addon", a) for a in rules.get("addons", [])]
    for kind, g in groups:
        rows = g.get("gates", []) + g.get("factors", []) + g.get("extra_factors", []) + g.get("penalties", [])
        rows += g.get("bonuses", []) + g.get("filter_presets", [])
        for r in rows:
            if "id" in r and r in g.get("factors", []) + g.get("extra_factors", []):
                factor_ids.add(r["id"])
            if r.get("status") == "gap":
                continue
            for f in fields(r):
                if f not in known:
                    errs.append(f"{kind} {g['id']}: field '{f}' not in PublishedVariant (mark status: gap?)")
    for kind, g in groups:
        for step in g.get("weight_steps") or {}:
            if step not in factor_ids:
                errs.append(f"{kind} {g['id']}: weight step '{step}' names no factor")
    answers = {q["id"]: set(q["answers"]) for q in rules.get("picker", [])}
    for kind, g in groups:
        for q, vals in (g.get("picker") or {}).items():
            bad = set(vals) - answers.get(q, set())
            if bad:
                errs.append(f"{kind} {g['id']}: picker {q} has unknown answers {sorted(bad)}")
    return errs


def main() -> int:
    picks = yaml.safe_load((HERE / "menno-picks.yaml").read_text())["primary_car_picks"]
    rules = yaml.safe_load((HERE / "shortlist_rules.yaml").read_text())
    errs = check_structure(rules)
    for e in errs:
        print("STRUCTURE:", e)
    prof = next(p for p in rules["profiles"] if p["id"] == "road-tripper")
    years = defaultdict(set)
    for e in picks:
        if e["model_year"]:
            years[line_key(e)].add(e["model_year"])
    multi = {k for k, v in years.items() if len(v) > 1}
    max_year.update({k: max(v) for k, v in years.items()})
    rows, hit, near, n = [], 0, 0, 0
    for e in picks:
        pts, band, why = score(e, prof, multi, multi)
        rated = e["verdict"] in ORDER and pts is not None
        if rated:
            n += 1
            hit += band == e["verdict"]
            near += abs(ORDER.get(band, -1) - ORDER[e["verdict"]]) <= 1
        rows.append((e, pts, band, why, rated))
    md = "--markdown" in sys.argv
    if md:
        print("| Car | Menno | Rules | Score | Why |\n|---|---|---|---|---|")
    for e, pts, band, why, rated in sorted(rows, key=lambda r: -(r[1] or -1)):
        name = f"{e['make']} {e['model']} {e['model_year'] or ''} {e['variant'] or ''}".strip()
        mark = "" if not rated else ("✓" if band == e["verdict"] else "✗")
        if md:
            print(
                f"| {name} | {e['verdict']} | {band} {mark} | {pts if pts is not None else '—'} | {', '.join(why)} |"
            )
        else:
            print(f"{mark:1} {str(pts):>5} {band:9} menno={e['verdict']:9} {name}  {' '.join(why)}")
    agree = hit / n if n else 0
    print(
        f"\nRated rows: {n} · exact band match: {hit} ({agree:.0%}) · within one band: {near} ({near / n:.0%})"
    )
    return 0 if agree >= MIN_AGREEMENT and not errs else 1


if __name__ == "__main__":
    sys.exit(main())
