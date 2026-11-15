"""`ev refresh`: fetch → snapshot → fingerprint → normalise → release, for due sources only.

Per source (each step timed, with the process's peak memory so far):

1. **probe**: if the source has staging data and the previous fetch left validators (ETag /
   Last-Modified, or a git commit), ask upstream whether anything changed. Unchanged: stop.
   An adapter may offer its own cheap check, `probe_unchanged(client, previous_fetch_meta)`
   returning True / False / None (unknown); it is tried first.
2. **fetch**: the adapter's own `fetch_cmd()` (allowlisted `net.safe_client`, streaming),
   with every HTTP response's status, ETag and Last-Modified recorded.
3. **snapshot**: the raw folder goes into the snapshot store (content-addressed). Same
   content hash as the accepted data and staging present: unchanged, stop.
4. **fingerprint**: column names and types of the raw files. A breaking change (column or
   file gone) **fails closed**: the previous raw folder is restored from the snapshot store,
   staging is not touched, a review item goes to data/review/source-health.csv, and the source
   stays on its previous good data until `ev sources accept <id>`.
5. **normalise**: the adapter's `normalise_cmd()`. Staging is backed up first and put back if
   normalise fails or the record count falls below half of the previous count.

Then, if any source brought new data: `build_release` → blocking QA → `write_release`, with
`sources.json` (health per source) and `refresh.json` (this run's summary) in the release
folder. No release when nothing changed, when the catalogue would be identical, or when a
refreshable source has no staging data at all (a fresh machine whose fetch failed): a release
missing a whole source is never published.

The run log goes to `data/runs/<timestamp>.json` (git-ignored). Scheduling is the CLI (cron /
GitHub Actions) for now; pg-boss takes over when the database exists (Decision 021).
"""

from __future__ import annotations

import json
import resource
import shutil
import sys
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ev_pipeline import net
from ev_pipeline.health import fingerprint as fpmod
from ev_pipeline.health.state import (
    KEEP_PREVIOUS,
    add_review_item,
    load_state,
    release_sources_doc,
    runs_dir,
    save_state,
)
from ev_pipeline.refresh import plan as _plan
from ev_pipeline.refresh.plan import (
    PlannedSource,
    plan,
    raw_dir_name,
    registry_entries,
)
from ev_pipeline.snapshot.probe import ProbeResult, probe_git, probe_http
from ev_pipeline.snapshot.recording import recording
from ev_pipeline.snapshot.store import (
    SnapshotError,
    SnapshotStore,
    find_manifest,
    open_store,
    restore_snapshot,
    take_snapshot,
)
from ev_pipeline.sources import _common as c

MIN_ROW_RATIO = 0.5
"""A normalise that yields fewer than half the previous records is held back (fail closed)."""
MEMORY_BUDGET_MB = 1024
"""ev-jobs container limit (Decision 006). Reported, and flagged in the run log if exceeded."""

EXIT_OK = 0
EXIT_RELEASE_FAILED = 1
EXIT_SOURCE_PROBLEMS = 3


def peak_rss_mb() -> float:
    """Peak resident memory of this process so far (Linux reports KiB, macOS bytes)."""
    v = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(v / (1024 * 1024) if sys.platform == "darwin" else v / 1024, 1)


def children_peak_rss_mb() -> float:
    v = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    return round(v / (1024 * 1024) if sys.platform == "darwin" else v / 1024, 1)


def count_lines(path: Path) -> int:
    n = 0
    with path.open("rb") as fh:
        for line in fh:
            if line.strip():
                n += 1
    return n


@dataclass
class SourceRun:
    id: str
    action: str
    reason: str
    status: str = "pending"
    message: str = ""
    steps: list[dict[str, Any]] = field(default_factory=list)
    seconds: float = 0.0
    changed: bool = False

    def step(self, name: str, started: float, outcome: str, **extra: Any) -> dict[str, Any]:
        entry = {
            "step": name,
            "outcome": outcome,
            "seconds": round(time.monotonic() - started, 2),
            "peak_rss_mb": peak_rss_mb(),
            **extra,
        }
        self.steps.append(entry)
        return entry

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "action": self.action,
            "reason": self.reason,
            "status": self.status,
            "changed": self.changed,
            "message": self.message,
            "seconds": round(self.seconds, 2),
            "steps": self.steps,
        }


@dataclass
class RefreshOptions:
    sources: list[str] | None = None
    dry_run: bool = False
    force: bool = False
    release: bool = True
    accept: set[str] = field(default_factory=set)


@dataclass
class Deps:
    """Seams for tests: the network-facing pieces are swappable."""

    store: SnapshotStore | None = None
    client_factory: Callable[[str], Any] = field(default=lambda sid: net.safe_client(sid))
    git_runner: Callable[[list[str]], str] | None = None
    now: Callable[[], datetime] = field(default=lambda: datetime.now(UTC).replace(microsecond=0))
    find: Callable[[str], Any] = field(default=lambda sid: _plan.find_adapter(sid))


# --- per source ---------------------------------------------------------------------------


def _probe(
    ps: PlannedSource, entry: dict[str, Any], deps: Deps, store: SnapshotStore
) -> ProbeResult:
    mod = ps.adapter
    hook = getattr(mod, "probe_unchanged", None)
    if callable(hook):
        # Optional adapter hook: probe_unchanged(client, previous_fetch_meta) -> bool | None
        # (e.g. RDW: compare the dataset's rowsUpdatedAt instead of 40 paged queries).
        manifest = find_manifest(store, ps.id, str(entry.get("content_hash")))
        if manifest is not None and manifest.meta:
            client = None
            try:
                client = deps.client_factory(ps.id)
                verdict = hook(client, manifest.meta)
            except Exception as exc:  # a probe may never break a refresh
                verdict = None
                detail = f"adapter probe failed: {type(exc).__name__}"
            else:
                detail = "adapter probe"
            finally:
                close = getattr(client, "close", None)
                if callable(close):
                    close()
            if verdict is True:
                return ProbeResult("unchanged", detail)
            if verdict is False:
                return ProbeResult("changed", detail)
    repo = getattr(mod, "REPO_URL", None)
    if repo and entry.get("commit"):
        return probe_git(str(repo), str(entry["commit"]), deps.git_runner)
    if entry.get("responses"):
        return probe_http(entry["responses"], lambda: deps.client_factory(ps.id))
    return ProbeResult("unknown", "no validators from the previous fetch")


def refresh_source(
    ps: PlannedSource,
    entry: dict[str, Any],
    data_dir: Path,
    store: SnapshotStore,
    opts: RefreshOptions,
    deps: Deps,
) -> tuple[SourceRun, dict[str, Any]]:
    run = SourceRun(ps.id, ps.action, ps.reason)
    entry = dict(entry)
    entry.update(
        {"id": ps.id, "name": ps.registry.get("name"), "licence": ps.registry.get("licence")}
    )
    entry["cadence"] = ps.cadence
    now = deps.now().isoformat()
    t0 = time.monotonic()
    try:
        _refresh_source(run, ps, entry, data_dir, store, opts, deps, now)
    except Exception as exc:  # one broken source must not stop the others
        run.status, run.message = "failed", f"{type(exc).__name__}: {exc}"[:500]
        run.steps.append(
            {"step": "error", "outcome": "failed", "trace": traceback.format_exc()[-2000:]}
        )
    run.seconds = time.monotonic() - t0
    if not opts.dry_run:
        entry["last_checked"] = now
        entry["status"] = run.status
        entry["message"] = run.message
        if run.status in ("ok", "unchanged"):
            entry["last_success"] = now
    return run, entry


def _refresh_source(
    run: SourceRun,
    ps: PlannedSource,
    entry: dict[str, Any],
    data_dir: Path,
    store: SnapshotStore,
    opts: RefreshOptions,
    deps: Deps,
    now: str,
) -> None:
    mod = ps.adapter
    assert mod is not None
    staging = data_dir / "staging" / f"{ps.id}.records.jsonl"
    raw = data_dir / "raw" / raw_dir_name(mod)
    accept = ps.id in opts.accept

    # 1. probe
    t = time.monotonic()
    if staging.exists() and entry.get("content_hash") and not accept:
        pr = _probe(ps, entry, deps, store)
        run.step("probe", t, pr.status, detail=pr.detail)
        if pr.status == "unchanged":
            run.status, run.message = "unchanged", pr.detail
            return
    else:
        run.step("probe", t, "skipped", detail="no accepted data yet" if not accept else "accept")
    if opts.dry_run:
        run.status, run.message = "would_fetch", "dry run: nothing fetched or written"
        return

    # 2. fetch
    t = time.monotonic()
    with recording(ps.id) as rec:
        rc = mod.fetch_cmd()
    responses = [r for r in rec.responses if r.get("method") != "HEAD"]
    run.step("fetch", t, "ok" if rc == 0 else "failed", responses=len(responses))
    if rc != 0:
        run.status, run.message = "failed", "fetch failed (see the adapter's message above)"
        return

    # 3. snapshot
    t = time.monotonic()
    manifest, new_content = take_snapshot(store, ps.id, raw, responses)
    meta = c.read_fetch_meta(raw)
    run.step(
        "snapshot",
        t,
        "new" if new_content else "known",
        content_hash=manifest.content_hash,
        files=len(manifest.files),
        bytes=manifest.bytes,
        snapshot=manifest.id,
    )
    entry["seen_hash"] = manifest.content_hash
    if manifest.content_hash == entry.get("content_hash") and staging.exists() and not accept:
        # Same data as accepted: keep validators fresh for the next probe.
        entry["responses"] = responses
        if meta.get("commit"):
            entry["commit"] = meta["commit"]
        run.status, run.message = "unchanged", "same content hash"
        return

    # 4. fingerprint
    t = time.monotonic()
    fp = fpmod.fingerprint_tree(raw)
    cmp = fpmod.compare(entry.get("fingerprint"), fp)
    run.step(
        "fingerprint",
        t,
        "breaking" if cmp["breaking"] else ("same" if cmp["same"] else "changed"),
        hash=fp["hash"],
        breaking=cmp["breaking"][:20],
        additive=cmp["additive"][:20],
    )
    if cmp["breaking"] and not accept:
        rid = add_review_item(
            data_dir,
            ps.id,
            "schema_drift",
            "; ".join(cmp["breaking"][:20]),
            str((entry.get("fingerprint") or {}).get("hash")),
            fp["hash"],
        )
        entry["seen_fingerprint"] = fp
        entry["review_id"] = rid
        _restore_raw(store, ps.id, entry, raw, run)
        run.status = "drift"
        run.message = (
            f"schema changed ({len(cmp['breaking'])} breaking); previous data kept; "
            f"review {rid}; accept with `ev sources accept {ps.id}`"
        )
        return

    # 5. normalise (staging backed up, put back on failure or a big drop)
    t = time.monotonic()
    backup = staging.with_name(staging.name + ".bak")
    if staging.exists():
        shutil.copy2(staging, backup)
    try:
        rc = mod.normalise_cmd(from_fixtures=False)
        rows = count_lines(staging) if staging.exists() else 0
        prev = int(entry.get("records") or 0)
        problem = None
        if rc != 0:
            problem = ("failed", "normalise failed")
        elif rows == 0:
            problem = ("failed", "normalise wrote no records")
        elif prev and rows < prev * MIN_ROW_RATIO and not accept:
            problem = ("rows_dropped", f"records fell from {prev} to {rows}")
        run.step(
            "normalise",
            t,
            problem[0] if problem else "ok",
            records=rows,
            records_previous=prev or None,
        )
        if problem:
            if backup.exists():
                shutil.copy2(backup, staging)
            elif staging.exists():
                staging.unlink()
            if problem[0] == "rows_dropped":
                entry["review_id"] = add_review_item(
                    data_dir, ps.id, "rows_dropped", problem[1], str(prev), str(rows)
                )
                problem = (problem[0], problem[1] + f"; review {entry['review_id']}")
            _restore_raw(store, ps.id, entry, raw, run)
            run.status, run.message = problem
            return
    finally:
        backup.unlink(missing_ok=True)

    # 6. accept
    entry.update(
        {
            "content_hash": manifest.content_hash,
            "snapshot_id": manifest.id,
            "fingerprint": fp,
            "records_previous": entry.get("records"),
            "records": rows,
            "last_change": now,
            "data_as_of": meta.get("fetched_at"),
            "responses": responses,
        }
    )
    entry.pop("seen_fingerprint", None)
    entry.pop("review_id", None)
    if meta.get("commit"):
        entry["commit"] = meta["commit"]
    run.status, run.changed = "ok", True
    run.message = f"{rows} records" + (" (accepted)" if accept else "")


def _restore_raw(
    store: SnapshotStore, sid: str, entry: dict[str, Any], raw: Path, run: SourceRun
) -> None:
    """Put the accepted raw folder back so raw and staging stay in step."""
    if not entry.get("content_hash"):
        return
    try:
        manifest = find_manifest(store, sid, str(entry["content_hash"]))
        if manifest is not None:
            restore_snapshot(store, manifest, raw)
            run.steps.append({"step": "restore_raw", "outcome": "ok", "snapshot": manifest.id})
    except SnapshotError as exc:
        run.steps.append({"step": "restore_raw", "outcome": "failed", "detail": str(exc)})


# --- the whole run --------------------------------------------------------------------------


def refresh(opts: RefreshOptions, deps: Deps | None = None) -> tuple[int, dict[str, Any]]:
    deps = deps or Deps()
    data_dir = c.data_dir()
    started = deps.now()
    t0 = time.monotonic()
    state = load_state(data_dir)
    planned = plan(data_dir, state, started, only=opts.sources, force=opts.force, find=deps.find)
    store = deps.store or open_store()
    runs: list[SourceRun] = []
    for ps in planned:
        if ps.action != "run":
            runs.append(SourceRun(ps.id, ps.action, ps.reason, status=ps.action))
            if ps.action == "skip" and not opts.dry_run and ps.id in state:
                state[ps.id] = {**state[ps.id], "status": "skipped", "message": ps.reason}
            continue
        print(f"refresh {ps.id}: {ps.reason}", flush=True)
        run, entry = refresh_source(ps, state.get(ps.id) or {}, data_dir, store, opts, deps)
        runs.append(run)
        print(f"refresh {ps.id}: {run.status} ({run.seconds:.1f}s) {run.message}", flush=True)
        if not opts.dry_run:
            state[ps.id] = entry
            save_state(data_dir, state)

    release = {"outcome": "not attempted"}
    code = EXIT_OK
    if not opts.dry_run and opts.release:
        release = _release(data_dir, state, planned, runs, started, t0)
        if release["outcome"] == "failed":
            code = EXIT_RELEASE_FAILED
    if code == EXIT_OK and any(r.status in KEEP_PREVIOUS for r in runs):
        code = EXIT_SOURCE_PROBLEMS

    log = run_document(opts, started, t0, runs, release, store)
    if not opts.dry_run:
        path = write_run_log(data_dir, log, started)
        log["run_log"] = c.rel(path)
    return code, log


def run_document(
    opts: RefreshOptions,
    started: datetime,
    t0: float,
    runs: list[SourceRun],
    release: dict[str, Any],
    store: SnapshotStore | None,
) -> dict[str, Any]:
    peak = peak_rss_mb()
    return {
        "step": "refresh",
        "started_at": started.isoformat(),
        "seconds": round(time.monotonic() - t0, 1),
        "options": {
            "sources": opts.sources,
            "dry_run": opts.dry_run,
            "force": opts.force,
            "release": opts.release,
            "accept": sorted(opts.accept),
        },
        "snapshot_store": store.describe() if store is not None else None,
        "peak_rss_mb": peak,
        "children_peak_rss_mb": children_peak_rss_mb(),
        "memory_budget_mb": MEMORY_BUDGET_MB,
        "within_memory_budget": peak < MEMORY_BUDGET_MB,
        "sources": [r.to_json() for r in runs],
        "release": release,
    }


def write_run_log(data_dir: Path, log: dict[str, Any], started: datetime) -> Path:
    d = runs_dir(data_dir)
    d.mkdir(parents=True, exist_ok=True)
    stamp = started.strftime("%Y%m%dT%H%M%SZ")
    path = d / f"{stamp}.json"
    i = 1
    while path.exists():
        path = d / f"{stamp}-{i}.json"
        i += 1
    path.write_text(json.dumps(log, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def _published_sources(data_dir: Path) -> set[str] | None:
    """Source ids cited by the latest release (None: no release yet, so every planned source
    must have staging data). A new source that never shipped does not block a release."""
    from ev_pipeline.health.state import latest_release

    n = latest_release(data_dir)
    path = data_dir / "releases" / str(n) / "catalogue.json" if n else None
    if path is None or not path.exists():
        return None
    doc = json.loads(path.read_text(encoding="utf-8"))
    return {str(src.get("id")) for src in doc.get("sources") or []}


def _release(
    data_dir: Path,
    state: dict[str, dict[str, Any]],
    planned: list[PlannedSource],
    runs: list[SourceRun],
    started: datetime,
    t0: float,
) -> dict[str, Any]:
    from ev_pipeline.release.build import build_release, write_release
    from ev_pipeline.release.validate import ReleaseError

    if not any(r.changed for r in runs):
        return {"outcome": "skipped", "reason": "no source brought new data"}
    published = _published_sources(data_dir)
    missing = [
        ps.id
        for ps in planned
        if ps.adapter is not None
        and (published is None or ps.id in published)
        and not (data_dir / "staging" / f"{ps.id}.records.jsonl").exists()
    ]
    if missing:
        return {
            "outcome": "skipped",
            "reason": "no staging data for " + ", ".join(missing) + " (a release that loses a"
            " whole source is never published)",
        }
    t = time.monotonic()
    try:
        res = build_release(data_dir)
    except ReleaseError as exc:
        return {"outcome": "failed", "reason": str(exc)[:2000]}
    counts = res.diff["counts"]
    if res.diff["previous_release"] is not None and not (
        counts["added"] or counts["removed"] or counts["changed"]
    ):
        return {"outcome": "skipped", "reason": "catalogue identical to the previous release"}
    summary = {
        "schema": "refresh-summary/v1",
        "release": res.release,
        "started_at": started.isoformat(),
        "sources": {
            r.id: {"status": r.status, "seconds": round(r.seconds, 1), "message": r.message}
            for r in runs
        },
        "peak_rss_mb": peak_rss_mb(),
        "seconds_before_release": round(t - t0, 1),
    }
    extras = {
        "sources.json": release_sources_doc(data_dir, res.catalogue, registry_entries(data_dir)),
        "refresh.json": summary,
    }
    try:
        out = write_release(res, data_dir, extras=extras)
    except ReleaseError as exc:
        return {"outcome": "failed", "release": res.release, "reason": str(exc)[:2000]}
    return {
        "outcome": "published",
        "release": res.release,
        "path": c.rel(out),
        "diff": counts,
        "seconds": round(time.monotonic() - t, 1),
        "peak_rss_mb": peak_rss_mb(),
    }
