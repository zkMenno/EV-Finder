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

## Review
