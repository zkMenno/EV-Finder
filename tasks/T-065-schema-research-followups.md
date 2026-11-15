# T-065 Schema follow-ups from the research pack
Role: coordinator (WS0)   Lane: packages/schema   Wave: 7
Status: todo

## Goal
Add the fields the research pack asked for (workstreams/OVERNIGHT2/MORNING-2.md, "Schema requests").

## Acceptance criteria
- [ ] FinanceProfile: `series_id`, `reference_period` (R-20)
- [ ] Bidirectional caveats: `bundle_only`, `ccs_hw_required`, `order_date_from` (R-25 §8)
- [ ] `consumption_epa_kwh_100km` separate from WLTP; optional EPA city/highway range and 240 V full-charge time (R-28)
- [ ] Clue types `dc_charge_kw`, `in_car_menu`, `vehicle_mass_kg` (R-22 §3) as taxonomy rows (WS3) if `clue_types` is a taxonomy
- [ ] Variant `replaced_by` (R-24); check `abrp_typecode` already exists (T-023)
- [ ] All optional; release 1 still validates; generated types updated

## Inputs
research/R-20, R-22, R-24, R-25, R-28; Decision 036.

## Out of scope
Data rows.

## Handoff notes

## Review
