# T-131 "Popular used EVs" section on the landing
Role: builder   Lane: WS3 (list) + WS2 (section): data/editorial/ (WS3), apps/web/ (WS2)   Wave: launch (staging feedback 2026-11-17)
Status: review (WS3 part; WS3 2nd chat, 2026-11-17). WS2 section: todo

## Goal
The landing shows the popular used EV generations, roughly Menno's own list.

## Acceptance criteria
- [x] WS3: `data/editorial/popular_used.yaml`, generation ids (not trims), seeded from Menno's New Car sheet generations (data/editorial picks, Decision 038) and registration counts; each row says why it is listed
- [ ] WS2: landing section renders the list as generation cards (photo once T-135 lands, used price band for the country, winter range)
- [x] Order and contents are data, not code (WS3 side: weights in the file's `method`, rows generated)
- [ ] Verify skill for the lane; evidence pack in the PR; `Verified:` on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes

## Inputs
docs/spec/feedback-2026-11-17-staging.md item 2; data/seed/top40.yaml

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes
**WS3 (2026-11-17):** `data/editorial/popular_used.yaml` (33 generations, ordered), built by `data/editorial/build_popular_used.py` (`--check` = stale/unknown-id guard).
- Candidates: Menno's own generation list (menno-picks.yaml `eras`, the eras already on the used market: 2019-2021 … 2024-2026). 2026-2028 (not yet used) left out.
- Order = registration points (41 − model rank in top40.yaml) + owner points (shortlist 20, consider 10, unrated 0, ruled out −10, favourite +5). Unrated generations outside the top 40 are dropped. Weights are written into the file (`method`), reversible default.
- `method.landing_count: 12` = how many the landing shows; the rest belong on the catalogue page.
- Each row has `why` (one plain EN line), `registrations.top40_rank`, `owner.verdict` / `favourite` / `remark`. Owner verdicts must be labelled as one person's opinion (Decision 038).
- Ranks are per model (top40 has no generation split): Niro DE and SG2 share #3.
- Popular models not on Menno's list (Audi Q4 #7, Audi e-tron #11, BMW i4 #14, Mini #15) are not in the section: "roughly his list" (feedback item 2). Say if you want the top 15 models added regardless.
- For WS2: all 33 ids are in release 2, but 6 have no variant rows yet (kia-ev3-gen1, kia-ev6-facelift, opel-astra-electric-gen1, peugeot-e-308-gen1, xpeng-g6-facelift, xpeng-p7-gen1): skip a card with no data rather than show an empty one.

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts. -->
