# T-065 Schema follow-ups from the research pack
Role: coordinator (WS0)   Lane: packages/schema   Wave: 7
Status: review (WS0 coordinator, 2026-11-15; branch t-066-schema-shortlist-rules, shared PR with T-066)

## Goal
Add the fields the research pack asked for (workstreams/OVERNIGHT2/MORNING-2.md, "Schema requests").

## Acceptance criteria
- [x] (already present) FinanceProfile: `series_id`, `reference_period` (R-20)
- [x] (no schema change; taxonomy rows for WS3) Bidirectional caveats: `bundle_only`, `ccs_hw_required`, `order_date_from` (R-25 §8)
- [x] `consumption_epa_kwh_100km` separate from WLTP; optional EPA city/highway range and 240 V full-charge time (R-28)
- [x] (no schema change; taxonomy rows for WS3) Clue types `dc_charge_kw`, `in_car_menu`, `vehicle_mass_kg` (R-22 §3) as taxonomy rows (WS3) if `clue_types` is a taxonomy
- [x] Variant `replaced_by` (R-24); check `abrp_typecode` already exists (T-023)
- [x] All optional; release 1 still validates; generated types updated

## Inputs
research/R-20, R-22, R-24, R-25, R-28; Decision 036.

## Out of scope
Data rows.

## Handoff notes
2026-11-15, WS0. Checked what existed before adding anything.
- **FinanceProfile series_id / reference_period:** already in the schema as `FinanceProfile.source.series_id` and `source.period` (FinanceSource, YYYY / YYYY-MM). R-20's `reference_period` maps to `source.period`. Nothing added.
- **Bidi caveats `bundle_only`, `ccs_hw_required`, `order_date_from`:** caveats are rows in data/taxonomy/bidi_caveats.yaml (BidiCaveat), not schema enums; `param_kind: date` already covers order-date-from. WS3: add rows `bundle-only`, `ccs-hw-required`, `order-date-from` (hyphen ids).
- **EPA (R-28):** `PublishedVariant.consumption_epa_kwh_100km` (separate from WLTP), `epa_range_city_km`, `epa_range_hwy_km`, `ac_full_charge_h` (240 V empty-to-full, hours, info only).
- **Clue types `dc_charge_kw`, `in_car_menu`, `vehicle_mass_kg`:** clue_types is a taxonomy (ClueType rows); value kinds number / text / number fit. WS3 adds rows (ids `dc-charge-kw`, `in-car-menu`, `vehicle-mass-kg`).
- **ABRP (R-24):** `abrp_typecode` already existed (Variant + PublishedVariant). Added `Variant.abrp_deprecated`, `Variant.abrp_replaced_by` and `PublishedVariant.abrp_replaced_by`. Named `abrp_replaced_by` because R-24's `replaced_by` is ABRP's code replacement; our own renamed variants go through retired ids (T-062).
- **WS1 requests:** `TownsRelease` (+ `Town`, `WeatherStation`, `ProvenanceNote`, `ClimateProvenance`) and `ConsumptionMatrixRelease` added, checked against real pipeline output from the T-034 / T-033 test fixtures. `ConsumptionTest.source` is now `Source | SourceRef` (the matrix ships `{id}` only). `PublishedVariant.ac_kw_optional` added (T-063). Retired ids: added `RetiredIds` + `RetiredIdsFile` (types the current retired_ids.json). **Not** added as `Catalogue.retired_ids` yet: the pipeline switches to the in-catalogue path as soon as Catalogue has it, and `pipeline/tests/test_t062_retired.py` still asserts the separate file, so that one-line schema change must ship with WS1's test update. Same for FactField `ac_kw_optional` and the EPA FactFields: `pipeline/tests/test_manual.py` needs a unit per FactField (manual/facts.py), so WS1 adds the FactField entries + units together (or asks WS0 to).
- Release 1 `catalogue.json` and `charging_stats.json` still validate; pipeline (1,353), schema (108) and web (285) tests green locally; web typecheck green.

## Review
