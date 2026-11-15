"""WCAG 2.2 AA contrast check for every text pair in docs/design/tokens.json (Menno's hard rule).

Usage: python3 workstreams/UX/tools/contrast.py   (exit 1 if any text pair fails AA)
Text needs 4.5:1; large text (24px+, or 19px+ bold) and non-text UI 3:1. Both themes.
"""
import json, sys, pathlib
TOK = pathlib.Path(__file__).resolve().parents[3] / "docs/design/tokens.json"
C = {k["name"]: k["value"] for k in json.load(open(TOK))["color"]["tokens"]}
GROUNDS = ["paper", "paper-sea", "surface", "surface-sunk", "sunflower-tint", "meadow-tint", "danger-tint"]  # sea = map fill, no text
TEXT = {g: ["ink", "ink-2", "ink-3"] for g in GROUNDS}
TEXT["paper"] += ["link", "success", "warning", "danger"]
TEXT["paper-sea"] += ["link"]
TEXT["surface"] += ["link", "success", "warning", "danger"]
TEXT["danger-tint"] += ["danger"]
EXTRA = [("on-action", "action"), ("on-action", "action-hover"), ("on-sunflower", "sunflower")]
UI = [("line-strong", "paper"), ("focus", "paper"), ("sky", "paper")]

def val(n, th):
    v = C[n]; v = v[th] if isinstance(v, dict) else v
    return val(v[1:-1], th) if v.startswith("{") else v
def lum(h):
    h = h.lstrip("#"); c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]
def cr(a, b):
    x, y = sorted([lum(a), lum(b)], reverse=True); return (x + .05) / (y + .05)

fails = 0
for th in ("light", "dark"):
    rows = [(f, g, 4.5) for g, fs in TEXT.items() for f in fs] + [(f, g, 4.5) for f, g in EXTRA] + [(f, g, 3.0) for f, g in UI]
    for f, g, need in rows:
        r = cr(val(f, th), val(g, th)); ok = r >= need; fails += not ok
        print(f"{th:5} {f:13} on {g:14} {r:5.1f}:1  {'AAA' if r >= 7 else 'AA ' if ok else 'FAIL'} (need {need})")
print("All pairs pass WCAG AA." if not fails else f"{fails} pair(s) FAIL WCAG AA.")
sys.exit(1 if fails else 0)
