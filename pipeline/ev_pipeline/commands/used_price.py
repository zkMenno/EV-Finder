"""`ev used-price fit`: fit the depreciation curve on our own samples (T-113, Decision 064).

Dry run on a published release (its catalogue.json + facts.parquet) and the gated samples in
data/manual/prices/. Prints the `fitted:` block for derive/used_price_params.yaml (a gate
file: paste it in its own PR) plus the hold-out back-test. Writes nothing unless --out.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import yaml


def _default_data_dir() -> Path:
    from ev_pipeline.release.build import default_data_dir

    return default_data_dir()


def release_inputs(
    data_dir: Path, release: int | None
) -> tuple[int, list[dict[str, Any]], list[dict[str, Any]], list[int | None]]:
    """(release, rows, price facts, record years) from a release folder."""
    import pyarrow.parquet as pq

    releases = data_dir / "releases"
    n = release or int((releases / "latest").read_text(encoding="utf-8").strip())
    d = releases / str(n)
    rows = json.loads((d / "catalogue.json").read_text(encoding="utf-8"))["rows"]
    table = pq.read_table(d / "facts.parquet").to_pylist()
    facts, years = [], []
    for r in table:
        if r.get("field") != "price_new":
            continue
        facts.append(
            {
                "field": "price_new",
                "subject_type": r["subject_type"],
                "subject_id": r["subject_id"],
                "country": r["country"],
                "value": r["value_num"],
                "unit": r["unit"],
                "source": {"id": r["source_id"]},
            }
        )
        years.append(r.get("record_year"))
    return n, rows, facts, years


def run_fit(
    data_dir: Path, release: int | None, as_of: date, params_path: Path | None = None
) -> dict[str, Any]:
    from ev_pipeline.derive import used_price as up
    from ev_pipeline.derive.depreciation import fit_block, fit_points, holdout_backtest
    from ev_pipeline.release.gate import load_registry

    p = up.load_params(params_path or up.PARAMS_FILE)
    n, rows, facts, years = release_inputs(data_dir, release)
    samples, problems = up.load_samples(data_dir / p["samples_dir"])
    samples, dropped = up.gate_samples(samples, load_registry(data_dir / "sources.yaml"))
    prices = up.list_prices(facts, years)
    points = fit_points(samples, rows, prices, as_of, p)
    published = p["curves"]["default"]
    return {
        "release": n,
        "as_of": as_of.isoformat(),
        "sample_rows": len(samples),
        "sample_problems": problems,
        "dropped_by_source_gate": dropped,
        "fitted": fit_block(points, p, published, as_of.isoformat(), n),
        "holdout": holdout_backtest(points, p, published),
        "points": [pt.to_dict() for pt in points],
    }


def cmd_fit(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir) if args.data_dir else _default_data_dir()
    as_of = date.fromisoformat(args.as_of) if args.as_of else datetime.now(UTC).date()
    res = run_fit(data_dir, args.release, as_of)
    block = yaml.safe_dump({"fitted": res["fitted"]}, sort_keys=False, allow_unicode=True)
    print(block)
    ho = res["holdout"]
    for name in ("fitted", "published"):
        e = ho[name]
        print(
            f"# hold-out {name}: {e['rows_compared']} rows, median abs error"
            f" {e['median_abs_error']}, median error {e['median_error']}"
        )
    if args.out:
        Path(args.out).write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    return 0


def register(sub: Any) -> None:
    p = sub.add_parser("used-price", help="used price model tools (T-113)")
    s = p.add_subparsers(dest="used_price_command", required=True)
    f = s.add_parser("fit", help="fit the depreciation curve on our samples (dry run, prints)")
    f.add_argument("--release", type=int, default=None, help="release number (default latest)")
    f.add_argument("--as-of", default=None, help="age reference date (default today)")
    f.add_argument("--data-dir", default=None)
    f.add_argument("--out", default=None, help="also write the full result (points) as JSON")
    f.set_defaults(func=cmd_fit)
