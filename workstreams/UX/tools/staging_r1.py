"""T-132 hero questions + T-130 catalogue layout mockups (UX, 2026-11-17).

Builds HTML frames on the real tokens (apps/web tokens.generated.css) and bundle.css, then renders
PNGs at 360 and 1280 px with Playwright + Chrome. Numbers in the frames are SAMPLE values for
layout only (every frame says so); real values come from the release.

    python3 workstreams/UX/tools/staging_r1.py   (run from the repo root)
"""
import json, os, re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
DS = ROOT / "docs/design"
OUT = DS / "explorations/staging-r1"
OUT.mkdir(parents=True, exist_ok=True)

tokens = (ROOT / "apps/web/src/app/tokens.generated.css").read_text()
tokens = tokens.replace(':root[data-theme="dark"]', '[data-theme="dark"]')
bundle = (DS / "components/bundle.css").read_text()
tj = json.loads((DS / "tokens.json").read_text())
fonts = "".join(
    f"@font-face{{font-family:'{f['family']}';src:url(file://{DS}/{f['file'].split('/')[-1] if not (DS/f['file']).exists() else f['file']});font-weight:{f['weight']};font-style:{f['style']}}}"
    for f in tj["type"]["fonts"]
)
fam = "".join(f"--font-{a}:{b};" for a, b in tj["type"]["families"].items())
sizes = "".join(f"--{k['name']}:{k['value']};" for f in ("spacing", "radius", "size") for k in tj[f]["tokens"])


def sym(name, cls="ic"):
    s = (DS / f"assets/Symbols/{name}.svg").read_text()
    s = s.replace('stroke="#16233A"', 'stroke="currentColor"').replace('fill="#CFE3F3"', 'fill="var(--sea)"')
    s = s.replace('stroke="#3B78AE"', 'stroke="var(--sky)"').replace('fill="#3B78AE"', 'fill="var(--sky)"')
    s = re.sub(r'width="48" height="48"', f'class="{cls}" aria-hidden="true"', s, count=1)
    return s


TICK = ('<svg class="tick" viewBox="0 0 64 64" aria-hidden="true"><path d="M10 34 L24 48 L52 16" fill="none" stroke="var(--ink)" '
        'stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/><path d="M10 34 L24 48 L52 16" fill="none" stroke="var(--sky)" '
        'stroke-width="8.5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="52" cy="14" r="6.8" fill="var(--sunflower)" stroke="var(--ink)" stroke-width="2.6"/></svg>')
SLOT = '<svg class="tick" viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="20" fill="none" stroke="var(--line-strong)" stroke-width="3"/></svg>'
CHEV = '<svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
PEN = '<svg class="pen" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20h4L19 9l-4-4L4 16v4z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>'
BACK = '<svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M15 6l-6 6 6 6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CARET = '<svg class="caret" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
X = '<svg class="x" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 7l10 10M17 7L7 17" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>'
STAR_ADD = ('<svg class="add" viewBox="0 0 64 64" aria-hidden="true"><rect x="8" y="8" width="48" height="48" rx="12" fill="none" stroke="currentColor" stroke-width="4"/>'
            '<path d="M32 20v24M20 32h24" stroke="currentColor" stroke-width="4.5" stroke-linecap="round"/></svg>')

CSS = """
*{box-sizing:border-box} body{margin:0;background:var(--paper);color:var(--ink);font:400 17px/26px var(--font-text)}
h1,h2,h3{margin:0} p{margin:0} ul,ol{margin:0;padding:0;list-style:none}
.ic{width:20px;height:20px;flex:none} .chev,.caret,.pen,.x{width:18px;height:18px;flex:none} .tick{width:28px;height:28px;flex:none}
.sample{display:table;margin:16px auto;font:400 15px/18px var(--font-hand);background:var(--sunflower);color:var(--on-sunflower);padding:3px 8px;border-radius:4px;transform:rotate(-1.5deg)}
.hdr{display:flex;align-items:center;gap:16px;padding:12px 16px;border-bottom:1.5px solid var(--line);background:var(--paper)}
.logo{font:800 20px/24px var(--font-display);letter-spacing:-.3px;display:flex;align-items:center;gap:6px}
.logo b{color:var(--sky);font-weight:800}
.hdr nav{margin-left:auto;display:flex;gap:20px;font-size:15px;color:var(--ink-2)} .hdr nav a{color:inherit;text-decoration:none}
.hdr nav a.on{color:var(--ink);font-weight:700;box-shadow:inset 0 -3px 0 var(--sunflower)}
/* ── progress road ── */
.road{display:grid;grid-template-columns:repeat(4,auto);align-items:start;position:relative;margin:4px 0 0}
.road::before{content:"";position:absolute;left:14px;right:14px;top:13px;height:4px;border-radius:4px;background:repeating-linear-gradient(90deg,var(--line-strong) 0 8px,transparent 8px 14px)}
.road .done-line{position:absolute;left:14px;top:12px;height:6px;border-radius:6px;background:var(--sky)}
.stop{position:relative;display:grid;justify-items:center;gap:4px;font-size:14px;line-height:18px;color:var(--ink-2);text-align:center}
.stop:first-child{justify-items:start;text-align:left} .stop:last-child{justify-items:end;text-align:right}
.dot{width:30px;height:30px;border-radius:50%;display:grid;place-items:center;background:var(--surface);border:2.5px solid var(--line-strong);font:700 14px/1 var(--font-text);color:var(--ink-2)}
.stop.done .dot{border-color:var(--ink);background:var(--surface)} .stop.done .dot svg{width:22px;height:22px}
.stop.now{color:var(--ink);font-weight:700} .stop.now .dot{border:3px solid var(--ink);background:var(--sunflower);color:var(--on-sunflower)}
.stop .flag{width:22px;height:22px}
.road{grid-template-columns:1fr 1fr 1fr auto}
/* ── answers trail ── */
.trail{display:flex;flex-wrap:wrap;gap:8px}
.ans{display:inline-flex;align-items:center;gap:6px;min-height:36px;padding:4px 10px 4px 12px;border-radius:var(--radius-pill);background:var(--surface);border:1.5px solid var(--line-strong);font-size:15px;line-height:20px;color:var(--ink)}
.ans .pen{color:var(--link);width:16px;height:16px}
/* ── question + option tiles ── */
.qcount{font-size:15px;color:var(--ink-2)}
.q{font:700 26px/32px var(--font-display);letter-spacing:-.3px;margin:4px 0 4px}
.qhelp{color:var(--ink-2);font-size:16px;line-height:24px}
.opts{display:grid;gap:10px;margin-top:16px}
.opt{display:grid;grid-template-columns:28px 1fr 28px;gap:2px 14px;align-items:center;min-height:64px;padding:12px 16px;border-radius:var(--radius-md);background:var(--surface);border:2px solid var(--line-strong);box-shadow:var(--shadow-sticker)}
.opt .ic{width:28px;height:28px;color:var(--ink)}
.opt b{font-size:18px;line-height:24px} .opt small{display:block;font-size:15px;line-height:21px;color:var(--ink-2)}
.opt.noic{grid-template-columns:1fr 28px}
.opt.on{border-color:var(--ink);background:var(--paper-sea);box-shadow:inset 0 0 0 1.5px var(--ink),var(--shadow-sticker)}
.opt .tick{justify-self:end}
.opts.two{grid-template-columns:1fr 1fr} .opts.two .opt{grid-template-columns:1fr 28px;min-height:56px}
.qnav{display:flex;align-items:center;justify-content:space-between;margin-top:18px}
.lnk{display:inline-flex;align-items:center;gap:4px;color:var(--link);font-weight:700;text-decoration:underline;text-underline-offset:3px;min-height:44px}
.muted{color:var(--ink-2);font-size:15px}
/* ── budget ── */
.money{display:flex;align-items:center;gap:8px;margin-top:14px;border:2px solid var(--ink);border-radius:var(--radius-md);background:var(--surface);padding:6px 14px;min-height:60px}
.money span{font:700 24px/1 var(--font-text);color:var(--ink-2)} .money input{border:0;outline:0;background:transparent;font:700 28px/1 var(--font-text);color:var(--ink);width:100%;font-variant-numeric:tabular-nums}
.quick{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:12px}
.qb{min-height:48px;border-radius:var(--radius-md);border:2px solid var(--line-strong);background:var(--surface);font:700 16px/1 var(--font-text);display:grid;place-items:center;color:var(--ink)}
.qb.on{border-color:var(--ink);background:var(--paper-sea);box-shadow:inset 0 -4px 0 var(--sunflower)}
.month{margin-top:12px;display:flex;gap:10px;align-items:flex-start;background:var(--sunflower-tint);border-radius:var(--radius-md);padding:10px 12px;font-size:15px;line-height:21px}
.month b{font-size:18px}
.seg{display:grid;grid-template-columns:repeat(3,1fr);padding:4px;gap:4px;background:var(--surface-sunk);border:1.5px solid var(--line);border-radius:var(--radius-md);margin-top:8px}
.seg span{min-height:40px;display:grid;place-items:center;border-radius:8px;font-weight:700;font-size:15px;color:var(--ink-2)}
.seg span.on{background:var(--surface);color:var(--ink);box-shadow:inset 0 -3px 0 var(--sunflower),var(--shadow-sticker)}
.lbl{font-weight:700;font-size:16px;margin-top:20px}
.cta{width:100%;justify-content:center;margin-top:20px;font-size:18px;min-height:56px}
/* ── results ── */
.summary{display:flex;align-items:center;gap:12px;flex-wrap:wrap;background:var(--surface);border:1.5px solid var(--line);border-radius:var(--radius-lg);padding:12px 14px}
.summary .who{font:700 20px/26px var(--font-display)}
.sl{background:var(--sunflower-tint);border-radius:var(--radius-lg);padding:14px 12px 8px;margin-top:16px}
.slh{display:flex;align-items:baseline;justify-content:space-between;gap:8px;padding:0 4px 10px}
.slh h2{font:700 22px/28px var(--font-display)}
.row{display:grid;grid-template-columns:auto 1fr auto;gap:2px 12px;align-items:start;background:var(--surface);border:1.5px solid var(--line);border-radius:var(--radius-md);padding:12px;margin-bottom:8px;box-shadow:var(--shadow-sticker)}
.rk{width:30px;height:30px;border-radius:50%;background:var(--ink);color:var(--surface);display:grid;place-items:center;font:700 15px/1 var(--font-text);margin-top:2px}
.nm{font:700 18px/23px var(--font-text)} .yrs{color:var(--ink-2);font-size:15px;line-height:20px}
.facts{grid-column:2/4;display:flex;flex-wrap:wrap;gap:4px 16px;margin-top:6px;font-size:15px;line-height:20px;color:var(--ink-2)}
.facts span{display:inline-flex;align-items:center;gap:5px} .facts b{color:var(--ink);font-size:17px}
.facts .price b{font-size:18px}
.why{grid-column:2/4;margin-top:6px;font-size:15px;line-height:21px;color:var(--ink)}
.why::before{content:"Why: ";font-weight:700}
.add{width:44px;height:44px;color:var(--ink-2)} .addbtn{width:48px;height:48px;display:grid;place-items:center;border-radius:var(--radius-md);border:1.5px solid var(--line-strong);background:var(--surface)}
.addbtn.on{background:var(--sunflower-tint);border-color:var(--ink)} .addbtn .tick{width:30px;height:30px} .addbtn .add{width:28px;height:28px}
.more h2{font:700 20px/26px var(--font-display);margin:24px 4px 8px}
.mini{display:grid;grid-template-columns:28px 1fr auto auto;gap:10px;align-items:center;padding:10px 4px;border-bottom:1.5px solid var(--line);font-size:16px}
.mini .n{color:var(--ink-2);font-weight:700;text-align:center} .mini .p{font-weight:700;font-variant-numeric:tabular-nums} .mini .w{color:var(--ink-2);font-size:15px;display:inline-flex;gap:4px;align-items:center;min-width:72px;justify-content:flex-end}
.actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}
.thumb{width:76px;height:50px;border-radius:8px;background:var(--surface-sunk);border:1.5px solid var(--line);display:grid;place-items:center;color:var(--ink-3)}
.thumb .ic{width:30px;height:30px}
.note{font:400 18px/22px var(--font-hand);color:var(--ink-2)}
.wrap{padding:16px}
.herocard{background:var(--paper-sea);border-radius:0 0 var(--radius-lg) var(--radius-lg);padding:20px 16px 24px}
.scene{display:block;margin:0 auto}
.panel{background:var(--surface);border:1.5px solid var(--line);border-radius:var(--radius-lg);padding:20px 16px;box-shadow:var(--shadow-sticker)}
/* ── desktop ── */
.d .hdr{padding:14px 40px} .d .logo{font-size:24px}
.dhero{background:var(--paper-sea);display:grid;grid-template-columns:minmax(0,1fr) 400px;gap:48px;padding:40px 40px 48px;align-items:start}
.dhero h1{font:800 52px/56px var(--font-display);letter-spacing:-1px}
.dpanel{background:var(--surface);border:1.5px solid var(--line);border-radius:var(--radius-lg);padding:28px 32px;box-shadow:var(--shadow-sticker);max-width:640px}
.d .opts.grid2{grid-template-columns:1fr 1fr}
.dres{display:grid;grid-template-columns:300px minmax(0,1fr);gap:40px;padding:32px 40px 48px;align-items:start}
.side{position:sticky;top:16px;background:var(--surface);border:1.5px solid var(--line);border-radius:var(--radius-lg);padding:20px}
.side h2{font:700 20px/26px var(--font-display)}
.sa{display:grid;grid-template-columns:1fr auto;gap:2px 8px;padding:10px 0;border-bottom:1.5px solid var(--line)}
.sa small,.sa b{grid-column:1}.sa small{color:var(--ink-2);font-size:14px;line-height:18px} .sa b{font-size:16px;line-height:22px} .sa .pen{grid-column:2;grid-row:1/3;align-self:center;color:var(--link)}
.tbl{width:100%;border-collapse:separate;border-spacing:0 8px}
.tbl th{font:700 14px/18px var(--font-text);color:var(--ink-2);text-align:left;padding:0 12px;white-space:nowrap}
.tbl th.r,.tbl td.r{text-align:right}
.tbl td{background:var(--surface);padding:12px;border-top:1.5px solid var(--line);border-bottom:1.5px solid var(--line);vertical-align:middle;font-size:16px}
.tbl td:first-child{border-left:1.5px solid var(--line);border-radius:var(--radius-md) 0 0 var(--radius-md)} .tbl td:last-child{border-right:1.5px solid var(--line);border-radius:0 var(--radius-md) var(--radius-md) 0}
.tbl .num{font:700 18px/22px var(--font-text);font-variant-numeric:tabular-nums;white-space:nowrap} .tbl .sub{display:block;color:var(--ink-2);font-size:14px;line-height:18px;font-weight:400}
.tbl .carc{display:flex;gap:12px;align-items:center}
.tbl .whyc{display:block;color:var(--ink);font-size:15px;line-height:20px;min-width:26ch;max-width:32ch}.tbl .nm{white-space:nowrap}
.slwrap{background:var(--sunflower-tint);border-radius:var(--radius-lg);padding:16px 16px 8px}
.tbl.small td{padding:8px 12px;font-size:15px} .tbl.small .num{font-size:16px}
/* ── catalogue ── */
.ctop{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;flex-wrap:wrap}
.ctop h1{font:800 40px/44px var(--font-display);letter-spacing:-.6px}
.bar{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-top:16px;padding:10px 0;border-top:1.5px solid var(--line);border-bottom:1.5px solid var(--line)}
.sel{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:8px 12px;border-radius:var(--radius-md);border:2px solid var(--line-strong);background:var(--surface);font-weight:700;font-size:15px}
.sel small{font-weight:400;color:var(--ink-2)}
.pill{display:inline-flex;align-items:center;gap:6px;min-height:36px;padding:4px 8px 4px 12px;border-radius:var(--radius-pill);background:var(--paper-sea);border:1.5px solid var(--ink);font-size:15px}
.pill .x{width:16px;height:16px}
.cat{display:grid;grid-template-columns:272px minmax(0,1fr);gap:32px;padding:28px 40px 48px;align-items:start}
.fl{background:var(--surface);border:1.5px solid var(--line);border-radius:var(--radius-lg);padding:6px 18px 18px}
.fg{border-bottom:1.5px solid var(--line);padding:14px 0}
.fg:last-child{border-bottom:0}
.fg h3{display:flex;justify-content:space-between;align-items:center;font:700 16px/22px var(--font-text)}
.fg .row2{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}
.inp{min-height:44px;border:2px solid var(--line-strong);border-radius:var(--radius-md);background:var(--surface);padding:8px 10px;font-size:15px;color:var(--ink-2);display:flex;align-items:center}
.tog{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.tg{min-height:40px;padding:6px 12px;border-radius:var(--radius-sm);border:1.5px solid var(--line-strong);background:var(--surface);font-size:15px;display:inline-flex;align-items:center;gap:6px}
.tg.on{border:2px solid var(--ink);background:var(--paper-sea);font-weight:700}
.tg.on::before{content:"";width:10px;height:6px;border-left:2.5px solid var(--ink);border-bottom:2.5px solid var(--ink);transform:rotate(-45deg) translateY(-2px)}
.slider{position:relative;height:28px;margin-top:12px}
.slider::before{content:"";position:absolute;left:0;right:0;top:12px;height:4px;border-radius:4px;background:var(--line)}
.slider i{position:absolute;top:12px;height:4px;background:var(--sky);border-radius:4px}
.slider b{position:absolute;top:3px;width:22px;height:22px;border-radius:50%;background:var(--surface);border:3px solid var(--ink)}
.chk{display:flex;align-items:center;gap:10px;min-height:36px;font-size:15px} .chk span{width:20px;height:20px;border-radius:5px;border:2px solid var(--line-strong);display:grid;place-items:center} .chk.on span{background:var(--ink);border-color:var(--ink)} .chk.on span::after{content:"";width:9px;height:5px;border-left:2.5px solid var(--surface);border-bottom:2.5px solid var(--surface);transform:rotate(-45deg) translateY(-1px)}
.chk em{margin-left:auto;font-style:normal;color:var(--ink-2);font-size:14px}
.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;margin-top:20px}
.cc{background:var(--surface);border:1.5px solid var(--line);border-radius:var(--radius-lg);box-shadow:var(--shadow-sticker);overflow:hidden;display:flex;flex-direction:column}
.ph{aspect-ratio:16/9;background:linear-gradient(180deg,var(--sea),var(--paper-sea) 62%,var(--hill-2) 62%);display:grid;place-items:center;position:relative;color:var(--ink-3)}
[data-theme=dark] .ph{background:linear-gradient(180deg,#1d3048,#172338 62%,#1f3324 62%)}
.ph svg{width:64px;height:64px;opacity:.55}
.ph .pop{position:absolute;left:10px;top:10px;background:var(--surface);color:var(--ink);border:1.5px solid var(--ink);border-radius:var(--radius-pill);font:700 14px/18px var(--font-text);padding:3px 10px}
.credit{font-size:13px;line-height:18px;color:var(--ink-2);padding:4px 14px 0}
.cb{padding:8px 14px 14px;display:grid;gap:6px;flex:1}
.cb .top{display:flex;justify-content:space-between;align-items:start;gap:10px}
.cb .nm{font:700 19px/24px var(--font-display)}
.cb .pr{font:700 20px/24px var(--font-text);font-variant-numeric:tabular-nums}
.cb .pr small{display:block;font:400 14px/18px var(--font-text);color:var(--ink-2)}
.cf{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:4px;padding-top:10px;border-top:1.5px dashed var(--line)}
.cf div{display:grid;gap:0;font-size:14px;line-height:18px;color:var(--ink-2)} .cf b{font-size:17px;line-height:22px;color:var(--ink);display:flex;align-items:center;gap:4px}
.cf .ic{width:16px;height:16px}
.mcc{display:grid;grid-template-columns:116px 1fr;gap:12px;background:var(--surface);border:1.5px solid var(--line);border-radius:var(--radius-lg);padding:10px;box-shadow:var(--shadow-sticker);margin-bottom:10px}
.mcc .ph{aspect-ratio:auto;height:78px;border-radius:10px}
.mcc .ph svg{width:40px;height:40px}
.mcc .nm{font:700 17px/22px var(--font-display)} .mcc .pr{font:700 17px/22px var(--font-text)} .mcc .meta{font-size:14px;line-height:18px;color:var(--ink-2)}
.mcc .mf{grid-column:1/3;display:flex;gap:14px;flex-wrap:wrap;font-size:14px;color:var(--ink-2);border-top:1.5px dashed var(--line);padding-top:8px} .mcc .mf b{color:var(--ink);font-size:16px} .mcc .mf span{display:inline-flex;align-items:center;gap:4px} .mcc .mf .ic{width:16px;height:16px}
.sticky{position:sticky;top:0;background:var(--paper);z-index:2;padding:10px 16px;border-bottom:1.5px solid var(--line);display:flex;gap:8px}
.sticky .sel{flex:1;justify-content:space-between;white-space:nowrap}
.hscroll{display:flex;gap:8px;overflow:hidden;padding:10px 16px 0}
.sheet{position:fixed;left:0;right:0;bottom:0;top:120px;background:var(--surface);border-radius:var(--radius-lg) var(--radius-lg) 0 0;box-shadow:0 -8px 30px rgba(22,35,58,.25);padding:8px 16px 0;display:flex;flex-direction:column}
.scrim{position:fixed;inset:0;background:rgba(22,35,58,.45)}
.grab{width:44px;height:5px;border-radius:5px;background:var(--line-strong);margin:4px auto 10px}
.sheet .foot{margin-top:auto;display:flex;gap:10px;padding:12px 0 16px;border-top:1.5px solid var(--line)}
.sheet .foot .evs-btn{flex:1;justify-content:center}
.m .showall{flex-direction:column;align-items:stretch}.m .showall .evs-btn{justify-content:center}
.showall{display:flex;align-items:center;justify-content:space-between;gap:12px;background:var(--surface);border:1.5px solid var(--line);border-radius:var(--radius-lg);padding:16px;margin-top:24px}
"""

SAMPLE = '<div class="sample">sample numbers · layout only</div>'


def page(body, theme="light", desktop=False):
    return (f'<!doctype html><html data-theme="{theme}"><head><meta charset="utf-8"><style>{fonts}:root{{{fam}{sizes}}}{tokens}{bundle}{CSS}</style></head>'
            f'<body class="{"d" if desktop else "m"}">{body}{SAMPLE}</body></html>')


def header(desktop=False, on=""):
    nav = ""
    if desktop:
        nav = '<nav>' + "".join(f'<a class="{"on" if n == on else ""}">{n}</a>' for n in ("Find my shortlist", "All cars", "Compare", "Learn")) + '<a>Netherlands · €</a></nav>'
    else:
        nav = f'<nav><a>NL · €</a><a aria-label="Menu">☰</a></nav>'
    return f'<header class="hdr"><span class="logo"><b>EV</b>Shortlist</span>{nav}</header>'


def road(now, desktop=False):
    names = ["Country", "Your driving", "Budget", "Shortlist"]
    out = []
    for i, n in enumerate(names):
        if i < now:
            cls, dot = "done", TICK
        elif i == now:
            cls, dot = "now", str(i + 1) if i < 3 else "★"
        else:
            cls, dot = "", str(i + 1) if i < 3 else "★"
        if i == 3 and i != now:
            dot = '<svg class="flag" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 21V4M6 4h11l-2 4 2 4H6" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/></svg>'
        out.append(f'<li class="stop {cls}"><span class="dot">{dot}</span><span>{n}</span></li>')
    pct = [0, 34, 67, 100][now]
    return f'<ol class="road" aria-label="Step {min(now+1,3)} of 3"><span class="done-line" style="width:calc({pct}% - {28 if pct else 0}px)"></span>{"".join(out)}</ol>'


def opt(icon, label, hint, on=False):
    return (f'<div class="opt{" on" if on else ""}{"" if icon else " noic"}">{sym(icon) if icon else ""}<span><b>{label}</b>'
            f'{f"<small>{hint}</small>" if hint else ""}</span>{TICK if on else SLOT}</div>')


def trail(items):
    return '<div class="trail" aria-label="Your answers">' + "".join(f'<span class="ans">{a}{PEN}</span>' for a in items) + '</div>'


# ── sample shortlist (names from data/seed/top40.yaml; numbers are SAMPLE) ──
CARS = [
    ("Kia e-Niro 64 kWh", "2019–2021", "€19–23k", "330", "190", "Long winter trips with spare range, €2k under budget"),
    ("Hyundai Kona Electric 64 kWh", "2019–2022", "€18–22k", "320", "180", "Same battery as the Niro, a little smaller inside"),
    ("Tesla Model 3 Long Range", "2019–2021", "€23–25k", "360", "300", "Fastest charging on the list, top of your budget"),
    ("Volkswagen ID.3 Pro S 77 kWh", "2021–2023", "€22–25k", "350", "240", "Big battery for the money, roomy for its size"),
    ("Skoda Enyaq iV 80", "2021–2022", "€24–25k", "340", "250", "Largest boot here, good for holidays"),
]
MORE = [("MG4 Long Range", "€19–22k", "300"), ("Kia EV6 RWD 77 kWh", "€25k", "370"), ("Polestar 2 Long Range", "€24–25k", "330"),
        ("Hyundai Ioniq 5 73 kWh", "€25k", "330"), ("Renault Megane E-Tech EV60", "€17–20k", "270")]


def m_row(i, c, on=False):
    nm, yrs, pr, wr, dc, why = c
    return (f'<li class="row"><span class="thumb" style="width:72px;height:48px;position:relative">{sym("car")}<span class="rk" style="position:absolute;left:-8px;top:-8px;width:26px;height:26px;font-size:14px;margin:0">{i}</span></span>'
            f'<span><span class="nm">{nm}</span><br><span class="yrs">{yrs} · used</span></span>'
            f'<span class="addbtn{" on" if on else ""}" aria-label="Add to my shortlist">{TICK if on else STAR_ADD}</span>'
            f'<span class="facts" style="grid-column:1/4"><span class="price"><b>{pr}</b></span><span>{sym("winter")}<b>{wr} km</b> winter</span>'
            f'<span>{sym("fast-charge")}<b>+{dc} km</b> in 20 min</span></span><p class="why" style="grid-column:1/4">{why}</p><p class="credit" style="grid-column:1/4;padding:2px 0 0">Photo: maker press photo · credit here</p></li>')


# ═════════ T-132 frames ═════════

def t132_m_country(theme="light"):
    opts = "".join(opt(None, n, None, n == "Netherlands") for n in ("Netherlands", "Belgium", "Germany", "France", "United Kingdom", "Spain", "Italy"))
    scene = (DS / "assets/Illustrations/scene-village-hero-day.svg").as_uri()
    return page(f"""{header()}<section class="herocard evs-tex evs-tex--map evs-tex--no-sun">
<h1 style="font:800 38px/42px var(--font-display);letter-spacing:-.6px">Used EVs got good.</h1>
<p style="margin-top:8px;color:var(--ink-2)">Three questions. Then a top 10 for the way you drive, with prices where you live.</p>
<img class="scene" src="{scene}" alt="" style="width:200px;margin-top:12px">
</section>
<div class="wrap"><div class="panel">{road(0)}
<p class="qcount" style="margin-top:18px">Step 1 of 3</p><h2 class="q">Where are you buying?</h2>
<p class="qhelp">Sets prices, currency and the listing sites.</p>
<div class="opts two">{opts}</div>
<p class="muted" style="margin-top:14px">Tap one to go on. You can change it later.</p></div></div>""", theme)


def t132_m_question(theme="light"):
    opts = (opt(None, "Never", "We take the train, rent or borrow") + opt(None, "A few times a year", "Holidays, family visits", True)
            + opt(None, "About once a month", None) + opt(None, "Several times a month", "Work trips, weekends away"))
    return page(f"""{header()}<div class="wrap"><div class="panel">{road(1)}
<div style="margin-top:16px">{trail(["Netherlands", "Our main car"])}</div>
<p class="qcount" style="margin-top:18px">Step 2 of 3 · question 2 of 4</p>
<h2 class="q">How often do you drive 300 km or more in one go?</h2>
<div class="opts">{opts}</div>
<div class="qnav"><a class="lnk">{BACK}Back</a><span class="muted">Tap an answer to go on</span></div></div></div>""", theme)


def t132_m_budget(theme="light"):
    quick = "".join(f'<span class="qb{" on" if q == "€25k" else ""}">{q}</span>' for q in ("€15k", "€20k", "€25k", "€30k", "€40k", "No limit"))
    return page(f"""{header()}<div class="wrap"><div class="panel">{road(2)}
<div style="margin-top:16px">{trail(["Netherlands", "Road-tripper"])}</div>
<p class="qcount" style="margin-top:18px">Step 3 of 3</p><h2 class="q">What's your budget?</h2>
<p class="qhelp">The most you want to spend.</p>
<div class="money"><span>€</span><input value="25.000" aria-label="Budget in euro"></div>
<div class="quick">{quick}</div>
<div class="month">{sym("monthly-cost")}<span><b>≈ €410 a month</b><br>Rough loan estimate: 10 % down, 60 months, 6.9 % a year. Not an offer. <a class="lnk" style="min-height:0;font-size:15px">Change</a></span></div>
<p class="lbl">New or used</p><div class="seg"><span class="on">Used</span><span>New</span><span>Either</span></div>
<button class="evs-btn evs-btn--primary cta">Show my top 10</button>
<div class="qnav" style="margin-top:8px"><a class="lnk">{BACK}Back</a><a class="lnk">More filters (optional)</a></div></div></div>""", theme)


def t132_m_results(theme="light"):
    rows = "".join(m_row(i + 1, c, on=i == 0) for i, c in enumerate(CARS))
    more = "".join(f'<li class="mini"><span class="n">{i + 6}</span><span>{n}</span><span class="p">{p}</span><span class="w">{sym("winter")}{w} km</span></li>' for i, (n, p, w) in enumerate(MORE))
    return page(f"""{header()}<div class="wrap">
{road(3)}
<div class="summary" style="margin-top:16px"><span style="flex:1"><span class="muted">Your profile</span><br><span class="who">Road-tripper</span><br><span class="muted">Netherlands · used · up to €25,000</span></span><a class="lnk">{PEN}Edit</a></div>
<div class="actions"><span class="evs-btn evs-btn--secondary" style="min-height:44px;padding:8px 14px">{sym("filter")}Refine · 0</span><span class="evs-btn evs-btn--secondary" style="min-height:44px;padding:8px 14px">{sym("share")}Share</span></div>
<section class="sl"><div class="slh"><h2>Your shortlist</h2><span class="muted">top 5 of 41 that fit</span></div><ol>{rows}</ol></section>
<section class="more"><h2>Also worth a look</h2><ol>{more}</ol>
<p class="muted" style="margin:10px 4px">Winter range is our real-world estimate at 0 °C. Prices: used, in the Netherlands.</p></section>
<div class="showall"><span><b>Browse every EV</b><br><span class="muted">Sorted by what's popular</span></span><a class="evs-btn evs-btn--secondary">Show all cars{CHEV}</a></div>
</div>""", theme)


def t132_d_question(theme="light"):
    opts = (opt("home-charging", "At home", "Driveway, garage or a wallbox", True) + opt("charge-stop", "At work", "A charger at the office or depot")
            + opt("plug-type2", "Only at public chargers", "Street posts, supermarkets, fast chargers"))
    scene = (DS / f"assets/Illustrations/scene-village-{'hero-day' if theme == 'light' else 'night'}.svg").as_uri()
    return page(f"""{header(True, "Find my shortlist")}<section class="dhero evs-tex evs-tex--map evs-tex--no-sun"><div>
<h1>Used EVs got good.</h1><p style="margin:10px 0 24px;font-size:19px;line-height:30px;color:var(--ink-2);max-width:40ch">Three questions. Then a top 10 for the way you drive, with prices where you live.</p>
<div class="dpanel">{road(1)}<div style="margin-top:20px">{trail(["Netherlands", "Our main car", "A few long trips a year"])}</div>
<p class="qcount" style="margin-top:20px">Step 2 of 3 · question 3 of 4</p><h2 class="q">Where will you charge?</h2>
<p class="qhelp">Pick where most of your charging happens.</p><div class="opts">{opts}</div>
<div class="qnav"><a class="lnk">{BACK}Back</a><span class="muted">Tap an answer to go on</span></div></div></div>
<div style="padding-top:40px"><img class="scene" src="{scene}" alt="" style="width:380px"></div></section>""", theme, True)


def t132_d_results(theme="light"):
    def tr(i, c, on=False):
        nm, yrs, pr, wr, dc, why = c
        return (f'<tr><td><span class="rk">{i}</span></td><td><span class="carc"><span class="thumb">{sym("car")}</span><span><span class="nm">{nm}</span><span class="sub">{yrs} · used</span><span class="sub" style="font-size:12px">Photo: press · credit</span></span></span></td>'
                f'<td class="r"><span class="num">{pr}</span></td><td class="r"><span class="num">{wr} km</span></td><td class="r"><span class="num">+{dc} km</span></td>'
                f'<td><span class="whyc">{why}</span></td><td><span class="addbtn{" on" if on else ""}">{TICK if on else STAR_ADD}</span></td></tr>')
    head = (f'<thead><tr><th>#</th><th>Car</th><th class="r">Used price</th><th class="r">{sym("winter")} Winter range</th>'
            f'<th class="r">{sym("fast-charge")} In 20 min</th><th>Why it fits</th><th><span class="sr">Shortlist</span></th></tr></thead>')
    rows = "".join(tr(i + 1, c, i == 0) for i, c in enumerate(CARS))
    more = "".join(f'<tr><td><span class="n muted" style="font-weight:700">{i + 6}</span></td><td>{n}</td><td class="r"><span class="num">{p}</span></td><td class="r"><span class="num">{w} km</span></td><td class="r muted">…</td><td class="muted">Open for details</td><td><span class="addbtn">{STAR_ADD}</span></td></tr>' for i, (n, p, w) in enumerate(MORE))
    side = "".join(f'<div class="sa"><small>{q}</small>{PEN}<b>{a}</b></div>' for q, a in (("Country", "Netherlands"), ("This car will be", "Our main car"), ("Long trips", "A few times a year"), ("Charging", "At home"), ("Where you live", "Town or suburb"), ("Budget", "Up to €25,000 · used")))
    return page(f"""{header(True, "Find my shortlist")}<div class="dres"><aside class="side">
<span class="muted">Your profile</span><h2>Road-tripper</h2><p class="muted" style="margin:4px 0 8px">Main car that also does the holidays: fast charging and winter range first.</p>{side}
<p class="lbl" style="margin-top:14px">Set by your profile</p><div class="tog"><span class="tg on">+150 km in 20 min</span><span class="tg on">300+ km real range</span></div>
<a class="lnk" style="margin-top:6px">{sym("filter")}More filters (optional)</a></aside>
<main><div class="ctop"><div><h1 style="font:800 40px/44px var(--font-display);letter-spacing:-.6px">Your top 10</h1><p class="muted">41 models fit your answers · used prices in the Netherlands</p></div>
<div class="actions" style="margin:0"><span class="evs-btn evs-btn--secondary">{sym("share")}Share this list</span><span class="evs-btn evs-btn--secondary">{sym("compare")}Compare ticked</span></div></div>
<div class="slwrap" style="margin-top:20px"><div class="slh"><h2 style="font:700 22px/28px var(--font-display)">Your shortlist</h2><span class="muted">the top 5</span></div><table class="tbl">{head}<tbody>{rows}</tbody></table></div>
<h2 style="font:700 20px/26px var(--font-display);margin:24px 16px 0">Also worth a look</h2><div style="padding:0 16px"><table class="tbl small"><tbody>{more}</tbody></table></div>
<div class="showall"><span><b>Browse every EV we know</b><br><span class="muted">Filters and sorting, most popular first</span></span><a class="evs-btn evs-btn--secondary">Show all cars{CHEV}</a></div>
</main></div>""", theme, True)


# ═════════ T-130 frames ═════════
CAT = [("Tesla Model 3", "2019–2023", "€17–32k", "300–420", "+250–300", "1"), ("Kia e-Niro / Niro EV", "2019–2024", "€15–29k", "250–350", "+150–190", "2"),
       ("Volkswagen ID.3", "2020–2024", "€15–30k", "260–400", "+180–240", "3"), ("Hyundai Kona Electric", "2018–2023", "€14–26k", "220–330", "+140–180", "4"),
       ("Renault Zoe", "2013–2022", "€6–16k", "150–280", "+60–110", "5"), ("Peugeot e-208", "2020–2024", "€12–24k", "220–300", "+150–180", "6")]


def cc(c):
    nm, yrs, pr, wr, dc, pop = c
    return (f'<article class="cc"><div class="ph">{sym("car")}<span class="pop">#{pop} popular</span></div><p class="credit">Photo: maker press photo · credit here</p>'
            f'<div class="cb"><div class="top"><span><span class="nm">{nm}</span><br><span class="yrs">{yrs}</span></span><span class="addbtn">{STAR_ADD}</span></div>'
            f'<div class="pr">{pr}<small>used, in the Netherlands</small></div>'
            f'<div class="cf"><div><b>{sym("winter")}{wr.split("–")[0]}</b>km winter</div><div><b>{sym("summer")}{wr.split("–")[1]}</b>km summer</div><div><b>{sym("fast-charge")}{dc.split("–")[1]}</b>km / 20 min</div></div></div></article>')


def filters():
    return f"""<div class="fl"><div class="fg"><h3>Used price {CARET}</h3><div class="row2"><span class="inp">€ min</span><span class="inp">€ 25.000</span></div></div>
<div class="fg"><h3>Real winter range {CARET}</h3><div class="slider"><i style="left:0;width:45%"></i><b style="left:42%"></b></div><p class="muted">at least 250 km</p></div>
<div class="fg"><h3>Body type {CARET}</h3><div class="tog"><span class="tg">Small</span><span class="tg on">Hatchback</span><span class="tg on">SUV</span><span class="tg">Estate</span><span class="tg">Saloon</span><span class="tg">Van / MPV</span></div></div>
<div class="fg"><h3>Fast charging {CARET}</h3><div class="tog"><span class="tg">+100 km</span><span class="tg">+150 km</span><span class="tg">+200 km</span></div><p class="muted" style="margin-top:6px">added in 20 min</p></div>
<div class="fg"><h3>Build year {CARET}</h3><div class="row2"><span class="inp">From 2018</span><span class="inp">To any</span></div></div>
<div class="fg"><h3>Seats · battery · towing {CARET}</h3></div>
<div class="fg"><h3>Brands {CARET}</h3><span class="inp" style="margin-top:10px">{sym("search")}&nbsp;Find a brand</span>
<div style="margin-top:6px"><div class="chk"><span></span>Hyundai<em>9</em></div><div class="chk on"><span></span>Kia<em>8</em></div><div class="chk"><span></span>Renault<em>11</em></div><div class="chk"><span></span>Tesla<em>6</em></div><a class="lnk" style="font-size:15px">Show all 38</a></div></div></div>"""


def t130_d(theme="light"):
    pills = "".join(f'<span class="pill">{p}{X}</span>' for p in ("Up to €25,000", "250+ km winter", "Hatchback", "SUV"))
    return page(f"""{header(True, "All cars")}<div class="cat"><aside><div class="ctop" style="margin-bottom:12px"><h2 style="font:700 20px/26px var(--font-display)">Filters</h2><a class="lnk" style="font-size:15px">Clear all</a></div>{filters()}</aside>
<main><div class="ctop"><div><h1>All electric cars</h1><p class="muted">214 models · 87 match your filters · used prices in the Netherlands</p></div>
<div style="display:flex;gap:10px"><div class="evs-switch"><button aria-pressed="true">Simple</button><button>Detailed</button><button>Nerd</button></div><div class="evs-switch"><button aria-pressed="true">Cards</button><button>Table</button></div></div></div>
<div class="bar">{pills}<a class="lnk" style="font-size:15px;min-height:36px">Clear</a><span style="margin-left:auto" class="sel"><small>Sort</small> Most popular {CARET}</span></div>
<p class="muted" style="margin-top:10px">Most popular = cars on the road in the Netherlands and the UK, plus our editors' picks. <a class="lnk" style="min-height:0;font-size:15px">How we rank</a></p>
<div class="grid">{"".join(cc(c) for c in CAT)}</div></main></div>""", theme, True)


def mcc(c):
    nm, yrs, pr, wr, dc, pop = c
    return (f'<article class="mcc"><div class="ph">{sym("car")}</div><div><span class="nm">{nm}</span><br><span class="meta">{yrs} · #{pop} popular</span><br>'
            f'<span class="pr">{pr}</span> <span class="meta">used</span></div>'
            f'<div class="mf"><span>{sym("winter")}<b>{wr.split("–")[0]}–{wr.split("–")[1]}</b> km</span><span>{sym("fast-charge")}<b>{dc.split("–")[1]}</b> km/20 min</span><span class="addbtn" style="margin-left:auto;width:40px;height:40px">{STAR_ADD}</span></div></article>')


def t130_m(theme="light"):
    pills = "".join(f'<span class="pill" style="white-space:nowrap">{p}{X}</span>' for p in ("Up to €25k", "250+ km winter", "SUV"))
    return page(f"""{header()}<div style="padding:16px 16px 4px"><h1 style="font:800 30px/34px var(--font-display);letter-spacing:-.4px">All electric cars</h1><p class="muted">87 of 214 match · used prices in the Netherlands</p></div>
<div class="sticky"><span class="sel">{sym("filter")} Filters · 3</span><span class="sel" style="white-space:nowrap">Popular first {CARET}</span></div>
<div class="hscroll">{pills}</div><div style="padding:12px 16px">{"".join(mcc(c) for c in CAT[:5])}</div>""", theme)


def t130_m_sheet(theme="light"):
    return page(f"""{header()}<div style="padding:16px"><h1 style="font:800 30px/34px var(--font-display)">All electric cars</h1></div><div class="scrim"></div>
<div class="sheet"><div class="grab"></div><div class="ctop" style="align-items:center"><h2 style="font:700 22px/28px var(--font-display)">Filters</h2><a class="lnk" style="font-size:15px">Clear all</a></div>
<div style="overflow:hidden;flex:1;margin:0 -2px">{filters().replace('class="fl"', 'class="fl" style="border:0;padding:0 2px"')}</div>
<div class="foot"><span class="evs-btn evs-btn--primary">Show 87 cars</span></div></div>""", theme)


FRAMES = {
    "t132-m1-country": (t132_m_country, 360), "t132-m2-question": (t132_m_question, 360), "t132-m3-budget": (t132_m_budget, 360),
    "t132-m4-results": (t132_m_results, 360), "t132-d1-question": (t132_d_question, 1280), "t132-d2-results": (t132_d_results, 1280),
    "t130-d1-catalogue": (t130_d, 1280), "t130-m1-catalogue": (t130_m, 360), "t130-m2-filters": (t130_m_sheet, 360),
}

if __name__ == "__main__":
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for name, (fn, w) in FRAMES.items():
            for theme in ("light", "dark"):
                html = fn(theme)
                f = OUT / f"{name}-{theme}.html"
                f.write_text(html)
                pg = b.new_page(viewport={"width": w, "height": 760 if w == 360 else 900}, device_scale_factor=2 if w == 360 else 1)
                pg.goto(f.as_uri())
                pg.wait_for_timeout(250)
                full = "sheet" not in fn.__name__
                pg.screenshot(path=str(OUT / f"{name}-{theme}.png"), full_page=full)
                pg.close()
                print("rendered", name, theme)
        b.close()
