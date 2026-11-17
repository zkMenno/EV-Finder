# T-031 Trip fit seed: speed profiles, usage profiles, heater types, heat_pump
Role: WS3   Lane: data/taxonomy, data/seed   Wave: 7
Status: review (WS3, 2026-11-15; launch part only)

## Goal
Seed the editable tables that drive Trip fit.

## Acceptance criteria
- [ ] speed_profiles per launch country (e.g. NL 100 by day, FR 130, DE advisory 130, UK 70 mph) with sources
- [ ] usage_profiles weights from spec §6 as rows
- [x] heater_types rows; heat_pump for the top-40 used models incl. option status, cited (partly: see handoff)

## Inputs
docs/spec/trip-fit.md §4, §6, T-030.

## Out of scope
Model code.

## Handoff notes
2026-11-15, WS3 (https://claude.ai/code/session_01JuyZEW2aV2H7ifmpaT5Pfr). Launch part only (Decision 051): speed_profiles and usage_profiles are Trip fit, parked.
- `data/manual/heat-pump/r21-heat-pump.yaml`: 16 cited `heat_pump` facts (14 from R-21, plus Renault 5 and Ioniq 6 from maker pages). Only whole-generation rows; not-disclosed never entered. 10 partial-year or per-variant rows listed in the file header, waiting for a `years` span on manual facts (asked WS1) or variant splits. `ev manual check`: 0 errors. Internal only until Q-008.
- `data/taxonomy/temperature_bands.yaml` (5 rows) and `heater_types.yaml` (3 rows): six-language labels + tooltips; numbers copied from WS1's `consumption_params.yaml` v0.1 (load_params picks them up, verified). Added to `validate_taxonomy.py` (0 errors). DE/FR/ES/IT machine-drafted.
- Decision 059. ID.5 fact waits for T-068 (PR #31).

## Review
