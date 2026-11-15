"""Generates the EV Shortlist architecture canvas (Design type artboards)."""
import json, html, datetime
P = "/home/claude/arch/project"
INK, INK2, INK3, SKY, SUN = "#16233A", "#45546F", "#5B6982", "#3B78AE", "#FFD166"
SEA, MEADOWT, SUNT, LINE, WHITE, LINK = "#E8F1F9", "#E4F2DC", "#FFF2CC", "#D6DFEA", "#FFFFFF", "#2B5F91"
ARROW = "#5B6982"

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&amp;family=Bitter:wght@700;800&amp;family=Patrick+Hand&amp;display=swap">
<style>
body{{margin:0}}
a{{color:#2B5F91}}a:hover{{color:#16233A}}
</style>
</helmet>
"""
TAIL = """</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{w},"height":{h}}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
"""

STATUS = {  # word + style; never colour alone
    "built": ("Built", MEADOWT, "1px solid #9cc98a"),
    "proto": ("Prototype", SUNT, "1px solid #e6c463"),
    "planned": ("Planned", WHITE, f"1px dashed {INK3}"),
    "none": (None, WHITE, f"1px solid {LINE}"),
}

def e(s):
    return html.escape(s, quote=False)

class Board:
    def __init__(self):
        self.bands, self.arrows, self.cards, self.labels = [], [], [], []
        self.n = 0

    def band(self, x, y, w, h, fill, label, sub=""):
        self.bands.append(f'<div style="position: absolute; left: {x}px; top: {y}px; width: {w}px; height: {h}px; box-sizing: border-box; background: {fill}; border-radius: 18px"></div>')
        t = f'<b>{e(label)}</b>' + (f'<br><span style="font-family: \'Atkinson Hyperlegible\'; font-weight: 400; font-size: 14px; color: {INK2}">{e(sub)}</span>' if sub else "")
        self.labels.append(f'<div style="position: absolute; left: {x+20}px; top: {y+16}px; width: {w-40}px; font-family: Bitter; font-weight: 800; font-size: 19px; line-height: 24px; color: {INK}">{t}</div>')

    def card(self, x, y, w, h, title, sub="", status="none", align="left"):
        word, fill, border = STATUS[status]
        tag = (f'<br><span style="font-size: 12px; font-weight: 700; color: {INK2}; letter-spacing: .3px">{word.upper()}</span>' if word else "")
        sub_html = f'<br><span style="font-size: 13.5px; line-height: 18px; color: {INK2}">{e(sub)}</span>' if sub else ""
        just = "flex-start" if align == "left" else "center"
        self.cards.append(
            f'<div style="position: absolute; left: {x}px; top: {y}px; width: {w}px; height: {h}px; box-sizing: border-box; padding: 10px 14px; display: flex; align-items: center; justify-content: {just}; text-align: {align}; background: {fill}; border: {border}; border-radius: 10px; font-family: \'Atkinson Hyperlegible\'; font-size: 16px; line-height: 20px; color: {INK}">'
            f'<span><b>{e(title)}</b>{sub_html}{tag}</span></div>')

    def text(self, x, y, w, s, size=14, color=INK2, font="'Atkinson Hyperlegible'", weight=400):
        self.labels.append(f'<div style="position: absolute; left: {x}px; top: {y}px; width: {w}px; font-family: {font}; font-weight: {weight}; font-size: {size}px; line-height: {round(size*1.35)}px; color: {color}">{s}</div>')

    def arrow(self, x1, y1, x2, y2, label):
        """Straight arrow, tail (x1,y1) to tip (x2,y2); horizontal or vertical."""
        self.n += 1
        mid = f"dc-arrow-head-filled-{self.n}"
        h = 4
        if y1 == y2:
            n = abs(x2 - x1); left = min(x1, x2); top = y1 - 4; W, H = n, 8
            d = f"M 0 4 L {n-h} 4" if x2 > x1 else f"M {n} 4 L {h} 4"
        else:
            n = abs(y2 - y1); left = x1 - 4; top = min(y1, y2); W, H = 8, n
            d = f"M 4 0 L 4 {n-h}" if y2 > y1 else f"M 4 {n} L 4 {h}"
        self.arrows.append(
            f'<svg role="img" aria-label="{e(label)}" width="{W}" height="{H}" viewBox="0 0 {W} {H}" preserveAspectRatio="none" style="position: absolute; left: {left}px; top: {top}px; width: {W}px; height: {H}px; overflow: visible; fill: none; stroke: {ARROW}; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round">'
            f'<defs><marker id="{mid}" orient="auto" markerWidth="5" markerHeight="5" refX="2" refY="2" overflow="visible"><path d="M0 0 L4 2 L0 4 Z" fill="{ARROW}" stroke="none" style="stroke: none; fill: {ARROW}; fill: context-stroke"></path></marker></defs>'
            f'<path d="{d}" marker-end="url(#{mid})"></path></svg>')

    def render(self, title, w, h, bg=WHITE):
        body = "\n".join(self.bands + self.arrows + self.cards + self.labels)
        return HEAD.format(title=e(title)) + f'<div style="position: relative; width: {w}px; height: {h}px; background: {bg}; overflow: hidden">\n{body}\n</div>\n' + TAIL.format(w=w, h=h)

def legend(b, x, y):
    b.text(x, y, 120, "Status", 13, INK3, weight=700)
    for i, (k, lbl) in enumerate([("built", "Built: in the repo and working"), ("proto", "Prototype: works, provisional"), ("planned", "Planned: decided, not built")]):
        word, fill, border = STATUS[k]
        b.cards.append(f'<div style="position: absolute; left: {x + i*250}px; top: {y+22}px; width: 22px; height: 22px; box-sizing: border-box; background: {fill}; border: {border}; border-radius: 6px"></div>')
        b.text(x + i*250 + 30, y + 23, 214, lbl, 13.5, INK2)

# ---------------------------------------------------------------- Main: system map
def main():
    W, H = 1760, 1420
    b = Board()
    b.text(64, 52, 1100, "How EV Shortlist works", 44, INK, "Bitter", 800)
    b.text(64, 112, 1100, "Open data goes in on the left. Our own checked and derived figures come out as a numbered release. The website only reads releases. First version, 15 Nov 2026, based on Master spec v2 and Decisions 001–052.", 17, INK2)
    legend(b, 1000, 52)
    # schema bar
    b.card(440, 168, 1240, 56, "One shared data shape: packages/schema", "ev.schema.json → generated TypeScript types for the website and Python models for the pipeline. Stable IDs: Make → Model → Generation → Variant.", "built")
    TOPS = [312 + 100 * i for i in range(7)]
    # column A: sources
    b.band(64, 256, 300, 740, SEA, "1 · Open data sources", "Free, licence-checked")
    srcs = [("Spec databases", "Open EV Data, KilowattApp, Wikidata, EPA"),
            ("Vehicle registers", "RDW (NL), KBA (DE), DfT (UK), CBS"),
            ("Type approval + CO₂", "EEA, ADEME, RDW type approvals"),
            ("Charging statistics", "EAFO, BNetzA, DfT, NDW, AFDC"),
            ("Climate + places", "ERA5-Land, Meteostat, GeoNames"),
            ("Loan rates", "ECB interest-rate statistics"),
            ("Seed catalogue", "Hand-entered top 40, cited by URL")]
    for i, (t, s) in enumerate(srcs):
        b.card(80, 312 + 96 * i, 268, 76, t, s, "built" if i != 5 else "proto")
    # column B: pipeline
    b.band(440, 256, 340, 740, SEA, "2 · Data pipeline (Python)", "ev refresh: one command, weekly")
    steps = [("Probe + fetch", "Only sources that changed"),
             ("Snapshot", "Raw copy, stored by content hash"),
             ("Normalise + match", "Each record → a seed variant"),
             ("Merge by field rules", "Agreeing sources raise confidence"),
             ("Derive our figures", "Winter range, charging, consumption"),
             ("Quality gate", "Blocking checks + licence gate"),
             ("Publish release N", "Atomic switch, one-step rollback")]
    for i, (t, s) in enumerate(steps):
        b.card(470, TOPS[i], 280, 56, t, s, "built")
        if i:
            b.arrow(610, TOPS[i-1] + 56, 610, TOPS[i] - 1, f"From {steps[i-1][0]} to {t}")
    b.arrow(364, 340, 469, 340, "From open data sources into Probe + fetch")
    # column C: outputs
    b.band(840, 256, 340, 740, SEA, "3 · What a release holds", "Numbered, checked, undoable")
    b.text(860, 316, 300, "Every value carries its source, date, confidence and licence. Disagreeing sources are never averaged: they go to review.", 15, INK2)
    b.text(860, 420, 300, "Releases move out of git to GitHub Releases, later object storage (Decision 035).", 15, INK2)
    b.card(856, TOPS[3], 308, 56, "Review queue", "Conflicts, source-health alerts", "built")
    b.card(856, TOPS[4], 308, 56, "Staff review page", "/staff/review", "proto")
    b.card(856, TOPS[5], 308, 56, "Open data bundle", "CSV + JSON, CC BY 4.0, at launch", "built")
    b.card(856, TOPS[6], 308, 56, "catalogue.json + Parquet", "Wide row per variant + coverage.md", "built")
    b.arrow(750, TOPS[3] + 28, 855, TOPS[3] + 28, "From Merge by field rules to Review queue, when sources disagree")
    b.arrow(1010, TOPS[3] + 56, 1010, TOPS[4] - 1, "From Review queue to Staff review page")
    b.arrow(750, TOPS[6] + 28, 855, TOPS[6] + 28, "From Publish release N to catalogue.json")
    b.arrow(1010, TOPS[6], 1010, TOPS[5] + 57, "From catalogue.json to Open data bundle")
    # column D: web
    b.band(1240, 256, 440, 740, SEA, "4 · Website (Next.js + TypeScript)", "Reads releases, never writes catalogue data")
    web = [("Visitor", "5 countries · 6 languages · light + dark"),
           ("In the browser", "Filters in the URL, compare tray, detail switch"),
           ("Pages rendered on the server", "/[country]/[lang]/… hero, explore, cars, compare"),
           ("Catalogue interface", "lib/catalogue.ts: JSON now, Postgres later")]
    for i, (t, s) in enumerate(web):
        b.card(1260, TOPS[3 + i], 400, 56, t, s, "built" if i else "none")
        if i:
            b.arrow(1460, TOPS[3 + i], 1460, TOPS[2 + i] + 57, f"From {t} up to {web[i-1][0]}")
    b.arrow(1164, TOPS[6] + 28, 1259, TOPS[6] + 28, "From catalogue.json to the Catalogue interface")
    b.text(1260, 316, 400, "Launch scope (Decision 051): a three-step hero (country → profile → budget) that returns a top 10 with the top 5 as your shortlist, plus the full catalogue: Explore, car pages, Compare up to 4, /learn.", 15, INK2)
    b.text(1260, 450, 400, "Ranking = shortlist rules as data rows, back-tested on Menno's picks (Decision 038, 050).", 15, INK2)
    # rules row
    b.band(440, 1040, 1240, 140, "#F2F6FA", "Rules live in data files, not code", "Change a row, not a function")
    rules = [("sources.yaml", "Every source, licence, cadence, status"), ("field_sources.yaml", "Per field: primary, fallback, tolerance"),
             ("taxonomy/*.yaml", "Chemistries, voltage classes, glossary"), ("editorial/", "Shortlist rules + owner picks")]
    for i, (t, s) in enumerate(rules):
        b.card(460 + i * 302, 1096, 286, 64, t, s, "built")
    b.arrow(610, 1040, 610, 997, "From the rule files up into the data pipeline")
    # hosting row
    b.band(64, 1220, 1616, 140, "#F2F6FA", "Where it runs", "Decisions 005, 006, 035")
    host = [("GitHub", "Code, CI, weekly data-refresh PRs, images", "built"),
            ("Shared AppInfra server", "Hetzner Arm, Caddy, ev-web 768 MB", "planned"),
            ("Night jobs", "ev-jobs 1 GB, pg-boss, 00:30–02:30 UTC", "planned"),
            ("Postgres 17 + PostGIS", "Own database on the shared server", "planned"),
            ("Object storage", "Scaleway: snapshots + releases", "planned")]
    for i, (t, s, st) in enumerate(host):
        b.card(84 + i * 318, 1276, 302, 64, t, s, st)
    return b.render("How EV Shortlist works", W, H)

# ---------------------------------------------------------------- Data model
def model():
    W, H = 1440, 900
    b = Board()
    b.text(64, 52, 1200, "Inside one car's numbers", 40, INK, "Bitter", 800)
    b.text(64, 108, 1200, "The catalogue is a family tree. Shared hardware (platform, battery pack) is stored once and inherited. Every number is a Fact that remembers where it came from.", 17, INK2)
    y = 200
    tree = [("Make", "Kia"), ("Model", "Niro EV"), ("Generation", "1st gen, 2018–2022"), ("Variant", "64 kWh, 150 kW")]
    xs = [64, 384, 704, 1024]
    for i, (t, ex) in enumerate(tree):
        b.card(xs[i], y, 256, 72, t, f"e.g. {ex} (illustration)", "built")
        if i:
            b.arrow(xs[i-1] + 256, y + 36, xs[i] - 1, y + 36, f"From {tree[i-1][0]} to {t}, one to many")
    # shared hardware
    b.card(704, 360, 256, 72, "Platform", "Shared base, voltage class", "built")
    b.card(1024, 360, 256, 72, "Battery pack", "Chemistry, kWh, cooling, warranty", "built")
    b.arrow(1152, 359, 1152, 273, "From Battery pack up to Variant: the variant inherits pack facts")
    b.arrow(832, 359, 832, 273, "From Platform up to Generation")
    b.text(64, 372, 560, "Pack facts are inherited by every variant that uses the pack, unless the variant has its own measured value (Decision 010). Taxonomies like chemistries are data files, so a new chemistry needs no code change.", 15, INK2)
    # fact
    b.band(64, 500, 1312, 336, SEA, "A Fact: one number with its paper trail", "Data rule 1: every number is traceable")
    facts = [("value + unit", "e.g. usable kWh, metric internally"), ("source + retrieval date", "From sources.yaml"),
             ("confidence", "Raised when sources agree"), ("licence", "Gate: only open sources reach a release")]
    for i, (t, s) in enumerate(facts):
        b.card(84 + i * 322, 580, 306, 72, t, s, "built")
    more = [("agreeing sources", "N sources agree within tolerance"), ("fallback rung", "measured → platform → physics → WLTP ratio"),
            ("estimate flag", "Estimates are labelled in the UI"), ("charge curve", "SoC % → kW points, 10–80 % minutes")]
    for i, (t, s) in enumerate(more):
        b.card(84 + i * 322, 676, 306, 72, t, s, "built")
    b.text(84, 772, 1260, "Published as a wide PublishedVariant row per variant in catalogue.json; the website shows the value, and Nerd mode shows the source, date, confidence and rung.", 15, INK2)
    return b.render("Inside one car's numbers", W, H)

# ---------------------------------------------------------------- Tech board (grid page)
def section(title, inner, span=1):
    return (f'<section style="grid-column: span {span}; background: #FFFFFF; border: 1px solid {LINE}; border-radius: 18px; padding: 24px 26px; display: flex; flex-direction: column; gap: 12px">'
            f'<h2 style="margin: 0; font-family: Bitter; font-weight: 800; font-size: 22px; line-height: 28px; color: {INK}">{e(title)}</h2>{inner}</section>')

def table(head, rows, widths=None):
    th = "".join(f'<th style="text-align: left; padding: 6px 10px 6px 0; font-size: 13px; color: {INK3}; font-weight: 700; border-bottom: 1px solid {LINE}">{e(h)}</th>' for h in head)
    tr = ""
    for r in rows:
        tr += "<tr>" + "".join(f'<td style="padding: 7px 10px 7px 0; border-bottom: 1px solid #EEF2F6; vertical-align: top">{c}</td>' for c in r) + "</tr>"
    return f'<table style="border-collapse: collapse; width: 100%; font-size: 14.5px; line-height: 20px; color: {INK}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'

def pill(k):
    word, fill, border = STATUS[k]
    return f'<span style="display: inline-block; padding: 2px 8px; border-radius: 6px; background: {fill}; border: {border}; font-size: 12px; font-weight: 700; color: {INK}">{word}</span>'

def code(s):
    return f'<code style="font-family: ui-monospace, Menlo, monospace; font-size: 13px; background: #F2F6FA; padding: 1px 5px; border-radius: 4px; color: {INK}">{e(s)}</code>'

def tech():
    W, H = 1440, 2560
    secs = []
    secs.append(section("Frameworks and libraries", table(["Part", "What we use", "Why"], [
        ["Website", "Next.js 16, React 19, TypeScript (strict)", "Server-rendered pages, good SEO, one language front to back"],
        ["Styling", "Tailwind CSS 4 + design tokens", "Colours come from tokens.json; themes switch before paint"],
        ["Web tests", "Vitest, Playwright, axe-core", "Units, key flows, accessibility in both themes"],
        ["Pipeline", "Python 3.12, pydantic 2, DuckDB, PyArrow", "Typed records, fast local analytics, Parquet output"],
        ["Pipeline I/O", "httpx, PyYAML, jsonschema, openpyxl", "Fetching, rule files, validation, KBA's .xlsx files"],
        ["Pipeline tests", "pytest, ruff", "Every data rule has a test; tests never call the network"],
        ["Shared types", "JSON Schema → generated TS + Python", "One source of truth for the data shape"],
        ["Packages", "pnpm (web), uv (pipeline)", "Fast, locked installs; 3-day minimum age (Decision 052)"],
        ["Jobs (planned)", "pg-boss on Postgres", "No Redis; same server as the database"],
    ])))
    secs.append(section("Code map", table(["Folder", "What lives there"], [
        [code("apps/web/src/app/[country]/[lang]"), "All public pages: home/hero, ev/[make]/[model]/[generation]/[variant], compare, top, learn, charging, about"],
        [code("apps/web/src/lib"), "catalogue.ts (read interface), budget, compare store, charging links and stats"],
        [code("apps/web/src/components"), "Explore, CompareTable, CompareTray, SpecDiff, PriceBand, PriceMode, LevelGate, Term (tooltips), trip/"],
        [code("apps/web/src/i18n"), "en, nl, de, fr, es, it message files + coverage tests"],
        [code("pipeline/ev_pipeline/sources"), "One adapter per source (20): rdw, eea, ademe, kba_fz10, eafo, era5_land …"],
        [code("pipeline/ev_pipeline/match · merge · derive"), "Match records to seed variants, merge by field rules, derive our own figures"],
        [code("pipeline/ev_pipeline/qa · release · opendata"), "Blocking checks, licence gate, release build + publish, CC BY bundle"],
        [code("packages/schema"), "ev.schema.json and the generated types"],
        [code("data/"), "sources.yaml, field_sources.yaml, seed/, taxonomy/, editorial/, review/, releases/"],
        [code("infra/deploy"), "compose.ev.yml + Caddy snippet (written, not applied yet)"],
    ])))
    srows = [
        ["Open EV Data", "Specs", "CDLA-Permissive-2.0", pill("built")],
        ["KilowattApp Open EV Data", "Specs", "MIT with attribution", pill("built")],
        ["Wikidata", "Specs, years", "CC0", pill("built")],
        ["EPA fueleconomy.gov", "Range, consumption (back-test)", "US public domain", pill("built")],
        ["RDW (NL) + type approvals + APK defects", "Registrations, specs, faults", "CC0 (attribution question open)", pill("built")],
        ["EEA CO₂ monitoring", "Type-approval values", "CC BY 4.0", pill("built")],
        ["ADEME Car Labelling (FR)", "Type-approval values", "Licence Ouverte 2.0", pill("built")],
        ["KBA FZ10 (DE)", "New registrations", "dl-de/by-2-0", pill("built")],
        ["DfT vehicles + charging (UK)", "Registrations, chargers", "OGL v3", pill("built")],
        ["EAFO (EU)", "Chargers per power level", "CC BY 4.0, confirming", pill("proto")],
        ["BNetzA (DE), NDW (NL), AFDC (US)", "Charger statistics", "CC BY 4.0 / CC0", pill("built")],
        ["ERA5-Land, Meteostat, GeoNames", "Winter temperatures, towns", "CC BY 4.0", pill("built")],
        ["ECB MIR", "Typical loan rates", "ECB reuse terms", pill("proto")],
        ["Bjørn Nyland, Fastned, NAF, Spritmonitor", "Real-world tests", "Asking permission", pill("planned")],
        ["ADAC, Euro NCAP, InsideEVs, Aviloo …", "Tests, battery data", "Blocked: no open licence", f'<span style="font-size: 13px; font-weight: 700; color: #A1224A">Blocked</span>'],
    ]
    secs.append(section("Data sources (from data/sources.yaml)", table(["Source", "Gives us", "Licence", "Status"], srows) +
        f'<p style="margin: 0; font-size: 14px; line-height: 20px; color: {INK2}">Only active sources with a named licence or written permission reach a public release (Decision 009). Marketplaces are never scraped (Decision 004).</p>', 2))
    secs.append(section("How a number gets made", f'<ol style="margin: 0; padding-left: 20px; font-size: 15px; line-height: 23px; color: {INK}">'
        "<li><b>Fetch</b> only sources that changed (hash, HTTP 304, git commit).</li>"
        "<li><b>Match</b> each record to a seed variant; unclear matches go to review.</li>"
        "<li><b>Merge</b> per field: agreeing sources outvote a single priority value (Decision 025); a cited value beats a lone source (028).</li>"
        "<li><b>Guard</b>: battery gate (027), mix-up check (029), conflicts never averaged.</li>"
        "<li><b>Derive</b> real summer and winter range, consumption per road and temperature band, charging minutes and km added in 20 minutes.</li>"
        "<li><b>Back-test</b> against EPA: 7.6 % median error on 60 variants (audit A-30).</li>"
        "<li><b>Publish</b> after the quality gate passes; rollback is one command.</li></ol>"))
    secs.append(section("Commands", table(["Command", "Does"], [
        [code("ev refresh [--sources …] [--dry-run]"), "Runs every due source end to end"],
        [code("ev release diff <a> <b>"), "Explains what changed between releases"],
        [code("ev release rollback --to <n>"), "Points latest back to an older release"],
        [code("ev sources accept <id>"), "Accepts a source whose format changed"],
        [code("pnpm --filter @ev/web dev"), "Runs the website locally"],
        [code("python -m ev_pipeline.backtest"), "Compares our figures with EPA tests"],
    ])))
    secs.append(section("Data rules (non-negotiable)", f'<ul style="margin: 0; padding-left: 20px; font-size: 15px; line-height: 23px; color: {INK}">'
        "<li>Every number is traceable: source, date, confidence, licence.</li>"
        "<li>Derived, not copied: never republish another site's tables.</li>"
        "<li>Licences stay separate: ODbL (OpenStreetMap) never mixes into CC BY output.</li>"
        "<li>Raw data is not committed; only small fixtures.</li>"
        "<li>AI proposes, rules decide; uncertain values go to review.</li>"
        "<li>Metric internally (km, kWh, Wh/km, kW, °C, €).</li></ul>"))
    secs.append(section("Hosting and limits (Decision 006)", table(["Piece", "Limit"], [
        ["ev-web", "768 MB, 1 CPU"], ["ev-web-staging", "256 MB, 0.5 CPU"], ["ev-jobs", "1 GB, 1 CPU, nightly 00:30–02:30 UTC (to confirm)"],
        ["Postgres connections", "10 live, 3 staging, 3 jobs (of 100)"], ["Grow when", "evenings above 70 % RAM or CPU for weeks"],
    ]) + f'<p style="margin: 0; font-size: 14px; line-height: 20px; color: {INK2}">Images build in GitHub Actions for Arm and deploy over SSH; the server never builds (Decision 005).</p>'))
    secs.append(section("Privacy and security", f'<ul style="margin: 0; padding-left: 20px; font-size: 15px; line-height: 23px; color: {INK}">'
        "<li>Public repo: no secrets, no partner rates or sampling targets in it.</li>"
        "<li>Strict content security policy: no inline scripts.</li>"
        "<li>User data in its own schema; GDPR export and delete.</li>"
        "<li>Cookieless analytics (Umami) only.</li>"
        "<li>Hardened containers: read-only, no extra privileges.</li></ul>"))
    secs.append(section("Not built yet, in order", f'<ol style="margin: 0; padding-left: 20px; font-size: 15px; line-height: 23px; color: {INK}">'
        "<li>Releases out of git (T-064).</li><li>Shortlist rules scored in the release, hero result page (T-066–T-069).</li>"
        "<li>Server deploy on AppInfra, Postgres, pg-boss jobs.</li><li>Used price bands per country.</li>"
        "<li>After launch: Trip fit routing (Valhalla box), accounts, lease figures.</li></ol>"))
    grid = "".join(secs)
    body = (f'<div style="width: {W}px; min-height: {H}px; box-sizing: border-box; padding: 64px; background: #F7F9FC; font-family: \'Atkinson Hyperlegible\'; color: {INK}; display: flex; flex-direction: column; gap: 28px">'
            f'<header style="display: flex; flex-direction: column; gap: 8px"><h1 style="margin: 0; font-family: Bitter; font-weight: 800; font-size: 44px; line-height: 52px">Tech board</h1>'
            f'<p style="margin: 0; font-size: 17px; line-height: 26px; color: {INK2}; max-width: 980px">Libraries, sources, code and rules behind EV Shortlist. A first version from the repo as of 15 Nov 2026; folder names and decision numbers point to the repo for detail.</p></header>'
            f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; align-items: start">{grid}</div></div>')
    return HEAD.format(title="Tech board") + body + "\n" + TAIL.format(w=W, h=H)

if __name__ == "__main__":
    open(f"{P}/Main.dc.html", "w").write(main())
    open(f"{P}/DataModel.dc.html", "w").write(model())
    open(f"{P}/TechBoard.dc.html", "w").write(tech())
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    canvas = {"v": 3, "createdOnFiles": {"v": 1, "at": now}, "title": "EV Shortlist — architecture",
              "launch": {"view": "canvas"}, "pages": [],
              "boards": {"Main.dc.html": {"x": 0, "y": 0, "w": 1760, "h": 1420, "title": "System map"},
                         "DataModel.dc.html": {"x": 1840, "y": 0, "w": 1440, "h": 900, "title": "Data model"},
                         "TechBoard.dc.html": {"x": 3360, "y": 0, "w": 1440, "h": 2560, "title": "Tech board"}},
              "order": ["Main.dc.html", "DataModel.dc.html", "TechBoard.dc.html"],
              "notes": {"t1": {"x": 0, "y": -300, "text": "EV Shortlist — architecture, first version", "kind": "title1", "maxW": 4800}},
              "designSystems": [{"title": "EV Shortlist", "namespace": "evshortlist", "artifact": "https://claude.ai/artifact/EiqvMW5NcFgxFq6c5YHuPP", "version": "1794736101-5282", "copiedAt": now}]}
    json.dump(canvas, open(f"{P}/canvas.json", "w"), indent=1, ensure_ascii=False)
