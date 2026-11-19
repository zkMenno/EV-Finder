# T-157 Web reads popularity from the release; unpack the photo bundle
Role: builder   Lane: apps/web (WS2)   Wave: launch
Status: todo (start when release 4 is published)

## Goal
The web ranking uses the release's own popularity figures instead of its own script, and the build can read photos from the new bundle.

## Acceptance criteria
- [ ] `apps/web/scripts/popularity.mjs` reads `generations[].popularity` from the release (T-149) instead of computing its own; same ranking within the back-test tolerance (Spearman ≥ 0.95 vs today, number in the PR body). Old releases without the field still build (D5 N-1).
- [ ] `apps/web/scripts/fetch-release.mjs` unpacks (done now, ahead of T-146, so the photo path is ready when rows need it) `images.tar` when the release has one (Decision 086) and checks each file's sha256 from the manifest; releases 1–3 without a bundle still work.
- [ ] Unit tests with fixtures; web lint, types, tests, build green locally first.

## Inputs
WS0 INBOX 2026-11-19 03:02 UTC (batch: #171/T-149/T-150, item 5); Decision 086; T-149, T-150 Handoff notes.

## Out of scope
Showing photos in rows (T-146).

## Handoff notes

## Review
