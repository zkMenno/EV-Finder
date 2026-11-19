"""T-150 / Decision 086: release photos ship as one images.tar asset. No network."""

from __future__ import annotations

import io
import json
import shutil
import tarfile
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from ev_pipeline.images.qa import image_problems
from ev_pipeline.release.publish import (
    DirPublisher,
    PublishError,
    _select,
    ensure_local,
    fetch,
    load_config,
    manifest_paths,
    package,
    read_manifest,
    verify,
)

NOW = datetime(2026, 11, 19, 1, 0, tzinfo=UTC)
REPO = Path(__file__).resolve().parents[2]
PHOTOS = {f"images/g{i}-abcd1234-{w}.webp": bytes([i, w % 256]) * (50 + i) for i in range(3)
          for w in (400, 800)}  # fmt: skip


def _release(root: Path, n: int = 7, photos: dict[str, bytes] = PHOTOS) -> Path:
    d = root / "data" / "releases" / str(n)
    d.mkdir(parents=True)
    gens = [{"id": f"g{i}"} for i in range(3)]
    cat = {"release": n, "generated_at": "2026-11-19T01:00:00+00:00", "sources": [],
           "generations": gens, "rows": [{"variant_id": "v0", "generation_id": "g0"}]}  # fmt: skip
    (d / "catalogue.json").write_text(json.dumps(cat))
    (d / "qa.json").write_text(json.dumps({"status": "pass"}))
    for rel, data in photos.items():
        (d / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / rel).write_bytes(data)
    return d


def test_repo_config_bundles_images() -> None:
    assert load_config(REPO / "data").bundles == (("images/", "images.tar"),)


def test_package_writes_one_bundle_with_every_photo(tmp_path: Path) -> None:
    rel = _release(tmp_path)
    m = package(rel, load_config(tmp_path), now=NOW)
    paths = [e["path"] for e in m["files"]]
    assert "images.tar" in paths
    assert not [p for p in paths if p.startswith("images/")]  # no per-photo assets
    tar = next(e for e in m["files"] if e["path"] == "images.tar")
    assert tar["asset"] == "images.tar" and tar["in_git"] is False
    assert tar["bundle"]["folder"] == "images/"
    assert sorted(x["path"] for x in tar["bundle"]["files"]) == sorted(PHOTOS)
    for x in tar["bundle"]["files"]:
        assert x["bytes"] == len(PHOTOS[x["path"]]) and len(x["sha256"]) == 64
    assert m["counts"]["files"] == len(m["files"])
    with tarfile.open(rel / "images.tar") as t:  # uncompressed, plain files, fixed metadata
        assert t.getnames() == sorted(PHOTOS)
        assert all(i.isfile() and i.mtime == 0 and i.uid == 0 and i.mode == 0o644 for i in t)
    assert verify(rel, m) == []
    assert set(manifest_paths(m)) >= set(PHOTOS) | {"images.tar", "catalogue.json"}


def test_bundle_is_deterministic_and_package_idempotent(tmp_path: Path) -> None:
    a, b = _release(tmp_path / "a"), _release(tmp_path / "b")
    ma = package(a, load_config(tmp_path), now=NOW)
    mb = package(b, load_config(tmp_path), now=datetime(2027, 1, 1, tzinfo=UTC))
    sha = {m["release"]: next(e["sha256"] for e in m["files"] if e["path"] == "images.tar")
           for m in (ma,)}  # fmt: skip
    assert sha[7] == next(e["sha256"] for e in mb["files"] if e["path"] == "images.tar")
    again = package(a, load_config(tmp_path), now=datetime(2027, 1, 1, tzinfo=UTC))
    assert again == ma  # same bytes -> same manifest, packaged_at kept


def test_no_photos_no_bundle(tmp_path: Path) -> None:
    rel = _release(tmp_path, photos={})
    m = package(rel, load_config(tmp_path), now=NOW)
    assert "images.tar" not in [e["path"] for e in m["files"]]


def test_asset_count_drops_like_release_3(tmp_path: Path) -> None:
    """Release 3 shape: 357 photo files -> 1 bundle (646 assets -> about 290)."""
    photos = {f"images/g{i}-{w}.webp": b"x" * (i + 1) for i in range(119) for w in (400, 800, 1600)}
    rel = _release(tmp_path, photos=photos)
    cfg = load_config(tmp_path)
    with_bundle = package(rel, cfg, now=NOW)["counts"]["files"]
    shutil.rmtree(rel)
    rel = _release(tmp_path, photos=photos)
    without = package(rel, replace(cfg, bundles=()), now=NOW)["counts"]["files"]
    assert without - with_bundle == len(photos) - 1


def _store(m: dict[str, Any], rel: Path, store: Path) -> Any:
    DirPublisher(store).publish(rel, m, replace=False)
    tag = store / m["storage"]["tag"]

    def dl(url: str, dest: Path, max_bytes: int) -> None:
        dest.write_bytes((tag / url.rsplit("/", 1)[1]).read_bytes())

    return dl


def _strip(rel: Path, m: dict[str, Any]) -> None:
    for e in m["files"]:
        if not e["in_git"]:
            (rel / e["path"]).unlink()
    shutil.rmtree(rel / "images")


def test_fetch_downloads_checks_and_unpacks_the_bundle(tmp_path: Path) -> None:
    rel = _release(tmp_path)
    cfg = load_config(tmp_path)
    m = package(rel, cfg, now=NOW)
    dl = _store(m, rel, tmp_path / "store")
    assert not (tmp_path / "store" / "data-v7" / "images.g0-abcd1234-400.webp").exists()
    _strip(rel, m)
    stats = fetch(rel, cfg, download=dl)
    assert stats["unpacked"] == 1
    for p, data in PHOTOS.items():
        assert (rel / p).read_bytes() == data
    assert verify(rel, m) == []
    # a photo lost after the fetch: the next fetch unpacks again without downloading
    (rel / next(iter(PHOTOS))).unlink()
    again = fetch(rel, cfg, download=dl)
    assert again["downloaded"] == 0 and again["unpacked"] == 1 and verify(rel, m) == []


def test_ensure_local_only_images_picks_the_bundle(tmp_path: Path) -> None:
    rel = _release(tmp_path)
    cfg = load_config(tmp_path)
    m = package(rel, cfg, now=NOW)
    assert [e["path"] for e in _select(m["files"], frozenset({"images/"}))] == ["images.tar"]
    one = next(iter(PHOTOS))
    assert [e["path"] for e in _select(m["files"], frozenset({one}))] == ["images.tar"]
    dl = _store(m, rel, tmp_path / "store")
    _strip(rel, m)
    ensure_local(tmp_path / "data", 7, download=dl, only=frozenset({"images/"}))
    assert (rel / one).read_bytes() == PHOTOS[one]


def _tamper_tar(rel: Path, m: dict[str, Any], members: dict[str, bytes]) -> None:
    """Rewrite images.tar with other members and point the manifest's tar entry at it."""
    import hashlib

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as t:
        for name, data in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            t.addfile(info, io.BytesIO(data))
    (rel / "images.tar").write_bytes(buf.getvalue())
    e = next(e for e in m["files"] if e["path"] == "images.tar")
    e["bytes"], e["sha256"] = len(buf.getvalue()), hashlib.sha256(buf.getvalue()).hexdigest()
    (rel / "manifest.json").write_text(json.dumps(m))


@pytest.mark.parametrize(
    ("members", "why"),
    [
        ({**PHOTOS, "images/../../evil.webp": b"x"}, "unexpected member"),
        ({**PHOTOS, "images/extra.webp": b"x"}, "unexpected member"),
        ({k: (b"changed" if i == 0 else v) for i, (k, v) in enumerate(PHOTOS.items())},
         "does not match"),
        (dict(list(PHOTOS.items())[1:]), "members missing"),
    ],
)  # fmt: skip
def test_bad_bundle_is_refused(tmp_path: Path, members: dict[str, bytes], why: str) -> None:
    rel = _release(tmp_path)
    cfg = load_config(tmp_path)
    m = package(rel, cfg, now=NOW)
    shutil.rmtree(rel / "images")
    _tamper_tar(rel, m, members)
    with pytest.raises(PublishError, match=why):
        fetch(rel, cfg, download=lambda *_a: None)
    assert not (tmp_path / "data" / "evil.webp").exists()


@pytest.mark.parametrize("bad", ["/etc/x", "images/../x", "other/x.webp", "images\\x"])
def test_manifest_with_unsafe_bundle_member_is_refused(tmp_path: Path, bad: str) -> None:
    rel = _release(tmp_path)
    m = package(rel, load_config(tmp_path), now=NOW)
    next(e for e in m["files"] if e["path"] == "images.tar")["bundle"]["files"][0]["path"] = bad
    (rel / "manifest.json").write_text(json.dumps(m))
    with pytest.raises(PublishError, match="unsafe bundle member"):
        read_manifest(rel)


def test_release_without_bundle_still_fetches_the_old_way(tmp_path: Path) -> None:
    """Releases 1-3: photos are separate assets; the bundle config changes nothing for them."""
    rel = _release(tmp_path)
    cfg = load_config(tmp_path)
    m = package(rel, replace(cfg, bundles=()), now=NOW)
    assert all("bundle" not in e for e in m["files"])
    assert sum(e["path"].startswith("images/") for e in m["files"]) == len(PHOTOS)
    dl = _store(m, rel, tmp_path / "store")
    for e in m["files"]:
        if not e["in_git"]:
            (rel / e["path"]).unlink()
    stats = fetch(rel, cfg, download=dl)  # repo config (with bundles) on an old manifest
    assert "unpacked" not in stats and verify(rel, m) == []
    assert (rel / next(iter(PHOTOS))).exists()


def test_image_qa_finds_photos_inside_the_bundle(tmp_path: Path) -> None:
    rel = _release(tmp_path)
    package(rel, load_config(tmp_path), now=NOW)
    m = read_manifest(rel)
    assert m is not None
    member = next(x for e in m["files"] for x in (e.get("bundle") or {}).get("files") or [])
    img = {"source": "press", "licence": "press-terms", "credit": "Photo: X",
           "page_url": "https://x.example/p", "retrieved_at": "2026-11-18",
           "files": [{"width": 400, "path": member["path"], "bytes": member["bytes"],
                      "sha256": member["sha256"]}]}  # fmt: skip
    cat = {"release": 7, "generations": [{"id": "g0", "image": img}]}
    assert image_problems(cat, rel) == []
    img["files"][0]["sha256"] = "0" * 64
    assert any("differ" in p for p in image_problems(cat, rel))


def test_repackaging_an_old_release_keeps_its_manifest(tmp_path: Path) -> None:
    """#173 review: releases 1-3 (no bundle) keep their layout and order when re-packaged."""
    rel = _release(tmp_path)
    cfg = load_config(tmp_path)
    old = package(rel, replace(cfg, bundles=()), now=NOW)
    again = package(rel, cfg, now=datetime(2027, 1, 1, tzinfo=UTC))
    assert again == old and not (rel / "images.tar").exists()


def test_bad_bundle_config_is_a_publish_error() -> None:
    from ev_pipeline.release.publish import _bundles

    for raw in (["images/"], [{"folder": "a/b/", "path": "x.tar"}], [{"folder": "images/",
                "path": "x.zip"}]):  # fmt: skip
        with pytest.raises(PublishError):
            _bundles(raw)
