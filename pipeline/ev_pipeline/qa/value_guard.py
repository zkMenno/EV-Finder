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
"""

from __future__ import annotations

from typing import Any

from ev_pipeline.match.matcher import MatchedFact
from ev_pipeline.merge.merge import Merged, merge_facts
from ev_pipeline.merge.policy import Policies
from ev_pipeline.qa.checks import EPS, MAX_WLTP_KM_PER_KWH, ROUNDING_KWH

NET, GROSS, WLTP = "battery_kwh_net", "battery_kwh_gross", "wltp_range_km"
MAX_ROUNDS = 4


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
