"""data/review/unmatched.csv: what matching could not place, kept small for a human."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from ev_pipeline.match.matcher import (
    AMBIGUOUS_EVIDENCE,
    NO_BATTERY_MATCH,
    NO_POWER_MATCH,
    TGK_MISFIT,
    TGK_TIE,
    MatchResult,
    UnmatchedRow,
)

UNMATCHED_COLUMNS = ["source_id", "record_key", "make", "model", "variant_name", "year", "reason"]
MAX_ROWS = 1900  # brief: keep the file under 2000 rows
# Reasons listed before the rest, so the row cap never cuts them (Q-086: RDW records the
# power gate held back sort after most sources and were cut entirely; battery-gate
# records, TGK ties and misfits likewise).
PRIORITY_REASONS = (NO_POWER_MATCH, NO_BATTERY_MATCH, AMBIGUOUS_EVIDENCE, TGK_TIE, TGK_MISFIT)


def _priority(row: UnmatchedRow) -> int:
    return 0 if any(p in row.reason for p in PRIORITY_REASONS) else 1


def unmatched_rows(result: MatchResult, max_rows: int = MAX_ROWS) -> list[UnmatchedRow]:
    """Detail rows for makes in the seed, then one summary row per other (source, make).

    If the detail rows alone would pass `max_rows`, they collapse to one row per
    (source, make, model, reason) with the record count in the reason. Rows with a
    PRIORITY_REASONS reason come first, so the cap cuts other rows before them.
    """
    detail = sorted(
        result.unmatched, key=lambda r: (r.source_id, r.make.upper(), r.model.upper(), r.year)
    )
    others = sorted(result.other_makes.items(), key=lambda kv: (-kv[1], kv[0]))
    if len(detail) > max_rows - min(len(others), 100):
        groups: Counter[tuple[str, str, str, str]] = Counter()
        first: dict[tuple[str, str, str, str], UnmatchedRow] = {}
        for r in detail:
            k = (r.source_id, r.make.upper(), r.model.upper(), r.reason)
            groups[k] += 1
            first.setdefault(k, r)
        detail = [
            UnmatchedRow(
                k[0], first[k].record_key, first[k].make, first[k].model, "", "", f"{k[3]} ({n}x)"
            )
            for k, n in sorted(groups.items())
        ]
    detail.sort(key=_priority)  # stable: keeps the order above within each group
    rows = detail[: max_rows - min(len(others), 100)]
    room = max_rows - len(rows)
    if len(others) > room:
        rest = sum(n for _, n in others[room - 1 :])
        others = [*others[: room - 1], (("*", "(other makes)"), rest)]
    summary = [
        UnmatchedRow(src, "(summary)", make, "", "", "", f"make not in seed: {n} records")
        for (src, make), n in others
    ]
    return rows + summary


def write_unmatched(path: Path, rows: list[UnmatchedRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(UNMATCHED_COLUMNS)
        for r in rows:
            w.writerow([getattr(r, c) for c in UNMATCHED_COLUMNS])
