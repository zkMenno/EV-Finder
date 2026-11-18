"""T-136: count EV catalogue keys in the pulled EEA groups at several granularities."""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

D = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/t136")
rows = [json.loads(line) for p in sorted(D.glob("eea_*.jsonl")) for line in p.open()]

MAKE_ALIASES = {
    "VW": "VOLKSWAGEN", "VOLKSWAGEN VW": "VOLKSWAGEN", "VOLKSWAGEN, VW": "VOLKSWAGEN",
    "TESLA MOTORS": "TESLA", "MERCEDES": "MERCEDES-BENZ", "MERCEDES BENZ": "MERCEDES-BENZ",
    "BMW I": "BMW", "CITROËN": "CITROEN", "ŠKODA": "SKODA", "MG ROEWE": "MG",
    "DS AUTOMOBILES": "DS", "LYNK&CO": "LYNK & CO", "ALFA-ROMEO": "ALFA ROMEO",
}


def mk(s: str | None) -> str:
    s = re.sub(r"\s+", " ", (s or "").upper().strip())
    return MAKE_ALIASES.get(s, s)


def cn(s: str | None) -> str:
    return re.sub(r"[^A-Z0-9+]", "", (s or "").upper())


fill = defaultdict(lambda: [0, 0, 0, 0, 0])
for r in rows:
    f = fill[r["year"]]
    f[0] += r["r"] or 0
    f[1] += (r["r"] or 0) if r["Zr"] else 0
    f[2] += (r["r"] or 0) if r["z"] else 0
    f[3] += (r["r"] or 0) if r["ep"] else 0
    f[4] += (r["r"] or 0) if r["T"] else 0
print("year regs  %Zr %Z %Ep %T")
for y in sorted(fill):
    f = fill[y]
    print(y, f[0], *(round(100 * x / f[0]) for x in f[1:]))

levels = {
    "make+name": lambda r: (mk(r["Mk"]), cn(r["Cn"])),
    "make+type": lambda r: (mk(r["Mk"]), r["T"] or ""),
    "make+type+variant": lambda r: (mk(r["Mk"]), r["T"] or "", r["Va"] or ""),
    "make+type+variant+version": lambda r: (mk(r["Mk"]), r["T"] or "", r["Va"] or "", r["Ve"] or ""),
    # 'spec fingerprint': what a buyer sees as a different car: name, power, range (10 km band)
    "make+name+power+range": lambda r: (mk(r["Mk"]), cn(r["Cn"]), r["ep"], round((r["Zr"] or 0) / 10)),
    "make+name+power+range+year": lambda r: (mk(r["Mk"]), cn(r["Cn"]), r["ep"], round((r["Zr"] or 0) / 10), r["year"]),
}
print()
print("level | keys (any) | keys >=10 regs | >=50 | >=200 | >=1000")
for name, key in levels.items():
    tot: dict = defaultdict(int)
    for r in rows:
        tot[key(r)] += r["r"] or 0
    v = list(tot.values())
    print(name, "|", len(v), "|", *(sum(x >= t for x in v) for t in (10, 50, 200, 1000)))

# makes and model names covering 99% of registrations
tot_mn: dict = defaultdict(int)
for r in rows:
    tot_mn[(mk(r["Mk"]), cn(r["Cn"]))] += r["r"] or 0
allr = sum(tot_mn.values())
acc = 0
for i, (k, v) in enumerate(sorted(tot_mn.items(), key=lambda kv: -kv[1]), 1):
    acc += v
    if acc / allr >= 0.99:
        print("\nmake+name keys covering 99% of EU EV registrations 2010-2025:", i)
        break
makes = defaultdict(int)
for (m, _), v in tot_mn.items():
    makes[m] += v
print("makes >=1000 regs:", sum(v >= 1000 for v in makes.values()), "of", len(makes))
print("total regs:", allr)
