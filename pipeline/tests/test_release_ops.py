"""Addendum 6 P2: atomic `latest`, QA gate on `latest`, rollback, diff. Offline."""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from ev_pipeline.cli import main
from ev_pipeline.commands.releases import (
    ReleaseOpError,
    diff_summary,
    diff_text,
    list_releases,
    rollback,
)
from ev_pipeline.release.build import release_cmd, write_latest

FIX = Path(__file__).parent / "fixtures" / "release"
NOW = datetime(2026, 11, 15, 1, 0, tzinfo=UTC)


@pytest.fixture
def data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    d = tmp_path / "data"
    (d / "seed").mkdir(parents=True)
    shutil.copytree(FIX / "staging", d / "staging")
    shutil.copytree(FIX / "taxonomy", d / "taxonomy")
    for n in ("models", "variants", "platforms", "battery_packs", "variant_links"):
        shutil.copy(FIX / f"{n}.yaml", d / "seed" / f"{n}.yaml")
    for n in ("sources", "field_sources"):
        shutil.copy(FIX / f"{n}.yaml", d / f"{n}.yaml")
    monkeypatch.setenv("EV_DATA_DIR", str(d))
    monkeypatch.delenv("EV_RUNS_DIR", raising=False)
    return d


def _latest(d: Path) -> str:
    return (d / "releases" / "latest").read_text()


def _two_releases(d: Path) -> None:
    assert release_cmd(False, data_dir=d, now=NOW) == 0
    # Drop one staging source so release 2 differs from release 1.
    (d / "staging" / "eea.records.jsonl").unlink()
    assert release_cmd(False, data_dir=d, now=NOW) == 0


def test_write_latest_is_atomic_and_leaves_no_temp(tmp_path: Path) -> None:
    write_latest(tmp_path, 3)
    assert (tmp_path / "latest").read_text() == "3\n"
    write_latest(tmp_path, 4)
    assert (tmp_path / "latest").read_text() == "4\n"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["latest"]


def test_release_writes_no_temp_files(data_dir: Path) -> None:
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 0
    names = sorted(p.name for p in (data_dir / "releases").iterdir())
    assert names == ["1", "latest"]
    assert _latest(data_dir) == "1\n"


def test_blocking_qa_failure_does_not_move_latest(
    data_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 0
    import ev_pipeline.qa.release_step as step

    real = step.qa_document

    def failing(*args: Any, **kw: Any) -> dict[str, Any]:
        doc = real(*args, **kw)
        doc["status"] = "fail"
        doc["blocking_failures"] = ["provenance"]
        return doc

    monkeypatch.setattr(step, "qa_document", failing)
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 1
    assert _latest(data_dir) == "1\n"
    assert not (data_dir / "releases" / "2").exists()
    assert not list((data_dir / "releases").glob(".tmp-*"))
    assert (data_dir / "review" / "qa.md").exists()


def test_rollback_and_refusals(data_dir: Path) -> None:
    _two_releases(data_dir)
    assert _latest(data_dir) == "2\n"
    entry = rollback(data_dir, 1)
    assert entry["from"] == 2 and entry["to"] == 1 and _latest(data_dir) == "1\n"
    log = (data_dir / "runs" / "releases.jsonl").read_text().splitlines()
    assert json.loads(log[-1])["to"] == 1
    with pytest.raises(ReleaseOpError, match="does not exist"):
        rollback(data_dir, 9)
    (data_dir / "releases" / "2" / "qa.json").write_text('{"status": "fail"}')
    with pytest.raises(ReleaseOpError, match="QA status"):
        rollback(data_dir, 2)
    (data_dir / "releases" / "2" / "qa.json").unlink()
    with pytest.raises(ReleaseOpError, match="missing"):
        rollback(data_dir, 2)
    assert _latest(data_dir) == "1\n"
    # The next release still counts up from the highest folder.
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 0
    assert _latest(data_dir) == "3\n"


def test_diff_summary_and_text(data_dir: Path) -> None:
    _two_releases(data_dir)
    a = json.loads((data_dir / "releases" / "1" / "catalogue.json").read_text())
    b = json.loads((data_dir / "releases" / "2" / "catalogue.json").read_text())
    s = diff_summary(a, b)
    assert s["from"] == 1 and s["to"] == 2
    assert s["counts"]["changed"] > 0 and s["changed_fields"]
    assert "eea" in s["sources_removed"]
    text = diff_text(s)
    assert text.startswith("Release 1 -> 2") and "changed fields" in text
    same = diff_summary(a, a)
    assert same["counts"]["changed"] == 0 and same["counts"]["added"] == 0


def test_cli_release_subcommands(data_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _two_releases(data_dir)
    capsys.readouterr()
    assert main(["release", "diff", "1", "latest"]) == 0
    assert "Release 1 -> 2" in capsys.readouterr().out
    assert main(["release", "diff", "1", "2", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["counts"]["rows"] >= 1
    assert main(["release", "diff", "1", "7"]) == 1
    assert main(["release", "rollback", "--to", "1"]) == 0
    assert "latest: 2 -> 1" in capsys.readouterr().out
    assert main(["release", "list", "--json"]) == 0
    rows = json.loads(capsys.readouterr().out)
    assert [r["release"] for r in rows] == [1, 2] and rows[0]["latest"] and rows[0]["qa"] != "fail"
    assert main(["release", "list"]) == 0
    assert main(["release", "rollback", "--to", "5"]) == 1
    assert list_releases(data_dir)[1]["rows"] >= 1


def test_plain_release_still_works_with_subcommands(data_dir: Path) -> None:
    assert main(["release", "--dry-run"]) == 0
    assert not (data_dir / "releases").exists()
    assert main(["release"]) == 0
    assert (data_dir / "releases" / "1" / "sources.json").exists()
