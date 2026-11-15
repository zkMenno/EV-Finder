"""Rules-first matching of SourceRecords to seed models, generations and variants (T-005).

1. Make: normalised key of the record's make against seed make names/ids (+ MAKE_ALIASES).
2. Model: the longest token prefix of the record's model name (with or without a leading
   make name) that equals a seed model name or one of its `name_aliases`. A tie between two
   seed models is ambiguous and goes to review.
3. Generation: the record's year within [start, end] (end null = open). When two generations
   share a boundary year (e.g. a facelift year) the newer one wins, see QUESTIONS.md Q-014.
   A record without a year only matches a model with exactly one generation.
4. Variant (spec records): `<generation_id>-<slug(variant_name or 'base')>`. Records of one
   source with the same normalised variant name in one generation share a variant, whatever
   their year; years seen become the variant's year span. A seed-manual variant with the same
   normalised name in the same generation lends its id, so the two merge.
5. Registration counts are kept as facts on the generation, or on the model when the record
   has no year; aggregation happens in `aggregate_counts`.

Nothing here decides values: that is merge's job.
"""

from __future__ import annotations

import json
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
)
from ev_pipeline.records import SourceRecord, SpecValue
from ev_pipeline.schema_models import ChargeCurve, Fact, FactField

EXCLUDED_SOURCES = frozenset({"nyland"})  # permission pending: never in a release (hard floor)

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
    matched_records: int = 0


def priority_of(source_id: str) -> int:
    return SOURCE_PRIORITY.get(source_id, DEFAULT_PRIORITY)


def find_model(seed: Seed, make_id: str, record: SourceRecord) -> tuple[SeedModel | None, str]:
    make = seed.makes[make_id]
    alias_index: dict[str, set[str]] = {}
    for m in make.models:
        for k in model_alias_keys(m):
            alias_index.setdefault(k, set()).add(m.id)
    toks = tokens(record.model)
    variants_of_toks = [toks]
    for strip in (tokens(record.make), tokens(make.name), tokens(make_id)):
        if strip and toks[: len(strip)] == strip and len(toks) > len(strip):
            variants_of_toks.append(toks[len(strip) :])
    best_len = 0
    best: set[str] = set()
    for tl in variants_of_toks:
        for pk in prefix_keys(tl):
            if pk in alias_index:
                if len(pk) > best_len:
                    best_len, best = len(pk), set(alias_index[pk])
                elif len(pk) == best_len:
                    best |= alias_index[pk]
                break
    if not best:
        return None, "model not in seed"
    if len(best) > 1:
        return None, f"ambiguous model: {', '.join(sorted(best))}"
    return seed.models[best.pop()], ""


def find_generation(model: SeedModel, year: int | None) -> tuple[SeedGeneration | None, str]:
    if year is None:
        if len(model.generations) == 1:
            return model.generations[0], ""
        return None, f"no year and model has {len(model.generations)} generations"
    hits = [g for g in model.generations if g.covers(year)]
    if not hits:
        return None, f"year {year} outside every generation of {model.id}"
    return max(hits, key=lambda g: g.year_start), ""  # newer generation wins a shared year


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


def match_records(
    records: list[SourceRecord],
    seed: Seed,
    manual: list[ManualVariant] | None = None,
) -> MatchResult:
    result = MatchResult()
    manual = manual or []
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
        make_id = seed.make_id_for(rec.make)
        if make_id is None:
            result.other_makes[(sid, rec.make.strip().upper())] += 1
            continue
        model, why = find_model(seed, make_id, rec)
        if model is None:
            result.unmatched.append(_unmatched(rec, why))
            continue
        if rec.kind == "registration_count":
            _add_count(rec, model, result)
            continue
        gen, why = find_generation(model, rec.year)
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


def _add_count(rec: SourceRecord, model: SeedModel, result: MatchResult) -> None:
    sv = rec.specs.get(FactField.registered_count)
    if sv is None:
        result.unmatched.append(_unmatched(rec, "registration record without registered_count"))
        return
    if rec.year is None:
        subject_type, subject_id, gen_id = "model", model.id, None
    else:
        gen, why = find_generation(model, rec.year)
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
