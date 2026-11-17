# T-134 Image fields and storage in the release
Role: builder   Lane: WS1: pipeline/, packages/schema request to WS0   Wave: launch (staging feedback 2026-11-17)
Status: todo

## Goal
The release carries each generation's image with licence and credit, stored by us.

## Acceptance criteria
- [ ] Download each image from T-133 once, resize (e.g. 400/800/1600 px WebP), store in object storage next to the release; never hotlink
- [ ] Release field per generation: image paths, source URL, licence, credit, retrieval date (schema change requested from WS0)
- [ ] Images are excluded from the CC BY open data dump; licence check in the release QA
- [ ] Verify skill for the lane; evidence pack in the PR; `Verified:` on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes

## Inputs
Decision 081; T-133

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts. -->
