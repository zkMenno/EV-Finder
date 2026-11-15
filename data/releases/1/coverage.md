# Coverage, release 1

226 variants. Share of variants per field (count in brackets). 'estimate only' = our model or ratio, no source; derived values count by their weakest input.

| Field | 2+ agreeing sources | 1 source | estimate only | missing |
|---|---|---|---|---|
| battery_kwh_net | 24% (55) | 70% (158) | 3% (6) | 3% (7) |
| wltp_range_km | 31% (70) | 50% (114) | 0% (0) | 19% (42) |
| epa_range_km | 0% (0) | 44% (100) | 0% (0) | 56% (126) |
| consumption_kwh_100km | 4% (9) | 58% (131) | 26% (58) | 12% (28) |
| ac_kw | 32% (72) | 65% (148) | 0% (0) | 3% (6) |
| dc_peak_kw | 22% (50) | 69% (156) | 0% (0) | 9% (20) |
| dc_avg_10_80_kw | 0% (0) | 0% (0) | 92% (209) | 8% (17) |
| ac_km_per_h | 3% (7) | 59% (133) | 25% (57) | 13% (29) |
| dc_km_per_10min | 0% (0) | 0% (0) | 83% (188) | 17% (38) |
| real_range_km | 0% (0) | 0% (0) | 90% (203) | 10% (23) |
| power_kw | 0% (0) | 88% (199) | 0% (0) | 12% (27) |
| accel_0_100_s | 0% (0) | 57% (129) | 0% (0) | 43% (97) |
| boot_l | 0% (0) | 53% (119) | 0% (0) | 47% (107) |
| length_mm | 26% (59) | 72% (163) | 0% (0) | 2% (4) |
| weight_kg | 2% (5) | 54% (121) | 0% (0) | 44% (100) |
| towing_kg | 0% (0) | 31% (69) | 0% (0) | 69% (157) |
| seats | 31% (69) | 69% (157) | 0% (0) | 0% (0) |
| registered_count_nl | 0% (0) | 100% (226) | 0% (0) | 0% (0) |
| dc_minutes_10_80 | 0% (0) | 0% (0) | 89% (202) | 11% (24) |
| dc_km_per_20min | 0% (0) | 0% (0) | 83% (188) | 17% (38) |
| dc_peak_held_min | 0% (0) | 0% (0) | 89% (202) | 11% (24) |
| consumption_motorway_kwh_100km | 0% (0) | 0% (0) | 88% (198) | 12% (28) |
| voltage_nominal_v | 0% (0) | 15% (35) | 0% (0) | 85% (191) |
| voltage_max_v | 0% (0) | 0% (0) | 0% (0) | 100% (226) |
| charger_400v_kw | 0% (0) | 5% (12) | 0% (0) | 95% (214) |

## Battery pack and platform links

Per row: linked in data/seed/variant_links.yaml, linked by rule (same generation; for packs, usable kWh fits exactly one of the generation's packs), or missing.

| Link | variant_links.yaml | rule | missing |
|---|---|---|---|
| battery_pack_id | 55% (124) | 18% (40) | 27% (62) |
| platform_id | 66% (150) | 17% (38) | 17% (38) |

Rows missing a link (62):

- `audi-a6-e-tron-gen1-avant`: platform: no link in this generation; pack: no pack linked in this generation
- `audi-a6-e-tron-gen1-sportback`: platform: no link in this generation; pack: no pack linked in this generation
- `audi-q6-e-tron-gen1-quattro`: platform: no link in this generation; pack: no pack linked in this generation
- `audi-q6-e-tron-gen1-quattro-sportback`: platform: no link in this generation; pack: no pack linked in this generation
- `audi-q6-e-tron-gen1-sq6`: platform: no link in this generation; pack: no pack linked in this generation
- `bmw-i5-gen1-edrive40`: platform: no link in this generation; pack: no pack linked in this generation
- `bmw-i5-gen1-m60`: platform: no link in this generation; pack: no pack linked in this generation
- `bmw-ix-gen1-m60`: platform: no link in this generation; pack: no pack linked in this generation
- `bmw-ix-gen1-xdrive40`: platform: no link in this generation; pack: no pack linked in this generation
- `bmw-ix-gen1-xdrive50`: platform: no link in this generation; pack: no pack linked in this generation
- `bmw-ix1-gen1-xdrive30`: platform: no link in this generation; pack: no pack linked in this generation
- `bmw-ix3-gen1-ix3`: platform: no link in this generation; pack: no pack linked in this generation
- `byd-atto-3-gen1-standard-range`: pack: usable 49 kWh fits none of byd-blade-60
- `byd-atto-3-gen1-standard-range-2025`: pack: usable 49.92 kWh fits none of byd-blade-60
- `cupra-tavascan-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `cupra-tavascan-gen1-vz`: platform: no link in this generation; pack: no pack linked in this generation
- `ford-explorer-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `ford-mustang-mach-e-gen1-premium`: pack: usable 82 kWh fits none of ford-mach-e-75/ford-mach-e-98
- `ford-puma-gen-e-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `hyundai-ioniq-5-gen1-n`: pack: usable 78 kWh fits none of egmp-58/egmp-72-6/egmp-77-4
- `hyundai-ioniq-6-gen1-awd`: pack: usable 72.6 kWh fits none of egmp-53/egmp-77-4
- `hyundai-ioniq-6-gen1-long-range`: pack: usable 72.6 kWh fits none of egmp-53/egmp-77-4
- `hyundai-kona-electric-sx2-long-range`: pack: usable 58 kWh fits none of hk-kona-sx2-48/hk-kona-sx2-65
- `hyundai-kona-electric-sx2-standard-range`: pack: variant has no usable kWh to compare
- `mercedes-cla-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqa-h243-300-4matic`: pack: variant has no usable kWh to compare
- `mercedes-eqa-h243-350-4matic`: pack: variant has no usable kWh to compare
- `mercedes-eqa-h243-base`: pack: variant has no usable kWh to compare
- `mercedes-eqb-gen1-300-4matic`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqb-gen1-300-4matic-7-seater`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqb-gen1-350-4matic`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqb-gen1-350-4matic-7-seater`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqb-gen1-7-seater`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqb-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `polestar-2-gen1-long-range-dual-motor`: pack: usable 75 kWh fits 2 packs cma-78/cma-82
- `polestar-2-gen1-long-range-single-motor`: pack: usable 75 kWh fits 2 packs cma-78/cma-82
- `polestar-2-gen1-performance-pack`: pack: usable 75 kWh fits 2 packs cma-78/cma-82
- `polestar-2-gen1-performance-pack-long-range-dual-motor`: pack: usable 75 kWh fits 2 packs cma-78/cma-82
- `porsche-macan-electric-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `porsche-macan-electric-gen1-turbo`: platform: no link in this generation; pack: no pack linked in this generation
- `porsche-taycan-gen1-4s`: platform: no link in this generation; pack: no pack linked in this generation
- `porsche-taycan-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `porsche-taycan-gen1-turbo`: platform: no link in this generation; pack: no pack linked in this generation
- `porsche-taycan-gen1-turbo-gt`: platform: no link in this generation; pack: no pack linked in this generation
- `porsche-taycan-gen1-turbo-s`: platform: no link in this generation; pack: no pack linked in this generation
- `renault-5-e-tech-gen1-110-kw`: pack: no pack linked in this generation
- `renault-5-e-tech-gen1-40-kwh`: pack: no pack linked in this generation
- `renault-5-e-tech-gen1-base`: pack: no pack linked in this generation
- `renault-scenic-e-tech-gen1-60-kwh`: platform: no link in this generation; pack: no pack linked in this generation
- `renault-scenic-e-tech-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `skoda-elroq-gen1-base`: pack: no pack linked in this generation
- `skoda-elroq-gen1-rs`: pack: no pack linked in this generation
- `toyota-bz4x-gen1-front-wheel-drive`: platform: no link in this generation; pack: no pack linked in this generation
- `toyota-bz4x-gen1-front-wheel-drive-all-wheel-drive`: platform: no link in this generation; pack: no pack linked in this generation
- `volkswagen-id-buzz-gen1-cargo`: pack: no pack linked in this generation
- `volkswagen-id-buzz-gen1-pro`: pack: no pack linked in this generation
- `volkswagen-id7-gen1-pro`: pack: no pack linked in this generation
- `volkswagen-id7-gen1-tour`: pack: no pack linked in this generation
- `volvo-ex30-gen1-69-kwh`: platform: no link in this generation; pack: no pack linked in this generation
- `volvo-ex30-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `volvo-ex30-gen1-twin-motor`: platform: no link in this generation; pack: no pack linked in this generation
- `volvo-ex30-gen1-twin-motor-performance`: platform: no link in this generation; pack: no pack linked in this generation

## Other sections

- **EPA range** (`epa_range_km`, compared with EPA figures only): 100 variants; 0 with 2+ agreeing sources, of which 0 through fueleconomy.gov.
- **Generation years vs Wikidata** (corroboration only, +/-1 year): 12 generations checked, 10 corroborated; 11 of 13 years agree.
- **Known issues** (RDW APK defects, NL): 55 generations, 171 first-registration-year cohorts (46 marked few reports), 22 defect codes.
- **Charging stats** `bnetza`: 2720 rows in, 2720 rows shipped.
- **Charging stats** `dft-charging`: 141 rows in, 141 rows shipped.
- **Charging stats** `eafo`: 898 rows in, gated: status blocked.
