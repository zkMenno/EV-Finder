# T-001 Schema v0
Role: coordinator   Lane: packages/schema   Wave: 1
Status: review (coordinator, 2026-11-15)

## Goal
JSON Schema for every entity, generated TS + Pydantic types, fixture tests.

## Acceptance criteria
- [ ] Schema files for Make, Model, Generation, Variant, MarketVariant, Fact, PublishedVariant
- [ ] `pnpm --filter @ev/schema gen` writes TS types and Pydantic models
- [ ] Fixture tests pass in TS and Python
- [ ] Tests cover it (with fixtures, no live network calls)

## Inputs
Overnight brief (prototype 1), AGENTS.md, DECISIONS.md.

## Out of scope
Anything outside the lane above. No auth, no pg-boss, no Postgres tonight.

## Handoff notes

## Review
