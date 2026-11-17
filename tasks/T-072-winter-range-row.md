# T-072 Winter range per variant in the release rows
Role: builder   Lane: pipeline/ev_pipeline/derive (+ one PublishedVariant line in packages/schema, asked from WS0)   Wave: 9 (launch: hero card, model pages)
Status: doing (WS1 5th chat, 2026-11-17)

## Goal
Every variant with a consumption-matrix entry ships `real_range_winter_km` in its catalogue row, with provenance, so the hero card and model pages stop saying "In winter: not known yet".

## Acceptance criteria
- [ ] `real_range_winter_km` = usable kWh / winter mixed Wh/km from the matrix (same function and params as the shortlist: band t1 "-5 °C and colder", road mix 30/30/40, heater rule), so card and shortlist always agree
- [ ] Provenance: derived, estimate, confidence low, inputs' sources, note naming the band and that the temperature step is unvalidated (Q-059)
- [ ] Range check in validate.py; in ROW_NUMBER_FIELDS (provenance required); open-data bundle column
- [ ] Schema: `PublishedVariant.real_range_winter_km` (number|null), additive, types regenerated (WS0 asked)
- [ ] Tests with fixtures; dry run counts in the PR

## Inputs
WS2 INBOX 2026-11-15 12:55; START §3 item 6; derive/shortlist.py `derived_values`; Decision 041; launch-scope.md (winter range on cards and pages).

## Out of scope
Validating the temperature step (needs winter road tests, Q-059); T-070 (real range from the matrix).

## Handoff notes

## Review
