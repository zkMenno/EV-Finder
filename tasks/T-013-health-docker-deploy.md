# T-013 Health docker deploy
Role: builder   Lane: apps/web/Dockerfile, infra/   Wave: 3
Status: todo

## Goal
/health, arm64 Dockerfile, compose and Caddy files (not applied).

## Acceptance criteria
- [ ] /health returns 200 JSON
- [ ] Image builds for linux/arm64
- [ ] Limits as in Decision 006
- [ ] Tests cover it (with fixtures, no live network calls)

## Inputs
Overnight brief (prototype 1), AGENTS.md, DECISIONS.md.

## Out of scope
Anything outside the lane above. No auth, no pg-boss, no Postgres tonight.

## Handoff notes

## Review
