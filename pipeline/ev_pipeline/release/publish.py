"""Releases out of git (Decision 035, T-064): package, publish, fetch, verify.

A release folder `data/releases/<n>/` is built as before by `ev release`. Then:

- `package`  splits the catalogue per generation (index + one file per generation) and writes
  `manifest.json`: number, dates, QA summary, storage location, and every file with its size
  and sha256. Deterministic: packaging the same catalogue twice gives the same bytes.
- `publish`  uploads every file as an asset of the GitHub Release `data-v<n>` (or copies it to
  a directory, for tests and local mirrors). An existing tag is only reused when its assets
  already match the manifest; it is replaced only when no manifest for <n> is committed yet
  (an unmerged "Data release N" PR), so a merged release can never change under its manifest.
- `fetch`    downloads the files git doesn't hold into the release folder and checks size and
  sha256 against the manifest; a mismatch is an error, never a silent fallback.

Git keeps `manifest.json` plus the small files in `publish.yaml: in_git`. Rollback stays
"point `latest` at an earlier release": the manifest says where its files are.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

MANIFEST = "manifest.json"
MANIFEST_SCHEMA = "ev-release-manifest/1"
CONFIG_FILE = "publish.yaml"


class PublishError(RuntimeError):
    pass


# --- config ------------------------------------------------------------------------------


@dataclass(frozen=True)
class PublishConfig:
    target: str
    repo: str
    tag_pattern: str
    download_url: str
    download_hosts: tuple[str, ...]
    in_git: frozenset[str]
    index_path: str
    generation_path: str
    detail_only_keys: tuple[str, ...]
    max_file_bytes: int

    def tag(self, n: int) -> str:
        return self.tag_pattern.format(n=n)

    def asset_url(self, n: int, asset: str) -> str:
        return self.download_url.format(repo=self.repo, tag=self.tag(n), asset=asset)


def load_config(data_dir: Path) -> PublishConfig:
    path = data_dir / "releases" / CONFIG_FILE
    if not path.exists():  # a scratch data dir (tests, temp machine) uses the repo's config
        path = Path(__file__).resolve().parents[3] / "data" / "releases" / CONFIG_FILE
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except OSError as e:
        raise PublishError(f"{path}: cannot read publish config ({e})") from e
    gh = doc.get("github") or {}
    split = doc.get("split") or {}
    try:
        return PublishConfig(
            target=str(doc["target"]),
            repo=str(gh["repo"]),
            tag_pattern=str(gh["tag"]),
            download_url=str(gh["download_url"]),
            download_hosts=tuple(str(h) for h in gh.get("download_hosts") or ()),
            in_git=frozenset(str(f) for f in doc.get("in_git") or ()),
            index_path=str(split["index"]),
            generation_path=str(split["generation"]),
            detail_only_keys=tuple(str(k) for k in split.get("row_keys_detail_only") or ()),
            max_file_bytes=int(doc.get("max_file_bytes") or 200_000_000),
        )
    except KeyError as e:
        raise PublishError(f"{path}: missing key {e}") from e


# --- split -------------------------------------------------------------------------------


def _json_bytes(doc: Any) -> bytes:
    return (
        json.dumps(doc, separators=(",", ":"), ensure_ascii=False, sort_keys=True) + "\n"
    ).encode("utf-8")


def _safe_id(gid: str) -> str:
    if not gid or "/" in gid or "\\" in gid or gid.startswith(".") or ".." in gid:
        raise PublishError(f"generation id not usable as a file name: {gid!r}")
    return gid


def split_catalogue(cat: dict[str, Any], cfg: PublishConfig) -> dict[str, bytes]:
    """catalogue.json -> {relative path: bytes}: one index and one file per generation.

    Index: everything in the catalogue, but rows without the detail-only keys (provenance)
    and known issues without the per-generation breakdown. Each generation file: that
    generation, its full rows (with provenance) and its known issues. Every generation in
    `generations` gets a file, also one without rows (its page still renders)."""
    rows = cat.get("rows") or []
    drop = set(cfg.detail_only_keys)
    index = {k: v for k, v in cat.items() if k not in ("rows", "known_issues")}
    index["rows"] = [{k: v for k, v in r.items() if k not in drop} for r in rows]
    ki = cat.get("known_issues")
    by_gen: dict[str, Any] = {}
    if isinstance(ki, dict):
        by_gen = ki.get("by_generation") or {}
        index["known_issues"] = {k: v for k, v in ki.items() if k != "by_generation"}
    elif ki is not None:
        index["known_issues"] = ki
    rows_by_gen: dict[str, list[dict[str, Any]]] = {}
    for r in rows:
        rows_by_gen.setdefault(str(r["generation_id"]), []).append(r)
    gen_ids = [str(g["id"]) for g in cat.get("generations") or []]
    for gid in rows_by_gen:
        if gid not in gen_ids:
            gen_ids.append(gid)  # a row whose generation isn't listed still gets its file
    index["generation_files"] = {
        gid: cfg.generation_path.format(generation_id=_safe_id(gid)) for gid in sorted(gen_ids)
    }
    out: dict[str, bytes] = {cfg.index_path: _json_bytes(index)}
    gens = {str(g["id"]): g for g in cat.get("generations") or []}
    for gid in sorted(gen_ids):
        doc = {
            "release": cat.get("release"),
            "generated_at": cat.get("generated_at"),
            "generation": gens.get(gid),
            "rows": rows_by_gen.get(gid, []),
            "known_issues": by_gen.get(gid),
        }
        out[index["generation_files"][gid]] = _json_bytes(doc)
    return out


def join_split(files: dict[str, bytes], cfg: PublishConfig) -> dict[str, Any]:
    """Inverse of split_catalogue (tests and the round-trip check in `package`)."""
    index = json.loads(files[cfg.index_path])
    gen_files = index.pop("generation_files")
    detail: dict[str, dict[str, Any]] = {}
    by_gen: dict[str, Any] = {}
    for gid, path in gen_files.items():
        doc = json.loads(files[path])
        for r in doc["rows"]:
            detail[r["variant_id"]] = r
        if doc.get("known_issues") is not None:
            by_gen[gid] = doc["known_issues"]
    cat = dict(index)
    cat["rows"] = [detail[r["variant_id"]] for r in index["rows"]]
    if isinstance(index.get("known_issues"), dict) and by_gen:
        cat["known_issues"] = {**index["known_issues"], "by_generation": by_gen}
    return cat


# --- manifest ----------------------------------------------------------------------------


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def asset_name(rel_path: str) -> str:
    """Release assets are flat: `catalogue/generations/x.json` -> `catalogue.generations.x.json`."""
    return rel_path.replace("/", ".")


def _release_files(release_dir: Path) -> list[str]:
    out = []
    for p in sorted(release_dir.rglob("*")):
        if p.is_symlink():
            raise PublishError(f"symlink in release folder: {p}")
        if not p.is_file():
            continue
        rel = p.relative_to(release_dir).as_posix()
        if rel == MANIFEST or any(part.startswith(".") for part in rel.split("/")):
            continue
        out.append(rel)
    return out


def _qa_summary(release_dir: Path) -> dict[str, Any]:
    path = release_dir / "qa.json"
    try:
        qa = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"status": "missing"}
    out: dict[str, Any] = {"status": qa.get("status") or "unknown"}
    for key in ("blocking_failures", "warnings"):
        if key in qa:
            v = qa[key]
            out[key] = len(v) if isinstance(v, list | dict) else v
    return out


def package(
    release_dir: Path, cfg: PublishConfig, *, now: datetime | None = None
) -> dict[str, Any]:
    """Write the per-generation split and manifest.json into a built release folder."""
    cat_path = release_dir / "catalogue.json"
    if not cat_path.exists():
        raise PublishError(f"{release_dir}: no catalogue.json to package")
    cat = json.loads(cat_path.read_text(encoding="utf-8"))
    n = int(cat["release"])
    if release_dir.name.isdigit() and release_dir.name != str(n):
        raise PublishError(f"{release_dir} holds release {n}; folder name must match")
    files = split_catalogue(cat, cfg)
    if join_split(files, cfg) != cat:  # never publish a split the web can't put back together
        raise PublishError("per-generation split does not round-trip to catalogue.json")
    split_root = release_dir / Path(cfg.index_path).parts[0]
    if split_root.exists():
        shutil.rmtree(split_root)
    for rel, data in files.items():
        p = release_dir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    entries = []
    names: set[str] = set()
    for rel in _release_files(release_dir):
        p = release_dir / rel
        name = asset_name(rel)
        if name in names:
            raise PublishError(f"two files map to the same asset name {name!r}")
        names.add(name)
        entries.append(
            {
                "path": rel,
                "asset": name,
                "bytes": p.stat().st_size,
                "sha256": sha256_file(p),
                "in_git": rel in cfg.in_git,
            }
        )
    previous = read_manifest(release_dir)
    packaged_at = (now or datetime.now(UTC)).replace(microsecond=0).isoformat()
    if previous and previous.get("files") == entries:
        packaged_at = previous.get("packaged_at", packaged_at)  # idempotent: same bytes, same file
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "release": n,
        "generated_at": cat.get("generated_at"),
        "packaged_at": packaged_at,
        "storage": {
            "kind": cfg.target,
            "repo": cfg.repo,
            "tag": cfg.tag(n),
            "download_url": cfg.download_url.replace("{repo}", cfg.repo).replace(
                "{tag}", cfg.tag(n)
            ),
        },
        "counts": {
            "rows": len(cat.get("rows") or []),
            "generations": len(cat.get("generations") or []),
            "files": len(entries),
            "bytes": sum(e["bytes"] for e in entries),
        },
        "qa": _qa_summary(release_dir),
        "split": {"index": cfg.index_path, "generation": cfg.generation_path},
        "files": entries,
    }
    write_manifest(release_dir, manifest)
    return manifest


def write_manifest(release_dir: Path, manifest: dict[str, Any]) -> None:
    tmp = release_dir / f".{MANIFEST}.tmp-{os.getpid()}"
    tmp.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, release_dir / MANIFEST)


def read_manifest(release_dir: Path) -> dict[str, Any] | None:
    path = release_dir / MANIFEST
    if not path.exists():
        return None
    try:
        m = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise PublishError(f"{path}: not valid JSON ({e})") from e
    if m.get("schema") != MANIFEST_SCHEMA:
        raise PublishError(f"{path}: unknown manifest schema {m.get('schema')!r}")
    for e in m.get("files") or []:
        rel = str(e.get("path", ""))
        if not rel or rel.startswith("/") or ".." in rel.split("/") or "\\" in rel:
            raise PublishError(f"{path}: unsafe file path {rel!r}")
    return m


def verify(release_dir: Path, manifest: dict[str, Any], *, only_present: bool = False) -> list[str]:
    """Problems with the local files against the manifest (empty list = all good)."""
    problems = []
    for e in manifest["files"]:
        p = release_dir / e["path"]
        if not p.exists():
            if not only_present:
                problems.append(f"{e['path']}: missing")
            continue
        if p.stat().st_size != e["bytes"]:
            problems.append(f"{e['path']}: {p.stat().st_size} bytes, manifest says {e['bytes']}")
        elif sha256_file(p) != e["sha256"]:
            problems.append(f"{e['path']}: sha256 mismatch")
    return problems


# --- publishers --------------------------------------------------------------------------

Runner = Callable[[list[str]], subprocess.CompletedProcess[str]]


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, check=False)


@dataclass
class DirPublisher:
    """Copies assets flat into <root>/<tag>/ (tests, local mirror, an rsync'd bucket)."""

    root: Path

    def publish(self, release_dir: Path, manifest: dict[str, Any], *, replace: bool) -> str:
        dest = self.root / manifest["storage"]["tag"]
        if dest.exists():
            same = all(
                (dest / e["asset"]).exists() and sha256_file(dest / e["asset"]) == e["sha256"]
                for e in manifest["files"]
            )
            if same:
                return "unchanged"
            if not replace:
                raise PublishError(f"{dest} exists with different files; refusing to overwrite")
            shutil.rmtree(dest)
        dest.mkdir(parents=True)
        for e in manifest["files"]:
            shutil.copyfile(release_dir / e["path"], dest / e["asset"])
        return "published"


@dataclass
class GithubPublisher:
    """GitHub Release assets through the GitHub CLI (`gh`, preinstalled on Actions runners;
    auth from GH_TOKEN). Assets of an existing tag are compared by name and size, and by
    sha256 where GitHub reports a digest."""

    repo: str
    run: Runner = field(default=_run)

    def _assets(self, tag: str) -> dict[str, dict[str, Any]] | None:
        cp = self.run(["gh", "release", "view", tag, "--repo", self.repo, "--json", "assets"])
        if cp.returncode != 0:
            if "not found" in (cp.stderr or "").lower():
                return None
            raise PublishError(f"gh release view {tag} failed: {cp.stderr.strip()}")
        return {a["name"]: a for a in json.loads(cp.stdout or "{}").get("assets") or []}

    @staticmethod
    def _matches(assets: dict[str, dict[str, Any]], manifest: dict[str, Any]) -> bool:
        if set(assets) != {e["asset"] for e in manifest["files"]}:
            return False
        for e in manifest["files"]:
            a = assets[e["asset"]]
            if int(a.get("size", -1)) != e["bytes"]:
                return False
            digest = a.get("digest")
            if digest and digest != f"sha256:{e['sha256']}":
                return False
        return True

    def publish(self, release_dir: Path, manifest: dict[str, Any], *, replace: bool) -> str:
        tag = manifest["storage"]["tag"]
        assets = self._assets(tag)
        if assets is not None:
            if self._matches(assets, manifest):
                return "unchanged"
            if not replace:
                raise PublishError(
                    f"release {tag} exists with different assets; a published release never "
                    "changes (re-run with --replace only for an unmerged release)"
                )
            cp = self.run(["gh", "release", "delete", tag, "--repo", self.repo, "--yes",
                           "--cleanup-tag"])  # fmt: skip
            if cp.returncode != 0:
                raise PublishError(f"gh release delete {tag} failed: {cp.stderr.strip()}")
        with tempfile.TemporaryDirectory() as tmp:
            # Flat copies named like the assets (gh takes the file name as the asset name).
            paths = []
            for e in manifest["files"]:
                dst = Path(tmp) / e["asset"]
                shutil.copyfile(release_dir / e["path"], dst)
                paths.append(str(dst))
            notes = Path(tmp) / ".notes.md"
            notes.write_text(_release_notes(manifest), encoding="utf-8")
            cp = self.run(
                ["gh", "release", "create", tag, "--repo", self.repo, "--title",
                 f"Data release {manifest['release']}", "--notes-file", str(notes),
                 "--latest=false", *paths]
            )  # fmt: skip
            if cp.returncode != 0:
                raise PublishError(f"gh release create {tag} failed: {cp.stderr.strip()}")
        after = self._assets(tag)
        if after is None or not self._matches(after, manifest):
            raise PublishError(f"release {tag} was created but its assets don't match the manifest")
        return "published"


def _release_notes(m: dict[str, Any]) -> str:
    return (
        f"EV Finder catalogue data release {m['release']} (generated {m['generated_at']}).\n\n"
        f"{m['counts']['rows']} variants, {m['counts']['files']} files, QA {m['qa']['status']}.\n"
        "Files and sha256 checksums: `data/releases/"
        f"{m['release']}/manifest.json` in the repo. Data licence: CC BY 4.0 for our own "
        "output; third-party inputs keep their licences (see README.md and open/ATTRIBUTION.md)."
        "\n"
    )


def publisher_for(cfg: PublishConfig, *, target: str | None = None, out_dir: Path | None = None):
    kind = target or cfg.target
    if kind == "github":
        return GithubPublisher(cfg.repo)
    if kind == "dir":
        if out_dir is None:
            raise PublishError("target 'dir' needs --out")
        return DirPublisher(out_dir)
    raise PublishError(f"unknown publish target {kind!r} (s3 arrives with WS4 object storage)")


# --- fetch -------------------------------------------------------------------------------

Downloader = Callable[[str, Path, int], None]
"""(url, destination file, max bytes) -> writes the file or raises."""


def http_downloader(cfg: PublishConfig, *, transport: Any = None) -> Downloader:
    from ev_pipeline.net import safe_client

    def download(url: str, dest: Path, max_bytes: int) -> None:
        with safe_client(
            "release-assets", hosts=cfg.download_hosts, max_bytes=max_bytes,
            max_seconds=600, transport=transport,
        ) as client, client.stream("GET", url) as resp:  # fmt: skip
            resp.raise_for_status()
            with dest.open("wb") as fh:
                for chunk in resp.iter_bytes():
                    fh.write(chunk)

    return download


def fetch(
    release_dir: Path,
    cfg: PublishConfig,
    *,
    download: Downloader | None = None,
    include_in_git: bool = False,
    only: frozenset[str] | None = None,
) -> dict[str, int]:
    """Download the files git doesn't hold into release_dir, verified against the manifest.

    Files already present with the right sha256 are kept. A wrong download is deleted and
    raises PublishError; the release folder never ends up with an unverified file. `only`:
    fetch just these paths (a path ending in "/" means everything under it)."""
    manifest = read_manifest(release_dir)
    if manifest is None:
        raise PublishError(f"{release_dir}: no {MANIFEST}")
    dl = download or http_downloader(cfg)
    n = int(manifest["release"])
    base = manifest["storage"].get("download_url")
    stats = {"kept": 0, "downloaded": 0}
    for e in _select(manifest["files"], only):
        if e["in_git"] and not include_in_git and (release_dir / e["path"]).exists():
            stats["kept"] += 1
            continue
        dest = release_dir / e["path"]
        if dest.exists() and dest.stat().st_size == e["bytes"] and sha256_file(dest) == e["sha256"]:
            stats["kept"] += 1
            continue
        if e["bytes"] > cfg.max_file_bytes:
            raise PublishError(f"{e['path']}: {e['bytes']} bytes is over max_file_bytes")
        url = base.replace("{asset}", e["asset"]) if base else cfg.asset_url(n, e["asset"])
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_name(f".{dest.name}.part-{os.getpid()}")
        try:
            dl(url, tmp, e["bytes"])
            size = tmp.stat().st_size
            if size != e["bytes"] or sha256_file(tmp) != e["sha256"]:
                raise PublishError(f"{e['path']}: download does not match the manifest checksum")
            os.replace(tmp, dest)
        finally:
            tmp.unlink(missing_ok=True)
        stats["downloaded"] += 1
    return stats


def _select(
    files: list[dict[str, Any]], only: frozenset[str] | None, *, strict: bool = True
) -> list[dict[str, Any]]:
    if only is None:
        return files
    picked = [
        e for e in files
        if e["path"] in only or any(o.endswith("/") and e["path"].startswith(o) for o in only)
    ]  # fmt: skip
    missing = {o for o in only if not o.endswith("/")} - {e["path"] for e in files}
    if missing and strict:
        raise PublishError(f"not in the manifest: {', '.join(sorted(missing))}")
    return picked


def ensure_local(
    data_dir: Path,
    n: int,
    *,
    download: Downloader | None = None,
    only: frozenset[str] | None = None,
) -> Path:
    """Release n's files on disk (fetched by manifest if needed); for diff, rollback, QA.
    `only`: just these paths (see `fetch`); default every file."""
    release_dir = data_dir / "releases" / str(n)
    if (release_dir / "catalogue.json").exists() and read_manifest(release_dir) is None:
        return release_dir  # a release from before T-064, fully in git
    m = read_manifest(release_dir)
    if m is None:
        raise PublishError(f"release {n}: neither catalogue.json nor {MANIFEST} found")
    # Files git holds are trusted as committed; the asset files must match their checksums.
    # Only missing files are downloaded: a present file with a wrong checksum is an error.
    picked = _select(m["files"], only, strict=False)  # optional files may be absent
    assets = {**m, "files": [e for e in picked if not e["in_git"]]}
    problems = verify(release_dir, assets, only_present=True)
    if not problems and verify(release_dir, assets):
        fetch(
            release_dir,
            load_config(data_dir),
            download=download,
            only=frozenset(e["path"] for e in picked) if only is not None else None,
        )
    problems = problems or verify(release_dir, assets)
    if problems:
        raise PublishError(f"release {n}: " + "; ".join(problems[:5]))
    return release_dir


def committed_in_git(repo_root: Path, release_dir: Path, ref: str = "origin/main") -> bool:
    """True when `ref` already holds a manifest for this release (then it's immutable)."""
    rel = (release_dir / MANIFEST).resolve().relative_to(repo_root.resolve()).as_posix()
    cp = subprocess.run(
        ["git", "-C", str(repo_root), "cat-file", "-e", f"{ref}:{rel}"],
        capture_output=True, text=True, check=False,
    )  # fmt: skip
    return cp.returncode == 0


def local_catalogue(data_dir: Path, n: int, *, download: Downloader | None = None) -> Path | None:
    """Path of release n's catalogue.json, fetched by manifest when it isn't on disk.
    None when release n has neither (no such release). Raises PublishError when the
    manifest exists but the files can't be fetched: callers never treat that as "no release"."""
    release_dir = data_dir / "releases" / str(n)
    path = release_dir / "catalogue.json"
    if path.exists():
        return path
    if not (release_dir / MANIFEST).exists():
        return None
    ensure_local(data_dir, n, download=download, only=frozenset({"catalogue.json"}))
    return path
