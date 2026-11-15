import sys; sys.path.insert(0,'/home/claude/gen')
from fonts3 import fp, stem_of
from fontaudit import shape
from vtick import P
from vtick2 import curved_taper
F=fp("bitter","800")
dE,wE,CAP=shape(F,"E"); dS,wS,_=shape(F,"Shortlist"); K=CAP/70; STEM=19.0  # matches the Bitter card Menno picked (fonts3: clamped stem 19)
C={"light":dict(ink="#16233A",ev="#3B78AE",sun="#FFD166",ring="#16233A",bg="#FFFFFF"),
   "dark":dict(ink="#EEF3F9",ev="#93C1EA",sun="#FFD166",ring="#EEF3F9",bg="#111A2B"),
   "mono":dict(ink="#111111",ev="#111111",sun="#111111",ring="#111111",bg="#FFFFFF"),
   "rev":dict(ink="#FFFFFF",ev="#FFFFFF",sun="#FFFFFF",ring="#FFFFFF",bg="#16233A")}
def tick(col,ring,sun,stem,tip=4.6,small=False,cut=False):
    A=(69,-42); B=(87,-6); Cc=(124,-74)
    if small: tip=6
    sh=curved_taper(A,(77,-20),B,stem*0.94,stem*1.04); lo=curved_taper(B,(103,-44),Cc,stem*1.04,tip)
    g=f'<path d="{P(sh)}" fill="{col}"/><path d="{P(lo)}" fill="{col}"/><circle cx="{B[0]}" cy="{B[1]}" r="{stem*0.52}" fill="{col}"/>'
    if not cut: g+=f'<circle cx="{A[0]}" cy="{A[1]}" r="{stem*0.47}" fill="{col}"/>'
    r=9.5 if not small else 11
    g+=f'<circle cx="{Cc[0]+3}" cy="{Cc[1]-6}" r="{r}" fill="{sun}" stroke="{ring}" stroke-width="{2.6 if not small else 3.4}"/>'
    return g
def lockup(c,stemf=1.0,small=False,cut=False,gapk=24):
    tx=wE-62*K+2*K; gap=tx+(136+gapk)*K
    g=f'<path d="{dE}" fill="{c["ev"]}"/><g transform="translate({tx:.1f} 0) scale({K:.3f})">{tick(c["ev"],c["ring"],c["sun"],STEM*stemf,small=small,cut=cut)}</g>'
    g+=f'<path transform="translate({gap:.1f} 0)" d="{dS}" fill="{c["ink"]}"/>'
    return g,f"-4 -{CAP+30:.0f} {gap+wS+10:.0f} {CAP+42:.0f}"
def icon(kind,small=False):
    if kind=="ink": tile,ev,ring,sun="#16233A","#93C1EA","#EEF3F9","#FFD166"
    elif kind=="sky": tile,ev,ring,sun="#3B78AE","#FFFFFF","#16233A","#FFD166"
    else: tile,ev,ring,sun="#E8F1F9","#3B78AE","#16233A","#FFD166"
    s=0.44/K if not small else 0.5/K
    g=f'<rect x="2" y="2" width="60" height="60" rx="14" fill="{tile}"/>'
    tx=wE-62*K+2*K
    g+=f'<g transform="translate({6 if not small else 4} {50 if not small else 52}) scale({s*K:.3f})"><path d="{dE}" transform="scale({1/K:.3f})" fill="{ev}"/><g transform="translate({tx/K:.1f} 0)">{tick(ev,ring,sun,STEM,small=small)}</g></g>'
    return g
if __name__=="__main__":
    rows=[]
    g,vb=lockup(C["light"])
    rows.append(f'<div style="padding:22px 26px;border-bottom:1px solid #eee"><svg height="96" viewBox="{vb}">{g}</svg></div>')
    rowc=[]
    for t in ("light","dark","mono","rev"):
        c=C[t]; g,vb=lockup(c); gs,_=lockup(c,small=True)
        rowc.append(f'<div style="background:{c["bg"]};padding:18px;display:grid;gap:12px"><svg height="52" viewBox="{vb}">{g}</svg><svg height="24" viewBox="{vb}">{gs}</svg></div>')
    rows.append('<div style="display:grid;grid-template-columns:1fr 1fr">'+"".join(rowc)+'</div>')
    st=[]
    for lab,f in [("tick lighter",0.85),("tick matched to Bitter's stems",1.0),("tick heavier",1.15)]:
        g,vb=lockup(C["light"],stemf=f)
        st.append(f'<div style="padding:12px 16px"><div style="font:12px sans-serif;color:#667">{lab}</div><svg height="44" viewBox="{vb}">{g}</svg></div>')
    rows.append('<div style="display:grid;grid-template-columns:1fr 1fr 1fr;border-top:1px solid #eee">'+"".join(st)+'</div>')
    ic=[]
    for lab,k in [("Ink tile",'ink'),("Sky tile",'sky'),("Light tile",'light')]:
        ic.append(f'<div style="padding:12px 16px;display:flex;gap:14px;align-items:end"><div style="font:12px sans-serif;color:#667;width:60px">{lab}</div>'+"".join(f'<svg width="{s}" viewBox="0 0 64 64">{icon(k,s<32)}</svg>' for s in (72,32,16))+'</div>')
    rows.append('<div style="display:grid;grid-template-columns:1fr 1fr 1fr;border-top:1px solid #eee">'+"".join(ic)+'</div>')
    open('/home/claude/fonts2/bitter.html','w').write('<!doctype html><body style="margin:0;background:#fff">'+"".join(rows)+'</body>')
