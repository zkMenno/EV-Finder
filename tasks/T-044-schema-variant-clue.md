# T-044 Schema: Variant clue and Look-alike group
Role: coordinator (overnight tonight)   Lane: packages/schema   Wave: 7
Status: todo

## Goal
Add the two entities from Decision 019 / docs/spec/variant-finder.md §4.

## Acceptance criteria
- [ ] `VariantClue`: variant_id, clue_type (taxonomy id), market (CountryCode or global), value or range, strength (decisive/strong/weak), rules_out[] (variant ids), source, retrieved_at, confidence
- [ ] `LookalikeGroup`: id, variant_ids[], reason (same generation / same badge / same marketing name across markets), built_by (pipeline/staff)
- [ ] Taxonomy `clue_types` validated at release time (Decision 010 pattern)
- [ ] Valid + invalid fixtures; generated TS + Python types

## Inputs
docs/spec/variant-finder.md, Decision 019.

## Out of scope
Clue rows, UI.

## Handoff notes

## Review
