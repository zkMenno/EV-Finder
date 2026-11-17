# T-069 Score every released variant with the shortlist rules
Role: builder   Lane: pipeline/ev_pipeline/derive   Wave: 9
Status: merged (PR #15); fresh review via QA A-35; earlier note: WS1, 2026-11-15; built on the YAML before T-066

## Goal
Each release carries a per-variant, per-profile shortlist score with its reasons, from our own published fields.

## Acceptance criteria
- [x] Derived step reads `shortlist_rules.yaml`, writes `shortlist_score`, `shortlist_band`, `shortlist_reasons[]`, `shortlist_unknown_factors[]` per profile
- [x] Missing field → factor 0.5 and listed as unknown; a variant with more than half its weight unknown gets band `not-enough-data`
- [x] Coverage report in `coverage.md`: how many released variants have each rule field
- [x] Back-test on the release: compare bands with `menno-picks.yaml` verdicts where seed ids match; report in the release notes (not a gate yet)
- [x] pytest with fixtures; no network

## Inputs
Decision 038, research/R-32, `data/editorial/backtest_rules.py` (reference logic).

## Handoff notes
- Done (WS1, 2026-11-15): `pipeline/ev_pipeline/derive/shortlist.py` + `shortlist_params.yaml`, wired into `ev release`; writes `shortlist_scores.json` (editorial, estimate, CC BY 4.0), a coverage section in `coverage.md` and an owner-picks back-test in the release README. Decision 042.
- Shape: 18 combos per variant (3 trip profiles × home/kerbside × town/city/countryside); score, band, reason codes per combo; 0..1 factor values and unknown lists per trip profile. ~730 KB raw / 36 KB gzip on release 1's 226 rows.
- Surprise: the rule thresholds sit on ev-database's basis; ours is harsher (winter ×1.24, Wh/km ×1.155, DC ×1.42, medians over 13–15 matched picks). Bridged with `basis_scale`, thresholds untouched. Refit when the matrix or DC model changes.
- Back-test on release 1 rows + a fresh matrix: road-tripper 6 of 10 exact (60 %), 8 within one band. Misses: EV6 2024 (no 84 kWh row yet, T-068), Polestar 2 and Model Y 2022 score high (Model Y LR gen1 data looks wrong: WLTP 11.0 kWh/100 km), Enyaq 80 and Megane 2026 low.
- Neutral today for lack of data: bidi (V2L/V2H), heat_pump, one_pedal, frunk, width. Coverage per field is in coverage.md.
- Left for T-066: typed `ShortlistScoresRelease`, `unit` on rule rows, `winter_range_km` as a named field; then delete the bridge blocks in shortlist_params.yaml.
