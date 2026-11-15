# T-007 Derived metrics
Role: builder   Lane: pipeline/ev_pipeline/derive   Wave: 2
Status: review

## Goal
AC km/h, DC km per 10 min, real-range ladder, quality tier, change markers.

## Acceptance criteria
- [x] Formulas from the brief with tests
- [x] Each real-range value names its rung
- [x] Provisional ratios documented
- [x] Tests cover it (with fixtures, no live network calls)

## Inputs
Overnight brief (prototype 1), AGENTS.md, DECISIONS.md.

## Out of scope
Anything outside the lane above. No auth, no pg-boss, no Postgres tonight.

## Handoff notes

**Done (builder, 2026-11-15).** Code: `pipeline/ev_pipeline/derive/` (metrics, rows, links).
Tests: `tests/test_derive.py` (worked numbers for every formula).
- Consumption estimate, net = 0.93 × gross fallback, WLTP ≈ EPA × 1.12, ac_km_per_h,
  real-range ladder (owner → exact-test → sibling → brand×body×drivetrain → body ratio with
  awd −0.02, PROVISIONAL). Tonight every real range is `body-ratio` (120) or none (90).
- Charging (Decision 009): curve integration over 10–80 % (dc_avg, dc_minutes, dc_peak_held);
  without a curve a PROVISIONAL default shape (≈0.67 × peak, Q-018); motorway consumption
  = WLTP × 1.30 (estimate); dc_km_per_10/20min capped at the 10–80 % window;
  dc_peak_kw_is_claim (OpenEV/seed = claims).
- Decision 010: pack values inherited unless the variant has its own fact ("inherited from pack
  <id>"); voltage class from nominal_v via data/taxonomy/voltage_classes.yaml (explicit link
  class wins); fast_on_400v (Q-020); charge_100_daily from the chemistry row.
- Every non-null number has provenance (tested); estimates carry `estimate: true` and the
  `model-estimate` source. Tier: 0 sourced, 210 single-source (no second battery source; Q-019).
- registered_count_nl is the generation total on every variant (Q-023).

Release 1 published from real staging (openev 1229, rdw 3124, eea 3430 records) + seed: 210 rows,
56 generations, 6554 facts, catalogue.json 1.96 MB raw / 96 KB gzipped. Run: see pipeline/README.md
"Run the pipeline". Checks green: `uv run pytest` (154), `ruff check .`, `ruff format --check .`.
Includes coordinator addenda: Decision 009 (field_sources policy, conflicts.csv, licence gate,
coverage.md, charge curves) and Decision 010 (platforms, packs, voltage, taxonomy).
Open questions raised: Q-014 to Q-023 in QUESTIONS.md.

## Review
