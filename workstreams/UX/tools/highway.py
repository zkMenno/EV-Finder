"""Highway band (wide, 1200x420): motorway, EVs, solar charging plaza, blue direction signs to European cities.
Horizontal 'driving' parallax: each layer has a speed; translateX = progress * speed * 420px."""
import math
from kit import DAY, NIGHT, st, turbine, tree, poplar, car, van, solarfield, sun
from depth import haze, big_leaf, grass, bird, sparkle, cloud, asphalt
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
    """Service sign: blue panel, white inset, dark charging post with cable and a sunflower bolt (reads as 'charging here')."""
    return (f'<g transform="translate({x} {y})"><rect x="25" y="52" width="5" height="84" fill="{t["line"]}"/>'
            f'<rect x="0" y="0" width="56" height="56" rx="6" fill="{SIGN}" stroke="#FFFFFF" stroke-width="2.5"/><rect x="-2" y="-2" width="60" height="60" rx="7" fill="none" stroke="{t["line"]}" stroke-width="1.6"/>'
            f'<rect x="8" y="8" width="40" height="40" rx="4" fill="#FFFFFF"/>'
            f'<g fill="none" stroke="#16233A" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><rect x="16" y="14" width="13" height="27" rx="2.5" fill="#16233A"/><path d="M29 22 H33 Q37 22 37 26 V34 Q37 38 40 38"/><path d="M14 41 H31"/></g>'
            f'<path d="M23.5 18 L19.5 25 H22.5 L21.5 31 L26 24 H23Z" fill="#FFD166"/></g>')

def plaza(x, y, t, night, cars=("car", "van")):
    """Solar-roofed charging hub: canopy, ground line at y=60, one bay per car: charger post, cable, car parked on the ground."""
    from kit import car as _car, van as _van
    n = len(cars); bay = 96; w = n * bay + 10
    s = f'<g transform="translate({x} {y})" {st(t)}>'
    s += f'<path d="M-10 0 L{w} 0 L{w-14} -14 L4 -14Z" fill="{t["solar"]}"/>'
    s += "".join(f'<path d="M{8+i*28} -12 L{20+i*28} -2" stroke="#93C1EA" stroke-width="1"/>' for i in range(int(w // 28)))
    s += f'<rect x="-10" y="0" width="{w+10}" height="6" fill="{t["wall"]}"/><rect x="-4" y="6" width="5" height="54" fill="{t["wall"]}"/><rect x="{w-6}" y="6" width="5" height="54" fill="{t["wall"]}"/>'
    s += f'<path d="M-14 60 H{w+8}" stroke-width="2.2"/>'
    for i, kind in enumerate(cars):
        bx = 6 + i * bay
        s += f'<rect x="{bx}" y="26" width="13" height="34" rx="3" fill="{t["wall"]}"/><path d="M{bx+7} 31 L{bx+3} 38 H{bx+6} L{bx+5} 44 L{bx+9} 37 H{bx+6}Z" fill="#FFD166" stroke-width="1"/>'
        s += f'<path d="M{bx+13} 40 Q{bx+24} 40 {bx+26} 48" fill="none" stroke-width="1.6"/>'
        body = _van(t) if kind == "van" else _car(t, night)
        s += f'<g transform="translate({bx+20} {60-34.5*0.8:.1f}) scale(.8)">{body}</g>'
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
    s += f'<g transform="translate(140 70) scale(.9)">{sun(t, night)}</g>'
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
    s = ""
    xs = [-760, -420, -80, 260, 600, 940, 1280, 1620]
    for (name, d), x in zip(CITIES, xs):
        s += sign(x, 160, name, d, t, night)
    s += charge_sign(1460, 166, t) + charge_sign(100 + 330, 166, t)
    L.append(("signs", 0.55, s))   # on the far verge: behind the road and all traffic
    # motorway: verge, guard rail, two lanes each way, central reservation
    s = f'<rect x="-1200" y="286" width="3600" height="24" fill="{t["r2"]}" {st(t)}/>'
    s += asphalt(t, night, uid, -1200, 310, 3600, 84, lanes=False)
    s += f'<path d="M-1200 351 H2400" stroke="{t["line"]}" stroke-width="3"/>'
    s += "".join(f'<rect x="{x}" y="329" width="40" height="3" fill="#FFFFFF" opacity=".9"/><rect x="{x+30}" y="372" width="40" height="3" fill="#FFFFFF" opacity=".9"/>' for x in range(-1200, 2400, 90))
    s += f'<path d="M-1200 302 H2400" stroke="{t["line"]}" stroke-width="2.2"/>' + "".join(f'<rect x="{x}" y="296" width="3" height="12" fill="{t["line"]}"/>' for x in range(-1200, 2400, 60))
    s += f'<rect x="-1200" y="394" width="3600" height="140" fill="{t["r3"]}" {st(t)}/>'
    s += plaza(736, 236, t, night, cars=("car", "car"))
    L.append(("road", 0.6, s))
    # far lane drives left-to-right faster than the road scrolls; near lane the other way: they look like they're driving
    far_lane = "".join(f'<g transform="translate({x} 300)">{f(t) if f is van else f(t, night)}</g>' for x, f in [(-600, car), (80, car), (340, van), (1180, car), (1700, van)])
    near_lane = "".join(f'<g transform="translate({x} 343) scale(-1 1) translate(-80 0)">{f(t) if f is van else f(t, night)}</g>' for x, f in [(-260, van), (520, car), (900, car), (1500, car)])
    L.append(("traffic-far", 0.95, far_lane))
    L.append(("traffic-near", 0.2, near_lane))
    fg, fl = t["leafr"], t["line"]
    s = "".join(grass(x, 424, 26, t["r3"], fl) for x in range(-1000, 2200, 140))
    s += big_leaf(-20, 440, 2.0, 40, fg, fl, uid) + big_leaf(1220, 444, 2.1, -40, fg, fl, uid)
    L.append(("foreground", 1.35, s))
    return L
