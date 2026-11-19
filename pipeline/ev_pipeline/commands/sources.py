"""`ev sources check` (one health table) and `ev sources accept <id>` (addendum 6 P3).

`check` reads only local files (data/runs/sources-state.json, else the latest release's
sources.json) and data/sources.yaml: no network.
`accept <id>` re-runs the refresh of one source with its schema-drift / record-drop guard
lifted, after a human looked at the review item.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from typing import Any

from ev_pipeline.health.state import load_state
from ev_pipeline.refresh.plan import plan
from ev_pipeline.refresh.runner import RefreshOptions, refresh
from ev_pipeline.sources import _common as c


def _day(v: Any) -> str:
    return str(v)[:10] if v else "-"


def health_rows(now: datetime | None = None) -> list[dict[str, Any]]:
    data_dir = c.data_dir()
    state = load_state(data_dir)
    now = now or datetime.now(UTC)
    rows = []
    seen = set()
    for ps in plan(data_dir, state, now):
        e = state.get(ps.id) or {}
        seen.add(ps.id)
        rows.append(_row(ps.id, e, ps.cadence, ps.action, ps.reason))
    for sid, e in sorted(state.items()):
        if sid not in seen:
            rows.append(_row(sid, e, e.get("cadence"), "-", "not refreshable now"))
    return rows


def _row(sid: str, e: dict[str, Any], cadence: Any, action: str, reason: str) -> dict[str, Any]:
    fp = e.get("fingerprint") or {}
    return {
        "source": sid,
        "status": e.get("status") or "never",
        "cadence": cadence,
        "due": {"run": "yes", "not_due": "no", "skip": "skip"}.get(action, action),
        "due_reason": reason,
        "last_success": e.get("last_success"),
        "last_change": e.get("last_change"),
        "data_as_of": e.get("data_as_of"),
        "records": e.get("records"),
        "records_previous": e.get("records_previous"),
        "fingerprint": fp.get("hash"),
        "fingerprint_drift": bool(e.get("seen_fingerprint")),
        "review_id": e.get("review_id"),
        "message": e.get("message"),
    }


def table(rows: list[dict[str, Any]]) -> str:
    head = (
        f"{'source':<16} {'status':<12} {'cadence':<10} {'due':<5} {'success':<10} "
        f"{'changed':<10} {'as of':<10} {'records (prev)':<18} fingerprint"
    )
    lines = [head, "-" * len(head)]
    for r in rows:
        rec = "-" if r["records"] is None else str(r["records"])
        if r["records_previous"] not in (None, r["records"]):
            rec += f" ({r['records_previous']})"
        fp = (r["fingerprint"] or "-").removeprefix("fp:")[:10]
        if r["fingerprint_drift"]:
            fp += " DRIFT " + (r["review_id"] or "")
        lines.append(
            f"{r['source']:<16} {r['status']:<12} {str(r['cadence'] or '-'):<10} "
            f"{r['due']:<5} {_day(r['last_success']):<10} {_day(r['last_change']):<10} "
            f"{_day(r['data_as_of']):<10} {rec:<18} {fp}"
        )
    problems = [r for r in rows if r["status"] in ("failed", "drift", "rows_dropped")]
    for r in problems:
        lines.append(f"! {r['source']}: {r['message']}")
    return "\n".join(lines)


def cmd_check(args: argparse.Namespace) -> int:
    rows = health_rows()
    if args.json:
        print(json.dumps(rows, indent=1, ensure_ascii=False))
    else:
        print(table(rows))
    return 1 if any(r["status"] in ("failed", "drift", "rows_dropped") for r in rows) else 0


def cmd_accept(args: argparse.Namespace) -> int:
    code, log = refresh(
        RefreshOptions(sources=[args.source], accept={args.source}, release=not args.no_release)
    )
    if "refused" in log:  # G-49: another live refresh holds data/staging (already printed)
        return code
    for s in log["sources"]:
        print(f"{s['id']}: {s['status']} {s['message']}")
    print(f"release: {log['release'].get('outcome')} {log['release'].get('release') or ''}")
    return code


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("sources", help="source health: check, accept a reviewed change")
    actions = p.add_subparsers(dest="sources_action", required=True)
    chk = actions.add_parser("check", help="one table: status, dates, records, fingerprint")
    chk.add_argument("--json", action="store_true")
    chk.set_defaults(func=cmd_check)
    acc = actions.add_parser(
        "accept", help="re-fetch one source and accept its new schema / record count (network)"
    )
    acc.add_argument("source")
    acc.add_argument("--no-release", action="store_true")
    acc.set_defaults(func=cmd_accept)
