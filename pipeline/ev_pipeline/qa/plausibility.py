"""Plausibility gate (T-111, QA A-35 B4): figures that are possible but not believable.

`checks.impossible_values` catches what cannot be true (usable > gross, WLTP > 10 km/kWh).
This gate catches what is very unlikely to be true, the way release 1 shipped the Tesla Model Y
Long Range AWD (gen1 and Juniper) at WLTP 719 km on 79 kWh (9.1 km/kWh for a 2-tonne SUV) and
387 km per 20 min DC, against 252 km for the Performance on the same pack.

Rules (thresholds in qa_plausibility.yaml next to this file, a gate file: G-06):
- `wltp_efficiency`: WLTP km per usable kWh above `review_above` -> review; above the
  body type's `withhold_above` -> the WLTP value is withheld as well.
- `dc_vs_peers`: dc_km_per_20min above `max_ratio` x the median of its peers (`min_peers`
  values, itself included). Peers on the same generation AND battery pack -> withheld;
  peers on the generation only (different packs charge differently) -> review.
- `copied_across_generations`: two variants of one model in different generations with the
  same values on `min_equal_fields` of `fields` (primary values, not derived) while their
  packs differ (pack id, else usable kWh) -> review (which one is the copy is unknown).

"Withheld" = the value and every derived value computed from it are taken out of the row
(set to null, provenance dropped) and listed in data/review/conflicts.csv. Values are never
edited ("AI proposes, rules decide"). Without the config file the gate does nothing and the
QA check says so (`skipped`), so code and thresholds can land in separate PRs.
"""

from __future__ import annotations

import math
import statistics
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

CONFIG_FILE = Path(__file__).with_name("qa_plausibility.yaml")
REVIEW, WITHHOLD = "review", "withhold"
REASON_PREFIX = "plausibility"
# Labels that only describe another value: they leave with it (no review row; not a value).
COMPANIONS: dict[str, tuple[str, ...]] = {"real_range_km": ("real_range_rung",)}
# Inputs every range estimate is built on (consumption matrix -> winter range, the shortlist's
# derived values). A withheld one means the WLTP / usable kWh / consumption set is not
# believable as a whole, so no range estimate is built on the row (PR #91 review).
RANGE_BASIS = frozenset({"wltp_range_km", "battery_kwh_net", "consumption_kwh_100km"})


@dataclass
class Issue:
    variant_id: str
    rule: str
    field: str
    value: float
    action: str  # review | withhold
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_config(path: Path | None = None) -> dict[str, Any] | None:
    """The thresholds, or None when the file is missing (gate off, QA check `skipped`)."""
    path = path or CONFIG_FILE
    if not path.exists():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _num(v: object) -> float | None:
    if isinstance(v, int | float) and not isinstance(v, bool) and math.isfinite(v):
        return float(v)
    return None


def _derived(row: dict[str, Any], f: str) -> bool:
    return bool(((row.get("provenance") or {}).get(f) or {}).get("derived"))


# --- rules ---------------------------------------------------------------------------------


def wltp_efficiency(rows: list[dict[str, Any]], cfg: dict[str, Any]) -> list[Issue]:
    review_above = float(cfg["review_above"])
    withhold = {str(k): float(v) for k, v in (cfg.get("withhold_above") or {}).items()}
    out = []
    for r in rows:
        net, wltp = _num(r.get("battery_kwh_net")), _num(r.get("wltp_range_km"))
        if net is None or wltp is None or net <= 0:
            continue
        ratio = wltp / net
        if ratio <= review_above:
            continue
        limit = withhold.get(str(r.get("body")), withhold.get("default", math.inf))
        action = WITHHOLD if ratio > limit else REVIEW
        detail = f"WLTP {wltp:g} km / {net:g} kWh = {ratio:.2f} km/kWh > {review_above:g}"
        if action == WITHHOLD:
            detail += f" (withheld above {limit:g} for body {r.get('body')})"
        out.append(Issue(r["variant_id"], "wltp_efficiency", "wltp_range_km", wltp, action, detail))
    return out


def dc_vs_peers(rows: list[dict[str, Any]], cfg: dict[str, Any]) -> list[Issue]:
    fld = str(cfg.get("field", "dc_km_per_20min"))
    max_ratio, min_peers = float(cfg["max_ratio"]), int(cfg["min_peers"])
    by_pack: dict[tuple[str, str], list[float]] = defaultdict(list)
    by_gen: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        v = _num(r.get(fld))
        if v is None:
            continue
        by_gen[str(r.get("generation_id"))].append(v)
        if r.get("battery_pack_id"):
            by_pack[(str(r.get("generation_id")), str(r["battery_pack_id"]))].append(v)
    out = []
    for r in rows:
        v = _num(r.get(fld))
        if v is None:
            continue
        gid = str(r.get("generation_id"))
        pid = r.get("battery_pack_id")
        pack = by_pack.get((gid, str(pid))) if pid else None
        for peers, scope, action in ((pack, "generation + pack", WITHHOLD),
                                     (by_gen.get(gid), "generation", REVIEW)):  # fmt: skip
            if not peers or len(peers) < min_peers:
                continue
            med = statistics.median(peers)
            if med > 0 and v > max_ratio * med:
                detail = (
                    f"{fld} {v:g} = {v / med:.2f}x the {scope} median {med:g}"
                    f" ({len(peers)} variants) > {max_ratio:g}x"
                )
                out.append(Issue(r["variant_id"], "dc_vs_peers", fld, v, action, detail))
                break  # the stricter peer group decides; one issue per row
    return out


def _pack_key(r: dict[str, Any]) -> str | None:
    if r.get("battery_pack_id"):
        return f"pack:{r['battery_pack_id']}"
    net = _num(r.get("battery_kwh_net"))
    return f"kwh:{net:g}" if net is not None else None


def copied_across_generations(rows: list[dict[str, Any]], cfg: dict[str, Any]) -> list[Issue]:
    fields = [str(f) for f in cfg["fields"]]
    need = int(cfg["min_equal_fields"])
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_model[str(r.get("model_id"))].append(r)
    out = []
    for vs in by_model.values():
        for i, a in enumerate(vs):
            for b in vs[i + 1 :]:
                if a.get("generation_id") == b.get("generation_id"):
                    continue
                ka, kb = _pack_key(a), _pack_key(b)
                if ka is None or kb is None or ka == kb:
                    continue
                same = [
                    f
                    for f in fields
                    if _num(a.get(f)) is not None
                    and a.get(f) == b.get(f)
                    and not _derived(a, f)
                    and not _derived(b, f)
                ]
                if len(same) < need:
                    continue
                for x, y in ((a, b), (b, a)):
                    detail = (
                        f"{', '.join(same)} equal to {y['variant_id']} (other generation,"
                        f" other pack: {_pack_key(x)} vs {_pack_key(y)})"
                    )
                    out.append(
                        Issue(
                            x["variant_id"],
                            "copied_across_generations",
                            same[0],
                            float(x[same[0]]),
                            str(cfg.get("action", REVIEW)),
                            detail,
                        )
                    )
    return out


RULES = {
    "wltp_efficiency": wltp_efficiency,
    "dc_vs_peers": dc_vs_peers,
    "copied_across_generations": copied_across_generations,
}


def find_issues(rows: list[dict[str, Any]], cfg: dict[str, Any]) -> list[Issue]:
    out: list[Issue] = []
    for name, rule in RULES.items():
        rc = (cfg.get("rules") or {}).get(name)
        if rc and rc.get("enabled", True):
            out += rule(rows, rc)
    return sorted(out, key=lambda i: (i.variant_id, i.rule, i.field))


# --- withholding ---------------------------------------------------------------------------


def dependent_fields(row: dict[str, Any], fld: str, cfg: dict[str, Any]) -> list[str]:
    """Fields to take out with `fld`: derived values computed from its facts (only when `fld`
    is a primary value: a derived one shares inputs with unrelated fields), plus the
    config's `withhold_with` list for `fld`."""
    prov = row.get("provenance") or {}
    out = [str(f) for f in ((cfg.get("withhold_with") or {}).get(fld) or [])]
    own = set((prov.get(fld) or {}).get("fact_ids") or [])
    if own and not _derived(row, fld):
        for f, p in prov.items():
            if f != fld and p.get("derived") and own & set(p.get("fact_ids") or []):
                out.append(f)
    return sorted({f for f in out if f != fld and row.get(f) is not None})


def withhold(
    rows: list[dict[str, Any]], issues: list[Issue], cfg: dict[str, Any]
) -> list[dict[str, Any]]:
    """Take withheld values out of `rows` (in place); review rows for data/review/conflicts.csv
    (build.CONFLICT_COLUMNS), one per value taken out."""
    by_id = {r["variant_id"]: r for r in rows}
    review: list[dict[str, Any]] = []
    for iss in issues:
        if iss.action != WITHHOLD:
            continue
        row = by_id.get(iss.variant_id)
        if row is None or row.get(iss.field) is None:
            continue  # already taken out by an earlier issue
        prov = row.setdefault("provenance", {})
        for f in [iss.field, *dependent_fields(row, iss.field, cfg)]:
            p = prov.pop(f, None) or {}
            why = f"{REASON_PREFIX} {iss.rule}: {iss.detail}"
            if f != iss.field:
                why += f" (derived from {iss.field})"
            review.append(
                {
                    "variant_id": iss.variant_id,
                    "field": f,
                    "source_id": ",".join(p.get("source_ids") or []),
                    "value": row.get(f),
                    "unit": "",
                    "winning_value": None,
                    "tolerance": why,
                    "fact_id": ",".join(p.get("fact_ids") or []),
                }
            )
            row[f] = None
            for c in COMPANIONS.get(f, ()):
                row[c] = None
    return review


@dataclass
class GateResult:
    config_loaded: bool
    issues: list[Issue]
    review_rows: list[dict[str, Any]]

    @property
    def range_withheld(self) -> set[str]:
        """Variants with a RANGE_BASIS value withheld: build no range estimate on them."""
        return {str(r["variant_id"]) for r in self.review_rows if r["field"] in RANGE_BASIS}

    def log(self) -> dict[str, Any]:
        return {
            "config_loaded": self.config_loaded,
            "issues": len(self.issues),
            "withheld_values": len(self.review_rows),
            "range_estimates_withheld": sorted(self.range_withheld),
        }


def apply_gate(rows: list[dict[str, Any]], cfg: dict[str, Any] | None) -> GateResult:
    """Build step: find issues on the merged rows and withhold what the config says."""
    if cfg is None:
        return GateResult(False, [], [])
    issues = find_issues(rows, cfg)
    return GateResult(True, issues, withhold(rows, issues, cfg))


# --- qa.json check -------------------------------------------------------------------------


def check_plausibility(
    rows: list[dict[str, Any]],
    cfg: dict[str, Any] | None,
    withheld: list[dict[str, Any]] | None = None,
) -> Any:
    """qa.json `plausibility` (report, not blocking): issues still in the published rows
    (review) plus the values the build step withheld (`withheld`, Issue dicts)."""
    from ev_pipeline.qa.checks import MAX_LISTED, Check

    if cfg is None:
        return Check(
            "plausibility",
            "Plausibility gate (A-35 B4)",
            False,
            "skipped",
            "no qa_plausibility.yaml: thresholds not configured",
            {"config": None},
        )
    left = [i.to_dict() for i in find_issues(rows, cfg)]
    held = list(withheld or [])
    by_rule: dict[str, int] = defaultdict(int)
    for i in left + held:
        by_rule[f"{i['rule']} {i['action']}"] += 1
    return Check(
        "plausibility",
        "Plausibility gate (A-35 B4)",
        False,
        "flag" if left or held else "pass",
        f"{len(held)} issue(s) withheld from the rows (in conflicts.csv), {len(left)} to review",
        {
            "config": CONFIG_FILE.name,
            "by_rule": dict(sorted(by_rule.items())),
            "withheld_count": len(held),
            "withheld": held[:MAX_LISTED],
            "review_count": len(left),
            "review": left[:MAX_LISTED],
        },
    )
