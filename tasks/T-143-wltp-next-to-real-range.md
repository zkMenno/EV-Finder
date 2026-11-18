# T-143 Official WLTP range next to our real range (real range leads)

Role: builder   Lane: WS2 (apps/web); UX for the visual pattern   Wave: launch
Status: todo

## Goal
Decision 085 (Menno, 2026-11-18): everywhere range shows, our real range comes first and most prominent, and the official WLTP range sits right next to it in the same section, labelled "Official (WLTP)".

## Acceptance criteria
- [ ] Catalogue cards/rows (/cars), hero cards, car / generation / variant pages, compare: real range (and winter range where shown) leads; WLTP next to it in the same block, secondary style, label "Official (WLTP)"; tooltip explains the difference in one sentence.
- [ ] Filters: range filter defaults to real range; WLTP selectable in the same filter group (toggle or second control); URL state keeps which one; sort by range defaults to real range, WLTP sort available.
- [ ] Missing WLTP shows "not known" (never our estimate in its place); missing real range keeps today's behaviour.
- [ ] EN strings (Decision 082: English only at launch); other language files get keys only if the i18n tests require them.
- [ ] Contrast WCAG AA; 360 px and 1280 px, light + dark, plus one run with ~6 % wider letters (CI fonts); axe clean.
- [ ] Unit tests + e2e for the filter toggle and one variant page; verify-web skill; evidence pack with screenshots in the PR; `Verified:` on every commit.
- [ ] Fresh review (REVIEW.md from origin/main) passes.

## Inputs
Decision 085; docs/design/ (UX patterns); `wltp_range_km`, `real_range_km`, `real_range_winter_km` in the release.

## Out of scope
New data fields or pipeline changes.

## Handoff notes

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts. -->
