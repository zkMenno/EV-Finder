# T-067 Owner's picks and "Suggested for you" on the web
Role: builder   Lane: apps/web   Wave: 9
Status: review, picker + Suggested sort part (WS2, 2026-11-15, branch t-067-suggested-sort, on top of T-080)

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
- Not done here: `/top/owners-picks` (a rankings page, parked by Decision 051) and the "Owner's note" line on model pages. Both need Menno's yes or a WS0 call on whether the owner note is launch; reads `data/editorial/menno-picks.yaml` (verdict + note only, never `sheet_values`).
- Scoring parity: see `src/lib/shortlist.test.ts` (fixture checked against `backtest_rules.py`). Types are local until T-066 lands schema types for the rules.

