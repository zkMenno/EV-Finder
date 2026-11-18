"""candidates.json + choices.json → data/images/photos.yaml in the T-134 contract (WS1 INBOX 2026-11-17 22:40)."""
import html, json, re, urllib.parse
import yaml

C = json.load(open(str(__import__("pathlib").Path(__file__).parent / "candidates.json")))
CH = json.load(open(str(__import__("pathlib").Path(__file__).parent / "choices.json")))  # {generation_id: index | "none"}; default 0
OUT = str(__import__("pathlib").Path(__file__).parents[3] / "data/images/photos.yaml")
RETRIEVED = "2026-11-17"


def spdx(lic):
    m = re.match(r"CC BY(-SA)? ([0-9.]+)( [a-z]{2})?$", lic.strip(), re.I)
    port = f"-{m.group(3).strip().upper()}" if m.group(3) else ""
    return f"CC-BY{'-SA' if m.group(1) else ''}-{m.group(2)}{port}"


def author_text(artist_html):
    t = re.sub(r"<[^>]+>", "", artist_html or "")
    t = html.unescape(t).strip()
    return re.sub(r"\s+", " ", t)


def file_url(thumb):
    # thumb.wikimedia.org/wikipedia/commons/thumb/a/ab/NAME/500px-NAME → upload.wikimedia.org/wikipedia/commons/a/ab/NAME
    p = urllib.parse.urlparse(thumb).path
    m = re.match(r"/wikipedia/commons/thumb/([0-9a-f])/([0-9a-f]{2})/([^/]+)/", p)
    return f"https://upload.wikimedia.org/wikipedia/commons/{m.group(1)}/{m.group(2)}/{m.group(3)}"


photos, missing = [], []
for gid, entry in C.items():
    pick = CH.get(gid, 0)
    cands = entry["candidates"]
    if pick == "none" or not cands:
        missing.append(gid)
        continue
    c = cands[pick]
    author = author_text(c["artist"])
    if not author or author.lower() in {"unknown author", "unknown"}:
        missing.append(gid)
        continue
    lic = spdx(c["lic"])
    photos.append({
        "generation_id": gid,
        "source": "commons",
        "page_url": c["url"],
        "file_url": file_url(c["thumb"]),
        "licence": lic,
        "author": author,
        "credit": f"{author}, {c['lic'].strip()}, via Wikimedia Commons",
        "retrieved_at": RETRIEVED,
        "width": int(c["w"]),
        "height": int(c["h"]),
    })

doc = {
    "schema": "images-photos/v1",
    "notes": [
        "One photo per generation (Decision 081). Source order: maker press (only makers 'allowed' in "
        "press-terms.yaml; none today), then Wikimedia Commons CC BY / CC BY-SA.",
        "Chosen by data/images/tools (search + rules), then checked by eye on contact sheets. "
        "Never hotlink: WS1 downloads file_url once into our storage (T-134).",
        "CC BY-SA photos keep their licence and stay out of the CC BY open-data download (data rule 3).",
    ],
    "missing": sorted(missing),
    "photos": photos,
}
open(OUT, "w").write(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=120))
print(len(photos), "photos;", len(missing), "missing:", missing)
