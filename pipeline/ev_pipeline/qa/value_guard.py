"""Value guards after the merge (A-05 F7, F9; A-06): values that cannot be published as they are
go to data/review/conflicts.csv instead ("AI proposes, rules decide"; values are never edited).

Every guard works on a *pool*: the facts still allowed for a variant. A guard that takes facts
out removes them from the pool and merges the field again from what is left (which may give
another value, or none), so no later guard or re-merge can bring a removed value back
(A-06 F1, F2). `run_guards` runs all five until nothing changes (A-06 L1: a value one guard
sets is checked by the others too).

1. **Contradicted by a citation that can't ship (A-06 F3).** Citations from a blocked source
   (seed `cited:` values are `maker-docs`, blocked until Q-008) are *evidence*, never values.
   Low-confidence citations in the pool count as evidence too. When the field's value
   disagrees with every such citation (and they agree among themselves) and at most ONE
   independent origin backs it, the value's facts go to review ("contradicted by a citation
   that can't ship yet (Q-008)") and the field is merged again without them. We never ship
   a value we have evidence is wrong. Two or more agreeing origins keep their value; the
   citation is then listed for review. A citation that agrees is noted in provenance only
   (`Merged.evidence`). `newest` fields (prices, counts) are exempt, as for rule `cited`.
2. **Field mix-ups.** A field policy may list `mixup_with` fields (field_sources.yaml): a fact
   whose value is within MIXUP_ABS (0.5) of one of those fields, either the variant's merged
   value or the same source record's own fact, was most likely copied from that field.
   KilowattApp gives the Zoe R240 23.3 kW AC (its battery is 23.3 kWh gross) and one Zoe R110
   record 41 kW AC (41 kWh usable). Such a fact goes to review and the field is merged again
   without it, unless it is otherwise backed: the fact carries a citation (seed `cited:` or a
   manual fact, any confidence), or a fact from another independent origin, or a cited fact,
   agrees with it. A real 22 kW charger on a 22 kWh car therefore needs a second source or a
   citation to stay.
3. **Needs backing (A-05 F9, A-06 F1/F4).** A field policy may list `needs_backing` sources: a
   value whose agreeing sources are all in that list is withheld, those sources' facts go to
   review, and the field is merged again without them (a backed value of another group, or
   another source's value, then ships: adding a source never removes a value that would
   otherwise ship).
   An agreeing uncited seed value counts as backing only where the field says
   `seed_counts_as_backing: true` (dc_peak_kw). KilowattApp DC peaks: the Zoe Phase 1 R110 (no
   DC socket) carried KilowattApp's 150 kW alone.
4. **Impossible pairs (A-05 F7).** Two merged values of one variant that cannot both be true:
   - `wltp_efficiency`: WLTP km / usable kWh > MAX_WLTP_KM_PER_KWH (10);
   - `usable_gt_gross`: usable kWh > gross kWh (+ row rounding).
   One half is wrong, usually a fact attached to the wrong trim. When exactly one half rests on
   a citation (rule `cited`, or a cited winner), the other half is taken out (A-06 F2: a cited
   win is never undone by a lone uncited value). Otherwise the half with fewer independent
   agreeing sources is taken out (equal support: both). Taking out a half that won by rule
   `cited` also takes out the values that citation overruled, so they cannot come back. Only
   pairs of two merged values are guarded: when one half is inherited from the linked battery
   pack (variant_links.yaml), the link is the likely error (as in qa/pack_guard.py), so nothing
   is taken out and the release QA `impossible_values` check flags it.
5. **Versions that don't belong with the best case (T-155).** `guard_versions`: a TGK
   version's consumption or worst-case WLTP from another battery or approval family
   (its own best case > 15 % from the shipped one), and any worst case above the shipped
   best case, go to review.
"""

from __future__ import annotations

from typing import Any

from ev_pipeline.match.matcher import MatchedFact
from ev_pipeline.merge.merge import (
    NOT_INDEPENDENT,
    Merged,
    has_citation,
    is_cited,
    merge_facts,
    origin_of,
)
from ev_pipeline.merge.policy import Policies
from ev_pipeline.qa.checks import EPS, MAX_WLTP_KM_PER_KWH, ROUNDING_KWH

NET, GROSS, WLTP = "battery_kwh_net", "battery_kwh_gross", "wltp_range_km"
MAX_ROUNDS = 4
MIXUP_ABS = 0.5  # kW vs kWh: "the same number" within half a unit (23.3 kWh -> 23.3 kW)
CONTRADICTED = "contradicted by a citation that can't ship yet (Q-008)"
CONTRADICTED_LOW = "contradicted by a low-confidence citation"
CITATION_OUTVOTED = "citation (not published) disagrees with 2+ agreeing sources"

Pool = dict[str, list[MatchedFact]]


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


def _take_out(
    merged: dict[str, dict[str, Merged]],
    pool: Pool,
    vid: str,
    fname: str,
    ids: set[str],
    why: str,
    policies: Policies,
) -> list[dict[str, Any]]:
    """Remove facts `ids` of `fname` from the pool (review rows), then merge the field again
    from what is left, or delete it. Removed facts never come back in a later re-merge."""
    rows = [
        _row(vid, fname, mf, why)
        for mf in pool.get(vid, [])
        if mf.fact.id in ids and mf.fact.field.value == fname
    ]
    pool[vid] = [
        mf for mf in pool.get(vid, []) if not (mf.fact.id in ids and mf.fact.field.value == fname)
    ]
    left = [mf for mf in pool[vid] if mf.fact.field.value == fname]
    if left:
        merged[vid][fname] = merge_facts(left, policies.for_field(fname))
    else:
        merged[vid].pop(fname, None)
    return rows


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


def _rests_on_citation(mg: Merged) -> bool:
    return mg.rule == "cited" or is_cited(mg.winner)


def guard_impossible(
    merged: dict[str, dict[str, Merged]],
    facts_by_variant: Pool,
    policies: Policies,
) -> list[dict[str, Any]]:
    """Take impossible halves out of `merged` (in place); returns review rows."""
    rows: list[dict[str, Any]] = []
    for vid in sorted(merged):
        mv = merged[vid]
        for _ in range(MAX_ROUNDS):
            own = {f for f in (NET, GROSS, WLTP) if f in mv and _num(mv[f].value) is not None}
            values = {f: float(mv[f].value) for f in own}  # type: ignore[arg-type]
            bad = _violations(values, own)
            if not bad:
                break
            _rule, pair, why = bad[0]
            droppable = [f for f in pair if f in own]
            cited = [f for f in droppable if _rests_on_citation(mv[f])]
            if len(cited) == 1:  # A-06 F2: the uncited half goes
                drop = [f for f in droppable if f not in cited]
            else:
                support = {f: mv[f].independent_agreeing for f in droppable}
                low = min(support.values())
                drop = [f for f in droppable if support[f] == low]
            for f in drop:
                mg = mv[f]
                taken = set(mg.fact_ids)
                if mg.rule == "cited":  # what the citation overruled must not come back
                    taken |= {c.fact.id for c in mg.conflicts}
                rows += _take_out(merged, facts_by_variant, vid, f, taken, why, policies)
    return rows


def _is_backed(mg: Merged, weak: tuple[str, ...], seed_backs: bool) -> bool:
    """No `needs_backing` source in the value, or another source agrees with it (an uncited
    seed value only where the field says `seed_counts_as_backing`)."""
    if not set(mg.source_ids) & set(weak):
        return True
    backers = [s for s in mg.source_ids if s not in weak]
    if not seed_backs:
        backers = [s for s in backers if s != "seed-manual"]
    return bool(backers)


def guard_needs_backing(
    merged: dict[str, dict[str, Merged]],
    facts_by_variant: Pool,
    policies: Policies,
) -> list[dict[str, Any]]:
    """Withhold values backed only by `needs_backing` sources and merge the field again
    without them (in place); review rows. A-06 F1: never deletes a value that is backed."""
    rows: list[dict[str, Any]] = []
    for vid in sorted(merged):
        for fname in sorted(merged[vid]):
            pol = policies.for_field(fname)
            if not pol.needs_backing:
                continue
            for _ in range(MAX_ROUNDS * 4):
                mg = merged[vid].get(fname)
                if mg is None or _is_backed(mg, pol.needs_backing, pol.seed_counts_as_backing):
                    break
                why = f"needs backing: only {', '.join(mg.source_ids)}"
                # Only the weak facts go: an agreeing seed value stays and may ship alone.
                weak_ids = {
                    mf.fact.id
                    for mf in facts_by_variant.get(vid, [])
                    if mf.fact.id in set(mg.fact_ids) and mf.source_id in pol.needs_backing
                }
                rows += _take_out(merged, facts_by_variant, vid, fname, weak_ids, why, policies)
    return rows


def _cite_text(c: MatchedFact) -> str:
    v = _num(c.fact.value)
    shown = f"{v:g}" if v is not None else str(c.fact.value)
    return f"{c.source_id} {shown} {c.fact.unit}"


def guard_contradicted(
    merged: dict[str, dict[str, Merged]],
    facts_by_variant: Pool,
    policies: Policies,
    evidence: Pool | None = None,
) -> list[dict[str, Any]]:
    """A-06 F3: withhold a value that a citation we can't publish (blocked source, or low
    confidence) contradicts, when at most one independent origin backs it (in place)."""
    rows: list[dict[str, Any]] = []
    evidence = evidence or {}
    for vid in sorted(merged):
        blocked = evidence.get(vid, [])
        low = [mf for mf in facts_by_variant.get(vid, []) if has_citation(mf) and not is_cited(mf)]
        for fname in sorted({mf.fact.field.value for mf in blocked + low}):
            pol = policies.for_field(fname)
            if pol.mode == "newest":
                continue
            cites = [mf for mf in blocked + low if mf.fact.field.value == fname]
            if not all(pol.agree(cites[0].fact.value, c.fact.value) for c in cites):
                continue  # citations disagree among themselves: nothing clear to go by
            for _ in range(MAX_ROUNDS * 4):
                mg = merged[vid].get(fname)
                if mg is None:
                    break
                agreeing = [c for c in blocked if c.fact.field.value == fname]
                agreeing = [c for c in agreeing if pol.agree(mg.value, c.fact.value)]
                if agreeing or any(pol.agree(mg.value, c.fact.value) for c in cites):
                    mg.evidence = agreeing
                    break
                if has_citation(mg.winner):
                    break  # the value is itself a citation: rule `cited` decided it
                if mg.independent_agreeing >= 2:
                    rows += [_row(vid, fname, c, CITATION_OUTVOTED) for c in cites if c in blocked]
                    break
                kind = CONTRADICTED if any(c in blocked for c in cites) else CONTRADICTED_LOW
                why = f"{kind}: {_cite_text(cites[0])}"
                rows += _take_out(
                    merged, facts_by_variant, vid, fname, set(mg.fact_ids), why, policies
                )
    return rows


def _origin(mf: MatchedFact, policies: Policies | None = None) -> str:
    pol = policies.for_field(mf.fact.field.value) if policies is not None else None
    return origin_of(mf, pol) if pol is not None else origin_of(mf)


def _has_citation(mf: MatchedFact) -> bool:
    """Read from a public page it names (any confidence): not a blind copy of another field."""
    return has_citation(mf)


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
        if o.source_id not in NOT_INDEPENDENT and _origin(o, policies) != _origin(mf, policies):
            return True
    return False


def guard_mixups(
    merged: dict[str, dict[str, Merged]],
    facts_by_variant: Pool,
    policies: Policies,
) -> list[dict[str, Any]]:
    """Take likely field mix-ups out of `merged` (in place) and merge again; review rows."""
    rows: list[dict[str, Any]] = []
    for vid in sorted(merged):
        row = merged[vid]
        for fname in sorted(row):
            fields = policies.for_field(fname).mixup_with
            if not fields:
                continue
            facts = facts_by_variant.get(vid, [])
            same = [mf for mf in facts if mf.fact.field.value == fname]
            bad: list[tuple[MatchedFact, str]] = []
            for mf in same:
                other = _mixup_with(mf, facts, row, fields)
                if other is not None and not _backed(mf, same, policies):
                    bad.append((mf, other))
            for mf, other in bad:
                why = f"field mix-up: {fname} {mf.fact.value} equals {other} (no other backing)"
                rows += _take_out(merged, facts_by_variant, vid, fname, {mf.fact.id}, why, policies)
    return rows


# --- T-155: version-level values from another version than the shipped best case --------
WORST = "wltp_range_km_worst"
# Per-version values of a SPREAD_SOURCES record (TGK: one record per type-approved version)
# that only mean something next to that same record's own best-case WLTP.
VERSION_FIELDS = ("consumption_kwh_100km", WORST)
# A record whose own best-case WLTP is this far (share of the shipped value) from the row's
# shipped WLTP is another battery or another approval family (ë-SpaceTourer 50 vs 75 kWh:
# 238 vs 339 km, +42 %; Leaf e+ 2022 extension 449 vs 385 km, +17 %). Same-battery versions
# (wheels, model years) stay well inside it (Leaf 40 kWh 270-300 km, +11 %; ë-SpaceTourer
# 75 kWh 339-370 km vs cited 330 km, +12 %).
OTHER_FAMILY_REL = 0.15
WORST_ABOVE_BEST = "impossible: worst-case WLTP above the shipped best case"
OTHER_FAMILY = "version of another battery or approval family"


def guard_versions(
    merged: dict[str, dict[str, Merged]],
    facts_by_variant: Pool,
    policies: Policies,
) -> list[dict[str, Any]]:
    """T-155: keep a version's consumption and worst-case WLTP only next to a best case they
    belong with (in place; review rows):
    - a SPREAD_SOURCES fact whose own record's best-case WLTP is more than OTHER_FAMILY_REL
      from the row's shipped `wltp_range_km` comes from another battery or approval family:
      it goes to review (TGK records don't name the battery, so they are never split by it);
    - a worst-case WLTP above the shipped best case cannot be true (Leaf 40 kWh: 287 km from
      the 2022 extension next to the 270 km of the first versions): it goes to review.
    """
    from ev_pipeline.merge.merge import SPREAD_SOURCES

    rows: list[dict[str, Any]] = []
    for vid in sorted(merged):
        mv = merged[vid]
        best_mg = mv.get(WLTP)
        best = _num(best_mg.value) if best_mg is not None else None
        if best is None or best <= 0:
            continue
        pool = facts_by_variant.get(vid, [])
        for fname in VERSION_FIELDS:
            if fname not in mv:
                continue
            far: dict[str, float] = {}
            for mf in pool:
                if mf.fact.field.value != fname or mf.source_id not in SPREAD_SOURCES:
                    continue
                own = [v for v in _record_values(pool, mf, (WLTP,)) if v is not None]
                if own and abs(own[0] - best) > OTHER_FAMILY_REL * best + EPS:
                    far[mf.fact.id] = own[0]
            for fid, own_best in sorted(far.items()):
                why = f"{OTHER_FAMILY}: its best case {own_best:g} km vs shipped {best:g} km"
                rows += _take_out(merged, facts_by_variant, vid, fname, {fid}, why, policies)
                pool = facts_by_variant.get(vid, [])
        for _ in range(MAX_ROUNDS * 4):
            w = mv.get(WORST)
            wv = _num(w.value) if w is not None else None
            if w is None or wv is None or wv <= best + EPS:
                break
            why = f"{WORST_ABOVE_BEST}: {wv:g} > {best:g} km"
            rows += _take_out(merged, facts_by_variant, vid, WORST, set(w.fact_ids), why, policies)
    return rows


def run_guards(
    merged: dict[str, dict[str, Merged]],
    facts_by_variant: Pool,
    policies: Policies,
    evidence: Pool | None = None,
) -> list[dict[str, Any]]:
    """All value guards on a copy of the fact pool, repeated until no guard changes anything
    (A-06 L1), so each guard also checks the values the others set. Review rows, de-duplicated."""
    pool: Pool = {vid: list(fs) for vid, fs in facts_by_variant.items()}
    rows: list[dict[str, Any]] = []
    for _ in range(MAX_ROUNDS):
        before = sum(len(fs) for fs in pool.values())
        rows += guard_contradicted(merged, pool, policies, evidence)
        rows += guard_mixups(merged, pool, policies)
        rows += guard_needs_backing(merged, pool, policies)
        rows += guard_impossible(merged, pool, policies)
        rows += guard_versions(merged, pool, policies)
        if sum(len(fs) for fs in pool.values()) == before:
            break
    seen: set[tuple[str, str, str, str]] = set()
    out = []
    for r in rows:
        k = (r["variant_id"], r["field"], r["fact_id"], r["tolerance"])
        if k not in seen:
            seen.add(k)
            out.append(r)
    return out


def citation_values(evidence: Pool, facts_by_variant: Pool) -> dict[str, dict[str, list[float]]]:
    """Per variant and field, the numbers of citations that don't ship: blocked ones
    (`evidence`) and low-confidence ones in the pool. The derive step uses them so that a
    value withheld by `guard_contradicted` is not re-estimated from another field."""
    out: dict[str, dict[str, list[float]]] = {}
    for vid in sorted(set(evidence) | set(facts_by_variant)):
        low = [mf for mf in facts_by_variant.get(vid, []) if has_citation(mf) and not is_cited(mf)]
        for mf in [*evidence.get(vid, []), *low]:
            v = _num(mf.fact.value)
            if v is not None:
                out.setdefault(vid, {}).setdefault(mf.fact.field.value, []).append(v)
    return out
