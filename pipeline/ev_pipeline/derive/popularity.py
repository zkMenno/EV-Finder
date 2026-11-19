"""T-149: `generations[].popularity` for the "Most popular" sort (Decision 038 blend, T-130).

score (0-100, one decimal) = 100 x (w_reg x reg / max reg + w_pick x pick) / (w_reg + w_pick)

- **reg**: the generation's share of the release's own used-fleet registration facts
  (`rows[].registrations`, kind `fleet`), averaged over the ranking sources of the top-40 method
  (`qa.top40.RANK_SOURCES`: RDW NL fleet, DfT UK fleet). Shares are taken per source against the
  catalogue's total for that source, so counts of different sources are never added into the
  score. A model-level count (the source could not tell generations apart) is split over the
  model's generations by their RDW generation counts, evenly when there are none: the same rule
  as the web build had (`apps/web/src/lib/popularity.ts` generationShares).
- **pick**: Menno's best verdict for the generation in data/editorial/menno-picks.yaml, plus the
  favourite bonus, capped at 1 (weights and values in config/popularity.yaml, never in code).
- `registrations` = the counts attributed to the generation, summed over those sources (a
  display figure; the score never adds sources). `as_of` = end of the newest period used.
- No registration count for a generation → no popularity field (schema: absent when nothing
  matched). `rank` 1 = most popular among the generations that have one.
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

import yaml

CONFIG_FILE = Path("popularity.yaml")  # under config/
PICKS_FILE = Path("editorial") / "menno-picks.yaml"  # under data/
VERDICTS = ("shortlist", "consider", "fallback")
FLEET = "fleet"


class PopularityConfigError(ValueError):
    pass


def _num(v: object) -> float | None:
    if isinstance(v, bool) or not isinstance(v, int | float):
        return None
    return float(v)


def parse_config(doc: dict[str, Any] | None) -> dict[str, Any]:
    """Validated blend config (same rules as apps/web/scripts/popularity.mjs parseConfig)."""
    w = (doc or {}).get("weights") or {}
    reg, picks = _num(w.get("registrations")), _num(w.get("owner_picks"))
    if reg is None or picks is None or reg < 0 or picks < 0 or reg + picks <= 0:
        raise PopularityConfigError(
            "popularity.yaml: weights.registrations and weights.owner_picks must be numbers"
            " >= 0, not both 0"
        )
    values: dict[str, float] = {}
    for v in VERDICTS:
        x = _num(((doc or {}).get("pick_values") or {}).get(v))
        if x is None or not 0 <= x <= 1:
            raise PopularityConfigError(f"popularity.yaml: pick_values.{v} must be from 0 to 1")
        values[v] = x
    bonus = _num((doc or {}).get("favourite_bonus"))
    bonus = 0.0 if bonus is None else bonus
    if not 0 <= bonus <= 1:
        raise PopularityConfigError("popularity.yaml: favourite_bonus must be from 0 to 1")
    return {"registrations": reg, "owner_picks": picks, "pick_values": values, "bonus": bonus}


def pick_scores(picks_doc: dict[str, Any] | None, cfg: dict[str, Any]) -> dict[str, float]:
    """generation id -> 0..1: best verdict (+ favourite bonus, capped at 1). No verdict → absent."""
    out: dict[str, float] = {}
    for e in (picks_doc or {}).get("primary_car_picks") or []:
        gen, verdict = e.get("seed_generation_id"), e.get("verdict")
        if not isinstance(gen, str) or verdict not in VERDICTS:
            continue
        bonus = cfg["bonus"] if e.get("favourite") is True else 0.0
        v = min(1.0, cfg["pick_values"][verdict] + bonus)
        if v > 0:
            out[gen] = max(out.get(gen, 0.0), v)
    return out


_QUARTER = re.compile(r"^(\d{4})-Q([1-4])$")
_MONTHS = re.compile(r"^(\d{4})-(\d{2})(?:\.\.(\d{2}))?$")
_QUARTER_END = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}


def period_end(period: str) -> date | None:
    """Last day of a registration period: 2026-11-18, 2026-Q2, 2025-01..12, 2025."""
    import calendar

    p = period.strip()
    try:
        return date.fromisoformat(p)
    except ValueError:
        pass
    if m := _QUARTER.match(p):
        mm, dd = _QUARTER_END[int(m.group(2))]
        return date(int(m.group(1)), mm, dd)
    if m := _MONTHS.match(p):
        y, last = int(m.group(1)), int(m.group(3) or m.group(2))
        if 1 <= last <= 12:
            return date(y, last, calendar.monthrange(y, last)[1])
        return None
    if re.fullmatch(r"\d{4}", p):
        return date(int(p), 12, 31)
    return None


def _fleet_counts(
    rows: list[dict[str, Any]], sources: dict[str, str]
) -> tuple[dict[str, dict[str, int]], dict[str, dict[str, int]], dict[str, date]]:
    """Per source: generation-level counts, model-level counts, newest period end."""
    gen_counts: dict[str, dict[str, int]] = defaultdict(dict)
    model_counts: dict[str, dict[str, int]] = defaultdict(dict)
    newest: dict[str, date] = {}
    for r in rows:
        gid, mid = str(r.get("generation_id")), str(r.get("model_id") or "")
        for cc, entries in (r.get("registrations") or {}).items():
            for e in entries or []:
                sid, n = e.get("source_id"), e.get("count")
                if sources.get(str(sid)) != cc or e.get("kind") != FLEET:
                    continue
                if not isinstance(n, int) or isinstance(n, bool) or n < 0:
                    continue
                if e.get("level") == "model":
                    model_counts[sid][mid] = max(model_counts[sid].get(mid, 0), n)
                else:
                    gen_counts[sid][gid] = max(gen_counts[sid].get(gid, 0), n)
                end = period_end(str(e.get("period") or ""))
                if end is not None and (sid not in newest or end > newest[sid]):
                    newest[sid] = end
    return gen_counts, model_counts, newest


def attributed_counts(
    rows: list[dict[str, Any]], generations: list[dict[str, Any]], sources: dict[str, str]
) -> tuple[dict[str, dict[str, float]], dict[str, date]]:
    """source id -> generation id -> cars (model-level counts split, see module doc)."""
    gen_counts, model_counts, newest = _fleet_counts(rows, sources)
    in_rows = {str(r.get("generation_id")) for r in rows}
    gens_of: dict[str, list[str]] = defaultdict(list)
    for g in generations:
        if g["id"] in in_rows:
            gens_of[str(g.get("model_id"))].append(g["id"])
    split_by = gen_counts.get(next(iter(sources), ""), {})  # first ranking source = RDW
    out: dict[str, dict[str, float]] = {}
    for sid in sources:
        a: dict[str, float] = {g: float(n) for g, n in gen_counts.get(sid, {}).items()}
        for mid, n in model_counts.get(sid, {}).items():
            ids = sorted(gens_of.get(mid) or [])
            if not ids or n <= 0:
                continue
            weights = [split_by.get(g, 0) for g in ids]
            total = sum(weights)
            for g, w in zip(ids, weights, strict=True):
                a[g] = a.get(g, 0.0) + (n * w / total if total > 0 else n / len(ids))
        out[sid] = {g: v for g, v in a.items() if v > 0}
    return out, newest


def build_popularity(
    rows: list[dict[str, Any]],
    generations: list[dict[str, Any]],
    config_doc: dict[str, Any] | None,
    picks_doc: dict[str, Any] | None,
    rank_sources: dict[str, str] | None = None,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """(generation id -> popularity field, run-log section)."""
    if rank_sources is None:
        from ev_pipeline.qa.top40 import RANK_SOURCES as rank_sources
    cfg = parse_config(config_doc)
    picks = pick_scores(picks_doc, cfg)
    counts, newest = attributed_counts(rows, generations, rank_sources)
    totals = {sid: sum(c.values()) for sid, c in counts.items()}
    gids = sorted({g for c in counts.values() for g in c})
    reg = {
        g: sum(counts[s].get(g, 0.0) / totals[s] for s in rank_sources if totals.get(s))
        / len(rank_sources)
        for g in gids
    }
    top = max(reg.values(), default=0.0)
    wr, wp = cfg["registrations"], cfg["owner_picks"]
    scored: list[tuple[float, str]] = []
    fields: dict[str, dict[str, Any]] = {}
    for g in gids:
        s = 100 * (wr * (reg[g] / top if top > 0 else 0) + wp * picks.get(g, 0.0)) / (wr + wp)
        used = sorted(sid for sid in rank_sources if counts[sid].get(g))
        fields[g] = {
            "score": round(s, 1),
            "registrations": round(sum(counts[sid].get(g, 0.0) for sid in used)),
            "as_of": max(newest[sid] for sid in used if sid in newest).isoformat()
            if any(sid in newest for sid in used)
            else None,
            "source_ids": used,
        }
        scored.append((round(s, 1), g))
    for rank, (_, g) in enumerate(sorted(scored, key=lambda t: (-t[0], t[1])), start=1):
        fields[g]["rank"] = rank
    fields = {g: f for g, f in fields.items() if f["as_of"] is not None}
    log = {
        "generations": len(fields),
        "rank_sources": dict(rank_sources),
        "totals": {k: round(v) for k, v in sorted(totals.items())},
        "as_of": {k: v.isoformat() for k, v in sorted(newest.items())},
        "weights": {"registrations": wr, "owner_picks": wp},
        "owner_picks": len(picks),
        "picks_without_registrations": sorted(set(picks) - set(fields)),
    }
    return fields, log


def attach_popularity(
    catalogue: dict[str, Any], config_dir: Path, data_dir: Path
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Set `generations[].popularity`; returns (run-log section, inputs). A missing config file
    means no field (logged); a broken one raises (config errors are bugs, not data)."""
    cfg_path = config_dir / CONFIG_FILE
    picks_path = data_dir / PICKS_FILE
    if not cfg_path.exists():
        return {"status": f"skipped: {cfg_path.name} not found"}, []
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    picks = yaml.safe_load(picks_path.read_text(encoding="utf-8")) if picks_path.exists() else None
    model_of = {g["id"]: g.get("model_id") for g in catalogue["generations"]}
    rows = [{**r, "model_id": model_of.get(r.get("generation_id"))} for r in catalogue["rows"]]
    fields, log = build_popularity(rows, catalogue["generations"], cfg, picks)
    for g in catalogue["generations"]:
        g.pop("popularity", None)
        if g["id"] in fields:
            g["popularity"] = fields[g["id"]]
    inputs = [{"path": str(cfg_path)}] + ([{"path": str(picks_path)}] if picks else [])
    return {"status": "attached", **log}, inputs
