"""More solarpunk city scenes, layered for parallax like depth.py: canal city and green square."""
from kit import DAY, NIGHT, st, turbine, tree, car, van, solarfield, sun
from city import apartment, rowhouses, tram, lampcharger, bike, streettree
from depth import haze, defs, sky_layer, doodle_layer, big_leaf, flower, asphalt
from highway import plaza

def canal_house(t, x, w, h, kind, fill, rich, night):
    s = f'<g transform="translate({x} 0)" {st(t)}><rect x="0" y="{-h}" width="{w}" height="{h}" fill="{fill}"/>'
    if kind == "step":
        s += f'<path d="M0 {-h} V{-h-10} H{w*.2} V{-h-20} H{w*.4} V{-h-30} H{w*.6} V{-h-20} H{w*.8} V{-h-10} H{w} V{-h}" fill="{fill}"/>'
    elif kind == "bell":
        s += f'<path d="M0 {-h} Q{w*.1} {-h-14} {w*.3} {-h-18} Q{w*.5} {-h-34} {w*.7} {-h-18} Q{w*.9} {-h-14} {w} {-h}Z" fill="{fill}"/>'
    else:
        s += f'<path d="M-3 {-h} L{w/2} {-h-24} L{w+3} {-h}Z" fill="{t["roofr"] if rich else t["roof"]}"/><path d="M{w/2+3} {-h-20} L{w-2} {-h-3} L{w/2+3} {-h-3}Z" fill="{t["solar"]}" stroke-width="1.2"/>'
    rows = int((h - 20) // 26)
    for r in range(rows):
        for c in range(2):
            wx, wy = 6 + c * (w - 6) / 2, -h + 10 + r * 26
            s += f'<rect x="{wx:.1f}" y="{wy}" width="{(w-18)/2:.1f}" height="16" rx="2" fill="{t["window"]}" stroke-width="1.2"/>'
        if r % 2 == 0:
            s += f'<rect x="4" y="{-h + 27 + r*26}" width="{w-8}" height="4" fill="{t["leafr"] if rich else t["leaf"]}" stroke-width="1"/>'
    s += f'<rect x="{w/2-6}" y="-18" width="12" height="18" fill="{t["door"]}" stroke-width="1.3"/></g>'
    return s

def boat(t, x, y):
    return (f'<g transform="translate({x} {y})" {st(t)}><path d="M0 0 H70 Q66 12 56 14 H10 Q2 12 0 0Z" fill="{t["wall"]}"/>'
            f'<rect x="18" y="-12" width="30" height="12" rx="2" fill="{t["roofr"]}"/><path d="M20 -14 L46 -14 L42 -20 L24 -20Z" fill="{t["solar"]}" stroke-width="1.2"/></g>')

def canal_layers(t, rich=True, night=False, uid="k"):
    H = (t["r1"], t["r2"], t["r3"]) if rich else (t["h1"], t["h2"], t["h3"])
    L = [("sky", 0.55, defs(t, uid) + sky_layer(t, night, uid, sun_at=(196, 150), sun_scale=1.25)), ("doodles", 0.42, doodle_layer(t, night, mirror=True))]
    far = haze(t, H[0], .5)
    s = (f'<path d="M-40 230 V190 H10 V150 H30 V130 H44 V150 H64 V196 H120 V176 H150 V200 H250 V168 H262 V120 H270 V168 H282 V196 H340 V176 H380 V204 H430 V560 H-40Z" fill="{far}" stroke="{t["line"]}" stroke-opacity=".35" stroke-width="1.4"/>')
    s += f'<g transform="translate(360 128) scale(.5)" opacity=".6">{turbine(t, 40)}</g>'
    L.append(("far", 0.36, s))
    fills = [t["wall"], t["roof"] if not night else "#3a3320", t["wall"], "#DCEBF7" if not night else "#22324D", t["wall"], t["roof"] if not night else "#3a3320", t["wall"]]
    kinds = ["step", "gable", "bell", "gable", "step", "bell", "gable"]
    s = f'<g transform="translate(0 300)" filter="url(#sh{uid})">'
    x = -10
    for i, (k, f) in enumerate(zip(kinds, fills)):
        w = 56 if i % 2 else 52; h = 112 + (i * 37 % 40)
        s += canal_house(t, x, w, h, k, f, rich, night); x += w
    s += '</g>'
    for x in (40, 150, 270, 360):
        s += f'<g transform="translate({x} 286) scale(.9)">{streettree(t, rich)}</g>'
    L.append(("houses", 0.16, s))
    s = f'<rect x="-40" y="300" width="470" height="30" fill="{H[2]}" {st(t)}/>'
    s += f'<g transform="translate(330 250) scale(.8)">{lampcharger(t)}</g><g transform="translate(236 270) scale(.85)">{car(t, night)}</g><g transform="translate(150 300)">{bike(t)}</g>'
    s += f'<rect x="-40" y="330" width="470" height="240" fill="{"#9CC6E8" if not night else "#1B3350"}" {st(t)}/>'
    s += "".join(f'<path d="M{x} {y} q8 -4 16 0" stroke="{t["line"]}" stroke-opacity=".45" stroke-width="1.6" fill="none" stroke-linecap="round"/>' for x, y in [(30, 360), (120, 392), (300, 372), (220, 420), (360, 410)])
    s += boat(t, 60, 380)
    s += (f'<path d="M150 330 Q230 290 310 330" fill="none" stroke="{t["line"]}" stroke-width="10"/><path d="M150 330 Q230 290 310 330" fill="none" stroke="{t["wall"]}" stroke-width="6"/>'
          f'<path d="M168 330 Q230 306 292 330" fill="none" stroke="{t["line"]}" stroke-width="2"/>')
    L.append(("canal", 0.06, s))
    fg, fl = (t["leafr"] if rich else t["leaf"]), t["line"]
    s = big_leaf(404, 482, 2.1, -36, fg, fl, uid) + big_leaf(370, 488, 1.3, 10, haze(t, fg, .08), fl, uid)
    s += flower(40, 452, .8, "#F2B0C0" if not night else "#8a5a6b", fl)
    L.append(("foreground", -0.14, s))
    return L

def square_layers(t, rich=True, night=False, uid="q"):
    H = (t["r1"], t["r2"], t["r3"]) if rich else (t["h1"], t["h2"], t["h3"])
    L = [("sky", 0.55, defs(t, uid) + sky_layer(t, night, uid, sun_at=(270, 56), sun_scale=.7)), ("doodles", 0.42, doodle_layer(t, night))]
    far = haze(t, H[0], .5)
    s = f'<path d="M-40 240 V200 H40 V170 H90 V210 H150 V186 H230 V160 H270 V206 H330 V180 H430 V560 H-40Z" fill="{far}" stroke="{t["line"]}" stroke-opacity=".35" stroke-width="1.4"/>'
    L.append(("far", 0.36, s))
    s = f'<g transform="translate(10 112)" filter="url(#sh{uid})">{apartment(t, 92, 176, 7, rich)}</g>'
    s += f'<g transform="translate(290 128)" filter="url(#sh{uid})">{apartment(t, 92, 160, 6, rich)}</g>'
    # green-roof timber tower in the middle
    s += (f'<g transform="translate(150 70)" filter="url(#sh{uid})" {st(t)}><rect width="80" height="218" fill="{"#E9D9BE" if not night else "#3A3320"}"/>' +
          "".join(f'<rect x="-6" y="{20+i*32}" width="92" height="7" fill="{t["leafr"] if rich else t["leaf"]}"/>' for i in range(6)) +
          "".join(f'<rect x="{10+c*22}" y="{30+r*32}" width="16" height="14" rx="2" fill="{t["window"]}" stroke-width="1.2"/>' for r in range(6) for c in range(3)) +
          f'<path d="M6 0 L18 -10 H60 L72 0Z" fill="{t["solar"]}"/>' + "".join(f'<circle cx="{14+i*18}" cy="-12" r="8" fill="{t["leafr"] if rich else t["leaf"]}"/>' for i in range(4)) + '</g>')
    L.append(("towers", 0.16, s))
    s = f'<rect x="-40" y="288" width="470" height="300" fill="{H[2]}" {st(t)}/>'
    s += asphalt(t, night, uid, -40, 352, 470, 44, lanes=False) + f'<path d="M-40 384 H430 M-40 390 H430" stroke="#FFFFFF" stroke-opacity=".8" stroke-width="1.6"/>'
    s += f'<g transform="translate(150 350) scale(.9)">{tram(t)}</g>'
    s += f'<g transform="translate(40 300) scale(.82)">{plaza(0, 0, t, night)}</g>'
    s += f'<g transform="translate(64 300) scale(.72)">{car(t, night)}</g><g transform="translate(108 300) scale(.72)">{van(t)}</g>'
    for x in (260, 330):
        s += f'<g transform="translate({x} 314)">{streettree(t, rich)}</g>'
    s += f'<g transform="translate(280 412)">{bike(t)}</g><g transform="translate(60 418) scale(.9)">{bike(t)}</g>'
    L.append(("square", 0.06, s))
    fg, fl = (t["leafr"] if rich else t["leaf"]), t["line"]
    s = big_leaf(-14, 478, 2.0, 34, fg, fl, uid) + big_leaf(22, 486, 1.4, -8, haze(t, fg, .08), fl, uid) + big_leaf(-10, -6, 1.6, 150, fg, fl, uid)
    s += flower(200, 456, .8, "#FFFFFF" if not night else "#C9D3DF", fl)
    L.append(("foreground", -0.14, s))
    return L

def canal_wide_layers(t, night=False, uid="kw"):
    """Wide canal panorama (1200x420 viewBox, content from -900 to 2100) for horizontal 'driving' parallax.
    Same speed convention as highway_layers: translateX = progress * speed * 420px."""
    from kit import sun
    from depth import cloud, bird, sparkle
    H = (t["r1"], t["r2"], t["r3"])
    L = []
    s = (f'<defs><filter id="sh{uid}" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="3" stdDeviation="2" flood-color="#000" flood-opacity=".18"/></filter>'
         f'<filter id="bl{uid}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="4.5"/></filter></defs>'
         f'<rect x="-900" y="-60" width="3000" height="560" fill="{t["sky"]}"/>')
    if night:
        s += "".join(f'<circle cx="{x}" cy="{y}" r="1.3" fill="#EEF3F9" opacity=".8"/>' for x, y in [(80, 40), (260, 90), (420, 30), (640, 70), (880, 50), (1100, 100)])
    s += "".join(f'<path d="M-900 {30+i*48} H2100" stroke="{t["line"]}" stroke-opacity=".06" stroke-dasharray="2 5"/>' for i in range(4))
    s += f'<g transform="translate(600 120) scale(1.2)">{sun(t, night)}</g>'
    L.append(("sky", 0.03, s))
    L.append(("doodles", 0.08, cloud(260, 70, 1, t, .9 if not night else .25) + cloud(960, 50, .8, t, .8 if not night else .2) + bird(420, 90, 1, t["line"]) + bird(446, 80, .7, t["line"]) + sparkle(1100, 120, .8, t["line"])))
    far = haze(t, H[0], .5)
    s = "M-900 200 " + "".join(f"H{x} V{170 - (i*29 % 50)} H{x+40} V200 " for i, x in enumerate(range(-880, 2100, 110))) + "V520 H-900Z"
    s = f'<path d="{s}" fill="{far}" stroke="{t["line"]}" stroke-opacity=".35" stroke-width="1.4"/>'
    s += "".join(f'<g transform="translate({x} 120) scale(.5)" opacity=".6">{turbine(t, a)}</g>' for x, a in [(-300, 20), (140, 60), (880, 30), (1500, 80)])
    L.append(("far", 0.14, s))
    fills = [t["wall"], t["roof"] if not night else "#3a3320", t["wall"], "#DCEBF7" if not night else "#22324D"]
    kinds = ["step", "gable", "bell", "gable", "step", "bell", "gable"]
    s = f'<g transform="translate(0 290)" filter="url(#sh{uid})">'
    x, i = -900, 0
    while x < 2100:
        w = 56 if i % 2 else 52; h = 112 + (i * 37 % 40)
        s += canal_house(t, x, w, h, kinds[i % 7], fills[i % 4], True, night); x += w; i += 1
    s += '</g>' + "".join(f'<g transform="translate({x} 276) scale(.9)">{streettree(t, True)}</g>' for x in range(-860, 2100, 150))
    L.append(("houses", 0.3, s))
    s = f'<rect x="-1200" y="290" width="3600" height="26" fill="{H[2]}" {st(t)}/>'
    for x in (-500, 300, 1100, 1800):
        s += f'<g transform="translate({x} 238) scale(.8)">{lampcharger(t)}</g><g transform="translate({x-96} 258) scale(.8)">{car(t, night)}</g>'
    s += "".join(f'<g transform="translate({x} 286)">{bike(t)}</g>' for x in (-200, 640, 1460))
    s += f'<rect x="-1200" y="316" width="3600" height="220" fill="{"#9CC6E8" if not night else "#1B3350"}" {st(t)}/>'
    s += "".join(f'<path d="M{x} {y} q8 -4 16 0" stroke="{t["line"]}" stroke-opacity=".45" stroke-width="1.6" fill="none" stroke-linecap="round"/>' for x in range(-1100, 2300, 70) for y in ((350,) if (x // 70) % 2 else (380,)))
    for bx in (-700, 100, 900, 1700):
        s += (f'<path d="M{bx} 316 Q{bx+80} 276 {bx+160} 316" fill="none" stroke="{t["line"]}" stroke-width="10"/><path d="M{bx} 316 Q{bx+80} 276 {bx+160} 316" fill="none" stroke="{t["wall"]}" stroke-width="6"/>'
              f'<path d="M{bx+18} 316 Q{bx+80} 292 {bx+142} 316" fill="none" stroke="{t["line"]}" stroke-width="2"/>')
    L.append(("quay", 0.6, s))
    s = "".join(boat(t, x, y) for x, y in [(-400, 356), (420, 372), (1260, 352)])
    L.append(("boats", 0.85, s))
    fg, fl = t["leafr"], t["line"]
    from depth import grass
    s = big_leaf(-20, 440, 2.0, 40, fg, fl, uid) + big_leaf(1220, 444, 2.1, -40, fg, fl, uid) + "".join(grass(x, 430, 30, H[2], fl) for x in range(-1000, 2200, 160))
    L.append(("foreground", 1.35, s))
    return L
