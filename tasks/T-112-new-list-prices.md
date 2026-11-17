# T-112 A sourced new list price for every launch variant
Role: builder   Lane: WS3: data/seed/, data/manual/prices/   Wave: launch fixes (A-35)
Status: todo

## Goal
Every variant in the catalogue has its new list price, so Decision 064 can estimate a used price for any car.

## Acceptance criteria
- [ ] New list price (incl. VAT) at launch per variant, per launch country where the maker publishes it, at least one euro price (home market) otherwise; source URL (archived) + date
- [ ] Covers NL, DE, FR, BE, UK, ES, IT where available (Decision 066)
- [ ] Coverage report in the PR: % of release variants with a new price, by country; target 100 % with at least one price
- [ ] pytest green
- [ ] Verify skill run for the lane; evidence pack in the PR; `Verified:` line on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes; `## Review` line marks the A-35 finding(s) fixed

## Inputs
Decision 064, Decision 066

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-35 B2 fixed. -->
