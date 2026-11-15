# T-046 Clue types and clues for the top-40 used models
Role: WS3   Lane: data/taxonomy, data/manual   Wave: 7
Status: todo

## Goal
Write the clues that let a buyer match an ad to the right variant.

## Acceptance criteria
- [ ] `data/taxonomy/clue_types.yaml` (build date range, power kW, battery kWh, trim name per market, type-approval/version code, VIN position, visible feature, onboard charger) with plain-language tooltip text EN + NL
- [ ] 3–5 clues per variant for the top-40 used models, each cited (source URL + date), with strength and rules_out
- [ ] Trim names mapped per market, never translated
- [ ] "Ask the seller" line templates per clue type in six languages (EN + NL complete)

## Inputs
docs/spec/variant-finder.md §3 and §5, T-044, data/seed/top40.yaml (overnight addendum 6).

## Out of scope
Plate lookup, VIN decoding beyond cited facts.

## Handoff notes

## Review
