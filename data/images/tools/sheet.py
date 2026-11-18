"""Contact sheets: candidates per generation as a labelled grid, for checking picks by eye."""

import io
import json
import sys
import textwrap
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).parent
ROOT = HERE.parents[2]

UA = {"User-Agent": "EVShortlistResearch/0.1 (https://github.com/zkMenno/EV-Shortlist)"}
C = json.loads(Path(str(HERE / "candidates.json")).read_text())
CELL_W, CELL_H, COLS = 300, 230, 4


def thumb(url):
    import time

    for i in range(4):
        try:
            return Image.open(
                io.BytesIO(
                    urllib.request.urlopen(
                        urllib.request.Request(url, headers=UA), timeout=30
                    ).read()
                )
            ).convert("RGB")
        except Exception:  # noqa: BLE001
            time.sleep(3 * (i + 1))
    return None


def sheet(items, out):
    rows = (len(items) + COLS - 1) // COLS
    img = Image.new("RGB", (CELL_W * COLS, CELL_H * rows), "white")
    d = ImageDraw.Draw(img)
    for k, (label, cand) in enumerate(items):
        x, y = (k % COLS) * CELL_W, (k // COLS) * CELL_H
        if cand:
            t = thumb(cand["thumb"])
            if t:
                t.thumbnail((CELL_W - 6, CELL_H - 50))
                img.paste(t, (x + 3, y + 3))
        d.text((x + 3, y + CELL_H - 46), textwrap.fill(label, 48)[:150], fill="black")
    img.save(out, quality=80)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "top":  # top candidate for a slice of generations
        ids = [g for g in C][int(sys.argv[2]) : int(sys.argv[3])]
        items = [
            (
                f"{g} | {(C[g]['candidates'][0]['title'][5:60] if C[g]['candidates'] else 'NONE')}",
                C[g]["candidates"][0] if C[g]["candidates"] else None,
            )
            for g in ids
        ]
    elif mode == "multi":  # first 4 candidates for each listed generation, one row each
        items = []
        for g in sys.argv[2].split(","):
            cs = C[g]["candidates"][:4]
            for i in range(4):
                c = cs[i] if i < len(cs) else None
                items.append((f"{g} #{i} {c['title'][5:50] if c else '-'}", c))
    else:  # all candidates of one generation
        g = sys.argv[2]
        items = [(f"{i} {c['title'][5:70]}", c) for i, c in enumerate(C[g]["candidates"])]
    sheet(items, sys.argv[-1])
