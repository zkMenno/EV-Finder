# Coverage, release 1

218 variants. Share of variants per field (count in brackets). 'estimate only' = our model or ratio, no source; derived values count by their weakest input.

| Field | 2+ agreeing sources | 1 source | estimate only | missing |
|---|---|---|---|---|
| battery_kwh_net | 19% (42) | 78% (171) | 2% (5) | 0% (0) |
| wltp_range_km | 10% (22) | 51% (112) | 0% (0) | 39% (84) |
| epa_range_km | 7% (15) | 37% (80) | 0% (0) | 56% (123) |
| consumption_kwh_100km | 0% (1) | 29% (64) | 44% (96) | 26% (57) |
| ac_kw | 25% (54) | 74% (162) | 0% (0) | 1% (2) |
| dc_peak_kw | 17% (36) | 81% (177) | 0% (0) | 2% (5) |
| dc_avg_10_80_kw | 0% (0) | 0% (0) | 98% (213) | 2% (5) |
| ac_km_per_h | 0% (1) | 29% (64) | 44% (95) | 27% (58) |
| dc_km_per_10min | 0% (0) | 0% (0) | 72% (158) | 28% (60) |
| real_range_km | 0% (0) | 0% (0) | 74% (161) | 26% (57) |
| power_kw | 0% (0) | 87% (190) | 0% (0) | 13% (28) |
| accel_0_100_s | 0% (0) | 50% (110) | 0% (0) | 50% (108) |
| boot_l | 0% (0) | 54% (117) | 0% (0) | 46% (101) |
| length_mm | 0% (0) | 99% (215) | 0% (0) | 1% (3) |
| weight_kg | 3% (6) | 47% (103) | 0% (0) | 50% (109) |
| towing_kg | 0% (0) | 31% (68) | 0% (0) | 69% (150) |
| seats | 0% (0) | 100% (218) | 0% (0) | 0% (0) |
| registered_count_nl | 0% (0) | 100% (218) | 0% (0) | 0% (0) |
| dc_minutes_10_80 | 0% (0) | 0% (0) | 98% (213) | 2% (5) |
| dc_km_per_20min | 0% (0) | 0% (0) | 72% (158) | 28% (60) |
| dc_peak_held_min | 0% (0) | 0% (0) | 98% (213) | 2% (5) |
| consumption_motorway_kwh_100km | 0% (0) | 0% (0) | 74% (161) | 26% (57) |
| voltage_nominal_v | 0% (0) | 13% (29) | 0% (0) | 87% (189) |
| voltage_max_v | 0% (0) | 0% (0) | 0% (0) | 100% (218) |
| charger_400v_kw | 0% (0) | 6% (12) | 0% (0) | 94% (206) |

## Other sections

- **EPA range** (`epa_range_km`, compared with EPA figures only): 95 variants; 15 with 2+ agreeing sources, of which 15 through fueleconomy.gov.
- **Generation years vs Wikidata** (corroboration only, +/-1 year): 12 generations checked, 10 corroborated; 11 of 13 years agree.
- **Known issues** (RDW APK defects, NL): 53 generations, 168 first-registration-year cohorts (43 marked few reports), 22 defect codes.
- **Charging stats** `bnetza`: 2720 rows in, 2720 rows shipped.
- **Charging stats** `dft-charging`: 141 rows in, 141 rows shipped.
- **Charging stats** `eafo`: 898 rows in, gated: status blocked.
