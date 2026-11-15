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

T-025 additions:
- **Manual figures** (`data/manual/charging/*.yaml`, written by WS3): one file per source,
  `source_id` = a data/sources.yaml id, each row a ChargingStat without `entered_by` (set to
  `staff`) and with a required `source_url`. Same gate and checks as downloads. A manual row
  that repeats a downloaded figure (same country, region, metric, band, definition and date)
  is dropped: the download wins.
- **Release diff** (`charging_review_rows`): per series, a new figure that grew more than
  15 % a month (compound) since the series' previous date, any fall, a revised figure, or a
  series/date that the previous release had and this one lacks goes to
  `data/review/charging_changes.csv`.
  Review only: the release still ships.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from ev_pipeline.release.gate import Registry
from ev_pipeline.release.validate import ReleaseError, _schema

FILE_NAME = "charging_stats.json"
SUFFIX = ".charging_stats.jsonl"
MANUAL_FORMAT = "manual-charging/v1"
REVIEW_FILE = "charging_changes.csv"
CHANGE_LIMIT = 0.15  # T-025 acceptance: more than 15 % between consecutive dates -> review
REVIEW_COLUMNS = [
    "source_id", "record_key", "country", "region", "metric_id", "power_band_id",
    "definition_id", "period_end", "previous_period_end", "value", "previous_value",
    "change_pct", "reason",
]  # fmt: skip


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
    manual_dir: Path | None = None,
) -> ChargingStatsResult:
    out = ChargingStatsResult()
    groups = _staging_groups(staging, out) + _manual_groups(manual_dir, out)
    if not groups:
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
    seen: set[tuple[Any, ...]] = set()
    for name, meta, rows, problems in groups:
        sid = str(meta.get("source") or name)
        info: dict[str, Any] = {"source": sid, "rows_in": len(rows) + len(problems)}
        why = registry.reason_blocked(sid)
        if why is None and meta.get("releasable") is not True:
            why = "meta.json: releasable is not true"
        if why is None and not have_taxonomy:
            why = "charging taxonomy tables missing, ids cannot be checked"
        if why is not None:
            per_file[name] = {**info, "shipped": 0, "gated": why}
            continue
        dropped: Counter[str] = Counter(problems)
        kept = 0
        for row in rows:
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
            key = series_key(row) + (row["period_end"],)
            if key in seen:
                dropped["repeats a figure already loaded (downloads win over manual)"] += 1
                continue
            seen.add(key)
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
                url = (meta.get("download") or {}).get("url") or meta.get("url")
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


# --- inputs ------------------------------------------------------------------------------

Group = tuple[str, dict[str, Any], list[dict[str, Any]], list[str]]
"""(name, meta, rows, problems): one input file, its meta, parsed rows, unparseable rows."""


def _staging_groups(staging: Path, out: ChargingStatsResult) -> list[Group]:
    files = sorted(staging.glob(f"*{SUFFIX}")) if staging.is_dir() else []
    groups: list[Group] = []
    for path in files:
        name = path.name.removesuffix(SUFFIX)
        meta_path = path.with_name(f"{name}.charging_stats.meta.json")
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        out.inputs.append({"path": str(path), "records": len(lines)})
        groups.append((name, meta, [json.loads(ln) for ln in lines], []))
    return groups


def _manual_groups(manual_dir: Path | None, out: ChargingStatsResult) -> list[Group]:
    """data/manual/charging/*.yaml -> groups; staff rows get entered_by + a stable id."""
    if manual_dir is None or not manual_dir.is_dir():
        return []
    groups: list[Group] = []
    for path in sorted(manual_dir.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        name = f"manual-{path.stem}"
        problems: list[str] = []
        rows: list[dict[str, Any]] = []
        if doc.get("schema") != MANUAL_FORMAT:
            problems = [f"{path.name}: schema must be {MANUAL_FORMAT}"] * max(
                1, len(doc.get("stats") or [])
            )
        sid = str(doc.get("source_id") or "")
        for raw in doc.get("stats") or [] if not problems else []:
            if not isinstance(raw, dict):
                problems.append("manual row is not a mapping")
                continue
            row = {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in raw.items()}
            row.setdefault("source_id", sid)
            row["entered_by"] = "staff"
            if not row.get("source_url"):
                problems.append("manual row without source_url")
                continue
            row.setdefault(
                "id",
                "manual:"
                + ":".join(
                    str(row.get(k) or "-")
                    for k in ("country", "region", "metric_id", "power_band_id", "period_end")
                ),
            )
            rows.append(row)
        meta = {
            "source": sid or name,
            "releasable": True,  # the registry gate still decides (reason_blocked)
            "licence": doc.get("licence"),
            "attribution": doc.get("attribution"),
            "url": doc.get("url"),
        }
        meta = {k: v for k, v in meta.items() if v is not None}
        out.inputs.append({"path": str(path), "records": len(rows) + len(problems)})
        groups.append((name, meta, rows, problems))
    return groups


# --- release diff (T-025) ----------------------------------------------------------------


def monthly_rate(old: float, new: float, old_date: str, new_date: str) -> float:
    """Growth per month between two dates (compound), so yearly or quarterly series are held
    to the same month-on-month limit as monthly ones. Gaps under a month count as one month."""
    from datetime import date

    days = (date.fromisoformat(new_date[:10]) - date.fromisoformat(old_date[:10])).days
    months = max(1.0, days / 30.44)
    return float((new / old) ** (1 / months) - 1)


def series_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row.get("country"),
        row.get("region"),
        row.get("metric_id"),
        row.get("power_band_id"),
        row.get("definition_id"),
    )


def _by_series(doc: dict[str, Any] | None) -> dict[tuple[Any, ...], dict[str, dict[str, Any]]]:
    out: dict[tuple[Any, ...], dict[str, dict[str, Any]]] = defaultdict(dict)
    for r in (doc or {}).get("stats") or []:
        out[series_key(r)][str(r["period_end"])] = r
    return out


def _review_row(
    r: dict[str, Any], prev: dict[str, Any] | None, reason: str, prev_period: str = ""
) -> dict[str, str]:
    value = r.get("value")
    pv = prev.get("value") if prev else None
    pct = ""
    if isinstance(value, int | float) and isinstance(pv, int | float) and pv:
        pct = f"{(value - pv) / pv * 100:+.1f}"
    return {
        "source_id": str(r.get("source_id") or ""),
        "record_key": "|".join(str(x or "") for x in series_key(r)) + f"|{r.get('period_end')}",
        "country": str(r.get("country") or ""),
        "region": str(r.get("region") or ""),
        "metric_id": str(r.get("metric_id") or ""),
        "power_band_id": str(r.get("power_band_id") or ""),
        "definition_id": str(r.get("definition_id") or ""),
        "period_end": str(r.get("period_end") or ""),
        "previous_period_end": prev_period,
        "value": "" if value is None else str(value),
        "previous_value": "" if pv is None else str(pv),
        "change_pct": pct,
        "reason": reason,
    }


def charging_review_rows(
    previous: dict[str, Any] | None, current: dict[str, Any] | None, limit: float = CHANGE_LIMIT
) -> list[dict[str, str]]:
    """Figures a person should look at before trusting this release (review only).

    - step: a date new in this release whose value grew more than `limit` per month
      (compound, so yearly series are comparable) since the series' previous date, or fell
      (public charger counts should only grow). With no previous
      release every consecutive pair is checked once, as a baseline.
    - revised: the same series and date as the previous release, different value.
    - dropped: a series/date the previous release had and this one lacks.
    """
    cur, prev = _by_series(current), _by_series(previous)
    out: list[dict[str, str]] = []
    for key in sorted(cur, key=str):
        dates = sorted(cur[key])
        old = prev.get(key, {})
        for i, d in enumerate(dates):
            r = cur[key][d]
            if d in old:
                if old[d].get("value") != r.get("value"):
                    out.append(_review_row(r, old[d], "revised since the previous release", d))
                continue
            if previous is not None and old == {} and i == 0:
                continue  # a brand-new series: its first date has nothing to compare with
            if i == 0:
                continue
            p = cur[key][dates[i - 1]]
            pv, v = p.get("value"), r.get("value")
            if not isinstance(pv, int | float) or not isinstance(v, int | float):
                continue
            if v < pv:
                out.append(_review_row(r, p, "fell since the previous date", dates[i - 1]))
            elif pv and monthly_rate(pv, v, dates[i - 1], d) > limit:
                why = f"rose more than {limit:.0%} a month since the previous date"
                out.append(_review_row(r, p, why, dates[i - 1]))
    for key in sorted(prev, key=str):
        for d in sorted(prev[key]):
            if d not in cur.get(key, {}):
                out.append(_review_row(prev[key][d], None, "in the previous release, missing now"))
    return out
