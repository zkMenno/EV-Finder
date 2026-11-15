# T-035 Back-test harness for range and consumption models
Role: WS1   Lane: pipeline   Wave: 7
Status: todo

## Goal
Measure model error so Trip fit has an honest launch gate.

## Acceptance criteria
- [ ] Back-tests on NAF El Prix routes and condition-tagged tests
- [ ] Median error per top-40 used model and overall; report in audits/ (A-NN from WS0)
- [ ] Release diff check flags models whose error worsens

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

## Review
