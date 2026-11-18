"""Batch Commons searches: several MWAPI SERVICE blocks per WDQS request (~1 req/min). Resumable."""

import csv
import io
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[2]

UA = "EVShortlistResearch/0.1 (https://github.com/zkMenno/EV-Shortlist)"
CACHE = str(HERE / "search_cache.json")
BLOCK = """{ SERVICE wikibase:mwapi {
    bd:serviceParam wikibase:endpoint "commons.wikimedia.org"; wikibase:api "Generator";
      mwapi:generator "search"; mwapi:gsrsearch "%s"; mwapi:gsrnamespace "6"; mwapi:gsrlimit "50";
      mwapi:prop "imageinfo"; mwapi:iiprop "extmetadata|url|size"; mwapi:iiurlwidth "400";
      mwapi:iiextmetadatafilter "LicenseShortName|Artist|DateTimeOriginal".
    ?title wikibase:apiOutput mwapi:title.
    ?lic wikibase:apiOutput "imageinfo/ii/extmetadata/LicenseShortName/@value".
    ?artist wikibase:apiOutput "imageinfo/ii/extmetadata/Artist/@value".
    ?dto wikibase:apiOutput "imageinfo/ii/extmetadata/DateTimeOriginal/@value".
    ?url wikibase:apiOutput "imageinfo/ii/@descriptionurl".
    ?w wikibase:apiOutput "imageinfo/ii/@width".
    ?h wikibase:apiOutput "imageinfo/ii/@height".
    ?thumb wikibase:apiOutput "imageinfo/ii/@thumburl".
  } BIND(%d AS ?q) }"""


def run(queries):
    body = " UNION ".join(
        BLOCK % (q.replace("\\", "\\\\").replace('"', '\\"'), i) for i, q in enumerate(queries)
    )
    sparql = f"SELECT ?q ?title ?lic ?artist ?dto ?url ?w ?h ?thumb WHERE {{ {body} }}"
    data = urllib.parse.urlencode({"query": sparql}).encode()
    req = urllib.request.Request(
        "https://query.wikidata.org/sparql",
        data=data,
        headers={
            "User-Agent": UA,
            "Accept": "text/csv",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        rows = list(csv.DictReader(io.StringIO(r.read().decode())))
    out = {q: [] for q in queries}
    for row in rows:
        out[queries[int(row.pop("q"))]].append(row)
    return out


def main(qfile, size=6):
    queries = json.loads(Path(qfile).read_text())
    cache = json.loads(Path(CACHE).read_text()) if os.path.exists(CACHE) else {}
    todo = [q for q in queries if q not in cache]
    print(len(todo), "to fetch", flush=True)
    i = 0
    fails = {}
    while i < len(todo):
        chunk = todo[i : i + size]
        try:
            res = run(chunk)
            cache.update(res)
            Path(CACHE).write_text(json.dumps(cache, ensure_ascii=False))
            print(time.strftime("%H:%M:%S"), "ok", i, [len(res[q]) for q in chunk], flush=True)
            i += len(chunk)
            size = min(6, size + 1)
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            print(
                time.strftime("%H:%M:%S"), "err", i, size, msg[:80].replace("\n", " "), flush=True
            )
            if "429" not in msg:
                if size == 1:
                    fails[chunk[0]] = fails.get(chunk[0], 0) + 1
                    if fails[chunk[0]] >= 3:
                        cache[chunk[0]] = []
                        Path(CACHE).write_text(json.dumps(cache, ensure_ascii=False))
                        print("giving up on", chunk[0], flush=True)
                        i += 1
                size = max(1, size // 2)
        time.sleep(62)


if __name__ == "__main__":
    main(sys.argv[1])
