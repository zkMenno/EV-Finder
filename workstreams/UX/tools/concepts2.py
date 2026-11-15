import sys, glob, math; sys.path.insert(0,'/home/claude/gen')
from fontaudit import ttf, shape
from vtick import P
from vtick2 import curved_taper, qpt
INK="#22335A"; TOM="#E8573F"; SUN="#F7C948"; SEA="#BFE1EE"; MEA="#7BB661"; W="#FFFFFF"
def fp(pkg,wt="400"): return ttf(glob.glob(f"/home/claude/fonts2/fontsource-{pkg}-*/files/{pkg}-latin-{wt}-normal.woff2")[0])
def tick(col=TOM,stem=15,ring=INK,sun=SUN,tip=4.2):
    A=(69,-42); B=(87,-6); C=(124,-74)
    sh=curved_taper(A,(77,-20),B,stem*0.95,stem*1.05); lo=curved_taper(B,(103,-44),C,stem*1.05,tip)
    return (f'<path d="{P(sh)}" fill="{col}"/><path d="{P(lo)}" fill="{col}"/><circle cx="{A[0]}" cy="{A[1]}" r="{stem*0.47}" fill="{col}"/><circle cx="{B[0]}" cy="{B[1]}" r="{stem*0.52}" fill="{col}"/>'
            f'<circle cx="{C[0]+3}" cy="{C[1]-6}" r="9" fill="{sun}" stroke="{ring}" stroke-width="2.6"/>')
# C1 retro decal: sign E+tick, script Shortlist with road swash
def c1():
    dE,wE,capE=shape(fp("lilita-one"),"E",100)
    dS,wS,capS=shape(fp("yellowtail"),"Shortlist",150)
    g=f'<rect x="0" y="-92" width="140" height="96" rx="16" fill="{TOM}"/><rect x="7" y="-85" width="126" height="82" rx="10" fill="none" stroke="{W}" stroke-width="3.5"/>'
    g+=f'<path transform="translate(18 -14) scale(0.9)" d="{dE}" fill="{W}"/>'
    g+=f'<g transform="translate(14 -12) scale(0.86)">{tick(W,16,INK,SUN)}</g>'
    g+=f'<g transform="translate(150 -4)"><path d="{dS}" fill="{INK}"/></g>'
    sw=f"M178 14 C 300 34 420 30 520 2 C 560 -10 590 -30 612 -58"
    g+=f'<path d="{sw}" fill="none" stroke="{INK}" stroke-width="11" stroke-linecap="round"/><path d="M196 18 C 300 34 420 30 520 2 C 556 -9 582 -26 602 -48" fill="none" stroke="{W}" stroke-width="1.6" stroke-dasharray="5 5"/>'
    g+=f'<circle cx="614" cy="-62" r="10" fill="{SUN}" stroke="{INK}" stroke-width="3"/>'
    return g,"-6 -110 640 140","Retro decal: E-tick sign + road-trip script with a road swash"
# C3 70s travel: Shrikhand with sunflower offset shadow, EV tomato + tick
def c3():
    dE,wE,_=shape(fp("shrikhand"),"E",110); dS,wS,_=shape(fp("shrikhand"),"Shortlist",110)
    sh=lambda d,dx: f'<path transform="translate({dx+4} 5)" d="{d}" fill="{SUN}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/><path transform="translate({dx} 0)" d="{d}" fill="{INK}"/>'
    g=f'<path transform="translate(4 5)" d="{dE}" fill="{SUN}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/><path d="{dE}" fill="{TOM}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
    g+=f'<g transform="translate({wE-58} -2) scale(1.1)">{tick(TOM,17,INK,SUN)}</g>'
    g+=sh(dS,wE+92)
    return g,f"-6 -112 {wE+92+wS+14:.0f} 130","70s travel poster: heavy retro italic with a sunflower drop shadow"
# C4 sticker emblem
def c4():
    dT,wT,_=shape(fp("lilita-one"),"EV Shortlist",58)
    g=f'<rect x="0" y="-150" width="300" height="150" rx="34" fill="{SEA}" stroke="{INK}" stroke-width="5"/>'
    g+=f'<clipPath id="cl"><rect x="2.5" y="-147.5" width="295" height="145" rx="31.5"/></clipPath><g clip-path="url(#cl)">'
    g+=f'<circle cx="220" cy="-108" r="22" fill="{SUN}" stroke="{INK}" stroke-width="4"/>'
    g+=f'<path d="M-10 -60 C 60 -95 120 -70 170 -82 C 220 -95 260 -78 310 -88 L310 10 L-10 10Z" fill="{MEA}" stroke="{INK}" stroke-width="4"/>'
    g+=f'<path d="M150 0 C 130 -30 190 -40 175 -62 C 168 -72 190 -78 200 -82" fill="none" stroke="{W}" stroke-width="10" stroke-linecap="round"/><path d="M150 0 C 130 -30 190 -40 175 -62 C 168 -72 190 -78 200 -82" fill="none" stroke="{TOM}" stroke-width="3" stroke-dasharray="4 5"/>'
    g+=f'<rect x="-10" y="-46" width="320" height="56" fill="{INK}"/></g>'
    g+=f'<path transform="translate({150-wT/2:.1f} -14)" d="{dT}" fill="{W}"/>'
    return g,"-8 -160 316 168","Sticker emblem: a road-trip decal with sun, hills and road"
# C5 bouncy friendly: Titan One letters on a bouncing baseline + tick
def c5():
    from fontaudit import shape as sh
    f=fp("titan-one"); dE,wE,_=sh(f,"E",100)
    g=f'<path d="{dE}" fill="{INK}" transform="rotate(-4 30 -35)"/>'
    g+=f'<g transform="translate({wE-60} 0)">{tick(TOM,16,INK,SUN)}</g>'
    x=wE+92; rot=[-3,2,-2,3,-2,2,-3,2,-1]; dy=[0,-4,2,-3,1,-4,2,-2,0]
    for i,ch in enumerate("Shortlist"):
        d,w,_=sh(f,ch,100)
        g+=f'<path transform="translate({x:.1f} {dy[i]}) rotate({rot[i]} {w/2:.1f} -35)" d="{d}" fill="{INK}"/>'; x+=w-2
    return g,f"-6 -100 {x+10:.0f} 112","Bouncy holiday-map lettering: chunky letters on a hand-set baseline"
# C6 marker list: Sedgwick Ave Display + brush tick + underline
def c6():
    f=fp("sedgwick-ave-display"); dE,wE,_=shape(f,"E",120); dS,wS,_=shape(f,"Shortlist",120)
    g=f'<path d="{dE}" fill="{INK}"/><g transform="translate({wE-62} 0) scale(1.05)">{tick(TOM,15,INK,SUN)}</g>'
    g+=f'<g transform="translate({wE+90} 0)"><path d="{dS}" fill="{INK}"/></g>'
    g+=f'<path d="M{wE+92} 18 C {wE+200} 8 {wE+320} 12 {wE+90+wS} 6" fill="none" stroke="{TOM}" stroke-width="7" stroke-linecap="round"/>'
    return g,f"-6 -110 {wE+90+wS+16:.0f} 140","Marker list: written like your own shortlist, underlined"
# C7 Righteous deco road
def c7():
    f=fp("righteous"); dE,wE,_=shape(f,"E",110); dS,wS,_=shape(f,"Shortlist",110)
    g=f'<path d="{dE}" fill="{INK}"/><g transform="translate({wE-60} 2) scale(1.08)">{tick(TOM,14,INK,SUN)}</g><g transform="translate({wE+92} 0)"><path d="{dS}" fill="{INK}"/></g>'
    return g,f"-6 -100 {wE+92+wS+12:.0f} 112","Art-deco roadside: retro motel-sign curves"
CS=[c1,c3,c4,c5,c6,c7]
if __name__=="__main__":
    cells=[]
    for f in CS:
        g,vb,lab=f()
        cells.append(f'<div style="border:1px solid #e3e7ee;border-radius:10px;padding:12px 16px"><div style="font:13px sans-serif;color:#556;margin-bottom:8px">{lab}</div><div style="display:flex;gap:22px;align-items:end"><svg height="88" viewBox="{vb}">{g}</svg><svg height="30" viewBox="{vb}">{g}</svg></div></div>')
    open('/home/claude/fonts2/concepts2.html','w').write('<!doctype html><body style="margin:0;padding:14px;background:#fff;display:grid;grid-template-columns:1fr;gap:12px">'+"".join(cells)+'</body>')
