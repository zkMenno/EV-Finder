import os
O="/home/claude/ds/project/assets/Symbols"
I="#16233A"; S="#3B78AE"; SUN="#FFD166"; T="#CFE3F3"; M="#7BB661"; W="#FFFFFF"
def w(name,body):
    open(f"{O}/{name}.svg","w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="{I}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{body}</svg>\n')
ICONS={
# navigation and core
"home-pin":f'<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z" fill="{S}"/><path d="M9 11l3-2.5 3 2.5v3H9z" fill="{W}"/>',
"flag":f'<path d="M6 21V4"/><path d="M6 4h11l-2.5 3.5L17 11H6" fill="{S}"/>',
"charge-stop":f'<rect x="3" y="3" width="18" height="18" rx="5" fill="{SUN}"/><path d="M13 6l-4 6.5h4L11 18"/>',
"voltage-400":'<path d="M12 3l-5 9h5l-2 9"/>',
"voltage-800":'<path d="M9 3L5 12h4l-2 9M17 3l-4 9h4l-2 9"/>',
"voltage-900":'<path d="M7 3L4 12h3l-1.5 9M13.5 3l-3 9h3L12 21M20 3l-3 9h3l-1.5 9"/>',
"chemistry":f'<rect x="3" y="7" width="16" height="10" rx="2"/><path d="M19 10.5h2v3h-2"/><path d="M7.5 14.5c0-3 2.5-4.5 6-4.5 0 3.5-2 5-6 4.5z" fill="{M}"/>',
"air-cooled":'<rect x="3" y="7" width="16" height="10" rx="2"/><path d="M19 10.5h2v3h-2"/><circle cx="11" cy="12" r="1"/><path d="M11 11c0-2 1.5-3 3-2.5M12 12.5c1.8 1 1.8 2.8.6 3.5M10 12.5c-1.8 1-3.4.2-3.4-1.2"/>',
"learn":f'<path d="M12 6c-2-1.5-5-2-8-1.5v13c3-.5 6 0 8 1.5 2-1.5 5-2 8-1.5v-13c-3-.5-6 0-8 1.5z" fill="{T}"/><path d="M12 6v13"/>',
"explore":f'<path d="M3 6l6-2 6 2 6-2v14l-6 2-6-2-6 2z" fill="{T}"/><path d="M9 4v14M15 6v14"/>',
# shortlist family
"shortlist":f'<rect x="3" y="5" width="16" height="16" rx="4"/><path d="M7 13l3 3 7-9" stroke="{S}" stroke-width="2.6"/><circle cx="18.5" cy="5.5" r="2.3" fill="{SUN}"/>',
"rule-out":'<rect x="3" y="5" width="16" height="16" rx="4"/><path d="M6 13.5c3-1 7-.8 10-1.6" stroke-width="2.4"/>',
"compare":f'<rect x="3" y="4" width="7.5" height="16" rx="2" fill="{T}"/><rect x="13.5" y="4" width="7.5" height="16" rx="2" fill="{T}"/><path d="M6 9h1.5M16.5 9H18M6 13h1.5M16.5 13H18"/>',
"share":f'<circle cx="6" cy="12" r="2.5" fill="{S}"/><circle cx="18" cy="6" r="2.5" fill="{SUN}"/><circle cx="18" cy="18" r="2.5" fill="{SUN}"/><path d="M8.3 11l7.4-3.8M8.3 13l7.4 3.8" stroke-dasharray="2 2.5"/>',
# range and weather
"range":f'<path d="M3 21l6-12M21 21l-6-12" /><path d="M12 21v-2M12 16v-2M12 11.5v-1.5" stroke="{S}"/><circle cx="12" cy="5.5" r="2.8" fill="{SUN}"/>',
"summer":f'<circle cx="12" cy="12" r="4" fill="{SUN}"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M5.6 18.4L7 17M17 7l1.4-1.4"/>',
"winter":'<path d="M12 3v18M4.2 7.5l15.6 9M4.2 16.5l15.6-9M9.5 4.5L12 7l2.5-2.5M9.5 19.5L12 17l2.5 2.5"/>',
"route":f'<circle cx="5" cy="18" r="2.2" fill="{W}"/><path d="M7 17c4-1 2-6 6-7s5-2 5-4" stroke="{S}" stroke-width="2.4" stroke-dasharray="0.1 4"/><circle cx="18.5" cy="5" r="2.4" fill="{SUN}"/>',
# charging
"plug-type2":f'<path d="M5 8l2-3h10l2 3a8 8 0 1 1-14 0z" fill="{T}"/><circle cx="10" cy="8" r=".9"/><circle cx="14" cy="8" r=".9"/><circle cx="8" cy="12.5" r="1.4"/><circle cx="12" cy="12.5" r="1.4"/><circle cx="16" cy="12.5" r="1.4"/><circle cx="10" cy="16.5" r="1.4"/><circle cx="14" cy="16.5" r="1.4"/>',
"plug-ccs":f'<path d="M6 5l1.5-2h9L18 5a6 6 0 0 1-12 0z" fill="{T}"/><circle cx="10" cy="6" r="1"/><circle cx="14" cy="6" r="1"/><rect x="6" y="14" width="12" height="7" rx="3.5" fill="{T}"/><circle cx="9.5" cy="17.5" r="1.4"/><circle cx="14.5" cy="17.5" r="1.4"/>',
"fast-charge":f'<rect x="4" y="3" width="10" height="18" rx="2" fill="{T}"/><path d="M10 7l-3 5h3l-1.5 4.5" stroke="{S}"/><path d="M14 9h3a2 2 0 0 1 2 2v5a1.5 1.5 0 0 0 3 0V8l-2-2"/>',
"home-charging":f'<path d="M3 11l9-7 9 7v9H3z" fill="{T}"/><path d="M13 9l-3 4.5h3L11.5 17" stroke="{S}"/>',
"battery-health":f'<rect x="3" y="7" width="16" height="10" rx="2"/><path d="M19 10.5h2v3h-2"/><path d="M7 12.5l2.5 2 4.5-5" stroke="{S}" stroke-width="2.4"/>',
# money and cars
"price":f'<path d="M3 12V5a2 2 0 0 1 2-2h7l9 9-9 9z" fill="{T}"/><path d="M11 10.2a2.4 2.4 0 1 0 0 3.6M7.5 11.2h3.2M7.5 12.8h3.2"/>',
"monthly-cost":f'<rect x="3" y="5" width="18" height="16" rx="3" fill="{T}"/><path d="M3 10h18M8 3v4M16 3v4"/><path d="M14 13.6a2.3 2.3 0 1 0 0 3.4M10.3 14.6h3.2M10.3 16h3.2"/>',
"car":f'<path d="M3 15v-3l2.5-5h11L20 12v3a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z" fill="{T}"/><path d="M6 12h12"/><circle cx="7.5" cy="16.5" r="2" fill="{W}"/><circle cx="16.5" cy="16.5" r="2" fill="{W}"/>',
"used-car":f'<path d="M3 15v-3l2.5-5h11L20 12v3a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z" fill="{T}"/><circle cx="7.5" cy="16.5" r="2" fill="{W}"/><circle cx="16.5" cy="16.5" r="2" fill="{W}"/><path d="M14 3h6v4l-3 2-3-2z" fill="{SUN}"/>',
"see-listings":f'<rect x="3" y="4" width="14" height="16" rx="2" fill="{T}"/><path d="M6 9h8M6 13h5"/><path d="M15 15l6-6M21 9h-4M21 9v4"/>',
"boot-space":f'<rect x="3" y="7" width="18" height="13" rx="2" fill="{T}"/><path d="M9 7V5h6v2M3 12h18"/>',
# data and help
"legend":f'<rect x="3" y="3" width="18" height="18" rx="4" fill="{W}"/><circle cx="12" cy="8" r="1"/><path d="M12 11v6"/>',
"source":f'<path d="M6 3h9l4 4v14H6z" fill="{W}"/><path d="M15 3v4h4M9 11h7M9 15h5"/>',
"known-issue":'<path d="M14.5 5.5a4 4 0 0 0-5 5L4 16l4 4 5.5-5.5a4 4 0 0 0 5-5l-2.5 2.5-2-2z"/>',
"filter":'<path d="M4 7h10M18 7h2M4 17h2M10 17h10"/><circle cx="16" cy="7" r="2"/><circle cx="8" cy="17" r="2"/>',
"search":'<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5 5"/>',
"detail-levels":f'<path d="M12 4l9 4.5-9 4.5-9-4.5z" fill="{T}"/><path d="M3 13l9 4.5 9-4.5M3 17.5L12 22l9-4.5"/>',
}
for k,v in ICONS.items(): w(k,v)
print(len(ICONS))
# sheet
cells="".join(f'<div style="display:grid;justify-items:center;gap:6px;padding:10px;border:1px solid #e3e7ee;border-radius:10px"><img src="file://{O}/{k}.svg" width="40"><img src="file://{O}/{k}.svg" width="20"><span style="font:11px sans-serif;color:#556">{k}</span></div>' for k in ICONS)
open('/home/claude/gen/icons.html','w').write(f'<!doctype html><body style="margin:0;padding:14px;background:#fff;display:grid;grid-template-columns:repeat(9,1fr);gap:8px">{cells}</body>')
