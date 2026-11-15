# T-081 Used price band per variant, build year and country
Role: WS1 (+WS3 manual samples)   Lane: pipeline, data/manual   Wave: 10
Status: todo

## Goal
Give every launch variant a used price band per build year in each launch country, so the hero can filter by budget.

## Acceptance criteria
- [ ] Method: new list price at registration (RDW catalogusprijs for NL, maker price lists where cited) × age/km depreciation curve per segment and country, calibrated on the free price indices (T-056 terms permitting) and on manual samples in data/manual/prices/*.yaml (source URL + date, aggregates only, no scraping, Decision 004)
- [ ] Band = P25–P75 with sample count; labelled estimate when model-based; "not enough data" below the threshold
- [ ] Back-test against manual samples: median error reported in qa.json
- [ ] Per country, per build year; currency per country (GBP for UK) converted at display only

## Inputs
docs/spec/master-spec-v2.md §8, Decisions 004, 051, research/R-29, T-056.

## Out of scope
Layer 3 sampling, listing feeds.

## Handoff notes
- WS3, 2026-11-15 (https://claude.ai/code/session_01JuyZEW2aV2H7ifmpaT5Pfr), branch t-081-manual-price-samples: Menno chose agent sampling of search-result pages only (Decision 060). 24 files in data/manual/prices/ (NL, Marktplaats): 81 build-year rows over 20 models, fixed asking prices of electric cars from the first 5 result pages of one make+model search. Shared generation years skipped (never guessed); build year 2026+ dropped (mostly new/demo stock); facelift generations of #31 left out until it merges. Loads in WS1's `load_samples` (PR #21): 81 rows, 0 problems.
- Not sampled: AutoScout24 (robots.txt disallows ClaudeBot), La Centrale and mobile.de (403, stopped), Autotrader UK (/car-search disallowed in robots.txt; model pages show too few cars). DE, FR, BE and UK still have no samples.
- Caveats: Marktplaats free-text search mixes trims and mileages; asking prices, not sale prices; small n for some years (min 5).

## Review
