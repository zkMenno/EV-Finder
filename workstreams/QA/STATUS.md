# QA status

## 2026-11-17 · launch review 2 (A-36, branch qa/launch-review-2)
Done: hero walk on release 2 (80 runs), catalogue walk, A-35 re-check, A-36 report with 4 blockers, T-138 + T-139, one fix (parked bidi factors on hero cards) with an e2e test. Tools for the next review: `workstreams/QA/tools/hero-walk.mjs`, `catalogue-walk.mjs`.

### Retro
1. **What slowed me down:** the release files are not in git, so the pipeline tests fail locally until `uv run ev release fetch latest` (the web build fetches only 4 files); running the hero walk and the e2e suite at the same time made two axe tests time out; the first screenshots captured the page top instead of the results.
2. **What Menno had to do by hand:** nothing yet. Direct pushes to `main` from this session were refused, so the CHATS row, the WS0 INBOX line and STATUS ride in the PR; Menno or WS0 merges them.
3. **Which rule would have prevented it:** a task-number block handed to one chat only (QA's T-130–T-139 were reused by WS0 an hour later); "fetch the release first" in the pipeline README test section.
4. **What did a check miss, and which check would have caught it?** (a) `hero.spec.ts` proved the budget and the rank order but not that the pick fits the profile: a car with no data won the road-tripper list (A-36 B1) → profile-fit acceptance test on the published release. (b) `check-release` proved every value has a source, not the right one: 134 values cite a VW heat-pump page (B2) → "one source id = one citation" blocking check. (c) The release PR never ran the Images job, so the manifest-only release broke the deploy image (B3) → D1 includes the image build.
