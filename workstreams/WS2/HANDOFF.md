# WS2 handoff — 2026-11-18 10:40 UTC (6th chat → next chat for T-132)

Chat: https://claude.ai/code/session_01JuyZEWZuyZEW

## State
- Two WS2 chats ran at once. **T-130 part 2 is the 5th chat's PR #126** (under fresh review). The 6th chat built the same thing in parallel, found #126 on push, pushed nothing over it (ideas for #126 in WS2 INBOX 10:15).
- Menno's call (10:25): **6th-chat line takes T-132 hero redesign** on branch `t-132-hero-questions` (not created yet). 5th chat keeps #126, T-131, T-135. Claim is in tasks/T-132 Status + WS2 INBOX.
- Nothing open from the 6th chat.

## T-132 plan (start here)
Spec: docs/design/explorations/staging-r1/README.md §T-132 (signed off by Menno) + frames t132-m1…m4 (phone) and t132-d1/d2 (desktop), contact sheets SHEET-t132-*.png. Components: docs/design/components/{AnswerTile,ProgressRoad,ResultRow}/README.md.
Code today: `apps/web/src/components/Hero.tsx` (1013 lines: Step 133, Choice 146, NumberSelect 190, Hero 231, BudgetField 489, Refine 550, Results 664, Card 833, NerdScore 957), state in `src/lib/hero-state.ts` (URL), ranking in `src/lib/shortlist.ts` (don't change scoring: Decision 065), e2e `e2e/hero.spec.ts` (13 tests) + verify flows hero-* in `e2e/feature-map.yaml`.
Suggested split (two PRs, each half a day):
1. **Questions**: one question per screen (country → 4 driving questions → budget); `ProgressRoad` (ol, aria-current="step", 4 stops); `AnswerTile` (fieldset + radios, ≥ 64 px, tick when picked; country 2 columns); answer trail of pills (list of buttons, jump back; after step 2 collapse into the profile name); budget step = big € field, 6 quick picks (3×2 incl. "No limit"), ≈ monthly box, New/Used/Either switch, "Show my top 10", "More filters (optional)". Every answer still writes the URL; back = previous question. Copy changes listed in the README (en.json, then all 6 languages: D6). "Keep it 8 years" moves to the refine sheet. Slide-in ≈ 250 ms, reduced motion instant.
2. **Results**: phone = profile bar (name, country, budget, Edit) → "Your shortlist" (sunflower tint) 5 compact rows (rank, name, years, price band, winter km, km/20 min, one "Why:" line, shortlist button) → "Also worth a look" 6–10 one-liners; desktop = sticky answers sidebar + top-10 table with aligned columns; "Refine · n" (phone: bottom sheet like #126's filter sheet, reuse it after #126 merges); "Show all cars" box at the end. Photos wait for T-135 (5th chat): leave the thumbnail slot.
Before/after screenshots 360 + 1280, light + dark (AC). Run `node scripts/verify.mjs --changed --base origin/main`; flow `tooltip` fails on main too (WS0 asked WS2 to fix it: match `:visible` or scope to the clicked term; small separate PR, `Test-change:` line).

## Lessons (this chat)
- Before starting a task, check **open PRs and remote branches for the task id** (`gh api repos/zkMenno/EV-Shortlist/pulls`, `git ls-remote --heads origin | grep t-1NN`) *and again before the first push*. The handoff can be an hour stale while another chat is on it. Proposed rule for WS0.
- Server components can't call functions from a `"use client"` file, even pure ones: keep shared helpers in `src/lib/`.
- `Intl.NumberFormat` compact in de-DE doesn't shorten thousands: round first.
- Country names in sentences need prepositions per language ("aux Pays-Bas"): use per-country keys, not `Intl.DisplayNames`.

---

## Previous handoff
# WS2 handoff — 2026-11-18 00:20 UTC

Chat: https://claude.ai/code/session_01JuyZEUuCTBUyPNJ74C3iRD

## State (2026-11-18 08:55 UTC)
- **#117 T-130 part 1 merged** (/cars catalogue, Most popular default, landing "Show all cars", old-link redirect, per-generation popularity split by RDW counts). **#118 merged** (apps/web AGENTS.md lines).
- **#111 T-137** English only: check its state; it edits e2e specs that #117 changed, so it needs main merged in.
- **#104** landing parallax: merged.
- Asked WS1 for a release `popularity` field (WS1 INBOX); until then the web builds it from data/seed/top40.yaml + menno-picks (scripts/popularity.mjs, weights config/popularity.yaml). Swap point: `catalogue.popularity()`.

## Next (in order)
1. T-130 part 2: the design's visual layer (PR #107 frames t130-*): sidebar filter groups, phone "Filters · n" bottom sheet + sticky bar, removable pills + Clear, count "N models · M match", one card per generation (used price band, winter km, summer km, km/20 min). Photos wait for T-135.
2. T-131 Popular used EVs (data/editorial/popular_used.yaml, WS3 PR #106).
3. T-135 photo cards (WS1 T-134 image fields).
4. T-132 hero redesign (designs in #107).

## Lessons
- A native `<select>` is as wide as its longest option: FR/ES overflowed 360 px. Test 360 px in all six languages.
- `**/AGENTS.md` is a gate file: split doc changes into their own PR.
- Feature-map triggers must resolve inside apps/web (outside paths fail verify-map.test).
- Next page files may only export page things: helpers go to src/lib.
- Run `pnpm vitest run` again after editing e2e/feature-map.yaml.

## Previous handoff (2026-11-17 22:06)

Chat: https://claude.ai/code/session_01JuyZEUgDrkg5ED4ZkeyEzg

## State
- **#111 T-137 English only:** fresh review PASS on e2e49ce, CI green (Images red = main's release-2 Docker error, WS1/WS4). Waiting for WS0 to approve the feature-map change, then merge (main moved since: merge main in and let CI run first).
- **#104** landing parallax (2nd WS2 chat): still open.
- Open with others: REVIEW D6 gate PR for Decision 082 (WS0); verify flow `tooltip` checks only the first of ~336 hidden tooltip nodes (scripts/verify.mjs:223, `.first()`), fails on main too: rubric fix, WS0.

## How T-137 works (for whoever adds a language back)
- Languages come only from `config/countries/<cc>.yaml`: `languages: []` + `default_language: en` everywhere; the old list sits in a comment above. List a language again → routes, sitemap, hreflang, picker and banner all return, no code change.
- e2e specs that need a second language skip on `ENGLISH_ONLY` (apps/web/e2e/langs.ts, read from the generated config) and switch back on by themselves.

## Next (in order)
1. T-130 catalogue page + "Show all cars": UX designs are in PR #107 (not merged yet). Popularity score must come from the release: ask WS1 for the field (blend weights in config, Decision 038).
2. T-131 Popular used EVs section (WS3 makes the list first).
3. T-135 photo cards (needs WS1's image fields, T-134).
4. T-132 hero redesign (designs in #107).

## Lessons
- Run `pnpm vitest run` again after editing e2e/feature-map.yaml: verify-map.test.ts pins required flow ids.
- Don't rename files during `pnpm build` (the standalone copy step fails).
- num-labels.test.ts can fail locally and pass in CI: check CI before calling something "red on main".
