# T-113 Used price estimate from new price × depreciation curve
Role: builder   Lane: WS1: pipeline/ev_pipeline/derive/   Wave: launch fixes (A-35)
Status: review (WS0 subagent, 2026-11-17, PR #64 code + PR #63 params)

## Goal
Cars without a real used band get a labelled used price estimate per build year and country (Decision 064).

## Acceptance criteria
- [ ] Depreciation curve by age (and by segment if the data supports it), fitted on our own used samples (T-081, price indices T-056) vs new price; if too few points, a published curve with citation. Parameters in a `*_params.yaml` (gate file) with the fit quality
- [ ] Back-test section in qa.json: median error of the estimate vs real bands where both exist (rule G-10)
- [ ] `used_prices.json` rows carry `basis: band | estimate`, method, source and date; estimates never overwrite a real band
- [ ] Dry run on latest release rows first (G-10)
- [ ] Verify skill run for the lane; evidence pack in the PR; `Verified:` line on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes; `## Review` line marks the A-35 finding(s) fixed

## Inputs
Decision 064; T-081, T-056

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes
- WS1 (WS0 subagent), 2026-11-17. Stacked on T-111 (#62): needs its sample source gate. Code: `pipeline/ev_pipeline/derive/depreciation.py` (fit + hold-out back-test), `commands/used_price.py` (`ev used-price fit --release N --as-of D`, dry run, prints the `fitted:` block), `derive/used_price.py` (curve choice, row provenance). Params (gate file): PR #63 adds `fit:` thresholds, the published curve's citation and the `fitted:` block.
- Curve: value kept = a·exp(−k·age), least squares on ln(share); age from mid build year. Fitted on release 1 + the 106 gated sample rows (Marktplaats NL, 2dehands BE): 85 points, 19 generations, ages 1.4–9.4, a = 0.884, k = 0.115 (3 years 62.5 %, 5 years 49.7 %), R² (log) 0.72. Segment curves only with ≥ 15 points and ≥ 5 generations of their own: only J-medium qualifies, and it is almost the same (k 0.1153).
- Back-test (G-10), leave one generation out: fitted median abs error **9.8 %** (median error +2.8 %, 67 % within 15 %) vs published DAT/R-40 curve **13.9 %** (median −13.7 %: too low). Worst: Fiat 500e 2021 −27 %, Leaf ZE1 2019 +27 %, Q4 BE 2022 +26 %. In used_prices.json → qa.json `backtest_used_prices.holdout`.
- Fallback: without a `fitted` block the published curve applies, cited as DAT 3-year BEV 51.5 % (autohaus.de, 28 Sep 2026, checked 2026-11-17; other ages per research/R-40). No archived copy made (archive.org save is a form submit).
- Rows: `basis: band | estimate`; estimates add `curve` (fitted / fitted:<segment> / published), `source`, `date`; bands add `date` (observed_at) and `source_id`. `method` keeps model/samples so the web reader is unchanged. Estimates never replace a band (test).
- Dry run on release 1 rows (G-10): 99 of 226 variants have bands (1,314 estimates; 0 variant-level bands, because every sample is per generation). Coverage is limited by new prices: T-112 (WS3) lifts it; then rerun `ev used-price fit` and refit in a params PR.
- Choice (reversible): generation-level sample bands stay in `generation_bands` (now `basis: band`), not spread onto variants; a generation median across trims would misprice cheap and dear trims alike.
- Schema: `used_prices.json` has no schema in packages/schema (only `UsedPriceBand` for generation bands, which the current file doesn't fully match). Proposed shape for WS0 in the PR body.

- WS1 (WS0 subagent), 2026-11-17, fresh-review fixes (#64 review on 03c857f):
  - D3 must-fix: the hold-out now runs the visitor's path per fold: `fit_curves` (same thresholds; a thin fold falls back to published) → `choose_curve` (segment curve) → `kept_share` on the yearly table → each variant's list price → `used_price.shown_band` (the function the release uses: rounded median, P25/P75). Release 1: fitted **10.6 %** median abs error (was reported 9.8 % on the continuous curve), median +1.9 %, **57.6 %** of real medians inside the shown P25–P75; published 13.7 %, 36.5 % in band. Folds used `fitted` 48, `fitted:J-medium` 37. Reported as is, nothing tuned. A test pins hold-out band == published band for the held-out generation.
  - Decision 069: a variant without its own sample band takes its generation's band (same build year, country, currency) as `basis: band`, `scope: generation`; variant samples get `scope: variant` and win; newest sample wins on duplicates. Release 1: 318 variant rows on 90 variants now show a real band (NL 229, BE 89); variants with any band 99 → 142. Side effect to know: the generation median covers all trims (EV6 58 RWD NL 2021 shows €28,400 band, was €21,400 estimate).
  - New fields (schema, WS0): `scope` (variant | generation) on band rows; `curve_fitted_on` (list of country codes, e.g. ["BE","NL"]) on estimate rows from a fitted curve. Until WS0's schema change, these are the only ajv/jsonschema rejections of the dry-run file (1,155 + 318).
  - Nit: ages below the fitted age range are low confidence too. coverage.md shows generation bands and in-band share.
  - Open: the params gate file's `fitted.holdout` block still holds the old 9.8 % numbers (gate file, own PR: rerun `ev used-price fit`). Manual price_new facts had no year: fixed in PR #74 (fix/manual-price-year); T-112/T-118 rows need `year:` lines to count.


## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-35 B2 fixed. -->
