import urllib.parse
from round1 import FONTS, render
def uri(svg): return "url(\"data:image/svg+xml," + urllib.parse.quote(svg.replace("%23", "#"), safe="") + "\")"
def grain(col, a): return uri(f"<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 {col[0]} 0 0 0 0 {col[1]} 0 0 0 0 {col[2]} 0 0 0 {a} 0'/></filter><rect width='220' height='220' filter='url(%23n)'/></svg>")
def contour(c, a): return uri(f"<svg xmlns='http://www.w3.org/2000/svg' width='240' height='160'>" + "".join(f"<path d='M-10 {24+28*i} C 50 {6+28*i} 100 {40+28*i} 160 {18+28*i} S 240 {10+28*i} 260 {24+28*i}' fill='none' stroke='{c}' stroke-opacity='{a}' stroke-width='1.3'/>" for i in range(6)) + "</svg>")
def halftone(c, a): return uri(f"<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12'><circle cx='3' cy='3' r='1.6' fill='{c}' fill-opacity='{a}'/><circle cx='9' cy='9' r='1.6' fill='{c}' fill-opacity='{a}'/></svg>")
def hatch(c, a): return uri(f"<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12'><path d='M0 12 L12 0' stroke='{c}' stroke-opacity='{a}' stroke-width='1.2'/></svg>")
def rows(c, a): return uri(f"<svg xmlns='http://www.w3.org/2000/svg' width='60' height='14'><path d='M0 7 Q15 3 30 7 T60 7' fill='none' stroke='{c}' stroke-opacity='{a}' stroke-width='1.4'/></svg>")
def hills(c1, c2, line): return uri(f"<svg xmlns='http://www.w3.org/2000/svg' width='800' height='120' viewBox='0 0 800 120' preserveAspectRatio='none'><path d='M0 70 Q120 20 240 60 Q380 100 520 50 Q660 10 800 55 V120 H0Z' fill='{c1}' stroke='{line}' stroke-opacity='.5' stroke-width='1.5'/><path d='M0 95 Q160 60 320 90 Q480 115 640 80 Q720 65 800 85 V120 H0Z' fill='{c2}' stroke='{line}' stroke-opacity='.5' stroke-width='1.5'/></svg>")
def sunrays(c, a): return uri(f"<svg xmlns='http://www.w3.org/2000/svg' width='260' height='260'><g stroke='{c}' stroke-opacity='{a}' stroke-width='2' stroke-linecap='round'>" + "".join(f"<line x1='260' y1='0' x2='{260-130*__import__('math').cos(__import__('math').radians(d)):.0f}' y2='{130*__import__('math').sin(__import__('math').radians(d)):.0f}'/>" for d in range(5, 90, 10)) + "</g><circle cx='260' cy='0' r='56' fill='%23FFD166' fill-opacity='.55' stroke='%2316233A' stroke-opacity='.35' stroke-width='1.5'/></svg>")

INK=(0.09,0.14,0.23); WH=(0.93,0.95,0.98)
L = dict(sea="#E8F1F9", sun="#FFF2CC", mead="#E4F2DC", ink="#16233A")
D = dict(sea="#172338", sun="#3A3320", mead="#1F3324", ink="#EEF3F9")
EDGE = "linear-gradient(90deg, transparent 0 64%, #000 90%)"   # texture fades out behind the text column (left)

def styles(opt, th):
    dark = th is D; c = "%23EEF3F9" if dark else "%2316233A"; g = WH if dark else INK
    if opt == "A":   # map print: grain everywhere + contours/folds at the edge
        return {"base": f"background-image:{grain(g, .07 if not dark else .06)}",
                "deco": f"background-image:{contour(c, .22)};background-size:240px 160px;-webkit-mask-image:{EDGE};mask-image:{EDGE}"}
    if opt == "B":   # riso: grain + halftone corner + hatch strip
        return {"base": f"background-image:{grain(g, .09 if not dark else .07)}",
                "deco": f"background-image:{halftone('%23FFD166' if not dark else '%23FFD166', .7)},{hatch(c,.18)};background-size:12px 12px,12px 12px;-webkit-mask-image:radial-gradient(circle at 100% 0, #000 0 14%, transparent 30%),linear-gradient(0deg,#000 0 14%,transparent 26%);mask-image:radial-gradient(circle at 100% 0, #000 0 14%, transparent 30%),linear-gradient(0deg,#000 0 14%,transparent 26%)"}
    # C landscape: grain + field rows + hills along the bottom + sun corner
    hc1, hc2 = ("#DDEFD3", "#C7E4B8") if not dark else ("#1F3324", "#2F5A33")
    return {"base": f"background-image:{grain(g, .07 if not dark else .06)}",
            "deco": f"background-image:{sunrays(c,.25)},{hills(hc1.replace('#','%23'), hc2.replace('#','%23'), c)},{rows(c,.16)};background-size:260px 260px,100% 70px,60px 14px;background-repeat:no-repeat,no-repeat,repeat;background-position:right top,left bottom,0 0;-webkit-mask-image:linear-gradient(90deg,transparent 0 62%,#000 85%),linear-gradient(0deg,#000 0 30%,transparent 31%);mask-image:linear-gradient(90deg,transparent 0 62%,#000 85%),linear-gradient(0deg,#000 0 30%,transparent 31%)"}

def block(opt, th, ground, title, body, tall=False):
    s = styles(opt, th)
    return (f"<div class='blk' style='background-color:{th[ground]};color:{th['ink']};{'min-height:250px' if tall else ''}'>"
            f"<div class='lay' style='{s['base']}'></div><div class='lay' style='{s['deco']}'></div>"
            f"<div class='txt'><h3>{title}</h3><p>{body}</p></div></div>")

ROWS = [("A", "Map print", "Paper grain everywhere, contour lines that fade in towards the edge"),
        ("B", "Riso print", "Stronger grain, a sunflower halftone corner and hatching along the bottom"),
        ("C", "Landscape", "Grain, soft field rows, little hills along the bottom and a sun in the corner")]
html = "<div class='hd'><h1>Texture on plain coloured backgrounds</h1><p>Each texture is strongest at the edges and fades out behind the text, so text still passes WCAG AA. Same grounds in every row: hero band, tip callout, empty state, and a dark Night drive band.</p></div>"
for k, n, d in ROWS:
    html += f"<h2>{k} · {n}</h2><p class='sub'>{d}</p><div class='row'>"
    html += block(k, L, "sea", "Used EVs got good.", "Electric cars you can actually afford, with real range.", True)
    html += block(k, L, "sun", "Tip", "Winter range is the number to check if you drive long trips in January.")
    html += block(k, L, "mead", "Your shortlist is empty", "Tap “Add to shortlist” on any car to keep it here.")
    html += block(k, D, "sea", "Night drive", "Electric cars you can actually afford, with real range.")
    html += "</div>"
CSS = FONTS + """body{margin:0;background:#E3E8EE;font-family:Atkinson;padding:32px;width:1440px;color:#16233A}
.hd h1{font:800 32px Bitter;margin:0 0 6px}.hd p,.sub{margin:0 0 10px;color:#45546F;font-size:16px}
h2{font:800 22px Bitter;margin:26px 0 2px}
.row{display:grid;grid-template-columns:1.4fr 1fr 1fr 1.2fr;gap:16px}
.blk{position:relative;border-radius:18px;overflow:hidden;min-height:250px;isolation:isolate}
.lay{position:absolute;inset:0;z-index:-1}
.txt{padding:28px 26px;max-width:300px}.txt h3{font:800 26px/1.15 Bitter;margin:0 0 8px}.txt p{font-size:17px;line-height:1.5;margin:0;opacity:.88}"""
render(f"<!doctype html><style>{CSS}</style><body>{html}</body>", "texture-options", 1504, 1130)
