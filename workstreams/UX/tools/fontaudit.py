import sys, os; sys.path.insert(0,'/home/claude/gen')
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from vtick import P
from vtick2 import curved_taper
def ttf(woff):
    out=woff.replace('.woff2','.ttf')
    if not os.path.exists(out):
        t=TTFont(woff); t.flavor=None; t.save(out)
    return out
def shape(fp,text,size=100):
    data=open(fp,'rb').read(); tt=TTFont(fp); upem=tt['head'].unitsPerEm; gs=tt.getGlyphSet(); order=tt.getGlyphOrder()
    font=hb.Font(hb.Face(data)); buf=hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); hb.shape(font,buf,{"kern":True})
    s=size/upem; x=0; d=[]
    for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
        pen=SVGPathPen(gs); gs[order[info.codepoint]].draw(TransformPen(pen,(s,0,0,-s,(x+pos.x_offset)*s,0))); d.append(pen.getCommands()); x+=pos.x_advance
    cap=(getattr(tt['OS/2'],'sCapHeight',0) or 0.7*upem)*s
    return " ".join(d), x*s, cap
INK="#22335A"; TOM="#E8573F"; SUN="#F7C948"
def tick(k,stem):
    A=(69,-42); B=(87,-6); C=(124,-74)
    sh=curved_taper(A,(77,-20),B,stem*0.95,stem*1.05); lo=curved_taper(B,(103,-44),C,stem*1.05,4.2)
    g=f'<path d="{P(sh)}" fill="{TOM}"/><path d="{P(lo)}" fill="{TOM}"/><circle cx="{A[0]}" cy="{A[1]}" r="{stem*0.47}" fill="{TOM}"/><circle cx="{B[0]}" cy="{B[1]}" r="{stem*0.52}" fill="{TOM}"/>'
    g+=f'<circle cx="{C[0]+3}" cy="{C[1]-6}" r="9" fill="{SUN}" stroke="{INK}" stroke-width="2.6"/>'
    return g
def lockup(fp):
    dE,wE,cap=shape(fp,'E'); dS,wS,_=shape(fp,'Shortlist')
    k=cap/70  # scale tick to this font's cap height
    from fontTools.pens.boundsPen import BoundsPen
    tt=TTFont(fp); gs=tt.getGlyphSet(); upem=tt['head'].unitsPerEm
    bp=BoundsPen(gs); gs[tt.getBestCmap()[ord('l')]].draw(bp); stem=(bp.bounds[2]-bp.bounds[0])*100/upem
    stem=max(9,min(stem/k,18))
    tx=wE-62*k+2*k
    g=f'<path d="{dE}" fill="{INK}"/><g transform="translate({tx:.1f} 0) scale({k:.3f})">{tick(k,stem)}</g>'
    gap=tx+(136+24)*k
    g+=f'<g transform="translate({gap:.1f} 0)"><path d="{dS}" fill="{INK}"/></g>'
    return g, gap+wS, cap
F=[("Young Serif","young-serif","400","vintage travel-guide serif"),
   ("Caprasimo","caprasimo","400","retro holiday-poster display"),
   ("Fredoka","fredoka","600","rounded, playful, family"),
   ("Rubik","rubik","700","soft-cornered, friendly"),
   ("Bricolage Grotesque","bricolage-grotesque","800","quirky, characterful grotesk"),
   ("Gabarito","gabarito","800","bold, warm, geometric-humanist"),
   ("Barlow","barlow","700","based on California road signs and plates"),
   ("Figtree","figtree","800","clean, friendly, modern"),
   ("Bagel Fat One","bagel-fat-one","400","chunky, fun, sticker-like"),
   ("DM Serif Display","dm-serif-display","400","high-contrast editorial serif")]
if __name__=="__main__":
  cells=[]
  for name,pkg,wt,desc in F:
      fp=ttf(f"/home/claude/fonts2/fontsource-{pkg}-5.3.0/files/{pkg}-latin-{wt}-normal.woff2") if os.path.exists(f"/home/claude/fonts2/fontsource-{pkg}-5.3.0") else None
      if not fp:
          import glob; d=glob.glob(f"/home/claude/fonts2/fontsource-{pkg}-*/files/{pkg}-latin-{wt}-normal.woff2"); fp=ttf(d[0])
      g,w,cap=lockup(fp)
      vb=f"-4 -100 {w+10:.0f} 112"
      cells.append(f'<div style="border:1px solid #e3e7ee;border-radius:10px;padding:10px 14px"><div style="font:13px sans-serif;color:#556;margin-bottom:6px"><b>{name}</b> · {desc}</div><div style="display:flex;gap:20px;align-items:end"><svg height="58" viewBox="{vb}">{g}</svg><svg height="22" viewBox="{vb}">{g}</svg></div></div>')
  open('/home/claude/fonts2/audit.html','w').write('<!doctype html><body style="margin:0;padding:14px;background:#fff;display:grid;grid-template-columns:1fr 1fr;gap:10px">'+"".join(cells)+'</body>')
