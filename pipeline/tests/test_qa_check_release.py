"""T-057 `python -m ev_pipeline.qa check-release`: blocking QA re-run on a committed release.

Builds a release folder in tmp_path from the SYNTHETIC QA fixture (fixtures/qa/), the same
way release.build writes it (catalogue.json + facts.parquet). No network.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from ev_pipeline.qa.__main__ import main
from ev_pipeline.qa.check_release import (
    ReleaseInputError,
    check_release,
    fact_from_parquet,
    resolve_release_dir,
)
from ev_pipeline.release.build import _flat_facts, _write_parquet

QA = Path(__file__).parent / "fixtures" / "qa"
REPO_RELEASES = Path(__file__).resolve().parents[2] / "data" / "releases"


def _write_release(
    data: Path, cat: dict[str, Any], facts: list[dict[str, Any]], n: int = 1
) -> Path:
    d = data / "releases" / str(n)
    d.mkdir(parents=True)
    (d / "catalogue.json").write_text(json.dumps(cat), encoding="utf-8")
    _write_parquet(d / "facts.parquet", _flat_facts(facts, [None] * len(facts)))
    (data / "releases" / "latest").write_text(f"{n}\n", encoding="utf-8")
    return d


@pytest.fixture
def data(tmp_path: Path) -> Path:
    d = tmp_path / "data"
    d.mkdir()
    shutil.copy(QA / "sources.yaml", d / "sources.yaml")
    return d


@pytest.fixture
def cat() -> dict[str, Any]:
    return json.loads((QA / "catalogue.json").read_text())


@pytest.fixture
def facts() -> list[dict[str, Any]]:
    return json.loads((QA / "facts.json").read_text())


def test_fixture_release_passes_via_latest_pointer(data, cat, facts) -> None:
    _write_release(data, cat, facts)
    report = check_release(data / "releases" / "latest", data)
    assert report["status"] == "pass" and report["blocking_failures"] == []
    assert set(report["checks"]) == {"provenance", "licence_gate", "images", "release_diff"}
    assert main(["check-release", str(data / "releases" / "latest")]) == 0


def test_parquet_round_trip_matches_fact_dicts(facts) -> None:
    flat = _flat_facts(facts, [None] * len(facts))
    back = [fact_from_parquet(r) for r in flat]
    for orig, got in zip(facts, back, strict=True):
        assert got["id"] == orig["id"] and got["source"] == orig["source"]
        assert got["value"] == orig["value"] and got["confidence"] == orig["confidence"]


def test_odbl_source_fails_licence_gate(data, cat, facts, capsys) -> None:
    row = cat["rows"][0]
    key = next(iter(row["provenance"]))
    row["provenance"][key]["source_ids"].append("testosm")
    cat["sources"].append({"id": "testosm", "name": "ODbL", "licence": "ODbL-1.0"})
    rel = _write_release(data, cat, facts)
    assert main(["check-release", str(rel), "--data-dir", str(data)]) == 1
    assert "licence_gate: fail" in capsys.readouterr().out


def test_value_without_provenance_fails(data, cat, facts, capsys) -> None:
    row = cat["rows"][0]
    row["provenance"].pop(next(k for k in row["provenance"] if row.get(k) is not None))
    rel = _write_release(data, cat, facts)
    assert main(["check-release", str(rel), "--json"]) == 1
    out = json.loads(capsys.readouterr().out)
    assert out["blocking_failures"] == ["provenance"]


def test_fact_missing_licence_fails(data, cat, facts) -> None:
    facts[0]["source"]["licence"] = ""
    rel = _write_release(data, cat, facts)
    report = check_release(rel, data)
    assert report["status"] == "fail" and "provenance" in report["blocking_failures"]


def test_impossible_values_are_reported_not_blocking(data, cat, facts, capsys) -> None:
    cat["rows"][0]["battery_kwh_net"] = 60.0  # pack testpack-55: 55 kWh gross
    rel = _write_release(data, cat, facts)
    report = check_release(rel, data)
    assert report["status"] == "pass"  # outliers never block
    assert [i["rule"] for i in report["impossible_values"]] == ["usable_gt_gross"]
    assert main(["check-release", str(rel)]) == 0
    assert "usable 60.0 > gross 55.0 kWh" in capsys.readouterr().out


@pytest.mark.parametrize(
    "setup",
    ["missing_dir", "bad_pointer", "missing_facts", "no_registry", "broken_json"],
)
def test_bad_input_exits_2(tmp_path: Path, data, cat, facts, setup: str) -> None:
    rel = data / "releases" / "1"
    target: Path = rel
    if setup == "missing_dir":
        target = data / "releases" / "9"
    elif setup == "bad_pointer":
        (data / "releases").mkdir()
        target = data / "releases" / "latest"
        target.write_text("abc")
    else:
        rel = _write_release(data, cat, facts)
        if setup == "missing_facts":
            (rel / "facts.parquet").unlink()
        elif setup == "no_registry":
            (data / "sources.yaml").unlink()
        elif setup == "broken_json":
            (rel / "catalogue.json").write_text("{not json")
    assert main(["check-release", str(target), "--data-dir", str(data)]) == 2


def test_resolve_release_dir_rejects_missing_folder(tmp_path: Path) -> None:
    with pytest.raises(ReleaseInputError):
        resolve_release_dir(tmp_path / "nope")


def test_committed_release_passes_blocking_qa() -> None:
    """The real release in the repo (what the CI data-qa job checks)."""
    latest = REPO_RELEASES / "latest"
    if not latest.exists():
        pytest.skip("no committed release")
    report = check_release(latest, REPO_RELEASES.parent)
    assert report["status"] == "pass", report["blocking_failures"]
