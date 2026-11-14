# T-006 Validate release
Role: builder   Lane: pipeline/ev_pipeline/release   Wave: 2
Status: todo

## Goal
Range checks and release folder with catalogue.json + Parquet + diff.

## Acceptance criteria
- [ ] Range checks for kWh, km, kW, price
- [ ] data/releases/<n>/catalogue.json + .parquet
- [ ] Diff against previous release
- [ ] Tests cover it (with fixtures, no live network calls)

## Inputs
Overnight brief (prototype 1), AGENTS.md, DECISIONS.md.

## Out of scope
Anything outside the lane above. No auth, no pg-boss, no Postgres tonight.

## Handoff notes

## Review
