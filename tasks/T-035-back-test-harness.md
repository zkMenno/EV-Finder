# T-035 Back-test harness for range and consumption models
Role: WS1   Lane: pipeline   Wave: 7
Status: review (WS1, 2026-11-15; El Prix routes wait for permission)

## Goal
Measure model error so Trip fit has an honest launch gate.

## Acceptance criteria
- [ ] Back-tests on NAF El Prix routes and condition-tagged tests
- [x] Median error per top-40 used model and overall; report in audits/ (A-NN from WS0)
- [x] Release diff check flags models whose error worsens

## Inputs
docs/spec/trip-fit.md §5 (Validation gate), T-033.

## Out of scope
Tuning the UI.

## Handoff notes
- 2026-11-15 (overnight, pipeline builder): **skeleton only**. `pipeline/ev_pipeline/backtest/harness.py`
  scores `mild-mixed` condition-tagged tests leave-one-out per variant over `derive/metrics.real_range`
  and reports median abs % error overall / body / brand / year band / rung / model, plus the 10 worst
  and a regression guard (> 3 points vs the previous qa.json). It writes into qa.json `backtest`; that
  section is `skipped` tonight (no licence-cleared real tests). Fixtures: `pipeline/tests/fixtures/backtest/`
  (synthetic). Still open: NAF El Prix route ingest, a per-top-40 report in audits/, and the Trip fit
  consumption model (T-033). See Q-059.

- **WS1, 2026-11-15 (PR `t-035-backtest-epa`).** Real, licence-clean inputs exist only from
  EPA (fueleconomy.gov), so `backtest/epa.py` adds a **proxy** back-test next to the
  skeleton: real range vs EPA adjusted range (60 variants, median 7.6 %, bias −1 %) and the
  consumption model's wltp-ratio rung vs EPA city/highway (50 variants, 100 comparisons).
  Per model, per body, top-40 (21 of 40 models with data), worst cases, regressions
  (> 3 points per model vs previous qa.json). Written to qa.json `backtest_epa` every
  release (report only), audit `audits/A-30-backtest-epa.md` (generator:
  `python -m ev_pipeline.backtest epa-report data/releases/<n>`).
- Finding: the consumption model's wltp-ratio rung read 21.8 % lower than EPA (median error
  22.8 %), so cars with EPA tests looked worse than cars without. Calibrated
  `consumption_params.yaml` (town ×1.26, rural ×1.31, motorway drag step 1.18 from the
  adjusted highway figure) → 6.1 %, bias +0.3 % (in-sample, stated in A-30).
- Criterion 1 (El Prix routes) stays open: NAF is waiting_permission (Q-059).
- Worst range cases point at US/EU matching (Ioniq 5 58 kWh −35 %, Mini SE +38 %): worth a
  look by whoever owns matching (WS1 later / T-051).

## Review
