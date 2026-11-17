# T-130 Catalogue page with popularity sort; landing loses the full list
Role: builder   Lane: WS2 (+ UX layout): apps/web/   Wave: launch (staging feedback 2026-11-17)
Status: todo

## Goal
A "Show all cars" button on the landing leads to a catalogue page like ev-database.org, sorted by popularity by default.

## Acceptance criteria
- [ ] Landing page no longer renders the full car list; a "Show all cars" button links to the catalogue page
- [ ] Catalogue page: Explore filters, default sort = popularity, user sorts by price, range, battery, charging speed, year; sort and filters in the URL
- [ ] Popularity = registration counts from `data/seed/top40.yaml` (RDW, DfT, KBA, EEA) blended with Menno's picks (Decision 038); the blend weights live in config, not code, and the pipeline publishes the score in the release (ask WS1 via INBOX if a field is needed)
- [ ] UX gives the layout first (workstreams/UX INBOX); 360 and 1280 px screenshots, light and dark
- [ ] Verify skill for the lane; evidence pack in the PR; `Verified:` on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes

## Inputs
docs/spec/feedback-2026-11-17-staging.md item 1; Decision 038

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts. -->
