"""Generates the travel-map texture CSS block for bundle.css (v2: no dotted route; more map elements)."""
import urllib.parse, math, re
def u(svg): return 'url("data:image/svg+xml,' + urllib.parse.quote(svg, safe="=:/ ,'()").replace("%20", " ") + '")'
GRAIN = lambda c, a: u(f"<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 {c[0]} 0 0 0 0 {c[1]} 0 0 0 0 {c[2]} 0 0 0 {a} 0'/></filter><rect width='220' height='220' filter='url(#n)'/></svg>")
def CONTOUR(l, a): return u(f"<svg xmlns='http://www.w3.org/2000/svg' width='240' height='160'><g fill='none' stroke='{l}' stroke-opacity='{a}' stroke-width='1.3'>" + "".join(f"<path d='M-10 {24+28*i} C 50 {6+28*i} 100 {40+28*i} 160 {18+28*i} S 240 {10+28*i} 260 {24+28*i}'/>" for i in range(5)) + "</g></svg>")
def GRID(l, a): return u(f"<svg xmlns='http://www.w3.org/2000/svg' width='48' height='48'><path d='M0 .5H48M.5 0V48' stroke='{l}' stroke-opacity='{a}' stroke-dasharray='2 4'/><path d='M-3 .5h6M.5 -3v6' stroke='{l}' stroke-opacity='{a*2.2:.2f}'/></svg>")
def FOLDS(dark): return ("linear-gradient(90deg, transparent 0 33.2%, rgba(0,0,0,.22) 33.3%, rgba(255,255,255,.05) 33.6%, transparent 34% 66.5%, rgba(0,0,0,.22) 66.6%, rgba(255,255,255,.05) 66.9%, transparent 67.3%)" if dark else
                          "linear-gradient(90deg, transparent 0 33.2%, rgba(22,35,58,.05) 33.3%, rgba(255,255,255,.45) 33.6%, transparent 34% 66.5%, rgba(22,35,58,.05) 66.6%, rgba(255,255,255,.45) 66.9%, transparent 67.3%)")
def SUN(l):
    rays = "".join(f"<line x1='{60+30*math.cos(math.radians(a)):.1f}' y1='{20+30*math.sin(math.radians(a)):.1f}' x2='{60+38*math.cos(math.radians(a)):.1f}' y2='{20+38*math.sin(math.radians(a)):.1f}'/>" for a in range(90, 190, 25))
    return u(f"<svg xmlns='http://www.w3.org/2000/svg' width='80' height='80'><g stroke='{l}' stroke-opacity='.5' stroke-width='2' stroke-linecap='round'>{rays}</g><circle cx='60' cy='20' r='22' fill='#FFD166' stroke='{l}' stroke-opacity='.6' stroke-width='1.6'/></svg>")
def COMPASS(l):
    return u(f"<svg xmlns='http://www.w3.org/2000/svg' width='44' height='56' viewBox='0 0 44 56'><g fill='none' stroke='{l}' stroke-opacity='.45' stroke-width='1.3' stroke-linejoin='round'>"
             f"<circle cx='22' cy='34' r='15'/><path d='M22 15 L26 34 L22 53 L18 34Z'/><path d='M3 34 L22 30 L41 34 L22 38Z' stroke-opacity='.3'/></g>"
             f"<path d='M22 15 L26 34 L18 34Z' fill='{l}' fill-opacity='.35'/><text x='22' y='10' font-family='Georgia,serif' font-size='10' font-weight='700' text-anchor='middle' fill='{l}' fill-opacity='.55'>N</text></svg>")
def HILLS(h1, h2, l):
    return u(f"<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='64' viewBox='0 0 1200 64' preserveAspectRatio='none'>"
             f"<defs><pattern id='h' width='10' height='10' patternUnits='userSpaceOnUse'><path d='M1 9 L6 4' stroke='{l}' stroke-opacity='.16' stroke-width='1.2' stroke-linecap='round'/></pattern></defs>"
             f"<path d='M0 34 Q150 6 300 28 T600 24 T900 30 T1200 20 V64 H0Z' fill='{h1}' stroke='{l}' stroke-opacity='.5' stroke-width='1.5' vector-effect='non-scaling-stroke'/>"
             f"<path d='M0 34 Q150 6 300 28 T600 24 T900 30 T1200 20 V64 H0Z' fill='url(#h)'/>"
             f"<path d='M0 50 Q200 30 400 46 T800 44 T1200 40 V64 H0Z' fill='{h2}' stroke='{l}' stroke-opacity='.5' stroke-width='1.5' vector-effect='non-scaling-stroke'/></svg>")
INK, WH = (0.09, 0.14, 0.23), (0.93, 0.95, 0.98)
L = dict(l="#16233A", h1="#DDEFD3", h2="#C7E4B8"); D = dict(l="#EEF3F9", h1="#1F3324", h2="#2F5A33")
EDGE = "linear-gradient(90deg, transparent calc(100% - 112px), #000 calc(100% - 40px))"
FRAME = "linear-gradient(90deg, #000 0 24px, transparent 96px calc(100% - 96px), #000 calc(100% - 24px))"
PHONE = "linear-gradient(90deg, transparent calc(100% - 48px), #000 calc(100% - 8px))"
css = f'''/* Solarpunk travel map (Menno 2026-11-15, v2): the default for every plain coloured background. Map-style texture mixed in subtly:
   ::before = paper grain + faint map folds over the whole surface; ::after = contour lines + map grid at the edge(s), never behind text;
   the element's own background = a corner sun, a small compass rose, and a strip of hatched hills along the bottom (no routes, no dotted lines).
   evs-tex--map: left-aligned content. evs-tex--map-frame: centred content. evs-tex--no-sun: the block has its own illustration (hero, empty state).
   The class reserves bottom padding for the hills and side padding for the sun so nothing runs behind text (WCAG AA hard rule). */
.evs-tex--map::before, .evs-tex--map-frame::before {{ background-image: {GRAIN(INK, .11)}, {FOLDS(False)}; }}
[data-theme="dark"] .evs-tex--map::before, [data-theme="dark"] .evs-tex--map-frame::before {{ background-image: {GRAIN(WH, .07)}, {FOLDS(True)}; }}
.evs-tex--map::after, .evs-tex--map-frame::after {{ content: ""; position: absolute; inset: 0; z-index: -1; pointer-events: none; background-image: {CONTOUR(L['l'], .22)}, {GRID(L['l'], .1)}; background-size: 240px 160px, 48px 48px; }}
[data-theme="dark"] .evs-tex--map::after, [data-theme="dark"] .evs-tex--map-frame::after {{ background-image: {CONTOUR(D['l'], .18)}, {GRID(D['l'], .1)}; }}
.evs-tex--map::after {{ -webkit-mask-image: {EDGE}; mask-image: {EDGE}; }}
.evs-tex--map-frame::after {{ -webkit-mask-image: {FRAME}; mask-image: {FRAME}; }}
.evs-tex--map, .evs-tex--map-frame {{ --evs-tex-sun: {SUN(L['l'])}; --evs-tex-compass: {COMPASS(L['l'])}; --evs-tex-hills: {HILLS(L['h1'], L['h2'], L['l'])};
  background-image: var(--evs-tex-sun), var(--evs-tex-compass), var(--evs-tex-hills); background-repeat: no-repeat; background-position: right top, right 20px bottom 64px, left bottom; background-size: 80px 80px, 33px 42px, 100% 56px; padding-bottom: 88px; }}
[data-theme="dark"] .evs-tex--map, [data-theme="dark"] .evs-tex--map-frame {{ --evs-tex-sun: {SUN(D['l'])}; --evs-tex-compass: {COMPASS(D['l'])}; --evs-tex-hills: {HILLS(D['h1'], D['h2'], D['l'])}; }}
.evs-tex--no-sun, [data-theme="dark"] .evs-tex--no-sun {{ --evs-tex-sun: none; }}
.evs-tex--map:not(.evs-tex--no-sun) {{ padding-right: 104px; }}
.evs-tex--map-frame:not(.evs-tex--no-sun) {{ padding-left: 104px; padding-right: 104px; }}
@media (max-width: 760px) {{
  .evs-tex--map::after, .evs-tex--map-frame::after {{ -webkit-mask-image: {PHONE}; mask-image: {PHONE}; }}
  .evs-tex--map, .evs-tex--map-frame {{ --evs-tex-compass: none; background-size: 64px 64px, 0 0, 100% 44px; padding-bottom: 68px; }}
  .evs-tex--map:not(.evs-tex--no-sun) {{ padding-right: 80px; }}
  .evs-tex--map-frame:not(.evs-tex--no-sun) {{ padding-left: 80px; padding-right: 80px; }}
}}
'''
p = "components/bundle.css"; c = open(p).read()
start = c.index("\n/* Map print (default for every plain coloured background")
end_marker = "@media (max-width: 760px) { .evs-tex--map, .evs-tex--map-frame { background-size: 64px 64px, 100% 44px; padding-bottom: 68px; } }\n"
end = c.index(end_marker) + len(end_marker)
c = c[:start] + "\n" + css + c[end:]
open(p, "w").write(c)
print("ok", c.count("evs-tex--map"))
