# T-115 Budget filter uses band → estimate → new price; unpriced cars rank last
Role: builder   Lane: WS2: apps/web/src/lib/shortlist.ts, hero components   Wave: launch fixes (A-35)
Status: merged (PR #70, #100)

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
- **Merged the updated #69 (T-114 + main incl. #56/T-097), 2026-11-17 (WS2 subagent).** No conflicts: the budget rule and the Nerd value column don't overlap. Re-checked on a fresh preview release (release 1 + pipeline-made `shortlist_scores.json` + `used_prices.json`).
- **Review fixes after the #70 fresh review (WS2 subagent, 2026-11-17), merged main (#69 squashed, #64, #65):**
  - Bands are parsed from main's `UsedPriceYearBand` fields: `basis` (falls back to method/estimate only for old files), `scope`, `curve`, `curve_fitted_on`, `source` {name,url,ref}, `date`, `list_price`, `list_source_ids`, `kept_share`. The compact band is now `[year, p25, median, p75, flags, how?]` (flags 1 estimate, 2 low confidence, 4 generation scope; `how` = those provenance fields). Client catalogue +15 KB gzip (167 KB on the preview, budget 300).
  - Nerd price text (`src/lib/price-how.ts`) is built from those fields: curve kind (fitted / fitted:<segment> / published), the countries it was fitted on (Intl region names in the page language), the curve's source name and date, list price + its source names, value kept. No fixed "research/R-40" text any more. Bands: listing count, date, source.
  - `scope: generation` bands say "Typical for this generation" on the card at every level (six languages; DE/FR/ES/IT drafts).
  - `siblingsOverBudget()`: an unpriced variant counts as over budget when its generation's known prices (else its model's) are all over the budget; compared before refine filters. A model with no price anywhere still shows, last.
  - An estimate no longer stands in for a build year that has a real band (review nit).
  - e2e: profile tests need shortlist = min(5, priced cards) and > 0 with used prices; the budget test needs non-empty €35k and €15k (presets off) shortlists, an explained empty shortlist, and checks the sibling rule against the client catalogue; a new Nerd test checks the text is the row's own.
  - **Data fact:** with the road-tripper's own presets (350 km real range, 200 km/20 min, 380 l boot) no NL car priced ≤ €15k qualifies on release-1 data, so the €15k shortlist is honestly empty there (with the "why" line); the remaining €15k cards (A6 e-tron, Model S, Macan, Spring facelift, Soul) are models with no NL price at all.
- **Open:** e2e on published release 2; release 1 lacks #65's maker list prices, so the preview has fewer prices than release 2 will.
- **Release-2 fix (WS2 subagent, 2026-11-17, branch fix/hero-unpriced-never-top5):** on release 2, NL road-tripper €15k showed 1 priced card (Dacia Spring) + 8 unpriced premium cars numbered 2-9. The cheap priced cars drop out correctly: Leaf e+ (€14,900 band) fails the profile presets (93 km/20 min < 200, 327 km < 350; release band `fallback` 14.1); Zoe Ph2 R135 (€13,000) and e-208 P21 50 kWh (€12,100) are `ruled-out` in shortlist_scores.json (gates `dc-not-terrible`, `winter-range-floor`) and fail the presets too. Fix: only priced picks get a place number (`HeroPick.rank` null for unpriced, `HeroResult.priced`); unpriced cars move to their own section "No more cars with a known price fit…" (`hero-no-price`) without numbers. B3 re-check: 5 answer sets, hero order and scores equal shortlist_scores.json.

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-35 B2 fixed. -->

WS0 subagent, 2026-11-17, f791fd6 + 331d0bf: pass; band → estimate → new price; unpriced cars never numbered (release 2: NL €15k one priced pick + unpriced list, €35k 10 priced picks). **A-35 B2 fixed** (thin €15k list is real data: cheaper cars fail the road-tripper presets).

Reviewed by QA, 2026-11-17 (A-36, release 2, 80-run hero walk): pass for B2 (€15k ≠ €35k in 20/20; 0 shortlisted cards over budget; 288 unpriced cards, none numbered). Changes needed: A-36 B1 (no-data Dacia Spring is the only €15k road-tripper pick, T-138) and S5 (unpriced premium cars at €15k).
