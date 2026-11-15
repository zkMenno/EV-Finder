"""T-062 (pipeline part): retired variant ids, so stable ids never 404 (Decision 033).

`retired_ids: {old_id: successor_id | null}` is computed per release from:
1. the previous release's map (it never loses an entry, except an id that is live again:
   a live id must not redirect, so it leaves the map and the run log says so);
2. variant ids the previous release had and this one doesn't;
3. `data/seed/retired_ids.yaml` (hand-kept by WS3): `{schema: retired-ids/v1, ids: {old:
   new | null}}` names successors. An id that vanished without a hand-kept successor maps to
   null (the web shows a 410 page linking the generation).
Chains resolve to the last live id (a -> b -> c gives a -> c); a successor that isn't live
becomes null and is logged. The id itself never appears as its own successor.

Until the schema has `Catalogue.retired_ids` (requested from WS0), the map ships as
`retired_ids.json` next to the catalogue; once the schema has it, it goes into the
catalogue instead (`has_catalogue_field`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

FILE_NAME = "retired_ids.json"
SEED_FILE = "retired_ids.yaml"
FORMAT = "retired-ids/v1"


@dataclass
class RetiredResult:
    ids: dict[str, str | None] = field(default_factory=dict)
    log: dict[str, Any] = field(default_factory=dict)


def load_hand_kept(seed_dir: Path) -> dict[str, str | None]:
    p = seed_dir / SEED_FILE
    if not p.exists():
        return {}
    doc = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if doc.get("schema") != FORMAT:
        raise ValueError(f"{p}: schema must be {FORMAT}")
    return {str(k): (None if v is None else str(v)) for k, v in (doc.get("ids") or {}).items()}


def compute_retired(
    previous: dict[str, Any] | None,
    previous_retired: dict[str, str | None] | None,
    current_ids: set[str],
    hand_kept: dict[str, str | None],
) -> RetiredResult:
    out = RetiredResult()
    raw: dict[str, str | None] = dict(previous_retired or {})
    prev_ids = {str(r["variant_id"]) for r in (previous or {}).get("rows") or []}
    vanished = sorted(prev_ids - current_ids)
    for vid in vanished:
        raw.setdefault(vid, None)
    for old, new in hand_kept.items():
        raw[old] = new  # staff decisions win (also for entries from earlier releases)
    live_again = sorted(k for k in raw if k in current_ids)
    for k in live_again:
        del raw[k]

    def resolve(start: str) -> str | None:
        seen = {start}
        nxt = raw.get(start)
        while nxt is not None and nxt not in current_ids:
            if nxt in seen or nxt not in raw:
                return None
            seen.add(nxt)
            nxt = raw.get(nxt)
        return nxt

    dangling = []
    for old in sorted(raw):
        target = resolve(old)
        if raw[old] is not None and target is None:
            dangling.append(old)
        out.ids[old] = target
    out.log = {
        "retired": len(out.ids),
        "with_successor": sum(1 for v in out.ids.values() if v),
        "new_this_release": [v for v in vanished if v in out.ids],
        "live_again": live_again,
        "successor_not_live": dangling,
        "hand_kept": len(hand_kept),
    }
    return out


def has_catalogue_field(schema: dict[str, Any]) -> bool:
    cat = (schema.get("$defs") or {}).get("Catalogue") or {}
    return "retired_ids" in (cat.get("properties") or {})
