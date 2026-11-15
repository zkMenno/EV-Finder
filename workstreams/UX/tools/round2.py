import math
from round1 import *
import round1
def bez(p0,p1,p2,p3,n=40): return [tuple((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d for a,b,c,d in zip(p0,p1,p2,p3)) for t in [i/n for i in range(n+1)]]
def hybrid(rich):
    H1,H2,H3 = ("#B9DCA6","#7BB661","#4E9A3F") if rich else ("#EEF6E8","#DDEFD3","#C7E4B8")
    sky = "#E8F1F9" if rich else "#FBFAF6"
    st=f'stroke="{INK}" stroke-width="2" stroke-linejoin="round"'
    sh='filter="url(#sh)"' 
    s='<defs><filter id="sh" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="3" stdDeviation="2" flood-color="#16233A" flood-opacity=".18"/></filter></defs>'
    s+=f'<rect width="390" height="460" fill="{sky}"/>'
    s+="".join(f'<path d="M-10 {40+i*12} Q 90 {15+i*12} 180 {50+i*10} T 400 {25+i*12}" stroke="#d6dfea" fill="none" stroke-width="1"/>' for i in range(4))
    s+=f'<circle cx="290" cy="105" r="40" fill="{SUN}" {st}/>'+"".join(f'<line x1="{290+48*math.cos(math.radians(a))}" y1="{105+48*math.sin(math.radians(a))}" x2="{290+58*math.cos(math.radians(a))}" y2="{105+58*math.sin(math.radians(a))}" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>' for a in range(0,360,30))
    s+=f'<path d="M-10 230 Q 80 160 170 205 Q 260 150 400 200 V460 H-10Z" fill="{H1}" {st} {sh}/>'
    for x,y,sc in [(95,182,.75),(132,178,.85),(330,170,.8)]:
        s+=f'<g transform="translate({x} {y}) scale({sc})" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"><line x1="0" y1="0" x2="0" y2="52"/>'+"".join(f'<path d="M0 0 L0 -26" transform="rotate({a})" stroke-width="3.2"/>' for a in (20,140,260))+'<circle r="3.5" fill="#fff"/></g>'
    s+=f'<path d="M-10 290 Q 120 230 230 275 Q 320 310 400 260 V460 H-10Z" fill="{H2}" {st} {sh}/>'
    s+=f'<path d="M-10 360 Q 100 320 200 350 Q 300 380 400 340 V460 H-10Z" fill="{H3}" {st} {sh}/>'
    P=[(175,475),(200,410),(300,405),(275,352),(250,318),(160,326),(185,292),(200,274),(230,265),(241,254)]
    pts=[]
    for i in range(0,9,3): pts+=bez(*P[i:i+4])
    N=len(pts)
    seg=lambda col,add: "".join(f'<line x1="{pts[i][0]:.1f}" y1="{pts[i][1]:.1f}" x2="{pts[i+1][0]:.1f}" y2="{pts[i+1][1]:.1f}" stroke="{col}" stroke-width="{46-40*i/N+add:.1f}" stroke-linecap="round"/>' for i in range(N-1))
    s+=seg(INK,4)+seg("#fff",0)
    d="M"+" L".join(f"{x:.1f} {y:.1f}" for x,y in pts[:int(N*.85)])
    s+=f'<path d="{d}" stroke="{INK}" stroke-width="1.8" fill="none" stroke-dasharray="8 8"/>'
    s+=(f'<g transform="translate(40 300)" {st}><rect x="0" y="18" width="62" height="40" fill="#fff"/>'
        f'<path d="M-6 20 L31 -4 L68 20Z" fill="{"#F2B63D" if rich else "#FFF2CC"}"/><path d="M34 -1 L64 18 L50 18 L24 4Z" fill="#2F679C" stroke-width="1.5"/>'
        f'<rect x="10" y="32" width="12" height="26" fill="{SUN}"/><rect x="34" y="30" width="16" height="12" fill="#CFE3F3"/></g>')
    s+=f'<g transform="translate(110 336)" {st}><rect width="13" height="22" rx="4" fill="#fff"/><path d="M8 4 L4 11 H7 L6 17 L10 10 H7Z" fill="{SKY}" stroke-width="1"/></g>'
    s+=(f'<g transform="translate(252 393)" {st}>'
        f'<path d="M0 22 Q2 9 16 8 L24 -2 Q27 -6 34 -6 H50 Q58 -6 62 0 L69 8 Q80 9 80 19 V27 H0Z" fill="{SKY}"/>'
        f'<path d="M28 6 L33 -1 H42 V6Z M47 6 V-1 H54 L59 6Z" fill="#CFE3F3" stroke-width="1.5"/>'
        f'<circle cx="19" cy="27" r="7.5" fill="#fff"/><circle cx="61" cy="27" r="7.5" fill="#fff"/></g>')
    for x,y,r in [(345,298,14),(368,312,11),(22,395,13),(340,425,13)]:
        s+=f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+r+9}" stroke="{INK}" stroke-width="2"/><circle cx="{x}" cy="{y}" r="{r}" fill="{"#3F8A3A" if rich else "#B9DCA6"}" {st}/>'
    s+=f'<text x="180" y="236" font-family="Patrick" font-size="16" fill="{INK}">quiet road →</text>'
    return s
SUB="Electric cars you can actually afford, with real range. Compare them in plain language and make your shortlist."
round1.DIRS={"B+C · soft":("",lambda:hybrid(False),"Used EVs got good.",SUB),"B+C · rich":("",lambda:hybrid(True),"Used EVs got good.",SUB)}
import round1 as r
r.CSS=r.CSS
html=f"<!doctype html><style>{r.CSS}</style><body>{''.join(r.phone(k).replace(' · </div>','</div>') for k in r.DIRS)}</body>"
r.render(html,"hybrid",880,900)
