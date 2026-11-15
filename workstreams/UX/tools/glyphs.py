import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
F='/home/claude/logo/overpass-latin-800-normal.ttf'
def glyphs(text,size=100):
    data=open(F,'rb').read(); tt=TTFont(F); upem=tt['head'].unitsPerEm; gs=tt.getGlyphSet(); order=tt.getGlyphOrder()
    font=hb.Font(hb.Face(data)); buf=hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); hb.shape(font,buf,{"kern":True})
    s=size/upem; x=0; out=[]
    for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
        name=order[info.codepoint]; pen=SVGPathPen(gs)
        gs[name].draw(TransformPen(pen,(s,0,0,-s,(x+pos.x_offset)*s,0)))
        out.append((name,x*s,pos.x_advance*s,pen.getCommands())); x+=pos.x_advance
    return out,x*s
