"""candidates.json + choices.json -> data/images/photos.yaml (T-134 contract, WS1 INBOX 11-17)."""

import html
import json
import re
import urllib.parse
from pathlib import Path

import yaml

HERE = Path(__file__).parent
ROOT = HERE.parents[2]

C = json.loads(Path(str(HERE / "candidates.json")).read_text())
CH = json.loads(
    Path(str(HERE / "choices.json")).read_text()
)  # {generation_id: index | "none"}; default 0
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


photos, missing = [], []
for gid, entry in C.items():
    pick = CH.get(gid)  # chosen file title (checked by eye); falls back to the top candidate
    cands = entry["candidates"]
    if pick == "none" or not cands:
        missing.append(gid)
        continue
    by_title = {c["title"]: c for c in cands}
    c = by_title.get(pick) or (cands[0] if pick is None else None)
    if c is None:
        raise SystemExit(f"{gid}: chosen file {pick!r} is no longer a candidate")
    author = author_text(c["artist"])
    if not author or author.lower() in {"unknown author", "unknown"}:
        missing.append(gid)
        continue
    lic = spdx(c["lic"])
    tpl = TEMPLATES.get(c["title"])
    if lic in ("CC0-1.0", "public-domain") and tpl is None:
        raise SystemExit(f"{gid}: {lic} photo without a checked licence template (Decision 083)")
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
                {"licence_template": tpl["template"], "licence_checked_at": tpl["checked_at"]}
                if tpl
                else {}
            ),
        }
    )

doc = {
    "schema": "images-photos/v1",
    "notes": [
        "One photo per generation (Decisions 081, 083). Source order: maker press (only makers "
        "'allowed' in "
        "press-terms.yaml; none today), then Wikimedia Commons CC BY / CC BY-SA.",
        "Chosen by data/images/tools (search + rules), then checked by eye on contact sheets. "
        "Never hotlink: WS1 downloads file_url once into our storage (T-134).",
        "Photos keep their own licence and stay out of the CC BY open-data download (data rule 3).",
    ],
    "missing": sorted(missing),
    "photos": photos,
}
Path(OUT).write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=120))
print(len(photos), "photos;", len(missing), "missing:", missing)
