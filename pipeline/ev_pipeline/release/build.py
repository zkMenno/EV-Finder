"""`ev release`: match -> range-check -> merge -> derive -> validate -> publish (T-006).

Inputs:  data/staging/*.records.jsonl (SourceRecord per line), data/seed/models.yaml,
         data/seed/variants.yaml (optional, source `seed-manual`).
         data/sources.yaml (licence gate), data/field_sources.yaml (merge policy per field).
Outputs: data/review/{unmatched,validation,conflicts}.csv,
         data/releases/<n>/{catalogue.json, catalogue.parquet, facts.parquet, diff.json,
         coverage.md, README.md, run_log.json} and data/releases/latest (holds n).

n = highest existing release number + 1 (Decision 008). The folder is written under a
temporary name and renamed at the end, so a failed run never leaves a half release.
`--dry-run` computes everything and prints the summary but writes nothing.
Licence gate (Decision 009): records from a source that data/sources.yaml does not list as
`active` with a named licence are dropped on load and guarded again before writing; `nyland`
(permission pending) is always excluded.
"""

from __future__ import annotations

import csv
import gzip
import json
import os
import shutil
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from ev_pipeline.derive.links import (
    catalogue_parts,
    finish_voltage,
    id_errors,
    inherited_for,
    load_links,
    pack_facts,
)
from ev_pipeline.derive.rows import ESTIMATE_SOURCE, build_rows
from ev_pipeline.match.matcher import (
    EXCLUDED_SOURCES,
    MatchedFact,
    MatchResult,
    Problem,
    UnmatchedRow,
    aggregate_counts,
    match_records,
)
from ev_pipeline.match.review import unmatched_rows, write_unmatched
from ev_pipeline.match.seed import ManualVariant, Seed, load_manual_variants, load_seed
from ev_pipeline.merge.merge import Merged, merge_variant_facts
from ev_pipeline.merge.policy import load_policies
from ev_pipeline.records import SourceRecord
from ev_pipeline.release.gate import load_registry
from ev_pipeline.release.validate import (
    ROW_NUMBER_FIELDS,
    ReleaseError,
    check_fact_ranges,
    excluded_source_errors,
    licence_errors,
    provenance_errors,
    schema_errors,
    write_validation,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
DIFF_IGNORE = {"release", "provenance"}


def default_data_dir() -> Path:
    return Path(os.environ.get("EV_DATA_DIR", REPO_ROOT / "data"))


@dataclass
class ReleaseResult:
    release: int
    catalogue: dict[str, Any]
    facts: list[dict[str, Any]]
    fact_years: list[int | None]
    diff: dict[str, Any]
    match: MatchResult
    problems: list[Problem]
    unmatched_count: int
    inputs: list[dict[str, Any]] = field(default_factory=list)
    unmatched_rows: list[UnmatchedRow] = field(default_factory=list)
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    gated: dict[str, dict[str, Any]] = field(default_factory=dict)
    out_dir: Path | None = None
    catalogue_bytes: int = 0
    catalogue_gzip_bytes: int = 0


# --- loading -----------------------------------------------------------------------------


def load_staging(staging: Path) -> tuple[list[SourceRecord], list[dict[str, Any]], list[Problem]]:
    records: list[SourceRecord] = []
    inputs: list[dict[str, Any]] = []
    problems: list[Problem] = []
    if not staging.is_dir():
        return records, inputs, problems
    for path in sorted(staging.glob("*.records.jsonl")):
        name = path.name.removesuffix(".records.jsonl")
        if name in EXCLUDED_SOURCES:
            inputs.append({"path": str(path), "skipped": "excluded source (permission pending)"})
            continue
        n = 0
        with path.open(encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                try:
                    rec = SourceRecord.model_validate_json(line)
                except Exception as exc:
                    problems.append(
                        Problem(
                            "parse", name, f"{path.name}:{lineno}", "", "", "", "", str(exc)[:200]
                        )
                    )
                    continue
                records.append(rec)
                n += 1
        inputs.append({"path": str(path), "records": n, "modified": _mtime(path)})
    return records, inputs, problems


def _mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=UTC).isoformat(timespec="seconds")


def existing_releases(releases: Path) -> list[int]:
    if not releases.is_dir():
        return []
    return sorted(int(p.name) for p in releases.iterdir() if p.is_dir() and p.name.isdigit())


def next_release_number(releases: Path) -> int:
    nums = existing_releases(releases)
    return (nums[-1] + 1) if nums else 1


# --- building ----------------------------------------------------------------------------


def _fact_dict(mf: MatchedFact) -> dict[str, Any]:
    return mf.fact.model_dump(mode="json", exclude_none=True)


def _generation_dicts(seed: Seed) -> list[dict[str, Any]]:
    out = []
    for gid in sorted(seed.generations):
        g = seed.generations[gid]
        d: dict[str, Any] = {
            "id": g.id,
            "model_id": g.model_id,
            "name": g.name,
            "slug": g.id,
            "year_start": g.year_start,
            "year_end": g.year_end,
            "uncertain": g.uncertain,
        }
        if g.change_markers:
            d["change_markers"] = [
                {"year": int(c["year"]), "text": str(c["text"])} for c in g.change_markers
            ]
        out.append(d)
    return out


def compute_diff(prev: dict[str, Any] | None, cur: dict[str, Any]) -> dict[str, Any]:
    cur_rows = {r["variant_id"]: r for r in cur["rows"]}
    prev_rows = {r["variant_id"]: r for r in (prev or {}).get("rows", [])}
    added = sorted(set(cur_rows) - set(prev_rows))
    removed = sorted(set(prev_rows) - set(cur_rows))
    changed: dict[str, dict[str, dict[str, Any]]] = {}
    for vid in sorted(set(cur_rows) & set(prev_rows)):
        a, b = prev_rows[vid], cur_rows[vid]
        fields = {}
        for k in sorted((set(a) | set(b)) - DIFF_IGNORE):
            if a.get(k) != b.get(k):
                fields[k] = {"old": a.get(k), "new": b.get(k)}
        if fields:
            changed[vid] = fields
    return {
        "release": cur["release"],
        "previous_release": prev["release"] if prev else None,
        "added": added,
        "removed": removed,
        "changed": changed,
        "counts": {
            "rows_previous": len(prev_rows),
            "rows": len(cur_rows),
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed),
        },
    }


def build_release(
    data_dir: Path,
    now: datetime | None = None,
    release: int | None = None,
) -> ReleaseResult:
    now = now or datetime.now(UTC)
    today = now.date()
    seed_path = data_dir / "seed" / "models.yaml"
    if not seed_path.exists():
        raise ReleaseError(f"seed not found: {seed_path}")
    seed = load_seed(seed_path)
    manual: list[ManualVariant] = []
    problems: list[Problem] = []
    records, inputs, parse_problems = load_staging(data_dir / "staging")
    problems += parse_problems
    variants_path = data_dir / "seed" / "variants.yaml"
    if variants_path.exists():
        manual, manual_problems = load_manual_variants(variants_path)
        problems += [Problem("seed", "seed-manual", "", "", "", "", "", p) for p in manual_problems]
        inputs.append(
            {"path": str(variants_path), "records": len(manual), "modified": _mtime(variants_path)}
        )
    inputs.insert(0, {"path": str(seed_path), "modified": _mtime(seed_path)})

    registry = load_registry(data_dir / "sources.yaml")
    policies = load_policies(data_dir / "field_sources.yaml")
    gated: dict[str, dict[str, Any]] = {}

    def gate(sid: str) -> bool:
        why = registry.reason_blocked(sid)
        if why is not None:
            g = gated.setdefault(sid, {"reason": why, "records": 0})
            g["records"] += 1
            return False
        return True

    records = [r for r in records if gate(r.source.id.root)]
    manual = [mv for mv in manual if gate(mv.record.source.id.root)]

    result = match_records(records, seed, manual)
    problems += result.problems
    spec_facts, dropped = check_fact_ranges(result.spec_facts)
    problems += dropped

    by_variant: dict[str, list[MatchedFact]] = {}
    for mf in spec_facts:
        by_variant.setdefault(mf.fact.subject_id.root, []).append(mf)
    merged = {vid: merge_variant_facts(fs, policies) for vid, fs in by_variant.items()}
    conflicts = conflict_rows(merged)
    nl_counts = aggregate_counts(result.count_facts, seed, "rdw", "NL")

    n = release or next_release_number(data_dir / "releases")
    links = load_links(data_dir)
    inputs += [{"path": p} for p in links.inputs]
    inherited = {
        vid: inherited_for(
            links,
            vid,
            info.generation_id,
            {f: mg.value for f, mg in merged.get(vid, {}).items()},
        )
        for vid, info in result.variants.items()
    }
    rows, row_problems = build_rows(
        result.variants, merged, seed, nl_counts, today, n, policies=policies, inherited=inherited
    )
    for row in rows:
        finish_voltage(links, row, row.get("platform_id"))
        if links.taxonomy is None:
            # Ids cannot be checked without the taxonomy files: do not publish them.
            for f in ("chemistry_id", "cooling_id"):
                row.pop(f, None)
                row["provenance"].pop(f, None)
    problems += row_problems

    all_facts = spec_facts + result.count_facts
    sources: dict[str, dict[str, Any]] = {}
    for mf in all_facts:
        sources.setdefault(mf.source_id, mf.fact.source.model_dump(mode="json", exclude_none=True))
    if any(ESTIMATE_SOURCE in p["source_ids"] for r in rows for p in r["provenance"].values()):
        est = registry.source_object(ESTIMATE_SOURCE) or {
            "id": ESTIMATE_SOURCE,
            "name": "EV Finder estimate models",
            "licence": "CC-BY-4.0",
        }
        sources.setdefault(ESTIMATE_SOURCE, est)
    catalogue = {
        "release": n,
        "generated_at": now.isoformat(timespec="seconds"),
        "sources": [sources[k] for k in sorted(sources)],
        "generations": _generation_dicts(seed),
        "rows": rows,
        **catalogue_parts(links),
    }
    if links.packs and links.retrieved_at:
        sources.setdefault(links.source["id"], links.source)
        catalogue["sources"] = [sources[k] for k in sorted(sources)]
    facts = [_fact_dict(mf) for mf in all_facts]
    pfacts = pack_facts(links)
    facts += pfacts

    errors = (
        schema_errors(catalogue, facts)
        + provenance_errors(rows)
        + excluded_source_errors(catalogue, facts, registry.releasable)
        + licence_errors(catalogue["sources"])
        + id_errors(links, catalogue)
    )
    if errors:
        raise ReleaseError("release failed validation:\n  " + "\n  ".join(errors[:50]))

    prev = None
    prev_nums = [x for x in existing_releases(data_dir / "releases") if x < n]
    if prev_nums:
        prev_path = data_dir / "releases" / str(prev_nums[-1]) / "catalogue.json"
        if prev_path.exists():
            prev = json.loads(prev_path.read_text(encoding="utf-8"))
    diff = compute_diff(prev, catalogue)
    unmatched = unmatched_rows(result)
    res = ReleaseResult(
        release=n,
        catalogue=catalogue,
        facts=facts,
        fact_years=[mf.year for mf in all_facts] + [None] * len(pfacts),
        diff=diff,
        match=result,
        problems=problems,
        unmatched_count=len(result.unmatched) + sum(result.other_makes.values()),
        inputs=inputs,
        unmatched_rows=unmatched,
        conflicts=conflicts,
        gated=gated,
    )
    raw = catalogue_bytes(catalogue)
    res.catalogue_bytes = len(raw)
    res.catalogue_gzip_bytes = len(gzip.compress(raw, mtime=0))
    return res


CONFLICT_COLUMNS = [
    "variant_id",
    "field",
    "source_id",
    "value",
    "unit",
    "winning_value",
    "tolerance",
    "fact_id",
]


def conflict_rows(merged: dict[str, dict[str, Merged]]) -> list[dict[str, Any]]:
    """Facts outside the field tolerance of the winning value. Never averaged in."""
    out = []
    for vid in sorted(merged):
        for fname, mg in merged[vid].items():
            for c in mg.conflicts:
                out.append(
                    {
                        "variant_id": vid,
                        "field": fname,
                        "source_id": c.source_id,
                        "value": c.fact.value,
                        "unit": c.fact.unit,
                        "winning_value": mg.value,
                        "tolerance": mg.tolerance,
                        "fact_id": c.fact.id,
                    }
                )
    return out


def write_conflicts(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CONFLICT_COLUMNS)
        w.writeheader()
        w.writerows(rows)


COVERAGE_BUCKETS = ("2+ agreeing sources", "1 source", "estimate only", "missing")


def coverage(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    """Per row field: how many variants have 2+ agreeing sources, 1, an estimate, nothing."""
    out: dict[str, dict[str, int]] = {}
    for f in ROW_NUMBER_FIELDS:
        c = dict.fromkeys(COVERAGE_BUCKETS, 0)
        for r in rows:
            p = (r.get("provenance") or {}).get(f)
            if r.get(f) is None or p is None:
                c["missing"] += 1
            elif p.get("estimate"):
                c["estimate only"] += 1
            elif p.get("agreeing_sources", 1) >= 2:
                c["2+ agreeing sources"] += 1
            else:
                c["1 source"] += 1
        out[f] = c
    return out


def coverage_md(res: ReleaseResult) -> str:
    rows = res.catalogue["rows"]
    n = len(rows) or 1
    lines = [
        f"# Coverage, release {res.release}",
        "",
        f"{len(rows)} variants. Share of variants per field (count in brackets). 'estimate only'"
        " = our model or ratio, no source; derived values count by their weakest input.",
        "",
        "| Field | " + " | ".join(COVERAGE_BUCKETS) + " |",
        "|---|" + "---|" * len(COVERAGE_BUCKETS),
    ]
    for f, c in coverage(rows).items():
        cells = [f"{100 * c[b] / n:.0f}% ({c[b]})" for b in COVERAGE_BUCKETS]
        lines.append(f"| {f} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


# --- writing -----------------------------------------------------------------------------


def catalogue_bytes(catalogue: dict[str, Any]) -> bytes:
    return json.dumps(catalogue, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _flat_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    countries = sorted({cc for r in rows for cc in (r.get("price_new") or {})})
    out = []
    for r in rows:
        flat = {
            k: v for k, v in r.items() if k not in ("price_new", "change_markers", "provenance")
        }
        for cc in countries:
            money = (r.get("price_new") or {}).get(cc)
            flat[f"price_new_{cc.lower()}"] = money["amount"] if money else None
            flat[f"price_new_{cc.lower()}_currency"] = money["currency"] if money else None
        flat["change_markers_json"] = json.dumps(r.get("change_markers") or [], ensure_ascii=False)
        flat["provenance_json"] = json.dumps(r["provenance"], separators=(",", ":"))
        out.append(flat)
    return out


def _flat_facts(facts: list[dict[str, Any]], years: list[int | None]) -> list[dict[str, Any]]:
    out = []
    for f, y in zip(facts, years, strict=True):
        v = f["value"]
        num = isinstance(v, int | float) and not isinstance(v, bool)
        out.append(
            {
                "id": f["id"],
                "subject_type": f["subject_type"],
                "subject_id": f["subject_id"],
                "field": f["field"],
                "value_num": float(v) if num else None,
                "value_text": None if num else str(v),
                "unit": f["unit"],
                "country": f.get("country"),
                "source_id": f["source"]["id"],
                "source_name": f["source"]["name"],
                "source_licence": f["source"]["licence"],
                "source_record": f.get("source_record"),
                "retrieved_at": f["retrieved_at"],
                "confidence": f["confidence"],
                "record_year": y,
            }
        )
    return out


def _write_parquet(path: Path, rows: list[dict[str, Any]]) -> None:
    pq.write_table(pa.Table.from_pylist(rows), path, compression="zstd")


def release_readme(res: ReleaseResult) -> str:
    cat = res.catalogue
    rows = cat["rows"]
    tiers = Counter(r["quality_tier"] for r in rows)
    rungs = Counter(r.get("real_range_rung") or "none" for r in rows)
    lines = [
        f"# EV Finder catalogue release {res.release}",
        "",
        f"Generated {cat['generated_at']} by `ev release`. Data licence: CC BY 4.0"
        " (see DATA_LICENSE.md); third-party inputs keep their own licences, listed below.",
        "",
        "## Counts",
        "",
        f"- Variants (rows): {len(rows)}",
        f"- Generations with rows: {len({r['generation_id'] for r in rows})}"
        f" of {len(cat['generations'])} in the seed",
        f"- Facts: {len(res.facts)}",
        "- Quality tiers: " + ", ".join(f"{k} {v}" for k, v in sorted(tiers.items())),
        "- Real-range rungs: " + ", ".join(f"{k} {v}" for k, v in sorted(rungs.items())),
        f"- Changes vs previous: +{res.diff['counts']['added']} / -{res.diff['counts']['removed']}"
        f" / ~{res.diff['counts']['changed']}",
        "",
        "## Sources and licences",
        "",
        "| Source | Licence | Attribution |",
        "|---|---|---|",
    ]
    for s in cat["sources"]:
        attribution = s.get("attribution") or s["name"]
        lines.append(f"| {s['id']} ({s['name']}) | {s['licence']} | {attribution} |")
    lines += [
        "",
        "## Attribution",
        "",
        *[
            f"- Contains data from {s['name']}"
            + (f" ({s['url']})" if s.get("url") else "")
            + f", licensed {s['licence']}."
            + (f" {s['attribution']}" if s.get("attribution") else "")
            for s in cat["sources"]
        ],
        "",
        "## Caveats",
        "",
        "- Real-range figures on the `body-ratio` rung are PROVISIONAL generic ratios"
        " (mild-weather mixed driving), not measurements.",
        "- `seed-manual` values are hand-entered and unchecked (confidence low).",
        "- `registered_count_nl` is per generation: every variant of a generation shows the"
        " same RDW total.",
        "",
    ]
    return "\n".join(lines)


def write_release(res: ReleaseResult, data_dir: Path) -> Path:
    releases = data_dir / "releases"
    releases.mkdir(parents=True, exist_ok=True)
    final = releases / str(res.release)
    if final.exists():
        raise ReleaseError(f"release folder already exists: {final}")
    tmp = releases / f".tmp-{res.release}"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir()
    (tmp / "catalogue.json").write_bytes(catalogue_bytes(res.catalogue))
    _write_parquet(tmp / "catalogue.parquet", _flat_rows(res.catalogue["rows"]))
    _write_parquet(tmp / "facts.parquet", _flat_facts(res.facts, res.fact_years))
    (tmp / "diff.json").write_text(
        json.dumps(res.diff, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (tmp / "README.md").write_text(release_readme(res), encoding="utf-8")
    (tmp / "coverage.md").write_text(coverage_md(res), encoding="utf-8")
    (tmp / "run_log.json").write_text(
        json.dumps(run_log(res, "published"), indent=1) + "\n", encoding="utf-8"
    )
    tmp.rename(final)
    (releases / "latest").write_text(f"{res.release}\n", encoding="utf-8")
    review = data_dir / "review"
    write_unmatched(review / "unmatched.csv", res.unmatched_rows)
    write_validation(review / "validation.csv", res.problems)
    write_conflicts(review / "conflicts.csv", res.conflicts)
    res.out_dir = final
    return final


def summary(res: ReleaseResult) -> dict[str, Any]:
    rows = res.catalogue["rows"]
    return {
        "release": res.release,
        "rows": len(rows),
        "generations_with_rows": len({r["generation_id"] for r in rows}),
        "facts": len(res.facts),
        "sources": [s["id"] for s in res.catalogue["sources"]],
        "matched_records": res.match.matched_records,
        "excluded_records": dict(res.match.excluded),
        "unmatched_records": res.unmatched_count,
        "unmatched_seed_makes": len(res.match.unmatched),
        "validation_problems": len(res.problems),
        "conflicts": len(res.conflicts),
        "gated_sources": res.gated,
        "real_range_rungs": dict(Counter(r.get("real_range_rung") or "none" for r in rows)),
        "quality_tiers": dict(Counter(r["quality_tier"] for r in rows)),
        "catalogue_json_bytes": res.catalogue_bytes,
        "catalogue_json_gzip_bytes": res.catalogue_gzip_bytes,
        "diff": res.diff["counts"],
    }


def run_log(res: ReleaseResult, outcome: str) -> dict[str, Any]:
    return {
        "step": "release",
        "at": res.catalogue["generated_at"],
        "inputs": res.inputs,
        "outputs": summary(res),
        "outcome": outcome,
    }


def release_cmd(
    dry_run: bool,
    *,
    data_dir: Path | None = None,
    now: datetime | None = None,
    today: date | None = None,
) -> int:
    data_dir = data_dir or default_data_dir()
    if today is not None and now is None:
        now = datetime(today.year, today.month, today.day, tzinfo=UTC)
    try:
        res = build_release(data_dir, now=now)
    except ReleaseError as exc:
        print(f"release failed: {exc}", file=sys.stderr)
        return 1
    if dry_run:
        print(json.dumps(run_log(res, "dry-run (nothing written)"), indent=1))
        return 0
    try:
        out = write_release(res, data_dir)
    except ReleaseError as exc:
        print(f"release failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(run_log(res, f"published {out}"), indent=1))
    return 0
