# T-002 Repo plumbing
Role: builder   Lane: root config, .github, pipeline/pyproject.toml   Wave: 1
Status: todo

## Goal
pnpm workspace, uv project, lint/format/typecheck, CI job per lane.

## Acceptance criteria
- [ ] `pnpm install` works at root
- [ ] `uv sync` works in pipeline/
- [ ] CI runs schema, web, pipeline jobs; auto-detect kept
- [ ] Tests cover it (with fixtures, no live network calls)

## Inputs
Overnight brief (prototype 1), AGENTS.md, DECISIONS.md.

## Out of scope
Anything outside the lane above. No auth, no pg-boss, no Postgres tonight.

## Handoff notes

## Review
