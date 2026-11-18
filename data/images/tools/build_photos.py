"""choices.json + candidates -> data/images/photos.yaml (T-134 contract, WS1 INBOX 11-17).

Offline: picked.json (committed) holds the chosen candidate per generation, so photos.yaml rebuilds
without the network. With candidates.json present (after pick.py) it is used and picked.json
refreshed.
"""

import html
import json
import re
import urllib.parse
from pathlib import Path

import yaml

HERE = Path(__file__).parent
ROOT = HERE.parents[2]

import sys  # noqa: E402

sys.path.insert(0, str(HERE))
from check_templates import allowed  # noqa: E402

CAND = HERE / "candidates.json"
PICKED = HERE / "picked.json"
CH = json.loads((HERE / "choices.json").read_text())  # {generation_id: file title | "none"}
OUT = str(ROOT / "data/images/photos.yaml")
RETRIEVED = "2026-11-17"


TEMPLATES = json.loads(Path(str(HERE / "licence_templates.json")).read_text())


def spdx(lic):
    if lic.strip() == "CC0":
        return "CC0-1.0"
    if lic.strip().lower() == "public domain":
        return "public-domain"
    m = re.match(r"CC BY(-SA)? ([0-9.]+)( [a-z]{2})?$", lic.strip(), re.I)
    port = f"-{m.group(3).strip().upper()}" if m.group(3) else ""
    return f"CC-BY{'-SA' if m.group(1) else ''}-{m.group(2)}{port}"


def author_text(artist_html):
    t = re.sub(r"<[^>]+>", "", artist_html or "")
    t = html.unescape(t).strip()
    return re.sub(r"\s+", " ", t)


def file_url(thumb):
    # thumb.wikimedia.org/wikipedia/commons/thumb/a/ab/NAME/500px-NAME
    #   -> upload.wikimedia.org/wikipedia/commons/a/ab/NAME
    p = urllib.parse.urlparse(thumb).path
    m = re.match(r"/wikipedia/commons/thumb/([0-9a-f])/([0-9a-f]{2})/([^/]+)/", p)
    return f"https://upload.wikimedia.org/wikipedia/commons/{m.group(1)}/{m.group(2)}/{m.group(3)}"


if CAND.exists():
    C = json.loads(CAND.read_text())
    picked = {}
    for gid, entry in C.items():
        pick = CH.get(gid)
        if pick is None:
            raise SystemExit(f"{gid}: no pin in choices.json (a file title or 'none')")
        if pick == "none":
            continue
        by_title = {c["title"]: c for c in entry["candidates"]}
        if pick not in by_title:
            raise SystemExit(f"{gid}: chosen file {pick!r} is no longer a candidate")
        picked[gid] = by_title[pick]
    PICKED.write_text(json.dumps(picked, indent=1, ensure_ascii=False) + "\n")  # seed order
else:
    picked = json.loads(PICKED.read_text())

photos, missing = [], sorted(g for g, v in CH.items() if v == "none")
for gid, c in picked.items():
    author = author_text(c["artist"])
    if not author or author.lower() in {"unknown author", "unknown"}:
        missing.append(gid)
        continue
    lic = spdx(c["lic"])
    tpl = TEMPLATES.get(c["title"])
    if lic in ("CC0-1.0", "public-domain"):
        # Decision 083: template read from the file page, worldwide only, no warning templates
        if tpl is None or not tpl.get("page_template") or not allowed(tpl["page_template"]):
            raise SystemExit(
                f"{gid}: {lic} photo needs an allowed file-page template (Decision 083)"
            )
        if tpl.get("warning_templates"):
            raise SystemExit(f"{gid}: file page carries {tpl['warning_templates']}")
    photos.append(
        {
            "generation_id": gid,
            "source": "commons",
            "page_url": c["url"],
            "file_url": file_url(c["thumb"]),
            "licence": lic,
            "author": author,
            "credit": (
                f"{author}, {c['lic'].strip()}, via Wikimedia Commons"
                if lic not in ("CC0-1.0", "public-domain")
                else f"{author or 'Wikimedia Commons'} ({c['lic'].strip()}), via Wikimedia Commons"
            ),
            "retrieved_at": RETRIEVED,
            "width": int(c["w"]),
            "height": int(c["h"]),
            **(
                {
                    "licence_template": tpl["page_template"],
                    "licence_checked_at": tpl["checked_at"],
                    "licence_checked_on": "file page",
                }
                if tpl
                else {}
            ),
        }
    )

doc = {
    "schema": "images-photos/v1",
    "notes": [
        "One photo per generation (Decisions 081, 083). Source order: maker press (only makers "
        "'allowed' in press-terms.yaml; none today), then Wikimedia Commons CC BY / CC BY-SA, "
        "or CC0 / worldwide public domain with the template read from the file page "
        "(licence_template).",
        "Chosen by data/images/tools (search + rules), then checked by eye on contact sheets. "
        "Never hotlink: WS1 downloads file_url once into our storage (T-134).",
        "Photos keep their own licence and stay out of the CC BY open-data download (data rule 3).",
    ],
    "missing": sorted(missing),
    "photos": photos,
}
Path(OUT).write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=120))
print(len(photos), "photos;", len(missing), "missing:", missing)
