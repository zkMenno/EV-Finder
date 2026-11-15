"""`ev` command line. Each step is small and idempotent and writes a run log line."""

from __future__ import annotations

import argparse
import importlib
import sys

from ev_pipeline import __version__

SOURCES = ["openev", "rdw", "eea", "nyland", "dft-veh", "kba-fz10", "ademe"]


def _adapter(name: str):
    return importlib.import_module(f"ev_pipeline.sources.{name.replace('-', '_')}.adapter")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ev", description="EV Finder data pipeline")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("version", help="print the pipeline version")

    p_fetch = sub.add_parser("fetch", help="download raw data for a source (network)")
    p_fetch.add_argument("source", choices=SOURCES)

    p_norm = sub.add_parser("normalise", help="raw data -> data/staging/<source>.records.jsonl")
    p_norm.add_argument("source", choices=SOURCES)
    p_norm.add_argument(
        "--from-fixtures", action="store_true", help="use the recorded sample in tests/fixtures"
    )

    p_rel = sub.add_parser("release", help="match, merge, derive, validate, publish a release")
    p_rel.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "version":
        print(__version__)
        return 0
    if args.command == "fetch":
        return _adapter(args.source).fetch_cmd()
    if args.command == "normalise":
        return _adapter(args.source).normalise_cmd(from_fixtures=args.from_fixtures)
    if args.command == "release":
        from ev_pipeline.release.build import release_cmd

        return release_cmd(dry_run=args.dry_run)
    return 1


if __name__ == "__main__":
    sys.exit(main())
