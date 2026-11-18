# T-137 English only at launch: serve /{country}/en/ everywhere
Role: builder   Lane: WS2: apps/web/, config/countries/ (cross-lane: tell WS3)   Wave: launch (staging feedback 2026-11-17)
Status: review (WS2, 2026-11-17)

## Goal
Every country serves English by default; other languages are hidden, not deleted (Decision 082).

## Acceptance criteria
- [x] Every country config: `default_language: en`, no extra UI languages served; `/{country}/` redirects to `/{country}/en/`
- [x] `/{country}/{nl|de|fr|es|it}/` redirect to `/{country}/en/`, are not linked, not in sitemap or hreflang; the language picker is hidden
- [x] Strings stay in the repo; i18n tests keep passing; e2e covers the redirects for all seven countries
- [x] Spain and Italy work in English
- [x] Verify skill for the lane; evidence pack in the PR; `Verified:` on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes

## Inputs
Decision 082, 015, 066

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes
- 2026-11-17 WS2 (session_01JuyZEUgDrkg5ED4ZkeyEzg). All seven `config/countries/*.yaml`: `languages: []`, `default_language: en`, with a comment naming the old list so it can come back. `scripts/countries.mjs` now accepts an empty list (served = EN only) and a default of `en`. Routing, hreflang, sitemap, x-default and the country switcher all read `served`, so nothing else needed code changes.
- Layout renders the language picker and the Accept-Language banner only when a country serves 2+ languages. Components and all six dictionaries stay.
- e2e: `es-it.spec.ts` → `english-only.spec.ts` (redirects for all 7 countries × 5 hidden languages + bare `/{country}` + cookie, no picker/banner, no internal link to a hidden language, hreflang/sitemap EN only, ES/IT hero walks in English). Other specs moved from `/xx/yy` to `/xx/en` with the English strings (looked up by dictionary key). Specs that only make sense with a second language (`no-english`, learn fallback) skip on `ENGLISH_ONLY` from `e2e/langs.ts`, which reads the generated config, so they switch back on by themselves when a country lists a language again. The 360 px Nerd loop now runs every served route from config.
- feature-map: `language-switch` flow replaced by `english-only`; `country-spain-italy` now expects `/es/en`. This changes rubric checks (verify skill §4: WS0 approves); sent to WS0.
- Known, not mine: `num-labels.test.ts` (glossary term `derived` missing) fails on main too; verify flow `tooltip` fails 3/3 on main's map because the check takes the first of ~336 hidden `[role=tooltip]` nodes; the tooltip itself opens (probe: 1 visible after the click). Both sent to WS0.

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts. -->
