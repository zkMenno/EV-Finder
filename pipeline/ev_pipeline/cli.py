"""Command-line entry point: `ev <subcommand>`.

Other builders add subcommands by registering a parser in `build_parser`.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from ev_pipeline import __version__


def _cmd_version(_args: argparse.Namespace) -> int:
    print(__version__)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ev", description="EV Finder data pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    p_version = sub.add_parser("version", help="print the pipeline version")
    p_version.set_defaults(func=_cmd_version)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
