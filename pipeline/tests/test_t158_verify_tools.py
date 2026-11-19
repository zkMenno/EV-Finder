"""T-158: `ev verify --keep` (G-53), `--base-release-from` (G-56), approved_changes checks
(G-54 / G-57), changed-rule globs, refresh-lock wording and the short-refresh stamp. No network."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from ev_pipeline.refresh import lock, runner
from ev_pipeline.release import approvals as ap
from ev_pipeline.verify import run as vr
from ev_pipeline.verify.run import report_md, verify
from tests.test_t127_verify import NOW, TRICKY, data_dir  # noqa: F401  (fixture)

REPO = Path(__file__).resolve().parents[2]


# --- G-53 --keep ------------------------------------------------------------------------


def test_keep_keeps_the_scratch_build(data_dir: Path, tmp_path: Path) -> None:  # noqa: F811
    keep = tmp_path / "kept"
    rep = verify(data_dir, repo=tmp_path, skip_tests=True, tricky=TRICKY, now=NOW, keep=keep)
    assert rep.status == "pass", rep.failures
    built = keep / "data" / "releases" / "2" / "catalogue.json"
    assert built.exists() and len(json.loads(built.read_text())["rows"]) == 7
    assert (keep / "data" / "staging").is_symlink()  # staging linked, not copied
    assert (keep / "data" / "review" / "release_diff.csv").exists()
    assert f"kept in `{keep}`" in report_md(rep)
    assert not (data_dir / "releases" / "2").exists()  # the checkout's data/ is untouched


def test_keep_refuses_a_non_empty_folder(data_dir: Path, tmp_path: Path) -> None:  # noqa: F811
    keep = tmp_path / "kept"
    keep.mkdir()
    (keep / "x").write_text("mine")
    rep = verify(data_dir, repo=tmp_path, skip_tests=True, tricky=TRICKY, now=NOW, keep=keep)
    assert rep.status == "fail" and "not an empty folder" in rep.failures[0]
    assert (keep / "x").read_text() == "mine"


# --- G-56 --base-release-from -----------------------------------------------------------


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


@pytest.fixture
def base_repo(data_dir: Path, tmp_path: Path) -> Path:  # noqa: F811
    """A git repo holding this checkout's pipeline code + config and the fixture's inputs."""
    r = tmp_path / "repo"
    shutil.copytree(REPO / "pipeline" / "ev_pipeline", r / "pipeline" / "ev_pipeline",
                    ignore=shutil.ignore_patterns("__pycache__"))  # fmt: skip
    shutil.copytree(REPO / "config", r / "config")
    shutil.copytree(REPO / "packages" / "schema", r / "packages" / "schema",
                    ignore=shutil.ignore_patterns("node_modules"))  # fmt: skip
    (r / "data").mkdir()  # iterdir order varies: a file may come before any folder
    for p in sorted(data_dir.iterdir(), key=lambda x: (x.is_dir(), x.name)):  # files first
        if p.name not in ("staging", "releases", "review", "runs"):
            (shutil.copytree if p.is_dir() else shutil.copy2)(p, r / "data" / p.name)
    (r / "data" / "releases").mkdir(exist_ok=True)
    shutil.copy2(REPO / "data" / "releases" / "publish.yaml", r / "data" / "releases")
    _git(r, "init", "-q")
    _git(r, "add", "-A")
    _git(r, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base")
    return r


def test_base_release_from_diffs_against_the_same_staging(
    data_dir: Path,  # noqa: F811
    base_repo: Path,
    tmp_path: Path,
) -> None:
    # A fresh staging moved under the committed release 1: plain verify blocks on it ...
    p = data_dir / "staging" / "openev.records.jsonl"
    p.write_text(p.read_text().replace('"value": 46.3', '"value": 48.0'))
    plain = verify(data_dir, repo=base_repo, skip_tests=True, tricky=TRICKY, now=NOW)
    assert plain.numbers["release_diff_blocking"] == 1
    # ... while the base ref built on that same staging shows only what the branch changes.
    rep = verify(data_dir, repo=base_repo, skip_tests=True, tricky=TRICKY, now=NOW,
                 base_release_from="HEAD", keep=tmp_path / "kept")  # fmt: skip
    assert rep.status == "pass", rep.failures
    assert rep.sections["base_build"]["status"] == "pass"
    assert rep.numbers["release_diff_blocking"] == 0
    assert rep.sections["rebuild"]["release"] == 2
    md = report_md(rep)
    assert "Base (G-56): HEAD @" in md and "not the committed release" in md
    # the base build ran the ref's own exported code, not this checkout's
    assert (tmp_path / "kept" / "base-src" / "pipeline" / "ev_pipeline").is_dir()
    exported = tmp_path / "kept" / "base-src" / "data" / "releases"
    assert [x.name for x in exported.iterdir()] == ["publish.yaml"]  # no release folders


def test_base_release_from_shows_a_branch_change(
    data_dir: Path,  # noqa: F811
    base_repo: Path,
) -> None:
    p = data_dir / "staging" / "openev.records.jsonl"
    p.write_text(p.read_text().replace('"value": 46.3', '"value": 48.0'))
    # the branch's own input differs from the base ref's: a seed variant renamed
    seed = data_dir / "seed" / "variants.yaml"
    doc = yaml.safe_load(seed.read_text())
    v = doc["variants"][0]
    v["name"] = str(v.get("name", v["id"])) + " (renamed)"
    seed.write_text(yaml.safe_dump(doc, sort_keys=False))
    rep = verify(data_dir, repo=base_repo, skip_tests=True, tricky=TRICKY, now=NOW,
                 base_release_from="HEAD")  # fmt: skip
    assert rep.sections["base_build"]["status"] == "pass"
    lines = rep.release_diff_csv or ""
    assert "(renamed)" in lines
    assert "46.3" not in lines  # the staging move is in the base build too: not this branch's


def test_base_release_from_a_bad_ref_fails_plainly(
    data_dir: Path,  # noqa: F811
    base_repo: Path,
) -> None:
    rep = verify(data_dir, repo=base_repo, skip_tests=True, tricky=TRICKY, now=NOW,
                 base_release_from="no-such-ref")  # fmt: skip
    assert rep.status == "fail"
    assert rep.sections["base_build"]["status"] == "fail"
    assert any("cannot export no-such-ref" in f for f in rep.failures)


# --- changed-rule globs (T-155 nit 6) ---------------------------------------------------


@pytest.mark.parametrize(
    "path",
    [
        "pipeline/ev_pipeline/qa/value_guard.py",
        "pipeline/ev_pipeline/backtest/popularity.py",
        "data/manual/specs/t151-van-leaf-ioniq5.yaml",
        "data/sources.yaml",
        "data/field_sources.yaml",
        "config/popularity.yaml",
        "pipeline/ev_pipeline/derive/shortlist_params.yaml",
    ],
)
def test_rule_globs_list_rule_files(path: str) -> None:
    import fnmatch

    assert any(fnmatch.fnmatchcase(path, g) for g in vr.RULE_GLOBS)


def test_rule_globs_skip_plain_code() -> None:
    import fnmatch

    for path in ("pipeline/ev_pipeline/qa/checks.py", "apps/web/src/app/page.tsx", "README.md"):
        assert not any(fnmatch.fnmatchcase(path, g) for g in vr.RULE_GLOBS)


# --- refresh-lock nits (T-153 follow-up 5) ----------------------------------------------


def test_refused_refresh_uses_its_own_words(tmp_path: Path) -> None:
    with lock.hold(tmp_path), pytest.raises(lock.StagingBusy) as e, lock.hold(tmp_path):
        pass
    msg = str(e.value)
    assert "another ev refresh is already writing" in msg
    assert "ev verify" not in msg and "If no ev refresh is running, delete" in msg
    # verify keeps its own wording
    with lock.hold(tmp_path):
        assert "then run ev verify again" in (lock.refusal(tmp_path) or "")


def test_every_refresh_leaves_a_stamp(tmp_path: Path) -> None:
    assert lock.last_run(tmp_path) is None
    with lock.hold(tmp_path):
        first = lock.last_run(tmp_path)
    assert first is not None and json.loads(first)["pid"]
    assert lock.last_run(tmp_path) == first  # stays after the run
    assert not lock.lock_path(tmp_path).exists()


def test_verify_fails_when_a_short_refresh_ran_during_the_rebuild(
    data_dir: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real = vr.rebuild

    def rebuild_with_a_quick_refresh(*a, **kw):  # type: ignore[no-untyped-def]
        out = real(*a, **kw)
        with lock.hold(data_dir):  # starts and finishes inside the rebuild
            pass
        return out

    monkeypatch.setattr(vr, "rebuild", rebuild_with_a_quick_refresh)
    rep = verify(data_dir, repo=data_dir, skip_tests=True, tricky=TRICKY, now=NOW)
    assert rep.status == "fail"
    assert any(".refresh.last changed" in f for f in rep.failures)


def test_refresh_command_prints_its_own_refusal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(runner.c, "data_dir", lambda: tmp_path)
    monkeypatch.setattr(runner, "_refresh", lambda opts, deps=None: pytest.fail("ran"))
    with lock.hold(tmp_path):
        runner.refresh(runner.RefreshOptions())
    out = capsys.readouterr().out
    assert "refresh: refused: another ev refresh is already writing" in out
    assert "run ev verify again" not in out


# --- G-54 / G-57 approved_changes -------------------------------------------------------


def _cfg(*approved: dict) -> dict:
    return {"schema": "approved-changes/v1", "files": [], "approved": list(approved)}


A3 = {"file": "catalogue.json", "id": "x", "field": "wltp_range_km", "reason": "r",
      "approved_by": "PR #1", "release": 3}  # fmt: skip
A4 = {**A3, "id": "y", "release": 4}
OLD = {**A3, "id": "old", "release": 2}


def test_new_entries_scoped_to_a_published_release_warn() -> None:
    new = ap.new_entries(_cfg(OLD, A3, A4), _cfg(OLD))
    assert new == [A3, A4]
    w = ap.stale_warnings(new, latest=3)
    assert len(w) == 1
    assert "catalogue.json:x:wltp_range_km" in w[0] and "Scope it to release 4" in w[0]
    assert ap.stale_warnings(new, latest=None) == []
    # no release scope = applies to any release: never stale
    assert ap.stale_warnings([{**A3, "release": None}], latest=9) == []
    assert ap.stale_warnings([{**A3, "release": [2, 3]}], latest=3) != []
    assert ap.stale_warnings([{**A3, "release": [3, 4]}], latest=3) == []


def test_check_reports_a_bad_approved_by_as_an_error(tmp_path: Path) -> None:
    p = tmp_path / "approved_changes.yaml"
    p.write_text(yaml.safe_dump(_cfg({**A4, "approved_by": "Menno said so"})))
    errors, warnings = ap.check(p, None, 3)
    assert len(errors) == 1 and "approved_by must start with 'PR #<n>'" in errors[0]
    assert warnings == []


def test_check_on_the_repo_file_loads() -> None:
    errors, _ = ap.check(REPO / "config" / "approved_changes.yaml", None, None)
    assert errors == []


def test_cli_exit_codes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    from ev_pipeline.cli import main

    head, base = tmp_path / "head.yaml", tmp_path / "base.yaml"
    head.write_text(yaml.safe_dump(_cfg(OLD, A3)))
    base.write_text(yaml.safe_dump(_cfg(OLD)))
    args = ["release", "approvals", "--file", str(head), "--base-file", str(base), "--latest", "3"]
    assert main(args) == 0  # a warning only
    assert "WARNING" in capsys.readouterr().out
    assert main([*args, "--strict"]) == 1
    head.write_text(yaml.safe_dump(_cfg({**A3, "reason": ""})))
    assert main(args) == 1
    assert "ERROR" in capsys.readouterr().out


def test_data_qa_runs_the_approvals_check() -> None:
    sh = (REPO / "data" / "seed" / "data_qa.sh").read_text()
    assert "uv run ev release approvals" in sh


# --- review round 1 (#195) --------------------------------------------------------------


def test_stamp_is_read_before_the_busy_check(
    data_dir: Path,  # noqa: F811
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A refresh that takes the lock right after verify's busy check, then finishes during the
    rebuild, must still fail the run (the stamp is read first)."""
    real = lock.refusal
    state = {"n": 0}

    def refusal_then_refresh(d: Path) -> str | None:
        state["n"] += 1
        if state["n"] == 1:  # the busy check passes; a refresh starts and stamps right after
            out = real(d)
            with lock.hold(d):
                pass
            return out
        return real(d)

    monkeypatch.setattr(lock, "refusal", refusal_then_refresh)
    rep = verify(data_dir, repo=data_dir, skip_tests=True, tricky=TRICKY, now=NOW)
    assert any(".refresh.last changed" in f for f in rep.failures)


def test_keep_refuses_a_file_and_a_folder_inside_data(data_dir: Path, tmp_path: Path) -> None:  # noqa: F811
    f = tmp_path / "afile"
    f.write_text("x")
    rep = verify(data_dir, repo=tmp_path, skip_tests=True, tricky=TRICKY, now=NOW, keep=f)
    assert rep.status == "fail" and "not an empty folder" in rep.failures[0]
    inside = data_dir / "kept"
    rep = verify(data_dir, repo=tmp_path, skip_tests=True, tricky=TRICKY, now=NOW, keep=inside)
    assert rep.status == "fail" and "outside data/" in rep.failures[0]
    assert not inside.exists()


def test_cli_bad_base_file_is_an_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    from ev_pipeline.cli import main

    head, base = tmp_path / "head.yaml", tmp_path / "base.yaml"
    head.write_text(yaml.safe_dump(_cfg(OLD)))
    base.write_text("approved: [unclosed\n")
    assert main(["release", "approvals", "--file", str(head), "--base-file", str(base)]) == 1
    assert "ERROR cannot read --base-file" in capsys.readouterr().out
