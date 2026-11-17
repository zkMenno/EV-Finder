"""Load and validate data/images/photos.yaml + press-terms.yaml (T-133 → T-134 contract).

photos.yaml:
    photos:
      - generation_id: volkswagen-id3-gen1
        source: commons            # commons | press
        page_url: https://commons.wikimedia.org/wiki/File:...
        file_url: https://upload.wikimedia.org/wikipedia/commons/...jpg
        licence: CC-BY-SA-4.0      # commons: CC-BY-* / CC-BY-SA-*; press: press-terms
        author: Jane Doe
        credit: "Photo: Jane Doe, CC BY-SA 4.0, via Wikimedia Commons"
        retrieved_at: 2026-11-18
        make_id: volkswagen        # press only

press-terms.yaml:
    makers:
      - {make_id, terms_url, checked_at, quote, verdict: allowed | not_allowed | unclear,
         photo_hosts: [...]}

A photo that breaks a rule is dropped with a Problem (review queue), never guessed or fixed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

PHOTOS_FILE = Path("images") / "photos.yaml"
PRESS_TERMS_FILE = Path("images") / "press-terms.yaml"

SOURCES = ("commons", "press")
PRESS_LICENCE = "press-terms"
COMMONS_LICENCE = re.compile(r"^CC-BY(-SA)?-(2\.0|2\.5|3\.0|4\.0)$")
"""Decision 081: Commons photos are CC BY or CC BY-SA only (no NC, no ND, no GFDL-only)."""
SOURCE_ID = {"commons": "wikimedia-commons", "press": "maker-press-photos"}
"""data/sources.yaml rows whose `hosts:` allowlist the downloads."""


@dataclass(frozen=True)
class Photo:
    generation_id: str
    source: str
    page_url: str
    file_url: str
    licence: str
    author: str | None
    credit: str
    retrieved_at: date
    make_id: str | None = None

    def field(self) -> dict[str, Any]:
        """The release field without `files` (added once the sizes exist)."""
        return {
            "source": self.source,
            "page_url": self.page_url,
            "file_url": self.file_url,
            "licence": self.licence,
            "author": self.author,
            "credit": self.credit,
            "retrieved_at": self.retrieved_at.isoformat(),
            "make_id": self.make_id,
        }


@dataclass(frozen=True)
class PhotoProblem:
    generation_id: str
    reason: str


def licence_allowed(source: str, licence: str) -> bool:
    if source == "commons":
        return bool(COMMONS_LICENCE.match(licence))
    return source == "press" and licence == PRESS_LICENCE


def _https(url: object) -> bool:
    if not isinstance(url, str):
        return False
    u = urlparse(url)
    return u.scheme == "https" and bool(u.hostname)


def _date(v: object) -> date | None:
    if isinstance(v, date):
        return v
    if isinstance(v, str):
        try:
            return date.fromisoformat(v)
        except ValueError:
            return None
    return None


def allowed_makers(terms_doc: dict[str, Any] | None) -> set[str]:
    """Makers whose press terms allow our use. `unclear` counts as not allowed (T-133)."""
    out: set[str] = set()
    for m in (terms_doc or {}).get("makers") or []:
        if isinstance(m, dict) and m.get("verdict") == "allowed" and m.get("make_id"):
            out.add(str(m["make_id"]))
    return out


def parse_photos(
    doc: dict[str, Any] | None,
    terms_doc: dict[str, Any] | None,
    generation_ids: set[str],
    today: date,
) -> tuple[list[Photo], list[PhotoProblem]]:
    makers = allowed_makers(terms_doc)
    photos: list[Photo] = []
    problems: list[PhotoProblem] = []
    seen: set[str] = set()
    for raw in (doc or {}).get("photos") or []:
        gid = str(raw.get("generation_id") or "") if isinstance(raw, dict) else ""

        def bad(reason: str, gid: str = gid) -> None:
            problems.append(PhotoProblem(gid or "?", reason))

        if not isinstance(raw, dict) or not gid:
            bad("entry without generation_id")
            continue
        if gid not in generation_ids:
            bad("unknown generation_id")
            continue
        if gid in seen:
            bad("second photo for this generation (one per generation at launch)")
            continue
        source = raw.get("source")
        licence = str(raw.get("licence") or "")
        credit = str(raw.get("credit") or "").strip()
        retrieved = _date(raw.get("retrieved_at"))
        make_id = raw.get("make_id")
        if source not in SOURCES:
            bad(f"source must be one of {SOURCES}")
        elif not licence_allowed(source, licence):
            bad(f"licence {licence!r} not allowed for {source} photos (Decision 081)")
        elif not credit:
            bad("empty credit line")
        elif not _https(raw.get("page_url")) or not _https(raw.get("file_url")):
            bad("page_url and file_url must be https URLs")
        elif retrieved is None or retrieved > today:
            bad("retrieved_at missing, not a date or in the future")
        elif source == "press" and make_id not in makers:
            bad(f"press terms for {make_id!r} are not 'allowed' in press-terms.yaml")
        else:
            seen.add(gid)
            photos.append(
                Photo(
                    generation_id=gid,
                    source=str(source),
                    page_url=str(raw["page_url"]),
                    file_url=str(raw["file_url"]),
                    licence=licence,
                    author=(str(raw["author"]).strip() or None) if raw.get("author") else None,
                    credit=credit,
                    retrieved_at=retrieved,
                    make_id=str(make_id) if make_id else None,
                )
            )
    return photos, problems


def load_photos(
    data_dir: Path, generation_ids: set[str], today: date
) -> tuple[list[Photo], list[PhotoProblem]]:
    """Missing files mean no photos yet (not an error)."""
    p, t = data_dir / PHOTOS_FILE, data_dir / PRESS_TERMS_FILE
    doc = yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else None
    terms = yaml.safe_load(t.read_text(encoding="utf-8")) if t.exists() else None
    return parse_photos(doc, terms, generation_ids, today)
