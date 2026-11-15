"""A-05 L6: git-cloned sources must pass the github.com host check before git runs.

No network: `subprocess.run` is replaced, and every test asserts git is never started
when the URL or the allowlist is wrong.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest

from ev_pipeline import net
from ev_pipeline.snapshot.probe import probe_git
from ev_pipeline.sources.kilowatt_openev import adapter as kw
from ev_pipeline.sources.openev import adapter as openev

ADAPTERS = [pytest.param(openev, id="openev"), pytest.param(kw, id="kilowatt-openev")]


def _sources_yaml(tmp: Path, hosts: dict[str, list[str]]) -> Path:
    lines = ["sources:"]
    for sid, hs in hosts.items():
        lines.append(f"  - {{id: {sid}, hosts: [{', '.join(hs)}]}}")
    path = tmp / "sources.yaml"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


class GitRecorder:
    """Stands in for subprocess.run; records calls and fails the clone (nothing on disk)."""

    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def __call__(self, cmd: list[str], *args: Any, **kwargs: Any) -> subprocess.CompletedProcess:
        self.calls.append(list(cmd))
        return subprocess.CompletedProcess(cmd, 128, stdout="", stderr="mocked: no network")


@pytest.fixture
def data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("EV_DATA_DIR", str(tmp_path))
    return tmp_path


# --- check_git_url ----------------------------------------------------------------------

GOOD = "https://github.com/open-ev-data/open-ev-data-dataset"


@pytest.mark.parametrize(
    "url", [GOOD, GOOD + ".git", "https://github.com/KilowattApp/open-ev-data"]
)
def test_check_git_url_accepts_github_repo(url: str) -> None:
    assert net.check_git_url("openev", url, hosts=["github.com"]) == url


@pytest.mark.parametrize(
    "url",
    [
        "http://github.com/a/b",  # not https
        "ssh://git@github.com/a/b",
        "git://github.com/a/b",
        "file:///etc/passwd",
        "ext::sh -c touch% /tmp/pwned",
        "https://github.com:8443/a/b",  # port
        "https://user:pw@github.com/a/b",  # user info
        "https://gitlab.com/a/b",  # not github
        "https://github.com.evil.example/a/b",
        "https://api.github.com/a/b",
        "https://github.com/a",  # owner only
        "https://github.com/a/b/c",  # extra path
        "https://github.com/a/b/",  # trailing slash = empty part
        "https://github.com/../b",
        "https://github.com/a/b?x=1",
        "https://github.com/a/b#frag",
        "https://github.com/-a/b",  # option-looking owner
        "https://140.82.112.3/a/b",  # IP literal
        "",
    ],
)
def test_check_git_url_refuses(url: str) -> None:
    with pytest.raises(net.FetchBlocked):
        net.check_git_url("openev", url, hosts=["github.com"])


def test_check_git_url_needs_host_in_allowlist(tmp_path: Path) -> None:
    path = _sources_yaml(tmp_path, {"openev": ["example.org"]})
    with pytest.raises(net.FetchBlocked, match="not in data/sources.yaml"):
        net.check_git_url("openev", GOOD, sources_path=path)


def test_check_git_url_fails_closed_without_source_entry(tmp_path: Path) -> None:
    path = _sources_yaml(tmp_path, {"other": ["github.com"]})
    with pytest.raises(ValueError, match="not listed"):
        net.check_git_url("openev", GOOD, sources_path=path)


def test_repo_sources_yaml_allows_both_git_sources() -> None:
    assert net.check_git_url("openev", openev.REPO_URL) == openev.REPO_URL
    assert net.check_git_url("kilowatt-openev", kw.REPO_URL) == kw.REPO_URL


def test_git_clone_cmd_pins_https_and_ends_options() -> None:
    cmd = net.git_clone_cmd("openev", GOOD, "/tmp/x", hosts=["github.com"])
    assert cmd[:5] == ["git", "-c", "protocol.allow=never", "-c", "protocol.https.allow=always"]
    assert cmd[-3:] == ["--", GOOD, "/tmp/x"]


# --- adapters ---------------------------------------------------------------------------


@pytest.mark.parametrize("mod", ADAPTERS)
def test_fetch_uses_checked_clone_cmd(
    mod: Any, data_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rec = GitRecorder()
    monkeypatch.setattr(subprocess, "run", rec)
    assert mod.fetch_cmd() == 1  # the mocked clone "fails"; nothing was fetched
    assert len(rec.calls) == 1
    cmd = rec.calls[0]
    assert "protocol.allow=never" in cmd and "protocol.https.allow=always" in cmd
    assert cmd[cmd.index("clone") :][-3] == "--" and mod.REPO_URL in cmd


@pytest.mark.parametrize("mod", ADAPTERS)
@pytest.mark.parametrize(
    "bad", ["https://gitlab.com/a/b", "ssh://git@github.com/a/b", "https://github.com/a/b/c"]
)
def test_fetch_refuses_bad_repo_url_before_git_runs(
    mod: Any, bad: str, data_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: Any
) -> None:
    rec = GitRecorder()
    monkeypatch.setattr(subprocess, "run", rec)
    monkeypatch.setattr(mod, "REPO_URL", bad)
    assert mod.fetch_cmd() == 1
    assert rec.calls == []
    assert "refusing to clone" in capsys.readouterr().out


@pytest.mark.parametrize("mod", ADAPTERS)
def test_fetch_refuses_when_host_not_allowlisted(
    mod: Any, data_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: Any
) -> None:
    _sources_yaml(data_dir, {mod.NAME: ["example.org"]})  # data_dir/sources.yaml wins
    rec = GitRecorder()
    monkeypatch.setattr(subprocess, "run", rec)
    assert mod.fetch_cmd() == 1
    assert rec.calls == []
    assert "not in data/sources.yaml" in capsys.readouterr().out


# --- probe ------------------------------------------------------------------------------


def test_probe_git_checks_url_when_source_known() -> None:
    calls: list[list[str]] = []

    def run(cmd: list[str]) -> str:
        calls.append(cmd)
        return "abc\tHEAD\n"

    assert probe_git(openev.REPO_URL, "abc", run, source_id="openev").status == "unchanged"
    assert calls[0][-3:] == ["--", openev.REPO_URL, "HEAD"]
    res = probe_git("https://gitlab.com/a/b", "abc", run, source_id="openev")
    assert res.status == "unknown" and "refused" in res.detail
    assert len(calls) == 1
