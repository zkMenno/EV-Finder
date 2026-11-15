# T-030 Schema: Trip fit taxonomies, variant fields, consumption tests and model
Role: coordinator (WS0)   Lane: packages/schema   Wave: 6
Status: todo

## Goal
Add the types from Decision 013 and the Trip fit spec §7.

## Acceptance criteria
- [ ] Taxonomies road_classes, speed_profiles, temperature_bands, heater_types, usage_profiles
- [ ] Variant facts heat_pump (standard/option/none/not-disclosed), drag_coefficient, frontal_area, kerb_mass, wheel_size, usable_kwh
- [ ] ConsumptionTest (speed, temperature, wheels, source, date, conditions) and ConsumptionModel (per variant: band × temperature cells with rung + confidence)
- [ ] ClimateNormal per town/grid cell; fixtures + generated types

## Inputs
docs/spec/trip-fit.md §5 and §7, Decision 013.

## Out of scope
Builders, UI.

## Handoff notes

## Review
