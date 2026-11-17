# T-094 Variant pages: used price by build year
Role: WS2   Lane: apps/web   Wave: 10
Status: review (WS2, 2026-11-15, branch t-094-variant-used-prices, stacked on T-092)

## Goal
Launch scope §2: model/variant pages show the used price band per country; with T-081's per-variant, per-build-year bands the variant page lists them year by year.

## Acceptance criteria
- [x] Variant page "Used price in {country}": one line per build year (newest first), P25–P75, samples when counted
- [x] Estimate note for model bands; `*` + note for low confidence
- [x] Falls back to the generation band (PriceBand) when the release has no per-variant bands
- [x] Checked by hand against a temp release with a sample used_prices.json (variant page + hero re-ranking)

## Handoff notes
- 2026-11-15 WS2: `ev/_components/UsedByYear.tsx`. No e2e yet: release 1 has no used_prices.json; add one when the first release with the file is published.

## Review
