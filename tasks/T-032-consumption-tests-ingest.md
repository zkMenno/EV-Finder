# T-032 Condition-tagged consumption tests ingest
Role: WS1   Lane: pipeline   Wave: 7
Status: review (WS1, 2026-11-15)

## Goal
Load consumption and range tests with their conditions so the model can use measured values first.

## Acceptance criteria
- [ ] Adapters for licence-clean sources (ADAC, NAF El Prix facts with credit, Spritmonitor once permitted); Bjørn Nyland stays waiting_permission
- [x] Each test stores speed, temperature, wheels, source, date
- [x] Fixtures only in tests

## Inputs
docs/spec/trip-fit.md §5, docs/spec/source-matrix.md, T-030.

## Out of scope
The model builder (T-033).

## Handoff notes
**WS1, 2026-11-15 (PR `t-033-consumption-model`, with T-033).**
- Licence-clean today: EPA city/highway from fueleconomy.gov only. ADAC is blocked (no
  licence), NAF El Prix, Spritmonitor and Bjørn Nyland are waiting_permission, so no adapters
  for them (criterion 1 partly: the shape is ready; each becomes a `*.consumption_tests.jsonl`
  writer when permission lands).
- `fueleconomy` normalise writes ConsumptionTest rows (speed, band, lab temperature 23.9 °C,
  tyre season not disclosed, wall basis, source, retrieved date, confidence, note that EPA
  label values are 5-cycle adjusted). Wheels: EPA rows don't say; left out.
- Live: 3,368 tests from 1,684 BEV rows; 902 attach to 75+ variants in release 1.

## Review
