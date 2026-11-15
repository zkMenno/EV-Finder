"""T-059: outside production years corroborate a generation's hand-entered years.

Inputs are `kind="corroboration"` records of a year source (matcher.YEAR_CORROBORATION_SOURCES,
today only `wikidata`): no specs, the year in `year`, our model id, the item and the boundary in
`record_key` (`wikidata:volkswagen-id3/Q63636478#production_start:P571`).

Each year is compared with the nearest generation boundary of the same kind in that model:
a production start with the generations' `year_start`, an end with their `year_end` (ties go to
the older generation). Within YEAR_TOLERANCE (1 year) it agrees. An end year for a model whose
generations are all still on sale goes to the newest generation and disagrees (the seed says
"on sale"). The check is attached to that generation as `years_corroboration`; a generation is
`corroborated` when every check on it agrees.

**Never a value.** Years are never changed or set from here, and no check is offered to a
generation of another model. Records whose model is not in the seed are counted and skipped.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from ev_pipeline.match.seed import Seed, SeedGeneration
from ev_pipeline.records import SourceRecord

YEAR_TOLERANCE = 1
_KEY = re.compile(
    r"^(?P<src>[a-z0-9-]+):(?P<model>[^/]+)/(?P<item>[^#]+)#production_(?P<b>start|end):"
)


@dataclass
class YearsResult:
    by_generation: dict[str, dict[str, Any]] = field(default_factory=dict)
    sources: dict[str, dict[str, Any]] = field(default_factory=dict)  # source id -> Source
    log: dict[str, Any] = field(default_factory=dict)


def _nearest(gens: list[SeedGeneration], year: int, boundary: str) -> tuple[SeedGeneration, bool]:
    if boundary == "start":
        pool = [(abs(year - g.year_start), g.year_start, g) for g in gens]
    else:
        pool = [(abs(year - g.year_end), g.year_start, g) for g in gens if g.year_end is not None]
        if not pool:  # every generation still on sale: the seed has no end to agree with
            return max(gens, key=lambda g: g.year_start), False
    diff, _, gen = min(pool, key=lambda t: (t[0], t[1]))
    return gen, diff <= YEAR_TOLERANCE


def corroborate_years(records: list[SourceRecord], seed: Seed) -> YearsResult:
    out = YearsResult()
    skipped: Counter[str] = Counter()
    checks: dict[str, list[dict[str, Any]]] = {}
    for rec in sorted(records, key=lambda r: r.record_key):
        m = _KEY.match(rec.record_key)
        if m is None or rec.year is None:
            skipped["no model id, boundary or year in the record"] += 1
            continue
        model = seed.models.get(m["model"])
        if model is None or not model.generations:
            skipped["model not in seed"] += 1
            continue
        gen, agrees = _nearest(model.generations, rec.year, m["b"])
        sid = rec.source.id.root
        check: dict[str, Any] = {
            "boundary": m["b"],
            "year": rec.year,
            "agrees": agrees,
            "source_id": sid,
            "source_record": rec.record_key,
            "retrieved_at": rec.retrieved_at.isoformat(),
        }
        if rec.variant_name:
            check["label"] = rec.variant_name
        checks.setdefault(gen.id, []).append(check)
        out.sources.setdefault(sid, rec.source.model_dump(mode="json", exclude_none=True))
    agreements: list[dict[str, Any]] = []
    disagreements: list[dict[str, Any]] = []
    for gid in sorted(checks):
        cs = checks[gid]
        out.by_generation[gid] = {
            "corroborated": all(c["agrees"] for c in cs),
            "tolerance_years": YEAR_TOLERANCE,
            "source_ids": sorted({c["source_id"] for c in cs}),
            "checks": cs,
        }
        g = seed.generations[gid]
        for c in cs:
            item = {
                "generation_id": gid,
                "boundary": c["boundary"],
                "source_year": c["year"],
                "seed_year": g.year_start if c["boundary"] == "start" else g.year_end,
                "source_record": c["source_record"],
            }
            (agreements if c["agrees"] else disagreements).append(item)
    out.log = {
        "records": len(records),
        "checks": len(agreements) + len(disagreements),
        "agree": len(agreements),
        "disagree": len(disagreements),
        "generations_checked": len(out.by_generation),
        "generations_corroborated": sum(1 for v in out.by_generation.values() if v["corroborated"]),
        "skipped": dict(sorted(skipped.items())),
        "disagreements": disagreements,
    }
    return out
