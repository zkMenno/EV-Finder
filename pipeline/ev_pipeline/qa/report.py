"""Run the release QA checks and render qa.json / qa.md."""

from __future__ import annotations

from typing import Any

from ev_pipeline.merge.policy import Policies
from ev_pipeline.qa.checks import (
    Check,
    check_diff,
    check_licence_gate,
    check_outliers,
    check_provenance,
    check_sections,
    check_top40_coverage,
)
from ev_pipeline.qa.plausibility import check_plausibility
from ev_pipeline.release.gate import Registry


def run_qa(
    catalogue: dict[str, Any],
    facts: list[dict[str, Any]],
    registry: Registry,
    policies: Policies,
    previous: dict[str, Any] | None = None,
    charging: dict[str, Any] | None = None,
    plausibility_cfg: dict[str, Any] | None = None,
    plausibility_withheld: list[dict[str, Any]] | None = None,
) -> list[Check]:
    return [
        check_provenance(catalogue, facts),
        check_licence_gate(catalogue, facts, registry, charging),
        check_diff(previous, catalogue, policies),
        check_outliers(catalogue, previous, facts),
        check_top40_coverage(catalogue),
        check_sections(catalogue, charging),
        check_plausibility(catalogue.get("rows", []), plausibility_cfg, plausibility_withheld),
    ]


def overall_status(checks: list[Check]) -> str:
    if any(c.blocking and c.status == "fail" for c in checks):
        return "fail"
    if any(c.status == "flag" for c in checks):
        return "review"
    return "pass"


def qa_document(
    catalogue: dict[str, Any],
    checks: list[Check],
    backtest: dict[str, Any],
    open_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    doc: dict[str, Any] = {
        "release": catalogue.get("release"),
        "generated_at": catalogue.get("generated_at"),
        "status": overall_status(checks),
        "blocking_failures": [c.id for c in checks if c.blocking and c.status == "fail"],
        "checks": {c.id: c.to_dict() for c in checks},
        "backtest": backtest,
    }
    if open_data is not None:
        doc["open_data"] = open_data
    return doc


def qa_md(doc: dict[str, Any]) -> str:
    lines = [
        f"# Release QA, release {doc['release']}",
        "",
        f"Overall: **{doc['status']}** (fail = blocked; review = published, items to check)."
        " Details in qa.json.",
        "",
        "| Check | Blocking | Status | Summary |",
        "|---|---|---|---|",
    ]
    for c in doc["checks"].values():
        lines.append(
            f"| {c['title']} | {'yes' if c['blocking'] else 'no'} | {c['status']} |"
            f" {c['summary']} |"
        )
    bt = doc.get("backtest") or {}
    summary = (
        f"median abs error {bt['median_abs_pct']}% over {bt['scored']} tests"
        if "median_abs_pct" in bt
        else bt.get("note", "")
    )
    lines.append(f"| Back-test (real range) | no | {bt.get('status', 'skipped')} | {summary} |")
    for cid in ("provenance", "licence_gate"):
        errs = doc["checks"][cid]["details"].get("errors") or []
        if errs:
            lines += ["", f"## {doc['checks'][cid]['title']}: first problems", ""]
            lines += [f"- {e}" for e in errs[:10]]
    out = doc["checks"]["outliers"]["details"]
    if out.get("impossible"):
        lines += ["", "## Impossible values (first 10)", ""]
        lines += [f"- {i['variant_id']}: {i['detail']}" for i in out["impossible"][:10]]
    pl = (doc["checks"].get("plausibility") or {}).get("details") or {}
    if pl.get("withheld") or pl.get("review"):
        lines += ["", "## Plausibility (first 10 each)", ""]
        for kind in ("withheld", "review"):
            lines += [f"- {kind}: {i['variant_id']}: {i['detail']}" for i in pl.get(kind, [])[:10]]
    flags = doc["checks"]["diff"]["details"].get("flags") or []
    if flags:
        lines += ["", "## Diff flags", "", *[f"- {f}" for f in flags]]
    return "\n".join(lines) + "\n"
