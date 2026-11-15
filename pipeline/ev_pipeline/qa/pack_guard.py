"""Pack guard (T-057): a usable-capacity fact larger than the gross capacity of the variant's
linked battery pack cannot describe that pack, so it is kept out of the merge and listed in
data/review/conflicts.csv instead ("AI proposes, rules decide"; values are never edited).

Why: an attach-only source can place a later model year's figure on a variant whose link
points at the earlier pack. Example (T-057): KilowattApp lists the 2024+ Kia EV6 facelift
(84 kWh gross pack) at 80 kWh usable; that record lands on kia-ev6-gen1-77kwh-awd, linked to
egmp-77-4 (77.4 kWh gross). Its source ranks above seed-manual, so 80 won the median and the
release QA flagged `usable 80.0 > gross 77.4 kWh`.

Rules:
- Only `battery_kwh_net` facts, only variants whose link (variant beats generation) names one
  `battery_pack_id` with a numeric `gross_kwh`. `battery_pack_options` are ambiguous: skipped.
- A fact is impossible when value > gross + ROUNDING_KWH (row values are rounded to 0.1 kWh).
- If every `battery_kwh_net` fact of a variant is impossible, nothing is removed: then the
  link itself is the likely error, and the release QA `usable_gt_gross` check flags it.
"""

from __future__ import annotations

from typing import Any

from ev_pipeline.derive.links import Links
from ev_pipeline.match.matcher import MatchedFact
from ev_pipeline.qa.checks import EPS, ROUNDING_KWH

FIELD = "battery_kwh_net"


def linked_gross_kwh(links: Links, generation_of: dict[str, str]) -> dict[str, tuple[str, float]]:
    """variant id -> (pack id, gross kWh) for variants linked to exactly one pack."""
    out: dict[str, tuple[str, float]] = {}
    for vid, gid in generation_of.items():
        pid = links.link_for(vid, gid).get("battery_pack_id")
        g = (links.packs.get(pid) or {}).get("gross_kwh") if pid else None
        if isinstance(g, int | float) and not isinstance(g, bool):
            out[vid] = (str(pid), float(g))
    return out


def _value(mf: MatchedFact) -> float | None:
    v = mf.fact.value
    return float(v) if isinstance(v, int | float) and not isinstance(v, bool) else None


def split_impossible(
    facts: list[MatchedFact], gross: float
) -> tuple[list[MatchedFact], list[MatchedFact]]:
    """(kept, rejected): rejected = battery_kwh_net facts above `gross`. Keeps everything when
    no battery_kwh_net fact would be left."""
    rejected = [
        mf
        for mf in facts
        if mf.fact.field.value == FIELD
        and (v := _value(mf)) is not None
        and v > gross + ROUNDING_KWH + EPS
    ]
    if not rejected:
        return facts, []
    left = [mf for mf in facts if mf.fact.field.value == FIELD and mf not in rejected]
    if not left:
        return facts, []
    return [mf for mf in facts if mf not in rejected], rejected


def guard_usable_vs_pack(
    by_variant: dict[str, list[MatchedFact]],
    links: Links,
    generation_of: dict[str, str],
) -> tuple[dict[str, list[MatchedFact]], list[dict[str, Any]]]:
    """Facts per variant with impossible usable figures removed, plus conflict rows (same
    columns as release.build.conflict_rows) for data/review/conflicts.csv."""
    gross = linked_gross_kwh(links, generation_of)
    out: dict[str, list[MatchedFact]] = {}
    conflicts: list[dict[str, Any]] = []
    for vid in sorted(by_variant):
        facts = by_variant[vid]
        if vid not in gross:
            out[vid] = facts
            continue
        pid, g = gross[vid]
        kept, rejected = split_impossible(facts, g)
        out[vid] = kept
        for mf in rejected:
            conflicts.append(
                {
                    "variant_id": vid,
                    "field": FIELD,
                    "source_id": mf.source_id,
                    "value": mf.fact.value,
                    "unit": mf.fact.unit,
                    "winning_value": None,  # filled in after the merge
                    "tolerance": f"> pack {pid} gross {g:g} kWh",
                    "fact_id": mf.fact.id,
                }
            )
    return out, conflicts


def fill_winning_values(conflicts: list[dict[str, Any]], merged: dict[str, Any]) -> None:
    """Set `winning_value` from the merged results (dict vid -> field -> Merged)."""
    for c in conflicts:
        mg = (merged.get(c["variant_id"]) or {}).get(c["field"])
        c["winning_value"] = getattr(mg, "value", None)
