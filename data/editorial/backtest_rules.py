"""Back-test shortlist_rules.yaml against Menno's own verdicts.

Usage: python3 -I data/editorial/backtest_rules.py [--markdown]

Scores every rated row of `primary_car_picks` with the `only-car-long-trips` profile, using the
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
    key = (e["make"].lower(), e["model"].lower())
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


max_year: dict[tuple[str, str], int] = {}


def main() -> int:
    picks = yaml.safe_load((HERE / "menno-picks.yaml").read_text())["primary_car_picks"]
    rules = yaml.safe_load((HERE / "shortlist_rules.yaml").read_text())
    prof = next(p for p in rules["profiles"] if p["id"] == "only-car-long-trips")
    years = defaultdict(set)
    for e in picks:
        if e["model_year"]:
            years[(e["make"].lower(), e["model"].lower())].add(e["model_year"])
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
    return 0 if agree >= MIN_AGREEMENT else 1


if __name__ == "__main__":
    sys.exit(main())
