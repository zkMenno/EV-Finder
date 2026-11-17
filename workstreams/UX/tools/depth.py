"""Depth v2: scenes split into parallax layers, with atmospheric perspective, blurred foreground foliage
and floating line doodles (inspired by Menno's reference). Each layer is a full 390x460 SVG group.
layers(kind, theme) -> list of (name, depth_factor, svg_inner)."""
import math
from kit import DAY, NIGHT, st, house, wallbox, turbine, tree, poplar, car, solarfield, sun, bez, road_winding
from city import apartment, rowhouses, tram, lampcharger, bike, streettree

def lerp_hex(a, b, t):
    a, b = a.lstrip('#'), b.lstrip('#')
    return '#' + ''.join(f'{round(int(a[i:i+2], 16) * (1 - t) + int(b[i:i+2], 16) * t):02x}' for i in (0, 2, 4))

def haze(t, col, amount):  # atmospheric perspective: mix towards the sky colour
    return lerp_hex(col, t['sky'], amount)

def defs(t, uid):
    return (f'<defs><filter id="sh{uid}" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="3" stdDeviation="2" flood-color="#000" flood-opacity=".18"/></filter>'
            f'<filter id="bl{uid}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="4.5"/></filter>'
            f'<filter id="bl2{uid}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="1.2"/></filter></defs>')

# --- doodles: map-symbol line drawings floating in the sky ---
def bird(x, y, s, c, o=.7):
    return f'<path d="M{x-8*s} {y} q{4*s} {-5*s} {8*s} 0 q{4*s} {-5*s} {8*s} 0" fill="none" stroke="{c}" stroke-opacity="{o}" stroke-width="1.8" stroke-linecap="round"/>'
def sparkle(x, y, s, c, o=.6):
    return f'<path d="M{x} {y-7*s} L{x+1.6*s} {y-1.6*s} L{x+7*s} {y} L{x+1.6*s} {y+1.6*s} L{x} {y+7*s} L{x-1.6*s} {y+1.6*s} L{x-7*s} {y} L{x-1.6*s} {y-1.6*s}Z" fill="none" stroke="{c}" stroke-opacity="{o}" stroke-width="1.6" stroke-linejoin="round"/>'
def cloud(x, y, s, t, o=1):
    return (f'<path d="M{x} {y} q{-14*s} 0 {-14*s} {-10*s} q0 {-10*s} {12*s} {-10*s} q{4*s} {-12*s} {18*s} {-10*s} q{12*s} {-6*s} {20*s} {6*s} q{12*s} 0 {12*s} {10*s} q0 {14*s} {-14*s} {14*s}Z" '
            f'fill="{t["wall"]}" fill-opacity="{0.85*o}" stroke="{t["line"]}" stroke-opacity="{.45*o}" stroke-width="1.5" stroke-linejoin="round"/>')
def leaf_doodle(x, y, s, c, rot=0, o=.55):
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})" fill="none" stroke="{c}" stroke-opacity="{o}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M0 10 Q-8 -2 0 -12 Q8 -2 0 10Z"/><path d="M0 8 V-8"/></g>')
def plug_doodle(x, y, s, c, o=.55):
    return (f'<g transform="translate({x} {y}) scale({s})" fill="none" stroke="{c}" stroke-opacity="{o}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
            f'<rect x="-6" y="-6" width="12" height="10" rx="3"/><path d="M-3 -6 V-10 M3 -6 V-10 M0 4 Q0 12 8 12"/></g>')

# --- foreground foliage: big soft leaves, blurred = depth of field ---
def big_leaf(x, y, s, rot, col, line, uid, blur=True):
    f = f' filter="url(#bl{uid})"' if blur else ''
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})"{f}><path d="M0 0 Q26 -30 0 -80 Q-26 -30 0 0Z" fill="{col}" stroke="{line}" stroke-opacity=".35" stroke-width="2"/>'
            f'<path d="M0 -4 Q2 -40 0 -74" fill="none" stroke="{line}" stroke-opacity=".3" stroke-width="2"/></g>')
def grass(x, y, h, col, line):
    return (f'<path d="M{x} {y} q-3 {-h*.6} -9 {-h} M{x+4} {y} q1 {-h*.7} 4 {-h*1.15} M{x+8} {y} q4 {-h*.5} 11 {-h*.8}" fill="none" stroke="{col}" stroke-width="3" stroke-linecap="round"/>'
            f'<path d="M{x} {y} q-3 {-h*.6} -9 {-h} M{x+4} {y} q1 {-h*.7} 4 {-h*1.15} M{x+8} {y} q4 {-h*.5} 11 {-h*.8}" fill="none" stroke="{line}" stroke-opacity=".35" stroke-width="1" stroke-linecap="round"/>')
def flower(x, y, s, petal, line):
    p = "".join(f'<ellipse cx="0" cy="-6" rx="3.2" ry="6" transform="rotate({a})" fill="{petal}" stroke="{line}" stroke-opacity=".5" stroke-width="1.2"/>' for a in range(0, 360, 72))
    return f'<g transform="translate({x} {y}) scale({s})">{p}<circle r="3" fill="#FFD166" stroke="{line}" stroke-opacity=".5" stroke-width="1.2"/></g>'

def sky_layer(t, night, uid, H=520, sun_at=(300, 96), sun_scale=1.0):
    s = f'<rect x="-40" y="-60" width="470" height="{H}" fill="{t["sky"]}"/>'
    if night:
        for x, y, r in [(40, 40, 1.4), (120, 70, 1.1), (200, 30, 1.6), (250, 120, 1.0), (90, 140, 1.2), (350, 160, 1.3), (30, 190, 1.0)]:
            s += f'<circle cx="{x}" cy="{y}" r="{r}" fill="#EEF3F9" opacity=".8"/>'
    # faint map grid in the sky = the travel-map identity behind the scene
    s += "".join(f'<path d="M-40 {30+i*48} H430" stroke="{t["line"]}" stroke-opacity=".06" stroke-dasharray="2 5"/>' for i in range(5))
    s += "".join(f'<path d="M{10+i*48} -60 V250" stroke="{t["line"]}" stroke-opacity=".06" stroke-dasharray="2 5"/>' for i in range(9))
    if sun_at:
        s += f'<g transform="translate({sun_at[0]} {sun_at[1]}) scale({sun_scale})">{sun(t, night)}</g>'
    return s

def doodle_layer(t, night, mirror=False):
    c = t["line"]
    s = cloud(96, 92, .9, t, .9 if not night else .25) + cloud(214, 58, .6, t, .8 if not night else .2)
    s += bird(160, 120, 1, c) + bird(182, 108, .7, c) + bird(60, 150, .8, c, .5)
    s += sparkle(36, 54, .8, c) + sparkle(372, 190, .7, c, .45) + leaf_doodle(352, 34, .9, c, 30) + plug_doodle(30, 212, .9, c, .4)
    return f'<g transform="translate(390 0) scale(-1 1)">{s}</g>' if mirror else s

def village_layers(t, rich=True, night=False, uid="v"):
    H = (t["r1"], t["r2"], t["r3"]) if rich else (t["h1"], t["h2"], t["h3"])
    L = []
    L.append(("sky", 0.55, defs(t, uid) + sky_layer(t, night, uid)))
    L.append(("doodles", 0.42, doodle_layer(t, night)))
    far = haze(t, H[0], .45)
    s = (f'<path d="M-40 236 Q20 196 70 214 Q120 170 170 204 Q230 168 280 196 Q340 172 430 198 V560 H-40Z" fill="{far}" stroke="{t["line"]}" stroke-opacity=".35" stroke-width="1.4"/>')
    for x, y, sc, a in [(60, 204, .45, 10), (84, 200, .5, 70), (300, 186, .45, 40), (322, 190, .5, 100)]:
        s += f'<g transform="translate({x} {y}) scale({sc})" opacity=".6">{turbine(t, a)}</g>'
    L.append(("far", 0.36, s))
    s = f'<path d="M-40 250 Q 80 180 170 225 Q 260 170 430 220 V560 H-40Z" fill="{H[0]}" {st(t,1.8)} filter="url(#sh{uid})"/>'
    for x, y, sc, a in [(110, 206, .7, 20), (140, 202, .8, 70)]:
        s += f'<g transform="translate({x} {y}) scale({sc})" opacity=".9">{turbine(t, a)}</g>'
    s += f'<g transform="translate(300 214) scale(.7)" opacity=".9">{solarfield(t)}</g>'
    L.append(("hills-far", 0.24, s))
    s = f'<path d="M-40 300 Q 120 240 230 285 Q 320 318 430 270 V560 H-40Z" fill="{H[1]}" {st(t,2)} filter="url(#sh{uid})"/>'
    s += f'<g transform="translate(150 252) scale(.55)">{house(t, rich)}</g><g transform="translate(196 246) scale(.5)">{house(t, rich)}</g>'
    for x, y, r in [(345, 280, 12), (366, 292, 10), (300, 300, 9)]:
        s += f'<g transform="translate({x} {y})">{tree(t, r, rich)}</g>'
    L.append(("hills-mid", 0.13, s))
    s = f'<path d="M-40 368 Q 100 328 200 358 Q 300 388 430 348 V560 H-40Z" fill="{H[2]}" {st(t,2.2)} filter="url(#sh{uid})"/>'
    s += road_winding(t, [(175, 485), (200, 415), (300, 410), (275, 360), (250, 326), (160, 334), (185, 300), (200, 282), (230, 273), (241, 262)])
    s += f'<g transform="translate(36 306)">{house(t, rich)}</g><g transform="translate(106 340)">{wallbox(t)}</g>'
    s += f'<g transform="translate(252 400)">{car(t, night)}</g>'
    for x, y, r in [(22, 400, 13), (338, 428, 13)]:
        s += f'<g transform="translate({x} {y})">{tree(t, r, rich)}</g>'
    L.append(("near", 0.05, s))
    fg, fl = (t["leafr"] if rich else t["leaf"]), t["line"]
    s = (big_leaf(-14, 478, 2.0, 34, fg, fl, uid) + big_leaf(30, 486, 1.5, -6, haze(t, fg, .08), fl, uid) +
         big_leaf(404, 482, 2.1, -36, fg, fl, uid) + big_leaf(374, 490, 1.3, 12, haze(t, fg, .08), fl, uid) +
         big_leaf(-10, -6, 1.6, 150, fg, fl, uid) + big_leaf(24, -14, 1.1, 196, haze(t, fg, .08), fl, uid))
    s += grass(70, 466, 22, H[2], fl) + grass(300, 468, 18, H[2], fl)
    s += flower(96, 452, .9, "#F2B0C0" if not night else "#8a5a6b", fl) + flower(318, 448, .8, "#FFFFFF" if not night else "#C9D3DF", fl)
    L.append(("foreground", -0.14, s))
    return L

def city_layers(t, rich=True, night=False, uid="c"):
    H = (t["r1"], t["r2"], t["r3"]) if rich else (t["h1"], t["h2"], t["h3"])
    L = [("sky", 0.55, defs(t, uid) + sky_layer(t, night, uid, sun_at=(70, 84), sun_scale=.85)), ("doodles", 0.42, doodle_layer(t, night, mirror=True))]
    far = haze(t, H[0], .5)
    s = (f'<path d="M-40 250 V196 H20 V170 H48 V204 H82 V160 H104 V146 H126 V214 H160 V182 H198 V204 H236 V172 H270 V208 H306 V186 H344 V216 H430 V560 H-40Z" '
         f'fill="{far}" stroke="{t["line"]}" stroke-opacity=".35" stroke-width="1.4"/>')
    for x, sc, a in [(210, .5, 30), (236, .55, 80)]:
        s += f'<g transform="translate({x} 128) scale({sc})" opacity=".6">{turbine(t, a)}</g>'
    L.append(("far", 0.36, s))
    s = f'<path d="M-40 272 Q 120 249 220 266 Q 320 282 430 259 V560 H-40Z" fill="{H[1]}" {st(t,1.8)}/>'
    s += f'<g transform="translate(18 162)" filter="url(#sh{uid})">{apartment(t, 72, 128, 5, rich)}</g>'
    s += f'<g transform="translate(214 144)" filter="url(#sh{uid})">{apartment(t, 64, 146, 6, rich)}</g>'
    s += f'<g transform="translate(292 180)" filter="url(#sh{uid})">{apartment(t, 84, 110, 4, rich, True)}</g>'
    s += f'<g transform="translate(108 200)" filter="url(#sh{uid})">{rowhouses(t, rich)}</g>'
    L.append(("buildings", 0.18, s))
    s = f'<rect x="-40" y="290" width="470" height="26" fill="{H[2]}" {st(t)}/>' + asphalt(t, night, uid, -40, 316, 470, 70)
    s += f'<path d="M-40 388 H430 M-40 396 H430" stroke="{t["line"]}" stroke-width="1.5"/>'
    s += f'<g transform="translate(40 355)">{tram(t)}</g>'
    s += f'<rect x="-40" y="408" width="470" height="160" fill="{H[2] if not rich else H[1]}" {st(t)}/>'
    s += f'<g transform="translate(332 216)">{lampcharger(t)}</g><g transform="translate(240 290) scale(.9)">{car(t, night)}</g>'
    for x in (90, 200):
        s += f'<g transform="translate({x} 266) scale(.85)">{streettree(t, rich)}</g>'
    s += f'<g transform="translate(160 420)">{bike(t)}</g>'
    L.append(("street", 0.06, s))
    fg, fl = (t["leafr"] if rich else t["leaf"]), t["line"]
    s = (big_leaf(-14, 478, 2.0, 34, fg, fl, uid) + big_leaf(404, 482, 2.1, -36, fg, fl, uid) + big_leaf(374, 490, 1.3, 12, haze(t, fg, .08), fl, uid) +
         '')
    s += f'<g transform="translate(64 448) scale(1.1)">{streettree(t, rich)}</g>'
    s += flower(300, 452, .8, "#F2B0C0" if not night else "#8a5a6b", fl)
    L.append(("foreground", -0.14, s))
    return L

def asphalt(t, night, uid, x, y, w, h, lanes=True, centre=None):
    """Grey asphalt with a fine speckle texture and white road markings (edge lines + dashed lane line)."""
    base = "#8C96A5" if not night else "#2A3A57"
    s = (f'<defs><pattern id="asp{uid}" width="9" height="9" patternUnits="userSpaceOnUse"><circle cx="2" cy="3" r=".7" fill="#16233A" fill-opacity=".18"/>'
         f'<circle cx="7" cy="7" r=".6" fill="#FFFFFF" fill-opacity=".18"/></pattern></defs>'
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{base}" stroke="{t["line"]}" stroke-width="2"/><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#asp{uid})"/>'
         f'<path d="M{x} {y+5} H{x+w} M{x} {y+h-5} H{x+w}" stroke="#FFFFFF" stroke-opacity=".9" stroke-width="2"/>')
    if lanes:
        cy = centre if centre is not None else y + h / 2
        s += f'<path d="M{x} {cy} H{x+w}" stroke="#FFFFFF" stroke-opacity=".9" stroke-width="2.4" stroke-dasharray="18 14"/>'
    return s

def flat(layers, w=390, h=460):
    return f'<svg viewBox="0 0 390 460" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">' + "".join(f'<g>{s}</g>' for _, _, s in layers) + '</svg>'
