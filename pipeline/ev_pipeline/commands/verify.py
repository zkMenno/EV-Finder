"""`ev verify` (T-127): rebuild from recorded staging, tests, release diff, back-tests, rule
dry run, tricky-car spot checks, PR body claims -> verify-report.md. See verify/run.py."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_OUT = Path(__file__).resolve().parents[2] / "verify-report.md"


def cmd_verify(args: argparse.Namespace) -> int:
    from ev_pipeline.release.build import default_data_dir
    from ev_pipeline.verify.run import report_md, verify

    body = Path(args.pr_body).read_text(encoding="utf-8") if args.pr_body else None
    rep = verify(
        Path(args.data_dir) if args.data_dir else default_data_dir(),
        base=args.base,
        skip_tests=args.skip_tests,
        pr_body=body,
    )
    out = Path(args.out) if args.out else DEFAULT_OUT
    out.write_text(report_md(rep), encoding="utf-8")
    if args.json:
        print(json.dumps({"status": rep.status, "failures": rep.failures, "numbers": rep.numbers}))
    else:
        print(f"verify: {rep.status} -> {out}")
        for f in rep.failures:
            print(f"  - {f}")
    return 0 if rep.status == "pass" else 1


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("verify", help="prove a data change: rebuild, diff, back-tests (T-127)")
    p.add_argument("--data-dir", help="default: EV_DATA_DIR or data/")
    p.add_argument("--base", default="origin/main", help="git ref for changed rule files")
    p.add_argument("--skip-tests", action="store_true", help="don't run pytest")
    p.add_argument("--pr-body", help="file with the PR body; its `key: number` lines are checked")
    p.add_argument("--out", help=f"report path (default {DEFAULT_OUT.name} in pipeline/)")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_verify)
