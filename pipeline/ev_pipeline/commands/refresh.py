"""`ev refresh [--sources a,b] [--dry-run] [--force] [--no-release]` (addendum 6 P1)."""

from __future__ import annotations

import argparse
import json

from ev_pipeline.refresh.runner import RefreshOptions, refresh


def split_sources(values: list[str] | None) -> list[str] | None:
    if not values:
        return None
    out: list[str] = []
    for v in values:
        out += [s.strip() for s in v.split(",") if s.strip()]
    return out or None


def print_summary(log: dict) -> None:
    print()
    print(f"{'source':<18} {'status':<13} {'seconds':>8}  note")
    for s in log["sources"]:
        note = s["message"] or s["reason"]
        print(f"{s['id']:<18} {s['status']:<13} {s['seconds']:>8.1f}  {note[:90]}")
    rel = log["release"]
    print(f"\nrelease: {rel.get('outcome')}", end="")
    if rel.get("release"):
        print(f" {rel['release']}", end="")
    if rel.get("reason"):
        print(f" ({rel['reason'][:300]})", end="")
    print(
        f"\npeak memory: {log['peak_rss_mb']} MB (children {log['children_peak_rss_mb']} MB,"
        f" budget {log['memory_budget_mb']} MB); total {log['seconds']} s"
    )
    if log.get("run_log"):
        print(f"run log: {log['run_log']}")


def cmd_refresh(args: argparse.Namespace) -> int:
    opts = RefreshOptions(
        sources=split_sources(args.sources),
        dry_run=args.dry_run,
        force=args.force,
        release=not args.no_release,
        accept=set(split_sources(args.accept) or []),
    )
    code, log = refresh(opts)
    if "refused" in log:  # G-49: another live refresh holds data/staging (already printed)
        return code
    if args.json:
        print(json.dumps(log, indent=1, ensure_ascii=False))
    else:
        print_summary(log)
    return code


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser(
        "refresh",
        help="fetch due sources, skip unchanged ones, build the next release (network)",
        description="For each active source whose cadence is due: fetch, snapshot, check the "
        "schema fingerprint, normalise; then build and QA the next release if anything "
        "changed. Exit 0 ok, 1 release failed, 3 a source failed or drifted.",
    )
    p.add_argument(
        "--sources",
        action="append",
        metavar="ID[,ID]",
        help="only these sources, run now whatever their cadence (repeatable)",
    )
    p.add_argument(
        "--dry-run", action="store_true", help="plan and probe only; download and write nothing"
    )
    p.add_argument("--force", action="store_true", help="run every refreshable source now")
    p.add_argument("--no-release", action="store_true", help="update staging only")
    p.add_argument(
        "--accept",
        action="append",
        metavar="ID",
        help="accept a schema change or record drop for this source (after review)",
    )
    p.add_argument("--json", action="store_true", help="print the run log as JSON")
    p.set_defaults(func=cmd_refresh)
