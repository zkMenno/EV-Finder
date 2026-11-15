"""Addendum 6 P1/P3: `ev refresh`, snapshot store, skip-unchanged, fingerprint drift. Offline."""

from __future__ import annotations

import csv
import json
import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
import pytest

from ev_pipeline import net
from ev_pipeline.cli import main
from ev_pipeline.health import fingerprint as fp
from ev_pipeline.health.state import load_state, release_sources_doc, review_id
from ev_pipeline.refresh.plan import cadence_interval, plan
from ev_pipeline.refresh.runner import (
    EXIT_OK,
    EXIT_SOURCE_PROBLEMS,
    Deps,
    RefreshOptions,
    refresh,
)
from ev_pipeline.snapshot.probe import probe_git, probe_http
from ev_pipeline.snapshot.recording import recording
from ev_pipeline.snapshot.store import (
    LocalSnapshotStore,
    S3SnapshotStore,
    SnapshotError,
    content_hash,
    open_store,
    restore_snapshot,
    scan_tree,
    take_snapshot,
)
from ev_pipeline.sources import _common as c

FIX = Path(__file__).parent / "fixtures" / "release"
NOW = datetime(2026, 11, 15, 2, 0, tzinfo=UTC)
HOST = "data.example.org"
CSV_OK = "make,model,count\nTESLA,MODEL 3,10\nKIA,EV6,5\n" + "".join(
    f"X{i},Y{i},{i}\n" for i in range(8)
)


class FakeAdapter:
    """Stands in for ev_pipeline.sources.<id>.adapter: writes raw files, then staging."""

    def __init__(self, name: str = "fake") -> None:
        self.NAME = name
        self.DIR = name.replace("-", "_")
        self.files: dict[str, str] = {"data.csv": CSV_OK}
        self.fetch_rc = 0
        self.fetches = 0
        self.normalises = 0
        self.etag: str | None = None
        self.REQUIRES_ENV: list[str] = []

    def fetch_cmd(self) -> int:
        self.fetches += 1
        if self.fetch_rc:
            return self.fetch_rc
        if self.etag:  # go through net.safe_client like a real adapter
            transport = httpx.MockTransport(
                lambda req: httpx.Response(200, headers={"ETag": self.etag}, text="x")
            )
            with net.safe_client(self.NAME, transport=transport, hosts=[HOST]) as client:
                client.get(f"https://{HOST}/data.csv").raise_for_status()
        target = c.raw_dir(self.DIR)
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)
        for name, text in self.files.items():
            (target / name).write_text(text, encoding="utf-8")
        c.write_fetch_meta(target, {"url": f"https://{HOST}/data.csv"})
        return 0

    def normalise_cmd(self, from_fixtures: bool) -> int:
        self.normalises += 1
        src = c.raw_dir(self.DIR) / "data.csv"
        with src.open(encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        out = c.staging_dir() / f"{self.NAME}.records.jsonl"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        return 0


REGISTRY = """schema: sources/v1
sources:
  - {id: fake, name: Fake source, licence: CC0-1.0, cadence: weekly, status: active}
  - {id: pending, name: Pending, licence: none, cadence: weekly, status: waiting_permission}
  - {id: nyland, name: Nyland, licence: none, cadence: ad hoc, status: active}
"""


@pytest.fixture
def data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    d = tmp_path / "data"
    d.mkdir()
    (d / "sources.yaml").write_text(REGISTRY, encoding="utf-8")
    monkeypatch.setenv("EV_DATA_DIR", str(d))
    monkeypatch.delenv("EV_RUNS_DIR", raising=False)
    monkeypatch.delenv("SNAPSHOT_DIR", raising=False)
    monkeypatch.delenv("SNAPSHOT_BACKEND", raising=False)
    return d


def _deps(adapter: FakeAdapter, now: datetime = NOW, **kw: Any) -> Deps:
    return Deps(
        find=lambda sid: adapter if sid == adapter.NAME else None,
        now=lambda: now,
        **kw,
    )


def _run(adapter: FakeAdapter, now: datetime = NOW, **opts: Any) -> tuple[int, dict]:
    opts.setdefault("release", False)
    return refresh(RefreshOptions(**opts), _deps(adapter, now))


def _status(log: dict, sid: str = "fake") -> dict:
    return next(s for s in log["sources"] if s["id"] == sid)


def _staging(d: Path, sid: str = "fake") -> Path:
    return d / "staging" / f"{sid}.records.jsonl"


# --- snapshot store ----------------------------------------------------------------------


def test_content_hash_ignores_fetch_meta_and_git(tmp_path: Path) -> None:
    a = tmp_path / "a"
    (a / ".git").mkdir(parents=True)
    (a / "x.csv").write_text("1")
    (a / ".git" / "HEAD").write_text("ref")
    (a / "_fetch.json").write_text('{"fetched_at": "2026-01-01T00:00:00+00:00"}')
    (a / "big.part").write_text("partial")
    files = scan_tree(a)
    assert [f["path"] for f in files] == ["x.csv"]
    h1 = content_hash(files)
    (a / "_fetch.json").write_text('{"fetched_at": "2026-02-02T00:00:00+00:00"}')
    assert content_hash(scan_tree(a)) == h1
    (a / "x.csv").write_text("2")
    assert content_hash(scan_tree(a)) != h1


def test_snapshot_dedupes_blobs_and_restores(tmp_path: Path) -> None:
    store = LocalSnapshotStore(tmp_path / "snap")
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "a.csv").write_text("a,b\n1,2\n")
    (raw / "sub").mkdir()
    (raw / "sub" / "b.json").write_text("[]")
    c.write_fetch_meta(raw, {"url": "https://x.example/a"})
    m1, new1 = take_snapshot(store, "src", raw, [{"url": "u", "status": 200, "etag": '"1"'}])
    assert new1 and m1.files and m1.bytes == 10
    m2, new2 = take_snapshot(store, "src", raw)
    assert not new2 and m2.id == m1.id  # same content: no new manifest
    (raw / "a.csv").write_text("a,b\n1,3\n")
    m3, new3 = take_snapshot(store, "src", raw)
    assert new3 and m3.content_hash != m1.content_hash
    blobs = list((tmp_path / "snap" / "objects").rglob("*"))
    assert len([b for b in blobs if b.is_file()]) == 3  # b.json stored once
    assert len(store.manifests("src")) == 2
    restore_snapshot(store, m1, raw)
    assert (raw / "a.csv").read_text() == "a,b\n1,2\n"
    assert c.read_fetch_meta(raw)["url"] == "https://x.example/a"
    first = next(m for m in store.manifests("src") if m.id == m1.id)
    assert first.responses[0]["etag"] == '"1"'


def test_snapshot_refuses_bad_ids_and_paths(tmp_path: Path) -> None:
    store = LocalSnapshotStore(tmp_path)
    with pytest.raises(SnapshotError):
        store.has_blob("../../etc/passwd")
    with pytest.raises(SnapshotError):
        store.manifests("../x")
    with pytest.raises(SnapshotError):
        take_snapshot(store, "src", tmp_path / "empty")


def test_open_store_backends(tmp_path: Path) -> None:
    store = open_store({"SNAPSHOT_DIR": str(tmp_path)})
    assert isinstance(store, LocalSnapshotStore) and store.root == tmp_path
    with pytest.raises(SnapshotError, match="S3_BUCKET"):
        open_store({"SNAPSHOT_BACKEND": "s3", "S3_ENDPOINT": "https://s3.example"})
    env = {k: "x" for k in S3SnapshotStore.ENV} | {"SNAPSHOT_BACKEND": "s3"}
    with pytest.raises(NotImplementedError):
        open_store(env)
    with pytest.raises(SnapshotError):
        open_store({"SNAPSHOT_BACKEND": "ftp"})


def test_recording_captures_validators_and_restores_safe_client() -> None:
    original = net.safe_client
    transport = httpx.MockTransport(
        lambda r: httpx.Response(
            200, headers={"ETag": '"v1"', "Last-Modified": "Sun, 01 Nov 2026 00:00:00 GMT"}
        )
    )
    with (
        recording("fake") as rec,
        net.safe_client("fake", transport=transport, hosts=[HOST]) as client,
    ):
        client.get(f"https://{HOST}/a.csv")
    assert net.safe_client is original
    assert rec.responses == [
        {
            "url": f"https://{HOST}/a.csv",
            "method": "GET",
            "status": 200,
            "etag": '"v1"',
            "last_modified": "Sun, 01 Nov 2026 00:00:00 GMT",
        }
    ]


# --- probes ------------------------------------------------------------------------------


def test_probe_http_304_and_changed() -> None:
    seen: list[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req)
        if req.headers.get("if-none-match") == '"v1"':
            return httpx.Response(304)
        return httpx.Response(200, headers={"ETag": '"v2"'})

    def factory() -> httpx.Client:
        return net.safe_client("fake", transport=httpx.MockTransport(handler), hosts=[HOST])

    rec = [{"url": f"https://{HOST}/a", "method": "GET", "status": 200, "etag": '"v1"'}]
    assert probe_http(rec, factory).status == "unchanged"
    assert seen[0].method == "HEAD"
    rec2 = [{"url": f"https://{HOST}/a", "method": "GET", "status": 200, "etag": '"v0"'}]
    assert probe_http(rec2, factory).status == "changed"
    no_validators = [{"url": f"https://{HOST}/a", "method": "GET", "status": 200}]
    assert probe_http(no_validators, factory).status == "unknown"
    blocked = [{"url": "https://evil.example/a", "method": "GET", "status": 200, "etag": "x"}]
    assert probe_http(blocked, factory).status == "unknown"  # allowlist still applies
    many = rec * 30
    assert probe_http(many, factory).status == "unknown"


def test_probe_git() -> None:
    assert probe_git("u", "abc", lambda cmd: "abc\tHEAD\n").status == "unchanged"
    assert probe_git("u", "abc", lambda cmd: "def\tHEAD\n").status == "changed"
    assert probe_git("u", "abc", lambda cmd: "").status == "unknown"

    def boom(cmd: list[str]) -> str:
        raise OSError("no git")

    assert probe_git("u", "abc", boom).status == "unknown"


# --- plan --------------------------------------------------------------------------------


def test_cadence_intervals() -> None:
    assert cadence_interval("weekly") == timedelta(days=7)
    assert cadence_interval("Monthly") == timedelta(days=30)
    assert cadence_interval("ad hoc") is None and cadence_interval(None) is None


def test_plan_due_logic(data_dir: Path) -> None:
    fake = FakeAdapter()

    def find(s: str) -> Any:
        return fake if s == "fake" else None

    p = {x.id: x for x in plan(data_dir, {}, NOW, find=find)}
    assert p["fake"].action == "run" and p["fake"].reason == "no staging file"
    assert p["nyland"].action == "skip"  # permission pending, whatever the registry says
    assert "pending" not in p  # not active, not named
    _staging(data_dir).parent.mkdir(parents=True)
    _staging(data_dir).write_text("{}\n")
    recent = {"fake": {"last_checked": (NOW - timedelta(days=2)).isoformat()}}
    assert plan(data_dir, recent, NOW, find=find)[0].action == "not_due"
    old = {"fake": {"last_checked": (NOW - timedelta(days=6, hours=13)).isoformat()}}
    assert plan(data_dir, old, NOW, find=find)[0].action == "run"  # 12 h slack
    assert plan(data_dir, recent, NOW, force=True, find=find)[0].action == "run"
    named = {x.id: x for x in plan(data_dir, recent, NOW, only=["fake", "pending", "x"], find=find)}
    assert named["fake"].action == "run"
    assert named["pending"].action == "skip" and named["x"].action == "skip"
    fake.REQUIRES_ENV = ["FAKE_API_KEY"]
    p = plan(data_dir, {}, NOW, find=find, env={})
    assert p[0].action == "skip" and "FAKE_API_KEY" in p[0].reason
    assert plan(data_dir, {}, NOW, find=find, env={"FAKE_API_KEY": "k"})[0].action == "run"


# --- refresh -----------------------------------------------------------------------------


def test_first_refresh_fetches_snapshots_and_normalises(data_dir: Path) -> None:
    fake = FakeAdapter()
    code, log = _run(fake)
    assert code == EXIT_OK
    s = _status(log)
    assert s["status"] == "ok" and s["changed"]
    assert [st["step"] for st in s["steps"]] == [
        "probe",
        "fetch",
        "snapshot",
        "fingerprint",
        "normalise",
    ]
    assert all(st["peak_rss_mb"] > 0 for st in s["steps"])
    assert log["peak_rss_mb"] > 0 and log["within_memory_budget"]
    assert _status(log, "nyland")["status"] == "skip"
    entry = load_state(data_dir)["fake"]
    assert entry["records"] == 10 and entry["status"] == "ok"
    assert entry["content_hash"].startswith("sha256:")
    assert entry["fingerprint"]["hash"].startswith("fp:")
    assert entry["last_success"] == entry["last_change"] == NOW.isoformat()
    assert (data_dir / "snapshots" / "fake").is_dir()
    run_logs = list((data_dir / "runs").glob("2026*.json"))
    assert len(run_logs) == 1
    assert json.loads(run_logs[0].read_text())["sources"][0]["id"] == "fake"


def test_unchanged_content_skips_normalise_and_release(data_dir: Path) -> None:
    fake = FakeAdapter()
    _run(fake)
    later = NOW + timedelta(days=8)
    code, log = _run(fake, later, release=True)
    s = _status(log)
    assert code == EXIT_OK and s["status"] == "unchanged" and s["message"] == "same content hash"
    assert fake.normalises == 1 and fake.fetches == 2
    assert log["release"]["outcome"] == "skipped"
    entry = load_state(data_dir)["fake"]
    assert entry["last_change"] == NOW.isoformat()
    assert entry["last_success"] == later.isoformat()


def test_not_due_source_is_not_fetched(data_dir: Path) -> None:
    fake = FakeAdapter()
    _run(fake)
    code, log = _run(fake, NOW + timedelta(days=1))
    assert _status(log)["status"] == "not_due" and fake.fetches == 1 and code == EXIT_OK


def test_etag_304_skips_download(data_dir: Path) -> None:
    fake = FakeAdapter()
    fake.etag = '"v1"'
    _run(fake)
    assert load_state(data_dir)["fake"]["responses"][0]["etag"] == '"v1"'

    def handler(req: httpx.Request) -> httpx.Response:
        if req.method == "HEAD" and req.headers.get("if-none-match") == '"v1"':
            return httpx.Response(304)
        return httpx.Response(200, headers={"ETag": '"v2"'})

    deps = _deps(fake, NOW + timedelta(days=8))
    deps.client_factory = lambda sid: net.safe_client(
        sid, transport=httpx.MockTransport(handler), hosts=[HOST]
    )
    code, log = refresh(RefreshOptions(release=False), deps)
    s = _status(log)
    assert s["status"] == "unchanged" and "not modified" in s["message"]
    assert fake.fetches == 1  # no download


def test_git_probe_skips_clone(data_dir: Path) -> None:
    fake = FakeAdapter()
    fake.REPO_URL = "https://github.com/example/repo"  # type: ignore[attr-defined]
    orig = fake.fetch_cmd

    def fetch_with_commit() -> int:
        rc = orig()
        meta = c.read_fetch_meta(c.raw_dir(fake.DIR))
        c.write_fetch_meta(c.raw_dir(fake.DIR), {**meta, "commit": "abc123"})
        return rc

    fake.fetch_cmd = fetch_with_commit  # type: ignore[method-assign]
    _run(fake)
    assert load_state(data_dir)["fake"]["commit"] == "abc123"
    # The probe checks the git URL against `hosts:` first (A-05 L6); fake lists github.com.
    (data_dir / "sources.yaml").write_text(
        REGISTRY.replace("status: active}", "status: active, hosts: [github.com]}", 1),
        encoding="utf-8",
    )
    deps = _deps(fake, NOW + timedelta(days=8), git_runner=lambda cmd: "abc123\tHEAD\n")
    _, log = refresh(RefreshOptions(release=False), deps)
    assert _status(log)["status"] == "unchanged" and fake.fetches == 1
    deps = _deps(fake, NOW + timedelta(days=16), git_runner=lambda cmd: "fff\tHEAD\n")
    _, log = refresh(RefreshOptions(release=False), deps)
    assert fake.fetches == 2


def test_schema_drift_fails_closed_then_accept(data_dir: Path) -> None:
    fake = FakeAdapter()
    _run(fake)
    before = _staging(data_dir).read_text()
    many = "model,count\n" + "".join(f"M{i},{i}\n" for i in range(30))  # `make` column gone
    fake.files = {"data.csv": many}
    later = NOW + timedelta(days=8)
    code, log = _run(fake, later)
    s = _status(log)
    assert code == EXIT_SOURCE_PROBLEMS and s["status"] == "drift"
    assert "column gone: make" in json.dumps(s["steps"])
    assert _staging(data_dir).read_text() == before  # previous good staging kept
    assert fake.normalises == 1
    assert (c.raw_dir("fake") / "data.csv").read_text() == CSV_OK  # raw restored too
    entry = load_state(data_dir)["fake"]
    assert entry["status"] == "drift" and entry["seen_fingerprint"]
    assert entry["last_success"] == NOW.isoformat()
    with (data_dir / "review" / "source-health.csv").open() as fh:
        items = list(csv.DictReader(fh))
    assert len(items) == 1 and items[0]["status"] == "open" and items[0]["kind"] == "schema_drift"
    assert items[0]["id"] == entry["review_id"]
    # Same drift again: still closed, same review id, no duplicate row.
    _run(fake, later + timedelta(days=8))
    with (data_dir / "review" / "source-health.csv").open() as fh:
        assert len(list(csv.DictReader(fh))) == 1
    # A human accepts it.
    code, log = _run(fake, later + timedelta(days=9), sources=["fake"], accept={"fake"})
    assert code == EXIT_OK and _status(log)["status"] == "ok"
    entry = load_state(data_dir)["fake"]
    assert entry["records"] == 30 and "seen_fingerprint" not in entry


def test_added_column_is_not_drift(data_dir: Path) -> None:
    fake = FakeAdapter()
    _run(fake)
    fake.files = {"data.csv": CSV_OK.replace("make,model,count", "make,model,count,extra")}
    _, log = _run(fake, NOW + timedelta(days=8))
    s = _status(log)
    assert s["status"] == "ok"
    fps = next(st for st in s["steps"] if st["step"] == "fingerprint")
    assert fps["outcome"] == "changed" and any("new column: extra" in a for a in fps["additive"])


def test_record_drop_fails_closed(data_dir: Path) -> None:
    fake = FakeAdapter()
    _run(fake)
    before = _staging(data_dir).read_text()
    fake.files = {"data.csv": "make,model,count\nTESLA,MODEL 3,10\n"}
    code, log = _run(fake, NOW + timedelta(days=8))
    s = _status(log)
    assert code == EXIT_SOURCE_PROBLEMS and s["status"] == "rows_dropped"
    assert "10 to 1" in s["message"]
    assert _staging(data_dir).read_text() == before
    assert load_state(data_dir)["fake"]["records"] == 10


def test_fetch_failure_keeps_previous_data(data_dir: Path) -> None:
    fake = FakeAdapter()
    _run(fake)
    before = _staging(data_dir).read_text()
    fake.fetch_rc = 1
    code, log = _run(fake, NOW + timedelta(days=8))
    assert code == EXIT_SOURCE_PROBLEMS and _status(log)["status"] == "failed"
    assert _staging(data_dir).read_text() == before
    entry = load_state(data_dir)["fake"]
    assert entry["status"] == "failed" and entry["last_success"] == NOW.isoformat()


def test_adapter_exception_is_contained(data_dir: Path) -> None:
    fake = FakeAdapter()

    def boom() -> int:
        raise RuntimeError("parser exploded")

    fake.fetch_cmd = boom  # type: ignore[method-assign]
    code, log = _run(fake)
    assert code == EXIT_SOURCE_PROBLEMS
    assert "parser exploded" in _status(log)["message"]


def test_dry_run_writes_nothing(data_dir: Path) -> None:
    fake = FakeAdapter()
    code, log = _run(fake, dry_run=True)
    assert code == EXIT_OK and _status(log)["status"] == "would_fetch"
    assert fake.fetches == 0
    assert sorted(p.name for p in data_dir.iterdir()) == ["sources.yaml"]


def test_release_guard_when_a_source_has_no_staging(data_dir: Path) -> None:
    fake, other = FakeAdapter(), FakeAdapter("other")
    other.fetch_rc = 1
    (data_dir / "sources.yaml").write_text(
        REGISTRY + "  - {id: other, name: O, licence: CC0-1.0, cadence: weekly, status: active}\n"
    )
    deps = Deps(find=lambda s: {"fake": fake, "other": other}.get(s), now=lambda: NOW)
    code, log = refresh(RefreshOptions(), deps)
    assert log["release"]["outcome"] == "skipped"
    assert "no staging data for other" in log["release"]["reason"]
    assert code == EXIT_SOURCE_PROBLEMS


# --- release integration (fixture catalogue) ---------------------------------------------


@pytest.fixture
def release_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
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
    monkeypatch.delenv("SNAPSHOT_DIR", raising=False)
    return d


class StagingCopyAdapter(FakeAdapter):
    """Fetch = copy the fixture staging file into raw; normalise = copy it back."""

    def __init__(self, name: str, payload: str) -> None:
        super().__init__(name)
        self.payload = payload

    def fetch_cmd(self) -> int:
        self.fetches += 1
        target = c.raw_dir(self.DIR)
        target.mkdir(parents=True, exist_ok=True)
        (target / "records.jsonl").write_text(self.payload, encoding="utf-8")
        c.write_fetch_meta(target, {"url": "https://example.org/fixture"})
        return 0

    def normalise_cmd(self, from_fixtures: bool) -> int:
        self.normalises += 1
        shutil.copy(c.raw_dir(self.DIR) / "records.jsonl", c.staging_dir() / "rdw.records.jsonl")
        return 0


def test_refresh_publishes_release_with_sources_json(release_dir: Path) -> None:
    payload = (FIX / "staging" / "rdw.records.jsonl").read_text()
    rdw = StagingCopyAdapter("rdw", payload)
    deps = Deps(find=lambda s: rdw if s == "rdw" else None, now=lambda: NOW)
    code, log = refresh(RefreshOptions(), deps)
    assert code == EXIT_OK, log
    assert log["release"]["outcome"] == "published" and log["release"]["release"] == 1
    out = release_dir / "releases" / "1"
    assert (release_dir / "releases" / "latest").read_text().strip() == "1"
    doc = json.loads((out / "sources.json").read_text())
    assert doc["schema"] == "release-sources/v1" and doc["release"] == 1
    assert doc["sources"]["rdw"]["status"] == "ok"
    assert doc["sources"]["rdw"]["records"] == len(payload.splitlines())
    assert doc["sources"]["rdw"]["data_as_of"]
    assert doc["sources"]["rdw"]["fingerprint"]["hash"].startswith("fp:")
    assert doc["sources"]["openev"]["status"] == "not_refreshed"  # cited, not refreshed
    summary = json.loads((out / "refresh.json").read_text())
    assert summary["sources"]["rdw"]["status"] == "ok" and summary["peak_rss_mb"] > 0
    # A fresh machine (no local state) starts from the release's sources.json.
    shutil.rmtree(release_dir / "runs")
    assert load_state(release_dir)["rdw"]["content_hash"] == doc["sources"]["rdw"]["content_hash"]
    # Same data next week: no new release.
    _, log = refresh(RefreshOptions(), Deps(find=deps.find, now=lambda: NOW + timedelta(days=8)))
    assert _status(log, "rdw")["status"] == "unchanged"
    assert log["release"]["outcome"] == "skipped"
    assert not (release_dir / "releases" / "2").exists()


def test_release_sources_doc_for_plain_release(release_dir: Path) -> None:
    cat = {"release": 3, "generated_at": "x", "sources": [{"id": "openev"}]}
    doc = release_sources_doc(release_dir, cat, [{"id": "openev", "name": "O", "status": "active"}])
    assert doc["sources"]["openev"]["registry_status"] == "active"
    assert doc["sources"]["openev"]["in_catalogue"] is True


# --- fingerprint units -------------------------------------------------------------------


def test_fingerprint_normalises_digits_and_months(tmp_path: Path) -> None:
    (tmp_path / "page-001.json").write_text(json.dumps([{"a": 1, "b": "x"}] * 25))
    (tmp_path / "page-002.json").write_text(json.dumps([{"a": 2, "b": "y"}] * 25))
    (tmp_path / "q.csv").write_text("Make,2026 Q2,2026 Q1\nA,1,2\n")
    f = fp.fingerprint_tree(tmp_path)
    assert set(f["groups"]) == {"page-#.json", "q.csv"}
    assert set(f["groups"]["q.csv"]["columns"]) == {"Make", "# Q#"}
    assert f["groups"]["page-#.json"]["files"] == 2
    assert fp.norm_name("Oktober 2026") == "<month> #"
    # A new quarter column is not drift.
    (tmp_path / "q.csv").write_text("Make,2026 Q3,2026 Q2\nA,1,2\n")
    assert fp.compare(f, fp.fingerprint_tree(tmp_path))["same"]


def test_fingerprint_map_keys_and_rare_paths(tmp_path: Path) -> None:
    brands = {f"brand{i}x": {"name": "n"} for i in range(60)}
    (tmp_path / "brands.json").write_text(json.dumps(brands))
    cols = fp.fingerprint_tree(tmp_path)["groups"]["brands.json"]["columns"]
    assert "{*}.name" in cols  # a big dict is a map, not 60 columns


def test_fingerprint_compare_rules() -> None:
    old = {
        "hash": "fp:1",
        "groups": {
            "a.csv": {"files": 1, "columns": {"x": {"types": "num", "n": 20}}},
            "b.json": {
                "files": 1,
                "columns": {"$.rare": {"types": "str", "n": 3}, "$.k": {"types": "num", "n": 50}},
            },
        },
    }
    new = {
        "hash": "fp:2",
        "groups": {
            "a.csv": {"files": 1, "columns": {"x": {"types": "str", "n": 20}}},
            "b.json": {"files": 1, "columns": {"$.k": {"types": "num", "n": 50}}},
            "c.csv": {"files": 1, "columns": {}},
        },
    }
    r = fp.compare(old, new)
    assert r["breaking"] == []  # rare path gone, type change: not breaking
    assert any("type num -> str" in a for a in r["additive"])
    assert any("new file group: c.csv" in a for a in r["additive"])
    del new["groups"]["a.csv"]
    assert fp.compare(old, new)["breaking"] == ["file group gone: a.csv"]
    assert fp.compare(None, new)["first"]


def test_fingerprint_xlsx_skips_data_cells(tmp_path: Path) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "FZ 10.1"
    ws.append(["Neuzulassungen im Oktober 2026"])
    ws.append(["Marke", "Modellreihe", "mit Elektroantrieb (BEV)"])
    ws.append(["TESLA", "MODEL Y", 1200])
    wb.save(tmp_path / "fz10_2026_10.xlsx")
    cols = fp.fingerprint_tree(tmp_path)["groups"]["fz#_#_#.xlsx"]["columns"]
    assert "FZ #.#!Marke" in cols and "FZ #.#!Neuzulassungen im <month> #" in cols
    assert not any("TESLA" in k for k in cols)


def test_review_id_is_stable() -> None:
    assert review_id("a", "k", "1", "2") == review_id("a", "k", "1", "2")
    assert review_id("a", "k", "1", "2") != review_id("a", "k", "1", "3")


# --- CLI ---------------------------------------------------------------------------------


def test_cli_sources_check_and_refresh_dry_run(
    data_dir: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fake = FakeAdapter()
    _run(fake)
    monkeypatch.setattr(
        "ev_pipeline.refresh.plan.find_adapter", lambda s: fake if s == "fake" else None
    )
    assert main(["sources", "check"]) == 0
    out = capsys.readouterr().out
    assert "fake" in out and "ok" in out and "weekly" in out
    assert main(["sources", "check", "--json"]) == 0
    rows = {r["source"]: r for r in json.loads(capsys.readouterr().out)}
    assert rows["fake"]["records"] == 10 and rows["fake"]["status"] == "ok"
    assert rows["nyland"]["due"] == "skip"
    assert main(["refresh", "--dry-run", "--sources", "fake"]) == 0
    assert "would_fetch" in capsys.readouterr().out


def test_adapter_probe_hook(data_dir: Path) -> None:
    fake = FakeAdapter()
    _run(fake)
    calls: list[dict] = []

    def probe_unchanged(client: Any, meta: dict) -> bool:
        calls.append(meta)
        return True

    fake.probe_unchanged = probe_unchanged  # type: ignore[attr-defined]
    deps = _deps(fake, NOW + timedelta(days=8), client_factory=lambda sid: None)
    _, log = refresh(RefreshOptions(release=False), deps)
    assert _status(log)["status"] == "unchanged" and fake.fetches == 1
    assert calls[0]["url"] == f"https://{HOST}/data.csv"

    def broken(client: Any, meta: dict) -> bool:
        raise RuntimeError("x")

    fake.probe_unchanged = broken  # type: ignore[attr-defined]
    _, log = _run(fake, NOW + timedelta(days=16))
    assert _status(log)["status"] == "unchanged" and fake.fetches == 2  # fell back to hash


def test_new_source_without_staging_does_not_block_release(data_dir: Path) -> None:
    fake, other = FakeAdapter(), FakeAdapter("other")
    other.fetch_rc = 1
    (data_dir / "sources.yaml").write_text(
        REGISTRY + "  - {id: other, name: O, licence: CC0-1.0, cadence: weekly, status: active}\n"
    )
    rel = data_dir / "releases" / "1"
    rel.mkdir(parents=True)
    (rel / "catalogue.json").write_text(json.dumps({"release": 1, "sources": [{"id": "fake"}]}))
    (data_dir / "releases" / "latest").write_text("1\n")
    deps = Deps(find=lambda s: {"fake": fake, "other": other}.get(s), now=lambda: NOW)
    _, log = refresh(RefreshOptions(), deps)
    # Guard passed (`other` never shipped); the build itself fails here: no seed in this dir.
    assert log["release"]["outcome"] == "failed" and "seed" in log["release"]["reason"]
