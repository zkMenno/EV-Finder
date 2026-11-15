import json,os,sys,re
P="/home/claude/ds/project"; t=json.load(open(P+"/tokens.json"))
def v(x): return re.sub(r"\{([^}]+)\}",r"var(--\1)",x)
css=":root,[data-theme=light]{"+"".join(f"--{k['name']}:{v(k['value']['light'] if isinstance(k['value'],dict) else k['value'])};" for k in t['color']['tokens']+t['shadow']['tokens'])+"}"
css+="[data-theme=dark]{"+"".join(f"--{k['name']}:{v(k['value']['dark'])};" for k in t['color']['tokens']+t['shadow']['tokens'] if isinstance(k['value'],dict))+"}"
css+=":root{"+"".join(f"--{k['name']}:{k['value']};" for f in ('spacing','radius','size') for k in t[f]['tokens'])+"".join(f"--font-{a}:{b};" for a,b in t['type']['families'].items())+"}"
bc=open(P+"/components/bundle.css").read()
css+="".join(f"@font-face{{font-family:'{f['family']}';src:url(file://{P}/{f['file']});font-weight:{f['weight']};font-style:{f['style']}}}" for f in t['type']['fonts'])
for comp in sorted(os.listdir(P+"/components")):
    f=f"{P}/components/{comp}/preview.html"
    if not os.path.exists(f): continue
    body=open(f).read()
    for th in ("light","dark"):
        open(f"/tmp/rh/{comp}-{th}.html","w").write(f'<!doctype html><html data-theme="{th}"><head><style>{css}{bc} body{{margin:0;background:var(--paper)}}</style></head><body>{body}</body></html>')
