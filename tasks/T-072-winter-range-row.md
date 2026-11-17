# T-072 Winter range per variant in the release rows
Role: builder   Lane: pipeline/ev_pipeline/derive (+ one PublishedVariant line in packages/schema, asked from WS0)   Wave: 9 (launch: hero card, model pages)
Status: review (WS1 5th chat, 2026-11-17)

## Goal
Every variant with a consumption-matrix entry ships `real_range_winter_km` in its catalogue row, with provenance, so the hero card and model pages stop saying "In winter: not known yet".

## Acceptance criteria
- [x] `real_range_winter_km` = usable kWh / winter mixed Wh/km from the matrix (same function and params as the shortlist: band t1 "-5 °C and colder", road mix 30/30/40, heater rule), so card and shortlist always agree
- [x] Provenance: derived, estimate, confidence low, inputs' sources, note naming the band and that the temperature step is unvalidated (Q-059)
- [x] Range check in validate.py; in ROW_NUMBER_FIELDS (provenance required); open-data bundle column
- [x] Schema: `PublishedVariant.real_range_winter_km` (number|null), additive, types regenerated (WS0 asked)
- [x] Tests with fixtures; dry run counts in the PR

## Inputs
WS2 INBOX 2026-11-15 12:55; START §3 item 6; derive/shortlist.py `derived_values`; Decision 041; launch-scope.md (winter range on cards and pages).

## Out of scope
Validating the temperature step (needs winter road tests, Q-059); T-070 (real range from the matrix).

## Handoff notes
- `derive/winter.py` attaches the field right after the matrix is built, using the shortlist's `derived_values` and `shortlist_params.yaml` (band t1, mix 30/30/40, heater rule). Same number on card and in the shortlist by construction (test).
- Dry run on release 1 rows (matrix rebuilt without staging EPA tests, so rungs are WLTP-based): **196 of 226** rows filled, provenance errors 0. Median winter / WLTP 0.575, winter / real range 0.718. Examples: EV6 58 kWh 225 km, Ioniq 5 58 kWh 224, MG4 Standard 200, Model Y RWD 234, Model 3 Highland LR 396, Zoe R135 195; lowest smart fortwo EQ 55, longest ID.7 Tourer / A6 e-tron 443–450. 🟡 Plausible for -5 °C with 40 % motorway; unvalidated (Q-059), labelled estimate.
- No back-test possible yet: no licence-clean winter test (Q-059). qa.json `profile_fields.winter_range_km` already reports coverage, rungs and the 20 °C proxy.
- Schema: one additive PublishedVariant property + regenerated TS/Python (cross-lane, asked in WS0 INBOX 10:45). Schema tests 108 passed; web `tsc --noEmit` exit 0.
- Release diff (T-123): new field on ~196 rows in release 2 → part of the release-scoped approval.
- WS2: field `real_range_winter_km` + `provenance.real_range_winter_km` in each row; nothing else to fetch.

## Review
