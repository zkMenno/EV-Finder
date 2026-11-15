"""`python -m ev_pipeline.backtest FILE.jsonl...`: print a back-test report (local use)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from ev_pipeline.backtest.harness import load_tests, run_backtest


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print("usage: python -m ev_pipeline.backtest FILE.jsonl...", file=sys.stderr)
        return 2
    print(json.dumps(run_backtest(load_tests(Path(a) for a in args)), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
