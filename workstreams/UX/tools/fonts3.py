import sys, glob; sys.path.insert(0,'/home/claude/gen')
from fontaudit import ttf, shape
from concepts2 import tick
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
INK="#1E2B45"; SUN="#F4C542"
def fp(pkg,wt): return ttf(glob.glob(f"/home/claude/fonts2/fontsource-{pkg}-*/files/{pkg}-latin-{wt}-normal.woff2")[0])
def stem_of(f):
    tt=TTFont(f); gs=tt.getGlyphSet(); b=BoundsPen(gs); gs[tt.getBestCmap()[ord('l')]].draw(b); return (b.bounds[2]-b.bounds[0])*100/tt['head'].unitsPerEm
def logo(f,ink=INK,sun=SUN):
    dE,wE,cap=shape(f,"E"); dS,wS,_=shape(f,"Shortlist"); k=cap/70; st=max(10,min(stem_of(f)/k,19))
    tx=wE-62*k+3*k
    g=f'<path d="{dE}" fill="{ink}"/><g transform="translate({tx:.1f} 0) scale({k:.3f})">{tick(ink,st,ink,sun)}</g>'
    gap=tx+150*k
    g+=f'<path transform="translate({gap:.1f} 0)" d="{dS}" fill="{ink}"/>'
    return g, gap+wS, cap
F=[("Solway","solway","800","rounded slab: sturdy like a road sign, soft at the edges"),
   ("Zilla Slab","zilla-slab","700","warm slab serif: dependable, a bit bookish"),
   ("Fraunces","fraunces","700","soft old-style serif: trustworthy with a wink"),
   ("Bitter","bitter","800","contemporary slab: clear, honest, sturdy"),
   ("Lexend","lexend","700","built for easy reading: open, calm, plain-spoken"),
   ("Red Hat Display","red-hat-display","800","friendly geometric: confident, open"),
   ("Nunito","nunito","800","rounded sans: the warmest, most approachable"),
   ("Albert Sans","albert-sans","800","Scandinavian grotesk: clean, honest, modern")]
if __name__=="__main__":
    cells=[]
    for name,pkg,wt,desc in F:
        f=fp(pkg,wt); g,w,cap=logo(f)
        vb=f"-4 -100 {w+10:.0f} 112"
        css=f"@font-face{{font-family:'{name}';src:url(file://{glob.glob(f'/home/claude/fonts2/fontsource-{pkg}-*/files/{pkg}-latin-{wt}-normal.woff2')[0]})}}"
        cells.append(f'<style>{css}</style><div style="border:1px solid #e3e7ee;border-radius:10px;padding:12px 16px"><div style="font:13px sans-serif;color:#556;margin-bottom:8px"><b>{name}</b>: {desc}</div><div style="display:flex;gap:22px;align-items:end"><svg height="56" viewBox="{vb}">{g}</svg><svg height="22" viewBox="{vb}">{g}</svg></div><div style="font-family:\'{name}\';font-size:26px;line-height:1.15;color:{INK};margin-top:10px">Compare EVs. Make your shortlist.</div></div>')
    open('/home/claude/fonts2/fonts3.html','w').write('<!doctype html><body style="margin:0;padding:14px;background:#fff;display:grid;grid-template-columns:1fr 1fr;gap:12px">'+"".join(cells)+'</body>')
