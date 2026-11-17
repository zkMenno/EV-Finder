# T-067 Owner's picks and "Suggested for you" on the web
Role: builder   Lane: apps/web   Wave: 9
Status: done (merged by WS2 with Menno's OK, 2026-11-17)

## Goal
Show Menno's picks as a labelled editorial list and use the rules to suggest cars for the shortlist tray.

## Acceptance criteria
- [ ] `/top/owners-picks`: groups as in the sheet (800 V picks, 400 V mid-size, 400 V full-size, "great but pricey"), verdict chip, owner note, link to the model page. Label: "One owner's picks for an only car with regular long trips, NL + FR market, Nov 2026. Opinion, not a test."
- [ ] Model / generation pages: an "Owner's note" line when a pick exists (verdict + note), hidden in Simple mode if empty
- [ ] Profile picker (4 taps: car role, long trips, where you charge, where you live; Decision 050) → base profile + modifier + kerbside layer; preselects that profile's `filter_presets` as removable chips "Set by your profile"; state in the URL
- [ ] Explore: optional "Suggested" sort for the chosen profile, score computed in the browser from published fields + `shortlist_rules.yaml`; ⓘ shows "Why this order" (top 3 reasons + gates hit, plain words from the rules file)
- [ ] Price stays a filter; "great but pricey" stays a separate group
- [ ] Never shows `sheet_values`; unknown factors shown as "not known yet", not as a low score
- [ ] Vitest for scoring parity with `data/editorial/backtest_rules.py` on a fixture; EN + NL strings, other languages marked review: needed

## Inputs
Decisions 038–039, research/R-32 and R-33, docs/design (ShortlistTray, chips), trip-fit §6 (later merge with Fit score).

## Out of scope
Account sync, marketplace links.

## Handoff notes
- 2026-11-15 WS2: the 4-tap picker is the hero's (T-080). This branch adds Explore's "Suggested for: {profile}" toggle (`sort=-suggested`), scoring in the browser with `src/lib/shortlist.ts`, ruled-out cars last, and an ⓘ "Why this order" (three heaviest factors after weight steps, the gates in plain words, "unknown counts as average", the owner/research caveat). Explore follows hero answers live (browser event `ev-finder:profile`). Server render sorts the same way.
- Owner's note: done on model + generation pages (`scripts/owner-picks.mjs` → `src/config/owner-notes.generated.json`, verdict + favourite + note only; `--check` + unit test keep it in step; 12 generations linked by `seed_generation_id`). Labelled as one owner's opinion. Not done: `/top/owners-picks` (a rankings page, parked by Decision 051).
- Scoring parity: see `src/lib/shortlist.test.ts` (fixture checked against `backtest_rules.py`). Types are local until T-066 lands schema types for the rules.

