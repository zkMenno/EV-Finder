"""T-059: "Known issues" from RDW APK defects (data/staging/rdw-defects.defects.jsonl).

The adapter (sources/rdw_defects) writes per make x trade name x first-registration year:
`defect_group` rows (sample_cars, cars_with_any_defect) and `defect_count` rows (cars with one
defect code). Groups under MIN_SAMPLE_CARS sampled cars and codes on fewer than
MIN_CARS_PER_CODE cars were already dropped there; the same minimums apply again here after
groups are summed per generation.

Here each group is placed on a seed generation (make + trade name through the RDW aliases of
data/seed/models.yaml, then the first-registration year). A year shared by two generations is
placed only when exactly one of them has catalogue rows; otherwise it is skipped and counted,
never split. Groups landing on the same generation and year are summed.

**Comparison only within a first-registration year (Q-078).** Older cars have had more APKs
in the report window, and the youngest cohort has barely had its first one. So every cohort
carries the baseline of *all* sampled BEVs of its own year (every make, also those not in the
seed) and the UI compares with that, never across years. `few_reports` marks cohorts to hide
by default: the whole year has fewer than MIN_COHORT_REPORT_SHARE cars with any report (young
cohort), or the cohort itself has fewer than MIN_REPORTED_CARS cars with a report.

Rates are per 100 *sampled* cars (the adapter's 10 % plate sample of that year). The data has
no inspection count per car, so a car with no defect report counts as zero whether or not it
was inspected. The codes' summed counts slightly undercount, because codes under the
per-group minimum were dropped before summing. Labels are RDW's own Dutch text (hx2c-gt7k);
RDW publishes no English label.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ev_pipeline.match.matcher import find_by_source_alias, find_model_noted
from ev_pipeline.match.seed import Seed, SeedModel
from ev_pipeline.records import SourceRecord
from ev_pipeline.sources.rdw_defects.adapter import MIN_CARS_PER_CODE, MIN_SAMPLE_CARS

SOURCE_ID = "rdw-defects"  # data/sources.yaml id of the defects dataset
MATCH_AS = "rdw"  # its make/trade names are RDW register names: match with RDW's aliases
STAGING_FILE = "rdw-defects.defects.jsonl"
TOP_N = 5
MIN_REPORTED_CARS = 10
MIN_COHORT_REPORT_SHARE = 0.10
# (first age, last age or None, label): age = fetch year - first-registration year.
AGE_BANDS: tuple[tuple[int, int | None, str], ...] = (
    (0, 4, "up to 4 years"),
    (5, 6, "5-6 years"),
    (7, 9, "7-9 years"),
    (10, None, "10+ years"),
)
RATE_BASIS = (
    "Cars with the defect per 100 sampled cars of the same generation and first-registration "
    "year (RDW APK reports in the window; cars without a report count as zero). Compare only "
    "with the same first-registration year."
)


def age_band(age: int) -> str:
    for lo, hi, label in AGE_BANDS:
        if age >= lo and (hi is None or age <= hi):
            return label
    return AGE_BANDS[0][2]


@dataclass
class _Cohort:
    sample: int = 0
    any_defect: int = 0
    codes: Counter[str] = field(default_factory=Counter)
    keys: list[str] = field(default_factory=list)


@dataclass
class KnownIssuesResult:
    section: dict[str, Any] | None = None
    source: dict[str, Any] | None = None
    log: dict[str, Any] = field(default_factory=dict)


def read_defects(staging: Path) -> list[dict[str, Any]]:
    path = staging / STAGING_FILE
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _per_100(n: int, d: int) -> float:
    return round(100 * n / d, 1) if d else 0.0


def _place(
    row: dict[str, Any], seed: Seed, gens_with_rows: set[str], scoped: bool
) -> tuple[str | None, str]:
    view = SourceRecord.model_validate(
        {
            "source": {"id": MATCH_AS, "name": "RDW", "licence": "CC0-1.0"},
            "record_key": str(row.get("record_key")),
            "make": str(row.get("make") or ""),
            "model": str(row.get("model") or ""),
            "year": row.get("year"),
            "retrieved_at": row.get("retrieved_at"),
            "confidence": row.get("confidence") or "medium",
        }
    )
    make_id = seed.make_id_for(view.make, MATCH_AS, scoped)
    model: SeedModel | None
    if make_id is None:
        model, _ = find_by_source_alias(seed, view, scoped)
    else:
        model, _, _ = find_model_noted(seed, make_id, view, scoped)
    if model is None:
        return None, "model not in seed"
    year = view.year
    hits = [g for g in model.generations if year is not None and g.covers(year)]
    if not hits:
        return None, "year outside every generation"
    if len(hits) == 1:
        return hits[0].id, ""
    with_rows = [g for g in hits if g.id in gens_with_rows]
    if len(with_rows) == 1:
        return with_rows[0].id, ""
    return None, "shared year, generation unknown"


def build_known_issues(
    rows: list[dict[str, Any]],
    seed: Seed,
    gens_with_rows: set[str],
    releasable: Any,
    scoped: bool = True,
) -> KnownIssuesResult:
    """`releasable(source_id) -> bool` is the licence gate. Returns no section when the source
    is gated, or when nothing could be placed."""
    out = KnownIssuesResult()
    groups = [r for r in rows if r.get("kind") == "defect_group"]
    counts = [r for r in rows if r.get("kind") == "defect_count"]
    if not groups:
        out.log = {"status": "no input"}
        return out
    row_sources = {str((r.get("source") or {}).get("id")) for r in rows}
    blocked = sorted(s for s in {SOURCE_ID, *row_sources} if not releasable(s))
    if blocked:
        out.log = {"status": "gated", "blocked_sources": blocked, "rows": len(rows)}
        return out
    if row_sources != {SOURCE_ID}:
        # The adapter writes SOURCE id "rdw-defects" itself; an older staging file (id "rdw")
        # is refused rather than renamed: re-run `ev normalise rdw-defects`.
        out.log = {"status": "wrong source id", "source_ids": sorted(row_sources)}
        return out

    # Per-year baseline over every sampled BEV group (all makes).
    year_base: dict[int, _Cohort] = defaultdict(_Cohort)
    by_key = {r["record_key"]: r for r in groups}
    for g in groups:
        b = year_base[int(g["year"])]
        b.sample += int(g["sample_cars"])
        b.any_defect += int(g["cars_with_any_defect"])
    labels: dict[str, dict[str, str]] = {}
    codes_of: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for c in counts:
        group_key = str(c["record_key"]).split("#defect:", 1)[0]
        codes_of[group_key].append(c)
        year_base[int(c["year"])].codes[str(c["defect_code"])] += int(c["cars_with_defect"])
        lab = {"code": str(c["defect_code"]), "label_nl": str(c.get("defect_description") or "")}
        if c.get("defect_article"):
            lab["article"] = str(c["defect_article"])
        labels.setdefault(lab["code"], lab)

    placed: dict[tuple[str, int], _Cohort] = defaultdict(_Cohort)
    skipped: Counter[str] = Counter()
    for key_, g in sorted(by_key.items()):
        gid, why = _place(g, seed, gens_with_rows, scoped)
        if gid is None:
            skipped[why] += 1
            continue
        co = placed[(gid, int(g["year"]))]
        co.sample += int(g["sample_cars"])
        co.any_defect += int(g["cars_with_any_defect"])
        co.keys.append(key_)
        for c in codes_of.get(key_, []):
            co.codes[str(c["defect_code"])] += int(c["cars_with_defect"])

    retrieved = max(str(r.get("retrieved_at")) for r in groups)
    fetch_year = int(retrieved[:4])
    gens_per_year = Counter(y for (_, y), co in placed.items() if co.sample >= MIN_SAMPLE_CARS)
    by_generation: dict[str, list[dict[str, Any]]] = defaultdict(list)
    used_codes: set[str] = set()
    small = 0
    for (gid, year), co in sorted(placed.items()):
        if co.sample < MIN_SAMPLE_CARS:
            small += 1
            continue
        base = year_base[year]
        defects = sorted(
            ((code, n) for code, n in co.codes.items() if n >= MIN_CARS_PER_CODE),
            key=lambda t: (-t[1], t[0]),
        )[:TOP_N]
        used_codes |= {code for code, _ in defects}
        few = (
            co.any_defect < MIN_REPORTED_CARS
            or (base.any_defect / base.sample if base.sample else 0) < MIN_COHORT_REPORT_SHARE
        )
        age = fetch_year - year
        by_generation[gid].append(
            {
                "first_registration_year": year,
                "age_years": age,
                "age_band": age_band(age),
                "sample_cars": co.sample,
                "cars_with_any_defect": co.any_defect,
                "any_defect_per_100": _per_100(co.any_defect, co.sample),
                "few_reports": few,
                "cohort": {
                    "generations": gens_per_year[year],
                    "sample_cars": base.sample,
                    "any_defect_per_100": _per_100(base.any_defect, base.sample),
                },
                "defects": [
                    {
                        "code": code,
                        "cars_with_defect": n,
                        "per_100": _per_100(n, co.sample),
                        "cohort_per_100": _per_100(base.codes[code], base.sample),
                    }
                    for code, n in defects
                ],
                "source_records": sorted(co.keys),
            }
        )
    if not by_generation:
        out.log = {"status": "nothing placed", "skipped_groups": dict(skipped)}
        return out
    first = groups[0]
    src = dict(first.get("source") or {})
    out.source = {
        k: v for k, v in src.items() if k in ("id", "name", "url", "licence", "attribution")
    }
    out.section = {
        "country": str(first.get("country") or "NL"),
        "source_id": SOURCE_ID,
        "retrieved_at": retrieved,
        "confidence": str(first.get("confidence") or "medium"),
        "inspection": str(first.get("inspection") or ""),
        "reported_from": min(str(g["reported_from"]) for g in groups),
        "reported_to": max(str(g["reported_to"]) for g in groups),
        "sample_rule": str(first.get("sample_rule") or ""),
        "rate_basis": RATE_BASIS,
        "min_sample_cars": MIN_SAMPLE_CARS,
        "min_cars_per_code": MIN_CARS_PER_CODE,
        "top_n": TOP_N,
        "codes": [labels[c] for c in sorted(used_codes)],
        "by_generation": dict(sorted(by_generation.items())),
    }
    cohorts = [c for cs in by_generation.values() for c in cs]
    out.log = {
        "status": "shipped",
        "groups_in": len(groups),
        "groups_placed": sum(len(co.keys) for co in placed.values()),
        "skipped_groups": dict(sorted(skipped.items())),
        "generations": len(by_generation),
        "cohorts": len(cohorts),
        "cohorts_few_reports": sum(1 for c in cohorts if c["few_reports"]),
        "cohorts_below_min_sample": small,
        "codes": len(used_codes),
    }
    return out
