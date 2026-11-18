"""Release QA for car photos (T-134): blocking licence + credit check on generations[].image."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ev_pipeline.images.photos import licence_allowed
from ev_pipeline.images.store import IMAGES_DIR
from ev_pipeline.qa.checks import Check


def _stored_files(release_dir: Path) -> dict[str, dict[str, Any]] | None:
    """path -> manifest entry, or None when the release has no manifest yet (not packaged)."""
    m = release_dir / "manifest.json"
    if not m.exists():
        return None
    doc = json.loads(m.read_text(encoding="utf-8"))
    return {str(f.get("path")): f for f in doc.get("files") or []}


def _file_problem(release_dir: Path, manifest: dict[str, Any] | None, f: dict[str, Any]) -> str:
    """'' when the stored file matches the field's sha256 + bytes (#110 review nit)."""
    path, sha, size = str(f.get("path") or ""), f.get("sha256"), f.get("bytes")
    if manifest is not None:
        entry = manifest.get(path)
        if entry is None:
            return f"file {path} is not in manifest.json"
        if entry.get("sha256") != sha or entry.get("bytes") != size:
            return f"file {path}: manifest sha256/bytes differ from the image field"
        return ""
    local = release_dir / path
    if not local.is_file():
        return f"file {path} is missing from the release folder"
    data = local.read_bytes()
    if hashlib.sha256(data).hexdigest() != sha or len(data) != size:
        return f"file {path}: sha256/bytes differ from the image field"
    return ""


def image_problems(catalogue: dict[str, Any], release_dir: Path | None = None) -> list[str]:
    """Licence, credit and path rules; with `release_dir`, also that each file is stored
    there (manifest.json entry, or the local file before packaging) with the same sha256."""
    out: list[str] = []
    manifest = _stored_files(release_dir) if release_dir is not None else None
    for g in catalogue.get("generations") or []:
        img = g.get("image")
        if img is None:
            continue
        gid = g.get("id", "?")
        if not licence_allowed(str(img.get("source")), str(img.get("licence"))):
            out.append(
                f"{gid}: licence {img.get('licence')!r} not allowed for {img.get('source')!r}"
            )
        if not str(img.get("credit") or "").strip():
            out.append(f"{gid}: no credit line")
        if not img.get("page_url") or not img.get("retrieved_at"):
            out.append(f"{gid}: source URL or retrieval date missing")
        files = img.get("files") or []
        if not files:
            out.append(f"{gid}: no image files")
        for f in files:
            path = str(f.get("path") or "")
            if not path.startswith(f"{IMAGES_DIR}/") or ".." in path or "://" in path:
                out.append(f"{gid}: file path {path!r} is not a stored release file (no hotlinks)")
            elif release_dir is not None and (why := _file_problem(release_dir, manifest, f)):
                out.append(f"{gid}: {why}")
    return out


def check_images(catalogue: dict[str, Any], release_dir: Path | None = None) -> Check:
    n = sum(1 for g in catalogue.get("generations") or [] if g.get("image"))
    problems = image_problems(catalogue, release_dir)
    return Check(
        id="images",
        title="Car photos: licence, credit, stored files (Decision 081)",
        blocking=True,
        status="fail" if problems else "pass",
        summary=(f"{len(problems)} problem(s) in {n} photo(s)" if problems else f"{n} photo(s) ok"),
        details={"problems": problems[:50], "generations_with_image": n},
    )
