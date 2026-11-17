"""Parallax landing prototype (one HTML page) using depth.py layers + the design-system bundle."""
import json, re, sys
sys.path.insert(0, "/home/claude/sp")
from depth import village_layers, city_layers
from kit import DAY, NIGHT
R = "/home/claude/ev-finder/docs/design"
t = json.load(open(f"{R}/tokens.json"))
def v(x): return re.sub(r"\{([^}]+)\}", r"var(--\1)", x)
css = ":root,[data-theme=light]{" + "".join(f"--{k['name']}:{v(k['value']['light'] if isinstance(k['value'], dict) else k['value'])};" for k in t['color']['tokens'] + t['shadow']['tokens']) + "}"
css += "[data-theme=dark]{" + "".join(f"--{k['name']}:{v(k['value']['dark'])};" for k in t['color']['tokens'] + t['shadow']['tokens'] if isinstance(k['value'], dict)) + "}"
css += ":root{" + "".join(f"--{k['name']}:{k['value']};" for f in ('spacing', 'radius', 'size') for k in t[f]['tokens']) + "".join(f"--font-{a}:{b};" for a, b in t['type']['families'].items()) + "}"
bundle = open(f"{R}/components/bundle.css").read()
logo_l = open(f"{R}/assets/Logo/lockup-light.svg").read()
logo_d = open(f"{R}/assets/Logo/lockup-dark.svg").read()
logo_l = re.sub(r'width="\d+" height="\d+"', 'height="30" width="164"', logo_l, 1).replace("<svg", '<svg class="logo logo--day" role="img" aria-label="EV Shortlist"', 1)
logo_d = re.sub(r'width="\d+" height="\d+"', 'height="30" width="164"', logo_d, 1).replace("<svg", '<svg class="logo logo--night" role="img" aria-label="EV Shortlist"', 1)

def scene(layers_fn, kind, uid):
    out = ""
    for theme, cls, night in [(DAY, "day", False), (NIGHT, "night", True)]:
        out += f'<div class="scene scene--{cls}" data-parallax aria-hidden="true">'
        for name, depth, svg in layers_fn(theme, True, night, uid + cls):
            out += f'<svg class="layer layer--{name}" data-depth="{depth}" viewBox="0 0 390 460" preserveAspectRatio="xMidYMid slice">{svg}</svg>'
        out += '</div>'
    return out

PAGE = f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>EV Shortlist — parallax hero prototype</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Bitter:wght@700;800&family=Patrick+Hand&display=swap">
<style>
{css}
:root{{--font-display:"Bitter",Georgia,serif;--font-text:"Atkinson Hyperlegible",system-ui,sans-serif;--font-note:"Patrick Hand",cursive}}
{bundle}
html{{background:var(--paper)}} body{{margin:0;background:var(--paper);color:var(--ink);font:400 17px/1.55 var(--font-text)}}
.bar{{position:sticky;top:0;z-index:20;display:flex;justify-content:space-between;align-items:center;padding:12px 20px;background:color-mix(in srgb,var(--paper) 88%,transparent);backdrop-filter:blur(8px);border-bottom:1.5px solid var(--line)}}
.logo--night{{display:none}} [data-theme=dark] .logo--day{{display:none}} [data-theme=dark] .logo--night{{display:block}}
.toggle{{min-height:44px;padding:0 14px;border-radius:10px;border:1.5px solid var(--line-strong);background:var(--paper);color:var(--ink);font:700 15px var(--font-text);cursor:pointer}}
.wrap{{max-width:1240px;margin:0 auto;padding:0 20px}}
.hero{{display:grid;gap:28px;align-items:center;padding:36px 0 40px}}
@media(min-width:900px){{.hero{{grid-template-columns:1fr 1fr;padding:64px 0}}}}
h1{{font:800 clamp(40px,7vw,64px)/1.04 var(--font-display);margin:0 0 14px;letter-spacing:-.5px}}
.lead{{font-size:19px;color:var(--ink-2);margin:0 0 24px;max-width:34ch}}
.step{{font:700 14px/20px var(--font-text);color:var(--ink-2);letter-spacing:.3px;text-transform:uppercase;margin:0 0 6px}}
.form{{display:flex;gap:10px;flex-wrap:wrap;max-width:440px}} .form label{{width:100%;font-weight:700}}
.form select{{flex:1;min-width:0;min-height:48px;padding:10px 12px;border:1.5px solid var(--line-strong);border-radius:6px;background:var(--paper);color:var(--ink);font:400 17px var(--font-text)}}
.btn{{min-height:48px;padding:0 20px;border:0;border-radius:10px;background:var(--action);color:var(--on-action);font:700 17px var(--font-text);cursor:pointer}}
.stage{{position:relative;aspect-ratio:390/460;width:100%;max-width:520px;justify-self:center;border-radius:24px;overflow:hidden;box-shadow:var(--shadow-sticker);isolation:isolate}}
.scene{{position:absolute;inset:0}} .scene--night{{display:none}} [data-theme=dark] .scene--day{{display:none}} [data-theme=dark] .scene--night{{display:block}}
.layer{{position:absolute;inset:0;width:100%;height:100%;overflow:visible;will-change:transform}}
.band{{border-radius:24px;margin:16px 0}}
.band h2{{font:800 30px/1.15 var(--font-display);margin:0 0 18px}}
.steps{{display:grid;gap:14px;max-width:62ch}} @media(min-width:900px){{.steps{{grid-template-columns:repeat(3,1fr);max-width:none}}}}
.card{{background:var(--paper);border:1.5px solid var(--line);border-radius:18px;padding:18px}}
.card b{{display:block;font:800 20px var(--font-display);margin-bottom:4px}} .card span{{color:var(--ink-2)}}
.pair{{margin:32px 0 8px}} .pair h2{{font:800 30px/1.15 var(--font-display);margin:0 0 16px}}
.pair-grid{{display:grid;gap:20px}} @media(min-width:900px){{.pair-grid{{grid-template-columns:1fr 1fr}}}}
.pair figure{{margin:0}} .pair figcaption{{margin-top:8px;color:var(--ink-2)}}
.note{{font:400 20px var(--font-note);color:var(--ink-2);margin:6px 0 40px}}
.foot{{padding:28px 20px 48px;color:var(--ink-2);font-size:15px}}
@media (prefers-reduced-motion: reduce){{.layer{{transform:none!important}}}}
</style>
</head>
<body class="evs">
<header class="bar">{logo_l}{logo_d}<button class="toggle" id="theme" type="button" aria-pressed="false">Night drive</button></header>
<main class="wrap">
<section class="hero">
<div>
<h1>Used EVs got good.</h1>
<p class="lead">Electric cars you can actually afford, with real range. Three questions, and you have your shortlist.</p>
<p class="step">Step 1 of 3</p>
<form class="form" onsubmit="event.preventDefault()"><label for="c">Where do you live?</label><select id="c"><option>Netherlands</option><option>Germany</option><option>France</option><option>Belgium</option><option>United Kingdom</option></select><button class="btn">Next</button></form>
</div>
<div class="stage">{scene(village_layers, "village", "h")}</div>
</section>
<section class="band evs-tex evs-tex--map" style="background-color:var(--paper-sea);padding-top:32px;padding-left:24px">
<h2>How it works</h2>
<div class="steps"><div class="card"><b>1. Tell us a little</b><span>Your country, how you drive, your budget.</span></div><div class="card"><b>2. Get ten good cars</b><span>Ranked on real range, running costs and used prices.</span></div><div class="card"><b>3. Keep your five</b><span>Your shortlist, ready to compare and test-drive.</span></div></div>
</section>
<section class="pair"><h2>Village or city, it fits</h2><div class="pair-grid"><figure><div class="stage">{scene(village_layers, "village", "p")}</div><figcaption>Countryside: your roof charges the car.</figcaption></figure><figure><div class="stage">{scene(city_layers, "city", "w")}</div><figcaption>City: a lamp-post charger round the corner.</figcaption></figure></div></section>
<p class="note">Scroll slowly, and on a computer move your mouse over the pictures: the layers drift at different speeds.</p>
</main>
<footer class="foot wrap">Prototype for Menno · EV Shortlist design system v6 · parallax turns off when your device asks for reduced motion.</footer>
<script>
(function(){{
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var scenes = [].slice.call(document.querySelectorAll('[data-parallax]'));
  var px = 0, py = 0, ticking = false;
  var AMP = 90;   // px of travel per unit of depth across one screen of scroll
  var TILT = 16;  // px of pointer drift per unit of depth (desktop only)
  function frame(){{
    ticking = false;
    if (reduce.matches) return;
    var vh = window.innerHeight;
    scenes.forEach(function(s){{
      if (s.offsetParent === null) return;               // hidden theme
      var r = s.getBoundingClientRect();
      if (r.bottom < -100 || r.top > vh + 100) return;   // off screen
      var p = (r.top + r.height / 2 - vh / 2) / vh;       // -1..1 around the centre
      s.querySelectorAll('.layer').forEach(function(l){{
        var d = parseFloat(l.dataset.depth);
        l.style.transform = 'translate3d(' + (-px * d * TILT).toFixed(1) + 'px,' + (p * d * AMP - py * d * TILT * .6).toFixed(1) + 'px,0)';
      }});
    }});
  }}
  function req(){{ if (!ticking) {{ ticking = true; requestAnimationFrame(frame); }} }}
  addEventListener('scroll', req, {{passive: true}});
  addEventListener('resize', req);
  if (matchMedia('(pointer: fine)').matches) addEventListener('pointermove', function(e){{
    px = e.clientX / innerWidth - .5; py = e.clientY / innerHeight - .5; req();
  }}, {{passive: true}});
  reduce.addEventListener && reduce.addEventListener('change', function(){{ scenes.forEach(function(s){{ s.querySelectorAll('.layer').forEach(function(l){{ l.style.transform = ''; }}); }}); req(); }});
  var b = document.getElementById('theme');
  b.addEventListener('click', function(){{
    var dark = document.documentElement.dataset.theme !== 'dark';
    document.documentElement.dataset.theme = dark ? 'dark' : 'light';
    b.textContent = dark ? 'Day trip' : 'Night drive'; b.setAttribute('aria-pressed', dark); req();
  }});
  req();
}})();
</script>
</body>
</html>'''
open("/home/claude/sp/out/parallax-proto.html", "w").write(PAGE)
print(len(PAGE))
