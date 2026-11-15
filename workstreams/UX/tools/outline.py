import uharfbuzz as hb, sys, json
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
def outline(fontpath, text, size):
    data=open(fontpath,'rb').read()
    tt=TTFont(fontpath); upem=tt['head'].unitsPerEm; gs=tt.getGlyphSet(); order=tt.getGlyphOrder()
    face=hb.Face(data); font=hb.Font(face); buf=hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(font,buf,{"kern":True,"liga":True})
    s=size/upem; x=0; d=[]; xs=[]
    for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
        name=order[info.codepoint]; pen=SVGPathPen(gs)
        tp=TransformPen(pen,(s,0,0,-s,(x+pos.x_offset)*s,0))
        gs[name].draw(tp); d.append(pen.getCommands()); xs.append(((x)*s,(x+pos.x_advance)*s,name)); x+=pos.x_advance
    return " ".join(d), x*s, xs
if __name__=="__main__":
    d,w,xs=outline(sys.argv[1],sys.argv[2],float(sys.argv[3]))
    print(json.dumps({"d":d,"w":w,"xs":xs}))
