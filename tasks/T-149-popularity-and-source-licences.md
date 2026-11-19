# T-149 Publish popularity, used-price source licences and photo licence templates
Role: builder   Lane: pipeline (WS1)   Wave: launch
Status: doing (batch chat https://claude.ai/code/session_01JuyZETPZUUpdfhHpfB9Pef, 2026-11-19)

## Goal
Fill the three fields WS0 added to the schema (PR "WS0: release 3 schema fields"): `Generation.popularity`, `UsedPriceSourceRef.licence`, `GenerationImage.licence_template` + `licence_checked_at`.

## Acceptance criteria
- [ ] `Generation.popularity` is computed in the pipeline with the weights in `config/popularity.yaml` (registrations from the release's registration facts, owner picks from `data/editorial/menno-picks.yaml`), `rank` 1 = most popular, `as_of` = newest registration data used, `source_ids` = the release source ids actually used. Absent when no registrations matched.
- [ ] Same ranking as today's web build (`apps/web/scripts/popularity.mjs`) on release 3 inputs, or every difference explained in the PR (the release field replaces the top40 registration input, so some moves are expected; list the top 20 before / after).
- [ ] Every `UsedPriceSourceRef` carries `licence` (SPDX id where one exists); the licence comes from the source registry, never typed per row.
- [ ] Commons photos record `licence_template` and `licence_checked_at` from the file-page check `ev images check` already does (Decision 083). Press photos leave them out.
- [ ] Release QA: a Commons photo without `licence_template` is blocking; a photo whose template doesn't match its `licence` (the "CC BY photo with a stray template" case) is blocking.
- [ ] `PD-old` (and `PD-old-70`, `PD-old-100`, worldwide variants only) added to the template allowlist, per Decision 083.
- [ ] Tests with fixtures; `ev verify --base main` output in the PR; the data diff of the next refresh shows only the new fields.

## Inputs
Decision 038 (popularity blend), 081, 083; WS0 INBOX 2026-11-18 19:14 UTC (batch: data / release 3); T-130.

## Out of scope
Web changes: WS2 switches `popularity.mjs` to the release field in a follow-up once a release carries it. Photo bundling (T-150).

## Handoff notes

## Review
