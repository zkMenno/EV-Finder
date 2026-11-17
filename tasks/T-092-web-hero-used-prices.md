# T-092 Hero: used price per build year from used_prices.json
Role: WS2   Lane: apps/web   Wave: 10
Status: review (WS2, 2026-11-15, branch t-092-hero-used-prices, stacked on T-080)

## Goal
Launch scope §1: each hero card shows the used price band for the build years that fit the budget (T-081 data, WS1 PR #21).

## Acceptance criteria
- [x] Reads optional `used_prices.json` (variants[].bands[country][] per build year); missing/broken = no bands
- [x] Compact bands in the client catalogue; budget picks the newest build year within budget; card shows years + P25–P75
- [x] `method: model` labelled estimate; low confidence says why
- [x] fetch-release fetches the file by default

## Handoff notes
- 2026-11-15 WS2: `src/lib/variant-prices.ts`, `catalogue.variantUsedPrices()`, `shortlist.ts variantFit()`. Per-variant bands win over generation `used_prices`. Effective once #21 merges and a release with the file is published + the site rebuilt.

## Review
