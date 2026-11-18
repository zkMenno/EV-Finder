"""Release QA for car photos (T-134): blocking licence + credit check on generations[].image."""

from __future__ import annotations

from typing import Any

from ev_pipeline.images.photos import licence_allowed
from ev_pipeline.images.store import IMAGES_DIR
from ev_pipeline.qa.checks import Check


def image_problems(catalogue: dict[str, Any]) -> list[str]:
    out: list[str] = []
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
    return out


def check_images(catalogue: dict[str, Any]) -> Check:
    n = sum(1 for g in catalogue.get("generations") or [] if g.get("image"))
    problems = image_problems(catalogue)
    return Check(
        id="images",
        title="Car photos: licence, credit, stored files (Decision 081)",
        blocking=True,
        status="fail" if problems else "pass",
        summary=(f"{len(problems)} problem(s) in {n} photo(s)" if problems else f"{n} photo(s) ok"),
        details={"problems": problems[:50], "generations_with_image": n},
    )
