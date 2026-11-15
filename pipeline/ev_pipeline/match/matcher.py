"""Rules-first matching of SourceRecords to seed models, generations and variants (T-005).

1. Make: normalised key of the record's make against seed make names/ids (+ MAKE_ALIASES).
2. Model: the longest token prefix of the record's model name (with or without a leading
   make name) that equals a seed model name or one of its `name_aliases`. A tie between two
   seed models is ambiguous and goes to review. Two seed-level guards (T-005 review):
   - `name_excludes`: a model never matches a record whose name contains one of these phrases
     as whole tokens ("e-tron GT" is not an "e-tron"); a shorter, non-excluded match may still
     win, otherwise the record goes to review.
   - `bev_only_aliases`: bare trade names ("KONA", "208", "CORSA") that mean the electric model
     only in sources holding nothing but BEVs (BEV_FILTERED_SOURCES: RDW is BEV-proxy-filtered,
     EEA is filtered on Ft = electric). Whole-name match only, never a prefix, so "GOLF GTI"
     or "500 1.4 16V" never ride on them.
3. Generation: the record's year within [start, end] (end null = open). When two generations
   share a year (a facelift or overlap year), evidence decides (T-005 review, supersedes the
   plain "newer wins" of Q-014):
   a. a generation whose known variant names equal the record's variant name, or whose known
      battery sizes (variant kWh, pack kWh, kWh in variant names) are within 1 kWh of a kWh
      figure in the record ("NISSAN LEAF 40KWH", battery_kwh_net 39) is preferred;
      evidence for several generations -> the newest of those;
   b. no evidence -> the newer generation, unless two or more of the candidate generations
      already have variants: then it is a guess, and the record goes to review with reason
      `ambiguous-generation`.
   Known variants/batteries come from a pre-pass over seed-manual variants and records whose
   year falls in exactly one generation. A record without a year only matches a model with
   exactly one generation.
4. Variant (spec records): `<generation_id>-<slug(variant_name or 'base')>`. Records of one
   source with the same normalised variant name in one generation share a variant, whatever
   their year; years seen become the variant's year span. A seed-manual variant with the same
   normalised name in the same generation lends its id, so the two merge.
   Year bands (`split_year_bands`): when a variant's records for a later model year differ from
   its earliest year by more than WLTP 5% or DC peak 10%, that is a real change, so the later
   years become their own variant `<variant_id>-<first year>` (the earliest band keeps the
   original id and ends the year before). Smaller differences stay in one variant; merge then
   prefers the earliest model year and lists the rest in conflicts.csv.
5. Registration counts are kept as facts on the generation, or on the model when the record
   has no year; aggregation happens in `aggregate_counts`.
6. Count-only sources (COUNT_ONLY_SOURCES, EEA): their spec records are dropped and counted,
   never matched: the EEA averages blend different cars (T-004 review, Q-039).

Nothing here decides values: that is merge's job.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field

from ev_pipeline.match.normalise import key, prefix_keys, slug, tokens
from ev_pipeline.match.seed import (
    CANONICAL_UNITS,
    ManualVariant,
    Seed,
    SeedGeneration,
    SeedModel,
    model_alias_keys,
    model_bev_only_keys,
    model_exclude_tokens,
)
from ev_pipeline.records import SourceRecord, SpecValue
from ev_pipeline.schema_models import ChargeCurve, Fact, FactField, Id

EXCLUDED_SOURCES = frozenset({"nyland"})  # permission pending: never in a release (hard floor)

# Sources that hold battery-electric cars only, so a bare trade name ("KONA") means the BEV.
# RDW: server-side BEV proxy (no displacement, see sources/rdw); EEA: Ft = 'electric'.
BEV_FILTERED_SOURCES = frozenset({"rdw", "eea"})

# Sources used for registration counts only; their spec records never become facts (Q-039).
COUNT_ONLY_SOURCES = frozenset({"eea"})

AMBIGUOUS_GENERATION = "ambiguous-generation"
KWH_TOLERANCE = 1.0  # "40KWH" in a name vs 39 kWh net / 40 kWh gross
# Year-band split thresholds (relative difference to the band's first year).
BAND_THRESHOLDS: dict[str, float] = {"wltp_range_km": 0.05, "dc_peak_kw": 0.10}
_KWH_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*-?\s*kwh", re.IGNORECASE)

# Sources whose figures are maker claims rather than measurements (Decision 009: OpenEV and
# seed values count as claims tonight).
CLAIM_SOURCES = frozenset({"openev", "seed-manual", "maker-docs"})

# Spec priority (higher wins). "checked" seed overrides will sit above openev later.
SOURCE_PRIORITY: dict[str, int] = {"openev": 30, "eea": 20, "seed-manual": 10}
DEFAULT_PRIORITY = 0

# Unit conversions to the canonical unit per field: (field, unit_lowercase) -> factor.
_UNIT_ALIASES = {"kwh": "kWh", "km": "km", "kw": "kW", "kwh/100km": "kWh/100km", "s": "s"}
_UNIT_ALIASES |= {"km/h": "km/h", "kph": "km/h", "l": "l", "litre": "l", "liter": "l"}
_UNIT_ALIASES |= {"min": "min", "minutes": "min", "v": "V", "id": "id"}
_UNIT_ALIASES |= {"years": "years", "year": "years", "y": "years"}
_UNIT_ALIASES |= {"mm": "mm", "kg": "kg", "count": "count", "seats": "count", "": "count"}
_CONVERSIONS: dict[tuple[str, str], float] = {
    ("consumption_kwh_100km", "wh/km"): 0.1,
    ("wltp_range_km", "mi"): 1.609344,
    ("epa_range_km", "mi"): 1.609344,
    ("real_range_km", "mi"): 1.609344,
    ("wltp_range_km", "miles"): 1.609344,
    ("epa_range_km", "miles"): 1.609344,
    ("real_range_km", "miles"): 1.609344,
    ("length_mm", "cm"): 10.0,
    ("length_mm", "m"): 1000.0,
}
CURRENCIES = {"EUR", "GBP"}


@dataclass
class MatchedFact:
    fact: Fact
    source_id: str
    priority: int
    year: int | None
    generation_id: str | None = None
    model_id: str | None = None


@dataclass
class VariantInfo:
    id: str
    generation_id: str
    name: str
    years: set[int] = field(default_factory=set)
    explicit_end: int | None = None  # seed-manual gives an end year directly
    open_end: bool = False  # seed-manual years [start, null]
    drivetrains: list[tuple[int, str, str]] = field(default_factory=list)  # (prio, value, src)
    source_ids: set[str] = field(default_factory=set)


@dataclass
class UnmatchedRow:
    source_id: str
    record_key: str
    make: str
    model: str
    variant_name: str
    year: str
    reason: str


@dataclass
class Problem:
    """A value we could not use; written to data/review/validation.csv."""

    stage: str
    source_id: str
    record_key: str
    subject_id: str
    field: str
    value: str
    unit: str
    reason: str


@dataclass
class MatchResult:
    variants: dict[str, VariantInfo] = field(default_factory=dict)
    spec_facts: list[MatchedFact] = field(default_factory=list)
    count_facts: list[MatchedFact] = field(default_factory=list)
    unmatched: list[UnmatchedRow] = field(default_factory=list)
    other_makes: Counter[tuple[str, str]] = field(default_factory=Counter)
    problems: list[Problem] = field(default_factory=list)
    excluded: Counter[str] = field(default_factory=Counter)
    count_only_skipped: Counter[str] = field(default_factory=Counter)
    year_bands: list[dict[str, object]] = field(default_factory=list)
    matched_records: int = 0


def priority_of(source_id: str) -> int:
    return SOURCE_PRIORITY.get(source_id, DEFAULT_PRIORITY)


def _contains_run(toks: list[str], run: list[str]) -> bool:
    n = len(run)
    return any(toks[i : i + n] == run for i in range(len(toks) - n + 1))


def find_model(seed: Seed, make_id: str, record: SourceRecord) -> tuple[SeedModel | None, str]:
    make = seed.makes[make_id]
    bev_only = record.source.id.root in BEV_FILTERED_SOURCES
    alias_index: dict[str, set[str]] = {}
    exact_index: dict[str, set[str]] = {}
    for m in make.models:
        for k in model_alias_keys(m):
            alias_index.setdefault(k, set()).add(m.id)
        if bev_only:
            for k in model_bev_only_keys(m):
                exact_index.setdefault(k, set()).add(m.id)
    toks = tokens(record.model)
    variants_of_toks = [toks]
    for strip in (tokens(record.make), tokens(make.name), tokens(make_id)):
        if strip and toks[: len(strip)] == strip and len(toks) > len(strip):
            variants_of_toks.append(toks[len(strip) :])
    # Every (match length, model) candidate; the longest non-excluded one wins.
    candidates: dict[str, int] = {}
    for tl in variants_of_toks:
        hits = [(pk, alias_index[pk]) for pk in prefix_keys(tl) if pk in alias_index]
        full = "".join(tl)
        if full in exact_index:
            hits.append((full, exact_index[full]))
        for pk, ids in hits:
            for mid in ids:
                candidates[mid] = max(candidates.get(mid, 0), len(pk))
    excluded: list[str] = []
    for mid in list(candidates):
        runs = model_exclude_tokens(seed.models[mid])
        if any(_contains_run(tl, run) for tl in variants_of_toks for run in runs):
            excluded.append(mid)
            del candidates[mid]
    if not candidates:
        if excluded:
            return None, f"model not in seed (name excluded from {', '.join(sorted(excluded))})"
        return None, "model not in seed"
    best_len = max(candidates.values())
    best = {mid for mid, n in candidates.items() if n == best_len}
    if len(best) > 1:
        return None, f"ambiguous model: {', '.join(sorted(best))}"
    return seed.models[best.pop()], ""


def kwh_in_text(*texts: str | None) -> set[float]:
    """kWh figures written in names: "40KWH", "62 kWh", "e+ 62-kWh" -> {40.0, 62.0}."""
    out: set[float] = set()
    for t in texts:
        for m in _KWH_RE.finditer(t or ""):
            out.add(float(m.group(1).replace(",", ".")))
    return out


def record_kwh(record: SourceRecord) -> set[float]:
    out = kwh_in_text(record.model, record.variant_name)
    for f in (FactField.battery_kwh_net, FactField.battery_kwh_gross):
        sv = record.specs.get(f)
        if sv is not None and isinstance(sv.value, int | float) and not isinstance(sv.value, bool):
            out.add(float(sv.value))
    return out


@dataclass
class GenerationEvidence:
    """What we already know per generation, used to place records from a shared year."""

    names: dict[str, set[str]] = field(default_factory=dict)  # gen id -> variant name keys
    kwh: dict[str, set[float]] = field(default_factory=dict)  # gen id -> battery sizes
    with_variants: set[str] = field(default_factory=set)

    def add_variant(self, gen_id: str, name: str | None, kwh: set[float]) -> None:
        self.with_variants.add(gen_id)
        if name:
            self.names.setdefault(gen_id, set()).add(key(name))
        self.kwh.setdefault(gen_id, set()).update(kwh | kwh_in_text(name))

    def supports(self, gen_id: str, name_key: str, kwh: set[float]) -> bool:
        if name_key and name_key in self.names.get(gen_id, set()):
            return True
        known = self.kwh.get(gen_id, set())
        return any(abs(a - b) <= KWH_TOLERANCE for a in kwh for b in known)


def find_generation(
    model: SeedModel,
    year: int | None,
    evidence: GenerationEvidence | None = None,
    record: SourceRecord | None = None,
) -> tuple[SeedGeneration | None, str]:
    if year is None:
        if len(model.generations) == 1:
            return model.generations[0], ""
        return None, f"no year and model has {len(model.generations)} generations"
    hits = [g for g in model.generations if g.covers(year)]
    if not hits:
        return None, f"year {year} outside every generation of {model.id}"
    newest = max(hits, key=lambda g: g.year_start)
    if len(hits) == 1 or evidence is None:
        return newest, ""  # no evidence index: plain "newer wins" (Q-014)
    name_key = key(record.variant_name) if record is not None else ""
    kwh = record_kwh(record) if record is not None else set()
    backed = [g for g in hits if evidence.supports(g.id, name_key, kwh)]
    if backed:
        return max(backed, key=lambda g: g.year_start), ""
    if sum(1 for g in hits if g.id in evidence.with_variants) >= 2:
        ids = ", ".join(g.id for g in sorted(hits, key=lambda g: g.year_start))
        return None, f"{AMBIGUOUS_GENERATION}: {year} is shared by {ids}; no name/battery evidence"
    return newest, ""


def normalise_unit(fname: str, sv: SpecValue) -> tuple[object, str, str]:
    """Return (value, canonical unit, problem). Problem is '' when the value is usable."""
    value = sv.value
    unit = sv.unit.strip()
    if fname == "price_new":
        cur = unit.upper()
        if cur not in CURRENCIES:
            return value, unit, f"unsupported currency {unit!r}"
        return value, cur, ""
    if fname == "dc_curve":
        try:
            raw = json.loads(value) if isinstance(value, str) else value
            return ChargeCurve.model_validate(raw), "kW", ""
        except Exception as exc:
            return value, unit, f"invalid charge curve: {str(exc)[:80]}"
    canonical = CANONICAL_UNITS.get(fname)
    if canonical is None:
        return value, unit, f"no canonical unit for {fname}"
    low = unit.lower()
    if _UNIT_ALIASES.get(low) == canonical or unit == canonical:
        return value, canonical, ""
    factor = _CONVERSIONS.get((fname, low))
    if factor is not None and isinstance(value, int | float) and not isinstance(value, bool):
        return float(value) * factor, canonical, ""
    return value, unit, f"unit {unit!r} not convertible to {canonical}"


def _make_fact(
    record: SourceRecord,
    fname: str,
    sv: SpecValue,
    subject_type: str,
    subject_id: str,
    result: MatchResult,
) -> Fact | None:
    value, unit, problem = normalise_unit(fname, sv)
    if problem:
        result.problems.append(
            Problem(
                "unit",
                record.source.id.root,
                record.record_key,
                subject_id,
                fname,
                str(sv.value),
                sv.unit,
                problem,
            )
        )
        return None
    return Fact(
        id=f"{record.source.id.root}:{record.record_key}:{fname}",
        subject_type=subject_type,
        subject_id=subject_id,
        field=FactField(fname),
        value=value,
        unit=unit,
        country=record.country,
        source=record.source,
        source_record=record.record_key,
        retrieved_at=record.retrieved_at,
        confidence=record.confidence,
        claim=True
        if record.source.id.root in CLAIM_SOURCES and fname != "registered_count"
        else None,
    )


def _unmatched(record: SourceRecord, reason: str) -> UnmatchedRow:
    return UnmatchedRow(
        source_id=record.source.id.root,
        record_key=record.record_key,
        make=record.make,
        model=record.model,
        variant_name=record.variant_name or "",
        year="" if record.year is None else str(record.year),
        reason=reason,
    )


def build_evidence(
    records: list[SourceRecord],
    seed: Seed,
    manual: list[ManualVariant],
    generation_kwh: dict[str, set[float]] | None = None,
) -> GenerationEvidence:
    """Pre-pass: variant names and battery sizes per generation from seed-manual variants and
    spec records whose year falls in exactly one generation (no circular guessing)."""
    ev = GenerationEvidence()
    for gid, kwhs in (generation_kwh or {}).items():
        ev.kwh.setdefault(gid, set()).update(kwhs)
    for mv in manual:
        if mv.record.source.id.root in EXCLUDED_SOURCES or mv.generation_id not in seed.generations:
            continue
        ev.add_variant(mv.generation_id, mv.name, record_kwh(mv.record))
    for rec in records:
        sid = rec.source.id.root
        if rec.kind != "spec" or sid in EXCLUDED_SOURCES or sid in COUNT_ONLY_SOURCES:
            continue
        make_id = seed.make_id_for(rec.make)
        if make_id is None or rec.year is None:
            continue
        model, _ = find_model(seed, make_id, rec)
        if model is None:
            continue
        hits = [g for g in model.generations if g.covers(rec.year)]
        if len(hits) == 1:
            ev.add_variant(hits[0].id, rec.variant_name or "base", record_kwh(rec))
    return ev


def match_records(
    records: list[SourceRecord],
    seed: Seed,
    manual: list[ManualVariant] | None = None,
    generation_kwh: dict[str, set[float]] | None = None,
) -> MatchResult:
    """`generation_kwh`: optional battery sizes per generation (e.g. from battery_packs.yaml
    via variant_links.yaml), used as evidence for shared-year records."""
    result = MatchResult()
    manual = manual or []
    evidence = build_evidence(records, seed, manual, generation_kwh)
    # (generation_id, variant name key) -> variant id
    variant_ids: dict[tuple[str, str], str] = {}

    for mv in manual:
        if mv.record.source.id.root in EXCLUDED_SOURCES:
            result.excluded[mv.record.source.id.root] += 1
            continue
        gen = seed.generations.get(mv.generation_id)
        if gen is None:
            result.unmatched.append(
                _unmatched(mv.record, f"seed-manual generation {mv.generation_id} not in seed")
            )
            continue
        variant_ids[(gen.id, key(mv.name))] = mv.id
        info = result.variants.setdefault(mv.id, VariantInfo(mv.id, gen.id, mv.name))
        if mv.year_start is not None:
            info.years.add(int(mv.year_start))
        if mv.year_end is not None:
            info.explicit_end = int(mv.year_end)
        elif mv.year_start is not None:
            info.open_end = True
        _add_spec_facts(mv.record, gen, mv.id, info, result)
        result.matched_records += 1

    ordered = sorted(
        records, key=lambda r: (-priority_of(r.source.id.root), r.source.id.root, r.record_key)
    )
    for rec in ordered:
        sid = rec.source.id.root
        if sid in EXCLUDED_SOURCES:
            result.excluded[sid] += 1
            continue
        if sid in COUNT_ONLY_SOURCES and rec.kind != "registration_count":
            result.count_only_skipped[sid] += 1
            continue
        make_id = seed.make_id_for(rec.make)
        if make_id is None:
            result.other_makes[(sid, rec.make.strip().upper())] += 1
            continue
        model, why = find_model(seed, make_id, rec)
        if model is None:
            result.unmatched.append(_unmatched(rec, why))
            continue
        if rec.kind == "registration_count":
            _add_count(rec, model, result, evidence)
            continue
        gen, why = find_generation(model, rec.year, evidence, rec)
        if gen is None:
            result.unmatched.append(_unmatched(rec, why))
            continue
        name = rec.variant_name or "base"
        vkey = (gen.id, key(name) or "base")
        vid = variant_ids.get(vkey)
        if vid is None:
            vid = f"{gen.id}-{slug(name) or 'base'}"
            variant_ids[vkey] = vid
        info = result.variants.setdefault(vid, VariantInfo(vid, gen.id, rec.variant_name or "Base"))
        if rec.year is not None:
            info.years.add(rec.year)
        _add_spec_facts(rec, gen, vid, info, result)
        result.matched_records += 1
    split_year_bands(result)
    return result


def _add_spec_facts(
    rec: SourceRecord, gen: SeedGeneration, vid: str, info: VariantInfo, result: MatchResult
) -> None:
    sid = rec.source.id.root
    info.source_ids.add(sid)
    if rec.drivetrain:
        info.drivetrains.append((priority_of(sid), rec.drivetrain, sid))
    for f, sv in rec.specs.items():
        fname = f.value if isinstance(f, FactField) else str(f)
        if fname == "registered_count":
            continue
        if fname == "price_new" and rec.country is None:
            result.problems.append(
                Problem(
                    "unit", sid, rec.record_key, vid, fname, str(sv.value), sv.unit, "no country"
                )
            )
            continue
        fact = _make_fact(rec, fname, sv, "variant", vid, result)
        if fact is not None:
            result.spec_facts.append(
                MatchedFact(fact, sid, priority_of(sid), rec.year, gen.id, gen.model_id)
            )


def _add_count(
    rec: SourceRecord,
    model: SeedModel,
    result: MatchResult,
    evidence: GenerationEvidence | None = None,
) -> None:
    sv = rec.specs.get(FactField.registered_count)
    if sv is None:
        result.unmatched.append(_unmatched(rec, "registration record without registered_count"))
        return
    if rec.year is None:
        subject_type, subject_id, gen_id = "model", model.id, None
    else:
        gen, why = find_generation(model, rec.year, evidence, rec)
        if gen is None:
            result.unmatched.append(_unmatched(rec, why))
            return
        subject_type, subject_id, gen_id = "generation", gen.id, gen.id
    fact = _make_fact(rec, "registered_count", sv, subject_type, subject_id, result)
    if fact is not None:
        result.count_facts.append(
            MatchedFact(
                fact,
                rec.source.id.root,
                priority_of(rec.source.id.root),
                rec.year,
                gen_id,
                model.id,
            )
        )
        result.matched_records += 1


def _band_values(facts: list[MatchedFact]) -> dict[str, float]:
    """Per band field, the value of the highest-priority fact (then lowest fact id)."""
    out: dict[str, float] = {}
    for fname in BAND_THRESHOLDS:
        cands = [
            mf
            for mf in facts
            if mf.fact.field.value == fname
            and isinstance(mf.fact.value, int | float)
            and not isinstance(mf.fact.value, bool)
        ]
        if cands:
            best = sorted(cands, key=lambda m: (-m.priority, m.fact.id))[0]
            out[fname] = float(best.fact.value)
    return out


def _differs(a: dict[str, float], b: dict[str, float]) -> str:
    for fname, limit in BAND_THRESHOLDS.items():
        if fname in a and fname in b:
            scale = max(abs(a[fname]), abs(b[fname])) or 1.0
            if abs(a[fname] - b[fname]) / scale > limit + 1e-9:
                return f"{fname} {a[fname]:g} -> {b[fname]:g} (> {limit:.0%})"
    return ""


def split_year_bands(result: MatchResult) -> None:
    """Split a variant whose later model years differ a lot from its first year (T-005 review).

    Walk the model years in order; a year whose WLTP range differs from the current band's
    first year by more than 5%, or whose DC peak differs by more than 10%, starts a new band.
    Facts without a year stay in the first band. The first band keeps the variant id; later
    bands get `<variant_id>-<first year>` and the name "<name> (<first year>+)". Each split is
    recorded in `result.year_bands` (written to the run log)."""
    by_variant: dict[str, list[MatchedFact]] = {}
    for mf in result.spec_facts:
        by_variant.setdefault(mf.fact.subject_id.root, []).append(mf)
    for vid in sorted(by_variant):
        facts = by_variant[vid]
        years = sorted({mf.year for mf in facts if mf.year is not None})
        if len(years) < 2:
            continue
        per_year = {y: _band_values([mf for mf in facts if mf.year == y]) for y in years}
        bands: list[list[int]] = [[years[0]]]
        anchor = per_year[years[0]]
        reasons: list[str] = []
        for y in years[1:]:
            why = _differs(anchor, per_year[y])
            if why:
                bands.append([y])
                anchor = per_year[y]
                reasons.append(f"{y}: {why}")
            else:
                bands[-1].append(y)
                for k, v in per_year[y].items():
                    anchor.setdefault(k, v)
        if len(bands) == 1:
            continue
        info = result.variants[vid]
        orig_end, orig_open = info.explicit_end, info.open_end
        for i, band in enumerate(bands):
            start = band[0]
            next_start = bands[i + 1][0] if i + 1 < len(bands) else None
            if i == 0:
                target = info
            else:
                new_id = f"{vid}-{start}"
                target = VariantInfo(
                    new_id,
                    info.generation_id,
                    f"{info.name} ({start}+)",
                    drivetrains=list(info.drivetrains),
                )
                result.variants[new_id] = target
                for mf in facts:
                    if mf.year in band:
                        mf.fact = mf.fact.model_copy(update={"subject_id": Id(new_id)})
                        target.source_ids.add(mf.source_id)
            target.years = set(band) if i else {y for y in info.years if y < bands[1][0]}
            if next_start is not None:
                target.explicit_end, target.open_end = next_start - 1, False
            else:
                target.explicit_end, target.open_end = orig_end, orig_open
        info.source_ids = {
            mf.source_id for mf in facts if mf.fact.subject_id.root == vid
        } or info.source_ids
        result.year_bands.append(
            {
                "variant_id": vid,
                "bands": [f"{b[0]}-{b[-1]}" for b in bands],
                "new_ids": [f"{vid}-{b[0]}" for b in bands[1:]],
                "reasons": reasons,
            }
        )


@dataclass
class CountAggregate:
    value: int
    fact_ids: list[str]
    source_ids: list[str]
    level: str  # "generation" or "model"


def aggregate_counts(
    count_facts: list[MatchedFact], seed: Seed, source_id: str, country: str
) -> dict[str, CountAggregate]:
    """Sum registration counts per generation for one source+country.

    Year-level records sum into their generation. A model-level record (no year) is used
    only when that source has no year-level record for the model, and only for a model with
    exactly one generation (otherwise we cannot split it); this avoids double counting.
    """
    mine = [
        mf
        for mf in count_facts
        if mf.source_id == source_id
        and (mf.fact.country.value if mf.fact.country else None) == country
        and isinstance(mf.fact.value, int | float)
    ]
    models_with_years = {mf.model_id for mf in mine if mf.generation_id}
    out: dict[str, CountAggregate] = {}
    for mf in sorted(mine, key=lambda m: m.fact.id):
        if mf.generation_id:
            gid = mf.generation_id
            level = "generation"
        else:
            if mf.model_id in models_with_years:
                continue
            gens = seed.models[mf.model_id].generations
            if len(gens) != 1:
                continue
            gid = gens[0].id
            level = "model"
        agg = out.setdefault(gid, CountAggregate(0, [], [source_id], level))
        agg.value += int(mf.fact.value)
        agg.fact_ids.append(mf.fact.id)
    return out
