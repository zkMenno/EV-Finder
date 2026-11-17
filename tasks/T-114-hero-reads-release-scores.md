# T-114 Hero ranks with shortlist_scores.json from the release
Role: builder   Lane: WS2: apps/web/src/lib/shortlist*, hero components   Wave: launch fixes (A-35)
Status: todo

## Goal
One implementation of the shortlist rules: the web reads release scores (Decision 065).

## Acceptance criteria
- [ ] Hero loads `shortlist_scores.json` (via fetch-release) and sorts by its score per profile; the web no longer computes factor scores (keep the old code only as a test oracle, or delete)
- [ ] Reason line built from the release factor values (winter range, DC km, price headroom)
- [ ] Missing scores file → clear "ranking not available" state, not a silent fallback to another basis
- [ ] e2e on the published release (not fixtures) once release 2 exists
- [ ] Verify skill run for the lane; evidence pack in the PR; `Verified:` line on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes; `## Review` line marks the A-35 finding(s) fixed

## Inputs
Decision 065; audits/A-35 B3; T-069

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-35 B3 fixed. -->
