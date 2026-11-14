# T-005 Match merge
Role: builder   Lane: pipeline/ev_pipeline/merge   Wave: 2
Status: todo

## Goal
Map source records to variants, merge with priority/majority/recency, confidence.

## Acceptance criteria
- [ ] Rules-first matching
- [ ] Unmatched rows → data/review/unmatched.csv
- [ ] Tests for each merge rule
- [ ] Tests cover it (with fixtures, no live network calls)

## Inputs
Overnight brief (prototype 1), AGENTS.md, DECISIONS.md.

## Out of scope
Anything outside the lane above. No auth, no pg-boss, no Postgres tonight.

## Handoff notes

## Review
