"""G-49 (T-153): `ev refresh` holds data/staging/ while it writes it; `ev verify` refuses to
rebuild from a half-written staging.

The lock is a small JSON file `data/staging/.refresh.lock` ({"pid", "started"}). It is held
for the whole refresh (not for --dry-run). A lock whose process no longer runs (a crash,
a killed job) is stale: it does not count as held, and the next refresh replaces it. A
second refresh while a live one holds the lock refuses to start (`StagingBusy`): the lock is
created exclusively, so two refreshes never share or delete each other's lock.

T-158: every refresh that takes the lock also writes `data/staging/.refresh.last`
({"pid", "started"}) and leaves it in place, so `ev verify` can tell that a refresh ran during
its rebuild even when that refresh was short and has already finished. A refused refresh says
so in its own words (`busy_message(.., "refresh")`), not verify's.
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
LAST_NAME = ".refresh.last"


class StagingBusy(RuntimeError):
    """Another live `ev refresh` holds data/staging."""


def lock_path(data_dir: Path) -> Path:
    return data_dir / "staging" / LOCK_NAME


def last_path(data_dir: Path) -> Path:
    return data_dir / "staging" / LAST_NAME


def last_run(data_dir: Path) -> str | None:
    """The stamp of the last refresh that took the lock (raw text), or None if none ever did."""
    try:
        return last_path(data_dir).read_text(encoding="utf-8")
    except OSError:
        return None


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
    """Hold the staging lock for the duration of the block (removed on any exit). Raises
    StagingBusy when a live process already holds it; a stale lock is taken over."""
    p = lock_path(data_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    started = (now or datetime.now(UTC)).isoformat(timespec="seconds")
    body = json.dumps({"pid": os.getpid(), "started": started}) + "\n"
    for _ in range(2):
        try:
            fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        except FileExistsError:
            if holder(data_dir) is not None:
                raise StagingBusy(
                    busy_message(data_dir, "refresh") or "data/staging is locked"
                ) from None
            p.unlink(missing_ok=True)  # stale: its process is gone
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(body)
        last = last_path(data_dir)
        tmp = last.with_name(f"{LAST_NAME}.tmp-{os.getpid()}")
        tmp.write_text(body, encoding="utf-8")
        os.replace(tmp, last)  # T-158: stays after the run; verify compares it before / after
        break
    else:
        raise StagingBusy(f"could not take {p}")
    try:
        yield p
    finally:
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            doc = {}
        if doc.get("pid") == os.getpid():  # never remove another process's lock
            p.unlink(missing_ok=True)


def busy_message(data_dir: Path, command: str) -> str | None:
    """Plain message when a live refresh holds staging, worded for `command` ("verify" or
    "refresh"), else None."""
    h = holder(data_dir)
    if h is None:
        return None
    who = f"process {h['pid']}" if h.get("pid") else "an unknown process"
    since = f" since {h['started']}" if h.get("started") else ""
    if command == "refresh":
        return (
            f"another ev refresh is already writing data/staging ({who}{since}). Wait for it to "
            "finish; two refreshes must not write staging at once (G-49). "
            f"If no ev refresh is running, delete {lock_path(data_dir)}."
        )
    return (
        f"ev refresh is still writing data/staging ({who}{since}). Wait for it to finish, "
        "then run ev verify again (a half-written staging gives a wrong rebuild, G-49). "
        f"If no ev refresh is running, delete {lock_path(data_dir)}."
    )


def refusal(data_dir: Path) -> str | None:
    """Plain message for `ev verify` when a refresh holds staging, else None."""
    return busy_message(data_dir, "verify")
