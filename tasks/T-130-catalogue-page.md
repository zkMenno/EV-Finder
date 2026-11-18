# T-130 Catalogue page with popularity sort; landing loses the full list
Role: builder   Lane: WS2 (+ UX layout): apps/web/   Wave: launch (staging feedback 2026-11-17)
Status: review passed (WS2, 2026-11-18: part 1 merged #117; part 2 #126 fresh re-review 4 PASS on 45ce05c; open should-fix: used-price licence, waiting on WS1)

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

**Fresh reviewer (subagent), re-review 2026-11-18, head `11f8a08` (fix commit on top of merge `fc68666`), REVIEW.md read from origin/main (`27ad23b`; REVIEW.md last changed in 075cd4b and unchanged since the first review). Verdict: PASS (0 must-fix; 1 should-fix open, waiting on WS1).**

| Item | Verdict | Evidence |
|---|---|---|
| R0 CI on head | PASS | CI 44278897887 (workflow_dispatch) and CI 44278908175 (pull_request) on 11f8a08 are both `completed success`. Every job passed: detect, repo-checks, gate-guard (pull_request run), schema, web, pipeline, e2e, audit, data-qa, ci-ok. Images 44278907931: `success`. The PR head is still 11f8a08 (`pulls/126 .head.sha`). |
| R1 conflict markers | PASS | `git grep -nE '^(<{7}\|={7}\|>{7})( \|$)' HEAD` finds nothing |
| R2 evidence pack | PASS | The fix commit carries `Verified:` + `Test-change:`, and the task file has the builder's response. I reproduced the gate on 11f8a08 after a fresh rebuild: typecheck exit 0; lint exit 0; vitest 52 files / 447 tests pass (the new "used price with build years" test runs: `filters.test.ts` 17/17); `APP_URL=https://ev.example.com pnpm build` exit 0; budget landing 163.2 KB, /cars 167.2 KB (< 200), catalogue 221.8 KB (< 300), "Perf budget: OK". |
| R3 own checks (new commit) | PASS | 11f8a08 touches `e2e/catalogue.spec.ts` (+29, one new test, nothing removed), `filters.test.ts` (+8, new case), `Explore.tsx`, `filters.ts` and the task file. No gate files, no `.skip`/`.only`/`fixme`, no thresholds changed. |
| Merge fc68666 vs the T-130 diff | PASS | `git diff-tree --cc -p fc68666` is empty, so no hand-resolved hunks. `git diff 2d6267b fc68666` (main parent → merge) touches exactly the PR's 19 files with the same stat as before the merge (1396+/205−). So the merge added nothing to the T-130 change. The adjustments that came in from main (English-only e2e paths in catalogue/smoke/a11y/polish specs, `ENGLISH_ONLY` from `e2e/langs.ts`) are main's own changes. |
| D6 strings | PASS | No string changes in 11f8a08 (new text reuses `filters.brands.count`). On the English-only head, `/nl/nl/cars?umax=25000` redirects to `/nl/en/cars?umax=25000`, and the header has no language picker (screenshot `cars-1280-dark.png`). |
| D7 new numbers | PASS (should-fix open) | The card new price now goes through `<Num>` (`newPriceNum`). At Nerd on the ID.3 card it shows "€59,790 · 1 source · raw: 59790 · RDW Open Data · medium · 2026-11-17 · newest rule". Still open: the used price band's Nerd line has source + date but no licence. The builder asked WS1 for a licence field in `used_prices.json` (see finding 6). |
| D8 UI (merged, English-only head) | PASS | My screenshots are in `/tmp/r126b/`: `cars-{360,1280}-{light,dark}.png`, `sheet-360-{light,dark}.png`, `card-360-nerd-{light,dark}.png`, `resize-open-1280.png`, `cars-1280-nerd.png`. Sideways overflow is 0 at 360 and 1280 in both themes. I also checked 360 px at simple/detailed/nerd for `/nl/en?view=cards`, `/uk/en/cars`, `/de/en/cars` and `/nl/en/cars?umax=25000&winter=250`: overflow none (this is the CI failure from round 1). axe: open sheet at 360 px Nerd and 1280 px Nerd, light + dark, gives 0 violations. Suite run (catalogue, smoke, a11y, review, polish, trip, english-only): **81 passed, 2 skipped, 0 failed (4.2 min)**. |
| D10 bundle | PASS | /cars 167.2 KB gzip (+0.3 KB from the fixes) |
| D13 network in tests | PASS | The new unit test uses inline rows. The new e2e test uses the local server. |

**Earlier findings, re-checked (same probes at 360 px, `/nl/en/cars?umax=25000&winter=250`)**
1. must-fix, sheet steals focus: **fixed.** I typed "10000" in `#f-usedMin` inside the open sheet. The value stays `10000`, the URL has `umin=10000`, and focus stays on `f-usedMin`. Winter slider: two ArrowRight presses take it 250 → 270 with focus kept on `f-winterMin`. Ticking a brand keeps focus on the checkbox, and a fast-charging tile keeps focus on itself (URL `make=tesla`, `dc=100`). The effect now depends on `[open]` only, with the callback in a ref (Explore.tsx `closeFn`).
2. must-fix, R0: **fixed.** CI is green on 11f8a08 (see R0). The Nerd 360 px overflow is gone (see D8).
3. should-fix, resize to desktop with the sheet open: **fixed.** I opened the sheet at 360 and widened to 1280. The dialog is removed, `body.style.overflow` is `""`, and a 1500 px wheel scrolls to `scrollY` 1325 (same as a fresh 1280 page). The duplicate `lg:static` is gone.
4. should-fix, focus trap: **fixed.** From Close, 150 Tab presses and then 150 Shift+Tab presses never leave `[role=dialog]`. Escape closes the sheet, focus returns to `filters-open`, and the scroll lock is released. A backdrop click also closes it.
5. should-fix, groups snapping shut: **fixed.** I opened "Seats · battery · towing", typed 5, then pressed Backspace. The group stays open and focus stays on `f-seatsMin`.
6. should-fix, D7: **half fixed.** The new price has provenance now. The used-price licence is still open and depends on WS1's data. Stays should-fix (before public); it doesn't block this merge.
7. nit, used band vs filters: **partly addressed.** The used-price filter now respects build years (filters.ts, unit test). The shown band is still p25–p75, so with `umax=25000` the MG4 card reads "€21k–€28k". The builder keeps this on purpose ("the honest spread"). Acceptable; a "typical" label would help.
8. nit, first card below the fold on phones: unchanged, documented default (first card starts at y ≈ 762 at 360 × 800).
9. nit, cramped facts at 1280: changed but not better (see new finding A).
10. nit, accessible names: **brand count fixed** (sr-only text). **Compare "+": my round-1 finding was wrong.** I had read `textContent`; the accessibility tree name is "Compare : Tesla Model 3 Long Range AWD", so the "+" is already hidden. Retracted.

**New findings (not blocking)**
- A. nit: `flex-wrap` on the fact `<dd>` (Explore.tsx, `fact()`) puts the snow/sun/plug icon on its own line above the number on every 1280 px card with a range (`cars-1280-dark.png`). Frame t130-d1 has the icon inline. Wrapping only the number's text, or `flex-nowrap` from `sm` up, would keep the 360 px fix.
- B. nit: "Clear all" inside the open sheet unmounts itself (it renders only while filters are on), so focus drops to `BODY` while the dialog stays open (probe: `afterClearAllFocus: BODY`, dialog count 1). The trap recovers on the next Tab. Better: move focus to the sheet heading or the Close button after clearing.
- C. nit: the compare button name has a stray space ("Compare : Tesla …"), from the sr-only text join.
- D. nit (data, for WS1, unchanged): some generation names repeat the years ("Model 3 (2019-2023) · 2019–2023").

Reproduced on 11f8a08 with a fresh rebuild. Probe scripts are in `/tmp/r126b/` (`probe.cjs`, `extra.cjs`, `resize.cjs`, `s360.cjs`). I didn't change, commit or push anything in the repo.

**Fresh reviewer (subagent), re-review 3, 2026-11-18, head `db62961` (nits fix on top of merge `bbaa60a`), REVIEW.md read from origin/main (`7f1e981`; REVIEW.md last changed in 075cd4b, unchanged). Verdict: FAIL (1 must-fix: R0, CI red on db62961, caused by the nit A fix).**
Scope: only what changed since 11f8a08.

| Item | Verdict | Evidence |
|---|---|---|
| R0 CI on head | **FAIL** | Both CI runs on db62961 finished `failure`: 44281463598 (workflow_dispatch) and 44281481316 (pull_request). Every job is green except `e2e` (and therefore `ci-ok`). The failure is `polish.spec.ts:16` "Explore cards at 360 px", with "page wider than the phone at level nerd". It fails on the first try and on retry1 in both runs. Images 44281481283: `success`. The same test was green on 11f8a08 (CI 44278897887 / 44278908175). See finding 1. |
| R1 conflict markers | PASS | `git grep -nE '^(<{7}\|={7}\|>{7})( \|$)' HEAD` finds 0 hits |
| R2 evidence pack | PASS (local) | I rebuilt from db62961 because `.next/BUILD_ID` (10:56) predated the commit (11:01). Then: typecheck exit 0, lint exit 0, vitest 447/447, `APP_URL=https://ev.example.com pnpm build` exit 0, budget /cars 167.2 KB (< 200), catalogue 221.8 KB (< 300), "Perf budget: OK". Playwright catalogue + polish + a11y + smoke + english-only: **70 passed, 1 skipped, 0 failed (3.7 min)**. Locally polish.spec:16 passes; CI does not (fonts render differently there, see finding 1). The commit claims "Verified" from the same local run, which CI doesn't confirm. |
| R3 own checks (db62961) | PASS | Only `e2e/catalogue.spec.ts` changes on the test side: +4 lines (the "Clear all" focus check), nothing removed. `Test-change:` line present. No gate files touched. |
| Merge bbaa60a vs the T-130 diff | PASS | `git diff-tree --cc -p bbaa60a` is empty (no hand-resolved hunks). The main parent (b8e8a2c) → merge diff is exactly the PR's 19 files with the same stat as the PR before the merge (1530+/205−). From main's side, the only file the merge brings into `apps/web` is `src/config/sources.generated.json`, which gains the two #110 sources `maker-press-photos` and `wikimedia-commons` (main's generated file; vitest's staleness test passes). The branch is 3 commits behind origin/main (7f1e981, 306d3c0, b5b651e): workstream log/handoff files only. |
| Nit A: icon inline at 1280 | PASS (but see finding 1) | My probe checked every fact on every card on `/nl/en/cars?umax=25000&winter=250`, light + dark, at 1280 and 360. The icon is vertically centred with the value and left of it in 100 % of facts. Screenshot `/tmp/r126c/cars-1280-light.png`. |
| Nit B: focus after "Clear all" | PASS | In the open sheet at 360 px, "Clear all" leaves focus on `H2#filters-heading`. The dialog stays open (count 1) and the URL drops to `?sort=-popular`. The next Tab goes to "Close filters" inside the dialog, and Escape returns focus to `filters-open`. Desktop sidebar: focus also goes to the heading. The e2e check passes locally. |

**Findings**
1. **must-fix: the nit A fix brings back the 360 px Nerd overflow (CI red).** db62961 removed `flex-wrap` from the fact `<dd>` (Explore.tsx `fact()`), and that was 11f8a08's fix for this test. Now the icon and value sit in one non-wrapping row. At Nerd the value `<Num>` renders an `inline-flex flex-col` block with unbreakable badges ("2 sources agree"), so it can't shrink below its content.
   - I reproduced this on the local build by widening the text, as CI's fonts do. At `/nl/en?view=cards&level=nerd`, 360 px: letter-spacing 0 or 0.03em gives scrollWidth 360. At 0.06em it gives **363** (widest: the `inline-flex flex-col items-start` span in card `bmw-ix3-gen1`, "141 estimate 2 sources agree…"). At 0.1em it gives 369 (`bmw-ix-gen1`).
   - Fix options: keep the icon inline with the number but let the Nerd details wrap below the row (render the inline sources/badges outside the icon + number flex row); or use `flex-wrap` only where the card is narrow; or use a grid `grid-cols-[auto_minmax(0,1fr)]` with the badges allowed to wrap.
   - Then confirm with the same wider-letter probe at 0.06em and 0.1em, and with CI green on the new head.
2. nit: the heading that gets focus after "Clear all" has `focus:outline-none`. That's acceptable for a non-interactive `tabIndex={-1}` target, but a visible focus ring there would help keyboard users see where they landed.

Earlier findings 1–10 were not re-checked beyond the two nits asked for; they were closed or accepted in re-review 2 on 11f8a08. Finding 6 (licence on the used-price Nerd line) stays open as a should-fix with WS1.

Probe scripts are in `/tmp/r126c/` (`ab.cjs`, `wide.cjs`). I didn't change, commit or push anything in the repo.

**Fresh reviewer (subagent), re-review 4, 2026-11-18, head `45ce05c`, REVIEW.md read from origin/main (`7d4d81a`; REVIEW.md last changed in 075cd4b, unchanged). Verdict: PASS.**
Scope: only what changed since db62961 (re-review 3).

| Item | Verdict | Evidence |
|---|---|---|
| R0 CI on head | PASS | CI 44284898385 (workflow_dispatch) on 45ce05c finished `completed success`: detect, repo-checks, schema, web, pipeline, e2e, audit, data-qa, ci-ok all success (gate-guard skipped, as on dispatch). CI 44284908092 (pull_request) finished `completed success`: gate-guard, repo-checks, detect, schema, web, pipeline, e2e, audit, ci-ok success (data-qa skipped). Images 44284908087: `success`. PR head confirmed as 45ce05c (`pulls/126 .head.sha`). |
| R1 conflict markers | PASS | `git grep -nE '^(<{7}\|={7}\|>{7})( \|$)' HEAD` finds 0 hits |
| R2 local gate (fresh rebuild from 45ce05c) | PASS | typecheck exit 0; lint exit 0; vitest 447/447; `APP_URL=https://ev.example.com pnpm build` exit 0 (`.next/BUILD_ID` 11:32); budget /cars 167.2 KB (< 200), "Perf budget: OK". Playwright catalogue + polish: **18 passed, 1 skipped**, including the new `catalogue.spec.ts:199` "catalogue cards fit 360 px at every level even with wider text". |
| R3 own checks (45ce05c) | PASS | Test side: `e2e/catalogue.spec.ts` +14 lines, one new test, nothing removed or loosened (the bar is `over <= 0`). `Test-change:` + `Verified:` present. No gate files. The new test would catch the round-3 bug: my round-3 probe measured 3 px overflow at 0.06em on db62961's layout, and the test uses the same 0.06em at 360 px. |
| Finding 1 (360 px Nerd overflow) | **fixed** | Wider-letter probe at 360 px over 5 pages per level (`/nl/en?view=cards`, `/nl/en/cars`, `/uk/en/cars`, `/de/en/cars`, `/nl/en/cars?umax=25000&winter=250`), with letter-spacing 0 / 0.06em / 0.1em × simple / detailed / nerd: max overflow **0 px in all 9 combinations**. On db62961 the same probe gave 3 px at 0.06em and 9 px at 0.1em. The fix: `flex-wrap` on the fact `<dd>` at Nerd only (Explore.tsx `fact()`). |
| Nit A (icon inline at 1280) | PASS for Simple/Detailed | 1280 px, `/nl/en/cars`, every fact on every card, light + dark: icon left of and level with the value in **150/150** facts at Simple and at Detailed. Screenshots `/tmp/r126d/cars-1280-{light,dark}-detailed.png`. At Nerd the icon sits above the value in 148/150 facts (2/150 inline). That's the intended trade-off of this fix (Nerd carries badges and inline sources) and doesn't block. |
| Heading focus ring (nit 2, round 3) | PASS | `focus:outline-none` removed. In the open sheet at 360 px, keyboard Enter on "Clear all" moves focus to `H2#filters-heading`, which matches `:focus-visible` and has a `solid 3px rgb(43, 95, 145)` outline. After a mouse click there is no ring, which is normal `:focus-visible` behaviour. |

**Notes**
- The branch is 20 commits behind origin/main (`git diff HEAD...origin/main`: 15 files; outside workstream/task/docs logs only `AGENTS.md`; nothing in `apps/web`). AGENTS.md says to merge each PR up to date with main, so merge main in and let CI re-run before merging. Because none of those files touch `apps/web`, this review's verdicts carry over to that merge commit unless it changes `apps/web`.
- Still open from earlier rounds, not blocking: finding 6, the licence on the used-price Nerd line (should-fix, waiting on WS1's licence field), plus the documented defaults (first card below the fold on phones, p25–p75 used band).

Probe scripts are in `/tmp/r126d/` (`p.cjs`, `kb.cjs`). I didn't change, commit or push anything in the repo.
