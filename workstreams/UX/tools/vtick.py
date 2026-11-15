import sys, math; sys.path.insert(0,'/home/claude/gen')
from glyphs import glyphs
GE,_=glyphs('E'); E=GE[0][3]
INK="#22335A"; TOM="#E8573F"; SUN="#F7C948"; W="#FFFFFF"
# V slot after E: x 62..127, baseline 0, cap -70
A=(69,-44); B=(87,-6); C=(124,-74)   # left top, valley, right top
def poly_taper(p0,p1,w0,w1):
    dx,dy=p1[0]-p0[0],p1[1]-p0[1]; L=math.hypot(dx,dy); nx,ny=-dy/L,dx/L
    return [(p0[0]+nx*w0/2,p0[1]+ny*w0/2),(p1[0]+nx*w1/2,p1[1]+ny*w1/2),(p1[0]-nx*w1/2,p1[1]-ny*w1/2),(p0[0]-nx*w0/2,p0[1]-ny*w0/2)]
def P(pts): return "M"+" L".join(f"{x:.1f} {y:.1f}" for x,y in pts)+"Z"
def v1(m): # solid tick + disc
    c=INK if not m else INK
    return f'<path d="M{A[0]} {A[1]} L{B[0]} {B[1]} L{C[0]} {C[1]}" fill="none" stroke="{c}" stroke-width="15" stroke-linecap="round" stroke-linejoin="round"/><circle cx="{C[0]+1}" cy="{C[1]-3}" r="10" fill="{SUN if not m else INK}" stroke="{INK}" stroke-width="3"/>'
def v2(m):
    d=f"M{A[0]} {A[1]} L{B[0]} {B[1]} L{C[0]} {C[1]}"
    if m: return v1(m)
    return f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/><path d="{d}" fill="none" stroke="{TOM}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/><path d="M73 -36 L87 -6 L119 -65" fill="none" stroke="{W}" stroke-width="1.6" stroke-dasharray="4 4"/><circle cx="125" cy="-77" r="10" fill="{SUN}" stroke="{INK}" stroke-width="3"/>'
def taper(m,fill,edge,dash=True,sun=True):
    short=poly_taper(A,B,15,15); long=poly_taper(B,C,15,4.5)
    g=f'<path d="{P(short)}" fill="{fill}" stroke="{edge}" stroke-width="{2.4 if edge!="none" else 0}" stroke-linejoin="round"/>'
    g+=f'<path d="{P(long)}" fill="{fill}" stroke="{edge}" stroke-width="{2.4 if edge!="none" else 0}" stroke-linejoin="round"/>'
    g+=f'<circle cx="{B[0]}" cy="{B[1]}" r="7.5" fill="{fill}"/>'
    g+=f'<circle cx="{A[0]}" cy="{A[1]}" r="7.5" fill="{fill}"/>'
    if dash and not m:
        # perspective dashes: shrinking along the long arm
        g+=f'<path d="M{A[0]+3} {A[1]+6} L{B[0]-1} {B[1]-2}" stroke="{W}" stroke-width="1.6" stroke-dasharray="4 4"/>'
        for t0,t1 in [(0.08,0.2),(0.3,0.39),(0.48,0.55),(0.62,0.67),(0.73,0.76)]:
            x0=B[0]+(C[0]-B[0])*t0; y0=B[1]+(C[1]-B[1])*t0; x1=B[0]+(C[0]-B[0])*t1; y1=B[1]+(C[1]-B[1])*t1
            g+=f'<path d="M{x0:.1f} {y0:.1f} L{x1:.1f} {y1:.1f}" stroke="{W}" stroke-width="{1.7*(1-t0*0.8):.2f}" stroke-linecap="round"/>'
    if sun: g+=f'<circle cx="{C[0]+3}" cy="{C[1]-6}" r="9" fill="{SUN if not m else INK}" stroke="{INK}" stroke-width="2.6"/>'
    return g
def v3(m): return taper(m,INK,"none")
def v4(m): return taper(m,TOM if not m else INK,"none")
def v4b(m): return taper(m,TOM if not m else INK,INK if not m else "none")
def v5(m): # arrow terminal
    d=f"M{A[0]} {A[1]} L{B[0]} {B[1]} L{C[0]-4} {C[1]+8}"
    head=f"M{C[0]+5} {C[1]-6} L{C[0]-14} {C[1]+0} L{C[0]+1} {C[1]+14}Z"
    col=INK if m else TOM
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="15" stroke-linecap="round" stroke-linejoin="round"/><path d="{head}" fill="{col}" stroke="{col}" stroke-width="3" stroke-linejoin="round"/>'
def v6(m): # hand tick, curved long arm
    d=f"M{A[0]} {A[1]+2} Q 78 -18 {B[0]} {B[1]} Q 100 -48 {C[0]} {C[1]}"
    return f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="15" stroke-linecap="round" stroke-linejoin="round"/><circle cx="{C[0]+1}" cy="{C[1]-3}" r="10" fill="{SUN if not m else INK}" stroke="{INK}" stroke-width="3"/>'
def v7(m): # start pin + route
    d=f"M{A[0]+3} {A[1]+10} L{B[0]} {B[1]} L{C[0]} {C[1]}"
    return f'<path d="{d}" fill="none" stroke="{TOM if not m else INK}" stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/><circle cx="{A[0]}" cy="{A[1]}" r="8" fill="{W}" stroke="{INK}" stroke-width="3.5"/><circle cx="{C[0]+1}" cy="{C[1]-3}" r="10" fill="{SUN if not m else INK}" stroke="{INK}" stroke-width="3"/>'
VS=[("1 Solid tick + sun",v1),("2 Road tick (current)",v2),("3 Perspective tick, ink",v3),("4 Perspective tick, tomato",v4),("5 Perspective tick, tomato + ink edge",v4b),("6 Road-sign arrow",v5),("7 Hand-drawn tick",v6),("8 Start pin to sun",v7)]
def ev(f,m): return f'<path d="{E}" fill="{INK}"/>'+f(m)
if __name__=="__main__":
    cells=[]
    for lab,f in VS:
        vb="-4 -92 142 100"
        cells.append(f'<div style="border:1px solid #e3e7ee;border-radius:10px;padding:12px 14px"><div style="font:13px sans-serif;color:#556;margin-bottom:6px">{lab}</div><div style="display:flex;gap:16px;align-items:end"><svg height="110" viewBox="{vb}">{ev(f,False)}</svg><svg height="24" viewBox="{vb}">{ev(f,False)}</svg><svg height="16" viewBox="{vb}">{ev(f,False)}</svg><svg height="48" viewBox="{vb}">{ev(f,True)}</svg></div></div>')
    open('/home/claude/logo/vtick.html','w').write('<!doctype html><body style="margin:0;padding:16px;background:#fff;display:grid;grid-template-columns:1fr 1fr;gap:12px">'+"".join(cells)+'</body>')
