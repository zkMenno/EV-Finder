# T-115 Budget filter uses band → estimate → new price; unpriced cars rank last
Role: builder   Lane: WS2: apps/web/src/lib/shortlist.ts, hero components   Wave: launch fixes (A-35)
Status: review (WS0 subagent, 2026-11-17, PR #70)

## Goal
Budget changes the result (Decision 064).

## Acceptance criteria
- [ ] `priceFit()` uses the used band median for those build years, else the estimate (labelled), else the new price for new cars
- [ ] No price at all: never in the top 5, listed after every priced car with "price not known yet"
- [ ] Unit tests for each case; e2e on the published release: road-tripper NL €15k and €35k give different top 10s, and every top-5 car at €15k is ≤ €15k
- [ ] Cards show "estimate" with method and source in Nerd mode
- [ ] Verify skill run for the lane; evidence pack in the PR; `Verified:` line on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes; `## Review` line marks the A-35 finding(s) fixed

## Inputs
Decision 064; audits/A-35 B2

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes
- **Builds on T-114 (PR #69)**; this branch was cut from it. Merge #69 first.
- **`priceFit()` order (Decision 064):** (1) a real used band for those build years: the variant's counted-listing bands (`used_prices.json`, `method: samples`), else the generation's sourced bands (`Catalogue.used_prices`); (2) our used price estimate (variant `method: model` bands); (3) the new price, only for cars `on_sale_new`. Used and new both fitting (condition "any"): the cheaper is shown. Returns `status: fits | over | unpriced`; `over` drops the car (budget = hard filter on the median/estimate), `unpriced` keeps it.
- **Unpriced cars** are listed after every priced car and never in "Your shortlist": `HeroResult.shortlistN` = priced picks, at most 5. Per model, a priced version beats a higher-scoring unpriced one. With no priced car, the hero says the shortlist is empty and why (EN/NL/DE/FR). Applied with or without a budget (Decision 064 is unconditional).
- **Labels:** cards carry `data-price` / `data-price-basis` (band / estimate / new / none). Estimates keep the "Estimate: …" note; Nerd mode adds the method and source ("new list price €52,300 × 58 % of value kept … List price source: RDW Open Data"). For this the compact band tuple gained three optional fields (list price, kept share, sources); `parseVariantUsedPrices` reads `list_price`, `kept_share`, `list_source_ids` / `source.name`.
- **Reversible default:** a real band year that is over budget doesn't block an estimate year that fits (different build year, the card says which years).
- **Evidence data:** release 1 has neither file, so the budget e2e skips there. Locally I built a preview release = release 1 + `shortlist_scores.json` + `used_prices.json`, both made by the pipeline's own code from release 1 rows/facts (99 variants with model bands, as WS1 reported for #21). There, NL road-tripper €15k: shortlist empty (no priced road-tripper ≤ €15k; all 10 cards "price not known yet"); €35k: 8 priced estimates (€26,800–€34,600) then 2 unpriced. On real release 2 the numbers will differ.
- **Open:** e2e on the published release 2 (runs automatically once it has both files). ES/IT strings come with T-117.

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-35 B2 fixed. -->
