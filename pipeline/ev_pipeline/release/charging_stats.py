"""T-059: charging statistics (Decision 012, aggregates only) -> releases/<n>/charging_stats.json.

Inputs: `data/staging/<source>.charging_stats.jsonl` (one ChargingStat per line) and its
`.meta.json` (registry source id, licence, attribution, `releasable`), written by the eafo,
bnetza and dft-charging loaders. Never point-level data.

A file ships only when its registry source passes the licence gate and its meta says
`releasable: true` (EAFO is `blocked`, Q-077). Every row is then checked again:
- its `source_id` (the taxonomy id, e.g. `bnetza-ladesaeulenregister`) must resolve through
  the data/sources.yaml `aliases` (Q-075) to that same releasable source;
- it must validate against the schema's ChargingStat def;
- its metric, definition and power band must exist in the catalogue taxonomy tables, and the
  definition must belong to the same source. Without those tables nothing ships (ids that
  cannot be checked are not published).
Rows failing a check are dropped and counted in the run log. The finished document is
validated against ChargingStatsRelease; a failure there stops the release.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from ev_pipeline.release.gate import Registry
from ev_pipeline.release.validate import ReleaseError, _schema

FILE_NAME = "charging_stats.json"
SUFFIX = ".charging_stats.jsonl"


@dataclass
class ChargingStatsResult:
    document: dict[str, Any] | None = None
    inputs: list[dict[str, Any]] = field(default_factory=list)
    log: dict[str, Any] = field(default_factory=dict)


def _validator(def_name: str) -> Draft202012Validator:
    schema = dict(_schema())
    schema["$ref"] = f"#/$defs/{def_name}"
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _ids(taxonomy: dict[str, Any] | None, table: str) -> dict[str, dict[str, Any]]:
    return {str(r["id"]): r for r in (taxonomy or {}).get(table) or []}


def build_charging_stats(
    staging: Path,
    registry: Registry,
    taxonomy: dict[str, Any] | None,
    release: int,
    generated_at: str,
) -> ChargingStatsResult:
    out = ChargingStatsResult()
    files = sorted(staging.glob(f"*{SUFFIX}")) if staging.is_dir() else []
    if not files:
        out.log = {"status": "no input"}
        return out
    stat_v = _validator("ChargingStat")
    metrics = _ids(taxonomy, "charging_metrics")
    definitions = _ids(taxonomy, "charging_definitions")
    bands = _ids(taxonomy, "power_bands")
    have_taxonomy = bool(metrics and definitions)
    per_file: dict[str, dict[str, Any]] = {}
    stats: list[dict[str, Any]] = []
    sources: dict[str, dict[str, Any]] = {}
    aliases: dict[str, str] = {}
    for path in files:
        name = path.name.removesuffix(SUFFIX)
        meta_path = path.with_name(f"{name}.charging_stats.meta.json")
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        sid = str(meta.get("source") or name)
        lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        info: dict[str, Any] = {"source": sid, "rows_in": len(lines)}
        out.inputs.append({"path": str(path), "records": len(lines)})
        why = registry.reason_blocked(sid)
        if why is None and meta.get("releasable") is not True:
            why = "meta.json: releasable is not true"
        if why is None and not have_taxonomy:
            why = "charging taxonomy tables missing, ids cannot be checked"
        if why is not None:
            per_file[name] = {**info, "shipped": 0, "gated": why}
            continue
        dropped: Counter[str] = Counter()
        kept = 0
        for ln in lines:
            row = json.loads(ln)
            rsid = str(row.get("source_id"))
            if registry.canonical(rsid) != sid:
                dropped[f"source_id {rsid} is not {sid} or one of its aliases"] += 1
                continue
            if next(iter(stat_v.iter_errors(row)), None) is not None:
                dropped["fails the ChargingStat schema"] += 1
                continue
            d = definitions.get(str(row["definition_id"]))
            if d is None:
                dropped["unknown definition_id"] += 1
                continue
            if registry.canonical(str(d.get("source_id"))) != sid:
                dropped["definition belongs to another source"] += 1
                continue
            if str(row["metric_id"]) not in metrics:
                dropped["unknown metric_id"] += 1
                continue
            if row.get("power_band_id") is not None and str(row["power_band_id"]) not in bands:
                dropped["unknown power_band_id"] += 1
                continue
            stats.append(row)
            kept += 1
            if rsid != sid:
                aliases[rsid] = sid
            if rsid not in sources:
                src: dict[str, Any] = {
                    "id": rsid,
                    "name": registry.sources[sid].name,
                    "licence": str(meta.get("licence") or registry.sources[sid].licence),
                }
                url = (meta.get("download") or {}).get("url")
                if url:
                    src["url"] = str(url)
                if meta.get("attribution"):
                    src["attribution"] = str(meta["attribution"])
                sources[rsid] = src
        per_file[name] = {**info, "shipped": kept, "dropped": dict(sorted(dropped.items()))}
    out.log = {"status": "shipped" if stats else "nothing shipped", "files": per_file}
    if not stats:
        return out
    stats.sort(
        key=lambda r: (r["country"], r["source_id"], r["metric_id"], r["period_end"], r["id"])
    )
    doc: dict[str, Any] = {
        "release": release,
        "generated_at": generated_at,
        "sources": [sources[k] for k in sorted(sources)],
        "source_aliases": dict(sorted(aliases.items())),
        "stats": stats,
    }
    errors = [e.message for e in _validator("ChargingStatsRelease").iter_errors(doc)][:10]
    if errors:
        raise ReleaseError("charging_stats.json fails the schema: " + "; ".join(errors))
    out.document = doc
    out.log["stats"] = len(stats)
    out.log["by_source"] = dict(sorted(Counter(r["source_id"] for r in stats).items()))
    return out
