"""T-064 / Decision 035: releases out of git — split, manifest, publish, fetch, rollback."""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import pytest

from ev_pipeline.commands.releases import ReleaseOpError, rollback
from ev_pipeline.release.build import release_cmd
from ev_pipeline.release.publish import (
    MANIFEST,
    DirPublisher,
    GithubPublisher,
    PublishError,
    asset_name,
    ensure_local,
    fetch,
    http_downloader,
    join_split,
    load_config,
    package,
    read_manifest,
    split_catalogue,
    verify,
)

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


@pytest.fixture
def built(data_dir: Path) -> Path:
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 0
    return data_dir / "releases" / "1"


def _cat() -> dict[str, Any]:
    return {
        "release": 7,
        "generated_at": "2026-11-15T01:00:00+00:00",
        "sources": [{"id": "rdw"}],
        "generations": [{"id": "g1"}, {"id": "g2"}, {"id": "g-empty"}],
        "rows": [
            {"variant_id": "v1", "generation_id": "g1", "x": 1, "provenance": {"x": "rdw"}},
            {"variant_id": "v2", "generation_id": "g2", "x": 2, "provenance": {"x": "rdw"}},
            {"variant_id": "v3", "generation_id": "g1", "x": 3, "provenance": {}},
        ],
        "taxonomy": {"a": 1},
        "known_issues": {"country": "NL", "by_generation": {"g1": {"codes": ["X"]}}},
    }


# --- config + split ----------------------------------------------------------------------


def test_repo_config_loads_and_scratch_dir_falls_back(tmp_path: Path) -> None:
    cfg = load_config(tmp_path)  # no publish.yaml here -> repo config
    assert cfg.target == "github" and cfg.tag(3) == "data-v3"
    assert "github.com" in cfg.download_hosts
    assert cfg.asset_url(3, "a.json").endswith("/releases/download/data-v3/a.json")
    assert "qa.json" in cfg.in_git and "catalogue.json" not in cfg.in_git


def test_repo_config_names_the_renamed_repo(tmp_path: Path) -> None:
    """The repo was renamed EV-Finder -> EV-Shortlist (2026-11-17): new manifests' storage
    URLs must name the new repo (PR #91 review), not lean on GitHub's rename redirect."""
    cfg = load_config(tmp_path)
    assert cfg.repo == "zkMenno/EV-Shortlist"
    assert cfg.asset_url(2, "a.json").startswith("https://github.com/zkMenno/EV-Shortlist/")


def test_split_round_trips_and_index_has_no_provenance(tmp_path: Path) -> None:
    cfg = load_config(tmp_path)
    cat = _cat()
    files = split_catalogue(cat, cfg)
    assert join_split(files, cfg) == cat
    index = json.loads(files[cfg.index_path])
    assert all("provenance" not in r for r in index["rows"])
    assert "by_generation" not in index["known_issues"]
    assert set(index["generation_files"]) == {"g1", "g2", "g-empty"}
    g1 = json.loads(files[index["generation_files"]["g1"]])
    assert [r["variant_id"] for r in g1["rows"]] == ["v1", "v3"]
    assert g1["known_issues"] == {"codes": ["X"]} and g1["rows"][0]["provenance"] == {"x": "rdw"}
    empty = json.loads(files[index["generation_files"]["g-empty"]])
    assert empty["rows"] == [] and empty["generation"] == {"id": "g-empty"}


def test_split_is_deterministic(tmp_path: Path) -> None:
    cfg = load_config(tmp_path)
    assert split_catalogue(_cat(), cfg) == split_catalogue(_cat(), cfg)


@pytest.mark.parametrize("bad", ["../x", "a/b", ".hidden", ""])
def test_split_refuses_unsafe_generation_ids(tmp_path: Path, bad: str) -> None:
    cat = _cat()
    cat["generations"].append({"id": bad})
    with pytest.raises(PublishError, match="file name"):
        split_catalogue(cat, load_config(tmp_path))


def test_row_with_unlisted_generation_still_gets_a_file(tmp_path: Path) -> None:
    cfg = load_config(tmp_path)
    cat = _cat()
    cat["rows"].append({"variant_id": "v9", "generation_id": "g9", "provenance": {}})
    files = split_catalogue(cat, cfg)
    assert join_split(files, cfg) == cat


def test_asset_names_are_flat() -> None:
    assert asset_name("catalogue/generations/g1.json") == "catalogue.generations.g1.json"


# --- package / manifest / verify ---------------------------------------------------------


def test_release_writes_manifest_covering_every_file(built: Path) -> None:
    m = read_manifest(built)
    assert m is not None and m["release"] == 1 and m["storage"]["tag"] == "data-v1"
    paths = {e["path"] for e in m["files"]}
    assert {"catalogue.json", "catalogue/index.json", "qa.json"} <= paths
    assert MANIFEST not in paths
    on_disk = {p.relative_to(built).as_posix() for p in built.rglob("*") if p.is_file()} - {
        MANIFEST
    }
    assert paths == on_disk
    assert m["qa"]["status"] in {"pass", "review"}
    assert m["counts"]["files"] == len(m["files"])
    assert verify(built, m) == []
    flags = {e["path"]: e["in_git"] for e in m["files"]}
    assert flags["qa.json"] and not flags["catalogue.json"]


def test_package_is_idempotent(built: Path, data_dir: Path) -> None:
    before = (built / MANIFEST).read_bytes()
    package(built, load_config(data_dir), now=datetime(2030, 1, 1, tzinfo=UTC))
    assert (built / MANIFEST).read_bytes() == before


def test_split_of_real_release_round_trips(built: Path, data_dir: Path) -> None:
    cfg = load_config(data_dir)
    cat = json.loads((built / "catalogue.json").read_text())
    files = {
        p.relative_to(built).as_posix(): p.read_bytes()
        for p in (built / "catalogue").rglob("*.json")
    }
    assert join_split(files, cfg) == cat


def test_verify_detects_tampering_and_missing_files(built: Path) -> None:
    m = read_manifest(built)
    assert m is not None
    (built / "catalogue.json").write_bytes(b"{}")
    (built / "facts.parquet").unlink()
    problems = verify(built, m)
    assert any("catalogue.json" in p for p in problems)
    assert any("facts.parquet: missing" in p for p in problems)
    assert not any("facts.parquet" in p for p in verify(built, m, only_present=True))


def test_package_refuses_folder_number_mismatch(built: Path, data_dir: Path) -> None:
    wrong = built.parent / "5"
    shutil.copytree(built, wrong)
    with pytest.raises(PublishError, match="must match"):
        package(wrong, load_config(data_dir))


@pytest.mark.parametrize("bad", ["../etc/passwd", "/abs", "a\\b"])
def test_manifest_with_unsafe_path_is_refused(built: Path, bad: str) -> None:
    m = json.loads((built / MANIFEST).read_text())
    m["files"][0]["path"] = bad
    (built / MANIFEST).write_text(json.dumps(m))
    with pytest.raises(PublishError, match="unsafe"):
        read_manifest(built)


def test_manifest_with_unknown_schema_is_refused(built: Path) -> None:
    m = json.loads((built / MANIFEST).read_text())
    m["schema"] = "something/9"
    (built / MANIFEST).write_text(json.dumps(m))
    with pytest.raises(PublishError, match="schema"):
        read_manifest(built)


# --- publishers --------------------------------------------------------------------------


def test_dir_publisher_publishes_then_unchanged_then_refuses(built: Path, tmp_path: Path) -> None:
    m = read_manifest(built)
    assert m is not None
    pub = DirPublisher(tmp_path / "store")
    assert pub.publish(built, m, replace=False) == "published"
    assert (tmp_path / "store" / "data-v1" / "catalogue.generations").exists() is False
    assert any(
        p.name.startswith("catalogue.generations.")
        for p in (tmp_path / "store" / "data-v1").iterdir()
    )
    assert pub.publish(built, m, replace=False) == "unchanged"
    (tmp_path / "store" / "data-v1" / "catalogue.json").write_bytes(b"x")
    with pytest.raises(PublishError, match="refusing"):
        pub.publish(built, m, replace=False)
    assert pub.publish(built, m, replace=True) == "published"


class FakeGh:
    """Records gh calls; holds one fake release store."""

    def __init__(self) -> None:
        self.calls: list[list[str]] = []
        self.assets: dict[str, list[dict[str, Any]]] = {}

    def __call__(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        self.calls.append(args)
        verb, tag = args[2], args[3]
        if verb == "view":
            if tag not in self.assets:
                return subprocess.CompletedProcess(args, 1, "", "release not found")
            return subprocess.CompletedProcess(
                args, 0, json.dumps({"assets": self.assets[tag]}), ""
            )
        if verb == "delete":
            self.assets.pop(tag, None)
            return subprocess.CompletedProcess(args, 0, "", "")
        if verb == "create":
            files = [Path(a) for a in args if a.startswith("/") and not a.endswith(".notes.md")]
            import hashlib

            self.assets[tag] = [
                {"name": f.name, "size": f.stat().st_size,
                 "digest": "sha256:" + hashlib.sha256(f.read_bytes()).hexdigest()}
                for f in files
            ]  # fmt: skip
            return subprocess.CompletedProcess(args, 0, "", "")
        raise AssertionError(args)


def test_github_publisher_create_unchanged_refuse_replace(built: Path) -> None:
    m = read_manifest(built)
    assert m is not None
    gh = FakeGh()
    pub = GithubPublisher("zkMenno/EV-Finder", run=gh)
    assert pub.publish(built, m, replace=False) == "published"
    create = next(c for c in gh.calls if c[2] == "create")
    assert "--latest=false" in create and "zkMenno/EV-Finder" in create
    assert {a["name"] for a in gh.assets["data-v1"]} == {e["asset"] for e in m["files"]}
    assert pub.publish(built, m, replace=False) == "unchanged"
    gh.assets["data-v1"][0]["size"] += 1
    with pytest.raises(PublishError, match="never changes"):
        pub.publish(built, m, replace=False)
    assert pub.publish(built, m, replace=True) == "published"
    assert any(c[2] == "delete" for c in gh.calls)


def test_github_publisher_other_view_error_is_raised(built: Path) -> None:
    m = read_manifest(built)
    assert m is not None

    def run(args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args, 1, "", "HTTP 401 bad credentials")

    with pytest.raises(PublishError, match="401"):
        GithubPublisher("o/r", run=run).publish(built, m, replace=False)


# --- fetch / ensure_local / rollback -----------------------------------------------------


def _store_downloader(store: Path, log: list[str]):
    def dl(url: str, dest: Path, max_bytes: int) -> None:
        log.append(url)
        dest.write_bytes((store / url.rsplit("/", 1)[1]).read_bytes())

    return dl


def _publish_and_strip(built: Path, store: Path) -> dict[str, Any]:
    m = read_manifest(built)
    assert m is not None
    DirPublisher(store).publish(built, m, replace=False)
    for e in m["files"]:
        if not e["in_git"]:
            (built / e["path"]).unlink()  # what git would hold after T-064
    return m


def test_fetch_restores_files_from_assets(built: Path, data_dir: Path, tmp_path: Path) -> None:
    m = _publish_and_strip(built, tmp_path / "store")
    log: list[str] = []
    stats = fetch(
        built,
        load_config(data_dir),
        download=_store_downloader(tmp_path / "store" / "data-v1", log),
    )
    assert stats["downloaded"] == sum(1 for e in m["files"] if not e["in_git"])
    assert verify(built, m) == []
    assert all("/releases/download/data-v1/" in u for u in log)
    log.clear()
    again = fetch(
        built,
        load_config(data_dir),
        download=_store_downloader(tmp_path / "store" / "data-v1", log),
    )
    assert again["downloaded"] == 0 and log == []


def test_fetch_rejects_a_wrong_download_and_leaves_nothing(
    built: Path, data_dir: Path, tmp_path: Path
) -> None:
    _publish_and_strip(built, tmp_path / "store")

    def evil(url: str, dest: Path, max_bytes: int) -> None:
        dest.write_bytes(b"not the file")

    with pytest.raises(PublishError, match="checksum"):
        fetch(built, load_config(data_dir), download=evil)
    assert not (built / "catalogue.json").exists()
    assert not any(p.name.startswith(".") and ".part-" in p.name for p in built.rglob("*"))


def test_http_downloader_uses_guarded_client(built: Path, data_dir: Path, tmp_path: Path) -> None:
    store = tmp_path / "store"
    m = _publish_and_strip(built, store)
    seen: list[str] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req.url.host)
        name = req.url.path.rsplit("/", 1)[1]
        return httpx.Response(200, content=(store / "data-v1" / name).read_bytes())

    cfg = load_config(data_dir)
    fetch(built, cfg, download=http_downloader(cfg, transport=httpx.MockTransport(handler)))
    assert set(seen) == {"github.com"} and verify(built, m) == []


def test_http_downloader_refuses_hosts_outside_allowlist(tmp_path: Path) -> None:
    from ev_pipeline.net import FetchBlocked

    cfg = load_config(tmp_path)
    dl = http_downloader(cfg, transport=httpx.MockTransport(lambda r: httpx.Response(200)))
    with pytest.raises(FetchBlocked):
        dl("https://evil.example.com/x.json", tmp_path / "x", 100)


def test_ensure_local_fetches_missing_and_refuses_tampered(
    built: Path, data_dir: Path, tmp_path: Path
) -> None:
    _publish_and_strip(built, tmp_path / "store")
    log: list[str] = []
    ensure_local(data_dir, 1, download=_store_downloader(tmp_path / "store" / "data-v1", log))
    assert (built / "catalogue.json").exists() and log
    (built / "catalogue.json").write_bytes(b"{}")
    with pytest.raises(PublishError, match="catalogue.json"):
        ensure_local(data_dir, 1, download=_store_downloader(tmp_path / "store" / "data-v1", log))


def test_ensure_local_accepts_pre_t064_release(data_dir: Path) -> None:
    d = data_dir / "releases" / "3"
    d.mkdir(parents=True)
    (d / "catalogue.json").write_text("{}")
    assert ensure_local(data_dir, 3) == d


def test_rollback_fetches_release_outside_git(
    data_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 0
    (data_dir / "staging" / "eea.records.jsonl").unlink()
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 0
    store = tmp_path / "store"
    _publish_and_strip(data_dir / "releases" / "1", store)
    log: list[str] = []
    import ev_pipeline.release.publish as pub

    monkeypatch.setattr(
        pub,
        "http_downloader",
        lambda cfg, transport=None: _store_downloader(store / "data-v1", log),
    )
    entry = rollback(data_dir, 1)
    assert entry["to"] == 1 and log


def test_rollback_without_files_or_store_is_refused(
    data_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 0
    (data_dir / "staging" / "eea.records.jsonl").unlink()
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 0
    r1 = data_dir / "releases" / "1"
    m = read_manifest(r1)
    assert m is not None
    for e in m["files"]:
        if not e["in_git"]:
            (r1 / e["path"]).unlink()
    import ev_pipeline.release.publish as pub

    def offline(cfg: Any, transport: Any = None):
        def dl(url: str, dest: Path, max_bytes: int) -> None:
            raise PublishError("offline")

        return dl

    monkeypatch.setattr(pub, "http_downloader", offline)
    with pytest.raises(ReleaseOpError, match="unavailable"):
        rollback(data_dir, 1)


def test_next_release_diffs_against_fetched_previous(
    data_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 0
    store = tmp_path / "store"
    _publish_and_strip(data_dir / "releases" / "1", store)
    log: list[str] = []
    import ev_pipeline.release.publish as pub

    monkeypatch.setattr(
        pub,
        "http_downloader",
        lambda cfg, transport=None: _store_downloader(store / "data-v1", log),
    )
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 0
    diff = json.loads((data_dir / "releases" / "2" / "diff.json").read_text())
    assert diff["counts"]["added"] == 0 and log  # compared with release 1, not with nothing


def test_next_release_fails_when_previous_unavailable(
    data_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 0
    r1 = data_dir / "releases" / "1"
    (r1 / "catalogue.json").unlink()
    import ev_pipeline.release.publish as pub

    def offline(cfg: Any, transport: Any = None):
        def dl(url: str, dest: Path, max_bytes: int) -> None:
            raise PublishError("offline")

        return dl

    monkeypatch.setattr(pub, "http_downloader", offline)
    assert release_cmd(False, data_dir=data_dir, now=NOW) == 1
    assert not (data_dir / "releases" / "2").exists()


def test_gitignore_keeps_exactly_the_in_git_files(tmp_path: Path) -> None:
    """.gitignore and publish.yaml `in_git` must list the same files (plus manifest.json)."""
    root = Path(__file__).resolve().parents[2]
    lines = (root / ".gitignore").read_text(encoding="utf-8").splitlines()
    kept = {
        ln.removeprefix("!data/releases/[0-9]*/")
        for ln in lines
        if ln.startswith("!data/releases/[0-9]*/")
    }
    assert "data/releases/[0-9]*/*" in lines
    assert kept == set(load_config(tmp_path).in_git) | {MANIFEST}


# --- the workflow's shell publisher (pipeline/scripts/gh-publish-release.sh) -------------

FAKE_GH = """#!/usr/bin/env bash
s="$FAKE_GH_STORE"; verb=$2; tag=$3
case $verb in
 view) [ -d "$s/$tag" ] || exit 1
       for f in "$s/$tag"/*; do
         printf '%s\\t%s\\n' "$(basename "$f")" "$(wc -c < "$f" | tr -d ' ')"
       done;;
 delete) rm -rf "$s/$tag";;
 create) mkdir -p "$s/$tag"
         for a in "$@"; do
           if [ -f "$a" ]; then case "$a" in */.notes.md) ;; *) cp "$a" "$s/$tag/";; esac; fi
         done;;
esac
"""


@pytest.mark.skipif(shutil.which("jq") is None, reason="jq not installed")
def test_shell_publisher_publishes_unchanged_and_refuses(built: Path, tmp_path: Path) -> None:
    script = Path(__file__).resolve().parents[1] / "scripts" / "gh-publish-release.sh"
    bindir = tmp_path / "bin"
    bindir.mkdir()
    (bindir / "gh").write_text(FAKE_GH)
    (bindir / "gh").chmod(0o755)
    store = tmp_path / "store"
    env = {
        **__import__("os").environ,
        "PATH": f"{bindir}:{__import__('os').environ['PATH']}",
        "GITHUB_REPOSITORY": "o/r",
        "FAKE_GH_STORE": str(store),
    }

    def run(*extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(script), str(built), *extra], env=env, capture_output=True, text=True
        )

    first = run()
    assert first.returncode == 0 and "published" in first.stdout, first.stderr + first.stdout
    m = read_manifest(built)
    assert m is not None
    assert {p.name for p in (store / "data-v1").iterdir()} == {e["asset"] for e in m["files"]}
    assert "unchanged" in run().stdout
    (store / "data-v1" / "qa.md").write_text("changed")
    refused = run()
    assert refused.returncode == 1 and "never changes" in refused.stdout
    shutil.rmtree(store)
    (built / "catalogue.json").write_bytes(b"{}")
    bad = run()
    assert bad.returncode == 1 and "differs from manifest" in bad.stdout


def test_fetch_only_selected_files(built: Path, data_dir: Path, tmp_path: Path) -> None:
    _publish_and_strip(built, tmp_path / "store")
    log: list[str] = []
    dl = _store_downloader(tmp_path / "store" / "data-v1", log)
    stats = fetch(built, load_config(data_dir), download=dl, only=frozenset({"catalogue.json"}))
    assert stats["downloaded"] == 1 and (built / "catalogue.json").exists()
    assert not (built / "facts.parquet").exists()
    fetch(built, load_config(data_dir), download=dl, only=frozenset({"catalogue/"}))
    assert (built / "catalogue" / "index.json").exists()
    with pytest.raises(PublishError, match="not in the manifest"):
        fetch(built, load_config(data_dir), download=dl, only=frozenset({"nope.json"}))


def test_ensure_local_only_ignores_absent_optional_files(built: Path, data_dir: Path) -> None:
    # Only catalogue.json is needed and present: no download even though split files are gone.
    shutil.rmtree(built / "catalogue")

    def no_net(url: str, dest: Path, max_bytes: int) -> None:
        raise AssertionError("should not download")

    only = frozenset({"catalogue.json", "not-in-this-release.json"})
    assert ensure_local(data_dir, 1, download=no_net, only=only) == built
