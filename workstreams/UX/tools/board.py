import sys, json, re; sys.path.insert(0,'/home/claude/gen')
from icons import ICONS
B="/home/claude/board/project"
INK="#16233A"; INK2="#45546F"; INK3="#5B6982"; SKY="#3B78AE"; ACT="#2F679C"; SUN="#FFD166"; TINT="#E8F1F9"; SUNT="#FFF2CC"
LINE="#D6DFEA"; LINES="#8091AB"; SUNK="#F2F6FA"; MEA="#7BB661"; SEA="#CFE3F3"; LINK="#2B5F91"; SUCC="#2F6E22"; MEAT="#E4F2DC"; WARN="#8A5A00"; DANG="#A1224A"; DANGT="#FBE3EA"
D_BG="#111A2B"; D_SURF="#18243A"; D_INK="#EEF3F9"; D_SKY="#93C1EA"
TEX={"paper":"/_blob/6e13f946a79255d2cc7d6ec4006d3046","contour":"/_blob/bc5a64d6e86fa3acefcbb280e144e386","grid":"/_blob/d39f4838adf6e42d7b7c6d657f8e2efa","hatch":"/_blob/e39e1711a3888955042fc5d347e1fc52","halftone":"/_blob/a9acdd243624eef728a7d17484426d91"}
FONTS='<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&amp;family=Bitter:wght@700;800&amp;family=Patrick+Hand&amp;display=swap">'
FD="'Bitter', Georgia, serif"; FT="'Atkinson Hyperlegible', system-ui, sans-serif"; FH="'Patrick Hand', cursive"
TEXCSS="".join(f".tex-{k}{{background-image:url({v});}}" for k,v in TEX.items())+".tex-contour{background-size:240px 160px}.tex-grid{background-size:48px 48px}"
def page(title,w,h,body,extra_css=""):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
{FONTS}
<style>
body{{margin:0}}
a{{color:{LINK}}}a:hover{{color:{INK}}}
{TEXCSS}
{extra_css}
</style>
</helmet>
<div style="width: {w}px; height: {h}px; box-sizing: border-box; background: #FFFFFF; color: {INK}; font-family: {FT}; font-size: 17px; line-height: 27px; position: relative; overflow: hidden">
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{w},"height":{h}}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''
# ---- logo (inline, hex) from generated v5 lockup by swapping vars
def logo(h,theme="light",small=False):
    s=open(f"/home/claude/logo/v5-lockup{'-small' if small else ''}.svg").read()
    m={"var(--ink)":INK if theme=="light" else D_INK,"var(--sky)":SKY if theme=="light" else D_SKY,"var(--sunflower)":SUN,"var(--paper)":"#FFFFFF" if theme=="light" else D_BG}
    for k,v in m.items(): s=s.replace(k,v)
    return s.replace('<svg class="evs-lockup"',f'<svg style="height: {h}px; width: auto; display: block"',1)
def appicon(px,small=False):
    s=open(f"/home/claude/logo/v5-icon{'-small' if small else ''}.svg").read()
    for k,v in {"var(--ink)":INK,"var(--sky)":D_SKY,"var(--paper)":"#EEF3F9","var(--sunflower)":SUN}.items(): s=s.replace(k,v)
    return s.replace('<svg class="evs-icon" viewBox="0 0 64 64" aria-hidden="true">',f'<svg viewBox="0 0 64 64" width="{px}" height="{px}" role="img" aria-label="EV Shortlist app icon">',1)
def icon(name,px=24,color=INK):
    body=ICONS[name].replace('#16233A',color)
    return f'<svg viewBox="0 0 24 24" width="{px}" height="{px}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="flex: none">{body}</svg>'
TICK_P="M10 34 L24 48 L52 16"
def tickbox(px=24,on=True):
    if on: return f'<svg viewBox="0 0 64 64" width="{px}" height="{px}" aria-hidden="true" style="flex: none"><path d="{TICK_P}" fill="none" stroke="{INK}" stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/><path d="{TICK_P}" fill="none" stroke="{SKY}" stroke-width="8.5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="52" cy="14" r="6.8" fill="{SUN}" stroke="{INK}" stroke-width="2.6"/></svg>'
    return f'<svg viewBox="0 0 64 64" width="{px}" height="{px}" aria-hidden="true" style="flex: none"><rect x="10" y="12" width="40" height="40" rx="10" fill="none" stroke="{LINES}" stroke-width="3"/></svg>'
def btn(label,kind="primary",ico=None,after=None,href="#"):
    st={"primary":f"background: {ACT}; color: #FFFFFF; border: 2px solid {ACT}; box-shadow: 0 2px 0 rgba(22,35,58,.16)",
        "secondary":f"background: #FFFFFF; color: {INK}; border: 2px solid {LINES}",
        "ghost":f"background: transparent; color: {LINK}; border: 2px solid transparent; text-decoration: underline"}[kind]
    i=icon(ico,20,"#FFFFFF" if kind=="primary" else INK) if ico else ""
    a=icon(after,18,"#FFFFFF" if kind=="primary" else INK) if after else ""
    return f'<a href="{href}" style="display: inline-flex; align-items: center; gap: 8px; min-height: 48px; padding: 0 20px; box-sizing: border-box; border-radius: 10px; font: 700 17px/24px {FT}; text-decoration: none; {st}">{i}<span>{label}</span>{a}</a>'
def pick(on=True,label=True):
    bg=SUNT if on else "#FFFFFF"; bd=INK if on else LINES
    txt=("On your shortlist" if on else "Add to shortlist") if label else ""
    pad="0 18px 0 12px" if label else "0"; wd="" if label else "width: 48px; justify-content: center;"
    return f'<button type="button" aria-pressed="{"true" if on else "false"}" style="display: inline-flex; align-items: center; gap: 8px; min-height: 48px; {wd} padding: {pad}; border-radius: 10px; border: 2px solid {bd}; background: {bg}; color: {INK}; font: 700 17px/24px {FT}; cursor: pointer" {"" if label else "aria-label=\"Add Kia e-Niro to shortlist\""}>{tickbox(28,on)}{("<span>"+txt+"</span>") if txt else ""}</button>'
def chip(text,kind,ico=None):
    c={"money":(SUNT,INK),"checked":(MEAT,SUCC),"caution":(SUNT,WARN),"fault":(DANGT,DANG),"plain":(SUNK,INK2)}[kind]
    i=icon(ico,16,c[1]) if ico else ""
    return f'<span style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 6px; background: {c[0]}; color: {c[1]}; font: 400 15px/22px {FT}">{i}{text}</span>'
def label(plain,term):
    return f'<span style="display: block"><span style="display: block; font: 700 17px/24px {FT}; color: {INK}">{plain}</span><span style="display: block; font: 400 15px/22px {FT}; color: {INK2}">{term}</span></span>'
def note(items,width=300,tilt=-1.2,title="My shortlist"):
    lis=""
    for car,why,out in items:
        name_style=f"color: {INK3}; text-decoration: line-through; text-decoration-color: {SKY}; text-decoration-thickness: 3px" if out else f"color: {INK}"
        lis+=f'<li style="display: grid; grid-template-columns: 28px 1fr; column-gap: 12px; align-items: center"><span style="grid-row: span 2">{tickbox(28,not out)}</span><span style="font: 700 17px/22px {FT}; {name_style}">{car}</span><span style="font: 400 19px/20px {FH}; color: {INK2}">{why}</span></li>'
    return f'''<div style="position: relative; width: {width}px; box-sizing: border-box; background: #FFFFFF; border: 1.5px solid {INK}; border-radius: 4px 18px 18px 18px; box-shadow: 0 4px 0 rgba(22,35,58,.18), 0 10px 24px rgba(22,35,58,.10); padding: 24px 22px 18px; transform: rotate({tilt}deg)">
<div style="position: absolute; top: -12px; left: 28px; width: 72px; height: 22px; background: {SUN}; opacity: .9; border-radius: 3px; transform: rotate(-4deg)"></div>
<p style="margin: 0 0 12px; font: 400 26px/30px {FH}; color: {INK}">{title}</p>
<ol style="list-style: none; margin: 0; padding: 0; display: grid; gap: 12px">{lis}</ol></div>'''
def mapart(w,h,route=True):
    return f'''<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" aria-hidden="true" style="display: block">
<defs><pattern id="hh{w}" width="14" height="14" patternUnits="userSpaceOnUse"><path d="M2 12 L7 7" stroke="{INK}" stroke-opacity=".16" stroke-width="1.4" stroke-linecap="round"/></pattern></defs>
<rect width="{w}" height="{h}" fill="{TINT}"/>
<path d="M{w*0.18:.0f} 0 C {w*0.28:.0f} {h*0.22:.0f} {w*0.1:.0f} {h*0.42:.0f} {w*0.22:.0f} {h*0.6:.0f} C {w*0.32:.0f} {h*0.75:.0f} {w*0.16:.0f} {h*0.9:.0f} {w*0.26:.0f} {h} L{w} {h} L{w} 0 Z" fill="{MEA}" fill-opacity=".55"/>
<path d="M{w*0.18:.0f} 0 C {w*0.28:.0f} {h*0.22:.0f} {w*0.1:.0f} {h*0.42:.0f} {w*0.22:.0f} {h*0.6:.0f} C {w*0.32:.0f} {h*0.75:.0f} {w*0.16:.0f} {h*0.9:.0f} {w*0.26:.0f} {h} L{w} {h} L{w} 0 Z" fill="url(#hh{w})"/>
<g fill="none" stroke="{INK}" stroke-opacity=".12" stroke-width="1.2"><path d="M{w*0.3:.0f} {h*0.2:.0f} C {w*0.5:.0f} {h*0.1:.0f} {w*0.7:.0f} {h*0.3:.0f} {w} {h*0.2:.0f}"/><path d="M{w*0.3:.0f} {h*0.35:.0f} C {w*0.5:.0f} {h*0.25:.0f} {w*0.7:.0f} {h*0.45:.0f} {w} {h*0.35:.0f}"/></g>
{f'<path d="M{w*0.32:.0f} {h*0.9:.0f} C {w*0.5:.0f} {h*0.8:.0f} {w*0.55:.0f} {h*0.6:.0f} {w*0.7:.0f} {h*0.55:.0f} S {w*0.9:.0f} {h*0.35:.0f} {w*0.96:.0f} {h*0.12:.0f}" fill="none" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round"/><path d="M{w*0.32:.0f} {h*0.9:.0f} C {w*0.5:.0f} {h*0.8:.0f} {w*0.55:.0f} {h*0.6:.0f} {w*0.7:.0f} {h*0.55:.0f} S {w*0.9:.0f} {h*0.35:.0f} {w*0.96:.0f} {h*0.12:.0f}" fill="none" stroke="{SKY}" stroke-width="3" stroke-dasharray="2 8" stroke-linecap="round"/>' if route else ''}
</svg>'''
def header_phone(active="Explore",count=3):
    return f'''<div style="display: flex; align-items: center; justify-content: space-between; padding: 14px 18px; border-bottom: 1.5px solid {LINE}; background: #FFFFFF">
{logo(26,small=True)}
<a href="#" aria-label="Search" style="display: inline-grid; place-items: center; width: 44px; height: 44px; border-radius: 10px; color: {INK}">{icon("search",22)}</a></div>'''
def tabbar(active="Explore",count=3):
    items=[("Explore","explore"),("Compare","compare"),("Shortlist","shortlist"),("Learn","learn")]
    out=""
    for lab,ic in items:
        on=lab==active
        badge=f'<span style="position: absolute; top: 4px; left: calc(50% + 6px); min-width: 20px; height: 20px; padding: 0 5px; box-sizing: border-box; border-radius: 999px; background: {SUN}; border: 2px solid {INK}; font: 700 12px/16px {FT}; color: {INK}; text-align: center">{count}</span>' if lab=="Shortlist" else ""
        out+=f'<a href="#" {"aria-current=\"page\"" if on else ""} style="position: relative; display: grid; justify-items: center; gap: 2px; padding: 8px 4px 10px; text-decoration: none; color: {INK if on else INK2}; font: {"700" if on else "400"} 14px/18px {FT}">{icon(ic,24,SKY if on else INK2)}<span>{lab}</span>{badge}</a>'
    return f'<nav aria-label="Main" style="position: absolute; left: 0; right: 0; bottom: 0; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); background: #FFFFFF; border-top: 1.5px solid {LINE}; padding-bottom: 14px">{out}</nav>'
def tray(cars,count):
    slots="".join(f'<span style="display: inline-flex; align-items: center; padding: 6px 10px; border-radius: 6px; background: {TINT}; font: 700 14px/18px {FT}; white-space: nowrap">{c}</span>' for c in cars)
    return f'''<div style="position: absolute; left: 12px; right: 12px; bottom: 86px; display: flex; align-items: center; gap: 8px; padding: 10px 12px; background: #FFFFFF; border: 1.5px solid {INK}; border-radius: 18px; box-shadow: 0 4px 0 rgba(22,35,58,.18), 0 10px 24px rgba(22,35,58,.10)">
{tickbox(26)}<div style="display: flex; gap: 6px; overflow: hidden; flex: 1">{slots}</div>
<a href="#" style="display: inline-flex; align-items: center; min-height: 44px; padding: 0 14px; border-radius: 10px; background: {ACT}; color: #FFFFFF; font: 700 15px/20px {FT}; text-decoration: none; white-space: nowrap">Compare {count}</a></div>'''
def carcard(name,years,price,rng,charge,save,on=False,extra=""):
    return f'''<article style="position: relative; background: #FFFFFF; border: 1.5px solid {LINE}; border-radius: 18px; box-shadow: 0 2px 0 rgba(22,35,58,.16); padding: 16px 16px 16px; display: grid; gap: 10px">
<div style="display: flex; justify-content: space-between; gap: 10px; align-items: flex-start"><div><div style="font: 800 20px/26px {FD}; color: {INK}">{name}</div><div style="font: 400 15px/22px {FT}; color: {INK2}">{years}</div></div>{pick(on,False)}</div>
<div style="font: 700 22px/28px {FT}; color: {INK}">{price}<span style="font: 400 15px/22px {FT}; color: {INK2}"> used, NL</span></div>
<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px"><div><b style="display: block; font: 700 17px/24px {FT}">{rng}</b><span style="font: 400 14px/20px {FT}; color: {INK2}">Real range, winter to summer</span></div><div><b style="display: block; font: 700 17px/24px {FT}">{charge}</b><span style="font: 400 14px/20px {FT}; color: {INK2}">Added in 20 min</span></div></div>
<div style="display: flex; gap: 6px; flex-wrap: wrap">{chip(save,"money","price")}{extra}</div></article>'''
SAMPLE=f'<p style="margin: 0; font: 400 13px/18px {FT}; color: {INK3}">Sample figures for illustration only.</p>'
files={}
# ===== Main: brand sheet
sw=lambda name,hexv,use,dark=False: f'<div style="display: grid; gap: 8px"><div style="height: 88px; border-radius: 14px; background: {hexv}; border: 1.5px solid {LINE}"></div><div><b style="display: block; font: 700 16px/22px {FT}">{name}</b><span style="display: block; font: 400 14px/20px {FT}; color: {INK2}">{hexv} · {use}</span></div></div>'
main=f'''<div class="tex-paper" style="position: absolute; inset: 0; background-color: {TINT}"></div>
<div style="position: relative; padding: 64px 72px; display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr); gap: 56px; height: 100%; box-sizing: border-box">
<div style="display: flex; flex-direction: column; gap: 40px">
<div style="background: #FFFFFF; border-radius: 22px; border: 1.5px solid {LINE}; padding: 48px 44px; display: grid; gap: 28px">
{logo(96)}
<p style="margin: 0; font: 400 22px/32px {FT}; color: {INK2}">Compare EVs. Make your shortlist.</p></div>
<div style="display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 24px; align-items: center">
<div style="background: {D_BG}; border-radius: 22px; padding: 40px 36px">{logo(56,"dark")}</div>
<div style="display: flex; gap: 18px; align-items: flex-end">{appicon(112)}{appicon(56)}{appicon(28,True)}</div></div>
<div style="display: grid; gap: 10px"><p style="margin: 0; font: 400 15px/22px {FT}; color: {INK2}">The V is a tick that winds and narrows like a road to a sunflower sun. Working logo for the working title.</p></div>
<div style="background: #FFFFFF; border-radius: 22px; border: 1.5px solid {LINE}; padding: 24px 28px; display: grid; gap: 14px"><span style="font: 700 16px/22px {FT}">Brand devices</span>
<div style="display: flex; gap: 22px; align-items: center; flex-wrap: wrap">{tickbox(40)}<span style="width: 28px; height: 28px; border-radius: 50%; background: {SUN}; box-shadow: 0 0 0 2.5px {INK}"></span>{icon("route",36)}{icon("range",36)}{icon("charge-stop",36)}{icon("shortlist",36)}<div style="flex: 1; min-width: 120px; display: flex; align-items: center; gap: 6px"><div style="flex: 1; height: 4px; background-image: radial-gradient(circle, {SKY} 1.6px, transparent 2px); background-size: 12px 4px; background-repeat: repeat-x"></div><div style="width: 12px; height: 12px; border-radius: 50%; background: {SUN}; box-shadow: 0 0 0 2px {INK}"></div></div></div></div>
</div>
<div style="display: flex; flex-direction: column; gap: 36px">
<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px">
{sw("Ink",INK,"text, wordmark")}{sw("Sky",SKY,"brand, routes")}{sw("Action",ACT,"primary buttons")}
{sw("Sunflower",SUN,"chosen, sun")}{sw("Sky tint",TINT,"bands, chips")}{sw("Meadow",MEA,"land, decorative")}</div>
<div style="background: #FFFFFF; border-radius: 22px; border: 1.5px solid {LINE}; padding: 32px 32px; display: grid; gap: 18px">
<div style="font: 800 48px/52px {FD}; color: {INK}">Bitter for headings</div>
<div style="font: 400 19px/30px {FT}; color: {INK}">Atkinson Hyperlegible for everything people read and compare: 330 km in winter, €15,500–19,000 used.</div>
<div style="font: 400 26px/30px {FH}; color: {INK2}">Patrick Hand for notes: fits the dog</div></div>
</div></div>'''
files["Main.dc.html"]=(page("Brand sheet",1440,900,main),1440,900,"Brand: logo, palette, type")
# ===== Icons
names=list(ICONS)
cells="".join(f'<div style="display: grid; justify-items: center; gap: 10px; padding: 18px 8px; background: #FFFFFF; border: 1.5px solid {LINE}; border-radius: 14px">{icon(n,40)}{icon(n,20)}<span style="font: 400 13px/18px {FT}; color: {INK2}">{n}</span></div>' for n in names)
icons_html=f'''<div style="padding: 56px 64px; display: grid; gap: 28px">
<div><h1 style="margin: 0; font: 800 40px/46px {FD}">Icons</h1><p style="margin: 6px 0 0; color: {INK2}">Map symbols: 24px grid, 2px ink line, one flat fill at most. Always paired with a label.</p></div>
<div style="display: grid; grid-template-columns: repeat(9, minmax(0, 1fr)); gap: 12px">{cells}</div></div>'''
files["Icons.dc.html"]=(page("Icon set",1440,880,icons_html),1440,880,"Icons")
# ===== Elements
el=f'''<div style="padding: 56px 64px; display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 48px">
<div style="display: grid; gap: 36px; align-content: start">
<h1 style="margin: 0; font: 800 40px/46px {FD}">Elements</h1>
<section style="display: grid; gap: 14px"><h2 style="margin: 0; font: 700 22px/28px {FD}">Buttons</h2><div style="display: flex; gap: 12px; flex-wrap: wrap; align-items: center">{btn("See listings on AutoScout24",after="see-listings")}{btn("Share your shortlist","secondary","share")}{btn("Clear filters","ghost")}</div></section>
<section style="display: grid; gap: 14px"><h2 style="margin: 0; font: 700 22px/28px {FD}">Shortlist toggle</h2><div style="display: flex; gap: 12px; align-items: center">{pick(False)}{pick(True)}{pick(False,False)}</div></section>
<section style="display: grid; gap: 14px"><h2 style="margin: 0; font: 700 22px/28px {FD}">Chips</h2><div style="display: flex; gap: 8px; flex-wrap: wrap">{chip("€95 a month cheaper to run","money","price")}{chip("Checked data","checked","battery-health")}{chip("Air-cooled battery","caution","air-cooled")}{chip("Known issue: charging port","fault","known-issue")}{chip("2019–2022","plain")}</div></section>
<section style="display: grid; gap: 14px"><h2 style="margin: 0; font: 700 22px/28px {FD}">Label and legend</h2>
<div style="display: flex; gap: 10px; align-items: center">{label("Charges fast on older chargers","400 V compatibility")}<span style="display: inline-grid; place-items: center; width: 30px; height: 30px; border-radius: 999px; border: 1.5px solid {LINES}; font: 700 15px/1 {FT}">i</span></div>
<div style="max-width: 340px; background: #FFFFFF; border: 1.5px solid {INK}; border-radius: 10px; box-shadow: 0 4px 0 rgba(22,35,58,.18), 0 10px 24px rgba(22,35,58,.10); padding: 14px 16px; font: 400 15px/22px {FT}"><div style="display: flex; gap: 8px; align-items: center; font-weight: 700; margin-bottom: 4px">{icon("voltage-800",22)}400 V compatibility</div>Most fast chargers built before 2022 deliver 400 volts. Some 800 V cars charge slowly on them unless they have a booster. <a href="#">Read more about voltage</a></div></section>
<section style="display: grid; gap: 14px"><h2 style="margin: 0; font: 700 22px/28px {FD}">Detail switch</h2><div role="group" aria-label="Detail level" style="display: inline-flex; padding: 4px; gap: 4px; background: {SUNK}; border: 1.5px solid {LINE}; border-radius: 10px; width: max-content"><button type="button" aria-pressed="true" style="min-height: 40px; min-width: 96px; border: 0; border-radius: 8px; background: #FFFFFF; box-shadow: inset 0 -3px 0 {SUN}, 0 2px 0 rgba(22,35,58,.16); font: 700 15px/22px {FT}; color: {INK}">Simple</button><button type="button" aria-pressed="false" style="min-height: 40px; min-width: 96px; border: 0; border-radius: 8px; background: transparent; font: 700 15px/22px {FT}; color: {INK2}">Detailed</button><button type="button" aria-pressed="false" style="min-height: 40px; min-width: 96px; border: 0; border-radius: 8px; background: transparent; font: 700 15px/22px {FT}; color: {INK2}">Nerd</button></div></section>
</div>
<div style="display: grid; gap: 36px; align-content: start; padding-top: 72px">
<section style="display: grid; gap: 14px"><h2 style="margin: 0; font: 700 22px/28px {FD}">Car card</h2><div style="max-width: 420px">{carcard("Kia e-Niro 64 kWh","2019–2022, compact SUV","€15,500–19,000","330–440 km","245 km","€95 a month cheaper",True,chip("Checked data","checked","battery-health"))}</div>{SAMPLE}</section>
<section style="display: grid; gap: 14px"><h2 style="margin: 0; font: 700 22px/28px {FD}">Field</h2><div style="display: grid; gap: 6px; max-width: 420px"><label for="town" style="font: 700 17px/24px {FT}">Where do you drive from?</label><input id="town" placeholder="Utrecht" style="min-height: 48px; padding: 10px 14px; border: 1.5px solid {LINES}; border-radius: 6px; font: 400 17px/24px {FT}; color: {INK}"><span style="font: 400 15px/22px {FT}; color: {INK3}">We draw range maps from here. Nothing is stored.</span></div></section>
<section style="display: grid; gap: 14px"><h2 style="margin: 0; font: 700 22px/28px {FD}">Shortlist note</h2><div style="padding: 16px 8px">{note([("Kia e-Niro 64 kWh","fits the dog",False),("MG4 64 kWh","cheapest to run",False),("Nissan Leaf 40 kWh","air-cooled, skip",True)],320)}</div></section>
</div></div>'''
files["Elements.dc.html"]=(page("UI elements",1440,1100,el),1440,1100,"Elements")
# ===== Textures
tx=lambda cls,lab,bg="#FFFFFF": f'<div style="display: grid; gap: 10px"><div class="{cls}" style="height: 160px; border-radius: 18px; border: 1.5px solid {LINE}; background-color: {bg}"></div><span style="font: 700 16px/22px {FT}">{lab}</span></div>'
texture=f'''<div style="padding: 56px 64px; display: grid; gap: 28px">
<div><h1 style="margin: 0; font: 800 40px/46px {FD}">Textures</h1><p style="margin: 6px 0 0; color: {INK2}">Faint holiday-map surfaces for heroes, empty states, Learn headers and illustrations. Never behind tables, forms or prices.</p></div>
<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 24px">
{tx("tex-paper","Paper grain",TINT)}{tx("tex-contour","Contour lines",TINT)}{tx("tex-grid","Map grid")}
{tx("tex-hatch","Land hatching")}{tx("tex-halftone","Halftone sun")}
<div style="display: grid; gap: 10px"><div style="height: 160px; border-radius: 18px; border: 1.5px solid {LINE}; background: {TINT}; background-image: linear-gradient(90deg, transparent 0 33.2%, rgba(22,35,58,.07) 33.3%, rgba(255,255,255,.6) 33.6%, transparent 34% 66.5%, rgba(22,35,58,.07) 66.6%, rgba(255,255,255,.6) 66.9%, transparent 67.3%)"></div><span style="font: 700 16px/22px {FT}">Map folds</span></div></div>
<div style="display: flex; align-items: center; gap: 8px; margin-top: 8px" role="separator"><div style="flex: 1; height: 4px; background-image: radial-gradient(circle, {SKY} 1.6px, transparent 2px); background-size: 12px 4px; background-repeat: repeat-x"></div><div style="width: 14px; height: 14px; border-radius: 50%; background: {SUN}; box-shadow: 0 0 0 2px {INK}"></div></div>
<span style="font: 400 15px/22px {FT}; color: {INK2}">Route divider between big page sections</span></div>'''
files["Textures.dc.html"]=(page("Textures",1440,760,texture),1440,760,"Textures")
# ===== Phone: Home
home=f'''{header_phone()}
<section class="tex-paper" style="background-color: {TINT}; padding: 26px 20px 0; position: relative">
<h1 style="margin: 0; font: 800 36px/40px {FD}">Compare EVs. Make your shortlist.</h1>
<p style="margin: 10px 0 18px; font: 400 17px/26px {FT}; color: {INK2}">Real range, real running costs and real used prices for every electric car.</p>
<div style="display: grid; gap: 6px"><label for="t" style="font: 700 16px/22px {FT}">Where do you drive from?</label><div style="display: flex; gap: 8px"><input id="t" placeholder="Utrecht" style="flex: 1; min-width: 0; min-height: 48px; padding: 10px 12px; border: 1.5px solid {LINES}; border-radius: 6px; font: 400 17px/24px {FT}"><a href="#" style="display: inline-flex; align-items: center; min-height: 48px; padding: 0 16px; border-radius: 10px; background: {ACT}; color: #FFFFFF; font: 700 16px/22px {FT}; text-decoration: none">Show cars</a></div></div>
<div style="position: relative; margin: 22px -20px 0; height: 300px; overflow: hidden">{mapart(390,300)}<div style="position: absolute; left: 40px; top: 26px">{note([("Kia e-Niro 64 kWh","fits the dog",False),("MG4 64 kWh","cheapest to run",False),("Nissan Leaf 40 kWh","air-cooled, skip",True)],280)}</div></div>
</section>
<section style="padding: 22px 20px 200px; display: grid; gap: 12px">
<h2 style="margin: 0; font: 700 22px/28px {FD}">Popular used EVs near you</h2>
{carcard("Kia e-Niro 64 kWh","2019–2022","€15,500–19,000","330–440 km","245 km","€95/month cheaper",True)}
</section>
{tray(["Kia e-Niro","MG4"],2)}{tabbar("Explore",2)}'''
files["PhoneHome.dc.html"]=(page("Phone: home",390,1100,home),390,1100,"Phone: home")
# ===== Phone: Car page
car=f'''{header_phone()}
<div style="padding: 16px 20px 0"><a href="#" style="font: 400 15px/22px {FT}">Explore</a><span style="color: {INK3}"> / Kia / e-Niro</span>
<h1 style="margin: 6px 0 2px; font: 800 30px/34px {FD}">Kia e-Niro 64 kWh</h1><p style="margin: 0; color: {INK2}; font: 400 15px/22px {FT}">2019–2022, compact SUV</p>
<div style="display: flex; gap: 8px; margin: 14px 0 0">{pick(True)}</div></div>
<section style="margin: 18px 20px 0; padding: 18px; border-radius: 18px; background: {SUNT}; display: grid; gap: 6px">
<span style="font: 400 15px/22px {FT}; color: {INK2}">Used in the Netherlands</span><span style="font: 700 30px/34px {FT}">€15,500–19,000</span>
<span style="display: flex; gap: 8px; align-items: center; font: 400 16px/24px {FT}">{icon("monthly-cost",22)}About €95 a month cheaper to run than a petrol Kia Niro</span>
<div style="margin-top: 8px">{btn("See listings on AutoScout24",after="see-listings")}</div></section>
<section style="margin: 22px 20px 0; display: grid; gap: 10px"><h2 style="margin: 0; font: 700 22px/28px {FD}">How far it really goes</h2>
<div style="border-radius: 18px; overflow: hidden; border: 1.5px solid {LINE}">
<svg viewBox="0 0 350 200" width="350" height="200" aria-hidden="true" style="display: block"><rect width="350" height="200" fill="{SEA}"/><path d="M40 0 C 80 50 20 100 60 140 C 90 170 50 190 70 200 L350 200 L350 0 Z" fill="{MEA}" fill-opacity=".55"/><path d="M90 40 C 140 70 150 110 190 120 C 230 130 260 140 300 175" fill="none" stroke="#FFFFFF" stroke-width="8" stroke-linecap="round"/><path d="M90 40 C 120 58 130 80 140 92" fill="none" stroke="{INK}" stroke-width="4" stroke-dasharray="0.1 8" stroke-linecap="round"/><path d="M90 40 C 140 70 150 110 190 120 C 205 124 215 126 225 129" fill="none" stroke="{SKY}" stroke-width="4" stroke-linecap="round"/><circle cx="90" cy="40" r="8" fill="#FFFFFF" stroke="{INK}" stroke-width="2.5"/><circle cx="140" cy="92" r="6" fill="#FFFFFF" stroke="{INK}" stroke-width="2.5"/><circle cx="225" cy="129" r="6" fill="#FFFFFF" stroke="{INK}" stroke-width="2.5"/><rect x="252" y="136" width="16" height="16" rx="4" fill="{SUN}" stroke="{INK}" stroke-width="2"/><circle cx="300" cy="175" r="6" fill="#FFFFFF" stroke="{INK}" stroke-width="2.5"/><text x="104" y="36" font-family="Atkinson Hyperlegible" font-weight="700" font-size="13" fill="{INK}">Nantes</text><text x="152" y="96" font-family="Atkinson Hyperlegible" font-weight="700" font-size="13" fill="{INK}">La Rochelle</text><text x="236" y="122" font-family="Atkinson Hyperlegible" font-weight="700" font-size="13" fill="{INK}">Bordeaux</text><text x="150" y="160" font-family="Patrick Hand" font-size="18" fill="{INK}">Bordeaux: no stop</text></svg>
<div style="display: flex; flex-wrap: wrap; gap: 12px; padding: 12px 14px; font: 400 15px/22px {FT}; border-top: 1.5px solid {LINE}"><span>Summer: 440 km</span><span>Winter: 330 km</span><span style="display: inline-flex; gap: 6px; align-items: center"><span style="width: 12px; height: 12px; border-radius: 3px; background: {SUN}; border: 1.5px solid {INK}"></span>Estimated stop</span></div></div></section>
<section style="margin: 22px 20px 0; display: grid; gap: 12px"><h2 style="margin: 0; font: 700 22px/28px {FD}">Charging</h2>
<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px">
<div style="padding: 14px; border-radius: 14px; border: 1.5px solid {LINE}">{icon("fast-charge",24)}<b style="display: block; font: 700 22px/28px {FT}; margin-top: 6px">245 km</b>{label("Added in 20 min","DC fast charging")}</div>
<div style="padding: 14px; border-radius: 14px; border: 1.5px solid {LINE}">{icon("voltage-400",24)}<b style="display: block; font: 700 22px/28px {FT}; margin-top: 6px">42 min</b>{label("From 10 to 80%","400 V, 77 kW peak")}</div></div>
<div style="display: flex; gap: 6px; flex-wrap: wrap">{chip("Liquid-cooled battery","checked","battery-health")}{chip("NMC chemistry","plain","chemistry")}</div>{SAMPLE}</section>
{tabbar("Explore",3)}'''
files["PhoneCar.dc.html"]=(page("Phone: car page",390,1260,car),390,1260,"Phone: car page")
# ===== Phone: Compare
rows=[("Used price","€15.5–19k","€17–21k"),("Monthly vs petrol","€95 less","€105 less"),("Winter range","330 km","300 km"),("Added in 20 min","245 km","280 km"),("Boot","451 L","363 L"),("Battery","Liquid-cooled","Liquid-cooled")]
best=[0,1,0,1,0,None]  # lower price, more saving, more range, more km in 20 min, bigger boot
tr=""
for (lab,a,b),bi in zip(rows,best):
    ca=f'background: {SUNT}; font-weight: 700' if bi==0 else ''; cb=f'background: {SUNT}; font-weight: 700' if bi==1 else ''
    tag=lambda on: f'<span style="display: block; font: 700 12px/16px {FT}; color: {WARN}">Best</span>' if on else ''
    tr+=f'<tr><th scope="row" style="text-align: left; padding: 12px 10px; font: 700 15px/20px {FT}; border-bottom: 1px solid {LINE}; background: {SUNK}">{lab}</th><td style="padding: 12px 10px; border-bottom: 1px solid {LINE}; {ca}">{a}{tag(bi==0)}</td><td style="padding: 12px 10px; border-bottom: 1px solid {LINE}; {cb}">{b}{tag(bi==1)}</td></tr>'
cmp=f'''{header_phone()}
<div style="padding: 18px 20px 0"><h1 style="margin: 0; font: 800 30px/34px {FD}">Compare 2 cars</h1><p style="margin: 4px 0 0; color: {INK2}; font: 400 15px/22px {FT}">From your shortlist. Swipe for the next pair.</p></div>
<div style="margin: 16px 20px 0; border: 1.5px solid {LINE}; border-radius: 18px; overflow: hidden">
<table style="width: 100%; border-collapse: collapse; font: 400 16px/22px {FT}; color: {INK}">
<thead><tr><th style="background: {SUNK}"></th><th scope="col" style="text-align: left; padding: 12px 10px; font: 800 17px/22px {FD}; border-bottom: 1.5px solid {LINES}">Kia e-Niro 64</th><th scope="col" style="text-align: left; padding: 12px 10px; font: 800 17px/22px {FD}; border-bottom: 1.5px solid {LINES}">MG4 64 kWh</th></tr></thead>
<tbody>{tr}</tbody></table></div>
<div style="margin: 14px 20px 0">{SAMPLE}</div>
<div style="margin: 18px 20px 0; display: grid; gap: 10px">{btn("See listings for both",after="see-listings")}{btn("Share this comparison","secondary","share")}</div>
{tabbar("Compare",2)}'''
files["PhoneCompare.dc.html"]=(page("Phone: compare",390,900,cmp),390,900,"Phone: compare")
# ===== Phone: Shortlist
sl=f'''{header_phone()}
<section class="tex-paper" style="background-color: {TINT}; padding: 30px 20px 26px; display: grid; justify-items: center">
{note([("Kia e-Niro 64 kWh","fits the dog, 330 km in winter",False),("MG4 64 kWh","cheapest to run",False),("Skoda Enyaq 80","big boot, tows a trailer",False),("Nissan Leaf 40 kWh","air-cooled, skip",True)],330)}</section>
<div style="padding: 18px 20px 0; display: grid; gap: 10px">{btn("Compare 3 cars")}{btn("Share your shortlist","secondary","share")}</div>
<section style="padding: 20px 20px 120px; display: grid; gap: 12px"><h2 style="margin: 0; font: 700 22px/28px {FD}">In your order</h2>
{carcard("1. Kia e-Niro 64 kWh","Your note: fits the dog","€15,500–19,000","330–440 km","245 km","€95/month cheaper",True)}
</section>{tabbar("Shortlist",3)}'''
files["PhoneShortlist.dc.html"]=(page("Phone: shortlist",390,1100,sl),390,1100,"Phone: shortlist")
# ===== Desktop: Explore
cars=[("Renault Zoe R110","2019–2022","€9,000–12,500","€22,000 new","230–330 km","95 km",False),("Kia e-Niro 64 kWh","2019–2022","€15,500–19,000","€38,000 new","330–440 km","245 km",True),("MG4 64 kWh","2022–2025","€17,000–21,000","€33,000 new","300–420 km","280 km",True),("Hyundai Ioniq 5 77 kWh","2022–2024","€28,000–34,000","€47,000 new","340–460 km","410 km",False),("Skoda Enyaq 80","2021–2024","€26,000–31,000","€45,000 new","320–440 km","300 km",True)]
trs="".join(f'<tr><td style="padding: 14px 16px; border-bottom: 1px solid {LINE}"><b style="font: 700 17px/22px {FT}">{n}</b><span style="display: block; font: 400 15px/22px {FT}; color: {INK2}">{y}</span></td><td style="padding: 14px 16px; border-bottom: 1px solid {LINE}; text-align: right; font-weight: 700">{u}</td><td style="padding: 14px 16px; border-bottom: 1px solid {LINE}; text-align: right; color: {INK2}">{nw}</td><td style="padding: 14px 16px; border-bottom: 1px solid {LINE}; text-align: right; font-weight: 700">{r}</td><td style="padding: 14px 16px; border-bottom: 1px solid {LINE}; text-align: right; font-weight: 700">{c}</td><td style="padding: 8px 16px; border-bottom: 1px solid {LINE}; text-align: right">{pick(on,False)}</td></tr>' for n,y,u,nw,r,c,on in cars)
th=lambda p,t,al="right": f'<th scope="col" style="text-align: {al}; vertical-align: bottom; padding: 12px 16px; background: {SUNK}; border-bottom: 1.5px solid {LINES}">{label(p,t)}</th>'
desk=f'''<header style="display: flex; align-items: center; gap: 28px; padding: 16px 40px; border-bottom: 1.5px solid {LINE}">
{logo(32,small=True)}<nav aria-label="Main" style="display: flex; gap: 6px"><a href="#" aria-current="page" style="padding: 12px 12px; font: 700 17px/24px {FT}; color: {INK}; text-decoration: none; box-shadow: inset 0 -3px 0 {SKY}">Explore</a><a href="#" style="padding: 12px; font: 700 17px/24px {FT}; color: {INK}; text-decoration: none">Rankings</a><a href="#" style="padding: 12px; font: 700 17px/24px {FT}; color: {INK}; text-decoration: none">Learn</a><a href="#" style="padding: 12px; font: 700 17px/24px {FT}; color: {INK}; text-decoration: none">Charging</a></nav>
<div style="margin-left: auto; display: flex; gap: 12px; align-items: center"><div role="group" aria-label="Detail level" style="display: inline-flex; padding: 4px; gap: 4px; background: {SUNK}; border: 1.5px solid {LINE}; border-radius: 10px"><button type="button" aria-pressed="true" style="min-height: 38px; padding: 0 14px; border: 0; border-radius: 8px; background: #FFFFFF; box-shadow: inset 0 -3px 0 {SUN}; font: 700 15px/22px {FT}; color: {INK}">Simple</button><button type="button" aria-pressed="false" style="min-height: 38px; padding: 0 14px; border: 0; background: transparent; font: 700 15px/22px {FT}; color: {INK2}">Detailed</button><button type="button" aria-pressed="false" style="min-height: 38px; padding: 0 14px; border: 0; background: transparent; font: 700 15px/22px {FT}; color: {INK2}">Nerd</button></div>
<a href="#" style="display: inline-flex; align-items: center; gap: 8px; min-height: 48px; padding: 0 16px; border-radius: 10px; border: 2px solid {LINES}; color: {INK}; font: 700 17px/24px {FT}; text-decoration: none">{tickbox(24)}Shortlist<span style="display: inline-grid; place-items: center; min-width: 24px; height: 24px; border-radius: 999px; background: {SUN}; border: 2px solid {INK}; font: 700 13px/1 {FT}">3</span></a></div></header>
<section class="tex-paper" style="background-color: {TINT}; padding: 36px 40px 32px; display: flex; gap: 40px; align-items: flex-end">
<div><h1 style="margin: 0; font: 800 44px/48px {FD}">Every electric car, compared</h1><p style="margin: 8px 0 0; color: {INK2}; font: 400 19px/30px {FT}">Used and new prices side by side. Tick the ones that fit.</p></div>
<div style="margin-left: auto; display: flex; gap: 8px; flex-wrap: wrap">{chip("Budget up to €25,000","plain","price")}{chip("Winter range 300 km+","plain","winter")}{chip("8 filters, 214 cars","plain","filter")}</div></section>
<div style="padding: 24px 40px"><div style="border: 1.5px solid {LINE}; border-radius: 18px; overflow: hidden"><table style="width: 100%; border-collapse: collapse; font: 400 16px/22px {FT}; color: {INK}"><thead><tr>{th("Car","generation","left")}{th("Used price ↑","NL market range")}{th("New price","when new")}{th("Real range","winter to summer")}{th("Fast charge","km in 20 min")}{th("Shortlist","tick to keep")}</tr></thead><tbody>{trs}</tbody></table></div><div style="margin-top: 10px">{SAMPLE}</div></div>
<div style="position: absolute; right: 40px; bottom: 28px; display: flex; align-items: center; gap: 10px; padding: 12px 14px; background: #FFFFFF; border: 1.5px solid {INK}; border-radius: 18px; box-shadow: 0 4px 0 rgba(22,35,58,.18), 0 10px 24px rgba(22,35,58,.10)">{tickbox(26)}<span style="padding: 6px 10px; border-radius: 6px; background: {TINT}; font: 700 14px/18px {FT}">Kia e-Niro</span><span style="padding: 6px 10px; border-radius: 6px; background: {TINT}; font: 700 14px/18px {FT}">MG4</span><span style="padding: 6px 10px; border-radius: 6px; background: {TINT}; font: 700 14px/18px {FT}">Skoda Enyaq</span><a href="#" style="display: inline-flex; align-items: center; min-height: 44px; padding: 0 16px; border-radius: 10px; background: {ACT}; color: #FFFFFF; font: 700 15px/20px {FT}; text-decoration: none">Compare 3 cars</a></div>'''
files["DesktopExplore.dc.html"]=(page("Desktop: Explore",1440,900,desk),1440,900,"Desktop: Explore")
# write files
for k,(src,w,h,t) in files.items(): open(f"{B}/{k}","w").write(src)
# layout
L={}; order=[]
row1=["Main.dc.html","Icons.dc.html"]; row2=["Elements.dc.html","Textures.dc.html"]; row3=["PhoneHome.dc.html","PhoneCar.dc.html","PhoneCompare.dc.html","PhoneShortlist.dc.html"]; row4=["DesktopExplore.dc.html"]
y=0
for row in (row1,row2,row3,row4):
    x=0; mh=0
    for f in row:
        _,w,h,t=files[f]; L[f]={"x":x,"y":y,"w":w,"h":h,"title":t}; x+=w+80; mh=max(mh,h); order.append(f)
    y+=mh+340
notes={"brand":{"x":0,"y":-300,"text":"Brand and foundations","kind":"title1","maxW":2960},
       "ui":{"x":0,"y":L["Elements.dc.html"]["y"]-300,"text":"Elements and textures","kind":"title1","maxW":2960},
       "phone":{"x":0,"y":L["PhoneHome.dc.html"]["y"]-300,"text":"Phone mockups","kind":"title1","maxW":1800},
       "desk":{"x":0,"y":L["DesktopExplore.dc.html"]["y"]-300,"text":"Desktop","kind":"title1","maxW":1440},
       "link":{"x":3040,"y":0,"w":420,"size":"m","fill":"blue","text":"This board is the visual companion of the EV Shortlist design system: https://claude.ai/artifact/EiqvMW5NcFgxFq6c5YHuPP\n\nTokens, components and rules live there (and in the repo under docs/design/). When either changes, the other follows."}}
canvas={"v":3,"createdOnFiles":{"v":1,"at":"2026-11-15T10:00:00Z"},"title":"EV Shortlist design board","launch":{"view":"canvas"},"pages":[],"boards":L,"order":order,"notes":notes,
 "designSystems":[{"title":"EV Shortlist","namespace":"evshortlist","artifact":"https://claude.ai/artifact/EiqvMW5NcFgxFq6c5YHuPP","version":None,"copiedAt":"2026-11-15T10:00:00Z"}]}
json.dump(canvas,open(f"{B}/canvas.json","w"),indent=1)
import os; os.makedirs(f"{B}/ds/evshortlist",exist_ok=True)
import shutil; shutil.copy("/home/claude/ds/project/tokens.json",f"{B}/ds/evshortlist/tokens.json")
print(order)
