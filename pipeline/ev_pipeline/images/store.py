"""Fetch each photo once into data/cache/images/, then resize to WebP for a release."""

from __future__ import annotations

import hashlib
import io
import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from ev_pipeline import net
from ev_pipeline.images.photos import SOURCE_ID, Photo

CACHE_DIR = Path("cache") / "images"
WIDTHS = (400, 800, 1600)
WEBP_QUALITY = 80
MAX_ORIGINAL_BYTES = 30_000_000
MAX_PIXELS = 60_000_000
"""Pillow decompression-bomb guard: refuse originals bigger than this many pixels."""
FETCH_SLEEP_S = 1.0
IMAGES_DIR = "images"

ClientFactory = Callable[[str], httpx.Client]


def cache_key(file_url: str) -> str:
    return hashlib.sha256(file_url.encode("utf-8")).hexdigest()


def cached_original(cache: Path, photo: Photo) -> Path | None:
    p = cache / f"{cache_key(photo.file_url)}.bin"
    return p if p.exists() else None


@dataclass
class FetchReport:
    fetched: list[str]
    cached: list[str]
    failed: dict[str, str]
    stopped: str | None = None

    def log(self) -> dict[str, Any]:
        return {
            "stopped": self.stopped,
            "fetched": len(self.fetched),
            "already_cached": len(self.cached),
            "failed": dict(sorted(self.failed.items())),
        }


USER_AGENT = (
    "ev-finder-pipeline/0.1 (https://github.com/zkMenno/EV-Shortlist; car photos, fetched once)"
)
"""Wikimedia's User-Agent policy asks bots for a name and a contact URL."""


class RateLimited(Exception):
    """The host answered 429: stop this run instead of hammering the remaining URLs."""


def _default_client(source_id: str) -> httpx.Client:
    client = net.safe_client(source_id, max_bytes=MAX_ORIGINAL_BYTES)
    client.headers["User-Agent"] = USER_AGENT
    return client


def fetch_originals(
    photos: list[Photo],
    cache: Path,
    client_for: ClientFactory = _default_client,
    sleep: Callable[[float], None] = time.sleep,
) -> FetchReport:
    """Download every photo not yet in the cache, one at a time. Never re-fetches."""
    cache.mkdir(parents=True, exist_ok=True)
    rep = FetchReport([], [], {})
    clients: dict[str, httpx.Client] = {}
    try:
        for ph in photos:
            if cached_original(cache, ph) is not None:
                rep.cached.append(ph.generation_id)
                continue
            sid = SOURCE_ID[ph.source]
            try:
                client = clients.get(sid) or clients.setdefault(sid, client_for(sid))
                r = client.get(ph.file_url)
                if r.status_code == 429:
                    raise RateLimited(
                        f"429 from {r.url.host}, retry-after {r.headers.get('retry-after', '?')} s"
                    )
                r.raise_for_status()
                ctype = r.headers.get("content-type", "").split(";")[0].strip()
                if not ctype.startswith("image/"):
                    raise ValueError(f"not an image ({ctype or 'no content type'})")
                body = r.content
            except RateLimited as e:
                # stop: everything not yet fetched waits for the next run
                for rest in photos[photos.index(ph) :]:
                    if cached_original(cache, rest) is None:
                        rep.failed[rest.generation_id] = f"RateLimited: {e}"
                rep.stopped = str(e)
                break
            except (httpx.HTTPError, ValueError) as e:
                # net.py errors name only the host or the reason, never the full URL
                rep.failed[ph.generation_id] = type(e).__name__ + ": " + str(e)[:200]
                sleep(FETCH_SLEEP_S)
                continue
            key = cache_key(ph.file_url)
            tmp = cache / f"{key}.bin.part"
            tmp.write_bytes(body)
            tmp.replace(cache / f"{key}.bin")
            meta = {
                "file_url": ph.file_url,
                "bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest(),
                "content_type": ctype,
                "fetched_at": datetime.now(UTC).isoformat(timespec="seconds"),
            }
            (cache / f"{key}.json").write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
            rep.fetched.append(ph.generation_id)
            sleep(FETCH_SLEEP_S)
    finally:
        for c in clients.values():
            c.close()
    return rep


def _flatten(img: Any) -> Any:
    """RGB for WebP. PNG / GIF / WebP with alpha (RGBA, LA, P + transparency) go onto white,
    so transparent areas don't turn black (Decision 083 brought the first PNG pick)."""
    from PIL import Image

    if img.mode == "P" and "transparency" in img.info:
        img = img.convert("RGBA")
    if img.mode in ("RGBA", "LA", "PA"):
        rgba = img.convert("RGBA")
        bg = Image.new("RGB", rgba.size, (255, 255, 255))
        bg.paste(rgba, mask=rgba.getchannel("A"))
        return bg
    return img.convert("RGB")


def render_sizes(original: bytes, generation_id: str) -> dict[str, bytes]:
    """Release-relative path -> WebP bytes for each width <= the original's width.

    Never upscaled; an original narrower than the smallest width gives one file at its own
    width. Paths carry a short content hash so a changed photo gets a new URL. Metadata
    (EXIF, GPS) is dropped: Pillow writes none unless asked.
    """
    from PIL import Image, ImageOps

    Image.MAX_IMAGE_PIXELS = MAX_PIXELS
    with Image.open(io.BytesIO(original)) as im:
        im.load()
        img = _flatten(ImageOps.exif_transpose(im))
    sha8 = hashlib.sha256(original).hexdigest()[:8]
    widths = [w for w in WIDTHS if w <= img.width] or [img.width]
    out: dict[str, bytes] = {}
    for w in widths:
        h = max(1, round(img.height * w / img.width))
        resized = img if w == img.width else img.resize((w, h), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        resized.save(buf, format="WEBP", quality=WEBP_QUALITY, method=6)
        out[f"{IMAGES_DIR}/{generation_id}-{sha8}-{w}.webp"] = buf.getvalue()
    return out


@dataclass
class ReleaseImages:
    fields: dict[str, dict[str, Any]]  # generation id -> release field
    files: dict[str, bytes]  # release-relative path -> bytes
    missing: dict[str, str]  # generation id -> reason (not cached, unreadable)

    def log(self) -> dict[str, Any]:
        return {
            "generations_with_image": len(self.fields),
            "files": len(self.files),
            "bytes": sum(len(b) for b in self.files.values()),
            "by_source": _count(f["source"] for f in self.fields.values()),
            "missing": dict(sorted(self.missing.items())),
        }


def _count(items: Any) -> dict[str, int]:
    out: dict[str, int] = {}
    for i in items:
        out[i] = out.get(i, 0) + 1
    return dict(sorted(out.items()))


def build_release_images(photos: list[Photo], cache: Path) -> ReleaseImages:
    res = ReleaseImages({}, {}, {})
    for ph in photos:
        p = cached_original(cache, ph)
        if p is None:
            res.missing[ph.generation_id] = "not fetched yet (ev images fetch)"
            continue
        try:
            sizes = render_sizes(p.read_bytes(), ph.generation_id)
        except Exception as e:  # noqa: BLE001  any decoder error: skip this photo, log it
            res.missing[ph.generation_id] = f"unreadable image: {type(e).__name__}"
            continue
        files = []
        for path, data in sizes.items():
            res.files[path] = data
            width = int(path.rsplit("-", 1)[1].removesuffix(".webp"))
            files.append(
                {
                    "width": width,
                    "path": path,
                    "bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                }
            )
        res.fields[ph.generation_id] = {"files": files, **ph.field()}
    return res
