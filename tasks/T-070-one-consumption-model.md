# T-070 Real range and DC km from the calibrated consumption matrix
Role: builder   Lane: pipeline/ev_pipeline/derive   Wave: 9
Status: todo (proposed by WS1, 2026-11-15; needs WS0 to tag it on BOARD)

## Goal
One consumption model behind every range and charging number, so the catalogue, Trip fit and the shortlist agree.

## Acceptance criteria
- [ ] `real_range_km` = usable kWh / the matrix's mild mixed consumption (rung from the cells), replacing the body-ratio rung in derive/metrics.py; old values kept in the diff for review
- [ ] `consumption_motorway_kwh_100km` and `dc_km_per_10min` / `dc_km_per_20min` use the matrix motorway cell (battery basis) when there is no measured fact
- [ ] `profile_fields` ratios in qa.json land within ±2 % for every variant with a matrix entry
- [ ] EPA range back-test (A-30) not worse than 7.8 % median abs error; regressions listed
- [ ] T-069 `basis_scale` refit noted for whoever owns the shortlist params (the DC and winter scales move)
- [ ] pytest with fixtures; no network

## Inputs
audits/A-30 (follow-up 2), qa.json `profile_fields`, Decision 041, derive/consumption.py, derive/metrics.py.

## Out of scope
The temperature step itself (needs winter tests, Q-059); DC curve shapes.

## Handoff notes

## Review
