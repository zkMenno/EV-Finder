# T-137 English only at launch: serve /{country}/en/ everywhere
Role: builder   Lane: WS2: apps/web/, config/countries/ (cross-lane: tell WS3)   Wave: launch (staging feedback 2026-11-17)
Status: todo

## Goal
Every country serves English by default; other languages are hidden, not deleted (Decision 082).

## Acceptance criteria
- [ ] Every country config: `default_language: en`, no extra UI languages served; `/{country}/` redirects to `/{country}/en/`
- [ ] `/{country}/{nl|de|fr|es|it}/` redirect to `/{country}/en/`, are not linked, not in sitemap or hreflang; the language picker is hidden
- [ ] Strings stay in the repo; i18n tests keep passing; e2e covers the redirects for all seven countries
- [ ] Spain and Italy work in English
- [ ] Verify skill for the lane; evidence pack in the PR; `Verified:` on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes

## Inputs
Decision 082, 015, 066

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts. -->
