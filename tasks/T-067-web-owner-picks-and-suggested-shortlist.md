# T-067 Owner's picks and "Suggested for you" on the web
Role: builder   Lane: apps/web   Wave: 9
Status: todo (after T-066 types; can start on the YAML now)

## Goal
Show Menno's picks as a labelled editorial list and use the rules to suggest cars for the shortlist tray.

## Acceptance criteria
- [ ] `/top/owners-picks`: groups as in the sheet (800 V picks, 400 V mid-size, 400 V full-size, "great but pricey"), verdict chip, owner note, link to the model page. Label: "One owner's picks for an only car with regular long trips, NL + FR market, Nov 2026. Opinion, not a test."
- [ ] Model / generation pages: an "Owner's note" line when a pick exists (verdict + note), hidden in Simple mode if empty
- [ ] Profile picker (4 taps: car role, long trips, where you charge, where you live; Decision 039) → base profile + modifier + kerbside layer; preselects that profile's `filter_presets` as removable chips "Set by your profile"; state in the URL
- [ ] Explore: optional "Suggested" sort for the chosen profile, score computed in the browser from published fields + `shortlist_rules.yaml`; ⓘ shows "Why this order" (top 3 reasons + gates hit, plain words from the rules file)
- [ ] Price stays a filter; "great but pricey" stays a separate group
- [ ] Never shows `sheet_values`; unknown factors shown as "not known yet", not as a low score
- [ ] Vitest for scoring parity with `data/editorial/backtest_rules.py` on a fixture; EN + NL strings, other languages marked review: needed

## Inputs
Decisions 038–039, research/R-32 and R-33, docs/design (ShortlistTray, chips), trip-fit §6 (later merge with Fit score).

## Out of scope
Account sync, marketplace links.
