# T-033 Consumption matrix builder with fallback ladder
Role: WS1   Lane: pipeline   Wave: 7
Status: todo

## Goal
Build the per-variant consumption matrix the browser uses.

## Acceptance criteria
- [ ] 3 road bands × 5 temperature bands per variant; rung (measured/platform/physics/WLTP ratio) + confidence per cell
- [ ] Temperature curves per heater type fitted to Recurrent / El Prix ratios; car's own winter test wins
- [ ] Warm-up kWh per cold start and climb/regen factors as config, flagged estimate
- [ ] Static JSON in the release, small enough for the browser (gzip size reported)

## Inputs
docs/spec/trip-fit.md §5, Decision 013, T-030–T-032.

## Out of scope
UI.

## Handoff notes

## Review
