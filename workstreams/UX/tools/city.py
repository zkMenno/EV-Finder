"""Urban solarpunk elements + city scene, sharing kit.py's style and palettes."""
from kit import *

def apartment(t, w=70, h=120, floors=5, rich=False, garden=True):
    s = f'<g {st(t)}><rect x="0" y="0" width="{w}" height="{h}" fill="{t["wall"]}"/>'
    cols = max(2, int(w // 22))
    for f in range(floors):
        for c in range(cols):
            x = 8 + c * ((w - 16) / cols); y = 10 + f * ((h - 24) / floors)
            s += f'<rect x="{x:.1f}" y="{y:.1f}" width="{(w-16)/cols-6:.1f}" height="{(h-24)/floors-8:.1f}" fill="{t["window"]}" stroke-width="1.3"/>'
        if f % 2 == 1:  # balcony planters
            s += f'<rect x="4" y="{10 + (f+1)*((h-24)/floors) - 7:.1f}" width="{w-8}" height="5" fill="{t["leafr"] if rich else t["leaf"]}" stroke-width="1.2"/>'
    # roof: solar + garden
    s += f'<path d="M4 0 L12 -9 H{w/2-2} L{w/2-8} 0Z" fill="{t["solar"]}" stroke-width="1.4"/>'
    if garden:
        for i, r in enumerate([7, 9, 6]):
            s += f'<circle cx="{w/2 + 6 + i*11}" cy="{-r+1}" r="{r}" fill="{t["leafr"] if rich else t["leaf"]}" stroke-width="1.5"/>'
    return s + '</g>'

def rowhouses(t, rich=False):
    s = f'<g {st(t)}>'
    fills = [t["wall"], t["roof"], t["wall"]]
    for i in range(3):
        x = i * 30
        s += f'<rect x="{x}" y="14" width="30" height="46" fill="{fills[i]}"/><path d="M{x} 14 L{x+15} 0 L{x+30} 14Z" fill="{t["roofr"] if rich else t["roof"]}"/>'
        s += f'<rect x="{x+9}" y="40" width="10" height="20" fill="{t["door"]}" stroke-width="1.3"/><rect x="{x+8}" y="22" width="14" height="10" fill="{t["window"]}" stroke-width="1.3"/>'
    s += f'<path d="M33 12 L45 2 L57 12Z" fill="{t["solar"]}" stroke-width="1.3"/>'
    return s + '</g>'

def tram(t, lights=False):
    s = (f'<g {st(t)}><path d="M6 0 H124 Q134 0 136 12 L138 34 H0 L2 12 Q4 0 6 0Z" fill="{t["roofr"]}"/>'
         f'<path d="M50 0 L56 -10 H86 L92 0" fill="none" stroke-width="1.6"/><path d="M60 -10 L71 -22 M71 -22 L82 -10" fill="none" stroke-width="1.6"/>')
    for i in range(5):
        s += f'<rect x="{10 + i*24}" y="7" width="18" height="13" rx="2" fill="{t["window"]}" stroke-width="1.3"/>'
    s += f'<rect x="0" y="26" width="138" height="4" fill="{t["solar"]}" stroke="none"/>'
    s += f'<circle cx="26" cy="36" r="5" fill="{t["wall"]}"/><circle cx="112" cy="36" r="5" fill="{t["wall"]}"/></g>'
    return s

def lampcharger(t):
    return (f'<g {st(t)}><path d="M0 0 V90" stroke-width="3"/><path d="M0 2 Q0 -10 14 -10 H22" fill="none" stroke-width="3"/>'
            f'<path d="M16 -12 H32 L28 -4 H20Z" fill="{t["sun"]}" stroke-width="1.6"/>'
            f'<rect x="-7" y="44" width="14" height="22" rx="4" fill="{t["wall"]}" stroke-width="1.8"/>'
            f'<path d="M1.5 48 L-2 55 H1 L0 61 L3.5 54 H0.5Z" fill="{t["sun"]}" stroke-width="1"/>'
            f'<path d="M7 58 Q24 58 26 74" fill="none" stroke-width="1.8"/></g>')

def bike(t):
    return (f'<g {st(t, 1.8)} fill="none"><circle cx="0" cy="12" r="10"/><circle cx="34" cy="12" r="10"/>'
            f'<path d="M0 12 L12 -2 H26 L34 12 M12 -2 L17 12 L26 -2 M10 -6 H16 M26 -2 L24 -8 H30"/></g>')

def streettree(t, rich=False):
    return (f'<g {st(t)}><rect x="-10" y="18" width="20" height="10" fill="{t["roofr"] if rich else t["roof"]}"/>'
            f'<line x1="0" y1="0" x2="0" y2="18"/><circle cy="-6" r="13" fill="{t["leafr"] if rich else t["leaf"]}"/></g>')

def city_scene(t, rich, night=False):
    s = '<defs><filter id="sh2" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="3" stdDeviation="2" flood-color="#000" flood-opacity=".18"/></filter></defs>'
    s += f'<rect width="390" height="460" fill="{t["sky"] if (rich or night) else t["bg"]}"/>'
    if not night:
        s += "".join(f'<path d="M-10 {40+i*12} Q 90 {15+i*12} 180 {50+i*10} T 400 {25+i*12}" stroke="{t["grid"]}" fill="none" stroke-width="1"/>' for i in range(4))
    s += f'<g transform="translate(300 90)">{sun(t, night)}</g>'
    H = (t["r1"], t["r2"], t["r3"]) if rich else (t["h1"], t["h2"], t["h3"])
    # back skyline (pale silhouette) with turbines beyond the city
    s += f'<path d="M-10 250 V190 H30 V160 H60 V200 H95 V150 H120 V135 H140 V210 H175 V175 H215 V200 H250 V165 H285 V205 H320 V180 H355 V215 H400 V250Z" fill="{H[0]}" {st(t)} filter="url(#sh2)"/>'
    for x, sc, a in [(210, .55, 30), (238, .6, 80)]:
        s += f'<g transform="translate({x} 120) scale({sc})">{turbine(t, a)}</g>'
    # park strip
    s += f'<path d="M-10 268 Q 120 245 220 262 Q 320 278 400 255 V300 H-10Z" fill="{H[1]}" {st(t)} filter="url(#sh2)"/>'
    # mid buildings
    s += f'<g transform="translate(18 158)" filter="url(#sh2)">{apartment(t, 72, 128, 5, rich)}</g>'
    s += f'<g transform="translate(108 196)" filter="url(#sh2)">{rowhouses(t, rich)}</g>'
    s += f'<g transform="translate(214 140)" filter="url(#sh2)">{apartment(t, 64, 146, 6, rich)}</g>'
    s += f'<g transform="translate(292 176)" filter="url(#sh2)">{apartment(t, 84, 110, 4, rich, True)}</g>'
    # street: pavement, tram line, road
    s += f'<rect x="-10" y="286" width="410" height="26" fill="{H[2]}" {st(t)}/>'
    s += f'<rect x="-10" y="312" width="410" height="60" fill="{t["road"]}" {st(t)}/>'
    s += f'<path d="M-10 384 H400 M-10 392 H400" stroke="{t["line"]}" stroke-width="1.5"/>'
    s += f'<rect x="-10" y="372" width="410" height="40" fill="none"/>'
    s += f'<g transform="translate(40 351)">{tram(t)}</g>'
    s += f'<rect x="-10" y="404" width="410" height="60" fill="{H[2] if not rich else H[1]}" {st(t)}/>'
    # kerbside charging car + lamp charger, bike, trees
    s += f'<g transform="translate(332 212)">{lampcharger(t)}</g>'
    s += f'<g transform="translate(240 286) scale(.9)">{car(t, night)}</g>'
    for x in (90, 200):
        s += f'<g transform="translate({x} 262) scale(.85)">{streettree(t, rich)}</g>'
    s += f'<g transform="translate(160 416)">{bike(t)}</g><g transform="translate(240 420) scale(.9)">{bike(t)}</g>'
    for x, y in [(40, 428), (330, 430), (370, 418)]:
        s += f'<g transform="translate({x} {y})">{tree(t, 12, rich)}</g>'
    return s

def village_scene(t, rich, night=False):
    s = scene(t, rich, night)
    # extra cottages + bell tower on the middle hill to read as a village
    s += f'<g transform="translate(150 246) scale(.55)">{house(t, rich)}</g><g transform="translate(195 238) scale(.5)">{house(t, rich)}</g>'
    s += (f'<g transform="translate(232 226)" {st(t, 1.6)}><rect x="0" y="6" width="12" height="26" fill="{t["wall"]}"/>'
          f'<path d="M-2 7 L6 -8 L14 7Z" fill="{t["roofr"] if rich else t["roof"]}"/><rect x="4" y="12" width="4" height="6" fill="{t["window"]}" stroke-width="1"/></g>')
    return s

if __name__ == "__main__":
    def ecell(svg, label, t, vb="-75 -75 150 150"): return cell(svg, label, t, vb=vb)
    def urban(t, night=False):
        return "".join([
            ecell(f'<g transform="translate(-35 -50) scale(.9)">{apartment(t)}</g>', "Apartments + roof garden", t),
            ecell(f'<g transform="translate(-45 -32)">{rowhouses(t)}</g>', "Row houses", t),
            ecell(f'<g transform="translate(-62 -12) scale(.9)">{tram(t)}</g>', "Tram", t),
            ecell(f'<g transform="translate(-12 -45) scale(.9)">{lampcharger(t)}</g>', "Lamp-post charger", t),
            ecell(f'<g transform="translate(-17 -6) scale(1.2)">{bike(t)}</g>', "Bike", t),
            ecell(f'<g transform="translate(0 -6) scale(1.3)">{streettree(t)}</g>', "Street tree", t),
            ecell(f'<g transform="translate(-30 -40) scale(.8)">{apartment(t, 72, 110, 4, True)}</g>', "Apartments, rich", t)])
    scenes = [(village_scene, DAY, True, False, "Village · day · rich (hero)"), (city_scene, DAY, True, False, "City · day · rich (hero)"),
              (village_scene, DAY, False, False, "Village · day · soft"), (city_scene, DAY, False, False, "City · day · soft"),
              (village_scene, NIGHT, True, True, "Village · night"), (city_scene, NIGHT, True, True, "City · night")]
    html = (f"<!doctype html><style>{CSS}</style><body><h1>Illustration kit · city + village</h1>"
            "<p>The same B + C style for the three \"where you live\" answers: city, town, countryside. Kerbside lamp-post charging belongs with the city.</p>"
            "<h2>Scenes</h2><div class='scenes' style='flex-wrap:wrap'>" +
            "".join(f"<figure><svg viewBox='0 0 390 460' width='350' height='413'>{f(t, r, n)}</svg><figcaption>{c}</figcaption></figure>" for f, t, r, n, c in scenes) +
            "</div><h2>Urban elements · Day trip</h2><div class='row'>" + urban(DAY) +
            "</div><h2>Urban elements · Night drive</h2><div class='row'>" + urban(NIGHT, True) + "</div></body>")
    render(html, "kit-city", 1602, 1610)
