"""Candidate variants from RDW TGK type-approval versions (T-073, R-41 task 1, Decision 049).

A type-approval version (TAN|variant|uitvoering) is one stated build of a car. We already
place each version on a seed variant when exactly one fits (match/matcher.py `tgk_pick`).
This step looks at **every** version of every seed generation, groups them by a spec
fingerprint, and says for each group whether it is a variant we have, one we are missing, or
several of ours at once. Nothing here reaches a release: the output is a review queue
(`data/review/variant-candidates.csv`) that WS3 turns into seed variants, plus a coverage
count (`data/review/variant-coverage.json`).

**Fingerprint** (R-08 plan D, "by spec, not by name"), per generation:

1. Cycle: WLTP when the version has a WLTP range + consumption pair, else NEDC.
2. Motors: "single" when TGK states a 30-minute power, "multi" when it does not (TGK leaves
   it out on multi-motor versions; a missing value is not guessed). The exact 30-minute
   power is listed, not split on: makers file one battery and motor under many values
   (Tesla Model Y RWD 455 km: 88 / 90 / 100 / 120 / 125 / 127 kW on the 2026-11-18 data).
3. Energy drawn on the test (range x consumption / 100, the matcher's battery proxy):
   sorted, split where a version is more than ENERGY_GAP above the next lower version, i.e.
   at a gap in the values. Packs differ clearly (Zoe 22 vs 41 kWh, ID.3 58 vs 77 kWh),
   while one pack's wheels and trims spread densely (Mach-E 91 kWh: 99-109 kWh drawn). A
   "within x % of the lowest" rule was tried first and cut such dense runs at arbitrary
   points (2026-11-18 dry run: 2, 3 and 4 % gaps and the 8 % lowest rule gave 93-104
   candidate groups; 4 % kept the fewest arbitrary cuts).

**Verdict of a group:**

- `have`: the versions the matcher placed all sit on one seed variant.
- `several`: placed versions sit on 2+ seed variants (the fingerprint can't split them, or
  the seed holds two names for one build): review whether the seed rows differ.
- `tie`: nothing placed, and the matcher found several seed variants that fit (named in
  `seed_variants`): the variant exists, the evidence to choose is missing.
- `no-fit`: nothing placed and no seed variant of the generation fits. Either a variant we
  lack, or a seed variant with a wrong battery figure (e.g. OpenEV gives the ID.7 Pro the
  Pro S's 86 kWh, so the 77 kWh Pro versions fit nothing): the reviewer decides.
- `no-variant`: the generation has no variant at all yet (new seed generations, T-068).

`no-fit` and `no-variant` groups are the candidate variants.

**EEA (counts only, Decision 049):** EU registrations per TAN base|Va|Ve
(sources/eea/versions.py), shared evenly over the TGK records with that key, summed per
group: `eu_cars > 0` corroborates that the build was sold in the EU. Coverage "% of EU
registrations" = EU cars on versions of seed generations / all EU BEV registrations in the
years read.

Every group cites its TGK record keys (`record_keys`, up to MAX_KEYS, plus the count).
"""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ev_pipeline.match.matcher import (
    MatchResult,
    find_by_source_alias,
    find_generation,
    find_model_noted,
    tgk_energies,
)
from ev_pipeline.match.seed import Seed
from ev_pipeline.records import SourceRecord
from ev_pipeline.schema_models import FactField
from ev_pipeline.sources.eea.versions import EeaVersionCounts, version_key

SOURCE_ID = "rdw-tgk"
TIE_MARK = "several variants fit"  # matcher.TGK_TIE
_IDS_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)+")
_IN_GEN_RE = re.compile(r" in [a-z0-9]+(?:-[a-z0-9]+)+(?: \(\d+x\))?$")
ENERGY_GAP = 0.04
"""Split where a version's energy drawn is more than 4 % above the next lower one (a gap)."""
MAX_KEYS = 5
CSV_NAME = "variant-candidates.csv"
COVERAGE_NAME = "variant-coverage.json"
COLUMNS = (
    "record_key",
    "source_id",
    "verdict",
    "generation_id",
    "seed_variants",
    "cycle",
    "motors",
    "power_30min_kw",
    "energy_kwh",
    "range_km",
    "years",
    "versions",
    "nl_cars",
    "eu_cars",
    "trade_names",
    "record_keys",
    "reason",
)


def tgk_key(record_key: str) -> tuple[str, str, str] | None:
    """`gr7t...[...]:<TAN>|<variant>|<uitvoering>|<rev>` -> (TAN, variant, uitvoering)."""
    _, _, tail = record_key.rpartition("]:")
    parts = tail.split("|")
    return (parts[0], parts[1], parts[2]) if len(parts) >= 3 else None


def _num(rec: SourceRecord, f: str) -> float | None:
    sv = rec.specs.get(FactField(f))
    if sv is None or isinstance(sv.value, bool) or not isinstance(sv.value, int | float):
        return None
    return float(sv.value)


@dataclass
class Version:
    rec: SourceRecord
    generation_id: str
    placed: str | None  # seed variant id the matcher placed this version on
    unplaced_reason: str
    cycle: str
    power: float | None
    energy: float | None
    range_km: float | None
    tied: frozenset[str]  # seed variants the matcher's tie reason names (known ids only)
    nl_cars: int
    eu_cars: float  # this version's share of its EEA key's registrations (see place_versions)

    @property
    def trade(self) -> str:
        return (self.rec.variant_name or self.rec.model or "").split(" · ")[0].strip()


@dataclass
class Group:
    generation_id: str
    cycle: str
    motors: str
    generation_has_variants: (
        bool  # "single" (30-min power stated) | "multi" (not stated: multi-motor or unknown)
    )
    members: list[Version] = field(default_factory=list)
    split_by: str = ""  # T-159: the seed variant a split-evidence subgroup is placed on

    @property
    def placed(self) -> Counter[str]:
        return Counter(v.placed for v in self.members if v.placed)

    @property
    def tied(self) -> set[str]:
        """Seed variants named in the matcher's tie reasons of the unplaced members."""
        return {t for v in self.members if not v.placed for t in v.tied}

    @property
    def verdict(self) -> str:
        p = self.placed
        if len(p) == 1:
            return "have"
        if p:
            return "several"
        if self.tied:
            return "tie"
        return "no-fit" if self.generation_has_variants else "no-variant"

    def _span(self, vals: Iterable[float | None]) -> str:
        xs = sorted(x for x in vals if x is not None)
        if not xs:
            return ""
        lo, hi = round(xs[0], 1), round(xs[-1], 1)
        return f"{lo:g}" if lo == hi else f"{lo:g}-{hi:g}"

    @property
    def key(self) -> str:
        e = self._span(v.energy for v in self.members) or "unknown"
        key = f"{self.generation_id}|{self.cycle}|{self.motors}|e={e}"
        return f"{key}|v={self.split_by}" if self.split_by else key

    def row(self) -> dict[str, str]:
        years = sorted(v.rec.year for v in self.members if v.rec.year is not None)
        trades = Counter(v.trade for v in self.members if v.trade)
        reasons = Counter(_short_reason(v.unplaced_reason) for v in self.members if not v.placed)
        keys = sorted(v.rec.record_key for v in self.members)
        return {
            "record_key": self.key,
            "source_id": SOURCE_ID,
            "verdict": self.verdict,
            "generation_id": self.generation_id,
            "seed_variants": ", ".join(sorted(self.placed) or sorted(self.tied)),
            "cycle": self.cycle,
            "motors": self.motors,
            "power_30min_kw": self._span(v.power for v in self.members),
            "energy_kwh": self._span(v.energy for v in self.members),
            "range_km": self._span(v.range_km for v in self.members),
            "years": f"{years[0]}-{years[-1]}" if years else "",
            "versions": str(len(self.members)),
            "nl_cars": str(sum(v.nl_cars for v in self.members)),
            "eu_cars": str(round(sum(v.eu_cars for v in self.members))),
            "trade_names": "; ".join(t for t, _ in trades.most_common(3)),
            "record_keys": " ".join(keys[:MAX_KEYS])
            + (f" (+{len(keys) - MAX_KEYS})" if len(keys) > MAX_KEYS else ""),
            "reason": "; ".join(f"{r} ({n}x)" for r, n in reasons.most_common(3)),
        }


def _short_reason(reason: str) -> str:
    """The matcher's reason without prefix, generation id and per-record detail."""
    r = reason.removeprefix("attach-only: ")
    r = _IN_GEN_RE.sub("", r)
    if r.startswith("tgk"):
        r = (
            r.split(" (")[0].split(": ")[0]
            if not r.startswith("tgk: ")
            else ("tgk: " + r[5:].split(" (")[0].split(": ")[0])
        )
    return r[:80]


def fingerprint(rec: SourceRecord) -> tuple[str, float | None, float | None]:
    """(cycle, energy drawn kWh, best-case range km) of one TGK version."""
    wr, wc = _num(rec, "wltp_range_km"), _num(rec, "consumption_kwh_100km")
    if wr and wc:
        return "wltp", round(wr * wc / 100, 1), wr
    nr, nc = _num(rec, "nedc_range_km"), _num(rec, "nedc_consumption_kwh_100km")
    if nr and nc:
        return "nedc", round(nr * nc / 100, 1), nr
    e = tgk_energies(rec)
    return ("wltp" if wr else "nedc" if nr else "none"), (e[0] if e else None), wr or nr


def split_by_energy(members: list[Version], gap: float = ENERGY_GAP) -> list[list[Version]]:
    """Sorted by energy drawn, split at every gap of more than `gap` between neighbours;
    versions without an energy figure form their own group."""
    known = sorted((v for v in members if v.energy is not None), key=lambda v: v.energy or 0)
    out: list[list[Version]] = []
    for v in known:
        if out and (v.energy or 0) <= (out[-1][-1].energy or 0) * (1 + gap):
            out[-1].append(v)
        else:
            out.append([v])
    unknown = [v for v in members if v.energy is None]
    if unknown:
        out.append(unknown)
    return out


@dataclass
class Proposal:
    groups: list[Group]
    versions: list[Version]
    no_model: Counter[tuple[str, str]]  # (make, model) -> versions with no seed model
    no_generation: Counter[str]  # reason -> versions
    eea: EeaVersionCounts | None

    def rows(self) -> list[dict[str, str]]:
        order = {"no-variant": 0, "no-fit": 1, "tie": 2, "several": 3, "have": 4}
        gs = sorted(
            self.groups,
            key=lambda g: (order[g.verdict], -sum(v.eu_cars + v.nl_cars for v in g.members), g.key),
        )
        return [g.row() for g in gs]


def place_versions(
    records: list[SourceRecord],
    seed: Seed,
    result: MatchResult,
    nl_cars: dict[tuple[str, str, str], int],
    eea: EeaVersionCounts | None,
) -> Proposal:
    """Every TGK record -> its generation and fingerprint; groups per generation."""
    placed: dict[str, str] = {}
    for mf in result.spec_facts:
        if mf.source_id == SOURCE_ID and mf.fact.source_record:
            placed[mf.fact.source_record] = str(mf.fact.subject_id.root)
    reasons = {u.record_key: u.reason for u in result.unmatched if u.source_id == SOURCE_ID}
    gen_of_variant = {vid: info.generation_id for vid, info in result.variants.items()}

    versions: list[Version] = []
    no_model: Counter[tuple[str, str]] = Counter()
    no_gen: Counter[str] = Counter()
    for rec in records:
        if rec.source.id.root != SOURCE_ID:
            continue
        vid = placed.get(rec.record_key)
        gid = gen_of_variant.get(vid) if vid else None
        if gid is None:
            make_id = seed.make_id_for(rec.make, SOURCE_ID, scoped=result.scoped_aliases)
            model = (
                find_model_noted(seed, make_id, rec, result.scoped_aliases)[0] if make_id else None
            )
            if model is None:
                no_model[(rec.make, rec.model)] += 1
                continue
            gen, why = find_generation(model, rec.year)
            if gen is None:
                no_gen[why.split(" of ")[0][:50]] += 1
                continue
            gid = gen.id
        k = tgk_key(rec.record_key)
        cycle, energy, rng = fingerprint(rec)
        versions.append(
            Version(
                rec=rec,
                generation_id=gid,
                placed=vid,
                unplaced_reason=reasons.get(rec.record_key, "" if vid else "not placed"),
                tied=frozenset(
                    t
                    for t in _IDS_RE.findall(reasons.get(rec.record_key, "").split(" in ")[0])
                    if t in result.variants
                )
                if TIE_MARK in reasons.get(rec.record_key, "")
                else frozenset(),
                cycle=cycle,
                power=_num(rec, "power_30min_kw"),
                energy=energy,
                range_km=rng,
                nl_cars=nl_cars.get(k, 0) if k else 0,
                eu_cars=0.0,
            )
        )
    # One EEA key (TAN base|Va|Ve) can sit behind several TGK records (approval extensions,
    # NL-only uitvoering splits): its registrations are shared out evenly, never counted twice.
    if eea is not None:
        share: dict[tuple[str, str, str], list[Version]] = {}
        for v in versions:
            k = tgk_key(v.rec.record_key)
            if k is not None:
                share.setdefault(version_key(*k), []).append(v)
        for ek, vs in share.items():
            n = eea.by_version.get(ek, 0)
            for v in vs:
                v.eu_cars = n / len(vs)
    by_fp: dict[tuple[str, str, str], list[Version]] = {}
    for v in versions:
        motors = "single" if v.power is not None else "multi"
        by_fp.setdefault((v.generation_id, v.cycle, motors), []).append(v)
    gens_with_variants = set(gen_of_variant.values())
    groups = []
    for (gid, cycle, motors), members in sorted(by_fp.items()):
        for part in split_by_energy(members):
            for sub, by in split_by_evidence(part, result):
                groups.append(Group(gid, cycle, motors, gid in gens_with_variants, sub, by))
    return Proposal(groups, versions, no_model, no_gen, eea)


def split_by_evidence(part: list[Version], result: MatchResult) -> list[tuple[list[Version], str]]:
    """T-159 (T-153 follow-up 6): a fingerprint group whose placed versions sit on 2+ seed
    variants, each of which has split evidence (match/tgk_split.yaml: type code, 30-min power,
    top speed, motors), is the same pack in trims the fingerprint can't see: one subgroup per
    variant (`have`), the unplaced members in one more subgroup (their own verdict). Any
    placed variant without split evidence: the group stays whole (`several`, for review)."""
    placed = sorted({v.placed for v in part if v.placed})
    if len(placed) < 2 or not all(result.tgk_split.get(_root(vid, result)) for vid in placed):
        return [(part, "")]
    out = [([v for v in part if v.placed == vid], vid) for vid in placed]
    rest = [v for v in part if not v.placed]
    if rest:
        out.append((rest, "unplaced"))
    return out


def _root(vid: str, result: MatchResult) -> str:
    """The candidate root of a year band (split evidence is keyed on the root variant)."""
    for b in result.year_bands:
        if vid in b["new_ids"]:  # type: ignore[operator]
            return str(b["variant_id"])
    return vid


def coverage(p: Proposal, seed: Seed, published_variants: int | None) -> dict[str, Any]:
    """Counts for the PR body (Decision 048): models / generations / variants / % EU."""
    st = Counter(g.verdict for g in p.groups)
    gens_with = {v.generation_id for v in p.versions}
    out: dict[str, Any] = {
        "seed_models": len(seed.models),
        "seed_generations": len(seed.generations),
        "published_variants": published_variants,
        "tgk_versions_in_seed_generations": len(p.versions),
        "tgk_versions_model_not_in_seed": sum(p.no_model.values()),
        "tgk_versions_year_outside_generations": sum(p.no_generation.values()),
        "generations_with_tgk_versions": len(gens_with),
        "fingerprint_groups": len(p.groups),
        "groups_have": st["have"],
        "groups_several": st["several"],
        "groups_tie": st["tie"],
        "groups_no_fit": st["no-fit"],
        "groups_no_variant": st["no-variant"],
        "candidate_groups": st["no-fit"] + st["no-variant"],
        "variants_if_candidates_added": (published_variants or 0) + st["no-fit"] + st["no-variant"],
    }
    if p.eea is not None and p.eea.total:
        in_seed = round(sum(v.eu_cars for v in p.versions))
        have = round(
            sum(v.eu_cars for g in p.groups if g.verdict in ("have", "several") for v in g.members)
        )
        out["eea"] = {
            "years": f"{p.eea.years[0]}-{p.eea.years[-1]}" if p.eea.years else "",
            "eu_bev_registrations": p.eea.total,
            "eu_cars_on_tgk_versions_of_seed_generations": in_seed,
            "pct_eu_registrations_seed_generations_via_tgk": round(100 * in_seed / p.eea.total, 1),
            "pct_eu_registrations_on_groups_we_have": round(100 * have / p.eea.total, 1),
            "candidate_groups_sold_in_eu": sum(
                1
                for g in p.groups
                if g.verdict in ("no-fit", "no-variant") and any(v.eu_cars for v in g.members)
            ),
        }
    out["top_models_not_in_seed"] = [
        {"make": mk, "model": md, "versions": n} for (mk, md), n in p.no_model.most_common(25)
    ]
    return out


def model_coverage(
    seed: Seed, eea: EeaVersionCounts, scoped: bool = True, top: int = 60
) -> dict[str, Any]:
    """% of EU BEV registrations whose EEA make + commercial name the seed matcher places on
    a seed model (EEA's own aliases, `aliases_by_source: eea`), as `ev release` would.

    Base: registrations with a commercial name (blank names can't be placed by anyone).
    Returns the share, the counts and the biggest unplaced names (the gap list)."""
    from datetime import date

    from ev_pipeline.sources.eea.adapter import SOURCE as EEA_SOURCE

    today = date.today()
    matched = base = 0
    by_model: Counter[str] = Counter()
    gaps: Counter[tuple[str, str, str]] = Counter()
    for (mk, cn), n in eea.by_name.items():
        if not cn:
            continue
        base += n
        rec = SourceRecord(
            source=EEA_SOURCE,
            record_key=f"coverage:{mk}|{cn}",
            kind="registration_count",
            make=mk or "?",
            model=cn,
            retrieved_at=today,
            confidence="high",
        )
        make_id = seed.make_id_for(mk, EEA_SOURCE.id.root, scoped=scoped)
        model, why = None, "make not in seed"
        if make_id:
            model, why, _ = find_model_noted(seed, make_id, rec, scoped)
        if model is None:
            hit, _ = find_by_source_alias(seed, rec, scoped)
            if hit is not None:
                model, why = hit, ""
        if model is None:
            gaps[(mk, cn, why.split(" (")[0])] += n
            continue
        matched += n
        by_model[model.id] += n
    return {
        "base_registrations_with_a_name": base,
        "matched_to_a_seed_model": matched,
        "pct_eu_registrations_model_level": round(100 * matched / base, 1) if base else None,
        "seed_models_with_eu_registrations": len(by_model),
        "seed_models_without_eu_registrations": sorted(set(seed.models) - set(by_model)),
        "biggest_unmatched": [
            {"make": mk, "name": cn, "reason": why, "registrations": n}
            for (mk, cn, why), n in gaps.most_common(top)
        ],
    }


def load_nl_cars(versions_json: Path) -> dict[tuple[str, str, str], int]:
    """NL plates per (TAN, variant, uitvoering) from the TGK raw `versions.json` (counts)."""
    out: dict[tuple[str, str, str], int] = {}
    if not versions_json.exists():
        return out
    for r in json.loads(versions_json.read_text(encoding="utf-8")):
        k = (
            str(r.get("typegoedkeuringsnummer") or "").strip(),
            str(r.get("variant") or "").strip(),
            str(r.get("uitvoering") or "").strip(),
        )
        out[k] = out.get(k, 0) + int(r.get("n") or 0)
    return out
