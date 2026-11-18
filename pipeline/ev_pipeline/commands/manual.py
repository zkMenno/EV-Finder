"""`ev manual check`: validate every data/manual/<topic>/*.yaml file (addendum 6, P7).

Checks each fact against the schema `Fact` def plus the manual-entry rules (source URL,
retrieved date, quote or locator, entered_by, unit matches field; see manual/facts.py).
Ids that the seed or the latest release does not know are warnings, not errors (a variant
may be added later), except in fixture files where they are expected. An id listed in
data/seed/retired_ids.yaml is an error that names the successor: such a fact never applies
(A-36 S7: T-110 / T-112 facts on the retired hyundai-ioniq-5-gen1-n were silently dropped).
Exit 1 on any error.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import yaml

from ev_pipeline.manual.facts import ManualIssue, gate_reason, load_manual_dir
from ev_pipeline.release.gate import load_registry
from ev_pipeline.release.retired import load_hand_kept


def _default_data_dir() -> Path:
    from ev_pipeline.release.build import default_data_dir

    return default_data_dir()


def known_ids(data_dir: Path) -> tuple[set[str], set[str]]:
    """(generation ids from the seed, variant ids from variants.yaml + the latest release)."""
    gens: set[str] = set()
    variants: set[str] = set()
    models = data_dir / "seed" / "models.yaml"
    if models.exists():
        data = yaml.safe_load(models.read_text(encoding="utf-8")) or {}
        for make in data.get("makes") or []:
            for model in make.get("models") or []:
                for g in model.get("generations") or []:
                    if g.get("id"):
                        gens.add(str(g["id"]))
    seed_variants = data_dir / "seed" / "variants.yaml"
    if seed_variants.exists():
        data = yaml.safe_load(seed_variants.read_text(encoding="utf-8")) or {}
        variants |= {str(v["id"]) for v in data.get("variants") or [] if v.get("id")}
    latest = data_dir / "releases" / "latest"
    if latest.exists():
        cat = data_dir / "releases" / latest.read_text(encoding="utf-8").strip() / "catalogue.json"
        if cat.exists():
            rows = json.loads(cat.read_text(encoding="utf-8")).get("rows") or []
            variants |= {str(r["variant_id"]) for r in rows if r.get("variant_id")}
    return gens, variants


def check(data_dir: Path, today=None) -> tuple[int, list[str]]:
    """Returns (exit code, report lines)."""
    today = today or datetime.now(UTC).date()
    registry = load_registry(data_dir / "sources.yaml")
    load = load_manual_dir(data_dir, today, registry, for_release=False)
    gens, variants = known_ids(data_dir)
    retired = load_hand_kept(data_dir / "seed")
    issues = list(load.issues)
    for mf in load.facts:
        if mf.path in load.fixture_files:
            continue  # example ids exist only in test fixtures
        f = mf.fact
        sid = f.subject_id.root
        if sid in retired:
            to = retired[sid]
            issues.append(
                ManualIssue(
                    mf.path,
                    None,
                    mf.record_key,
                    f"{f.subject_type.value} {sid} is retired (data/seed/retired_ids.yaml): "
                    + (f"use {to}" if to else "it has no successor; remove the fact"),
                )
            )
            continue
        if f.subject_type.value == "variant" and variants and sid not in variants:
            issues.append(
                ManualIssue(mf.path, None, mf.record_key, f"variant {sid} unknown", warning=True)
            )
        if f.subject_type.value == "generation" and gens and sid not in gens:
            issues.append(
                ManualIssue(mf.path, None, mf.record_key, f"generation {sid} unknown", warning=True)
            )
    errors = [i for i in issues if not i.warning]
    lines = [i.text() for i in issues]
    # Decision 080: files may name their own source (e.g. a blocked third-party site).
    for sid in sorted({mf.fact.source.id.root for mf in load.facts} - {"manual"}):
        n = sum(1 for mf in load.facts if mf.fact.source.id.root == sid)
        why = registry.reason_blocked(sid)
        lines.append(
            f"Source `{sid}`: {n} facts, " + (f"internal only ({why})" if why else "releasable")
        )
    why = gate_reason(registry) if registry.loaded else "no data/sources.yaml"
    lines.append(
        f"{len(load.files)} files, {len(load.facts)} valid facts, {len(errors)} errors, "
        f"{len(issues) - len(errors)} warnings. Release status of source `manual`: "
        + (f"internal only ({why})" if why else "releasable")
    )
    return (1 if errors else 0), lines


def _run(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir) if args.data_dir else _default_data_dir()
    code, lines = check(data_dir)
    for line in lines:
        print(line)
    return code


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("manual", help="hand-entered, cited facts (data/manual/)")
    sub = p.add_subparsers(dest="manual_command", required=True)
    c = sub.add_parser("check", help="validate every data/manual/<topic>/*.yaml file")
    c.add_argument("--data-dir", help="data folder (default: EV_DATA_DIR or repo data/)")
    c.set_defaults(func=_run)
