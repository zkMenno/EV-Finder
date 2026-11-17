# T-114 Hero ranks with shortlist_scores.json from the release
Role: builder   Lane: WS2: apps/web/src/lib/shortlist*, hero components   Wave: launch fixes (A-35)
Status: merged (PR #69)

## Goal
One implementation of the shortlist rules: the web reads release scores (Decision 065).

## Acceptance criteria
- [ ] Hero loads `shortlist_scores.json` (via fetch-release) and sorts by its score per profile; the web no longer computes factor scores (keep the old code only as a test oracle, or delete)
- [ ] Reason line built from the release factor values (winter range, DC km, price headroom)
- [ ] Missing scores file → clear "ranking not available" state, not a silent fallback to another basis
- [ ] e2e on the published release (not fixtures) once release 2 exists
- [ ] Verify skill run for the lane; evidence pack in the PR; `Verified:` line on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes; `## Review` line marks the A-35 finding(s) fixed

## Inputs
Decision 065; audits/A-35 B3; T-069

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes
- **What changed.** `src/lib/release-scores.ts` parses `shortlist_scores.json` (schema `ShortlistScoresRelease`); `catalogue.shortlistScores()` reads it next to `catalogue.json`, like `used_prices.json`. `fetch-release.mjs` now fetches it by default. Each Explore row carries a compact `shortlist` (`s` combo → [score, band, ...reason codes], `f` factor 0..1, `u` unknown, `d` derived winter range / real Wh/km); the client catalogue has `scores: true|false`.
- **One implementation.** `scoreRow`, `scoreContext`, `lin` and the factor maths are gone from `shortlist.ts` (deleted, not kept as an oracle: the parity tests now compare against the pipeline's own output instead). `comboKey(rp)` builds the pipeline's combination key (`road-tripper+kerbside.rural`; tested against every picker answer set). `rankHero` keeps the hard filters (country, new/used, budget, refine chips, presets) and sorts by the release score; `ruled-out` never shows; a variant without a score for the combination is not ranked (`unscored`). Explore's "Suggested" sort reads the same scores (`suggestedScore`).
- **No scores file** → `status: "no-scores"`: the hero shows "Ranking not available yet" (EN/NL/DE/FR) and ranks nothing; Suggested shows the same line when active. Release 1 has no scores file, so the published site shows that state until release 2 (T-116).
- **Reason line** uses the release's `+factor` codes with the release's values: winter range = `derived.winter_range_km` (labelled estimate), efficiency = `derived.real_wh_km`, DC = row km/20 min, plus price headroom. The "In winter" card cell now shows the release's winter estimate ("estimate at −10 °C"; t1 band, representative −10 °C, data/taxonomy/temperature_bands.yaml).
- **Nerd table** shows the release's 0..1 per factor and the rule weights after layer/modifier steps; unknown = 0.5, "not known yet". Plus a line naming the release and file.
- **Reversible default (keep-8-years):** the release has no add-on combinations, so the checkbox can't change the order. It is kept (URL state) with a note "Doesn't change the order yet". Ask WS1 to add add-on combos (or a `+keep8` suffix) to T-069 if we want it to count.
- **Fixtures.** `src/fixtures/shortlist-scores.sample.json` = the pipeline's `build_matrix` + `build_shortlist` run on the dev fixture rows (38 variants, 18 combos; see its `note`). Regenerate when the rules change. The dev fixture catalogue serves it, so `pnpm dev` without a release ranks.
- **e2e.** `e2e/release.ts` tells whether the release under test has `shortlist_scores.json`. Ranking tests skip with that reason on release 1 (Test-change, see PR); a new test checks the "ranking not available" state instead. Not done (rubric change, own PR): `e2e/feature-map.yaml` hero flows expect cards, so `verify` on bare release 1 fails those flows until release 2; a `hero-no-scores` flow could be added.
- **Open:** e2e on the published release 2 once it exists (acceptance criterion 4). PR #56 (T-097) edits the same Nerd table and `FactorScore`; whichever merges second must adapt (the release has no raw factor values, only 0..1, so its `raw` column maps to row/derived values here).
- **Merged main after #56 (T-097), 2026-11-17 (WS2 subagent).** Both intents kept: the score column is the release's 0..1 (Decision 065, no web scoring), the Value column is T-097's `nerdValue()` (the car's own figure with its unit). `FactorView` gained `field` + `raw`, filled in `scoreFor()` from the row, or from the release's derived estimates where the release scores those (`winter-range` → `winter_range_km`, `efficiency` → `real_wh_km`; mirrors `field_overrides` in pipeline/ev_pipeline/derive/shortlist_params.yaml, `SCORED_FIELD` in shortlist.ts). Yes/no factors whose field is a structure (bidi) read the release's 0/1. New strings `hero.nerd.unit.real_wh_km` ("{v} Wh/km") and `hero.nerd.unit.winter_range_km` ("{v} km in winter (est.)") in all six languages, so the winter figure is labelled an estimate. The old `factorValue()` in Hero.tsx is gone. T-097's e2e tests (Nerd DC value = the card's own km/20 min; Nerd table fits 360 px in six languages) now skip without a scores file, like the other ranking tests.

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-35 B3 fixed. -->

WS0 subagent, 2026-11-17, 11160ab: R0–R3, D3, D6–D8, D10, D13 pass; hero scores = release scores on 7 answer sets; re-checked on release 2 (#100 review, 3 sets). **A-35 B3 fixed.**
