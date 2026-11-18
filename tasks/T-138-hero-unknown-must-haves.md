# T-138 Hero: a car with no data on its profile's must-have fields is never a ranked pick
Role: builder   Lane: WS2: apps/web/src/lib/shortlist.ts, hero components (+ WS0 decides the rule; WS3 fills the Spring facelift row)   Wave: launch fixes (A-36)
Status: todo

## Goal
The road-tripper and kerbside shortlists never put a car first whose range and fast-charging figures are unknown (A-36 B1: Dacia Spring 2024 facelift is the only road-tripper and kerbside pick at €15k in NL, DE, FR, ES and IT).

## Acceptance criteria
- [ ] WS0 decides the rule (proposal in A-36 B1): a car whose value is unknown on **every** preset field of the profile (road-tripper: real range, DC km in 20 min, boot) is listed with "not known yet" after the cars with known values, without a place number, like an unpriced car (Decision 064 pattern); logged as a decision
- [ ] `presetCheck` callers implement it; unit test with a fixture row that has no range, no DC and no boot data
- [ ] Profile-fit acceptance test on the **published** release (REVIEW R4): for road-tripper and kerbside at €15k and €35k in all launch countries, every numbered card has a known real range or winter range
- [ ] WS3: `dacia-spring-gen1-facelift-65` gets its WLTP range and DC figures from the maker sheet (cited), so the row is no longer empty
- [ ] Fresh review (REVIEW.md from origin/main) passes; `## Review` marks A-36 B1 fixed

## Inputs
audits/A-36-launch-review-2.md B1; screenshots `audits/A-36-screens/hero-*-roadtripper-15k-*.png`; Decisions 050, 064, 065; launch-scope.md §1 ("hard filters first")

## Out of scope
Changing the release scores or the shortlist rules themselves (WS1 / WS0).

## Handoff notes

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-36 B1 fixed. -->
