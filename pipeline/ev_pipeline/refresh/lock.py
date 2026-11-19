"""G-49 (T-153): `ev refresh` holds data/staging/ while it writes it; `ev verify` refuses to
rebuild from a half-written staging.

The lock is a small JSON file `data/staging/.refresh.lock` ({"pid", "started"}). It is held
for the whole refresh (not for --dry-run). A lock whose process no longer runs (a crash,
a killed job) is stale: it does not count as held, and the next refresh replaces it.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

LOCK_NAME = ".refresh.lock"


def lock_path(data_dir: Path) -> Path:
    return data_dir / "staging" / LOCK_NAME


def _alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # another user's process: it exists
    return True


def holder(data_dir: Path) -> dict[str, Any] | None:
    """The live lock's content, or None when no refresh holds staging (no file, or stale)."""
    p = lock_path(data_dir)
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, ValueError):
        return {"pid": None, "started": None, "note": "unreadable lock file"}
    pid = doc.get("pid")
    if isinstance(pid, int) and not _alive(pid):
        return None
    return doc if isinstance(doc, dict) else {"pid": None, "started": None}


@contextmanager
def hold(data_dir: Path, now: datetime | None = None) -> Iterator[Path]:
    """Hold the staging lock for the duration of the block (removed on any exit)."""
    p = lock_path(data_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    started = (now or datetime.now(UTC)).isoformat(timespec="seconds")
    p.write_text(json.dumps({"pid": os.getpid(), "started": started}) + "\n", encoding="utf-8")
    try:
        yield p
    finally:
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            doc = {}
        if doc.get("pid") == os.getpid():  # never remove another process's lock
            p.unlink(missing_ok=True)


def refusal(data_dir: Path) -> str | None:
    """Plain message for `ev verify` when a refresh holds staging, else None."""
    h = holder(data_dir)
    if h is None:
        return None
    who = f"process {h['pid']}" if h.get("pid") else "an unknown process"
    since = f" since {h['started']}" if h.get("started") else ""
    return (
        f"ev refresh is still writing data/staging ({who}{since}). Wait for it to finish, "
        "then run ev verify again (a half-written staging gives a wrong rebuild, G-49)."
    )
