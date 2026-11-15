# T-069 Score every released variant with the shortlist rules
Role: builder   Lane: pipeline/ev_pipeline/derive   Wave: 9
Status: todo (after T-066)

## Goal
Each release carries a per-variant, per-profile shortlist score with its reasons, from our own published fields.

## Acceptance criteria
- [ ] Derived step reads `shortlist_rules.yaml`, writes `shortlist_score`, `shortlist_band`, `shortlist_reasons[]`, `shortlist_unknown_factors[]` per profile
- [ ] Missing field → factor 0.5 and listed as unknown; a variant with more than half its weight unknown gets band `not-enough-data`
- [ ] Coverage report in `coverage.md`: how many released variants have each rule field
- [ ] Back-test on the release: compare bands with `menno-picks.yaml` verdicts where seed ids match; report in the release notes (not a gate yet)
- [ ] pytest with fixtures; no network

## Inputs
Decision 038, research/R-32, `data/editorial/backtest_rules.py` (reference logic).
