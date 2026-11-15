import sys, math; sys.path.insert(0,'/home/claude/gen')
from glyphs import glyphs
from vtick import poly_taper, P, A, B, C, E, INK, TOM, SUN, W
GS,WS=glyphs('Shortlist')
def qpt(p0,p1,p2,t): return ((1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t*t*p2[0],(1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t*t*p2[1])
def curved_taper(p0,ctrl,p2,w0,w1,n=28):
    L=[];R=[]
    for i in range(n+1):
        t=i/n; x,y=qpt(p0,ctrl,p2,t); a=qpt(p0,ctrl,p2,min(1,t+0.01)); b=qpt(p0,ctrl,p2,max(0,t-0.01))
        dx,dy=a[0]-b[0],a[1]-b[1]; l=math.hypot(dx,dy) or 1; nx,ny=-dy/l,dx/l; w=w0+(w1-w0)*t
        L.append((x+nx*w/2,y+ny*w/2)); R.append((x-nx*w/2,y-ny*w/2))
    return L+R[::-1]
def tick_straight(col,sun=True,m=False):
    g=f'<path d="{P(poly_taper(A,B,15,15))}" fill="{col}"/><path d="{P(poly_taper(B,C,15,4.5))}" fill="{col}"/>'
    g+=f'<circle cx="{B[0]}" cy="{B[1]}" r="7.5" fill="{col}"/><circle cx="{A[0]}" cy="{A[1]}" r="7.5" fill="{col}"/>'
    if sun: g+=f'<circle cx="{C[0]+3}" cy="{C[1]-6}" r="9" fill="{INK if m else SUN}" stroke="{INK}" stroke-width="2.6"/>'
    return g
def tick_hand(col,m=False):
    d=f"M{A[0]} {A[1]+2} Q 78 -18 {B[0]} {B[1]} Q 100 -48 {C[0]} {C[1]}"
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="15" stroke-linecap="round" stroke-linejoin="round"/><circle cx="{C[0]+1}" cy="{C[1]-3}" r="10" fill="{INK if m else SUN}" stroke="{INK}" stroke-width="3"/>'
def tick_hybrid(col,m=False,dashes=False):
    short=curved_taper((A[0],A[1]+2),(77,-20),B,14,15.5)
    long=curved_taper(B,(103,-44),C,15.5,4.2)
    g=f'<path d="{P(short)}" fill="{col}"/><path d="{P(long)}" fill="{col}"/><circle cx="{A[0]}" cy="{A[1]+2}" r="7" fill="{col}"/><circle cx="{B[0]}" cy="{B[1]}" r="7.7" fill="{col}"/>'
    if dashes and not m:
        for t0,t1 in [(0.1,0.22),(0.32,0.41),(0.5,0.57),(0.64,0.69)]:
            p0=qpt(B,(103,-44),C,t0); p1=qpt(B,(103,-44),C,t1)
            g+=f'<path d="M{p0[0]:.1f} {p0[1]:.1f} L{p1[0]:.1f} {p1[1]:.1f}" stroke="{W}" stroke-width="{1.7*(1-t0*0.8):.2f}" stroke-linecap="round"/>'
    g+=f'<circle cx="{C[0]+3}" cy="{C[1]-6}" r="9" fill="{INK if m else SUN}" stroke="{INK}" stroke-width="2.6"/>'
    return g
VS=[("3 Perspective, ink",lambda m: tick_straight(INK,m=m)),
    ("4 Perspective, tomato",lambda m: tick_straight(INK if m else TOM,m=m)),
    ("7 Hand-drawn, tomato",lambda m: tick_hand(INK if m else TOM,m)),
    ("4+7 Winding perspective, tomato",lambda m: tick_hybrid(INK if m else TOM,m)),
    ("4+7 Winding perspective, ink",lambda m: tick_hybrid(INK,m)),
    ("4+7 Winding, tomato + road dashes",lambda m: tick_hybrid(INK if m else TOM,m,True))]
def lock(f,m):
    return f'<path d="{E}" fill="{INK}"/>'+f(m)+f'<g transform="translate(156 0)">'+"".join(f'<path d="{d}" fill="{INK}"/>' for n,x,a,d in GS)+'</g>'
if __name__=="__main__":
    cells=[]
    for lab,f in VS:
        vb=f"-4 -92 {156+WS+8} 100"
        cells.append(f'<div style="border:1px solid #e3e7ee;border-radius:10px;padding:12px 14px"><div style="font:13px sans-serif;color:#556;margin-bottom:8px">{lab}</div><svg height="64" viewBox="{vb}">{lock(f,False)}</svg><div style="display:flex;gap:18px;align-items:end;margin-top:10px"><svg height="26" viewBox="{vb}">{lock(f,False)}</svg><svg height="26" viewBox="{vb}">{lock(f,True)}</svg></div></div>')
    open('/home/claude/logo/vtick2.html','w').write('<!doctype html><body style="margin:0;padding:16px;background:#fff;display:grid;grid-template-columns:1fr 1fr;gap:12px">'+"".join(cells)+'</body>')
