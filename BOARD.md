# Board

One screen: what's happening. Coordinator only. Task details live in `tasks/`.

_Last updated: 2026-11-15 (overnight prototype 1, branch `proto/overnight-1`)_

## Now
- Wave 1 — Foundations

## Next
### Wave 1 — Foundations
- T-001 schema-v0 (coordinator, `packages/schema`)
- T-002 repo-plumbing (builder, `root config, .github, pipeline/pyproject.toml`)
- T-003 seed-models (builder, `data/seed`)

### Wave 2 — Data pipeline v0
- T-004 source-adapters (builder, `pipeline/sources`)
- T-005 match-merge (builder, `pipeline/ev_pipeline/merge`)
- T-006 validate-release (builder, `pipeline/ev_pipeline/release`)
- T-007 derived-metrics (builder, `pipeline/ev_pipeline/derive`)

### Wave 3 — Web prototype
- T-008 explore (builder, `apps/web (explore)`)
- T-009 model-pages (builder, `apps/web (ev pages)`)
- T-010 compare (builder, `apps/web (compare)`)
- T-011 rankings (builder, `apps/web (top)`)
- T-012 i18n (builder, `apps/web (i18n)`)
- T-013 health-docker-deploy (builder, `apps/web/Dockerfile, infra/`)

### Wave 4 — Harden
- T-014 review (reviewer, `tasks/ (review notes)`)
- T-015 tests-smoke (coordinator, `apps/web/e2e`)
- T-016 perf-budget (coordinator, `audits/`)
- T-017 security-pass (coordinator, `audits/`)

## Blocked
- Pushing to GitHub and opening the PR: this session has read-only access (Q-004)

## Done
- 2026-11-15: GitHub repo, licences, scaffold, CI skeleton, templates, security settings
