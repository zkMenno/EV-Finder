# Open EV catalogue, release 1

- Release: 1
- Date: 2026-11-15 (generated 2026-11-15T04:13:46+00:00)
- Variants: 244
- Sources: ademe, dft-veh, eea, fueleconomy, kba-fz10, kilowatt-openev, model-estimate, openev, rdw, rdw-tgk, seed-manual
- Licence: CC BY 4.0 (LICENSE); third-party credits in ATTRIBUTION.md

Files: `variants.csv` (UTF-8, comma-separated, header row, empty = unknown) and `variants.json` (the same rows plus this field list).

## How to cite

> Source: EV Shortlist (data release 1, 2026-11-15), CC BY 4.0

Please also keep the credits in ATTRIBUTION.md when you redistribute the data.

## Read this first

- Every value lists its sources (`<field>_sources`) and confidence (`<field>_confidence`); `estimate` means our own model, not a measurement.
- `real_range_km` on the `body-ratio` rung is a PROVISIONAL generic ratio (mild-weather mixed driving), not a measurement.
- `seed_manual_fields` marks values from hand-entered, unchecked seed data.
- Registration counts are official counts per country and kind; counts from different sources or periods are never added together. `registrations_json` has them all.
- Units are metric; prices carry their own currency.

## Fields

| Field | Unit | Description |
|---|---|---|
| `release` |  | Data release number |
| `variant_id` |  | Stable variant id (make-model-generation-variant) |
| `variant_name` |  | Variant name |
| `generation_id` |  | Generation id |
| `generation_name` |  | Generation name |
| `generation_uncertain` |  | true when the generation boundaries are not yet verified |
| `model_id` |  | Model id |
| `model_name` |  | Model name |
| `make_id` |  | Make id |
| `make_name` |  | Make name |
| `year_start` | year | First model year of the variant |
| `year_end` | year | Last model year (empty = still on sale) |
| `era` |  | Model-year band |
| `segment` |  | Market segment (A-F, J = SUV) |
| `body` |  | Body type |
| `drivetrain` |  | fwd | rwd | awd |
| `on_sale_new` |  | true when sold new in the last two model years |
| `quality_tier` |  | checked | sourced (2+ sources on battery and range) | single-source |
| `battery_kwh_net` | kWh | Usable battery capacity |
| `battery_kwh_net_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `battery_kwh_net_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `wltp_range_km` | km | WLTP combined range |
| `wltp_range_km_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `wltp_range_km_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `consumption_kwh_100km` | kWh/100 km | WLTP combined consumption |
| `consumption_kwh_100km_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `consumption_kwh_100km_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `consumption_motorway_kwh_100km` | kWh/100 km | Motorway consumption (~120 km/h) |
| `consumption_motorway_kwh_100km_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `consumption_motorway_kwh_100km_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `real_range_km` | km | Real-world range, mild-weather mixed driving (our model) |
| `real_range_km_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `real_range_km_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `real_range_rung` |  | Which rung of our real-range ladder produced real_range_km |
| `ac_kw` | kW | Maximum AC charging power |
| `ac_kw_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `ac_kw_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `ac_km_per_h` | km/h | km of WLTP range added per hour of AC charging |
| `ac_km_per_h_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `ac_km_per_h_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `dc_peak_kw` | kW | DC peak charging power |
| `dc_peak_kw_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `dc_peak_kw_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `dc_peak_kw_is_claim` |  | true when the DC peak is a maker claim |
| `dc_avg_10_80_kw` | kW | Average DC power from 10 to 80 % state of charge |
| `dc_avg_10_80_kw_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `dc_avg_10_80_kw_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `dc_minutes_10_80` | min | DC charging time from 10 to 80 % |
| `dc_minutes_10_80_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `dc_minutes_10_80_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `dc_km_per_10min` | km | Motorway km added in 10 minutes of DC charging |
| `dc_km_per_10min_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `dc_km_per_10min_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `dc_km_per_20min` | km | Motorway km added in 20 minutes of DC charging |
| `dc_km_per_20min_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `dc_km_per_20min_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `dc_peak_held_min` | min | Minutes within 10-80 % at >= 90 % of peak power |
| `dc_peak_held_min_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `dc_peak_held_min_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `dc_curve_status` |  | measured | estimated | default (generic shape) |
| `power_kw` | kW | Maximum motor power |
| `power_kw_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `power_kw_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `accel_0_100_s` | s | 0-100 km/h |
| `accel_0_100_s_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `accel_0_100_s_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `boot_l` | l | Boot volume |
| `boot_l_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `boot_l_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `length_mm` | mm | Length |
| `length_mm_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `length_mm_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `weight_kg` | kg | Kerb weight |
| `weight_kg_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `weight_kg_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `towing_kg` | kg | Braked towing capacity |
| `towing_kg_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `towing_kg_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `seats` |  | Number of seats |
| `seats_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `seats_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `platform_id` |  | Platform id |
| `platform_id_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `platform_id_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `battery_pack_id` |  | Battery pack id |
| `battery_pack_id_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `battery_pack_id_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `chemistry_id` |  | Cell chemistry (taxonomy id) |
| `chemistry_id_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `chemistry_id_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `cooling_id` |  | Battery cooling (taxonomy id) |
| `cooling_id_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `cooling_id_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `cell_format` |  | Cell format |
| `cell_format_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `cell_format_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `voltage_class_id` |  | 400 V / 800 V class (taxonomy id) |
| `voltage_class_id_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `voltage_class_id_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `voltage_nominal_v` | V | Nominal pack voltage |
| `voltage_nominal_v_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `voltage_nominal_v_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `voltage_max_v` | V | Maximum pack voltage |
| `voltage_max_v_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `voltage_max_v_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `charger_400v_mode` |  | How an 800 V car charges on a 400 V charger |
| `charger_400v_mode_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `charger_400v_mode_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `charger_400v_kw` | kW | DC power on a 400 V charger |
| `charger_400v_kw_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `charger_400v_kw_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `price_new_de` | currency | New list price, DE |
| `price_new_de_currency` |  | ISO 4217 currency of the price |
| `price_new_de_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `price_new_de_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `price_new_fr` | currency | New list price, FR |
| `price_new_fr_currency` |  | ISO 4217 currency of the price |
| `price_new_fr_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `price_new_fr_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `price_new_nl` | currency | New list price, NL |
| `price_new_nl_currency` |  | ISO 4217 currency of the price |
| `price_new_nl_sources` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `price_new_nl_confidence` |  | high | medium | low | estimate (our model, no direct source) |
| `reg_be_fleet` | vehicles | Official count, BE, cars on the road (newest period) |
| `reg_be_fleet_period` |  | Period of the count (date, quarter, year or month range) |
| `reg_be_fleet_level` |  | generation | model (count covers the whole model) |
| `reg_be_fleet_source` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `reg_be_new_registrations` | vehicles | Official count, BE, first registrations in period (newest period) |
| `reg_be_new_registrations_period` |  | Period of the count (date, quarter, year or month range) |
| `reg_be_new_registrations_level` |  | generation | model (count covers the whole model) |
| `reg_be_new_registrations_source` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `reg_de_fleet` | vehicles | Official count, DE, cars on the road (newest period) |
| `reg_de_fleet_period` |  | Period of the count (date, quarter, year or month range) |
| `reg_de_fleet_level` |  | generation | model (count covers the whole model) |
| `reg_de_fleet_source` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `reg_de_new_registrations` | vehicles | Official count, DE, first registrations in period (newest period) |
| `reg_de_new_registrations_period` |  | Period of the count (date, quarter, year or month range) |
| `reg_de_new_registrations_level` |  | generation | model (count covers the whole model) |
| `reg_de_new_registrations_source` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `reg_fr_fleet` | vehicles | Official count, FR, cars on the road (newest period) |
| `reg_fr_fleet_period` |  | Period of the count (date, quarter, year or month range) |
| `reg_fr_fleet_level` |  | generation | model (count covers the whole model) |
| `reg_fr_fleet_source` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `reg_fr_new_registrations` | vehicles | Official count, FR, first registrations in period (newest period) |
| `reg_fr_new_registrations_period` |  | Period of the count (date, quarter, year or month range) |
| `reg_fr_new_registrations_level` |  | generation | model (count covers the whole model) |
| `reg_fr_new_registrations_source` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `reg_nl_fleet` | vehicles | Official count, NL, cars on the road (newest period) |
| `reg_nl_fleet_period` |  | Period of the count (date, quarter, year or month range) |
| `reg_nl_fleet_level` |  | generation | model (count covers the whole model) |
| `reg_nl_fleet_source` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `reg_nl_new_registrations` | vehicles | Official count, NL, first registrations in period (newest period) |
| `reg_nl_new_registrations_period` |  | Period of the count (date, quarter, year or month range) |
| `reg_nl_new_registrations_level` |  | generation | model (count covers the whole model) |
| `reg_nl_new_registrations_source` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `reg_uk_fleet` | vehicles | Official count, UK, cars on the road (newest period) |
| `reg_uk_fleet_period` |  | Period of the count (date, quarter, year or month range) |
| `reg_uk_fleet_level` |  | generation | model (count covers the whole model) |
| `reg_uk_fleet_source` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `reg_uk_new_registrations` | vehicles | Official count, UK, first registrations in period (newest period) |
| `reg_uk_new_registrations_period` |  | Period of the count (date, quarter, year or month range) |
| `reg_uk_new_registrations_level` |  | generation | model (count covers the whole model) |
| `reg_uk_new_registrations_source` |  | Source id(s) behind the value; see ATTRIBUTION.md |
| `registrations_json` |  | Every official count: country, source, period, kind, level, count |
| `seed_manual_fields` |  | Fields resting on hand-entered, unchecked seed data (confidence low) |
| `estimate_fields` |  | Fields that are our model estimates |
