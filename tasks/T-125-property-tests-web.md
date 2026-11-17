# T-125 Property tests for the web app (fast-check)
Role: WS2   Lane: apps/web/src/lib   Wave: process
Status: done (WS2, 2026-11-17; PR #52)

## Goal
Same as T-124 for the web logic that turns release data into what a buyer sees.

## Acceptance criteria
- [x] `fast-check` dev dependency (MIT), fixed seed in CI.
- [x] Properties, at least:
  - Round-trip: Explore/compare/shortlist URL state encode → decode = original (state.ts, shortlist.ts)
  - Invariants: hero shortlist never drops a car for missing data (Decision 055); sort is stable and total; finance/loan estimate monotonic in price and rate; price bands P25 ≤ median ≤ P75 after currency conversion
  - Every number formatter: metric units, no NaN/undefined shown, locale-correct for 6 languages
- [x] Failing examples kept as regression tests.

## Inputs
Article: property tests. T-124 for the pipeline twin.

## Handoff notes
- `apps/web/src/lib/properties.test.ts`: 21 tests, 200 cases each with seed 20261117 (fixed; `FC_SEED` / `FC_RUNS` env to explore). Also ran 2,000 cases on seeds 1, 42 and 777: all green.
- Dependency: `fast-check` 4.10.2 (MIT), dev only. Why: generates the inputs and shrinks a failure to the smallest example; nothing hand-written comes close.
- **Real bug found and fixed:** `parseVariantUsedPrices` passed through bands with P25 above the median or P75 below it, so a card could show a range that reads backwards. A quartile on the wrong side is now dropped (median shown alone; never invented). Kept as regression test 'drops a quartile on the wrong side of the median'.
- Properties: Explore state URL and storage round-trip; parsing any URL or stored junk never throws and is idempotent; hero state round-trip and `mergeHeroIntoUrl` keeps sort/view/level/pay; a car with no data qualifies for all 312 complete answer sets; removing any data from a qualifying car never rules it out (Decision 055); hero ranks 1..n, ≤ 10, one per model, best first; sort is a permutation, missing last, ordered, ties in catalogue order, idempotent; loan monthly is monotonic in price and rate, credit cost ≥ 0, deposit + principal = price; parsed bands P25 ≤ median ≤ P75 and the hero's price sits in its band; formatNumber reads back to the rounded value in all 6 locales; missing values show "—"; money shows € / £ (or the ISO code where that's the language's style: es-ES writes "0 GBP"); spec units and all 6 dictionaries are metric.
- Defaults taken: 'after currency conversion' — the web app does no conversion (bands arrive in the country's currency from WS1), so the check is on what we parse and show; the conversion itself belongs to T-124 (pipeline twin). A direction without a sort key isn't part of URL state (the URL carries it inside `sort=-key`), so the generator only makes `desc` with a key.

## Review
- PR #52 head 0d7d0ea (fresh reviewer): R0–R3, dependency, seeds, `fc.pre` 19.5–21.9 % of cases kept, mutation of the missing-data gate caught, regression fails on old parser: PASS. Should-fix (no compare round-trip) done in fix/review-followups-1117: compare tray link and compare page link → ids round-trip, plus `parseCompareIds` never throws and caps at 4.
