import os
from city import *
O = "/home/claude/sp/assets/Illustrations"; os.makedirs(O, exist_ok=True)
def svg(inner, vb="-75 -75 150 150", w=150, h=150, label=""):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{w}" height="{h}" role="img" aria-label="{label}">{inner}</svg>'
def els(t, night):
    return {
        "house-solar": (f'<g transform="translate(-31 -22)">{house(t)}</g>', "House with solar roof"),
        "house-solar-rich": (f'<g transform="translate(-31 -22)">{house(t, True)}</g>', "House with solar roof"),
        "wallbox": (f'<g transform="translate(-14 -16) scale(1.3)">{wallbox(t)}</g>', "Home wallbox"),
        "public-charger": (f'<g transform="translate(-16 -30)">{charger(t)}</g>', "Public charger"),
        "lamp-post-charger": (f'<g transform="translate(-12 -45) scale(.9)">{lampcharger(t)}</g>', "Lamp-post charger"),
        "turbine": (f'<g transform="translate(0 -18)">{turbine(t)}</g>', "Wind turbine"),
        "solar-field": (f'<g transform="translate(-48 -6)">{solarfield(t)}</g>', "Solar panels"),
        "trees": (f'<g transform="translate(-26 -8)">{tree(t)}</g><g transform="translate(24 -16)">{poplar(t)}</g>', "Trees"),
        "trees-rich": (f'<g transform="translate(-26 -8)">{tree(t,14,True)}</g><g transform="translate(24 -16)">{poplar(t,True)}</g>', "Trees"),
        "street-tree": (f'<g transform="translate(0 -6) scale(1.3)">{streettree(t)}</g>', "Street tree"),
        "ev": (f'<g transform="translate(-40 -10)">{car(t, night)}</g>', "Electric car"),
        "ev-van": (f'<g transform="translate(-40 -10)">{van(t)}</g>', "Electric van"),
        "bus": (f'<g transform="translate(-62 -12) scale(.9)">{tram(t)}</g>', "Electric bus"),
        "bike": (f'<g transform="translate(-17 -6) scale(1.2)">{bike(t)}</g>', "Bike"),
        "apartments": (f'<g transform="translate(-35 -50) scale(.9)">{apartment(t)}</g>', "Apartments with roof garden"),
        "apartments-rich": (f'<g transform="translate(-30 -40) scale(.8)">{apartment(t,72,110,4,True)}</g>', "Apartments with roof garden"),
        "row-houses": (f'<g transform="translate(-45 -32)">{rowhouses(t)}</g>', "Row houses"),
        "road-bend": (f'<g transform="translate(-60 -30)">{road_bend(t)}</g>', "Road bend"),
        "road-straight": (f'<g transform="translate(-70 -13) scale(.7 1)">{road_straight(t)}</g>', "Straight road"),
        "road-winding": (road_winding(t, [(0,70),(10,30),(60,30),(40,0),(25,-20),(-30,-20),(-10,-45)], 30, 6), "Road winding into the distance"),
        "sky": (sun(t, night), "Moon and stars" if night else "Sun"),
    }
order = []
for t, night, sfx in [(DAY, False, "day"), (NIGHT, True, "night")]:
    for k, (inner, lab) in els(t, night).items():
        n = f"{k}-{sfx}.svg"; order.append(n)
        open(f"{O}/{n}", "w").write(svg(inner, label=lab))
for f, nm in [(village_scene, "village"), (city_scene, "city")]:
    for t, r, n, sfx, lab in [(DAY, True, False, "hero-day", "rich, home hero"), (DAY, False, False, "day", "soft"), (NIGHT, True, True, "night", "night")]:
        name = f"scene-{nm}-{sfx}.svg"; order.insert(0 if False else len(order), name)
        open(f"{O}/{name}", "w").write(svg(f(t, r, n), "0 0 390 460", 390, 460, f"{nm.title()} scene"))
scenes = [o for o in order if o.startswith("scene")]; rest = [o for o in order if not o.startswith("scene")]
open("/home/claude/sp/assets/order.txt", "w").write("\n".join(scenes + rest))
print(len(order))
