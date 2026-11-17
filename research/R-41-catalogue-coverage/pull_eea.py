"""T-136: pull EEA CO2 cars grouped EV keys per data year into /tmp/t136/eea_<year>.jsonl.

One request at a time, 2 s apart (fair use). Grouped server-side; no per-registration rows.
"""

import json
import os
import ssl
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

URL = "https://discodata.eea.europa.eu/sql"
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/t136")
ALL = "[CO2Emission].[latest].[co2cars]"
TABLES = [(y, ALL, f"v{2 * (y - 2010) + 2}") for y in range(2010, 2020)] + [
    (2020, "[CO2Emission].[latest].[co2cars_2020Fv22]", None),
    (2021, "[CO2Emission].[latest].[co2cars_2021Fv24]", None),
    (2022, "[CO2Emission].[latest].[co2cars_2022Fv26]", None),
    (2023, "[CO2Emission].[latest].[co2cars_2023Fv28]", None),
    (2024, "[CO2Emission].[latest].[co2cars_2024Fv30]", None),
    (2025, "[CO2Emission].[latest].[co2cars_2025Pv31]", None),
]
PAGE = 10000
ctx = ssl.create_default_context(cafile=os.path.expanduser("~/.ccr/ca-bundle.crt"))


def post(query: str, page: int) -> list[dict]:
    body = urllib.parse.urlencode({"query": query, "nrOfHits": PAGE, "p": page}).encode()
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(URL, data=body), timeout=300, context=ctx) as r:
                return json.load(r)["results"]
        except Exception as e:  # noqa: BLE001
            print("retry", attempt, e, file=sys.stderr)
            time.sleep(10 * (attempt + 1))
    raise SystemExit("failed")


for year, table, vf in TABLES:
    out = OUT / f"eea_{year}.jsonl"
    if out.exists():
        continue
    where = "Ft = 'electric'"
    if vf:
        where += f" AND Year = {year} AND Status = 'F' AND Version_file = '{vf}'"
    q = (
        "SELECT Mk, Cn, Mh, T, Va, Ve, [Ep (KW)] AS ep, Zr, [Z (Wh/km)] AS z, MIN([M (kg)]) AS m_min, "
        f"SUM(R) AS r FROM {table} WHERE {where} "
        "GROUP BY Mk, Cn, Mh, T, Va, Ve, [Ep (KW)], Zr, [Z (Wh/km)] ORDER BY Mk, Cn, T, Va, Ve"
    )
    rows: list[dict] = []
    page = 1
    while True:
        got = post(q, page)
        rows += got
        time.sleep(2)
        if len(got) < PAGE:
            break
        page += 1
    with out.open("w") as f:
        for r in rows:
            r["year"] = year
            f.write(json.dumps(r) + "\n")
    print(year, len(rows), "groups", sum(r["r"] or 0 for r in rows), "regs", flush=True)
