import sys, os; sys.path.insert(0,'/home/claude/gen')
from bitterlogo import dE, wE, dS, wS, CAP, K, STEM, tick
O="/home/claude/ds/project/assets/Logo"
for f in os.listdir(O):
    if f.endswith('.svg'): os.remove(os.path.join(O,f))
TH={"light":dict(ink="#16233A",ev="#3B78AE",sun="#FFD166",ring="#16233A",tile="#16233A",tev="#93C1EA",tring="#EEF3F9"),
    "dark":dict(ink="#EEF3F9",ev="#93C1EA",sun="#FFD166",ring="#EEF3F9",tile="#24365A",tev="#93C1EA",tring="#EEF3F9"),
    "var":dict(ink="var(--ink)",ev="var(--sky)",sun="var(--sunflower)",ring="var(--ink)")}
TX=wE-62*K+2*K; GAP=TX+160*K
def lockup(c,small=False):
    g=f'<path d="{dE}" fill="{c["ev"]}"/><g transform="translate({TX:.1f} 0) scale({K:.3f})">{tick(c["ev"],c["ring"],c["sun"],STEM,small=small)}</g>'
    g+=f'<path transform="translate({GAP:.1f} 0)" d="{dS}" fill="{c["ink"]}"/>'
    return g,f"-3 -{CAP+28:.0f} {GAP+wS+7:.0f} {CAP+38:.0f}"
def icon(c,small=False):
    # content box of E + tick + sun in 100-unit space; keep generous padding inside the tile
    x0=3.0; x1=TX+(127+9.5+1.6)*K; y0=-(80+9.5+1.6)*K; y1=(-6+STEM*0.52)*K
    w=x1-x0; h=y1-y0
    m=13 if not small else 10          # padding in tile units (tile is 60 wide): text never near the edge
    avail=60-2*m; s=min(avail/w,avail/h)
    ox=2+m+(avail-w*s)/2-x0*s; oy=2+m+(avail-h*s)/2-y0*s
    g=f'<rect x="2" y="2" width="60" height="60" rx="14" fill="{c["tile"]}"/>'
    g+=f'<g transform="translate({ox:.2f} {oy:.2f}) scale({s:.4f})"><path d="{dE}" fill="{c["tev"]}"/><g transform="translate({TX:.1f} 0) scale({K:.3f})">{tick(c["tev"],c["tring"],c["sun"],STEM,small=small)}</g></g>'
    return g
def svg(vb,b,w,h): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{w}" height="{h}" role="img"><title>EV Shortlist</title>{b}</svg>\n'
for th in ("light","dark"):
    c=TH[th]
    for sm,suf in ((False,""),(True,"-small")):
        b,vb=lockup(c,sm); vw=float(vb.split()[2]); vh=float(vb.split()[3])
        open(f"{O}/lockup{suf}-{th}.svg","w").write(svg(vb,b,round(vw*48/vh),48))
    for sm,suf in ((False,""),(True,"-small")):
        open(f"{O}/icon{suf}-{th}.svg","w").write(svg("0 0 64 64",icon(c,sm),512 if not sm else 32,512 if not sm else 32))
c=TH["var"]
for sm,suf in ((False,""),(True,"-small")):
    b,vb=lockup(c,sm); open(f"/home/claude/logo/v5-lockup{suf}.svg","w").write(f'<svg class="evs-lockup" viewBox="{vb}" role="img" aria-label="EV Shortlist">{b}</svg>')
ci=dict(tile="var(--ink)",tev="var(--sky)",tring="var(--paper)",sun="var(--sunflower)")
for sm,suf in ((False,""),(True,"-small")):
    open(f"/home/claude/logo/v5-icon{suf}.svg","w").write(f'<svg class="evs-icon" viewBox="0 0 64 64" aria-hidden="true">{icon(dict(ci),sm)}</svg>')
print(sorted(os.listdir(O)))
