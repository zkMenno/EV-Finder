import sys; sys.path.insert(0,'/home/claude/gen')
from glyphs import glyphs
G,W=glyphs('EV Shortlist')
def gp(names_skip,ink):
    return "".join(f'<path d="{d}" fill="{ink}"/>' for i,(n,x,a,d) in enumerate(G) if i not in names_skip)
def tick(style,ink,tom,sun,dash):
    d="M68 -40 L87 -8 L122 -74"
    if style=="ink":
        return f'<path d="{d}" fill="none" stroke="{ink}" stroke-width="14.5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="122" cy="-76" r="10.5" fill="{sun}" stroke="{ink}" stroke-width="3.2"/>'
    return (f'<path d="{d}" fill="none" stroke="{ink}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{tom}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M72 -33 L87 -8 L117 -64" fill="none" stroke="{dash}" stroke-width="1.6" stroke-dasharray="4 4" stroke-linejoin="round"/>'
            f'<circle cx="122" cy="-76" r="10.5" fill="{sun}" stroke="{ink}" stroke-width="3.2"/>')
SX=152.5
SP="M50 -59 C 45 -66 38 -64.5 30 -64.5 C 18 -64.5 11 -58.5 11 -50 C 11 -40 20 -38 30 -35.5 C 42 -32.5 50 -28 50 -18.5 C 50 -9.5 42 -6 30 -6 C 20 -6 12.5 -9 9 -15"
def sroad(style,ink,tom,sun,dash,paper):
    t=f'transform="translate({SX} 0)"'
    if style=="ink":
        s=f'<path {t} d="{SP}" fill="none" stroke="{ink}" stroke-width="14" stroke-linecap="round"/>'
        s+=f'<path {t} d="{SP}" fill="none" stroke="{dash}" stroke-width="1.6" stroke-dasharray="3.6 3.6" stroke-dashoffset="-3"/>'
    else:
        s=f'<path {t} d="{SP}" fill="none" stroke="{ink}" stroke-width="15.5" stroke-linecap="round"/>'
        s+=f'<path {t} d="{SP}" fill="none" stroke="{tom}" stroke-width="10" stroke-linecap="round"/>'
        s+=f'<path {t} d="{SP}" fill="none" stroke="{dash}" stroke-width="1.5" stroke-dasharray="3.6 3.6" stroke-dashoffset="-3"/>'
    s+=f'<circle cx="{SX+50.5}" cy="-60" r="6.5" fill="{paper}" stroke="{ink}" stroke-width="3"/>'
    s+=f'<circle cx="{SX+8.5}" cy="-14" r="8.5" fill="{sun}" stroke="{ink}" stroke-width="3"/>'
    return s
TH={"light":dict(ink="#22335A",tom="#E8573F",sun="#F7C948",dash="#FFFFFF",paper="#FFFFFF",bg="#FFFFFF"),
    "dark":dict(ink="#EEF2F7",tom="#FF8A6B",sun="#F7C948",dash="#141C30",paper="#141C30",bg="#141C30")}
def v_logo(style,c): return gp({1},c["ink"])+tick(style,c["ink"],c["tom"],c["sun"],c["dash"])
def s_logo(style,c): return gp({3},c["ink"])+sroad(style,c["ink"],c["tom"],c["sun"],c["dash"],c["paper"])
VB=f"-4 -92 {W+10} 100"
if __name__=="__main__":
    rows=[]
    for lab,f,st in [("1a V tick, ink",v_logo,"ink"),("1b V tick, tomato road",v_logo,"tom"),("2a S road, ink",s_logo,"ink"),("2b S road, tomato",s_logo,"tom")]:
        cells="".join(f'<div style="background:{TH[t]["bg"]};padding:18px 22px;display:flex;gap:26px;align-items:end"><svg height="70" viewBox="{VB}">{f(st,TH[t])}</svg><svg height="26" viewBox="{VB}">{f(st,TH[t])}</svg></div>' for t in ("light","dark"))
        rows.append(f'<div style="font:13px sans-serif;color:#667;padding:8px 22px 2px">{lab}</div><div style="display:grid;grid-template-columns:1fr 1fr">{cells}</div>')
    open('/home/claude/logo/combo.html','w').write('<!doctype html><body style="margin:0;background:#fff">'+"".join(rows)+'</body>')
