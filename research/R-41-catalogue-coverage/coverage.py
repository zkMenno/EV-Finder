"""T-136: share of EU BEV registrations (EEA 2010-2025) whose make + name the seed matches,
and the biggest unmatched (make, name) groups. Uses the pipeline's own matcher."""

import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

from ev_pipeline.match.matcher import find_by_source_alias, find_model_noted, match_view
from ev_pipeline.match.seed import load_seed
from ev_pipeline.records import SourceRecord
from ev_pipeline.sources.eea.adapter import SOURCE
from ev_pipeline.schema_models import Country

D = Path(sys.argv[1])
seed = load_seed(Path(sys.argv[2]))
agg: dict[tuple[str, str], int] = defaultdict(int)
by_year: dict[tuple[str, str], set[int]] = defaultdict(set)
for p in sorted(D.glob("eea_*.jsonl")):
    for line in p.open():
        r = json.loads(line)
        if r["Mk"] and r["Cn"]:
            agg[(r["Mk"], r["Cn"])] += r["r"] or 0
            by_year[(r["Mk"], r["Cn"])].add(r["year"])

matched, unmatched_make, unmatched_model = 0, defaultdict(int), defaultdict(int)
models_hit: set[str] = set()
for (mk, cn), n in agg.items():
    rec = SourceRecord(record_key="x", kind="registration_count", source=SOURCE, make=mk, model=cn,
                       year=None, country=Country("NL"), retrieved_at=date(2026, 11, 17), specs={}, confidence="high")
    view = match_view(rec)
    mid = seed.make_id_for(mk, "eea", True)
    if mid is None:
        model, _ = find_by_source_alias(seed, view, True)
        if model is None:
            unmatched_make[mk.upper()] += n
            continue
    else:
        model, why, _ = find_model_noted(seed, mid, view, True)
        if model is None:
            unmatched_model[(mid, cn.upper())] += n
            continue
    matched += n
    models_hit.add(model.id)

tot = sum(agg.values())
print(f"EU BEV registrations 2010-2025: {tot}")
print(f"matched to a seed model: {matched} ({100 * matched / tot:.1f}%), seed models hit: {len(models_hit)}")
um = sum(unmatched_make.values())
print(f"make not in seed: {um} ({100 * um / tot:.1f}%)")
print("top missing makes:", sorted(unmatched_make.items(), key=lambda kv: -kv[1])[:25])
mm = sum(unmatched_model.values())
print(f"make in seed, name not matched: {mm} ({100 * mm / tot:.1f}%)")
print("top missing names:")
for k, v in sorted(unmatched_model.items(), key=lambda kv: -kv[1])[:40]:
    print("  ", k, v)

# Variant gap on models we already have: EEA (make, T, Va) keys vs our variant rows per model.
cat = json.load(open(sys.argv[3]))
gen_model = {g["id"]: g.get("model_id") for g in cat["generations"]}
ours: dict[str, int] = defaultdict(int)
for row in cat["rows"]:
    ours[gen_model.get(row.get("generation_id"))] += 1
mapped: dict[tuple[str, str], str] = {}
for (mk, cn) in agg:
    rec = SourceRecord(record_key="x", kind="registration_count", source=SOURCE, make=mk, model=cn,
                       year=None, country=Country("NL"), retrieved_at=date(2026, 11, 17), specs={},
                       confidence="high")
    mid = seed.make_id_for(mk, "eea", True)
    model = find_model_noted(seed, mid, match_view(rec), True)[0] if mid else find_by_source_alias(seed, match_view(rec), True)[0]
    if model:
        mapped[(mk, cn)] = model.id
tva: dict[str, dict[tuple, int]] = defaultdict(lambda: defaultdict(int))
for p in sorted(D.glob("eea_*.jsonl")):
    for line in p.open():
        r = json.loads(line)
        m = mapped.get((r["Mk"], r["Cn"]))
        if m:
            tva[m][(r["T"], r["Va"])] += r["r"] or 0
print("\nper matched model: EEA type+variant keys (>=50 / >=200 regs) vs our variant rows")
s50 = s200 = so = 0
for m in sorted(tva, key=lambda m: -sum(tva[m].values())):
    a = sum(v >= 50 for v in tva[m].values()); b = sum(v >= 200 for v in tva[m].values())
    s50 += a; s200 += b; so += ours.get(m, 0)
print("totals: EEA>=50", s50, "EEA>=200", s200, "ours", so, "models", len(tva))
for m in sorted(tva, key=lambda m: -sum(tva[m].values()))[:12]:
    print("  ", m, sum(v >= 50 for v in tva[m].values()), sum(v >= 200 for v in tva[m].values()), ours.get(m, 0))

# Buyer-variant proxy on matched models: (model, power kW) and (model, power, range in 50 km bands)
pe: dict[tuple, int] = defaultdict(int); per: dict[tuple, int] = defaultdict(int); pery: dict[tuple, int] = defaultdict(int)
for p in sorted(D.glob("eea_*.jsonl")):
    for line in p.open():
        r = json.loads(line)
        m = mapped.get((r["Mk"], r["Cn"]))
        if m and r["ep"]:
            pe[(m, r["ep"])] += r["r"] or 0
            per[(m, r["ep"], round((r["Zr"] or 0) / 50))] += r["r"] or 0
            pery[(m, r["ep"], r["year"])] += r["r"] or 0
for name, d in (("model+power", pe), ("model+power+range50", per), ("model+power+year", pery)):
    print(name, ">=50:", sum(v >= 50 for v in d.values()), ">=200:", sum(v >= 200 for v in d.values()))
for m in ("tesla-model-3", "peugeot-e-208", "volkswagen-id3", "renault-zoe", "dacia-spring"):
    print(m, sorted((k[1], v) for k, v in pe.items() if k[0] == m and v >= 200))

# Scale: (make, type) keys >=200 regs, matched models vs everything
tall: dict[tuple, int] = defaultdict(int); tm: dict[tuple, int] = defaultdict(int)
mall: dict[tuple, int] = defaultdict(int); mm_: dict[tuple, int] = defaultdict(int)
for p in sorted(D.glob("eea_*.jsonl")):
    for line in p.open():
        r = json.loads(line)
        k = ((r["Mk"] or "").upper(), r["T"])
        tall[k] += r["r"] or 0
        if (r["Mk"], r["Cn"]) in mapped:
            tm[k] += r["r"] or 0
        if r["ep"]:
            mall[((r["Mk"] or "").upper(), r["T"], r["ep"])] += r["r"] or 0
for t in (50, 200):
    a = sum(v >= t for v in tall.values()); b = sum(v >= t for k, v in tall.items() if tm.get(k, 0) >= v / 2)
    c = sum(v >= t for v in mall.values())
    print(f"make+type >= {t}: all {a}, mostly matched models {b}; make+type+power all {c}")
