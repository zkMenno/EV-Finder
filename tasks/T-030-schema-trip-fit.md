# T-030 Schema: Trip fit taxonomies, variant fields, consumption tests and model
Role: coordinator (WS0)   Lane: packages/schema   Wave: 6
Status: review (schema delegate for WS0, 2026-11-15)

## Goal
Add the types from Decision 013 and the Trip fit spec §7.

## Acceptance criteria
- [x] Taxonomies road_classes, speed_profiles, temperature_bands, heater_types, usage_profiles
- [x] Variant facts heat_pump (standard/option/none/not-disclosed), drag_coefficient, frontal_area, kerb_mass, wheel_size, usable_kwh
- [x] ConsumptionTest (speed, temperature, wheels, source, date, conditions) and ConsumptionModel (per variant: band × temperature cells with rung + confidence)
- [x] ClimateNormal per town/grid cell; fixtures + generated types

## Inputs
docs/spec/trip-fit.md §5 and §7, Decision 013.

## Out of scope
Builders, UI.

## Handoff notes
- `$defs` added: enums `RoadBand` (town/rural/motorway), `HeatPumpFitment` (standard/option/none/not-disclosed), `ConsumptionRung` (measured/platform/physics/wltp-ratio), `WeightLevel`; taxonomy rows `RoadClass` (band, osm_highway[]), `SpeedProfile` (country, `speeds_kmh` = `BandSpeeds`, style offsets), `TemperatureBand` (min_c/max_c, representative_c), `HeaterType` (temperature_curve [(°C, factor)], warm_up_kwh, sources), `UsageProfile` (kind base|addon, applies_when, weights factor → WeightLevel, weight_steps for add-ons); entities `ConsumptionTest` (test_kind, speed_kmh, road_band, band_km, temperature_c, wheel_size_in, tyre, tyre_season, consumption_wh_km, **energy_basis battery|wall**, observed_at, conditions{preconditioned, hvac, heat_pump_fitted, payload_kg, battery_soh_pct, ...}, full `Source`), `ConsumptionModel` (variant_id, release, heat_pump, usable_kwh, mass_kg, warm_up_kwh, regen_recovery, `cells[ConsumptionCell{road_band, temperature_band_id, heater_type_id?, wh_km, p10/p90, rung, confidence, test_ids}]`), `ClimateNormal` (town|grid-cell, geonames_id, lat/lon, period 'YYYY-YYYY', 12 `MonthlyClimate{mean_c, p10_c}`, source_id).
- FactField: `heat_pump`, `drag_coefficient`, `frontal_area_m2`, `kerb_mass_kg`, `wheel_size_in`. PublishedVariant: `heat_pump`, `drag_coefficient`, `frontal_area_m2`, `kerb_mass_kg`, `wheel_sizes_in[]`.
- **No separate `usable_kwh` fact**: `battery_kwh_net` already is the usable capacity (and `BatteryPack.usable_kwh` exists); `ConsumptionModel.usable_kwh` carries the value the model used. Unit suffixes follow the repo's field naming (`length_mm`, `weight_kg`).
- A heat pump that is an option gets two cell sets in `ConsumptionModel` (one per `heater_type_id`), so the UI can show both cases.
- Taxonomy tables: `road_classes`, `speed_profiles`, `temperature_bands`, `heater_types`, `usage_profiles`. ConsumptionModel and ClimateNormal are not added to `Catalogue`; the release file layout (matrix JSON, climate file) is WS1's call.
- Fixtures: `road-class`, `speed-profile`, `usage-profile`, `consumption-test`, `consumption-model`, `climate-normal`, `taxonomy` (valid + invalid); `temperature-band`, `heater-type`, `fact-heat-pump`, `fact-drag` (valid).
- Unattended schema delegate (WS0), 2026-11-15. Additive only: no existing required field changed; `data/releases/1/catalogue.json` still validates (`tests/test_real_release.py` green).
- Taxonomy ids in data use the `Id` pattern, so **hyphens, not the spec's underscores** (`ac-onboard`, `iso15118-20`, `not-disclosed`, `needs-dc-box`, `public-points-dc`, `dc-150-349`). Same rule as Decision 010; seeders (T-019/T-024/T-031) must write them this way.
- New taxonomy tables are optional properties of `Taxonomy`, so old releases stay valid.
- New shared defs: `LocalizedText` (per-language map, en required) and `CountryCode` (`^[A-Z]{2}$`, UK not GB). New entities use `CountryCode` instead of the 5-value `Country` enum so US/AU rows need no schema change; markets are checked against config at release time.
- Tests: `uv run pytest tests/test_schema_fixtures.py tests/test_real_release.py` (111 passed), full pipeline suite 383 passed, `pnpm --filter @ev/schema test` 55 passed, `pnpm --filter @ev/schema typecheck` clean. `apps/web` typecheck has one unrelated error (`src/lib/state.test.ts` missing `tripFit`, web builder's work in progress).
- Judgement calls: QUESTIONS.md Q-054.

## Review
