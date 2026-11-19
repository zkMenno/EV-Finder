"""T-158: checks on `config/approved_changes.yaml` before a PR merges.

- G-57: the file parses the way the release build reads it (`differ.load_config`), so a bad
  `approved_by` or `release` fails in data QA, not first in a release build.
- G-54: an approval this branch adds (not in the base ref's file) whose `release` is at or
  below the latest published release can never apply: that release is already built, and the
  intended change lands in the next one unapproved, blocking main's next build. Warned, with
  the release to use instead.

Pure functions; `ev release approvals` (commands/releases.py) and scripts/merge_ready.py
call them. No network.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import yaml

from ev_pipeline.release.differ import CONFIG_FILE, DiffConfigError, load_config

REL_PATH = "config/approved_changes.yaml"


def _key(entry: Any) -> str:
    return json.dumps(entry, sort_keys=True, default=str)


def new_entries(head_doc: dict[str, Any] | None, base_doc: dict[str, Any] | None) -> list[Any]:
    """`approved` entries in head that the base file doesn't have (exact entry match)."""
    base = {_key(e) for e in ((base_doc or {}).get("approved") or [])}
    return [e for e in ((head_doc or {}).get("approved") or []) if _key(e) not in base]


def _releases(entry: Any) -> list[int] | None:
    rel = entry.get("release") if isinstance(entry, dict) else None
    if rel is None:
        return None
    items = rel if isinstance(rel, list) else [rel]
    return [x for x in items if isinstance(x, int) and not isinstance(x, bool)] or None


def stale_warnings(entries: list[Any], latest: int | None) -> list[str]:
    """G-54: one plain line per new entry scoped only to releases that are already built."""
    if latest is None:
        return []
    out = []
    for e in entries:
        rels = _releases(e)
        if rels is None or max(rels) > latest:
            continue
        what = ":".join(str(e.get(k, "*")) for k in ("file", "id", "field"))
        out.append(
            f"approval {what} ({e.get('approved_by', '?')}) is scoped to release"
            f" {', '.join(map(str, rels))}, but release {latest} is already published: it can"
            f" never apply. Scope it to release {latest + 1} (G-54)."
        )
    return out


def latest_published(data_dir: Path) -> int | None:
    p = data_dir / "releases" / "latest"
    try:
        t = p.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return int(t) if t.isdigit() else None


def base_doc_from_git(repo: Path, ref: str) -> dict[str, Any] | None:
    """The base ref's file, or None when the ref or the file is missing."""
    cp = subprocess.run(
        ["git", "-C", str(repo), "show", f"{ref}:{REL_PATH}"], capture_output=True, text=True
    )
    if cp.returncode != 0:
        return None
    doc = yaml.safe_load(cp.stdout)
    return doc if isinstance(doc, dict) else None


def check(
    path: Path = CONFIG_FILE, base_doc: dict[str, Any] | None = None, latest: int | None = None
) -> tuple[list[str], list[str]]:
    """(errors, warnings). Errors = the file doesn't load (G-57); warnings = G-54."""
    try:
        load_config(path)
    except DiffConfigError as e:
        return [str(e)], []
    head = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [], stale_warnings(new_entries(head, base_doc), latest)
