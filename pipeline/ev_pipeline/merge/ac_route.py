"""Route source AC figures to the optional on-board charger field (T-063, Decision 034).

`ac_kw` is the standard on-board charger; `ac_kw_optional` is a bigger one sold as an
option (e-208 / e-2008: 7.4 kW standard, 11 kW optional; Megane EV40: 7.4 / 22).
OpenEV and KilowattApp give one "max AC" number and say nothing about options (0 of 746
OpenEV AC records name an option, checked 2026-11-17), so they often hold the option.

We never guess which one a source means. A source `ac_kw` fact moves to `ac_kw_optional`
only when a citation for the same variant says so:

- a cited `ac_kw_optional` (seed `cited:` value or a data/manual fact) agrees with it
  within the `ac_kw` tolerance, and
- no cited `ac_kw` agrees with it (then the source means the standard charger).

Citations count here even when their source can't ship yet (maker-docs, manual: Q-008):
like guard_contradicted (A-06 F3) they are evidence that classifies a releasable value,
never a published value themselves. Without such a citation nothing moves, and the
merged `ac_kw` stays what the sources say (Decision 034: "rows keep today's merged value").
A cited optional that is not above every cited standard is a data error: nothing moves
and the variant is listed for review.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from ev_pipeline.match.matcher import MatchedFact
from ev_pipeline.merge.merge import has_citation
from ev_pipeline.merge.policy import FieldPolicy
from ev_pipeline.schema_models import FactField

STANDARD = FactField.ac_kw
OPTIONAL = FactField.ac_kw_optional
ROUTE_NOTE = "routed to ac_kw_optional: matches a cited optional on-board charger (T-063)"


@dataclass(frozen=True)
class Routed:
    variant_id: str
    source_id: str
    value: float
    cited_optional: float
    cited_standard: float | None


@dataclass(frozen=True)
class RouteProblem:
    variant_id: str
    message: str


def _cited(facts: list[MatchedFact], field: FactField) -> list[float]:
    return [
        float(mf.fact.value)
        for mf in facts
        if mf.fact.field == field and has_citation(mf) and isinstance(mf.fact.value, int | float)
    ]


def route_optional_ac(
    by_variant: dict[str, list[MatchedFact]],
    evidence: dict[str, list[MatchedFact]],
    policy: FieldPolicy,
) -> tuple[dict[str, list[MatchedFact]], list[Routed], list[RouteProblem]]:
    """Return `by_variant` with matching source `ac_kw` facts moved to `ac_kw_optional`."""
    out: dict[str, list[MatchedFact]] = {}
    routed: list[Routed] = []
    problems: list[RouteProblem] = []
    for vid, facts in by_variant.items():
        pool = facts + evidence.get(vid, [])
        opts = _cited(pool, OPTIONAL)
        stds = _cited(pool, STANDARD)
        if not opts:
            out[vid] = facts
            continue
        if stds and min(opts) <= max(stds):
            problems.append(
                RouteProblem(
                    vid,
                    f"cited ac_kw_optional {min(opts):g} kW is not above cited ac_kw "
                    f"{max(stds):g} kW; nothing routed",
                )
            )
            out[vid] = facts
            continue
        new: list[MatchedFact] = []
        for mf in facts:
            v = mf.fact.value
            if (
                mf.fact.field == STANDARD
                and not has_citation(mf)
                and isinstance(v, int | float)
                and not any(policy.agree(v, s) for s in stds)
            ):
                match = next((o for o in opts if policy.agree(v, o)), None)
                if match is not None:
                    note = f"{mf.note}; {ROUTE_NOTE}" if mf.note else ROUTE_NOTE
                    fact = mf.fact.model_copy(update={"field": OPTIONAL})
                    new.append(replace(mf, fact=fact, note=note))
                    routed.append(
                        Routed(vid, mf.source_id, float(v), match, max(stds) if stds else None)
                    )
                    continue
            new.append(mf)
        out[vid] = new
    return out, routed, problems
