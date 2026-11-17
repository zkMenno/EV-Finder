# T-116 Rebuild and publish release 2; latest = 2
Role: builder   Lane: WS1 (+ WS4 if staging data is needed): pipeline/, data/releases/   Wave: launch fixes (A-35)
Status: todo

## Goal
The site runs on data that includes every launch data task.

## Acceptance criteria
- [ ] After T-110, T-111, T-112, T-113 and #44/#51 (T-123 release diff, T-127 `ev verify`) are merged: rebuild from the same inputs; raw public sources fetched on a session or temporary machine, never the shared server (Decision 006)
- [ ] Release 2 has `used_prices.json` (bands + estimates), `shortlist_scores.json`, winter range, T-068 seed, T-031 heat pump facts, the Model Y fix; the plausibility gate passes
- [ ] Release diff vs 1 (T-123) in the PR with every change approved; manifest committed → Data publish workflow → `latest` = 2
- [ ] A-35 S7 (T-064 part 2): release files no longer tracked in git
- [ ] Hero walk on release 2: winter range and a used band on most NL cards
- [ ] Verify skill run for the lane; evidence pack in the PR; `Verified:` line on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes; `## Review` line marks the A-35 finding(s) fixed

## Inputs
audits/A-35 B1, S7; Decision 035, 044

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-35 B1, S7 fixed. -->
