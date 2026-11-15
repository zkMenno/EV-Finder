# T-033 Consumption matrix builder with fallback ladder
Role: WS1   Lane: pipeline   Wave: 7
Status: review (WS1, 2026-11-15)

## Goal
Build the per-variant consumption matrix the browser uses.

## Acceptance criteria
- [x] 3 road bands × 5 temperature bands per variant; rung (measured/platform/physics/WLTP ratio) + confidence per cell
- [ ] Temperature curves per heater type fitted to Recurrent / El Prix ratios; car's own winter test wins
- [x] Warm-up kWh per cold start and climb/regen factors as config, flagged estimate
- [x] Static JSON in the release, small enough for the browser (gzip size reported)

## Inputs
docs/spec/trip-fit.md §5, Decision 013, T-030–T-032.

## Out of scope
UI.

## Handoff notes
**WS1, 2026-11-15 (PR `t-033-consumption-model`).**
- `derive/consumption.py` + `derive/consumption_params.yaml` → `consumption_matrix.json`.
  Cells follow the schema's ConsumptionModel/ConsumptionCell; validated in tests.
- Rungs: measured (EPA tests), physics (motorway from EPA highway × drag factor), wltp-ratio.
  `platform` rung not built (needs platform-level tests).
- 🟡 Temperature curves are physics-shaped defaults (heating W/°C, COP, traction k), NOT yet
  fitted to Recurrent / El Prix (no licence-clean data). "Car's own winter test wins" is
  wired through test_ids when such tests exist; none today.
- Warm-up kWh per heater type, regen 0.6, drivetrain 0.88: config, confidence low.
- Size: 57 KB gzip for 198 variants (reported in coverage.md + run log).
- For WS2: replace `src/fixtures/consumption-matrix.sample.json` with the release file;
  shape note in WS2's INBOX. Schema def for the whole file requested from WS0.

## Review
