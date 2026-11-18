# T-134 Image fields and storage in the release
Role: builder   Lane: WS1: pipeline/, packages/schema request to WS0   Wave: launch (staging feedback 2026-11-17)
Status: review (WS1 6th session, 2026-11-17); field goes live once WS0 adds Generation.image and T-133 lands photos.yaml

## Goal
The release carries each generation's image with licence and credit, stored by us.

## Acceptance criteria
- [x] Download each image from T-133 once, resize (e.g. 400/800/1600 px WebP), store in object storage next to the release; never hotlink
- [x] Release field per generation: image paths, source URL, licence, credit, retrieval date (schema change requested from WS0)
- [x] Images are excluded from the CC BY open data dump; licence check in the release QA
- [ ] Verify skill for the lane; evidence pack in the PR; `Verified:` on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes

## Inputs
Decision 081; T-133

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes
- 2026-11-17 WS1 (6th): pipeline side built (PR on branch t-134-image-fields, on top of #109 Pillow).
  - Input contract for T-133 sent to WS3 INBOX: data/images/photos.yaml + press-terms.yaml (format in pipeline/ev_pipeline/images/photos.py).
  - `ev images check` validates; `ev images fetch` downloads each original once into data/cache/images/ (hosts from sources.yaml rows `wikimedia-commons`, `maker-press-photos`; press hosts empty until WS3 lists allowed makers).
  - Release step: 400/800/1600 px WebP (never upscaled, EXIF stripped, content-hashed paths `images/<gen>-<sha8>-<w>.webp`), published as assets, never in git. `generations[].image` = files + source, page_url, file_url, licence, author, credit, retrieved_at, make_id.
  - Schema: field is held back (run-log `images.status`) until packages/schema has `Generation.image` (exact request in WS0 INBOX 22:40). Second box stays open until then.
  - QA: blocking `images` check (licence allowlist, credit, stored paths only) in release QA and check-release.
  - WS2 (T-135): web fetch-release must download `images/*` assets, and the Dockerfile copies only catalogue.json today.

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts. -->
- 2026-11-18 WS1: after #109/#113/#119. Real photos.yaml: 120 valid (country ports CC-BY-SA-3.0-DE accepted). Attach on release 2 catalogue validates against the real Generation.image schema; release QA passes. Wikimedia throttles this sandbox's IP (429, retry-after 600): fetch stops at the first 429, UA names the repo. Night refresh now fetches photos before build_release. First real download = first night run after merge.
- Follow-up (not in this PR): a night with only new photos and no data change is skipped ("catalogue identical"), so photos ship with the next data change.
