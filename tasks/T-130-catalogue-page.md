# T-130 Catalogue page with popularity sort; landing loses the full list
Role: builder   Lane: WS2 (+ UX layout): apps/web/   Wave: launch (staging feedback 2026-11-17)
Status: review (WS2, 2026-11-18, part 1: PR on branch t-130-catalogue-page)

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
WS2, 2026-11-18 (session_01JuyZEUuCTBUyPNJ74C3iRD).

**Part 1 (this PR): the working page.**
- `/{country}/{lang}/cars` = Explore, default sort Most popular, default view cards. Landing: no list, "Show all cars" box. Header link "All cars".
- Popularity is per generation: `score = 100 × (0.8 × registration share ÷ top model + 0.2 × owner pick)`. Registrations: `data/seed/top40.yaml` `score_pct` (NL RDW first registered 2018–2024 + UK DfT fleet, averaged by WS1's top40 method). Picks: best verdict from `menno-picks.yaml` (shortlist 1, consider 0.6, fallback 0.3, favourite +0.2, cap 1). Weights in `config/popularity.yaml` (reversible default, WS2's pick: registrations dominate so the order reflects the road, picks only nudge). Unknown cars: no score, last, no tag.
- Reversible default: the web builds the score from the seed file at build time, because the release has no popularity field yet. Asked WS1 for `popularity` per generation in the release (INBOX); `catalogue.popularity()` is the single switch point.
- Old landing Explore links (with `view` or `sort`, no hero answers) 307 to `/cars` with the same query.
- Sort menu offers the design's six orders. "Price" sorts by **new** price (that's the only price on every row); label says so.

**Not done yet (part 2, needs no new data):** the design's visual layer: filter sidebar groups (used price, winter range slider, body tiles, brands with search + counts), phone "Filters · n" bottom sheet + sticky bar, removable filter pills + Clear, "214 models · 87 match" count line, one card per generation with used price band and the three facts (winter km, summer km, km in 20 min). Photo + credit on cards is T-135 (needs WS1's image fields).

**Known gap:** resetting the sort to "unsorted" via a table header leaves no `sort` in the URL, so a reload shows Most popular again. Small; fix with part 2 if the table keeps the unsorted state.

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts. -->
