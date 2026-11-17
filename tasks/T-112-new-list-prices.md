# T-112 A sourced new list price for every launch variant
Role: builder   Lane: WS3: data/seed/, data/manual/prices/   Wave: launch fixes (A-35)
Status: review (WS0 subagent, 2026-11-17, PR #65)

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
- **Shape:** the existing schema FactField `price_new` (Money per Country) as manual facts, in `data/manual/new-prices/` (not `prices/`: that topic has its own loader for used-price aggregates, `OWN_LOADER_TOPICS`).
- **Done:** 72 sourced new prices: 71 BE (Autotijd.be copies of the importer price lists, incl. VAT) and 1 DE (Hyundai press release). Coverage of release-1 variants with at least one new price: **46.0% → 77.4%** (all 226) and **50.0% → 84.8%** (204 variants on sale 2020 or later).
- **Rule:** the earliest list that carries the variant's powertrain, cheapest trim. Where that list is later than the variant's first year, `confidence: low` and the notes say so (Autotijd's archive starts about 2021-2022).
- **Doesn't ship yet:** source `manual` is blocked until Q-008 (Menno). Decision 064 estimates need either Q-008 answered or a registered source for these prices.
- **Schema gaps (WS0):** (1) `Country` enum is `NL, DE, FR, BE, UK`; Decision 066 needs `ES` and `IT` before any ES/IT price fact validates. (2) Decision 064 depreciates by age, so a launch price needs its price-list date. `Fact.observed_at` exists, but the manual loader (`FACT_KEYS`, WS1) doesn't accept `observed_at`. The list month is in `locator` and `source_name` for now.
- **Left (2020+, 31 variants, no price yet):** audi-q6-e-tron-gen1-quattro-sportback, bmw-i3-i01-120ah, bmw-i3-i01-i3s, bmw-i4-g26-xdrive40, byd-atto-3-gen1-standard-range, byd-atto-3-gen1-standard-range-2025, cupra-born-gen1-45kwh, cupra-tavascan-gen1-vz, dacia-spring-gen1-essential-comfort, fiat-500e-332-abarth, ford-mustang-mach-e-gen1-premium, ford-puma-gen-e-gen1-base, hyundai-ioniq-5-gen1-awd (merged into the 77.4 kWh AWD row by T-110), hyundai-ioniq-electric-gen1-38kwh, jaguar-i-pace-x590-ev400, kia-soul-ev-sk3-39kwh, kia-soul-ev-sk3-64kwh, mercedes-eqb-gen1-300-4matic-7-seater, mercedes-eqb-gen1-350-4matic-7-seater, mercedes-eqb-gen1-7-seater, mg-mg4-gen1-standard-long-range (power doesn't match any BE row), mg-zs-ev-gen1-44kwh, nissan-leaf-ze1-62-kwh, porsche-taycan-gen1-turbo-gt, renault-5-e-tech-gen1-40-kwh, tesla-model-3-gen1-sr-plus, tesla-model-s-facelift-raven-long-range, tesla-model-y-juniper-long-range-rwd, tesla-model-y-juniper-performance, volkswagen-id3-gen1-gtx, volkswagen-id7-gen1-tour. Plus 20 pre-2020 variants (Model S gen1/facelift, Zoe ph1, Leaf ze0, i3 60/94 Ah, Soul EV PS, Ioniq 28 kWh, 500e US, smart 451).
- **Not done:** NL/DE/FR/UK/ES/IT from maker lists for the 71 BE variants (NL 93 and FR 14 come from RDW/ADEME). web.archive.org is blocked from this environment and tesla.com returns 403, so archived maker lists couldn't be read. Next session: maker press releases per market (hyundai.news, volkswagen-newsroom.com, media.volvocars.com) and the UK price lists.
- Scraper helper used (not committed): fetched about 80 Autotijd pages once, 1.5 s apart. robots.txt allows `/prijzen/`.

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-35 B2 fixed. -->
