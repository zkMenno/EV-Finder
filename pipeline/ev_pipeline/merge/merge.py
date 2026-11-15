"""Merge the facts for one (variant, field[, country]) into one value (T-005, Decision 009).

The field's policy (merge/policy.py, from data/field_sources.yaml) decides priority order,
tolerance and mode. Fields without a policy use the overnight defaults:
1. **Majority**: if 3 or more facts agree within 3% of each other, the largest such group
   wins, whatever the sources' priority. Ties go to the group holding the higher-ranked fact.
2. **Priority** otherwise: openev > eea > seed-manual (see matcher.SOURCE_PRIORITY).
3. **Earliest model year** breaks ties within one priority (T-005 review): a used-car row
   should show what the first cars of the variant had, not the newest model year's specs.
   Big year-to-year changes are split into year-banded variants by the matcher
   (`split_year_bands`); smaller ones stay, and the later values show up as conflicts.
   Then latest `retrieved_at`, then fact id. Facts without a model year rank last.
   (The `newest` mode, used for prices and counts, still prefers the latest year.)

Values are never averaged: the merged value is always one real fact's value.

Confidence: `high` when 2+ *independent* sources agree within the field tolerance; otherwise
the winning fact's own confidence. `seed-manual` is hand-entered from memory and unchecked, so
it never counts as an independent confirmation (QUESTIONS.md Q-015). `agreeing_sources` is the
number of distinct independent sources agreeing with the value, and at least 1 (the winner).

Facts outside the tolerance of the winning value are *conflicts*: kept out of the value,
listed on the Merged result and written to data/review/conflicts.csv by the release step.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ev_pipeline.match.matcher import MatchedFact
from ev_pipeline.merge.policy import DEFAULT_POLICY, FieldPolicy, Policies

MAJORITY_MIN = 3
NOT_INDEPENDENT = frozenset({"seed-manual", "model-estimate"})

_CONF_RANK = {"low": 0, "medium": 1, "high": 2}


def agree(a: object, b: object, policy: FieldPolicy = DEFAULT_POLICY) -> bool:
    return policy.agree(a, b)


def _conf(mf: MatchedFact) -> str:
    c = mf.fact.confidence
    return c.value if hasattr(c, "value") else str(c)


@dataclass
class Merged:
    value: object
    unit: str
    confidence: str
    source_ids: list[str]
    fact_ids: list[str]
    winner: MatchedFact
    rule: str  # "majority", "priority", "median", "newest", "single"
    overruled: int
    independent_agreeing: int  # distinct independent sources agreeing with the value
    conflicts: list[MatchedFact] = field(default_factory=list)
    tolerance: str = ""
    # Q-019: generation-level facts that agree with the value (merge/corroborate.py). They
    # count toward agreeing_sources (and the quality tier), never toward value or confidence.
    corroborations: list[MatchedFact] = field(default_factory=list)

    @property
    def agreeing_sources(self) -> int:
        return max(1, self.independent_agreeing)

    @property
    def claim(self) -> bool:
        return bool(self.winner.fact.claim)

    def note(self) -> str | None:
        parts = []
        if self.rule in ("majority", "median", "newest"):
            parts.append(f"{self.rule} rule")
        if self.overruled:
            parts.append(f"{self.overruled} conflicting value(s) not used")
        for c in self.corroborations:
            parts.append(f"{c.source_id} generation average agrees (corroboration, not the value)")
        return "; ".join(parts) or None


def merge_facts(facts: list[MatchedFact], policy: FieldPolicy = DEFAULT_POLICY) -> Merged:
    if not facts:
        raise ValueError("merge_facts needs at least one fact")

    def rank(mf: MatchedFact) -> tuple:
        # Higher is better: priority, then EARLIEST model year (no year ranks last), then the
        # latest retrieval, then fact id for a stable order.
        year_pref = -mf.year if mf.year is not None else -10_000
        return (policy.priority(mf.source_id), year_pref, mf.fact.retrieved_at, mf.fact.id)

    by_rank = sorted(facts, key=rank, reverse=True)
    rule = "single" if len(facts) == 1 else policy.mode
    if len(facts) == 1:
        winner = by_rank[0]
    elif policy.mode == "newest":
        winner = max(
            facts,
            key=lambda f: (
                f.fact.retrieved_at,
                f.year or 0,
                policy.priority(f.source_id),
                f.fact.id,
            ),
        )
    elif policy.mode == "median":
        anchor = by_rank[0]
        group = [f for f in by_rank if policy.agree(anchor.fact.value, f.fact.value)]
        numeric = all(isinstance(f.fact.value, int | float) for f in group)
        if numeric and len(group) > 1:
            ordered = sorted(group, key=lambda f: (f.fact.value, f.fact.id))
            winner = ordered[(len(ordered) - 1) // 2]  # low median: a real value
        else:
            winner = anchor
    elif policy.mode == "default":
        groups = [[g for g in by_rank if policy.agree(f.fact.value, g.fact.value)] for f in by_rank]
        big = [g for g in groups if len(g) >= MAJORITY_MIN]
        if big:
            size = max(len(g) for g in big)
            winner = next(g for g in big if len(g) == size)[0]
            rule = "majority"
        else:
            winner = by_rank[0]
            rule = "priority"
    else:  # priority
        winner = by_rank[0]
        rule = "priority"
    agreeing = [f for f in by_rank if policy.agree(winner.fact.value, f.fact.value)]
    if winner in agreeing:  # winner first
        agreeing.remove(winner)
    agreeing.insert(0, winner)
    conflicts = [f for f in by_rank if f not in agreeing]
    source_ids: list[str] = []
    for f in agreeing:
        if f.source_id not in source_ids:
            source_ids.append(f.source_id)
    independent = {f.source_id for f in agreeing if f.source_id not in NOT_INDEPENDENT}
    confidence = "high" if len(independent) >= 2 else _conf(winner)
    return Merged(
        value=winner.fact.value,
        unit=winner.fact.unit,
        confidence=confidence,
        source_ids=source_ids,
        fact_ids=[f.fact.id for f in agreeing],
        winner=winner,
        rule=rule,
        overruled=len(conflicts),
        independent_agreeing=len(independent),
        conflicts=conflicts,
        tolerance=policy.tolerance_text(),
    )


def merge_variant_facts(
    facts: list[MatchedFact], policies: Policies | None = None
) -> dict[str, Merged]:
    """Merge all facts of one variant. Keys are field names; prices are `price_new.<CC>`."""
    policies = policies or Policies()
    buckets: dict[str, list[MatchedFact]] = {}
    for mf in facts:
        fname = mf.fact.field.value
        if fname == "price_new":
            cc = mf.fact.country.value if mf.fact.country else None
            if cc is None:
                continue  # matcher already logged prices without a country
            fname = f"price_new.{cc}"
        buckets.setdefault(fname, []).append(mf)
    return {k: merge_facts(v, policies.for_field(k)) for k, v in sorted(buckets.items())}


def merge_drivetrain(
    drivetrains: list[tuple[int, str, str]], policy: FieldPolicy | None = None
) -> tuple[str | None, list[str]]:
    """Highest-priority source's drivetrain (field policy order when given); most common
    value breaks ties."""
    if not drivetrains:
        return None, []
    if policy is not None and policy.order:
        drivetrains = [(policy.priority(s), v, s) for _, v, s in drivetrains]
    top = max(p for p, _, _ in drivetrains)
    values = [v for p, v, _ in drivetrains if p == top]
    best = max(sorted(set(values)), key=values.count)
    srcs = sorted({s for p, v, s in drivetrains if v == best})
    return best, srcs


def min_confidence(*levels: str) -> str:
    return min(levels, key=lambda c: _CONF_RANK[c]) if levels else "low"
