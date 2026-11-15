"""Solarpunk x EV round 1: three illustration directions rendered as phone heroes."""
import math, os, subprocess
R = "/home/claude/zkmenno/ev-finder/docs/design"
OUT = "/home/claude/sp/out"; os.makedirs(OUT, exist_ok=True)
LOGO = open(f"{R}/assets/Logo/lockup-light.svg").read().replace('width="262" height="48"', 'width="175" height="32"')
FONTS = "".join(
    f"@font-face{{font-family:'{n}';src:url(file://{R}/fonts/{f});font-weight:{w}}}"
    for n, f, w in [("Bitter", "bitter-latin-800-normal.woff2", 800), ("Bitter", "bitter-latin-700-normal.woff2", 700),
                    ("Atkinson", "atkinson-hyperlegible-latin-400-normal.woff2", 400),
                    ("Atkinson", "atkinson-hyperlegible-latin-700-normal.woff2", 700),
                    ("Patrick", "patrick-hand-latin-400-normal.woff2", 400)])
INK, SKY, ACTION, SUN = "#16233A", "#3B78AE", "#2F679C", "#FFD166"

# ---------- shared bits ----------
def rr(x, y, w, h, r, fill, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" {extra}/>'

ROAD = "M -20 330 H 110 Q 150 330 150 290 V 175 Q 150 135 190 135 H 290 Q 330 135 330 175 V 400 Q 330 440 290 440 H -20"
SPUR = "M 150 230 H 410"

# ---------- A: Play mat (true top-down, bright, toy-like) ----------
def car_top(x, y, rot, body, s=1.0):
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})">'
            f'{rr(-13,-21,6,10,2,"#2b2f36")}{rr(7,-21,6,10,2,"#2b2f36")}{rr(-13,11,6,10,2,"#2b2f36")}{rr(7,11,6,10,2,"#2b2f36")}'
            f'{rr(-11,-24,22,48,9,body)}{rr(-8,-14,16,9,3,"#cfe3f3")}{rr(-8,8,16,7,3,"#cfe3f3")}'
            f'<circle cx="0" cy="-1" r="3.2" fill="{SUN}"/><path d="M-1 -3 L1.4 -1 L-0.6 0 L1 2" stroke="{INK}" stroke-width="0.9" fill="none"/></g>')

def house_top(x, y, w, h, roof, solar=True):
    s = f'<g transform="translate({x} {y})">{rr(3,4,w,h,4,"rgba(22,35,58,.16)")}{rr(0,0,w,h,4,roof)}'
    s += f'<line x1="{w/2}" y1="0" x2="{w/2}" y2="{h}" stroke="rgba(0,0,0,.18)" stroke-width="1.5"/>'
    if solar:
        pw, ph = w/2 - 8, h - 12
        s += rr(w/2 + 4, 6, pw, ph, 2, "#1f4f80")
        for i in range(1, 3): s += f'<line x1="{w/2+4}" y1="{6+ph*i/3}" x2="{w/2+4+pw}" y2="{6+ph*i/3}" stroke="#7fb0de" stroke-width=".8"/>'
        s += f'<line x1="{w/2+4+pw/2}" y1="6" x2="{w/2+4+pw/2}" y2="{6+ph}" stroke="#7fb0de" stroke-width=".8"/>'
    return s + "</g>"

def tree_top(x, y, r, c1, c2):
    return (f'<circle cx="{x+3}" cy="{y+4}" r="{r}" fill="rgba(22,35,58,.15)"/><circle cx="{x}" cy="{y}" r="{r}" fill="{c1}"/>'
            f'<circle cx="{x-r*.3}" cy="{y-r*.3}" r="{r*.45}" fill="{c2}"/>')

def turbine_top(x, y, a):
    blades = "".join(f'<path d="M0 0 L-3 -26 Q0 -30 3 -26 Z" transform="rotate({a+i*120})" fill="#fff" stroke="#b9c6d6" stroke-width="1"/>' for i in range(3))
    return f'<g transform="translate({x} {y})"><circle r="6" fill="rgba(22,35,58,.15)" cx="3" cy="3"/>{blades}<circle r="4.5" fill="#e8eef5" stroke="#8091ab"/></g>'

def charger_top(x, y):
    return (f'<g transform="translate({x} {y})">{rr(-9,-12,18,24,5,"#ffffff","stroke=\'#16233A\' stroke-width=\'2\'")}'
            f'<path d="M1 -7 L-4 1 H0 L-1 7 L4 -1 H0 Z" fill="{SKY}"/></g>')

def scene_a():
    g, g2 = "#8CC56B", "#A6D58A"
    s = f'<rect width="390" height="460" fill="{g}"/>'
    s += '<path d="M0 0 H390 V40 Q300 70 200 50 Q100 30 0 60Z" fill="#A6D58A"/>'
    # lake
    s += '<g transform="translate(0 22)"><path d="M200 270 Q215 205 265 215 Q300 225 300 265 Q298 310 255 312 Q205 312 200 270Z" fill="#7FB8E6"/><path d="M220 262 q12 -6 24 0 M236 280 q12 -6 24 0" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round" opacity=".8"/></g>'
    # field rows
    s += '<g transform="translate(20 175)">' + "".join(f'<rect x="0" y="{i*13}" width="100" height="7" rx="3.5" fill="#6FAE52"/>' for i in range(8)) + '</g>'
    # roads
    s += f'<path d="{ROAD}" stroke="#5E6B7D" stroke-width="40" fill="none" stroke-linejoin="round"/>'
    s += f'<path d="{SPUR}" stroke="#5E6B7D" stroke-width="32" fill="none"/>'
    s += f'<path d="{ROAD}" stroke="#fff" stroke-width="3" fill="none" stroke-dasharray="12 10"/>'
    s += f'<path d="M 168 230 H 410" stroke="#fff" stroke-width="3" fill="none" stroke-dasharray="12 10"/>'
    # houses
    s += house_top(30, 362, 56, 40, "#E66F5C") + house_top(180, 362, 50, 40, "#F2B63D") + house_top(230, 70, 54, 40, "#7A9CC6")
    s += charger_top(105, 380) + charger_top(254, 352)
    for x, y, r in [(30, 100, 16), (70, 80, 12), (100, 118, 14), (370, 300, 16), (360, 360, 12), (130, 420, 12), (60, 445, 14), (365, 90, 13)]:
        s += tree_top(x, y, r, "#4E9A3F", "#6DBA55")
    s += turbine_top(190, 70, 15) + turbine_top(370, 175, 50)
    s += f'<circle cx="345" cy="38" r="20" fill="{SUN}"/>'
    s += car_top(150, 260, 0, SKY) + car_top(260, 135, 90, "#F2B63D", .95) + car_top(365, 230, 90, "#FFFFFF", .9)
    return s

# ---------- B: Picture-book map (ink line, pale tints, 3/4 objects) ----------
def tree_b(x, y, r=11):
    return f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+r+6}" stroke="{INK}" stroke-width="2"/><circle cx="{x}" cy="{y}" r="{r}" fill="#B9DCA6" stroke="{INK}" stroke-width="2"/>'

def house_b(x, y):
    return (f'<g transform="translate({x} {y})" stroke="{INK}" stroke-width="2" stroke-linejoin="round">'
            f'<rect x="0" y="16" width="44" height="28" fill="#fff"/><path d="M-4 18 L22 0 L48 18 Z" fill="#E4F2DC"/>'
            f'<path d="M24 2 L46 17 L36 17 L18 5Z" fill="#2F679C" stroke-width="1.5"/>'
            f'<rect x="8" y="26" width="9" height="18" fill="{SUN}"/><rect x="25" y="25" width="11" height="9" fill="#CFE3F3"/></g>')

def turbine_b(x, y):
    return (f'<g transform="translate({x} {y})" stroke="{INK}" stroke-width="2" stroke-linecap="round">'
            f'<line x1="0" y1="0" x2="0" y2="58"/>' + "".join(f'<path d="M0 0 L0 -26" transform="rotate({a})" stroke-width="3"/>' for a in (10, 130, 250)) +
            f'<circle r="3.5" fill="#fff"/></g>')

def car_b(x, y):
    return (f'<g transform="translate({x} {y})" stroke="{INK}" stroke-width="2" stroke-linejoin="round">'
            f'<path d="M0 14 Q2 4 12 3 L18 -5 Q20 -8 26 -8 H38 Q44 -8 47 -3 L52 3 Q60 4 60 12 V18 H0Z" fill="{SKY}"/>'
            f'<path d="M21 2 L25 -4 H32 V2Z M36 2 V-4 H41 L45 2Z" fill="#CFE3F3" stroke-width="1.5"/>'
            f'<circle cx="14" cy="18" r="6" fill="#fff"/><circle cx="46" cy="18" r="6" fill="#fff"/></g>')

def scene_b():
    s = '<rect width="390" height="460" fill="#FBFAF6"/>'
    # contour lines + grid
    s += "".join(f'<path d="M-10 {60+i*12} Q 90 {30+i*12} 180 {70+i*10} T 400 {40+i*12}" stroke="#d6dfea" fill="none" stroke-width="1"/>' for i in range(5))
    s += '<path d="M10 300 Q 40 250 110 255 Q 140 300 120 350 Q 60 380 10 340Z" fill="#E4F2DC" stroke="#16233A" stroke-width="1.5" stroke-dasharray="4 4"/>'
    s += '<path d="M220 300 Q 250 255 310 270 Q 350 300 330 345 Q 280 370 235 345Z" fill="#CFE3F3" stroke="#16233A" stroke-width="2"/>'
    s += '<path d="M245 305 q10 -5 20 0 M270 322 q10 -5 20 0" stroke="#2F679C" stroke-width="1.6" fill="none"/>'
    road = "M -10 420 C 80 420 60 330 150 320 S 200 210 120 180 S 140 90 250 110 S 360 200 400 150"
    s += f'<path d="{road}" stroke="{INK}" stroke-width="30" fill="none" stroke-linecap="round"/>'
    s += f'<path d="{road}" stroke="#fff" stroke-width="25" fill="none" stroke-linecap="round"/>'
    s += f'<path d="{road}" stroke="{INK}" stroke-width="2" fill="none" stroke-dasharray="8 8"/>'
    s += house_b(40, 205) + house_b(285, 380) + turbine_b(330, 55) + turbine_b(365, 75)
    for x, y in [(30, 140), (55, 125), (200, 260), (215, 395), (240, 415), (360, 260), (100, 445)]: s += tree_b(x, y)
    # charger pin
    s += (f'<g transform="translate(185 135)" stroke="{INK}" stroke-width="2"><rect x="-10" y="-14" width="20" height="28" rx="5" fill="#fff"/>'
          f'<path d="M1 -8 L-4 1 H0 L-1 8 L4 -1 H0 Z" fill="{SUN}" stroke-width="1.2"/></g>')
    s += car_b(110, 300)
    s += f'<circle cx="70" cy="50" r="22" fill="{SUN}" stroke="{INK}" stroke-width="2"/>' + "".join(
        f'<line x1="{70+30*math.cos(math.radians(a))}" y1="{50+30*math.sin(math.radians(a))}" x2="{70+38*math.cos(math.radians(a))}" y2="{50+38*math.sin(math.radians(a))}" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>' for a in range(0, 360, 45))
    s += f'<text x="230" y="215" font-family="Patrick" font-size="17" fill="{INK}" transform="rotate(-6 230 215)">quiet road →</text>'
    return s

# ---------- C: Paper cutout landscape (side view, winding road into the distance) ----------
def scene_c():
    s = '<defs><filter id="sh" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="3" stdDeviation="2.5" flood-color="#16233A" flood-opacity=".22"/></filter></defs>'
    s += '<rect width="390" height="460" fill="#E8F1F9"/>'
    s += f'<circle cx="290" cy="110" r="52" fill="{SUN}" filter="url(#sh)"/>'
    s += '<path d="M-10 230 Q 80 160 170 205 Q 260 150 400 200 V460 H-10Z" fill="#B9DCA6" filter="url(#sh)"/>'
    # turbines on far hill
    for x, y, sc in [(95, 182, .7), (130, 178, .8), (320, 172, .75)]:
        s += (f'<g transform="translate({x} {y}) scale({sc})" filter="url(#sh)"><rect x="-1.5" y="0" width="3" height="50" fill="#fff"/>' +
              "".join(f'<path d="M0 0 L-2.5 -24 Q0 -27 2.5 -24Z" transform="rotate({a})" fill="#fff"/>' for a in (20, 140, 260)) + '</g>')
    s += '<path d="M-10 290 Q 120 230 230 275 Q 320 310 400 260 V460 H-10Z" fill="#7BB661" filter="url(#sh)"/>'
    s += '<path d="M-10 360 Q 100 320 200 350 Q 300 380 400 340 V460 H-10Z" fill="#4E9A3F" filter="url(#sh)"/>'
    # winding road narrowing to the horizon (echo of the logo tick)
    import re as _re
    pts=[]; P=[(175,470),(200,410),(300,405),(275,352),(250,318),(160,326),(185,292),(200,274),(230,265),(241,254)]
    def bez(p0,p1,p2,p3,n=40): return [tuple((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d for a,b,c,d in zip(p0,p1,p2,p3)) for t in [i/n for i in range(n+1)]]
    for i in range(0,9,3): pts+=bez(*P[i:i+4])
    N=len(pts)
    s+='<g filter="url(#sh)">'+"".join(f'<line x1="{pts[i][0]:.1f}" y1="{pts[i][1]:.1f}" x2="{pts[i+1][0]:.1f}" y2="{pts[i+1][1]:.1f}" stroke="#5E6B7D" stroke-width="{46-40*i/N:.1f}" stroke-linecap="round"/>' for i in range(N-1))+'</g>'
    d="M"+" L".join(f"{x:.1f} {y:.1f}" for x,y in pts[:int(N*.85)])
    s+=f'<path d="{d}" stroke="#fff" stroke-width="2.2" fill="none" stroke-dasharray="9 8" opacity=".9"/>'
    # house with solar roof + car
    s += (f'<g transform="translate(40 300)" filter="url(#sh)"><rect x="0" y="18" width="62" height="40" fill="#fff"/>'
          f'<path d="M-6 20 L31 -4 L68 20Z" fill="#F2B63D"/><path d="M34 -1 L64 18 L50 18 L24 4Z" fill="#1F4F80"/>'
          f'<rect x="10" y="32" width="12" height="26" fill="{INK}"/><rect x="34" y="30" width="16" height="12" fill="#CFE3F3"/></g>')
    s += (f'<g transform="translate(108 340)" filter="url(#sh)"><rect width="10" height="18" rx="3" fill="#fff"/>'
          f'<path d="M6 3 L3 9 H5.5 L4.5 14 L8 8 H5.5Z" fill="{SKY}"/></g>')
    s += (f'<g transform="translate(250 395)" filter="url(#sh)">'
          f'<path d="M0 22 Q2 9 16 8 L24 -2 Q27 -6 34 -6 H50 Q58 -6 62 0 L69 8 Q80 9 80 19 V27 H0Z" fill="{SKY}"/>'
          f'<path d="M28 6 L33 -1 H42 V6Z M47 6 V-1 H54 L59 6Z" fill="#CFE3F3"/>'
          f'<circle cx="19" cy="27" r="8" fill="{INK}"/><circle cx="61" cy="27" r="8" fill="{INK}"/><circle cx="19" cy="27" r="3" fill="#fff"/><circle cx="61" cy="27" r="3" fill="#fff"/></g>')
    for x, y, r in [(345, 300, 16), (370, 315, 12), (20, 395, 14), (330, 420, 15)]:
        s += f'<g filter="url(#sh)"><rect x="{x-2}" y="{y}" width="4" height="{r+8}" fill="#6b4f2a"/><circle cx="{x}" cy="{y}" r="{r}" fill="#3F8A3A"/></g>'
    return s

# ---------- phone hero ----------
DIRS = {
    "A": ("Play mat", scene_a, "Used EVs got good.", "Electric cars you can actually afford, with real range. Compare them in plain language and make your shortlist."),
    "B": ("Picture-book map", scene_b, "Your next car is quieter.", "Good used EVs are finally within reach. Charging is easier than you think. Find the one that fits your life."),
    "C": ("Paper cutout", scene_c, "Be part of the switch.", "The electric future is already on the used-car market. Compare EVs, honestly, and make your shortlist."),
}

def phone(key):
    name, scene, h1, sub = DIRS[key]
    return f'''<div class="ph"><div class="top">{LOGO}<span class="menu">☰</span></div>
<div class="copy"><h1>{h1}</h1><p>{sub}</p><a class="btn">Start your shortlist</a><a class="lnk">How it works</a></div>
<svg viewBox="0 0 390 460" width="390" height="460">{scene()}</svg>
<div class="tag">{key} · {name}</div></div>'''

CSS = FONTS + f"""body{{margin:0;background:#dfe5ec;display:flex;gap:28px;padding:28px;font-family:Atkinson}}
.ph{{width:390px;height:844px;background:#fff;border-radius:34px;overflow:hidden;position:relative;box-shadow:0 10px 30px rgba(22,35,58,.18);display:flex;flex-direction:column}}
.top{{display:flex;justify-content:space-between;align-items:center;padding:22px 22px 6px}} .menu{{font-size:24px;color:{INK}}}
.copy{{padding:22px 24px 26px;flex:1}} h1{{font:800 36px/1.08 Bitter;color:{INK};margin:0 0 14px;letter-spacing:-.5px}}
p{{font-size:17px;line-height:1.5;color:#45546F;margin:0 0 22px}}
.btn{{display:inline-block;background:{ACTION};color:#fff;font-weight:700;font-size:17px;padding:14px 22px;border-radius:12px}}
.lnk{{display:inline-block;margin-left:18px;color:#2B5F91;font-weight:700;text-decoration:underline}}
.tag{{position:absolute;bottom:16px;left:16px;background:{INK};color:#fff;font:700 13px Atkinson;padding:5px 10px;border-radius:20px}}"""

def render(html, png, w, h):
    f = f"{OUT}/{png}.html"; open(f, "w").write(html)
    subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={w},{h}", "--force-device-scale-factor=2", f"--screenshot={OUT}/{png}.png", f"file://{f}"],
                   capture_output=True)

if __name__ == "__main__":
    for k in DIRS:
        render(f"<!doctype html><style>{CSS}</style><body>{phone(k)}</body>", f"dir-{k}", 446, 900)
    render(f"<!doctype html><style>{CSS}</style><body>{''.join(phone(k) for k in DIRS)}</body>", "dirs-all", 1310, 900)
