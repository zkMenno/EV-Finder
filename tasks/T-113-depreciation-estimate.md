# T-113 Used price estimate from new price × depreciation curve
Role: builder   Lane: WS1: pipeline/ev_pipeline/derive/   Wave: launch fixes (A-35)
Status: todo

## Goal
Cars without a real used band get a labelled used price estimate per build year and country (Decision 064).

## Acceptance criteria
- [ ] Depreciation curve by age (and by segment if the data supports it), fitted on our own used samples (T-081, price indices T-056) vs new price; if too few points, a published curve with citation. Parameters in a `*_params.yaml` (gate file) with the fit quality
- [ ] Back-test section in qa.json: median error of the estimate vs real bands where both exist (rule G-10)
- [ ] `used_prices.json` rows carry `basis: band | estimate`, method, source and date; estimates never overwrite a real band
- [ ] Dry run on latest release rows first (G-10)
- [ ] Verify skill run for the lane; evidence pack in the PR; `Verified:` line on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes; `## Review` line marks the A-35 finding(s) fixed

## Inputs
Decision 064; T-081, T-056

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-35 B2 fixed. -->
