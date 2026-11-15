import urllib.parse, os
O="/home/claude/ds/project/assets/Textures"
def uri(svg): return "url(\"data:image/svg+xml,"+urllib.parse.quote(svg,safe=" =:/;,'-.")+"\")"
def T(light,dark): return light,dark
INK="22233A"
def paper(c,a): return f"<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 {c[0]} 0 0 0 0 {c[1]} 0 0 0 0 {c[2]} 0 0 0 {a} 0'/></filter><rect width='220' height='220' filter='url(#n)'/></svg>"
def contour(col,a):
    paths="".join(f"<path d='M-10 {y} C 50 {y-18} 100 {y+16} 160 {y-6} S 240 {y-14} 260 {y}' fill='none' stroke='{col}' stroke-opacity='{a}' stroke-width='1.2'/>" for y in (24,52,80,108,136))
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='240' height='160'>{paths}</svg>"
def grid(col,a): return f"<svg xmlns='http://www.w3.org/2000/svg' width='48' height='48'><path d='M0 .5H48M.5 0V48' stroke='{col}' stroke-opacity='{a}' stroke-dasharray='2 4'/><path d='M-3 .5h6M.5 -3v6' stroke='{col}' stroke-opacity='{a*2.2}'/></svg>"
def hatch(col,a): return f"<svg xmlns='http://www.w3.org/2000/svg' width='14' height='14'><path d='M2 12 L7 7' stroke='{col}' stroke-opacity='{a}' stroke-width='1.4' stroke-linecap='round'/></svg>"
def halftone(col,a): return f"<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10'><circle cx='2.5' cy='2.5' r='1.3' fill='{col}' fill-opacity='{a}'/><circle cx='7.5' cy='7.5' r='1.3' fill='{col}' fill-opacity='{a}'/></svg>"
L="#16233A"; D="#EEF3F9"
css=f"""
/* Texture: holiday-map surfaces. Margins only: hero, empty states, /learn, footers, illustrations. Never behind tables, forms or body copy. */
.evs-tex {{ position: relative; isolation: isolate; }}
.evs-tex::before {{ content: ""; position: absolute; inset: 0; z-index: -1; pointer-events: none; }}
.evs-tex--paper::before {{ background-image: {uri(paper((0.09,0.14,0.23),0.11))}; }}
[data-theme="dark"] .evs-tex--paper::before {{ background-image: {uri(paper((0.93,0.95,0.98),0.07))}; }}
.evs-tex--contour::before {{ background-image: {uri(contour(L,0.10))}; background-size: 240px 160px; }}
[data-theme="dark"] .evs-tex--contour::before {{ background-image: {uri(contour(D,0.10))}; }}
.evs-tex--grid::before {{ background-image: {uri(grid(L,0.10))}; background-size: 48px 48px; }}
[data-theme="dark"] .evs-tex--grid::before {{ background-image: {uri(grid(D,0.10))}; }}
.evs-tex--hatch::before {{ background-image: {uri(hatch(L,0.14))}; background-size: 14px 14px; }}
[data-theme="dark"] .evs-tex--hatch::before {{ background-image: {uri(hatch(D,0.12))}; }}
.evs-tex--halftone::before {{ background-image: {uri(halftone("#FFD166",0.55))}; background-size: 10px 10px; }}
.evs-tex--fold::before {{ background-image: linear-gradient(90deg, transparent 0 33.2%, rgba(22,35,58,.06) 33.3%, rgba(255,255,255,.5) 33.6%, transparent 34% 66.5%, rgba(22,35,58,.06) 66.6%, rgba(255,255,255,.5) 66.9%, transparent 67.3%); }}
[data-theme="dark"] .evs-tex--fold::before {{ background-image: linear-gradient(90deg, transparent 0 33.2%, rgba(0,0,0,.25) 33.3%, rgba(255,255,255,.06) 33.6%, transparent 34% 66.5%, rgba(0,0,0,.25) 66.6%, rgba(255,255,255,.06) 66.9%, transparent 67.3%); }}
/* Combine: class="evs-tex evs-tex--paper" on a wrapper, or stack two by nesting wrappers. */

/* Route divider: a dotted sky route that ends at the sun, between page sections */
.evs-route-divider {{ display: flex; align-items: center; gap: 8px; margin: var(--space-7) 0; }}
.evs-route-divider::before {{ content: ""; flex: 1; height: 4px; background: radial-gradient(circle, var(--sky) 1.6px, transparent 2px) 0 50% / 12px 4px repeat-x; }}
.evs-route-divider::after {{ content: ""; width: 14px; height: 14px; border-radius: 50%; background: var(--sunflower); box-shadow: 0 0 0 2px var(--ink); }}

/* Hand-drawn underline for a heading's last line (one per page at most) */
.evs-scribble {{ background: linear-gradient(transparent 0 0) ; padding-bottom: 6px; background-image: {uri("<svg xmlns='http://www.w3.org/2000/svg' width='200' height='10' viewBox='0 0 200 10' preserveAspectRatio='none'><path d='M2 7 C 40 2 80 9 120 4 S 180 6 198 3' fill='none' stroke='%233B78AE' stroke-width='3' stroke-linecap='round'/></svg>")}; background-repeat: no-repeat; background-size: 100% 10px; background-position: 0 100%; }}
"""
open("/home/claude/gen/texture.css","w").write(css)
# standalone swatch files for the asset group
for name,svg in [("paper-grain",paper((0.09,0.14,0.23),0.07)),("contour-lines",contour(L,0.10)),("map-grid",grid(L,0.10)),("land-hatch",hatch(L,0.14)),("halftone-sun",halftone("#FFD166",0.55))]:
    open(f"{O}/{name}.svg","w").write(svg.replace("%23","#"))
print(len(css))
