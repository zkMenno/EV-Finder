"""`python -m ev_pipeline.qa check-release <release dir | latest pointer>` (T-057)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ev_pipeline.qa.check_release import ReleaseInputError, check_release, render


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m ev_pipeline.qa")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check-release", help="re-run the blocking QA on a committed release")
    c.add_argument("release", type=Path, help="data/releases/<n> or data/releases/latest")
    c.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="folder with sources.yaml (default: two levels above the release folder)",
    )
    c.add_argument("--json", action="store_true", help="print the report as JSON")
    args = p.parse_args(argv)
    data_dir = args.data_dir or args.release.resolve().parent.parent
    try:
        report = check_release(args.release, data_dir)
    except ReleaseInputError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=1, ensure_ascii=False) if args.json else render(report))
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
