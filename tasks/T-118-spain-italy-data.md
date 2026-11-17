# T-118 Spain and Italy: country config, finance defaults, links, prices
Role: builder   Lane: WS3 (+ WS1 for price data): config/countries/, data/taxonomy/finance_profiles.yaml, data/manual/, templates   Wave: launch fixes (A-35)
Status: todo

## Goal
Spain and Italy have everything the other launch countries have (Decision 066).

## Acceptance criteria
- [ ] `config/countries/es.yaml` and `it.yaml`: euro, locale, default language es / it
- [ ] Finance defaults with a sourced typical APR and the CCD2 warning in Spanish and Italian
- [ ] Marketplace search link templates (link-outs only), checked like T-041
- [ ] Used price bands: price indices or samples where robots and terms allow (Decision 060), otherwise the Decision 064 estimate; new prices from T-112
- [ ] Verify skill run for the lane; evidence pack in the PR; `Verified:` line on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes; `## Review` line marks the A-35 finding(s) fixed

## Inputs
Decision 066, 060, 064

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-35 B5 fixed. -->
