import re, json
from city import *
P="/home/claude/board/project"
def uniq(svg, k):
    return svg.replace('id="sh"', f'id="sh{k}"').replace('url(#sh)', f'url(#sh{k})').replace('id="sh2"', f'id="shc{k}"').replace('url(#sh2)', f'url(#shc{k})')
def sc(f, t, r, n, k, label, w=300):
    return (f'<figure style="margin: 0; display: flex; flex-direction: column; gap: 8px"><svg viewBox="0 0 390 460" width="{w}" height="{round(w*460/390)}" role="img" aria-label="{label}" style="display: block; border-radius: 18px">{uniq(f(t, r, n), k)}</svg>'
            f'<figcaption style="font: 700 15px/20px \'Atkinson Hyperlegible\', sans-serif; color: #16233A">{label}</figcaption></figure>')
def el(svg, label, t):
    return (f'<figure style="margin: 0; background: {t["bg"]}; border: 1px solid #C9D3DF; border-radius: 14px; padding: 10px; display: flex; flex-direction: column; align-items: center; gap: 4px">'
            f'<svg viewBox="-75 -75 150 150" width="120" height="120" role="img" aria-label="{label}">{svg}</svg>'
            f'<figcaption style="font: 700 14px/18px \'Atkinson Hyperlegible\', sans-serif; color: {t["line"]}; text-align: center">{label}</figcaption></figure>')
import export
from depth import village_layers, city_layers
def dflat(fn):
    def f(t, r, n):
        return ''.join(f'<g>{x}</g>' for _,_,x in fn(t, r, n, 'b'+str(id(t)%97)+str(int(r))+str(int(n))))
    return f
def grid(t, night):
    names = {"house-solar":"House + solar","house-solar-rich":"House, rich","wallbox":"Wallbox","public-charger":"Public charger","lamp-post-charger":"Lamp-post charger",
             "turbine":"Wind turbine","solar-field":"Solar field","trees":"Trees","trees-rich":"Trees, rich","street-tree":"Street tree","ev":"EV","ev-van":"EV van",
             "tram":"Tram","bike":"Bike","apartments":"Apartments","apartments-rich":"Apartments, rich","row-houses":"Row houses","road-bend":"Road bend",
             "road-straight":"Road straight","road-winding":"Winding road","sky":"Moon + stars" if night else "Sun"}
    return "".join(el(inner, names[k], t) for k, (inner, _) in export.els(t, night).items())
sw = [("hill-1","#EEF6E8","#1F3324"),("hill-2","#DDEFD3","#284A2E"),("hill-3","#C7E4B8","#2F5A33"),("hill-rich-1","#B9DCA6","#1F3324"),("hill-rich-2","#7BB661","#284A2E"),
      ("hill-rich-3","#4E9A3F","#2F5A33"),("leaf","#B9DCA6","#2B4A33"),("forest","#3F8A3A","#2F6B35"),("solar-gold","#F0BE45","#6B5520"),("solar-panel","#2F679C","#3B78AE")]
swh = "".join(f'<div style="display: grid; grid-template-columns: 40px 40px 1fr; gap: 10px; align-items: center; background: #FFFFFF; border-radius: 10px; padding: 8px 12px">'
              f'<div style="height: 30px; border-radius: 6px; border: 2px solid #16233A; background: {l}"></div><div style="height: 30px; border-radius: 6px; border: 2px solid #16233A; background: {d}"></div>'
              f'<span style="font: 400 14px/18px \'Atkinson Hyperlegible\', sans-serif; color: #16233A"><b>{n}</b><br>{l} · {d} · ink {cr(l, "#16233A"):.1f}:1</span></div>' for n, l, d in sw)
H = 2780
body = f'''<div style="width: 1440px; height: {H}px; box-sizing: border-box; padding: 64px; background: #F2F6FA; color: #16233A; font-family: 'Atkinson Hyperlegible', system-ui, sans-serif; display: flex; flex-direction: column; gap: 28px">
<header style="display: flex; flex-direction: column; gap: 8px"><h1 style="margin: 0; font: 800 44px/52px 'Bitter', Georgia, serif">Illustrations: solarpunk, within reach</h1>
<p style="margin: 0; max-width: 980px; font: 400 18px/28px 'Atkinson Hyperlegible', sans-serif; color: #45546F">Used EVs got good. Layered paper hills, a road winding into the distance like the tick in the logo, a 2px ink line. Village by default, city for people who live in one. Rich colour only in the home hero; soft everywhere else; deep green at night. Hero scenes are layered (haze, doodles, blurred foreground leaves) and drift with parallax: try it at claude.ai/artifact/BRpRwoSAM1rLeNtcLtd5Gg</p></header>
<h2 style="margin: 8px 0 0; font: 800 24px/30px 'Bitter', Georgia, serif">Scenes</h2>
<div style="display: grid; grid-template-columns: repeat(4, 300px); gap: 24px">
{sc(dflat(village_layers), DAY, True, False, "a", "Village · home hero, layered for parallax")}{sc(dflat(city_layers), DAY, True, False, "b", "City · home hero, layered for parallax")}{sc(village_scene, DAY, False, False, "c", "Village · pages (soft)")}{sc(city_scene, DAY, False, False, "d", "City · pages (soft)")}
{sc(dflat(village_layers), NIGHT, True, True, "e", "Village · Night drive")}{sc(dflat(city_layers), NIGHT, True, True, "f", "City · Night drive")}
</div>
<h2 style="margin: 8px 0 0; font: 800 24px/30px 'Bitter', Georgia, serif">Kit · Day trip</h2>
<div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 12px">{grid(DAY, False)}</div>
<h2 style="margin: 8px 0 0; font: 800 24px/30px 'Bitter', Georgia, serif">Kit · Night drive</h2>
<div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 12px">{grid(NIGHT, True)}</div>
<h2 style="margin: 8px 0 0; font: 800 24px/30px 'Bitter', Georgia, serif">Illustration colours (light · dark), never text</h2>
<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px">{swh}</div>
</div>'''
HEADB = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Illustrations</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&amp;family=Bitter:wght@700;800&amp;family=Patrick+Hand&amp;display=swap">
<style>
body{margin:0}
a{color:#2B5F91}a:hover{color:#16233A}
</style>
</helmet>
"""
TAILB = f"""
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":1440,"height":{H}}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
"""
open(f"{P}/Illustrations.dc.html", "w").write(HEADB + body + TAILB)
# hero scene svg for PhoneHome
open("/home/claude/sp/hero_inline.svg", "w").write(f'<svg viewBox="0 0 390 460" width="390" height="460" aria-hidden="true" style="display: block">{uniq(village_scene(DAY, True, False), "h")}</svg>')
