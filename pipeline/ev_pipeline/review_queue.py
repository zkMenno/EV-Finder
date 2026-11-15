"""Review queue ids and status for data/review/*.csv (addendum 6, P7).

Every row of every data/review/*.csv gets two leading columns:

- `review_id`: stable short id, `<prefix>-<10 hex>` = sha1 of (source_id, record key, reason).
  Counts that change between runs ("(4x)", ": 12 records") are left out of the reason, so the
  same problem keeps its id across rebuilds. Identical rows in one file get `~2`, `~3`.
- `status`: open | done | wont-fix.

Staff decisions live durably in data/review/status.yaml, keyed by review_id. A rebuild
rewrites the CSVs, so the release first harvests any status someone typed into the old CSVs
(`snapshot_statuses`, before writing) and stores it in status.yaml; then `annotate_review_dir`
adds the two columns to the new CSVs from status.yaml. Ids that disappear stay in status.yaml,
so a problem that comes back keeps its decision.
"""

from __future__ import annotations

import csv
import hashlib
import re
import sys
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

import yaml

STATUSES = ("open", "done", "wont-fix")
DEFAULT_STATUS = "open"
STATUS_FILE = "status.yaml"
STATUS_FORMAT = "review-status/v1"
ID_COLUMNS = ["review_id", "status"]

_COUNT_RE = re.compile(r"\s*\(\d+x\)|:\s*\d+ records")

Row = dict[str, str]


def _norm_reason(reason: str) -> str:
    return _COUNT_RE.sub("", reason or "").strip()


def _key_unmatched(r: Row) -> tuple[str, str, str]:
    key = "|".join(r.get(c, "") for c in ("record_key", "make", "model", "variant_name", "year"))
    return r.get("source_id", ""), key, _norm_reason(r.get("reason", ""))


def _key_validation(r: Row) -> tuple[str, str, str]:
    key = "|".join(r.get(c, "") for c in ("stage", "record_key", "subject_id", "field"))
    return r.get("source_id", ""), key, _norm_reason(r.get("reason", ""))


def _key_conflicts(r: Row) -> tuple[str, str, str]:
    key = r.get("fact_id") or f"{r.get('variant_id', '')}|{r.get('field', '')}"
    reason = f"conflict {r.get('field', '')}: {r.get('value', '')} {r.get('unit', '')}"
    return r.get("source_id", ""), key, reason.strip()


def _key_generic(r: Row) -> tuple[str, str, str]:
    if "record_key" in r:
        return r.get("source_id", ""), r["record_key"], _norm_reason(r.get("reason", ""))
    body = "|".join(f"{k}={v}" for k, v in sorted(r.items()))
    return r.get("source_id", ""), body, _norm_reason(r.get("reason", ""))


KEYS: dict[str, tuple[str, Callable[[Row], tuple[str, str, str]]]] = {
    "unmatched": ("um", _key_unmatched),
    "validation": ("va", _key_validation),
    "conflicts": ("cf", _key_conflicts),
}


def review_id(prefix: str, source_id: str, record_key: str, reason: str) -> str:
    h = hashlib.sha1(f"{source_id}\x1f{record_key}\x1f{reason}".encode()).hexdigest()
    return f"{prefix}-{h[:10]}"


def _ids_for(name: str, rows: list[Row]) -> list[str]:
    prefix, keyf = KEYS.get(name, (name[:2] or "rv", _key_generic))
    seen: dict[str, int] = {}
    out = []
    for r in rows:
        rid = review_id(prefix, *keyf(r))
        n = seen.get(rid, 0) + 1
        seen[rid] = n
        out.append(rid if n == 1 else f"{rid}~{n}")
    return out


def _read_csv(path: Path) -> tuple[list[str], list[Row]]:
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        header = list(reader.fieldnames or [])
        return header, [dict(r) for r in reader]


def _status_doc(review_dir: Path) -> dict[str, Any]:
    p = review_dir / STATUS_FILE
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def load_status(review_dir: Path) -> dict[str, dict[str, Any]]:
    """review_id -> entry (`status`, optional `note`, `file`, `summary`, `updated`)."""
    out: dict[str, dict[str, Any]] = {}
    for rid, entry in (_status_doc(review_dir).get("items") or {}).items():
        entry = entry if isinstance(entry, dict) else {"status": entry}
        st = str(entry.get("status", DEFAULT_STATUS))
        if st not in STATUSES:
            print(f"review status.yaml: {rid}: unknown status {st!r}, kept as is", file=sys.stderr)
        out[str(rid)] = dict(entry)
    return out


def load_written(review_dir: Path) -> dict[str, str]:
    """review_id -> status the last build wrote into a CSV (non-open only)."""
    return {str(k): str(v) for k, v in (_status_doc(review_dir).get("written") or {}).items()}


def save_status(
    review_dir: Path, items: dict[str, dict[str, Any]], written: dict[str, str]
) -> None:
    review_dir.mkdir(parents=True, exist_ok=True)
    header = (
        "# Review queue decisions, keyed by review_id (data/review/*.csv). Durable: rebuilds\n"
        "# never drop entries. status: open | done | wont-fix (optional `note`). Edit `items`\n"
        "# here, or a CSV's `status` column; the next `ev release` copies CSV edits in here.\n"
        "# `written` is kept by the pipeline (what the last build wrote): don't edit it.\n"
    )
    body = yaml.safe_dump(
        {
            "schema": STATUS_FORMAT,
            "items": dict(sorted(items.items())),
            "written": dict(sorted(written.items())),
        },
        sort_keys=False,
        allow_unicode=True,
        width=100,
    )
    (review_dir / STATUS_FILE).write_text(header + body, encoding="utf-8")


def snapshot_statuses(review_dir: Path) -> dict[str, tuple[str, str]]:
    """review_id -> (status, file) from the CSVs as they are now, before a rebuild."""
    out: dict[str, tuple[str, str]] = {}
    if not review_dir.is_dir():
        return out
    for path in sorted(review_dir.glob("*.csv")):
        header, rows = _read_csv(path)
        if "review_id" not in header or "status" not in header:
            continue
        for r in rows:
            rid, st = (r.get("review_id") or "").strip(), (r.get("status") or "").strip()
            if rid and st:
                out[rid] = (st, path.stem)
    return out


def _summary(name: str, r: Row) -> str:
    cols = {
        "unmatched": ("source_id", "make", "model", "reason"),
        "validation": ("source_id", "subject_id", "field", "reason"),
        "conflicts": ("variant_id", "field", "source_id", "value"),
    }.get(name, tuple(list(r)[:4]))
    return " | ".join(r.get(c, "") for c in cols if r.get(c))[:160]


def annotate_review_dir(
    review_dir: Path,
    previous: dict[str, tuple[str, str]] | None = None,
    today: date | None = None,
) -> dict[str, Any]:
    """Add review_id + status to every data/review/*.csv; merge CSV edits into status.yaml.

    `previous` comes from `snapshot_statuses`, taken before the CSVs were rewritten. A CSV
    status that differs from what the last build wrote there (status.yaml `written`) is a
    staff edit: it wins and is saved in `items`. Otherwise status.yaml decides, so an edit
    made in status.yaml is never undone by the stale CSV. Returns counts for the run log.
    """
    today = today or date.today()
    items = load_status(review_dir)
    old_written = load_written(review_dir)
    before_text = repr((items, old_written))
    for rid, (st, fname) in sorted((previous or {}).items()):
        if st == old_written.get(rid, DEFAULT_STATUS):
            continue  # untouched since the last build
        if st not in STATUSES:
            print(f"review {fname}.csv: {rid}: unknown status {st!r} ignored", file=sys.stderr)
            continue
        entry = items.setdefault(rid, {})
        if entry.get("status", DEFAULT_STATUS) != st:
            entry.update({"status": st, "file": fname, "updated": today.isoformat()})
    counts: dict[str, Any] = {}
    written: dict[str, str] = {}
    seen: set[str] = set()
    if review_dir.is_dir():
        for path in sorted(review_dir.glob("*.csv")):
            header, rows = _read_csv(path)
            base = [c for c in header if c not in ID_COLUMNS]
            clean = [{c: r.get(c) or "" for c in base} for r in rows]
            ids = _ids_for(path.stem, clean)
            c = dict.fromkeys(STATUSES, 0)
            with path.open("w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(ID_COLUMNS + base)
                for rid, r in zip(ids, clean, strict=True):
                    entry = items.get(rid)
                    st = str(entry.get("status", DEFAULT_STATUS)) if entry else DEFAULT_STATUS
                    if entry is not None and "summary" not in entry:
                        entry["summary"] = _summary(path.stem, r)
                        entry.setdefault("file", path.stem)
                    if st != DEFAULT_STATUS:
                        written[rid] = st
                    c[st] = c.get(st, 0) + 1
                    seen.add(rid)
                    w.writerow([rid, st, *(r[col] for col in base)])
            counts[path.stem] = {"rows": len(rows), **c}
    if repr((items, written)) != before_text:
        save_status(review_dir, items, written)
    counts["status_yaml_entries"] = len(items)
    counts["status_yaml_not_in_csvs"] = len(set(items) - seen)
    return counts
