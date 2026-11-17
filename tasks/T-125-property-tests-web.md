# T-125 Property tests for the web app (fast-check)
Role: WS2   Lane: apps/web/src/lib   Wave: process
Status: todo

## Goal
Same as T-124 for the web logic that turns release data into what a buyer sees.

## Acceptance criteria
- [ ] `fast-check` dev dependency (MIT), fixed seed in CI.
- [ ] Properties, at least:
  - Round-trip: Explore/compare/shortlist URL state encode → decode = original (state.ts, shortlist.ts)
  - Invariants: hero shortlist never drops a car for missing data (Decision 055); sort is stable and total; finance/loan estimate monotonic in price and rate; price bands P25 ≤ median ≤ P75 after currency conversion
  - Every number formatter: metric units, no NaN/undefined shown, locale-correct for 6 languages
- [ ] Failing examples kept as regression tests.

## Inputs
Article: property tests. T-124 for the pipeline twin.

## Handoff notes

## Review
