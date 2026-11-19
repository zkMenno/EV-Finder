"""Load and validate data/images/photos.yaml + press-terms.yaml (T-133 → T-134 contract).

photos.yaml:
    photos:
      - generation_id: volkswagen-id3-gen1
        source: commons            # commons | press
        page_url: https://commons.wikimedia.org/wiki/File:...
        file_url: https://upload.wikimedia.org/wikipedia/commons/...jpg
        licence: CC-BY-SA-4.0      # commons: CC-BY-* / CC-BY-SA-* / CC0-1.0 / public-domain;
                                   # press: press-terms
        licence_template: cc-zero  # CC0 / public-domain only (Decision 083): the template read
        licence_checked_at: 2026-11-18  # from the file page, the date, and where it was read
        licence_checked_on: file page
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
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

PHOTOS_FILE = Path("images") / "photos.yaml"
PRESS_TERMS_FILE = Path("images") / "press-terms.yaml"

SOURCES = ("commons", "press")
PRESS_LICENCE = "press-terms"
COMMONS_LICENCE = re.compile(r"^CC-BY(-SA)?-(4\.0|(2\.0|2\.5|3\.0)(-[A-Z]{2})?)$")
"""Decision 081: Commons photos are CC BY or CC BY-SA only (no NC, no ND, no GFDL-only).
Versions 2.0-3.0 also exist as country ports (e.g. CC-BY-SA-3.0-DE); 4.0 has none."""
COMMONS_FREE_LICENCES = ("CC0-1.0", "public-domain")
"""Decision 083: CC0 and worldwide public domain, only with an allowed file-page template."""
ALLOWED_TEMPLATES = frozenset(
    {
        "cc-zero",
        "self|cc-zero",
        "pd-self",
        "self|pd-self",
        "pd-author",
        "pd-old",
        "pd-old-70",
        "pd-old-100",
    }
)
"""Normalised (lowercase, no spaces) Commons templates; mirrors ALLOWED_TEMPLATES in
data/images/tools/check_templates.py (a test keeps the two equal)."""
REFUSED_TEMPLATE = re.compile(r"^(pd-us|pd-usgov|pd-textlogo|pd-ineligible)")
"""Country-only or not-a-photo public domain (Decision 083): refused even if listed above."""
LICENCE_CHECKED_ON = "file page"
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
    # Decision 083 / T-149: the template WS3 read on the file page (CC0 / PD picks); CC BY
    # photos get theirs from `ev images fetch` (store.read_templates).
    licence_template: str | None = None
    licence_checked_at: date | None = None

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
        } | (
            {
                "licence_template": self.licence_template,
                "licence_checked_at": self.licence_checked_at.isoformat(),
            }
            if self.licence_template and self.licence_checked_at
            else {}
        )


@dataclass(frozen=True)
class PhotoProblem:
    generation_id: str
    reason: str


def licence_allowed(source: str, licence: str) -> bool:
    if source == "commons":
        return bool(COMMONS_LICENCE.match(licence)) or licence in COMMONS_FREE_LICENCES
    return source == "press" and licence == PRESS_LICENCE


def normalise_template(template: str) -> str:
    return re.sub(r"\s+", "", template).lower()


def template_allowed(template: str) -> bool:
    t = normalise_template(template)
    return t in ALLOWED_TEMPLATES and not REFUSED_TEMPLATE.match(t.removeprefix("self|"))


_CC_TEMPLATE = re.compile(r"^(cc-by(?:-sa)?)-([0-9.,]+?)(\+)?(-[a-z]{2})?(?:-migrated)?$")
CC_VERSIONS = ("1.0", "2.0", "2.5", "3.0", "4.0")
TEMPLATE_ALIASES: dict[str, frozenset[str]] = {
    # Commons {{YouTube CC-BY}}: YouTube's only Creative Commons option is CC BY 3.0.
    "youtubecc-by": frozenset({"cc-by-3.0"}),
}
"""Commons licence templates whose name is not the licence itself (normalised name -> tokens)."""


def template_licences(template: str) -> set[str]:
    """Licence tokens a Commons template grants, normalised: `self|GFDL|cc-by-sa-4.0` →
    {gfdl, cc-by-sa-4.0}; `cc-by-sa-3.0,2.5,2.0` → one token per version; `self` and
    named parameters (`migration=...`, `author=...`) are dropped."""
    out: set[str] = set()
    for part in normalise_template(template).split("|"):
        if not part or part == "self" or "=" in part:
            continue
        m = _CC_TEMPLATE.match(part)
        if part in TEMPLATE_ALIASES:
            out |= TEMPLATE_ALIASES[part]
        elif m:
            base, versions, port = m.group(1), m.group(2), m.group(4) or ""
            vs = [v for v in versions.split(",") if v]
            if m.group(3) and len(vs) == 1 and vs[0] in CC_VERSIONS:  # "2.0+" = or later
                vs = [v for v in CC_VERSIONS if float(v) >= float(vs[0])]
            out |= {f"{base}-{v}{port}" for v in vs}
        else:
            out.add(part)
    return out


def template_matches(licence: str, template: str) -> bool:
    """True when the file-page template grants the licence the photo ships under (T-149:
    a CC BY photo with a stray template, or a CC0 photo with a CC BY template, is refused)."""
    tokens = template_licences(template)
    if licence == "CC0-1.0":
        return "cc-zero" in tokens
    if licence == "public-domain":
        return any(template_allowed(t) and t != "cc-zero" for t in tokens)
    return licence.lower() in tokens


def _free_licence_problem(raw: dict[str, Any], today: date) -> str:
    """'' when a CC0 / public-domain photo carries the file-page template check (Decision 083)."""
    template = str(raw.get("licence_template") or "")
    checked = _date(raw.get("licence_checked_at"))
    if not template:
        return "CC0 / public-domain photo without licence_template (Decision 083)"
    if not template_allowed(template):
        return f"licence_template {template!r} not allowed (Decision 083: worldwide CC0 / PD only)"
    if checked is None or checked > today:
        return "licence_checked_at missing, not a date or in the future"
    if raw.get("licence_checked_on") != LICENCE_CHECKED_ON:
        return f"licence_checked_on must be {LICENCE_CHECKED_ON!r} (Decision 083)"
    return ""


def _https(url: object) -> bool:
    if not isinstance(url, str):
        return False
    u = urlparse(url)
    return u.scheme == "https" and bool(u.hostname)


def _date(v: object) -> date | None:
    if isinstance(v, datetime):  # YAML `2026-11-18 10:00` loads as a datetime (#149 nit)
        return v.date()
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
            bad(f"licence {licence!r} not allowed for {source} photos (Decisions 081, 083)")
        elif licence in COMMONS_FREE_LICENCES and (why := _free_licence_problem(raw, today)):
            bad(why)
        elif raw.get("licence_template") and not template_matches(
            licence, str(raw["licence_template"])
        ):
            bad(f"licence_template {raw['licence_template']!r} does not grant {licence} (T-149)")
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
                    licence_template=str(raw["licence_template"])
                    if raw.get("licence_template")
                    else None,
                    licence_checked_at=_date(raw.get("licence_checked_at")),
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
