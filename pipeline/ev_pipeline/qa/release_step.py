"""The end-of-release step, called from release/build.py `write_release` before the release
folder is renamed into place: QA checks + back-test -> qa.json / qa.md, then the open data
bundle -> open/. A blocking QA failure raises ReleaseError, so the release is not published
(the temporary folder is removed and `latest` is not moved). qa.json and qa.md are also
written to data/review/ so a failed run can be inspected.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import yaml

from ev_pipeline.backtest.harness import release_backtest
from ev_pipeline.merge.policy import load_policies
from ev_pipeline.opendata.bundle import write_open_bundle
from ev_pipeline.qa.report import qa_document, qa_md, run_qa
from ev_pipeline.qa.top40 import top40_section
from ev_pipeline.release.gate import load_registry
from ev_pipeline.release.validate import ReleaseError


def _previous(data_dir: Path, n: int) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    releases = data_dir / "releases"
    nums = sorted(
        int(p.name)
        for p in (releases.iterdir() if releases.is_dir() else [])
        if p.is_dir() and p.name.isdigit() and int(p.name) < n
    )
    if not nums:
        return None, None
    d = releases / str(nums[-1])
    cat = json.loads((d / "catalogue.json").read_text(encoding="utf-8"))
    qa = d / "qa.json"
    prev_bt = json.loads(qa.read_text(encoding="utf-8")).get("backtest") if qa.exists() else None
    return cat, prev_bt


def _previous_qa_section(data_dir: Path, n: int, key: str) -> dict[str, Any] | None:
    releases = data_dir / "releases"
    nums = sorted(
        int(p.name)
        for p in (releases.iterdir() if releases.is_dir() else [])
        if p.is_dir() and p.name.isdigit() and int(p.name) < n
    )
    qa = releases / str(nums[-1]) / "qa.json" if nums else None
    if qa is None or not qa.exists():
        return None
    return json.loads(qa.read_text(encoding="utf-8")).get(key)


def registration_order(data_dir: Path) -> tuple[str, ...]:
    path = data_dir / "field_sources.yaml"
    if not path.exists():
        return ()
    spec = ((yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("fields") or {}).get(
        "registered_count"
    ) or {}
    return tuple(spec.get("primary") or []) + tuple(spec.get("fallbacks") or [])


def finish_release(
    catalogue: dict[str, Any],
    facts: list[dict[str, Any]],
    out_dir: Path,
    data_dir: Path,
    plausibility_withheld: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    registry = load_registry(data_dir / "sources.yaml")
    policies = load_policies(data_dir / "field_sources.yaml")
    prev, prev_bt = _previous(data_dir, int(catalogue["release"]))
    cs_path = out_dir / "charging_stats.json"  # T-059, written by write_release
    charging = json.loads(cs_path.read_text(encoding="utf-8")) if cs_path.exists() else None
    from ev_pipeline.qa.plausibility import load_config as load_plausibility

    checks = run_qa(
        catalogue, facts, registry, policies, prev, charging,
        load_plausibility(), plausibility_withheld,
    )  # fmt: skip
    backtest = release_backtest(data_dir, registry.releasable, prev_bt)
    doc = qa_document(catalogue, checks, backtest)
    doc["top40"] = top40_section(catalogue, data_dir)  # report only (ADDENDUM-6 P5)
    # T-035: proxy back-test on licence-clean EPA figures; report only, never blocks.
    from ev_pipeline.backtest.epa import epa_backtest

    doc["backtest_epa"] = epa_backtest(
        catalogue,
        facts,
        data_dir,
        registry.releasable,
        _previous_qa_section(data_dir, int(catalogue["release"]), "backtest_epa"),
    )
    # START §3 item 6: quality of the fields the usage profiles read; report only.
    from ev_pipeline.qa.profile_fields import profile_fields_section

    mx_path = out_dir / "consumption_matrix.json"  # T-033, written by write_release
    matrix = json.loads(mx_path.read_text(encoding="utf-8")) if mx_path.exists() else None
    doc["profile_fields"] = profile_fields_section(catalogue, matrix, doc["backtest_epa"])
    # T-081: used price back-test against manual samples; report only, never blocks.
    up_path = out_dir / "used_prices.json"
    if up_path.exists():
        doc["backtest_used_prices"] = json.loads(up_path.read_text(encoding="utf-8")).get(
            "backtest"
        )
    if doc["status"] == "fail":
        review = data_dir / "review"
        review.mkdir(parents=True, exist_ok=True)
        (review / "qa.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
        (review / "qa.md").write_text(_qa_md(doc), encoding="utf-8")
        shutil.rmtree(out_dir, ignore_errors=True)
        raise ReleaseError(
            "release QA failed (blocking): "
            + ", ".join(doc["blocking_failures"])
            + "; see data/review/qa.md"
        )
    doc["open_data"] = write_open_bundle(catalogue, registry, out_dir, registration_order(data_dir))
    (out_dir / "qa.json").write_text(
        json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (out_dir / "qa.md").write_text(_qa_md(doc), encoding="utf-8")
    return doc


def _qa_md(doc: dict[str, Any]) -> str:
    from ev_pipeline.qa.profile_fields import profile_fields_md

    extra = profile_fields_md(doc.get("profile_fields"))
    return qa_md(doc).rstrip("\n") + "\n" + "\n".join(extra) + "\n" if extra else qa_md(doc)
