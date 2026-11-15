"""Q-019 option (a): generation-level corroboration (EEA averages), never a value.

`match_records` (flag `EV_EEA_CORROBORATION`) turns EEA's registration-weighted range and
consumption averages into generation facts, one per generation and field. Here each one is
offered to every variant of that generation that (1) was on sale in the average's year and
(2) has a merged value for the field. When the average is within that field's tolerance
(data/field_sources.yaml) of the merged value, the source counts as one more agreeing
independent source: `independent_agreeing` + 1, its id joins `source_ids` / `fact_ids` and the
provenance note says so. The value, the winner, the conflicts and the confidence never change,
and a source that already agrees with the value is not counted twice. Outside tolerance it is
simply not used (no conflict: an average is not a competing value).
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from ev_pipeline.match.matcher import MatchedFact, VariantInfo
from ev_pipeline.merge.merge import NOT_INDEPENDENT, Merged
from ev_pipeline.merge.policy import Policies


def variant_covers(info: VariantInfo, year: int | None) -> bool:
    """Was this variant on sale in `year`? Unknown years count as yes (the generation fits)."""
    if year is None or not info.years:
        return True
    start, last = min(info.years), max(info.years)
    if year < start:
        return False
    if info.explicit_end is not None:
        return year <= info.explicit_end
    return info.open_end or year <= last


def _agreeing_independent(mg: Merged) -> set[str]:
    return {s for s in mg.source_ids if s not in NOT_INDEPENDENT}


def apply_corroboration(
    merged: dict[str, dict[str, Merged]],
    variants: dict[str, VariantInfo],
    corroboration: list[MatchedFact],
    policies: Policies | None = None,
) -> tuple[list[MatchedFact], dict[str, Any]]:
    """Apply corroboration facts in place. Returns (facts used, run-log summary)."""
    policies = policies or Policies()
    by_gen: dict[str, list[str]] = {}
    for vid, info in variants.items():
        by_gen.setdefault(info.generation_id, []).append(vid)
    used: dict[str, MatchedFact] = {}
    outcome: Counter[str] = Counter()
    agreed: Counter[str] = Counter()  # field -> variants corroborated
    for c in corroboration:
        fname = c.fact.field.value
        policy = policies.for_field(fname)
        for vid in sorted(by_gen.get(str(c.generation_id), [])):
            if not variant_covers(variants[vid], c.year):
                outcome["variant not on sale that year"] += 1
                continue
            mg = merged.get(vid, {}).get(fname)
            if mg is None:
                outcome["no merged value"] += 1
                continue
            if c.source_id in mg.source_ids:
                outcome["source already agrees"] += 1
                continue
            if not policy.agree(mg.value, c.fact.value):
                outcome["outside tolerance"] += 1
                continue
            before = _agreeing_independent(mg)
            mg.source_ids.append(c.source_id)
            mg.fact_ids.append(c.fact.id)
            mg.corroborations.append(c)
            if c.source_id not in NOT_INDEPENDENT and c.source_id not in before:
                mg.independent_agreeing += 1
            used[c.fact.id] = c
            outcome["agrees"] += 1
            agreed[fname] += 1
    log = {
        "facts_offered": len(corroboration),
        "facts_used": len(used),
        "outcomes": dict(sorted(outcome.items())),
        "variants_corroborated_by_field": dict(sorted(agreed.items())),
    }
    return [used[k] for k in sorted(used)], log
