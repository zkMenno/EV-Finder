# T-150 Ship release photos as one bundle (Decision 086)
Role: builder   Lane: pipeline (WS1) + one cross-lane file in apps/web   Wave: launch
Status: todo

## Goal
A fresh release uploads in one run: photos go into one `images.tar` asset per release (Decision 086).

## Acceptance criteria
- [ ] Gate PR first (its own PR, gate files): data-refresh `pr` job fails early, with a clear message, when a release would upload more than 450 assets. The guard stays after the bundle ships.
- [ ] Same gate PR: the data-refresh PR body quotes `ev verify --base main` for main and for the PR together (retro 2026-11-18), so blocking cells a gate PR knows about are visible in the data PR.
- [ ] The publisher writes `images.tar` (uncompressed) and lists it in the manifest with size + sha256, plus each inner file with path + sha256.
- [ ] `ev release fetch` downloads, checks and unpacks the bundle, then checks each file. Releases 1 to 3 still fetch the old way (test both).
- [ ] `apps/web/scripts/fetch-release.mjs` doesn't fetch `images/` today (default CATALOGUE_FILES). If T-146 (row thumbnails) needs photos by then, it unpacks the bundle the same way (cross-lane change, flagged in the PR and one line in WS0 INBOX); otherwise leave it and note it in Handoff.
- [ ] Asset count for a release like release 3 drops from 646 to about 290 (646 − 357 photos + 1 bundle), so a fresh release uploads in one run; measured and quoted in the PR.
- [ ] Tests with fixtures, no network.

## Inputs
Decision 086; #162 (resumable upload); #150 (photo-only releases); WS0 INBOX 2026-11-18 19:14 UTC.

## Out of scope
New photos. Image sizes or formats.

## Handoff notes

## Review
