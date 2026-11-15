"""T-025: manual charging figures (data/manual/charging/*.yaml) and the release diff rules."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any

import yaml

from ev_pipeline.release.charging_stats import (
    CHANGE_LIMIT,
    MANUAL_FORMAT,
    build_charging_stats,
    charging_review_rows,
)
from ev_pipeline.release.gate import parse_registry

TAXONOMY = {
    "charging_metrics": [{"id": "public-points"}],
    "charging_definitions": [
        {"id": "de-bnetza-ladepunkt", "source_id": "bnetza-ladesaeulenregister"},
        {"id": "be-eafo-point", "source_id": "eafo"},
    ],
    "power_bands": [{"id": "dc-150-349"}],
}


def _registry(eafo_status: str = "active_pending_confirmation"):
    return parse_registry(
        {
            "sources": [
                {"id": "bnetza", "licence": "CC-BY-4.0", "status": "active",
                 "aliases": ["bnetza-ladesaeulenregister"]},
                {"id": "eafo", "licence": "CC-BY-4.0", "status": eafo_status},
                {"id": "maker-docs", "licence": "none", "status": "blocked"},
            ]
        }
    )  # fmt: skip


def _stat(period: str, value: float, **kw: Any) -> dict[str, Any]:
    return {
        "id": f"bnetza:de:{period}:{kw.get('power_band_id')}",
        "country": "DE",
        "region": None,
        "period_end": period,
        "metric_id": "public-points",
        "power_band_id": None,
        "value": value,
        "unit": "count",
        "source_id": "bnetza-ladesaeulenregister",
        "definition_id": "de-bnetza-ladepunkt",
        "confidence": "high",
        "entered_by": "pipeline",
        "retrieved_at": "2026-11-15",
        **kw,
    }


def _stage(staging: Path, rows: list[dict[str, Any]]) -> None:
    staging.mkdir(parents=True, exist_ok=True)
    (staging / "bnetza.charging_stats.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8"
    )
    (staging / "bnetza.charging_stats.meta.json").write_text(
        json.dumps({"source": "bnetza", "releasable": True, "licence": "CC-BY-4.0"}),
        encoding="utf-8",
    )


def _manual(d: Path, name: str, doc: dict[str, Any]) -> None:
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.yaml").write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")


BE_ROW = {
    "country": "BE",
    "period_end": "2026-09-30",
    "metric_id": "public-points",
    "value": 91000,
    "unit": "count",
    "definition_id": "be-eafo-point",
    "confidence": "medium",
    "retrieved_at": "2026-11-15",
    "source_url": "https://alternative-fuels-observatory.ec.europa.eu/x",
}


# --- manual YAML -------------------------------------------------------------------------


def test_manual_rows_ship_as_staff_with_source_url(tmp_path: Path) -> None:
    man = tmp_path / "manual"
    _manual(man, "eafo-be", {"schema": MANUAL_FORMAT, "source_id": "eafo", "stats": [BE_ROW]})
    res = build_charging_stats(tmp_path / "none", _registry(), TAXONOMY, 2, "t", manual_dir=man)
    assert res.document is not None
    (row,) = res.document["stats"]
    assert row["entered_by"] == "staff" and row["source_id"] == "eafo"
    assert row["id"] == "manual:BE:-:public-points:-:2026-09-30"
    assert res.log["files"]["manual-eafo-be"]["shipped"] == 1


def test_manual_rows_without_source_url_are_dropped(tmp_path: Path) -> None:
    man = tmp_path / "manual"
    bad = {k: v for k, v in BE_ROW.items() if k != "source_url"}
    _manual(man, "x", {"schema": MANUAL_FORMAT, "source_id": "eafo", "stats": [bad, BE_ROW]})
    res = build_charging_stats(tmp_path / "none", _registry(), TAXONOMY, 2, "t", manual_dir=man)
    info = res.log["files"]["manual-x"]
    assert info["shipped"] == 1 and info["dropped"] == {"manual row without source_url": 1}


def test_manual_file_of_a_blocked_source_is_gated(tmp_path: Path) -> None:
    man = tmp_path / "manual"
    _manual(man, "x", {"schema": MANUAL_FORMAT, "source_id": "eafo", "stats": [BE_ROW]})
    res = build_charging_stats(
        tmp_path / "none", _registry("blocked"), TAXONOMY, 2, "t", manual_dir=man
    )
    assert res.document is None and res.log["files"]["manual-x"]["gated"] == "status blocked"


def test_manual_file_needs_the_schema_line(tmp_path: Path) -> None:
    man = tmp_path / "manual"
    _manual(man, "x", {"source_id": "eafo", "stats": [BE_ROW]})
    res = build_charging_stats(tmp_path / "none", _registry(), TAXONOMY, 2, "t", manual_dir=man)
    assert res.document is None
    assert "schema must be" in next(iter(res.log["files"]["manual-x"]["dropped"]))


def test_download_wins_over_a_manual_copy_of_the_same_figure(tmp_path: Path) -> None:
    st = tmp_path / "staging"
    _stage(st, [_stat("2026-09-30", 100)])
    man = tmp_path / "manual"
    dup = {**BE_ROW, "country": "DE", "definition_id": "de-bnetza-ladepunkt", "value": 999,
           "source_id": "bnetza-ladesaeulenregister"}  # fmt: skip
    _manual(man, "de", {"schema": MANUAL_FORMAT, "source_id": "bnetza", "stats": [dup]})
    res = build_charging_stats(st, _registry(), TAXONOMY, 2, "t", manual_dir=man)
    assert res.document is not None
    assert [r["value"] for r in res.document["stats"]] == [100]
    assert res.log["files"]["manual-de"]["dropped"] == {
        "repeats a figure already loaded (downloads win over manual)": 1
    }


def test_repo_manual_example_is_valid(tmp_path: Path) -> None:
    """The documented format (fixture handed to WS3) loads without problems."""
    example = Path(__file__).parent / "fixtures" / "manual" / "charging" / "example.yaml"
    man = tmp_path / "manual"
    man.mkdir()
    shutil.copy(example, man / "example.yaml")
    res = build_charging_stats(tmp_path / "none", _registry(), TAXONOMY, 2, "t", manual_dir=man)
    info = res.log["files"]["manual-example"]
    assert info.get("dropped", {}) == {} and info["shipped"] >= 1, info


# --- release diff ------------------------------------------------------------------------


def _doc(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {"stats": rows}


def test_first_release_checks_every_step_once() -> None:
    rows = [_stat("2026-06-30", 100), _stat("2026-07-31", 110), _stat("2026-08-31", 140),
            _stat("2026-09-30", 130)]  # fmt: skip
    out = charging_review_rows(None, _doc(rows))
    assert [(r["period_end"], r["reason"]) for r in out] == [
        ("2026-08-31", f"rose more than {CHANGE_LIMIT:.0%} a month since the previous date"),
        ("2026-09-30", "fell since the previous date"),
    ]
    assert out[0]["change_pct"] == "+27.3" and out[0]["previous_value"] == "110"


def test_exactly_15_percent_is_not_flagged() -> None:
    out = charging_review_rows(None, _doc([_stat("2026-06-30", 100), _stat("2026-07-31", 115)]))
    assert out == []


def test_later_release_checks_only_new_dates_and_revisions() -> None:
    prev = _doc([_stat("2026-06-30", 100), _stat("2026-07-31", 200)])  # old jump: not re-flagged
    cur = _doc([_stat("2026-06-30", 100), _stat("2026-07-31", 205), _stat("2026-08-31", 300)])
    reasons = {(r["period_end"], r["reason"]) for r in charging_review_rows(prev, cur)}
    assert reasons == {
        ("2026-07-31", "revised since the previous release"),
        ("2026-08-31", f"rose more than {CHANGE_LIMIT:.0%} a month since the previous date"),
    }


def test_series_or_date_missing_now_is_flagged() -> None:
    prev = _doc([_stat("2026-06-30", 100), _stat("2026-07-31", 101, power_band_id="dc-150-349")])
    cur = _doc([_stat("2026-06-30", 100)])
    (row,) = charging_review_rows(prev, cur)
    assert row["reason"] == "in the previous release, missing now"
    assert row["power_band_id"] == "dc-150-349"


def test_new_series_in_a_later_release_starts_quietly() -> None:
    prev = _doc([_stat("2026-06-30", 100)])
    cur = _doc([_stat("2026-06-30", 100), _stat("2026-06-30", 5, power_band_id="dc-150-349")])
    assert charging_review_rows(prev, cur) == []


def test_review_row_keys_are_stable() -> None:
    a = charging_review_rows(None, _doc([_stat("2026-06-30", 100), _stat("2026-07-31", 90)]))
    b = charging_review_rows(None, _doc([_stat("2026-06-30", 100), _stat("2026-07-31", 80)]))
    assert a[0]["record_key"] == b[0]["record_key"] and a[0]["reason"] == b[0]["reason"]


def test_review_csv_columns(tmp_path: Path) -> None:
    from ev_pipeline.release.build import write_csv
    from ev_pipeline.release.charging_stats import REVIEW_COLUMNS

    rows = charging_review_rows(None, _doc([_stat("2026-06-30", 100), _stat("2026-07-31", 90)]))
    write_csv(tmp_path / "c.csv", REVIEW_COLUMNS, rows)
    with (tmp_path / "c.csv").open() as fh:
        got = list(csv.DictReader(fh))
    assert got[0]["reason"] == "fell since the previous date" and got[0]["source_id"]


# --- ev refresh wiring -------------------------------------------------------------------


def test_refresh_looks_for_each_adapters_own_staging_file(tmp_path: Path) -> None:
    from ev_pipeline.refresh.plan import _due, find_adapter, staging_file

    for sid in ("eafo", "bnetza", "dft-charging"):
        mod = find_adapter(sid)
        assert staging_file(tmp_path, sid, mod).name == f"{sid}.charging_stats.jsonl"
    assert staging_file(tmp_path, "rdw-defects", find_adapter("rdw-defects")).name == (
        "rdw-defects.defects.jsonl"
    )
    assert staging_file(tmp_path, "rdw", find_adapter("rdw")).name == "rdw.records.jsonl"
    mod = find_adapter("bnetza")
    assert _due("bnetza", "monthly", {}, None, tmp_path, mod) == ("run", "no staging file")  # type: ignore[arg-type]
    (tmp_path / "staging").mkdir()
    staging_file(tmp_path, "bnetza", mod).write_text("{}\n")
    assert _due("bnetza", "monthly", {}, None, tmp_path, mod) == ("run", "never checked")  # type: ignore[arg-type]


def test_eafo_is_planned_now_that_it_is_pending_confirmation(tmp_path: Path) -> None:
    from datetime import UTC, datetime

    from ev_pipeline.refresh.plan import plan

    shutil.copy(Path(__file__).resolve().parents[2] / "data" / "sources.yaml", tmp_path)
    got = {p.id: p.action for p in plan(tmp_path, {}, datetime(2026, 11, 16, 1, tzinfo=UTC))}
    assert got.get("eafo") == "run" and got.get("bnetza") == "run"


def test_yearly_series_are_held_to_a_monthly_rate() -> None:
    from ev_pipeline.release.charging_stats import monthly_rate

    # +45 % in a year is ~3 % a month: fine. +45 % in a month: flagged.
    assert monthly_rate(100, 145, "2021-12-31", "2022-12-31") < CHANGE_LIMIT
    yearly = _doc([_stat("2021-12-31", 100), _stat("2022-12-31", 145)])
    monthly = _doc([_stat("2022-11-30", 100), _stat("2022-12-31", 145)])
    assert charging_review_rows(None, yearly) == []
    assert len(charging_review_rows(None, monthly)) == 1
    assert abs(monthly_rate(100, 120, "2026-01-01", "2026-01-10") - 0.2) < 1e-9
