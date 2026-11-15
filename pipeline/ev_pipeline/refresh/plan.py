"""Which sources `ev refresh` runs, and why (addendum 6 P1).

A source is **refreshable** when data/sources.yaml lists it as `active`, it has an adapter at
`ev_pipeline/sources/<id_with_underscores>/adapter.py` with `fetch_cmd` and `normalise_cmd`,
it is not permission-pending (`nyland`), and every env var in the adapter's optional
`REQUIRES_ENV` list is set (sources that need API keys are skipped, not failed).

It is **due** when its cadence (data/sources.yaml) has passed since it was last checked, when
it was never checked, or when its staging file is missing (a fresh machine). Cadences without
a fixed interval (`ad hoc`, `per release`, `n/a`) are never due on their own.
`--sources a,b` runs the named sources now whatever their cadence; `--force` runs all.
"""

from __future__ import annotations

import importlib
import importlib.util
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml

from ev_pipeline.release.gate import RELEASABLE_STATUSES

CADENCE_DAYS: dict[str, float] = {
    "hourly": 1 / 24,
    "daily": 1,
    "nightly": 1,
    "weekly": 7,
    "fortnightly": 14,
    "monthly": 30,
    "quarterly": 91,
    "twice yearly": 182,
    "yearly": 365,
    "annual": 365,
}
SLACK = timedelta(hours=12)
"""A weekly cron that starts a little earlier than last week still counts weekly sources."""
PERMISSION_PENDING = {"nyland"}


def cadence_interval(cadence: str | None) -> timedelta | None:
    days = CADENCE_DAYS.get(str(cadence or "").strip().lower())
    return timedelta(days=days) if days is not None else None


def module_name(source_id: str) -> str:
    return f"ev_pipeline.sources.{source_id.replace('-', '_')}.adapter"


def find_adapter(source_id: str) -> ModuleType | None:
    name = module_name(source_id)
    try:
        if importlib.util.find_spec(name) is None:
            return None
    except ModuleNotFoundError:
        return None
    mod = importlib.import_module(name)
    if not (hasattr(mod, "fetch_cmd") and hasattr(mod, "normalise_cmd")):
        return None
    return mod


def raw_dir_name(mod: ModuleType) -> str:
    return str(getattr(mod, "DIR", None) or mod.NAME)


def registry_entries(data_dir: Path) -> list[dict[str, Any]]:
    path = data_dir / "sources.yaml"
    if not path.exists():
        return []
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return [e for e in doc.get("sources") or [] if isinstance(e, dict) and e.get("id")]


@dataclass
class PlannedSource:
    id: str
    cadence: str | None
    action: str  # run | not_due | skip
    reason: str
    adapter: ModuleType | None = field(default=None, repr=False)
    registry: dict[str, Any] = field(default_factory=dict, repr=False)


def plan(
    data_dir: Path,
    state: dict[str, dict[str, Any]],
    now: datetime,
    only: list[str] | None = None,
    force: bool = False,
    env: dict[str, str] | None = None,
    find: Any = None,
) -> list[PlannedSource]:
    env = dict(os.environ if env is None else env)
    find = find or find_adapter
    entries = registry_entries(data_dir)
    known = {str(e["id"]) for e in entries}
    out: list[PlannedSource] = []
    for sid in only or []:
        if sid not in known:
            out.append(PlannedSource(sid, None, "skip", "not in data/sources.yaml"))
    for e in entries:
        sid = str(e["id"])
        if only and sid not in only:
            continue
        cad = e.get("cadence")
        if e.get("status") not in RELEASABLE_STATUSES:
            if only:
                out.append(PlannedSource(sid, cad, "skip", f"status {e.get('status')}"))
            continue
        if sid in PERMISSION_PENDING:
            out.append(PlannedSource(sid, cad, "skip", "permission pending"))
            continue
        mod = find(sid)
        if mod is None:
            if only:
                out.append(PlannedSource(sid, cad, "skip", "no adapter"))
            continue
        missing = [k for k in getattr(mod, "REQUIRES_ENV", []) or [] if not env.get(k)]
        if missing:
            out.append(PlannedSource(sid, cad, "skip", f"needs {', '.join(missing)}", mod, e))
            continue
        action, reason = _due(sid, cad, state.get(sid) or {}, now, data_dir)
        if force or only:
            action, reason = "run", ("forced" if force else "named on the command line")
        out.append(PlannedSource(sid, cad, action, reason, mod, e))
    return out


def _due(
    sid: str, cadence: str | None, entry: dict[str, Any], now: datetime, data_dir: Path
) -> tuple[str, str]:
    if not (data_dir / "staging" / f"{sid}.records.jsonl").exists():
        return "run", "no staging file"
    last = entry.get("last_checked")
    if not last:
        return "run", "never checked"
    interval = cadence_interval(cadence)
    if interval is None:
        return "not_due", f"cadence {cadence!r} has no fixed interval"
    try:
        when = datetime.fromisoformat(str(last))
    except ValueError:
        return "run", "unreadable last_checked"
    if now - when >= interval - SLACK:
        return "run", f"{cadence}: last checked {when.date().isoformat()}"
    nxt = (when + interval - SLACK).date().isoformat()
    return "not_due", f"{cadence}: next from {nxt}"
