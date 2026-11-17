# T-133 Car photos: sourcing and licence log per maker
Role: builder   Lane: WS3: data/images/   Wave: launch (staging feedback 2026-11-17)
Status: todo

## Goal
One licensed photo per generation, with its credit (Decision 081).

## Acceptance criteria
- [ ] `data/images/press-terms.yaml`: per maker, the press/media terms URL, date checked, a short quote of the relevant clause, verdict allowed / not allowed / unclear; unclear = not used
- [ ] Per generation: the chosen image (maker press if allowed, else Wikimedia Commons CC BY / CC BY-SA), source page URL, licence, author/credit line, retrieval date
- [ ] Coverage report: % of launch generations with a photo, by source
- [ ] No downloads committed to git (data rule 4): WS1 stores the files
- [ ] Verify skill for the lane; evidence pack in the PR; `Verified:` on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes

## Inputs
Decision 081

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts. -->
