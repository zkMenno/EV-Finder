"""Highway band (wide, 1200x420): motorway, EVs, solar charging plaza, blue direction signs to European cities.
Horizontal 'driving' parallax: each layer has a speed; translateX = progress * speed * 420px."""
import math
from kit import DAY, NIGHT, st, turbine, tree, poplar, car, van, solarfield, sun
from depth import haze, big_leaf, grass, bird, sparkle, cloud
SIGN = "#2F6FA8"   # motorway-sign blue (close to sky/action, white text 5.1:1)
CITIES = [("Amsterdam", "up"), ("Paris", "right"), ("Bruxelles · Brussel", "left"), ("Berlin", "up"), ("Köln", "right"), ("Lyon", "left"), ("Luxembourg", "up"), ("Rotterdam", "right")]

def arrow(x, y, d, s=1):
    rot = {"up": -90, "right": 0, "left": 180}[d]
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})" fill="none" stroke="#FFFFFF" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M-9 0 H9 M3 -6 L9 0 L3 6"/></g>')

def sign(x, y, name, d, t, night):
    w = max(120, 15 + len(name) * 10.2 + 34)
    post = t["line"] if not night else "#9AA7BC"
    return (f'<g transform="translate({x} {y})"><rect x="{w/2-30}" y="40" width="5" height="96" fill="{post}"/><rect x="{w/2+25}" y="40" width="5" height="96" fill="{post}"/>'
            f'<rect x="0" y="0" width="{w:.0f}" height="46" rx="6" fill="{SIGN}" stroke="#FFFFFF" stroke-width="2.5"/>'
            f'<rect x="-2" y="-2" width="{w+4:.0f}" height="50" rx="7" fill="none" stroke="{t["line"]}" stroke-width="1.6"/>'
            f'<text x="14" y="30" font-family="Atkinson Hyperlegible, Arial, sans-serif" font-weight="700" font-size="19" fill="#FFFFFF">{name}</text>'
            f'{arrow(w-20, 23, d, .9)}</g>')

def charge_sign(x, y, t):
    return (f'<g transform="translate({x} {y})"><rect x="21" y="44" width="5" height="92" fill="{t["line"]}"/>'
            f'<rect x="0" y="0" width="48" height="48" rx="6" fill="{SIGN}" stroke="#FFFFFF" stroke-width="2.5"/><rect x="-2" y="-2" width="52" height="52" rx="7" fill="none" stroke="{t["line"]}" stroke-width="1.6"/>'
            f'<g fill="none" stroke="#FFFFFF" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><rect x="14" y="12" width="20" height="16" rx="4"/><path d="M19 12 V7 M29 12 V7 M24 28 Q24 38 34 38"/></g>'
            f'<path d="M25.5 15 L21 21 H24.5 L23 26 L28 19.5 H24.5Z" fill="#FFD166"/></g>')

def plaza(x, y, t, night):
    s = f'<g transform="translate({x} {y})" {st(t)}>'
    s += f'<path d="M-10 0 L190 0 L176 -14 L4 -14Z" fill="{t["solar"]}"/>'
    s += "".join(f'<path d="M{8+i*28} -12 L{20+i*28} -2" stroke="#93C1EA" stroke-width="1"/>' for i in range(6))
    s += f'<rect x="-10" y="0" width="200" height="6" fill="{t["wall"]}"/><rect x="10" y="6" width="5" height="54" fill="{t["wall"]}"/><rect x="165" y="6" width="5" height="54" fill="{t["wall"]}"/>'
    for i in range(3):
        cx = 40 + i * 48
        s += f'<rect x="{cx}" y="22" width="14" height="36" rx="3" fill="{t["wall"]}"/><path d="M{cx+8} 28 L{cx+4} 35 H{cx+7} L{cx+6} 41 L{cx+10} 34 H{cx+7}Z" fill="#FFD166" stroke-width="1"/>'
    return s + '</g>'

def defs(uid):
    return (f'<defs><filter id="hsh{uid}" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="3" stdDeviation="2" flood-color="#000" flood-opacity=".18"/></filter>'
            f'<filter id="bl{uid}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="4.5"/></filter></defs>')

def highway_layers(t, night=False, uid="hw"):
    L = []
    s = defs(uid) + f'<rect x="-900" y="-60" width="3000" height="560" fill="{t["sky"]}"/>'
    if night:
        s += "".join(f'<circle cx="{x}" cy="{y}" r="1.3" fill="#EEF3F9" opacity=".8"/>' for x, y in [(80, 40), (260, 90), (420, 30), (640, 70), (880, 50), (1100, 100), (980, 20)])
    s += "".join(f'<path d="M-900 {30+i*48} H2100" stroke="{t["line"]}" stroke-opacity=".06" stroke-dasharray="2 5"/>' for i in range(5))
    s += f'<g transform="translate(960 80)">{sun(t, night)}</g>'
    L.append(("sky", 0.03, s))
    s = cloud(220, 92, 1, t, .9 if not night else .25) + cloud(700, 60, .7, t, .8 if not night else .2) + bird(400, 110, 1, t["line"]) + bird(424, 98, .7, t["line"]) + sparkle(1120, 150, .8, t["line"])
    L.append(("doodles", 0.08, s))
    far = haze(t, t["r1"], .45)
    s = f'<path d="M-900 220 Q-700 170 -500 205 T-100 196 T300 190 T700 200 T1100 186 T1500 198 T2100 190 V520 H-900Z" fill="{far}" stroke="{t["line"]}" stroke-opacity=".35" stroke-width="1.4"/>'
    for x, a in [(-200, 10), (-170, 60), (240, 30), (270, 90), (820, 20), (850, 70), (1400, 40)]:
        s += f'<g transform="translate({x} 186) scale(.55)" opacity=".6">{turbine(t, a)}</g>'
    L.append(("far", 0.14, s))
    s = f'<path d="M-900 262 Q-600 220 -300 250 T300 240 T900 252 T1500 238 T2100 250 V520 H-900Z" fill="{t["r1"]}" {st(t,1.8)} filter="url(#hsh{uid})"/>'
    for x in (-260, 360, 1020):
        s += f'<g transform="translate({x} 232) scale(.8)">{solarfield(t)}</g>'
    for x, y in [(120, 252), (150, 258), (560, 250), (600, 246), (1250, 252), (-480, 252)]:
        s += f'<g transform="translate({x} {y}) scale(.7)">{poplar(t, True)}</g>'
    L.append(("hills", 0.3, s))
    # motorway: verge, guard rail, two lanes each way, central reservation
    s = f'<rect x="-1200" y="286" width="3600" height="24" fill="{t["r2"]}" {st(t)}/>'
    s += f'<rect x="-1200" y="310" width="3600" height="84" fill="{t["road"] if not night else "#2A3A57"}" {st(t)}/>'
    s += f'<path d="M-1200 351 H2400" stroke="{t["line"]}" stroke-width="3"/>'
    s += "".join(f'<rect x="{x}" y="329" width="40" height="3" fill="{t["line"]}" opacity=".7"/><rect x="{x+30}" y="372" width="40" height="3" fill="{t["line"]}" opacity=".7"/>' for x in range(-1200, 2400, 90))
    s += f'<path d="M-1200 302 H2400" stroke="{t["line"]}" stroke-width="2.2"/>' + "".join(f'<rect x="{x}" y="296" width="3" height="12" fill="{t["line"]}"/>' for x in range(-1200, 2400, 60))
    s += f'<rect x="-1200" y="394" width="3600" height="140" fill="{t["r3"]}" {st(t)}/>'
    s += plaza(560, 236, t, night)
    s += f'<g transform="translate(600 274) scale(.8)">{car(t, night)}</g>'
    for x, y, f, sc in [(80, 300, car, 1), (340, 300, van, 1), (900, 343, car, 1), (1180, 300, car, .95), (-260, 343, van, 1)]:
        s += f'<g transform="translate({x} {y}) scale({sc})">{f(t) if f is van else f(t, night)}</g>'
    L.append(("road", 0.6, s))
    s = ""
    xs = [-760, -420, -80, 260, 600, 940, 1280, 1620]
    for (name, d), x in zip(CITIES, xs):
        s += sign(x, 160, name, d, t, night)
    s += charge_sign(1460, 166, t) + charge_sign(100 + 330, 166, t)
    L.append(("signs", 1.0, s))
    fg, fl = t["leafr"], t["line"]
    s = "".join(grass(x, 424, 26, t["r3"], fl) for x in range(-1000, 2200, 140))
    s += big_leaf(-20, 440, 2.0, 40, fg, fl, uid) + big_leaf(1220, 444, 2.1, -40, fg, fl, uid)
    L.append(("foreground", 1.35, s))
    return L
