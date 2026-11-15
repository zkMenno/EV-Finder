"""Solarpunk illustration kit sheet: elements, palette with contrast, day + night scenes."""
import math, subprocess
from round1 import FONTS, render, OUT

def lum(h):
    h = h.lstrip('#'); c = [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
    c = [x/12.92 if x <= .03928 else ((x+.055)/1.055)**2.4 for x in c]
    return .2126*c[0] + .7152*c[1] + .0722*c[2]
def cr(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True); return (la+.05)/(lb+.05)

DAY = dict(name="Day trip", bg="#FBFAF6", sky="#E8F1F9", line="#16233A", h1="#EEF6E8", h2="#DDEFD3", h3="#C7E4B8",
           r1="#B9DCA6", r2="#7BB661", r3="#4E9A3F", leaf="#B9DCA6", leafr="#3F8A3A", wall="#FFFFFF", roof="#FFF2CC",
           roofr="#F0BE45", solar="#2F679C", door="#FFD166", window="#CFE3F3", car="#3B78AE", road="#FFFFFF", sun="#FFD166",
           grid="#D6DFEA", trunk="#16233A")
NIGHT = dict(name="Night drive", bg="#111A2B", sky="#111A2B", line="#EEF3F9", h1="#18263A", h2="#1C2F35", h3="#21382F",
             r1="#1F3324", r2="#284A2E", r3="#2F5A33", leaf="#2B4A33", leafr="#2F6B35", wall="#22324D", roof="#3A3320",
             roofr="#6B5520", solar="#3B78AE", door="#FFD166", window="#FFD166", car="#93C1EA", road="#2A3A57", sun="#FFE7A3",
             grid="#2A3A57", trunk="#EEF3F9")

def st(t, w=2): return f'stroke="{t["line"]}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'

# ---- elements (each drawn around a local origin) ----
def house(t, rich=False):
    s = st(t)
    return (f'<g {s}><rect x="0" y="18" width="62" height="40" fill="{t["wall"]}"/>'
            f'<path d="M-6 20 L31 -4 L68 20Z" fill="{t["roofr"] if rich else t["roof"]}"/>'
            f'<path d="M34 -1 L64 18 L50 18 L24 4Z" fill="{t["solar"]}" stroke-width="1.5"/>'
            f'<path d="M37 4 L44 9 M42 1 L52 8" stroke-width="1"/>'
            f'<rect x="10" y="32" width="12" height="26" fill="{t["door"]}"/><rect x="34" y="30" width="16" height="12" fill="{t["window"]}"/></g>')

def wallbox(t):
    return (f'<g {st(t)}><rect width="16" height="26" rx="5" fill="{t["wall"]}"/><path d="M9 5 L5 13 H8.5 L7 21 L12 12 H8.5Z" fill="{t["sun"]}" stroke-width="1.2"/>'
            f'<path d="M8 26 Q8 40 22 40" fill="none"/></g>')

def charger(t):
    return (f'<g {st(t)}><rect x="0" y="0" width="26" height="48" rx="6" fill="{t["wall"]}"/><rect x="5" y="6" width="16" height="11" rx="2" fill="{t["window"]}"/>'
            f'<path d="M14 22 L9 31 H13 L11 40 L17 29 H13Z" fill="{t["sun"]}" stroke-width="1.2"/><path d="M26 30 Q36 30 36 44 V54" fill="none"/>'
            f'<rect x="-4" y="48" width="34" height="6" rx="2" fill="{t["line"]}"/></g>')

def turbine(t, a=20):
    return (f'<g {st(t, 2.4)}><path d="M-2 0 L-3 62 H3 L2 0Z" fill="{t["wall"]}" stroke-width="2"/>' +
            "".join(f'<path d="M0 0 Q4 -14 0 -30 Q-3 -14 0 0Z" transform="rotate({a+i*120})" fill="{t["wall"]}" stroke-width="2"/>' for i in range(3)) +
            f'<circle r="4" fill="{t["wall"]}"/></g>')

def tree(t, r=14, rich=False):
    return f'<g {st(t)}><line x1="0" y1="0" x2="0" y2="{r+10}" stroke="{t["trunk"]}"/><circle r="{r}" fill="{t["leafr"] if rich else t["leaf"]}"/></g>'

def poplar(t, rich=False):
    return f'<g {st(t)}><line x1="0" y1="10" x2="0" y2="38"/><path d="M0 -26 Q12 0 0 30 Q-12 0 0 -26Z" fill="{t["leafr"] if rich else t["leaf"]}"/></g>'

def car(t, lights=False):
    s = (f'<g {st(t)}><path d="M0 22 Q2 9 16 8 L24 -2 Q27 -6 34 -6 H50 Q58 -6 62 0 L69 8 Q80 9 80 19 V27 H0Z" fill="{t["car"]}"/>'
         f'<path d="M28 6 L33 -1 H42 V6Z M47 6 V-1 H54 L59 6Z" fill="{t["window"] if not lights else "#22324D"}" stroke-width="1.5"/>'
         f'<circle cx="19" cy="27" r="7.5" fill="{t["wall"]}"/><circle cx="61" cy="27" r="7.5" fill="{t["wall"]}"/>')
    if lights:
        s += f'<path d="M80 14 L130 4 L130 30 Z" fill="#FFD166" opacity=".22" stroke="none"/><circle cx="77" cy="15" r="2.5" fill="#FFD166" stroke="none"/>'
    return s + '</g>'

def van(t):
    return (f'<g {st(t)}><path d="M0 26 V0 Q0 -8 8 -8 H52 Q60 -8 64 0 L74 12 Q80 13 80 20 V26Z" fill="{t["roofr"]}"/>'
            f'<path d="M52 2 V-2 H60 L66 8 H52Z" fill="{t["window"]}" stroke-width="1.5"/><circle cx="18" cy="27" r="7.5" fill="{t["wall"]}"/><circle cx="62" cy="27" r="7.5" fill="{t["wall"]}"/></g>')

def solarfield(t):
    s = f'<g {st(t, 1.6)}>'
    for i in range(3):
        s += f'<path d="M{i*30} 20 L{i*30+10} 0 H{i*30+34} L{i*30+24} 20Z" fill="{t["solar"]}"/><line x1="{i*30+17}" y1="20" x2="{i*30+17}" y2="30"/>'
    return s + '</g>'

def sun(t, night=False):
    if night:
        return (f'<g {st(t)}><path d="M14 -22 A24 24 0 1 0 22 14 A18 18 0 1 1 14 -22Z" fill="{t["sun"]}"/></g>' +
                "".join(f'<path d="M{x} {y} l0 -5 M{x} {y} l0 5 M{x} {y} l-5 0 M{x} {y} l5 0" stroke="{t["line"]}" stroke-width="1.5" stroke-linecap="round"/>' for x, y in [(-60, -10), (50, -30), (70, 20)]))
    return (f'<circle r="24" fill="{t["sun"]}" {st(t)}/>' + "".join(
        f'<line x1="{30*math.cos(math.radians(a)):.1f}" y1="{30*math.sin(math.radians(a)):.1f}" x2="{38*math.cos(math.radians(a)):.1f}" y2="{38*math.sin(math.radians(a)):.1f}" {st(t)}/>' for a in range(0, 360, 30)))

def bez(p0, p1, p2, p3, n=30):
    return [tuple((1-u)**3*a+3*(1-u)**2*u*b+3*(1-u)*u*u*c+u**3*d for a, b, c, d in zip(p0, p1, p2, p3)) for u in [i/n for i in range(n+1)]]

def road_winding(t, P, w0=46, w1=6):
    pts = []
    for i in range(0, len(P)-1, 3): pts += bez(*P[i:i+4])
    N = len(pts)
    seg = lambda col, add: "".join(f'<line x1="{pts[i][0]:.1f}" y1="{pts[i][1]:.1f}" x2="{pts[i+1][0]:.1f}" y2="{pts[i+1][1]:.1f}" stroke="{col}" stroke-width="{w0-(w0-w1)*i/N+add:.1f}" stroke-linecap="round"/>' for i in range(N-1))
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts[:int(N*.85)])
    return seg(t["line"], 4) + seg(t["road"], 0) + f'<path d="{d}" stroke="{t["line"]}" stroke-width="1.8" fill="none" stroke-dasharray="8 8"/>'

def road_straight(t, w=200):
    return (f'<rect x="0" y="0" width="{w}" height="26" fill="{t["road"]}" {st(t)}/>'
            f'<line x1="8" y1="13" x2="{w-8}" y2="13" stroke="{t["line"]}" stroke-width="1.8" stroke-dasharray="8 8"/>')

def road_bend(t):
    return (f'<path d="M0 0 H40 Q80 0 80 40 V80" fill="none" stroke="{t["line"]}" stroke-width="30"/>'
            f'<path d="M0 0 H40 Q80 0 80 40 V80" fill="none" stroke="{t["road"]}" stroke-width="26"/>'
            f'<path d="M0 0 H40 Q80 0 80 40 V80" fill="none" stroke="{t["line"]}" stroke-width="1.8" stroke-dasharray="8 8"/>')

# ---- composed scene (the B+C hero) ----
def scene(t, rich, night=False):
    s = '<defs><filter id="sh" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="3" stdDeviation="2" flood-color="#000" flood-opacity=".18"/></filter></defs>'
    s += f'<rect width="390" height="460" fill="{t["sky"] if (rich or night) else t["bg"]}"/>'
    if not night:
        s += "".join(f'<path d="M-10 {40+i*12} Q 90 {15+i*12} 180 {50+i*10} T 400 {25+i*12}" stroke="{t["grid"]}" fill="none" stroke-width="1"/>' for i in range(4))
    s += f'<g transform="translate(290 105)">{sun(t, night)}</g>'
    H = (t["r1"], t["r2"], t["r3"]) if rich else (t["h1"], t["h2"], t["h3"])
    s += f'<path d="M-10 230 Q 80 160 170 205 Q 260 150 400 200 V460 H-10Z" fill="{H[0]}" {st(t)} filter="url(#sh)"/>'
    for x, y, sc, a in [(95, 182, .75, 20), (132, 178, .85, 70), (330, 170, .8, 40)]:
        s += f'<g transform="translate({x} {y}) scale({sc})">{turbine(t, a)}</g>'
    s += f'<path d="M-10 290 Q 120 230 230 275 Q 320 310 400 260 V460 H-10Z" fill="{H[1]}" {st(t)} filter="url(#sh)"/>'
    s += f'<g transform="translate(300 228) scale(.8)">{solarfield(t)}</g>'
    s += f'<path d="M-10 360 Q 100 320 200 350 Q 300 380 400 340 V460 H-10Z" fill="{H[2]}" {st(t)} filter="url(#sh)"/>'
    s += road_winding(t, [(175, 475), (200, 410), (300, 405), (275, 352), (250, 318), (160, 326), (185, 292), (200, 274), (230, 265), (241, 254)])
    s += f'<g transform="translate(40 300)">{house(t, rich)}</g><g transform="translate(110 334)">{wallbox(t)}</g>'
    s += f'<g transform="translate(252 393)">{car(t, night)}</g>'
    for x, y, r in [(345, 298, 14), (368, 312, 11), (22, 395, 13), (340, 425, 13)]:
        s += f'<g transform="translate({x} {y})">{tree(t, r, rich)}</g>'
    return s

# ---- sheet ----
def cell(svg, label, t, w=150, h=150, vb="-75 -75 150 150"):
    return (f'<figure class="cell" style="background:{t["bg"]}"><svg viewBox="{vb}" width="{w}" height="{h}">{svg}</svg>'
            f'<figcaption style="color:{t["line"]}">{label}</figcaption></figure>')

def elements(t, night=False):
    c = [cell(f'<g transform="translate(-31 -22)">{house(t)}</g>', "House + solar roof", t),
         cell(f'<g transform="translate(-31 -22)">{house(t, True)}</g>', "House, rich roof", t),
         cell(f'<g transform="translate(-14 -16) scale(1.3)">{wallbox(t)}</g>', "Home wallbox", t),
         cell(f'<g transform="translate(-16 -30)">{charger(t)}</g>', "Public charger", t),
         cell(f'<g transform="translate(0 -18)">{turbine(t)}</g>', "Wind turbine", t),
         cell(f'<g transform="translate(-48 -6)">{solarfield(t)}</g>', "Solar field", t),
         cell(f'<g transform="translate(-26 -8)">{tree(t)}</g><g transform="translate(24 -16)">{poplar(t)}</g>', "Trees, soft", t),
         cell(f'<g transform="translate(-26 -8)">{tree(t, 14, True)}</g><g transform="translate(24 -16)">{poplar(t, True)}</g>', "Trees, rich", t),
         cell(f'<g transform="translate(-40 -10)">{car(t, night)}</g>', "Toy EV" + (" + lights" if night else ""), t),
         cell(f'<g transform="translate(-40 -10)">{van(t)}</g>', "Toy EV van", t),
         cell(f'<g transform="translate(-60 -30)">{road_bend(t)}</g>', "Road bend", t),
         cell(f'<g transform="translate(-70 -13) scale(.7 1)">{road_straight(t)}</g>', "Road straight", t),
         cell(road_winding(t, [(0, 70), (10, 30), (60, 30), (40, 0), (25, -20), (-30, -20), (-10, -45)], 30, 6), "Road into distance", t),
         cell(f'<g>{sun(t, night)}</g>', "Moon + stars" if night else "Sun", t)]
    return "".join(c)

def swatches():
    rows = [("Leaf tint (soft hills)", "#EEF6E8"), ("Fern tint", "#DDEFD3"), ("Sage tint", "#C7E4B8"),
            ("Meadow light (rich)", "#B9DCA6"), ("Meadow (existing)", "#7BB661"), ("Leaf (rich)", "#4E9A3F"),
            ("Forest (rich trees)", "#3F8A3A"), ("Solar gold (roofs)", "#F0BE45"), ("Sunflower (existing)", "#FFD166")]
    out = ""
    for n, h in rows:
        r = cr(h, "#16233A")
        out += (f'<div class="sw"><div class="chip" style="background:{h}"></div><b>{n}</b><span>{h}</span>'
                f'<span>ink line {r:.1f}:1 {"✓" if r >= 3 else "✗"}</span></div>')
    return out

CSS = FONTS + """body{margin:0;background:#E3E8EE;font-family:Atkinson;color:#16233A;padding:36px;width:1530px}
h1{font:800 34px Bitter;margin:0 0 6px} h2{font:800 22px Bitter;margin:30px 0 12px} p{margin:0 0 6px;color:#45546F;font-size:16px}
.row{display:grid;grid-template-columns:repeat(7,1fr);gap:10px}
.cell{margin:0;border-radius:14px;padding:8px;display:flex;flex-direction:column;align-items:center;border:1px solid #c9d3df}
figcaption{font-size:14px;font-weight:700;margin-top:2px}
.scenes{display:flex;gap:20px;align-items:flex-start}.scenes figure{margin:0}.scenes svg{border-radius:18px;display:block}
.scenes figcaption{color:#16233A;margin-top:6px}
.sws{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.sw{display:grid;grid-template-columns:44px 1fr auto auto;gap:10px;align-items:center;background:#fff;border-radius:10px;padding:8px 12px;font-size:14px}
.sw span{color:#45546F}.chip{width:44px;height:30px;border-radius:6px;border:2px solid #16233A}"""

html = (f"<!doctype html><style>{CSS}</style><body><h1>Illustration kit · round 1</h1>"
        "<p>B + C style: ink line, rounded shapes, flat fills, soft paper shadow under hills. Rich colour = home hero only; soft = everywhere else.</p>"
        "<h2>Scenes</h2><div class='scenes'>" +
        "".join(f"<figure><svg viewBox='0 0 390 460' width='350' height='413'>{scene(t, r, n)}</svg><figcaption>{c}</figcaption></figure>"
                for t, r, n, c in [(DAY, False, False, "Day trip · soft (pages)"), (DAY, True, False, "Day trip · rich (home hero)"),
                                   (NIGHT, False, True, "Night drive · soft"), (NIGHT, True, True, "Night drive · rich")]) +
        "</div><h2>Elements · Day trip</h2><div class='row'>" + elements(DAY) +
        "</div><h2>Elements · Night drive</h2><div class='row'>" + elements(NIGHT, True) +
        "</div><h2>New secondary colours (illustration only, never text)</h2><div class='sws'>" + swatches() + "</div></body>")
render(html, "kit-r1", 1602, 1740)
