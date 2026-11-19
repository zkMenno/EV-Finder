# T-150 Ship release photos as one bundle (Decision 086)
Role: builder   Lane: pipeline (WS1) + one cross-lane file in apps/web   Wave: launch
Status: review (batch chat https://claude.ai/code/session_01JuyZETPZUUpdfhHpfB9Pef, 2026-11-19)

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
- Gate PR #172 (asset guard 450 + `ev verify` in the data PR body) is separate; merge it right before this one (release 3 has 646 assets, so the guard alone would stop every release).
- `data/releases/publish.yaml: bundles` names the bundled folders (today `images/` → `images.tar`). `package` writes a deterministic uncompressed tar (sorted, mtime 0, owner 0, mode 0644) and one manifest entry with `bundle: {folder, files: [{path, bytes, sha256}]}`; the photos are no longer separate assets. `catalogue/` can get the same treatment with one more line (Decision 086 says: new decision first).
- `ev release fetch` / `ensure_local`: download the tar, check it, unpack only the listed members (regular files, under the folder, each sha256-checked); a lost photo is re-unpacked from the kept tar without a download. `only={"images/"}` or a photo path picks the bundle. Releases 1–3 have no bundle entry and fetch exactly as before (test).
- Image QA (`images/qa._stored_files`) counts bundle members as stored files.
- Measured on a copy of release 3 repackaged with this code: **646 → 290 assets**, 357 photos in a 29.3 MB `images.tar`, every member's sha256 identical to release 3's files.
- `apps/web/scripts/fetch-release.mjs` left alone: it fetches only `CATALOGUE_FILES` (no `images/`), and T-146 (row thumbnails) is still `todo`. When T-146 needs photos, it unpacks `images.tar` the same way (cross-lane; flag in WS0 INBOX then).
- `gh-publish-release.sh` needed no change: it uploads `manifest.files[]`, which now holds the tar instead of the photos.

## Review
