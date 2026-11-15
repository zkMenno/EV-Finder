# Coverage, release 1

244 variants. Share of variants per field (count in brackets). 'estimate only' = our model or ratio, no source; derived values count by their weakest input.

| Field | 2+ agreeing sources | 1 source | estimate only | missing |
|---|---|---|---|---|
| battery_kwh_net | 22% (54) | 76% (185) | 2% (5) | 0% (0) |
| wltp_range_km | 19% (47) | 61% (149) | 0% (0) | 20% (48) |
| epa_range_km | 6% (15) | 36% (89) | 0% (0) | 57% (140) |
| consumption_kwh_100km | 2% (6) | 64% (155) | 23% (56) | 11% (27) |
| ac_kw | 28% (69) | 71% (173) | 0% (0) | 1% (2) |
| dc_peak_kw | 19% (46) | 79% (193) | 0% (0) | 2% (5) |
| dc_avg_10_80_kw | 0% (0) | 0% (0) | 98% (239) | 2% (5) |
| ac_km_per_h | 1% (3) | 65% (158) | 23% (55) | 11% (28) |
| dc_km_per_10min | 0% (0) | 0% (0) | 88% (214) | 12% (30) |
| real_range_km | 0% (0) | 0% (0) | 89% (216) | 11% (28) |
| power_kw | 0% (0) | 89% (216) | 0% (0) | 11% (28) |
| accel_0_100_s | 0% (0) | 55% (135) | 0% (0) | 45% (109) |
| boot_l | 0% (0) | 51% (125) | 0% (0) | 49% (119) |
| length_mm | 23% (55) | 75% (184) | 0% (0) | 2% (5) |
| weight_kg | 2% (6) | 52% (127) | 0% (0) | 45% (111) |
| towing_kg | 0% (0) | 28% (68) | 0% (0) | 72% (176) |
| seats | 30% (74) | 70% (170) | 0% (0) | 0% (0) |
| registered_count_nl | 0% (0) | 100% (244) | 0% (0) | 0% (0) |
| dc_minutes_10_80 | 0% (0) | 0% (0) | 98% (239) | 2% (5) |
| dc_km_per_20min | 0% (0) | 0% (0) | 88% (214) | 12% (30) |
| dc_peak_held_min | 0% (0) | 0% (0) | 98% (239) | 2% (5) |
| consumption_motorway_kwh_100km | 0% (0) | 0% (0) | 89% (217) | 11% (27) |
| voltage_nominal_v | 0% (0) | 14% (33) | 0% (0) | 86% (211) |
| voltage_max_v | 0% (0) | 0% (0) | 0% (0) | 100% (244) |
| charger_400v_kw | 0% (0) | 5% (12) | 0% (0) | 95% (232) |

## Other sections

- **EPA range** (`epa_range_km`, compared with EPA figures only): 104 variants; 15 with 2+ agreeing sources, of which 15 through fueleconomy.gov.
- **Generation years vs Wikidata** (corroboration only, +/-1 year): 12 generations checked, 10 corroborated; 11 of 13 years agree.
- **Known issues** (RDW APK defects, NL): 55 generations, 171 first-registration-year cohorts (46 marked few reports), 22 defect codes.
- **Charging stats** `bnetza`: 2720 rows in, 2720 rows shipped.
- **Charging stats** `dft-charging`: 141 rows in, 141 rows shipped.
- **Charging stats** `eafo`: 898 rows in, gated: status blocked.
