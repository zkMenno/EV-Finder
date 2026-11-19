"""Read the licence template of each CC0 / PD pick from its Commons file page (Decision 083).

Decision 083: check the template on the file page itself (wikitext via action=raw), never a
category or a mirror. Writes licence_templates.json; build_photos.py refuses a CC0 / PD pick whose
template is missing or not in ALLOWED_TEMPLATES.

Usage: python3 -I data/images/tools/check_templates.py   (network; ~2 s per file)
"""

import json
import re
import subprocess
import time
import urllib.parse
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
UA = "EVShortlistResearch/0.1 (https://github.com/zkMenno/EV-Shortlist)"

# Worldwide public domain or CC0 only. Country-only PD (PD-US*, PD-USGov*), PD-textlogo: refused.
ALLOWED_TEMPLATES = {
    "cc-zero",
    "self|cc-zero",
    "pd-self",
    "self|pd-self",
    "pd-author",
    "pd-old",
    "pd-old-70",
    "pd-old-100",
}
REFUSED = re.compile(r"^(pd-us|pd-usgov|pd-textlogo|pd-ineligible)", re.I)
WARNINGS = re.compile(
    r"\{\{\s*(delete|speedydelete|copyvio|no permission|no source|no license|personality rights"
    r"|nofop|no fop|fop-)",
    re.I,
)
LICENCE = re.compile(r"\{\{\s*((?:self\s*\|\s*)?(?:cc-zero|pd-[a-z0-9-]+))\s*(?:\||\}\})", re.I)


def norm(t: str) -> str:
    return re.sub(r"\s+", "", t).lower()


def allowed(template: str) -> bool:
    t = norm(template)
    return t in ALLOWED_TEMPLATES and not REFUSED.match(t.removeprefix("self|"))


def read_page(title: str) -> str:
    q = urllib.parse.urlencode({"title": title, "action": "raw"})
    url = f"https://commons.wikimedia.org/w/index.php?{q}"
    out = subprocess.run(["curl", "-sS", "-m", "30", "-A", UA, url], capture_output=True, text=True)
    return out.stdout


def main() -> None:
    picks = json.loads((HERE / "picked.json").read_text())
    titles = [p["title"] for p in picks.values() if p["lic"].strip() in ("CC0", "Public domain")]
    result = {}
    for title in titles:
        raw = read_page(title)
        found = [m.group(1) for m in LICENCE.finditer(raw)]
        result[title] = {
            "page_template": found[0] if found else None,
            "all_licence_templates": found,
            "warning_templates": [m.group(1) for m in WARNINGS.finditer(raw)],
            "method": "file page wikitext (action=raw)",
            "checked_at": date.today().isoformat(),
        }
        ok = found and allowed(found[0]) and not result[title]["warning_templates"]
        print(("OK  " if ok else "BAD ") + title, found, result[title]["warning_templates"])
        time.sleep(2)
    text = json.dumps(result, indent=1, ensure_ascii=False) + "\n"
    (HERE / "licence_templates.json").write_text(text)


if __name__ == "__main__":
    main()
