# T-001 Schema v0
Role: coordinator   Lane: packages/schema   Wave: 1
Status: review (coordinator, 2026-11-15)

## Goal
JSON Schema for every entity, generated TS + Pydantic types, fixture tests.

## Acceptance criteria
- [x] Schema files for Make, Model, Generation, Variant, MarketVariant, Fact, PublishedVariant
- [x] `pnpm --filter @ev/schema gen` writes TS types and Pydantic models
- [x] Fixture tests pass in TS and Python
- [ ] Tests cover it (with fixtures, no live network calls)

## Inputs
Overnight brief (prototype 1), AGENTS.md, DECISIONS.md.

## Out of scope
Anything outside the lane above. No auth, no pg-boss, no Postgres tonight.

## Handoff notes

## Review

**Reviewer (fresh agent), 2026-11-15. Verdict: changes needed (small).**

Checked: `pnpm --filter @ev/schema test` (8 passed). Re-ran `gen` in a temp copy: TS and Python output are byte-identical to the committed files, and `pipeline/ev_pipeline/schema_models.py` equals `generated/python/ev_schema.py`. The real release 1 validates against `Catalogue` (new test, see below).

Findings
1. **No fixtures for 5 of the 7 core entities.** `packages/schema/fixtures/` covers Fact, PublishedVariant, BatteryPack, GlossaryTerm, VoltageClass only. Make, Model, Generation, Variant and MarketVariant have none, against `packages/schema/AGENTS.md` ("every change needs a fixture") and box 4. Add one `.valid.json` each, plus an `.invalid.json` for Generation (year_end < year_start isn't caught; see 3).
2. **There was no Python fixture test.** The pipeline uses the Pydantic models only on release output. Reviewer added `pipeline/tests/test_schema_fixtures.py`: every fixture against JSON Schema (with format checks) and every valid fixture against the generated Pydantic model. It also has an xfail that lists the missing core-entity fixtures and a Q-017 regression (`not-disclosed` accepted by `anyOf`). Box 3 is ticked on that basis.
3. Rules the schema can't express yet, now enforced only in pipeline code: `real_range_km` non-null ⇒ `real_range_rung` non-null (`ev.schema.json` PublishedVariant has no `dependentRequired`/`if-then`), and Generation `year_end >= year_start`. Low.
4. `PublishedVariant.platform_id` / `battery_pack_id` / `chemistry_id` are free `string|null` rather than `Id | 'not-disclosed'`, so a bad id only fails at the taxonomy check in the pipeline. Low.
