# T-115 Budget filter uses band → estimate → new price; unpriced cars rank last
Role: builder   Lane: WS2: apps/web/src/lib/shortlist.ts, hero components   Wave: launch fixes (A-35)
Status: todo

## Goal
Budget changes the result (Decision 064).

## Acceptance criteria
- [ ] `priceFit()` uses the used band median for those build years, else the estimate (labelled), else the new price for new cars
- [ ] No price at all: never in the top 5, listed after every priced car with "price not known yet"
- [ ] Unit tests for each case; e2e on the published release: road-tripper NL €15k and €35k give different top 10s, and every top-5 car at €15k is ≤ €15k
- [ ] Cards show "estimate" with method and source in Nerd mode
- [ ] Verify skill run for the lane; evidence pack in the PR; `Verified:` line on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes; `## Review` line marks the A-35 finding(s) fixed

## Inputs
Decision 064; audits/A-35 B2

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-35 B2 fixed. -->
