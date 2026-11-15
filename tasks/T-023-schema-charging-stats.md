# T-023 Schema: charging stats, charging taxonomies, abrp_typecode
Role: coordinator (WS0)   Lane: packages/schema   Wave: 6
Status: review (schema delegate for WS0, 2026-11-15)

## Goal
Add the types from Decision 012 so WS1 and WS3 can build on them.

## Acceptance criteria
- [x] `$defs` ChargingStat, ChargingMetric, ChargingDefinition, PowerBand, CountryChargingLink
- [x] Variant field `abrp_typecode` (nullable string)
- [x] Valid + invalid fixtures; generated TS + Python types updated
- [x] Taxonomy ids validated against data/taxonomy at release time (Decision 010 pattern)

## Inputs
docs/spec/charging-buildout.md (Data model), Decision 012.

## Out of scope
Seed rows, ingest, UI.

## Handoff notes
- `$defs` added: `ChargingStat` (country = `ChargingArea` (CountryCode or EU27/EUROPE/WORLD), region?, period_end, metric_id, power_band_id (null = all), value ≥ 0, unit, source_id, definition_id, confidence, entered_by pipeline|staff, retrieved_at; **staff rows must carry `source_url`** (if/then, tested)), `ChargingMetric` (unit, higher_is_better, derived), `ChargingDefinition` (counts point/device/location/connector/port, country, source_id, includes_semi_public, fast_label, valid_from/to, replaced_by for series breaks, comparable_across_countries), `PowerBand` (current ac/dc/any, min_kw inclusive, max_kw exclusive, ours, source_id, maps_to our band ids), `CountryChargingLink` (country or ALL, tool, url, job official-map/local-app/map/route-planner/price-compare, order, label, deep_link_template).
- `abrp_typecode` (nullable string) on Variant and PublishedVariant.
- Taxonomy tables: `charging_metrics`, `charging_definitions`, `power_bands`. `country_charging_links` is config, so it is a def only (not in `Taxonomy` or `Catalogue`); where the charging stats ship in a release (catalogue vs own file) is left to WS1.
- Fixtures: `charging-stat`, `charging-definition`, `country-charging-link` (valid + invalid); `charging-metric`, `power-band` (valid).
- Unattended schema delegate (WS0), 2026-11-15. Additive only: no existing required field changed; `data/releases/1/catalogue.json` still validates (`tests/test_real_release.py` green).
- Taxonomy ids in data use the `Id` pattern, so **hyphens, not the spec's underscores** (`ac-onboard`, `iso15118-20`, `not-disclosed`, `needs-dc-box`, `public-points-dc`, `dc-150-349`). Same rule as Decision 010; seeders (T-019/T-024/T-031) must write them this way.
- New taxonomy tables are optional properties of `Taxonomy`, so old releases stay valid.
- New shared defs: `LocalizedText` (per-language map, en required) and `CountryCode` (`^[A-Z]{2}$`, UK not GB). New entities use `CountryCode` instead of the 5-value `Country` enum so US/AU rows need no schema change; markets are checked against config at release time.
- Tests: `uv run pytest tests/test_schema_fixtures.py tests/test_real_release.py` (111 passed), full pipeline suite 383 passed, `pnpm --filter @ev/schema test` 55 passed, `pnpm --filter @ev/schema typecheck` clean. `apps/web` typecheck has one unrelated error (`src/lib/state.test.ts` missing `tripFit`, web builder's work in progress).
- Judgement calls: QUESTIONS.md Q-054.

## Review
