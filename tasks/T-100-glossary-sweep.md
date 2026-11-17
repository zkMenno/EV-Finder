# T-100 Glossary sweep: every Explore column, filter, hero step and profile has a tooltip
Role: WS3   Lane: data/taxonomy   Wave: 10 (Launch, content)
Status: merged (PR #34, #43); fresh review via QA A-35; earlier note: WS3, 2026-11-15

## Goal
START.md §3 item 7: tooltips in EN + NL for everything a visitor sees in Explore and the hero.

## Acceptance criteria
- [x] Every `term`/`termId` the web app uses exists in the glossary (or chemistry / cooling / voltage tables) with EN + NL label and short text
- [x] Hero steps and the four profiles + "where you live" + "keep 8+ years" have terms
- [x] validate_taxonomy.py passes

## Handoff notes
2026-11-15, WS3 (https://claude.ai/code/session_01JuyZEW2aV2H7ifmpaT5Pfr).
- Checked all 31 term ids used in apps/web/src (main) and in the open hero/suggested-sort PRs (#22, #23 use no term ids yet): all exist with EN + NL. `agree`, `oneSource`, `release`, `assumption` in Num.tsx are internal keys mapped to glossary links, not term ids.
- Added 10 terms: shortlist, road-tripper, daily-driver, runabout, kerbside-charger, home-area, keep-8-years, budget, real-winter-range (id `winter-range` is taken by the /learn article). Full EN (label, technical, short, long, nerd_note), NL label + short.
- Rewrote `used-price`: it described a band of listing asking prices; the launch band is a model estimate per build year, replaced by hand samples where they exist (T-081). DE/FR/ES/IT for the new terms not written yet (fallback EN).
- For WS2: hero steps and profile chips can now use these ids.
