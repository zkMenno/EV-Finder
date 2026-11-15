# T-064 Move published releases out of git
Role: WS1 (pipeline) + WS4 (storage, CI)   Lane: pipeline, infra, .github (WS0 reviews)   Wave: 7
Status: todo

## Goal
Keep releases versioned and rollback-able without committing multi-MB JSON to git (Decision 035).

## Acceptance criteria
- [ ] `ev release publish` uploads release files to GitHub Release assets (tag `data-v<n>`) or an S3-compatible bucket from env config; checksums recorded
- [ ] Repo keeps `data/releases/<n>/manifest.json` (number, date, files, sizes, sha256, QA summary) and a small fixture release for tests
- [ ] Web build downloads the release named in `data/releases/latest` + manifest, verifies checksums; CATALOGUE_DIR still works locally
- [ ] Catalogue split per generation (index + one file per generation) so pages load only what they need
- [ ] Rollback = point `latest` at an earlier manifest; documented in pipeline/README.md
- [ ] `data/releases/1/*.json` removed from git once the new path works; CI release cap back to 5 MB

## Inputs
Decision 035, Decision 008, addendum 6 P2/P4, infra/README.md.

## Out of scope
Database-backed catalogue (comes with Postgres).

## Handoff notes

## Review
