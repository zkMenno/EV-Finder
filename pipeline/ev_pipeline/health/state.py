"""Source health state (addendum 6 P3): last success, last change, row counts, fingerprint.

One entry per source. It lives in two places:

- `data/runs/sources-state.json` (git-ignored): updated by every `ev refresh`, also by runs
  that published nothing (unchanged sources, failures, drift).
- `data/releases/<n>/sources.json` (committed with the release): a copy at release time, for
  the staff page and the Nerd mode "as of" dates. A fresh machine (the GitHub Actions runner)
  has no local state, so it starts from the latest release's copy.

`load_state` merges both and keeps, per source, the entry checked most recently.

Status values: `ok` (new data accepted), `unchanged` (same content or 304), `failed`
(fetch/normalise error; previous data kept), `drift` (schema fingerprint broke; previous data
kept, review item written), `rows_dropped` (far fewer records than before; previous data kept,
review item written), `skipped` (needs a key, or no adapter), `not_due`.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from ev_pipeline.sources import _common as c

STATE_FILE = "sources-state.json"
SOURCES_JSON = "sources.json"
SCHEMA = "release-sources/v1"
REVIEW_FILE = "source-health.csv"
REVIEW_COLUMNS = ["id", "status", "opened_at", "source", "kind", "detail", "old", "new"]
KEEP_PREVIOUS = ("failed", "drift", "rows_dropped")


def runs_dir(data_dir: Path | None = None) -> Path:
    override = os.environ.get("EV_RUNS_DIR", "").strip()
    if override:
        return Path(override)
    return (data_dir or c.data_dir()) / "runs"


def state_path(data_dir: Path | None = None) -> Path:
    return runs_dir(data_dir) / STATE_FILE


def latest_release(data_dir: Path) -> int | None:
    path = data_dir / "releases" / "latest"
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return int(text) if text.isdigit() else None


def _read(path: Path) -> dict[str, dict[str, Any]]:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return dict(doc.get("sources") or {})


def load_state(data_dir: Path) -> dict[str, dict[str, Any]]:
    local = _read(state_path(data_dir))
    n = latest_release(data_dir)
    released = _read(data_dir / "releases" / str(n) / SOURCES_JSON) if n else {}
    out = dict(released)
    for sid, entry in local.items():
        other = out.get(sid)
        if other is None or str(entry.get("last_checked") or "") >= str(
            other.get("last_checked") or ""
        ):
            out[sid] = entry
    return out


def save_state(data_dir: Path, state: dict[str, dict[str, Any]]) -> Path:
    path = state_path(data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    doc = {"schema": "sources-state/v1", "saved_at": c.now_utc(), "sources": state}
    tmp.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return path


def public_entry(entry: dict[str, Any]) -> dict[str, Any]:
    """What goes into a release's sources.json: everything except the quarantined data."""
    return {k: v for k, v in entry.items() if k not in ("seen_fingerprint",)}


def charging_source_ids(charging: dict[str, Any] | None) -> set[str]:
    """Registry ids of the sources behind charging_stats.json (its aliases resolved)."""
    if not charging:
        return set()
    aliases = charging.get("source_aliases") or {}
    ids = {str(s["id"]) for s in charging.get("sources") or [] if s.get("id")}
    ids |= {str(st["source_id"]) for st in charging.get("stats") or [] if st.get("source_id")}
    return {str(aliases.get(i, i)) for i in ids}


def release_sources_doc(
    data_dir: Path,
    catalogue: dict[str, Any],
    registry_entries: list[dict[str, Any]],
    charging: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """sources.json for a release: the health entry of every refreshable source plus every
    source the catalogue or charging_stats.json cites (manual ones get `refresh: none`;
    A-05 L5: the charging sources were missing)."""
    state = load_state(data_dir)
    reg = {str(e.get("id")): e for e in registry_entries if e.get("id")}
    cited = {str(s["id"]) for s in catalogue.get("sources") or []}
    in_charging = charging_source_ids(charging)
    out: dict[str, dict[str, Any]] = {}
    for sid in sorted(set(state) | cited | in_charging):
        entry = dict(state.get(sid) or {"id": sid, "status": "not_refreshed", "refresh": "none"})
        r = reg.get(sid) or {}
        for k in ("name", "licence", "cadence"):
            if r.get(k) is not None:
                entry.setdefault(k, r[k])
        entry["registry_status"] = r.get("status")
        entry["in_catalogue"] = sid in cited
        if sid in in_charging:
            entry["in_charging_stats"] = True
        out[sid] = public_entry(entry)
    return {
        "schema": SCHEMA,
        "release": catalogue.get("release"),
        "generated_at": catalogue.get("generated_at"),
        "sources": out,
    }


# --- review items -----------------------------------------------------------------------


def review_id(source: str, kind: str, old: str, new: str) -> str:
    digest = hashlib.sha1(f"{source}|{kind}|{old}|{new}".encode()).hexdigest()[:10]
    return f"SH-{digest}"


def add_review_item(data_dir: Path, source: str, kind: str, detail: str, old: str, new: str) -> str:
    """Append one open item to data/review/source-health.csv unless that id is there."""
    rid = review_id(source, kind, old, new)
    path = data_dir / "review" / REVIEW_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    existing: set[str] = set()
    if path.exists():
        with path.open(encoding="utf-8", newline="") as fh:
            existing = {row.get("id", "") for row in csv.DictReader(fh)}
    if rid in existing:
        return rid
    new_file = not path.exists()
    with path.open("a", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=REVIEW_COLUMNS)
        if new_file:
            w.writeheader()
        w.writerow(
            {
                "id": rid,
                "status": "open",
                "opened_at": c.now_utc(),
                "source": source,
                "kind": kind,
                "detail": detail[:2000],
                "old": old,
                "new": new,
            }
        )
    return rid
