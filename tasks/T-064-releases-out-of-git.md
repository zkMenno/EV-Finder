# T-064 Move published releases out of git
Role: WS1 (pipeline) + WS4 (storage, CI)   Lane: pipeline, infra, .github (WS0 reviews)   Wave: 7
Status: merged (PR #4); fresh review via QA A-35; earlier note: WS1, 2026-11-15; part 2 after data-v1 is published

## Goal
Keep releases versioned and rollback-able without committing multi-MB JSON to git (Decision 035).

## Acceptance criteria
- [x] `ev release publish` uploads release files to GitHub Release assets (tag `data-v<n>`) or an S3-compatible bucket from env config; checksums recorded
- [x] Repo keeps `data/releases/<n>/manifest.json` (number, date, files, sizes, sha256, QA summary) and a small fixture release for tests
- [x] Web build downloads the release named in `data/releases/latest` + manifest, verifies checksums; CATALOGUE_DIR still works locally
- [x] Catalogue split per generation (index + one file per generation) so pages load only what they need
- [x] Rollback = point `latest` at an earlier manifest; documented in pipeline/README.md
- [ ] (part 2) `data/releases/1/*.json` removed from git once the new path works; CI release cap back to 5 MB

## Inputs
Decision 035, Decision 008, addendum 6 P2/P4, infra/README.md.

## Out of scope
Database-backed catalogue (comes with Postgres).

## Handoff notes
**WS1, 2026-11-15 (part 1, PR `t-064-releases-out-of-git`).**
- New: `pipeline/ev_pipeline/release/publish.py` (split, manifest, verify, `DirPublisher`,
  `GithubPublisher`, `fetch`, `ensure_local`, `local_catalogue`), `ev release
  package|publish|fetch|verify`, config `data/releases/publish.yaml`, shell publisher
  `pipeline/scripts/gh-publish-release.sh`, `data/releases/1/manifest.json` (98 files, 20.8 MB).
- `ev release` now packages before the folder goes live. Diff vs the previous release,
  rollback, `ev refresh` and `qa top40` fetch an older release by manifest when its files
  aren't on disk, and fail (never "no previous release") when they can't.
- Split: `catalogue/index.json` 1.0 MB raw (no provenance; WS2 can gzip-check), 81 generation
  files. `catalogue.json` is still published whole, so today's web loader is unchanged.
- Web: `apps/web/scripts/fetch-release.mjs` (no deps) runs first in `build`/`dev`; default
  `CATALOGUE_SOURCE=auto` is a no-op while files are in git. WS2 reviews; switching pages to
  the per-generation files is WS2's call.
- Outside my lane, flagged in the PR for WS0: `.github/workflows/data-publish.yml` (new),
  `data-refresh.yml` (pr job uploads assets), `ci.yml` (`ev release fetch latest` before
  check-release), `.gitignore` (release files). WS4: `apps/web/Dockerfile` copies
  `data/releases`; it must run `fetch-release.mjs` (or `ev release fetch`) before part 2.
- **Part 2 (after merge):** run "Data publish" with release 1 (Actions → Data publish → Run
  workflow → `1`), check data-v1 has 98 assets, then remove `data/releases/1/` big files from
  git and set the release cap back to 5 MB (WS0, ci.yml).
- Tests: `tests/test_release_publish.py` (33), no network (MockTransport, fake `gh`).

## Review
