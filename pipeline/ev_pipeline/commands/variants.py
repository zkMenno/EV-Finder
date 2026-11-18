"""`ev variants`: candidate variants from type-approval versions (T-073, Decision 049).

- `ev variants fetch-eea`: EU registrations per type-approval version from EEA (network,
  counts only) -> data/raw/eea_versions/.
- `ev variants propose`: match the staged records like a release does, group every RDW TGK
  version of a seed generation by spec fingerprint, and write the review queue
  data/review/variant-candidates.csv + data/review/variant-coverage.json. Never a release.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def _data_dir(args: argparse.Namespace) -> Path:
    from ev_pipeline.release.build import default_data_dir

    return Path(args.data_dir) if args.data_dir else default_data_dir()


def fetch_eea_cmd(args: argparse.Namespace) -> int:
    import httpx

    from ev_pipeline import net
    from ev_pipeline.sources import _common as c
    from ev_pipeline.sources.eea import versions as ev

    target = c.raw_dir(ev.DIR)
    client = net.safe_client("eea", timeout=300)
    try:
        rows = ev.fetch(client, target)
    except (httpx.HTTPError, RuntimeError) as exc:
        print(f"variants fetch-eea: failed: {exc}")
        return 1
    finally:
        client.close()
    c.log_step(
        step="fetch",
        source="eea",
        input_=f"{ev.SQL_URL} {len(ev.VERSION_TABLES)} tables (grouped TAN|Va|Ve counts)",
        output=c.rel(target),
        rows_out=rows,
    )
    return 0


def published_variant_count(data_dir: Path) -> int | None:
    releases = data_dir / "releases"
    try:
        n = (releases / "latest").read_text(encoding="utf-8").strip()
        meta = json.loads((releases / n / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    counts = meta.get("counts") or {}
    v = counts.get("rows") if isinstance(counts, dict) else None
    return int(v) if isinstance(v, int) else None


def run_propose(data_dir: Path) -> dict[str, Any]:
    from ev_pipeline.derive.links import load_links
    from ev_pipeline.match.matcher import match_records
    from ev_pipeline.match.seed import load_manual_variants, load_seed, load_source_holds
    from ev_pipeline.release.build import generation_pack_kwh, load_staging
    from ev_pipeline.review_queue import DEFAULT_STATUS, ID_COLUMNS, _ids_for, load_status
    from ev_pipeline.sources import _common as c
    from ev_pipeline.sources.eea import versions as ev
    from ev_pipeline.variants import propose as vp

    seed = load_seed(data_dir / "seed" / "models.yaml")
    variants_path = data_dir / "seed" / "variants.yaml"
    manual, holds = [], []
    if variants_path.exists():
        manual, _ = load_manual_variants(variants_path)
        holds = load_source_holds(variants_path)
    records, inputs, _ = load_staging(data_dir / "staging")
    if not any(r.source.id.root == vp.SOURCE_ID for r in records):
        raise SystemExit(
            "variants propose: no rdw-tgk records in data/staging (ev fetch/normalise rdw-tgk)"
        )
    links = load_links(data_dir)
    result = match_records(records, seed, manual, generation_pack_kwh(links, manual), holds=holds)
    nl = vp.load_nl_cars(data_dir / "raw" / "rdw_tgk" / "versions.json")
    eea = ev.load(data_dir / "raw" / ev.DIR)
    proposal = vp.place_versions(records, seed, result, nl, eea)
    cov = vp.coverage(proposal, seed, published_variant_count(data_dir))
    if eea is not None and eea.by_name:
        cov["model_level"] = vp.model_coverage(seed, eea, scoped=result.scoped_aliases)
    cov["inputs"] = {
        "staging": sorted(
            str(Path(str(i.get("path"))).relative_to(data_dir.parent))
            if Path(str(i.get("path"))).is_relative_to(data_dir.parent)
            else Path(str(i.get("path"))).name
            for i in inputs
        ),
        "eea_versions": None
        if eea is None
        else {"years": eea.years, "fetched_at": eea.retrieved_at},
        "rdw_tgk_fetched_at": c.read_fetch_meta(data_dir / "raw" / "rdw_tgk").get("fetched_at"),
    }
    review = data_dir / "review"
    review.mkdir(parents=True, exist_ok=True)
    rows = proposal.rows()
    # Review ids and statuses as review_queue gives them (status.yaml decides), written for this
    # one file only: the other review CSVs belong to `ev release` and are left untouched. A
    # status typed into this CSV is harvested into status.yaml by the next `ev release`.
    items = load_status(review)
    ids = _ids_for(Path(vp.CSV_NAME).stem, rows)
    with (review / vp.CSV_NAME).open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=[*ID_COLUMNS, *vp.COLUMNS])
        w.writeheader()
        for rid, r in zip(ids, rows, strict=True):
            st = str((items.get(rid) or {}).get("status", DEFAULT_STATUS))
            w.writerow({"review_id": rid, "status": st, **r})
    (review / vp.COVERAGE_NAME).write_text(
        json.dumps(cov, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    c.log_step(
        step="variants-propose",
        source=vp.SOURCE_ID,
        input_="data/staging + data/raw/rdw_tgk/versions.json + data/raw/eea_versions",
        output=f"data/review/{vp.CSV_NAME}",
        rows_out=len(rows),
        candidate_groups=cov["candidate_groups"],
    )
    return cov


def propose_cmd(args: argparse.Namespace) -> int:
    cov = run_propose(_data_dir(args))
    short = {k: v for k, v in cov.items() if k not in ("top_models_not_in_seed", "inputs")}
    if "model_level" in short:
        ml = dict(short["model_level"])
        ml["biggest_unmatched"] = ml["biggest_unmatched"][:10]
        ml.pop("seed_models_without_eu_registrations", None)
        short["model_level"] = ml
    print(json.dumps(short, indent=2))
    return 0


def register(sub: Any) -> None:
    p = sub.add_parser("variants", help="candidate variants from type approvals (T-073)")
    vs = p.add_subparsers(dest="variants_cmd", required=True)
    f = vs.add_parser("fetch-eea", help="EEA registrations per type-approval version (network)")
    f.set_defaults(func=fetch_eea_cmd)
    pr = vs.add_parser("propose", help="write data/review/variant-candidates.csv + coverage")
    pr.add_argument("--data-dir", default=None)
    pr.set_defaults(func=propose_cmd)
