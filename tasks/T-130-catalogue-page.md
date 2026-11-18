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
