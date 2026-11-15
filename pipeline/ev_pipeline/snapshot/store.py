"""Raw snapshot store (addendum 6 P1): every raw fetch is kept, content-addressed.

A snapshot is a **manifest** (one JSON per source and change) that lists the files of a raw
folder (`data/raw/<dir>/`) with their sha256 and size, plus the fetch metadata: URL(s),
`fetched_at`, HTTP status, ETag and Last-Modified per response, and the adapter's
`_fetch.json`. File bodies are stored once as **blobs** named by their sha256, so a source
whose files did not change costs nothing, and unchanged files inside a changed tree (an
OpenEV clone) are shared between snapshots.

The content hash of a snapshot covers file paths and file hashes only. `_fetch.json` (it holds
the fetch time), `.git/` and `*.part` files are left out, so fetching the same data twice gives
the same hash.

Backends, chosen by env vars only (no credentials in the repo):

- `SNAPSHOT_BACKEND=local` (default): `$SNAPSHOT_DIR` (default `data/snapshots/`, git-ignored)
  with `objects/<2 hex>/<sha256>` and `<source>/<manifest id>.json`.
- `SNAPSHOT_BACKEND=s3`: S3-compatible object storage (Scaleway later) using `S3_ENDPOINT`,
  `S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET_KEY` and optional `SNAPSHOT_S3_PREFIX`. Same
  interface and layout as the local store. **Not implemented yet**: `S3SnapshotStore` raises a
  clear error; see pipeline/README.md "Keeping data fresh".

Everything streams in 1 MiB chunks: a large registry file is never held in memory.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Protocol

from ev_pipeline.sources import _common as c

CHUNK = 1 << 20
EXCLUDED_NAMES = {c.FETCH_META}
EXCLUDED_DIRS = {".git"}
EXCLUDED_SUFFIXES = (".part",)


class SnapshotError(RuntimeError):
    """The snapshot store is misconfigured or a stored object is missing or corrupt."""


# --- hashing ----------------------------------------------------------------------------


def hash_file(path: Path) -> tuple[str, int]:
    """sha256 hex digest and size of a file, read in chunks."""
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as fh:
        while chunk := fh.read(CHUNK):
            h.update(chunk)
            size += len(chunk)
    return h.hexdigest(), size


def iter_tree(root: Path) -> Iterable[Path]:
    """Files under `root` that belong in a snapshot, in a stable order."""
    if not root.is_dir():
        return
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if not path.is_file() or path.is_symlink():
            continue
        if path.name in EXCLUDED_NAMES or path.name.endswith(EXCLUDED_SUFFIXES):
            continue
        yield path


def scan_tree(root: Path) -> list[dict[str, Any]]:
    out = []
    for path in iter_tree(root):
        sha, size = hash_file(path)
        out.append({"path": path.relative_to(root).as_posix(), "sha256": sha, "bytes": size})
    return out


def content_hash(files: Iterable[dict[str, Any]]) -> str:
    """One hash for a set of files: sha256 over sorted `path NUL sha256 LF` lines."""
    h = hashlib.sha256()
    for f in sorted(files, key=lambda f: f["path"]):
        h.update(f"{f['path']}\0{f['sha256']}\n".encode())
    return "sha256:" + h.hexdigest()


# --- manifests --------------------------------------------------------------------------


@dataclass
class Manifest:
    source: str
    content_hash: str
    fetched_at: str
    files: list[dict[str, Any]]
    bytes: int
    responses: list[dict[str, Any]] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        stamp = self.fetched_at.replace(":", "").replace("-", "").replace("+0000", "Z")
        return f"{stamp}-{self.content_hash.removeprefix('sha256:')[:12]}"

    def to_json(self) -> dict[str, Any]:
        return {"id": self.id, **asdict(self)}

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Manifest:
        return cls(
            source=data["source"],
            content_hash=data["content_hash"],
            fetched_at=data["fetched_at"],
            files=list(data.get("files") or []),
            bytes=int(data.get("bytes") or 0),
            responses=list(data.get("responses") or []),
            meta=dict(data.get("meta") or {}),
        )


class SnapshotStore(Protocol):
    """What every backend provides. Blobs are keyed by sha256 hex; manifests by source."""

    def describe(self) -> str: ...
    def has_blob(self, sha: str) -> bool: ...
    def put_blob(self, sha: str, path: Path) -> None: ...
    def get_blob(self, sha: str, dest: Path) -> None: ...
    def put_manifest(self, manifest: Manifest) -> None: ...
    def manifests(self, source: str) -> list[Manifest]: ...


class LocalSnapshotStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    def describe(self) -> str:
        return f"local:{c.rel(self.root)}"

    def _blob(self, sha: str) -> Path:
        if len(sha) != 64 or any(ch not in "0123456789abcdef" for ch in sha):
            raise SnapshotError(f"not a sha256 hex digest: {sha[:80]!r}")
        return self.root / "objects" / sha[:2] / sha

    def has_blob(self, sha: str) -> bool:
        return self._blob(sha).is_file()

    def put_blob(self, sha: str, path: Path) -> None:
        dest = self._blob(sha)
        if dest.is_file():
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_name(dest.name + f".tmp-{os.getpid()}")
        h = hashlib.sha256()
        with path.open("rb") as src, tmp.open("wb") as out:
            while chunk := src.read(CHUNK):
                h.update(chunk)
                out.write(chunk)
        if h.hexdigest() != sha:
            tmp.unlink(missing_ok=True)
            raise SnapshotError(f"{path.name} changed while it was being stored")
        os.replace(tmp, dest)

    def get_blob(self, sha: str, dest: Path) -> None:
        src = self._blob(sha)
        if not src.is_file():
            raise SnapshotError(f"blob {sha[:12]} is missing from {self.describe()}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)

    def _source_dir(self, source: str) -> Path:
        if not source or "/" in source or source.startswith("."):
            raise SnapshotError(f"bad source id {source!r}")
        return self.root / source

    def put_manifest(self, manifest: Manifest) -> None:
        d = self._source_dir(manifest.source)
        d.mkdir(parents=True, exist_ok=True)
        path = d / f"{manifest.id}.json"
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(manifest.to_json(), indent=1) + "\n", encoding="utf-8")
        os.replace(tmp, path)

    def manifests(self, source: str) -> list[Manifest]:
        d = self._source_dir(source)
        if not d.is_dir():
            return []
        out = [
            Manifest.from_json(json.loads(p.read_text(encoding="utf-8")))
            for p in sorted(d.glob("*.json"))
        ]
        return sorted(out, key=lambda m: m.fetched_at)


class S3SnapshotStore:
    """S3-compatible backend (Scaleway Object Storage). Interface only for now.

    Planned: same layout as LocalSnapshotStore under `SNAPSHOT_S3_PREFIX`, SigV4-signed
    requests through a pinned httpx client (no boto3), credentials from env vars only.
    """

    ENV = ("S3_ENDPOINT", "S3_BUCKET", "S3_ACCESS_KEY", "S3_SECRET_KEY")

    def __init__(self, env: dict[str, str] | None = None) -> None:
        env = dict(os.environ if env is None else env)
        missing = [k for k in self.ENV if not env.get(k)]
        if missing:
            raise SnapshotError(f"SNAPSHOT_BACKEND=s3 needs {', '.join(missing)} (env vars)")
        raise NotImplementedError(
            "The S3 snapshot backend is not built yet. Use SNAPSHOT_BACKEND=local (default) "
            "and copy $SNAPSHOT_DIR to object storage by hand; see pipeline/README.md."
        )


def default_root() -> Path:
    override = os.environ.get("SNAPSHOT_DIR", "").strip()
    return Path(override) if override else c.data_dir() / "snapshots"


def open_store(env: dict[str, str] | None = None) -> SnapshotStore:
    env = dict(os.environ if env is None else env)
    backend = (env.get("SNAPSHOT_BACKEND") or "local").strip().lower()
    if backend == "local":
        root = env.get("SNAPSHOT_DIR", "").strip()
        return LocalSnapshotStore(Path(root) if root else c.data_dir() / "snapshots")
    if backend == "s3":
        return S3SnapshotStore(env)
    raise SnapshotError(f"unknown SNAPSHOT_BACKEND {backend!r} (use local or s3)")


# --- operations -------------------------------------------------------------------------


def latest_manifest(store: SnapshotStore, source: str) -> Manifest | None:
    found = store.manifests(source)
    return found[-1] if found else None


def find_manifest(store: SnapshotStore, source: str, content: str) -> Manifest | None:
    for m in reversed(store.manifests(source)):
        if m.content_hash == content:
            return m
    return None


def take_snapshot(
    store: SnapshotStore,
    source: str,
    raw_dir: Path,
    responses: list[dict[str, Any]] | None = None,
) -> tuple[Manifest, bool]:
    """Store the raw folder of one source. Returns (manifest, is_new_content).

    A manifest is written only when the content hash is new for that source; otherwise the
    existing manifest with that hash is returned (and no blob is copied).
    """
    files = scan_tree(raw_dir)
    if not files:
        raise SnapshotError(f"{source}: nothing to snapshot in {c.rel(raw_dir)}")
    digest = content_hash(files)
    meta = c.read_fetch_meta(raw_dir)
    existing = find_manifest(store, source, digest)
    if existing is not None:
        return existing, False
    for f in files:
        if not store.has_blob(f["sha256"]):
            store.put_blob(f["sha256"], raw_dir / f["path"])
    manifest = Manifest(
        source=source,
        content_hash=digest,
        fetched_at=str(meta.get("fetched_at") or c.now_utc()),
        files=files,
        bytes=sum(int(f["bytes"]) for f in files),
        responses=list(responses or []),
        meta=meta,
    )
    store.put_manifest(manifest)
    return manifest, True


def restore_snapshot(store: SnapshotStore, manifest: Manifest, target: Path) -> None:
    """Rebuild a raw folder from a manifest (written beside `target`, then swapped in)."""
    tmp = target.with_name(target.name + ".restore-tmp")
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    for f in manifest.files:
        rel = Path(f["path"])
        if rel.is_absolute() or ".." in rel.parts:
            shutil.rmtree(tmp, ignore_errors=True)
            raise SnapshotError(f"unsafe path in manifest {manifest.id}")
        store.get_blob(f["sha256"], tmp / rel)
    if manifest.meta:
        (tmp / c.FETCH_META).write_text(
            json.dumps(manifest.meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    if target.exists():
        shutil.rmtree(target)
    tmp.rename(target)
