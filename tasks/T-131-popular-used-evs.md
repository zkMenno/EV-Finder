# T-131 "Popular used EVs" section on the landing
Role: builder   Lane: WS3 (list) + WS2 (section): data/editorial/ (WS3), apps/web/ (WS2)   Wave: launch (staging feedback 2026-11-17)
Status: todo

## Goal
The landing shows the popular used EV generations, roughly Menno's own list.

## Acceptance criteria
- [ ] WS3: `data/editorial/popular_used.yaml`, generation ids (not trims), seeded from Menno's New Car sheet generations (data/editorial picks, Decision 038) and registration counts; each row says why it is listed
- [ ] WS2: landing section renders the list as generation cards (photo once T-135 lands, used price band for the country, winter range)
- [ ] Order and contents are data, not code
- [ ] Verify skill for the lane; evidence pack in the PR; `Verified:` on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes

## Inputs
docs/spec/feedback-2026-11-17-staging.md item 2; data/seed/top40.yaml

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts. -->
