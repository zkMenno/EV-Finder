"""Value guards after the merge (A-05 F7, F9): values that cannot be published as they are go
to data/review/conflicts.csv instead ("AI proposes, rules decide"; values are never edited).

1. **Impossible pairs (F7).** Two merged values of one variant that cannot both be true:
   - `wltp_efficiency`: WLTP km / usable kWh > MAX_WLTP_KM_PER_KWH (10);
   - `usable_gt_gross`: usable kWh > gross kWh (+ row rounding).
   One half is wrong, usually a fact attached to the wrong trim (A-05: Megane 40 kWh with the
   60 kWh car's WLTP). The half with fewer independent agreeing sources is taken out: its
   agreeing facts become review rows and the field is merged again from the facts left (which
   may give another value, or none). Equal support: both halves are taken out. Only pairs of
   two merged values are guarded: when one half is inherited from the linked battery pack
   (variant_links.yaml), the link is the likely error (as in qa/pack_guard.py), so nothing is
   taken out and the release QA `impossible_values` check flags it.
2. **Needs backing (F9).** A field policy may list `needs_backing` sources (field_sources.yaml):
   a value whose agreeing sources are all in that list is withheld and its facts go to review.
   KilowattApp DC peaks: the Zoe Phase 1 R110 (no DC socket) carried KilowattApp's 150 kW
   alone; the record was on the right trim, the source value was wrong.
3. **Field mix-ups.** A field policy may list `mixup_with` fields (field_sources.yaml): a fact
   whose value is within MIXUP_ABS (0.5) of one of those fields, either the variant's merged
   value or the same source record's own fact, was most likely copied from that field.
   KilowattApp gives the Zoe R240 23.3 kW AC (its battery is 23.3 kWh gross) and one Zoe R110
   record 41 kW AC (41 kWh usable). Such a fact goes to review and the field is merged again
   without it, unless it is otherwise backed: the fact carries a citation (seed `cited:` or a
   manual fact, any confidence), or a fact from another independent origin, or a cited fact,
   agrees with it. A real 22 kW charger on a 22 kWh car therefore needs a second source or a
   citation to stay.
"""

from __future__ import annotations

from typing import Any

from ev_pipeline.match.matcher import MatchedFact
from ev_pipeline.merge.merge import (
    CITED_RECORD_MARK,
    CITED_SOURCES,
    NOT_INDEPENDENT,
    SAME_ORIGIN,
    Merged,
    merge_facts,
)
from ev_pipeline.merge.policy import Policies
from ev_pipeline.qa.checks import EPS, MAX_WLTP_KM_PER_KWH, ROUNDING_KWH

NET, GROSS, WLTP = "battery_kwh_net", "battery_kwh_gross", "wltp_range_km"
MAX_ROUNDS = 4
MIXUP_ABS = 0.5  # kW vs kWh: "the same number" within half a unit (23.3 kWh -> 23.3 kW)


def _num(v: object) -> float | None:
    return float(v) if isinstance(v, int | float) and not isinstance(v, bool) else None


def _row(vid: str, fname: str, mf: MatchedFact, why: str) -> dict[str, Any]:
    return {
        "variant_id": vid,
        "field": fname,
        "source_id": mf.source_id,
        "value": mf.fact.value,
        "unit": mf.fact.unit,
        "winning_value": None,  # filled in after the guard (pack_guard.fill_winning_values)
        "tolerance": why,
        "fact_id": mf.fact.id,
    }


def _violations(values: dict[str, float], own: set[str]) -> list[tuple[str, tuple[str, str], str]]:
    """(rule, (field a, field b), detail) for each impossible pair; `own` = merged fields."""
    out = []
    net, gross, wltp = values.get(NET), values.get(GROSS), values.get(WLTP)
    if net is not None and wltp is not None and net > 0 and wltp / net > MAX_WLTP_KM_PER_KWH:
        out.append(("wltp_efficiency", (WLTP, NET), f"impossible: {wltp / net:.1f} km/kWh > 10"))
    if net is not None and gross is not None and net > gross + ROUNDING_KWH + EPS:
        out.append(
            ("usable_gt_gross", (NET, GROSS), f"impossible: usable {net:g} > gross {gross:g} kWh")
        )
    # Both halves must be merged facts: with a pack value as one half, the pack link is the
    # likely error (as in pack_guard), so the release QA flags it instead.
    return [v for v in out if set(v[1]) <= own]


def guard_impossible(
    merged: dict[str, dict[str, Merged]],
    facts_by_variant: dict[str, list[MatchedFact]],
    policies: Policies,
) -> list[dict[str, Any]]:
    """Take impossible halves out of `merged` (in place); returns review rows."""
    rows: list[dict[str, Any]] = []
    for vid in sorted(merged):
        mv = merged[vid]
        removed: set[str] = set()  # fact ids taken out of this variant
        for _ in range(MAX_ROUNDS):
            own = {f for f in (NET, GROSS, WLTP) if f in mv and _num(mv[f].value) is not None}
            values = {f: float(mv[f].value) for f in own}  # type: ignore[arg-type]
            bad = _violations(values, own)
            if not bad:
                break
            _rule, pair, why = bad[0]
            droppable = [f for f in pair if f in own]
            support = {f: mv[f].independent_agreeing for f in droppable}
            low = min(support.values())
            for f in [f for f in droppable if support[f] == low]:
                taken = set(mv[f].fact_ids)
                removed |= taken
                for mf in facts_by_variant.get(vid, []):
                    if mf.fact.id in taken and mf.fact.field.value == f:
                        rows.append(_row(vid, f, mf, why))
                left = [
                    mf
                    for mf in facts_by_variant.get(vid, [])
                    if mf.fact.field.value == f and mf.fact.id not in removed
                ]
                if left:
                    mv[f] = merge_facts(left, policies.for_field(f))
                else:
                    del mv[f]
    return rows


def guard_needs_backing(
    merged: dict[str, dict[str, Merged]],
    facts_by_variant: dict[str, list[MatchedFact]],
    policies: Policies,
) -> list[dict[str, Any]]:
    """Withhold values backed only by `needs_backing` sources (in place); review rows."""
    rows: list[dict[str, Any]] = []
    for vid in sorted(merged):
        for fname in list(merged[vid]):
            weak = policies.for_field(fname).needs_backing
            mg = merged[vid][fname]
            if not weak or not set(mg.source_ids) <= set(weak):
                continue
            why = f"needs backing: only {', '.join(mg.source_ids)}"
            for mf in facts_by_variant.get(vid, []):  # the value and its conflicts
                if mf.fact.field.value == fname:
                    rows.append(_row(vid, fname, mf, why))
            del merged[vid][fname]
    return rows


def _origin(mf: MatchedFact) -> str:
    return SAME_ORIGIN.get(mf.source_id, mf.source_id)


def _has_citation(mf: MatchedFact) -> bool:
    """Read from a public page it names (any confidence): not a blind copy of another field."""
    if mf.source_id in CITED_SOURCES:
        return True
    return mf.source_id == "seed-manual" and CITED_RECORD_MARK in (mf.fact.source_record or "")


def _record_values(
    facts: list[MatchedFact], mf: MatchedFact, fields: tuple[str, ...]
) -> list[float | None]:
    """The same source record's own values for `fields` (e.g. its battery figures)."""
    rec = mf.fact.source_record
    if rec is None:
        return []
    return [
        _num(o.fact.value)
        for o in facts
        if o.source_id == mf.source_id
        and o.fact.source_record == rec
        and o.fact.field.value in fields
    ]


def _mixup_with(
    mf: MatchedFact, facts: list[MatchedFact], row: dict[str, Merged], fields: tuple[str, ...]
) -> str | None:
    """The field `mf` most likely repeats (within MIXUP_ABS), else None."""
    v = _num(mf.fact.value)
    if v is None:
        return None
    for other in fields:
        candidates = [_num(row[other].value)] if other in row else []
        candidates += _record_values(facts, mf, (other,))
        if any(c is not None and abs(c - v) <= MIXUP_ABS + EPS for c in candidates):
            return other
    return None


def _backed(mf: MatchedFact, same_field: list[MatchedFact], policies: Policies) -> bool:
    """Cited itself, or another independent origin / a cited fact gives the same value."""
    if _has_citation(mf):
        return True
    pol = policies.for_field(mf.fact.field.value)
    for o in same_field:
        if o is mf or not pol.agree(mf.fact.value, o.fact.value):
            continue
        if _has_citation(o):
            return True
        if o.source_id not in NOT_INDEPENDENT and _origin(o) != _origin(mf):
            return True
    return False


def guard_mixups(
    merged: dict[str, dict[str, Merged]],
    facts_by_variant: dict[str, list[MatchedFact]],
    policies: Policies,
) -> list[dict[str, Any]]:
    """Take likely field mix-ups out of `merged` (in place) and merge again; review rows."""
    rows: list[dict[str, Any]] = []
    for vid in sorted(merged):
        row = merged[vid]
        facts = facts_by_variant.get(vid, [])
        for fname in sorted(row):
            fields = policies.for_field(fname).mixup_with
            if not fields:
                continue
            same = [mf for mf in facts if mf.fact.field.value == fname]
            bad: list[tuple[MatchedFact, str]] = []
            for mf in same:
                other = _mixup_with(mf, facts, row, fields)
                if other is not None and not _backed(mf, same, policies):
                    bad.append((mf, other))
            if not bad:
                continue
            for mf, other in bad:
                why = f"field mix-up: {fname} {mf.fact.value} equals {other} (no other backing)"
                rows.append(_row(vid, fname, mf, why))
            out = {mf.fact.id for mf, _ in bad}
            left = [mf for mf in same if mf.fact.id not in out]
            if left:
                row[fname] = merge_facts(left, policies.for_field(fname))
            else:
                del row[fname]
    return rows
