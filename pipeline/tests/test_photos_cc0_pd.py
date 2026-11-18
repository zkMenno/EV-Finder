"""Decision 083: Commons CC0 / worldwide public-domain photos, with the file-page template check.
No network: generated images only."""

from __future__ import annotations

import ast
import io
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from PIL import Image

from ev_pipeline.images.photos import (
    ALLOWED_TEMPLATES,
    licence_allowed,
    parse_photos,
    template_allowed,
)
from ev_pipeline.images.qa import image_problems
from ev_pipeline.images.store import render_sizes

TODAY = date(2026, 11, 18)
GENS = {"renault-5-gen1"}
REPO = Path(__file__).resolve().parents[2]


def free(**kw: Any) -> dict[str, Any]:
    e = {
        "generation_id": "renault-5-gen1",
        "source": "commons",
        "page_url": "https://commons.wikimedia.org/wiki/File:R5.jpg",
        "file_url": "https://upload.wikimedia.org/wikipedia/commons/f/f6/R5.jpg",
        "licence": "CC0-1.0",
        "author": "Charles",
        "credit": "Charles (CC0), via Wikimedia Commons",
        "retrieved_at": "2026-11-17",
        "licence_template": "cc-zero",
        "licence_checked_at": "2026-11-18",
        "licence_checked_on": "file page",
    }
    e.update(kw)
    return e


@pytest.mark.parametrize(
    ("licence", "template"),
    [
        ("CC0-1.0", "cc-zero"),
        ("CC0-1.0", "self|cc-zero"),
        ("CC0-1.0", "self | cc-zero"),
        ("public-domain", "PD-self"),
        ("public-domain", "self|PD-self"),
        ("public-domain", "PD-author"),
        ("public-domain", "PD-old-100"),
    ],
)
def test_cc0_and_worldwide_pd_with_template_pass(licence: str, template: str) -> None:
    photos, problems = parse_photos(
        {"photos": [free(licence=licence, licence_template=template)]}, None, GENS, TODAY
    )
    assert problems == [] and photos[0].licence == licence


@pytest.mark.parametrize(
    "template",
    [
        "PD-US",
        "PD-US-expired",
        "PD-USGov",
        "PD-USGov-NASA",
        "PD-textlogo",
        "PD-ineligible",
        "self|PD-US",
        "PD-old",
        "CC-BY-4.0",
        "cc-zero-ish",
    ],
)
def test_country_only_or_unknown_templates_are_refused(template: str) -> None:
    photos, problems = parse_photos(
        {"photos": [free(licence="public-domain", licence_template=template)]}, None, GENS, TODAY
    )
    assert photos == [] and "licence_template" in problems[0].reason


@pytest.mark.parametrize(
    ("kw", "reason"),
    [
        ({"licence_template": None}, "without licence_template"),
        ({"licence_checked_at": None}, "licence_checked_at"),
        ({"licence_checked_at": "2027-01-01"}, "licence_checked_at"),
        ({"licence_checked_on": "category"}, "licence_checked_on"),
        ({"licence_checked_on": None}, "licence_checked_on"),
    ],
)
def test_free_licence_needs_the_file_page_check(kw: dict[str, Any], reason: str) -> None:
    photos, problems = parse_photos({"photos": [free(**kw)]}, None, GENS, TODAY)
    assert photos == [] and reason in problems[0].reason


@pytest.mark.parametrize("lic", ["CC0", "cc0-1.0", "PD", "Public domain", "CC0-2.0"])
def test_free_licence_lookalikes_are_refused(lic: str) -> None:
    photos, problems = parse_photos({"photos": [free(licence=lic)]}, None, GENS, TODAY)
    assert photos == [] and "licence" in problems[0].reason


def test_free_licences_are_commons_only() -> None:
    assert licence_allowed("commons", "CC0-1.0") and licence_allowed("commons", "public-domain")
    assert not licence_allowed("press", "CC0-1.0")
    assert not licence_allowed("press", "public-domain")


def test_release_qa_accepts_cc0_pd_images() -> None:
    files = [{"width": 800, "path": "images/r5-800.webp", "bytes": 1, "sha256": "0" * 64}]
    gens = [
        {
            "id": f"g{i}",
            "image": {
                "source": "commons",
                "licence": lic,
                "credit": "x",
                "page_url": "https://c",
                "retrieved_at": "2026-11-17",
                "files": files,
            },
        }
        for i, lic in enumerate(["CC0-1.0", "public-domain", "CC-BY-SA-4.0"])
    ]
    assert image_problems({"generations": gens}) == []


def test_template_allowlist_matches_the_photo_tool() -> None:
    """data/images/tools/check_templates.py (WS3's picker) and the pipeline must agree."""
    tool = REPO / "data" / "images" / "tools" / "check_templates.py"
    if not tool.exists():
        pytest.skip("check_templates.py not on this branch yet (#132)")
    tree = ast.parse(tool.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "ALLOWED_TEMPLATES" for t in node.targets
        ):
            assert set(ast.literal_eval(node.value)) == set(ALLOWED_TEMPLATES)
            return
    pytest.fail("ALLOWED_TEMPLATES not found in check_templates.py")


def test_refused_prefixes_win_over_the_allowlist() -> None:
    assert not template_allowed("PD-USGov")
    assert template_allowed(" Self | CC-Zero ")


# --- PNG originals (the peugeot-e-308 pick is a PNG) -----------------------------------------


def png(mode: str) -> bytes:
    if mode == "P":
        im = Image.new("P", (900, 600), 0)
        im.putpalette([0, 0, 0, 200, 30, 30] + [0] * 762)
        im.paste(1, (0, 0, 450, 600))
        im.info["transparency"] = 0
        buf = io.BytesIO()
        im.save(buf, format="PNG", transparency=0)
        return buf.getvalue()
    colour = {"RGB": (200, 30, 30), "RGBA": (200, 30, 30, 255), "LA": (90, 255)}[mode]
    im = Image.new(mode, (900, 600), colour)
    if mode in ("RGBA", "LA"):
        clear = (0, 0, 0, 0) if mode == "RGBA" else (0, 0)
        im.paste(Image.new(mode, (450, 600), clear), (450, 0))  # right half transparent
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return buf.getvalue()


@pytest.mark.parametrize("mode", ["RGB", "RGBA", "LA", "P"])
def test_png_originals_render_to_webp(mode: str) -> None:
    out = render_sizes(png(mode), "peugeot-e-308-gen1")
    assert {p.rsplit("-", 1)[1] for p in out} == {"400.webp", "800.webp"}
    with Image.open(io.BytesIO(out[next(p for p in out if p.endswith("-800.webp"))])) as im:
        assert im.format == "WEBP" and im.mode == "RGB"
        if mode in ("RGBA", "LA"):
            r, g, b = im.getpixel((700, 300))  # was transparent
            assert min(r, g, b) > 240, "transparent area must go white, not black"
        if mode == "P":
            r, g, b = im.getpixel((700, 300))  # right half: palette index 0 = transparent
            assert min(r, g, b) > 240
