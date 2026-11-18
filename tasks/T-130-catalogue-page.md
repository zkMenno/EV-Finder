# T-130 Catalogue page with popularity sort; landing loses the full list
Role: builder   Lane: WS2 (+ UX layout): apps/web/   Wave: launch (staging feedback 2026-11-17)
Status: review (WS2, 2026-11-18: part 1 merged #117; part 2 PR on branch t-130-catalogue-visual)

## Goal
A "Show all cars" button on the landing leads to a catalogue page like ev-database.org, sorted by popularity by default.

## Acceptance criteria
- [ ] Landing page no longer renders the full car list; a "Show all cars" button links to the catalogue page
- [ ] Catalogue page: Explore filters, default sort = popularity, user sorts by price, range, battery, charging speed, year; sort and filters in the URL
- [ ] Popularity = registration counts from `data/seed/top40.yaml` (RDW, DfT, KBA, EEA) blended with Menno's picks (Decision 038); the blend weights live in config, not code, and the pipeline publishes the score in the release (ask WS1 via INBOX if a field is needed)
- [ ] UX gives the layout first (workstreams/UX INBOX); 360 and 1280 px screenshots, light and dark
- [ ] Verify skill for the lane; evidence pack in the PR; `Verified:` on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes

## Inputs
docs/spec/feedback-2026-11-17-staging.md item 1; Decision 038

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes
WS2, 2026-11-18 (session_01JuyZEUuCTBUyPNJ74C3iRD).

**Part 1 (this PR): the working page.**
- `/{country}/{lang}/cars` = Explore, default sort Most popular, default view cards. Landing: no list, "Show all cars" box. Header link "All cars".
- Popularity is per generation: `score = 100 × (0.8 × generation share ÷ top generation share + 0.2 × owner pick)`. Registrations: `data/seed/top40.yaml` `score_pct` is per **model** (NL RDW first registered 2018–2024 + UK DfT fleet, averaged by WS1's top40 method); it is split over the model's generations by the release's RDW `registered_count_nl` per generation (no count while siblings have one = no share; no count for any generation = even split). Fixed after the fresh review: before, every generation got the full model share, so Model 3 gen1 and Highland tied (#1/#2). Release 2 now: Model 3 gen1 #1, Model Y gen1 #2, Enyaq #3, ID.3 #4 … Highland #6; 82 of 93 generations ranked. Picks: best verdict from `menno-picks.yaml` (shortlist 1, consider 0.6, fallback 0.3, favourite +0.2, cap 1). Weights in `config/popularity.yaml` (reversible default, WS2's pick: registrations dominate, picks only nudge). Unknown cars: no score, last, no tag. Nerd level shows score, sources, licences and date under the tag; "How we rank" names RDW (CC0) and DfT (OGL v3).
- Reversible default: the web builds the score from the seed file at build time, because the release has no popularity field yet. Asked WS1 for `popularity` per generation in the release (INBOX); `catalogue.popularity()` is the single switch point.
- Old landing Explore links (with `view` or `sort`; the hero never writes either) 307 to `/cars` with the same query, hero answers included.
- Sort menu offers the design's six orders. "Price" sorts by **new** price (that's the only price on every row); label says so.

**Not done yet (part 2, needs no new data):** the design's visual layer: filter sidebar groups (used price, winter range slider, body tiles, brands with search + counts), phone "Filters · n" bottom sheet + sticky bar, removable filter pills + Clear, "214 models · 87 match" count line, one card per generation with used price band and the three facts (winter km, summer km, km in 20 min). Photo + credit on cards is T-135 (needs WS1's image fields).

**Known gap:** resetting the sort to "unsorted" via a table header leaves no `sort` in the URL, so a reload shows Most popular again. Small; fix with part 2 if the table keeps the unsorted state.

**Part 2 (branch t-130-catalogue-visual): the design's visual layer.** WS2, 2026-11-18 (session_01JuyZEW7knztpvwmHJjJ3mb).
- Sidebar (272 px) with collapsible groups in design order: used price (min/max), real winter range (slider, 0 = any), body tiles, fast charging (+100/+150/+200 km in 20 min → `dc`), build years, seats · battery · towing, brands (search, counts = generations per brand, top 6 + "Show all"), and "More filters" (closed unless one is on) with everything the old panel had (new price, real range, era, 400 V, 100 %, and at Detailed+ segment, voltage, chemistry, cooling, DC number, boot, length, AC, voltage slider).
- Phone: sticky bar with "Filters · n" + the sort menu; the same panel opens as a bottom sheet (role dialog when open, focus to Close, Escape and backdrop close, focus back to the button, page doesn't scroll behind) with a "Show n cars" button. One DOM for both, so every filter id exists once.
- Pills: one per active filter (one per value for lists), each removes itself; "Clear" resets. Count line "N of M models match · used prices in <country>" (models = generations).
- Cards: one per generation (`src/lib/generation-cards.ts`), in the order of the generation's best-placed variant, so every sort carries over. Card = "#n popular" tag, make + model (links to the generation page), generation + years, used price band (lower quartile of the cheapest band to upper quartile of the dearest, within the visitor's used-price and build-year filters; "Estimate…" note when any band is our model; Nerd adds the source + date), three facts through `<Num>` (winter km, summer km, km in 20 min; "min–max" when variants differ, provenance of the highest), Detailed adds battery + new price, "n versions" link. Heart + compare act on the generation's first matching variant (named in the button label).
- New state: `umin`/`umax` (used price where the visitor lives: some build year's typical price inside the range; no bands = no match) and `winter` (`real_range_winter_km`, now in the client rows with provenance). Sort menu: Most popular, used price (cheapest typical price), winter range, battery, charging speed, year (design). `price` and `range` stay valid sort keys for old links and table headers.
- Client catalogue grew 202 → 222 KB gzip (winter field + provenance); still under 300.
- Reversible defaults: body tiles are the schema's 8 bodies (the design's "Small" isn't a body; segment stays under More filters). Photos wait for T-135. The level/view and price-mode toggles stay above the list on phones (design has none there); if that's too much scrolling, move them into the sheet.

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts. -->
**fresh reviewer (subagent), 2026-11-18, head `03d8220`, REVIEW.md read from origin/main (f34ac1a). Verdict: FAIL (1 must-fix).**
Part 1 judged; part 2 (design's visual layer) out of scope as agreed.

| Item | Verdict | Evidence |
|---|---|---|
| R0 CI on head | PASS | `actions/runs?branch=t-130-catalogue-page`: CI + Images on 03d8220 `success`; check-runs web, e2e, schema, pipeline, data-qa, gate-guard, repo-checks, ci-ok all `success` |
| R1 conflict markers | PASS | `git grep -nE '^(<{7}\|={7}\|>{7})( \|$)' 03d8220` → no hits |
| R2 evidence pack | PASS | PR body has commands + numbers; reproduced locally: vitest 51 files / 435 tests pass; lint + typecheck clean; `APP_URL=https://ev.example.com pnpm build` exit 0; budget landing 163.1 KB, /cars 163.2 KB (< 200), client catalogue 202.3 KB (< 300) "Perf budget: OK"; Playwright catalogue + suggested + smoke 14/14. `Verified:` on all 3 commits |
| R3 own checks | PASS | e2e changes are path moves to `/cars` (+ `view=table` where the test needs the table); `Test-change:` lines in 0192437 and 03d8220; the replaced suggested test is explained (hero and Explore no longer on one page); no added `.skip(`/`.only(`/`test.fixme`; budget.mjs keeps 200/300 KB and now measures both pages |
| R4 launch/deploy | n/a | no `data/seed/**`, `data/manual/**`, `derive/**` change; not a deploy PR |
| D3 derived score | **FAIL, must-fix** | See finding 1. Otherwise: one implementation (`src/lib/popularity.ts`, used by catalogue.ts, the data route and budget.mjs); weights only in `config/popularity.yaml`; hand check on release 2: Model 3 = 100×0.8×8.263/8.263 = 80 ✓, Model Y gen1 = 100×(0.8×6.914/8.263 + 0.2×0.6) = 78.9 ✓ |
| D6 strings | PASS | all 24 new keys present in en/nl/de/fr/es/it (script diff, 0 missing); i18n.test green; `catalogue.`/`landing.` server-only, `sort.`/`card.` in the client dict. Key-count gap en 772 vs nl 760 is pre-existing on main |
| D7 new number on a page | FAIL, should-fix | "#n popular" tag (Explore.tsx:1238) has no source/date/licence in Nerd mode; "How we rank" names RDW + DfT and the date but no licence (RDW CC0-1.0, DfT OGL-UK-3.0 per data/sources.yaml) |
| D8 UI | PASS (note) | axe `--grep "catalogue\|explore-cards"`: 10/10 pass, light + dark, 1280 + 360 px (axe includes colour contrast); catalogue.spec 360 px check passes in all six languages. No screenshots attached to the PR (AC 4; layout sign-off is part 2) |
| D9 flags/routes | PASS | new route `/cars` + header link "All cars"; Rankings link still behind `parkedEnabled("rankings")` (smoke test 9 passes) |
| D10 bundle | PASS | numbers under R2 |
| D13 network in tests | PASS | popularity.test reads repo files only; e2e hit the local server |

Other checks asked for:
- sheet_values: PASS. `grep -c sheet_values` = 0 in `src/config/popularity.generated.json` and in `.next/static`; test "never carries sheet values into the output" present.
- Opinion label: PASS. `catalogue.how.picks` says "one person's verdict … an opinion, not a measurement" in all six languages; the sort line links to it.
- Hard-coded UI strings: PASS (only a `"—"` placeholder, cars/page.tsx:107).
- Lane: PASS as flagged. `config/popularity.yaml` is outside apps/web, named in the PR and in WS0/WS1 INBOX (main ff1c8aa); WS0 to confirm the owner.

**Findings**
1. **must-fix: generation ranks are built from model-level registrations.** `src/lib/popularity.ts:23` gives every generation of a model the model's full top40 share, then ranks per generation and shows "#n popular" per generation. On release 2: Model 3 gen1 #1 and Model 3 Highland #2 (both 80), Model Y Juniper #4 (66.9), Leaf ZE0 and ZE1 both #18 (22.6), Niro EV DE/SG2, Kona OS/SX2, XC40 gen1/EX40, e-tron GE/Q8 likewise tied; 15 models carry 2–3 generations each. The release already has per-generation NL counts that contradict the ties: Model 3 gen1 44 813 vs Highland 20 573, Leaf ZE0 1 965 vs ZE1 10 183 (`registered_count_nl`). The double counting also pushes other models down (Kia Niro EV, 3rd model by registration share at 3.686, shows #6 and #7 behind four Tesla generations). Fix: either rank models (one rank shared by their generations, and say so) or split the model share over its generations with a sourced key (e.g. each generation's share of the model's `registered_count_nl`), stated in "How we rank"; add a test with a two-generation model.
2. should-fix: old Explore links that also carry hero answers lose their Explore state. `src/lib/catalogue-redirect.ts:7` keeps `?role=only&trips=monthly&sort=-suggested&view=table` (the old suggested.spec URL) on the landing, where there is no Explore, so `sort`/`view` are dropped. The hero never writes `sort`/`view`, and `/cars` reads hero answers from the URL (suggested.spec test 12 passes), so redirect whenever `view` or `sort` is present.
3. should-fix: D7 above (licence + Nerd-mode provenance for the "#n popular" tag).
4. nit: `catalogue.intro` says "Every EV generation we track", but until part 2 the list has one card per variant (271 rows, 93 generations).
5. nit: 11 picked generations in popularity.generated.json are not in release 2 (e.g. kia-ev4-gen1, xpeng-p7-plus-gen1). Harmless, but they will rank silently once they land.
6. Known gap noted by the builder (table "unsorted" not in the URL) confirmed as documented; not blocking.

**fresh reviewer (subagent), re-review 2026-11-18, head `f1e7c45`, REVIEW.md from origin/main (4b61283; unchanged since f34ac1a). Verdict: PASS.**

| Item | Verdict | Evidence |
|---|---|---|
| R0 CI on head | PASS | CI run 44207490342 on f1e7c45 `completed success` (detect, repo-checks, gate-guard, schema, web, pipeline, e2e, audit, data-qa, ci-ok all success); Images 44207490344 success |
| R1 conflict markers | PASS | `git grep -nE '^(<{7}\|={7}\|>{7})( \|$)' HEAD` → no hits |
| R2 evidence pack | PASS | commit message numbers reproduced: vitest 51 files / 438 tests; lint + typecheck clean; `APP_URL=https://ev.example.com pnpm build` exit 0; budget landing 163.1 KB, /cars 163.3 KB (< 200), catalogue 202.4 KB (< 300) "Perf budget: OK"; Playwright catalogue + suggested + smoke + polish 21 passed, 1 skipped (polish.spec:114, Rankings parked, Decision 051) |
| R3 own checks | PASS | `Test-change:` line in f1e7c45; popularity tests rewritten around `rankGenerations` with more cases (split by count, missing count, even split, pick, null, relative weights, stable ties); the redirect test's two "stays on landing" cases changed because the behaviour changed on purpose (finding 2), and a hero-only link `{role, budget}` still stays; no added `.skip(`/`.only(`/`test.fixme` |
| D3 derived score | PASS | see finding 1 below |
| D6 strings | PASS | new keys `catalogue.how.split` and `card.popular.nerd`, plus the reworded `catalogue.how.regs`/`catalogue.intro`, present in en/nl/de/fr/es/it; i18n.test green |
| D7 new number | PASS | Nerd line `popular-nerd` (Explore.tsx:1248) shows score, RDW (CC0) + DfT (OGL v3) and date; "How we rank" names both licences; catalogue.spec asserts both (pass) |
| D8 UI | PASS (note) | catalogue 360 px six-language check passes; the change is one text line, the earlier axe run still covers the layout. Still no screenshots in the PR (part 2) |
| D10 bundle | PASS | numbers under R2 |
| D13 network | PASS | unit tests use inline rows; e2e use the local server |

**Earlier findings, re-checked**
1. must-fix (generation ranks from model shares): **fixed.** `generationShares` (src/lib/popularity.ts) splits each model's share by `registered_count_nl`. I recomputed release 2 with my own script (not the PR's function): 82 of 93 generations ranked, **0 score mismatches** against the PR. Model 3 gen1 #1 (80, NL 44 813), Highland #6 (36.7, NL 20 573); Model Y gen1 #2, Juniper #9; Leaf ZE1 #14, ZE0 #67; Niro EV DE #10, SG2 #21. No two generations of one model tie any more. The 8 remaining tied scores are all coincidences between different models (e.g. Polestar 4 and Zeekr 001 at 20 = pick only). On release 2 no generation is zeroed and no model is split evenly; both fallbacks are only covered by tests.
2. should-fix (old links with hero answers lost their Explore state): **fixed.** catalogue-redirect.ts:5 now redirects whenever `view` or `sort` is present; catalogue.spec checks `?role=only&trips=monthly&sort=-suggested&view=table` → `/cars` with the same query (pass).
3. should-fix (D7): **fixed** (see D7).
4. nit (intro): **fixed** ("Every electric car we track").
5. nit (11 picks not in release 2): left as is, which is fine. They have no effect because `rankGenerations` only iterates rows in the catalogue.

**New nits (not blocking)**
- The split key is the NL count of each generation over all years, while the share it splits is the NL 2018–2024 + UK fleet average. It's a reasonable proxy and "How we rank" explains it; WS1's release field should replace it.
- Polestar 4 (NL 2 057) and Zeekr 001 (NL 1 224) get no registration part because they're outside top40.yaml. That's a coverage gap in the top40 inputs, not a code bug.

**Fresh reviewer (subagent), 2026-11-18, head `44ac77e`, REVIEW.md read from origin/main (`3dbb80b`; last changed in 075cd4b, "D6: English only", Decision 082). Verdict: FAIL (2 must-fix).**
Scope: T-130 part 2, the design's visual layer. Note: during the review the PR head moved to `fc68666` (merge of main, T-137 English only). The items below were judged on 44ac77e. R0 is reported for both heads.

| Item | Verdict | Evidence |
|---|---|---|
| R0 CI on head | **FAIL** | 44ac77e: CI runs 44276134151 (pull_request) and 44276161194 (dispatch) both ended `cancelled` (superseded by the push), so 44ac77e has no green CI. New head fc68666: CI 44276903930 `failure`. The e2e job fails `polish.spec.ts:16` "Explore cards at 360 px", with "page wider than the phone at level nerd" (`/nl/en?view=cards&level=nerd` after the English-only merge). Dispatch run 44276892949 was still `in_progress` when I checked. Images on both heads: `success`. I could not reproduce the overflow on a 44ac77e build: `/nl/en/cars?view=cards&level=nerd`, `/nl/nl/cars?level=nerd` and `/nl/en/cars?umax=25000&winter=250&level=nerd` at 360 px all give scrollWidth 360 = innerWidth, with no card child past 360. So it comes from the merge, or it is flaky. Either way the new head must go green. |
| R1 conflict markers | PASS | `git grep -nE '^(<{7}\|={7}\|>{7})( \|$)' HEAD` returns no hits |
| R2 evidence pack | PASS | The PR body has commands and numbers. I reproduced them on 44ac77e. `pnpm typecheck` exit 0. `pnpm lint` exit 0. `pnpm vitest run`: 52 files / 447 tests pass. `APP_URL=https://ev.example.com pnpm build` exit 0. `node scripts/budget.mjs`: landing 163.2 KB, /cars 166.9 KB (< 200), catalogue 221.8 KB (< 300), "Perf budget: OK". The commit carries `Verified:` and `Test-change:`. Screenshots are said to be in `verify-report/` but are not attached to the PR (AC 4). |
| R3 own checks | PASS | smoke.spec only adds a click that opens "More filters" before `#f-rangeMin`. The catalogue.spec sort test swaps `price`/`range` for the design's `used`/`winter` (old keys still parse) and adds 4 tests. feature-map swaps the range fill for `#f-usedMax` and adds the `catalogue-cards` flow. state.test counter 24 → 27 (3 new filters). No `.skip(`/`.only(`/`fixme` added. budget.mjs is untouched. |
| D6 strings | PASS | Script check against origin/main: 64 new keys. 0 missing in en/nl/de/fr/es/it, 0 placeholder mismatches, 0 keys removed in any language. The few NL/FR/IT strings identical to EN are legitimate ("Min ({currency})", "km / 20 min", "Filters · {n}"). Glossary ids used exist in `data/taxonomy/glossary_terms.yaml` (real-winter-range, used-price, model-years, dc-km-20min, seats). Under the new D6 (English only), English is complete; this PR adds no routes or hreflang. |
| D7 new numbers | **FAIL (should-fix)** | Winter, summer and km/20 min facts and battery go through `<Num>` with the highest variant's provenance. At Nerd they show the sources and date inline (my Nerd probe on Model 3 shows sources, "low", 2026-11-17 and the method). But: (a) the card's **new price** (Explore.tsx:1665) is plain `formatMoney`, with no `<Num>` and no provenance. The old card used `priceCell` → `<Num provenance=price_new…>`, so this is a regression of apps/web/AGENTS.md rule 2. (b) The used price band at Nerd shows "Source: Marktplaats search results …, 2026-11-15" but no licence (D7 asks for source + date + licence). |
| D8 UI | PASS with findings | My screenshots: `/tmp/r126/cars-{360,1280}-{light,dark}.png`, `sheet-360-{light,dark}.png`, `cars-360-dark-card.png`, `cars-1280-nerd.png`. 360 px: no sideways scroll in either theme (scrollWidth − clientWidth = 0). axe (my run) on the **open sheet** at 360 px, Nerd, light + dark: 0 violations. The suite's axe catalogue cases pass. `contrast.py`: "All pairs pass WCAG AA". Layout matches frames t130-d1/m1/m2 in structure: sidebar groups in design order, pills + Clear, sort right, "#n popular", used band, three facts, sheet with "Show 9 cars". Real bugs below (findings 1–4). |
| D10 bundle | PASS | /cars 166.9 KB gzip first load (< 200); catalogue 221.8 KB (< 300), +19 KB as stated |
| D13 network in tests | PASS | New unit tests use inline rows (`filters.test.ts`, `generation-cards.test.ts`). The e2e specs hit the local server only. My run of catalogue + smoke + a11y + review + polish + trip: **72 passed, 2 skipped, 0 failed (4.1 min)**. |

**Findings**

1. **must-fix: the phone sheet steals focus after every filter change.** The effect at Explore.tsx:~964–980 depends on `[open, onClose]`. `onClose` is a new arrow on every render (Explore.tsx:372 `onClose={() => setSheet(false)}`). So each state update while the sheet is open runs the cleanup (focus → "Filters" button) and then the effect again (focus → Close). Reproduced at 360 px on `/nl/en/cars?umax=25000&winter=250`:
   - I opened the sheet, clicked `#f-usedMin` and typed "10000". The field holds "**1**", the URL is `umin=1`, and `document.activeElement` is "Close filters".
   - With the winter slider focused, ArrowRight moves it 250 → 260 and focus jumps to Close, so the second ArrowRight does nothing.
   - Every tick, tile or number entry in the sheet has the same problem. The sheet can't be used for typed filters.
   - Fix: keep `onClose` stable (`useCallback`), or depend on `open` only with a ref for the callback. Add an e2e test that types a multi-digit value in the open sheet and checks the value and focus.
2. **must-fix: R0.** 44ac77e has no completed CI (cancelled). The new head fc68666 is red (`polish.spec.ts:16`, Nerd cards wider than 360 px at `/nl/en`). Get CI green on the head that will merge, then re-run this review's R0 and D8 on it.
3. should-fix: resizing to desktop with the sheet open locks the page. I opened the sheet at 360 px, then resized to 1280. Body `overflow` stays `hidden`, the sidebar keeps `role="dialog"` + `aria-modal="true"`, and a 2000 px wheel leaves `scrollY` at 0. Close the sheet on the `lg` breakpoint (matchMedia), or only apply the lock and dialog role below `lg`. There is also a smell in the same spot: Explore.tsx:988 carries both `lg:static` and `lg:sticky`.
4. should-fix: the sheet claims `aria-modal` but doesn't trap focus. Tabbing from Close leaves the dialog after 43 Tab presses and lands on "Simple" (the level toggle behind the backdrop). Trap focus inside the sheet, or make the rest of the page `inert` while it is open.
5. should-fix: groups whose `open` depends on their filters collapse under the cursor. The groups are "Seats · battery · towing" (Explore.tsx:1081) and "More filters" (1089). I opened the seats group, typed 5, then pressed Backspace. The `<details>` closes (`open=false`) and focus drops to `BODY`. Only force `open` on, never off (for example `open={open \|\| undefined}` with initial state), or keep the open state in React.
6. should-fix: D7, as in the table. Put the card's new price through `<Num>` with `price_new.<CC>` provenance, as `priceCell` did. Add the licence to the Nerd used-price source line.
7. nit: the used band can exceed the visitor's max. Scope filters bands by **median** (generation-cards.ts:80) but shows p25–p75 (83–84). With `umax=25000`, cards show "€21k–€28k" (MG4) and "€21k–€27k" (Enyaq) under the pill "Up to €25,000 used". Either clamp the shown span or say "typical" in the label. Related: the used-price filter (filters.ts:50) checks every build year, while the build-year filter checks the variant's years. With `yearMin` + `umax`, a car can match on a cheap band from before `yearMin`. The card then falls back to all bands (generation-cards.ts:82).
8. nit (design deviation, documented as a reversible default): at 360 × 800 the first card starts at y = 762 px, below the fold. The level, view and price-mode toggles sit above the list. Frame t130-m1 shows cards right under the bar and compact horizontal cards. Worth moving the toggles into the sheet, as the builder suggests.
9. nit: at 1280 px with Detailed, the three facts are cramped when they are ranges ("306–334 481–488 224–259"). The labels wrap to two lines ("km / 20 min", "km summer"). Compare frame t130-d1.
10. nit: the compare button's accessible name is "+Compare: Tesla Model 3 Long Range AWD" (the visible "+" glyph is in the name; make it `aria-hidden`). The brand count uses `aria-label` on a plain `<span>` (Explore.tsx:919), which ARIA 1.2 prohibits on generic elements, though axe didn't flag it. Some generation names repeat the years ("Model 3 (2019-2023) · 2019–2023"); that's data, for WS1.
11. Not in this diff, for the follow-up: the PR says `apps/web/AGENTS.md` needs a line about generation cards and the new filters. That is a gate change in its own PR; fine.

Items reproduced: typecheck, lint, vitest, build, budget, 6 Playwright specs, axe on the open sheet, contrast.py, and my own probe scripts (`/tmp/r126/probe.cjs`, `nerd.cjs`, `axe.cjs`).

**Builder response (WS2, head after fc68666):** 1 fixed (sheet effect runs on open/close only, close callback via ref; e2e types "10000" in the open sheet and checks value, URL and focus). 2: CI re-run on the new head (the 5 px Nerd overflow at 360 px came from flex items without `min-w-0` in the card; now `min-w-0` on the card and fact values, probe at 360 px with 6 % wider letters: no overflow at any level). 3 fixed (sheet closes when the window reaches the lg breakpoint; duplicate `lg:static` gone; e2e). 4 fixed (Tab and Shift+Tab wrap inside the open sheet; e2e). 5 fixed (groups only ever open from code, never snap shut; e2e). 6 fixed for the new price (`<Num>` with `price_new.<CC>` provenance); licence on the used-price line needs a licence field in used_prices.json sources: asked WS1. 7: the used-price filter now respects the build-year filter (unit test); the shown band stays p25–p75 of the bands whose typical price fits (it is the honest spread). 8, 9: left as documented defaults (follow-up candidates). 10: brand count now sr-only text instead of `aria-label` on a span; the compare "+" is already `aria-hidden`.
