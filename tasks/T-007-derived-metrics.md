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

**Reviewer (fresh agent), 2026-11-15. Verdict: pass, with notes.**

Formulas checked against the brief and Decision 009, in code (`derive/metrics.py`) and on all 210 rows of release 1 (`tests/test_real_release.py`):
- `ac_km_per_h = ac_kw / consumption × 100` holds on every row.
- `dc_km_per_10/20min = min(dc_avg × N/60, net × 0.7) / motorway consumption × 100` holds, with motorway = WLTP consumption × 1.30 wherever it is an estimate.
- Every `real_range_km` names its rung, and the 120 `body-ratio` rows are flagged `estimate` with the model-estimate source.
- Provisional ratios are documented in the module docstring and in provenance notes.
- The DC ranking input (`dc_km_per_20min`) uses motorway consumption, not peak kW.

Notes
1. `rows.py:319-325` applies ×1.30 to *any* `consumption_kwh_100km`, and the note says "WLTP consumption" even when the value came from EEA's registration-weighted average (see T-004) or a seed figure. Word the note after the actual source, or apply the ratio only to WLTP-cycle values. Low.
2. Every dc_avg/dc_minutes/peak_held value tonight comes from the generic default curve (coverage.md: 83% estimate-only). That is fine while it's labelled, but the UI must show "estimate" clearly, especially on the DC ranking.
3. `registered_count_nl` is a generation total on every variant (documented, Q-023). Because of the matching errors in T-005 (e-tron GT, Leaf gen3, Kona), several of these totals are wrong. That's an input problem, not a derive bug.
4. Quality tier: 210/210 `single-source`. Correct given Q-019.
