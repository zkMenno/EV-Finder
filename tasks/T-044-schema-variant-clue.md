# T-044 Schema: Variant clue and Look-alike group
Role: coordinator (overnight tonight)   Lane: packages/schema   Wave: 7
Status: review (schema delegate for WS0, 2026-11-15)

## Goal
Add the two entities from Decision 019 / docs/spec/variant-finder.md §4.

## Acceptance criteria
- [x] `VariantClue`: variant_id, clue_type (taxonomy id), market (CountryCode or global), value or range, strength (decisive/strong/weak), rules_out[] (variant ids), source, retrieved_at, confidence
- [x] `LookalikeGroup`: id, variant_ids[], reason (same generation / same badge / same marketing name across markets), built_by (pipeline/staff)
- [x] Taxonomy `clue_types` validated at release time (Decision 010 pattern)
- [x] Valid + invalid fixtures; generated TS + Python types

## Inputs
docs/spec/variant-finder.md, Decision 019.

## Out of scope
Clue rows, UI.

## Handoff notes
Schema delegate (WS0), 2026-11-15. Additive only; release 1 still validates.

- **New defs** in `packages/schema/schemas/ev.schema.json`: `VariantClue`, `LookalikeGroup`, `ClueType` (taxonomy row for `data/taxonomy/clue_types.yaml`), `ClueRange`, `ClueSourceRef`, `ClueStrength` (decisive/strong/weak), `ClueValueKind`, `ClueFoundIn`, `LookalikeReason`.
- **Wired in (all optional):** `Taxonomy.clue_types`, `Catalogue.variant_clues`, `Catalogue.lookalike_groups`, `PublishedVariant.lookalike_group_ids`, `PublishedVariant.clue_count`.
- **Field names vs criteria:** `clue_type` → `clue_type_id`; `source` → `sources[]` (min 1 `ClueSourceRef`: source_id, url, locator, source_record, retrieved_at). `market` = CountryCode or `global`. Value is `value` (scalar) or `range` (`min`/`max`: numbers or `YYYY-MM[-DD]`, null = open). See Q-064.
- **Fixtures:** `variant-clue`, `lookalike-group`, `clue-type` (valid + invalid each), `clue-range.invalid` (spec-style `06/2021` dates are rejected; use `2021-06`). Fixture values are illustrative, not sourced.
- **Generated:** `generated/ts/index.ts`, `generated/python/ev_schema.py`, `pipeline/ev_pipeline/schema_models.py`.
- **Checks:** `pnpm --filter @ev/schema test` 66 passed; `typecheck` clean; `uv run pytest tests/test_schema_fixtures.py tests/test_real_release.py` 129 passed.
- **Left for release time (not in schema, Decision 020 pattern):**
  - T-046 (WS3): add `clue_types` to `TAXONOMY_FILES` in `data/taxonomy/validate_taxonomy.py` (row def `ClueType`) when `clue_types.yaml` lands.
  - T-047 (WS1): `clue_type_id` resolves to a clue_types row; exactly one of `value`/`range`; shape matches `value_kind` and unit matches the type's `unit`; `rules_out` ids exist and share a group with `variant_id`; decisive clues really separate; `sources[].source_id` resolve; staff clues have `url`; fill `lookalike_group_ids` / `clue_count` on rows.

## Review
