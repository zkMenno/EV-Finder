# T-081 Used price band per variant, build year and country
Role: WS1 (+WS3 manual samples)   Lane: pipeline, data/manual   Wave: 10
Status: merged (PR #21, #29, #38); fresh review via QA A-35; earlier note: WS1, 2026-11-15

## Goal
Give every launch variant a used price band per build year in each launch country, so the hero can filter by budget.

## Acceptance criteria
- [x] Method: new list price at registration (RDW catalogusprijs for NL, maker price lists where cited) × age/km depreciation curve per segment and country, calibrated on the free price indices (T-056 terms permitting) and on manual samples in data/manual/prices/*.yaml (source URL + date, aggregates only, no scraping, Decision 004)
- [x] Band = P25–P75 with sample count; labelled estimate when model-based; "not enough data" below the threshold
- [x] Back-test against manual samples: median error reported in qa.json (wired; no samples exist yet)
- [x] Per country, per build year; currency per country (GBP for UK) converted at display only

## Inputs
docs/spec/master-spec-v2.md §8, Decisions 004, 051, research/R-29, T-056.

## Out of scope
Layer 3 sampling, listing feeds.

## Handoff notes
- Done (WS1, 2026-11-15): `pipeline/ev_pipeline/derive/used_price.py` + `used_price_params.yaml`, wired into `ev release`: `used_prices.json`, coverage section, `qa.json backtest_used_prices`. Decision 043, research/R-40.
- Release 1 data: 99 of 226 variants get a band (NL/BE 326 model bands, DE 336, FR 326; UK 0: no UK list prices). Spot checks: EV6 77 kWh RWD 2022 NL ≈ €24.1k, Zoe R135 2020 NL ≈ €13.6k (plausible, not verified against listings).
- Not done: the back-test has no samples to run on (none exist). Who collects them is with WS0/Menno.
- Surprise: the price facts carry `record_year`, so the band uses the list price of that build year (RDW first-registration year), not today's price.
- WS3, 2026-11-15 (https://claude.ai/code/session_01JuyZEW2aV2H7ifmpaT5Pfr), branch t-081-manual-price-samples: Menno chose agent sampling of search-result pages only (Decision 060). 24 files in data/manual/prices/ (NL, Marktplaats): 81 build-year rows over 20 models, fixed asking prices of electric cars from the first 5 result pages of one make+model search. Shared generation years skipped (never guessed); build year 2026+ dropped (mostly new/demo stock); facelift generations of #31 left out until it merges. Loads in WS1's `load_samples` (PR #21): 81 rows, 0 problems.
- Not sampled: AutoScout24 (robots.txt disallows ClaudeBot), La Centrale and mobile.de (403, stopped), Autotrader UK (/car-search disallowed in robots.txt; model pages show too few cars). DE, FR, BE and UK still have no samples.
- Caveats: Marktplaats free-text search mixes trims and mileages; asking prices, not sale prices; small n for some years (min 5).

## Review
- Reviewed by QA, 2026-11-17 (main @ d086d49, REVIEW.md draft R0–R3 + triggered D items): changes needed — used_prices.json is not in release 1 (0 of 320 hero cards show a used band, A-35 B1); sample sources lack sources.yaml entries (S2).
