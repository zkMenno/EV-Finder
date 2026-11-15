# T-018 Schema: bidirectional capability, charging ports, ISO 15118-20 fact
Role: coordinator   Lane: packages/schema   Wave: 5
Status: review (schema delegate for WS0, 2026-11-15)

## Goal
Add the types from docs/spec/bidirectional-and-connectors.md §3 so data and web lanes can build on them.

## Acceptance criteria
- [x] `$defs` for BidiMode, BidiRoute, BidiProtocol, BidiCaveat (with optional param), BidiStatus, ConnectorType, BidiEquipment, BidiCapability, ChargingPort; variant Fact `iso15118_20_support`
- [x] Taxonomy ids are free strings validated against data/taxonomy at release time (same pattern as Decision 010)
- [x] Valid + invalid fixtures for BidiCapability and ChargingPort; generated TS + Python types updated
- [x] PublishedVariant carries `bidi[]` and `ports[]` (market + model year keyed)

## Inputs
docs/spec/bidirectional-and-connectors.md, research/R-01-bidirectional-and-connectors.md, Decision 010, 011.

## Out of scope
Seed data, UI.

## Handoff notes
- `$defs` added: taxonomy rows `BidiMode`, `BidiRoute` (+ `inverter_location`, `needs_special_box`), `BidiProtocol` (+ `standard`), `BidiCaveat` (`param_kind` none/number/date/version, `param_unit`, `severity`; label/short may contain `{param}`), `BidiStatus` (+ `filter_group` live / pilot-or-announced / not-available for the default "live in your country" filter), `ConnectorType` (`current` ac/dc), `BidiEquipment` (`price_band` = `PriceBandEur` in euros, markets, compatible platforms/variants, sources). Entities `BidiCapability` (subject_type variant|platform + subject_id, mode/route/protocol ids, min_software, min_battery_net_kwh, build_date_from, model_years, equipment_ids, tariff_required, caveats `[BidiCaveatRef{id, param?}]`, `market_status{CountryCode: BidiMarketStatus}` with its own status_id, source_ids, checked_at (for the 90-day flag), confidence, tariff_names, country caveats), `ChargingPort` (variant, market, model_year_from/to, ac_inlet_id, dc_inlet_id (null = no DC), native_or_adapter, supercharger_access native/adapter/magic-dock/none/not-disclosed, adapters_included `[AdapterRef]`). `Iso15118Support` enum yes/no/not-disclosed.
- FactField `iso15118_20_support`; PublishedVariant `iso15118_20_support` (default not-disclosed), `bidi[]` (BidiCapability, platform rows resolved in), `ports[]` (ChargingPort).
- Taxonomy tables: `bidi_modes`, `bidi_routes`, `bidi_protocols`, `bidi_caveats`, `bidi_status`, `connector_types`, `bidi_equipment`.
- Fixtures: `bidi-capability`, `charging-port`, `bidi-caveat`, `bidi-equipment`, `connector-type` (valid + invalid); `bidi-mode`, `bidi-route`, `bidi-protocol`, `bidi-status`, `fact-iso15118` (valid); `published-variant.valid.json` now carries `bidi`, `ports`, `iso15118_20_support`.
- For WS1: the Fact value of `iso15118_20_support` (and `heat_pump`) is not constrained in JSON Schema (an if/then on Fact turned the generated TS `Fact` into `{[k]: unknown}`), so the release validator should check it against `Iso15118Support`.
- Unattended schema delegate (WS0), 2026-11-15. Additive only: no existing required field changed; `data/releases/1/catalogue.json` still validates (`tests/test_real_release.py` green).
- Taxonomy ids in data use the `Id` pattern, so **hyphens, not the spec's underscores** (`ac-onboard`, `iso15118-20`, `not-disclosed`, `needs-dc-box`, `public-points-dc`, `dc-150-349`). Same rule as Decision 010; seeders (T-019/T-024/T-031) must write them this way.
- New taxonomy tables are optional properties of `Taxonomy`, so old releases stay valid.
- New shared defs: `LocalizedText` (per-language map, en required) and `CountryCode` (`^[A-Z]{2}$`, UK not GB). New entities use `CountryCode` instead of the 5-value `Country` enum so US/AU rows need no schema change; markets are checked against config at release time.
- Tests: `uv run pytest tests/test_schema_fixtures.py tests/test_real_release.py` (111 passed), full pipeline suite 383 passed, `pnpm --filter @ev/schema test` 55 passed, `pnpm --filter @ev/schema typecheck` clean. `apps/web` typecheck has one unrelated error (`src/lib/state.test.ts` missing `tripFit`, web builder's work in progress).
- Judgement calls: QUESTIONS.md Q-054.

## Review
