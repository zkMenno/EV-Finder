# Coverage, release 1

244 variants. Share of variants per field (count in brackets). 'estimate only' = our model or ratio, no source; derived values count by their weakest input.

| Field | 2+ agreeing sources | 1 source | estimate only | missing |
|---|---|---|---|---|
| battery_kwh_net | 21% (52) | 76% (186) | 2% (6) | 0% (0) |
| wltp_range_km | 30% (73) | 50% (123) | 0% (0) | 20% (48) |
| epa_range_km | 11% (27) | 32% (79) | 0% (0) | 57% (138) |
| consumption_kwh_100km | 4% (9) | 57% (139) | 28% (68) | 11% (28) |
| ac_kw | 27% (67) | 72% (175) | 0% (0) | 1% (2) |
| dc_peak_kw | 19% (46) | 68% (166) | 0% (0) | 13% (32) |
| dc_avg_10_80_kw | 0% (0) | 0% (0) | 92% (225) | 8% (19) |
| ac_km_per_h | 2% (6) | 58% (142) | 27% (67) | 12% (29) |
| dc_km_per_10min | 0% (0) | 0% (0) | 84% (204) | 16% (40) |
| real_range_km | 0% (0) | 0% (0) | 88% (215) | 12% (29) |
| power_kw | 0% (0) | 89% (216) | 0% (0) | 11% (28) |
| accel_0_100_s | 0% (0) | 55% (135) | 0% (0) | 45% (109) |
| boot_l | 0% (0) | 51% (125) | 0% (0) | 49% (119) |
| length_mm | 22% (53) | 76% (186) | 0% (0) | 2% (5) |
| weight_kg | 2% (5) | 52% (128) | 0% (0) | 45% (111) |
| towing_kg | 0% (0) | 28% (68) | 0% (0) | 72% (176) |
| seats | 27% (66) | 73% (178) | 0% (0) | 0% (0) |
| registered_count_nl | 0% (0) | 100% (244) | 0% (0) | 0% (0) |
| dc_minutes_10_80 | 0% (0) | 0% (0) | 92% (225) | 8% (19) |
| dc_km_per_20min | 0% (0) | 0% (0) | 84% (204) | 16% (40) |
| dc_peak_held_min | 0% (0) | 0% (0) | 92% (225) | 8% (19) |
| consumption_motorway_kwh_100km | 0% (0) | 0% (0) | 89% (216) | 11% (28) |
| voltage_nominal_v | 0% (0) | 14% (33) | 0% (0) | 86% (211) |
| voltage_max_v | 0% (0) | 0% (0) | 0% (0) | 100% (244) |
| charger_400v_kw | 0% (0) | 5% (12) | 0% (0) | 95% (232) |

## Other sections

- **EPA range** (`epa_range_km`, compared with EPA figures only): 106 variants; 27 with 2+ agreeing sources, of which 27 through fueleconomy.gov.
- **Generation years vs Wikidata** (corroboration only, +/-1 year): 12 generations checked, 10 corroborated; 11 of 13 years agree.
- **Known issues** (RDW APK defects, NL): 55 generations, 171 first-registration-year cohorts (46 marked few reports), 22 defect codes.
- **Charging stats** `bnetza`: 2720 rows in, 2720 rows shipped.
- **Charging stats** `dft-charging`: 141 rows in, 141 rows shipped.
- **Charging stats** `eafo`: 898 rows in, gated: status blocked.
