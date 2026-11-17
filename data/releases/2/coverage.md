# Coverage, release 2

271 variants. Share of variants per field (count in brackets). 'estimate only' = our model or ratio, no source; derived values count by their weakest input.

| Field | 2+ agreeing sources | 1 source | estimate only | missing |
|---|---|---|---|---|
| battery_kwh_net | 23% (63) | 74% (200) | 2% (6) | 1% (2) |
| wltp_range_km | 27% (74) | 54% (145) | 0% (0) | 19% (52) |
| epa_range_km | 0% (0) | 43% (117) | 0% (0) | 57% (154) |
| consumption_kwh_100km | 3% (8) | 55% (148) | 31% (85) | 11% (30) |
| ac_kw | 32% (86) | 66% (179) | 0% (0) | 2% (6) |
| ac_kw_optional | 0% (0) | 0% (0) | 0% (0) | 100% (271) |
| dc_peak_kw | 23% (61) | 69% (186) | 0% (0) | 9% (24) |
| dc_avg_10_80_kw | 0% (0) | 1% (3) | 92% (250) | 7% (18) |
| ac_km_per_h | 3% (7) | 55% (149) | 31% (84) | 11% (31) |
| dc_km_per_10min | 0% (0) | 0% (0) | 85% (231) | 15% (40) |
| real_range_km | 0% (0) | 0% (0) | 88% (239) | 12% (32) |
| real_range_winter_km | 0% (0) | 0% (0) | 87% (237) | 13% (34) |
| power_kw | 0% (0) | 90% (244) | 0% (0) | 10% (27) |
| accel_0_100_s | 0% (0) | 65% (175) | 0% (0) | 35% (96) |
| boot_l | 0% (0) | 49% (133) | 0% (0) | 51% (138) |
| length_mm | 24% (64) | 74% (200) | 0% (0) | 3% (7) |
| weight_kg | 2% (6) | 60% (162) | 0% (0) | 38% (103) |
| towing_kg | 0% (0) | 25% (69) | 0% (0) | 75% (202) |
| seats | 30% (80) | 70% (191) | 0% (0) | 0% (0) |
| registered_count_nl | 0% (0) | 100% (271) | 0% (0) | 0% (0) |
| dc_minutes_10_80 | 0% (0) | 2% (5) | 92% (248) | 7% (18) |
| dc_km_per_20min | 0% (0) | 0% (0) | 85% (231) | 15% (40) |
| dc_peak_held_min | 0% (0) | 0% (0) | 92% (248) | 8% (23) |
| consumption_motorway_kwh_100km | 0% (0) | 0% (0) | 89% (241) | 11% (30) |
| voltage_nominal_v | 0% (0) | 14% (39) | 0% (0) | 86% (232) |
| voltage_max_v | 0% (0) | 0% (0) | 0% (0) | 100% (271) |
| charger_400v_kw | 0% (0) | 4% (12) | 0% (0) | 96% (259) |

## Battery pack and platform links

Per row: linked in data/seed/variant_links.yaml, linked by rule (same generation; for packs, usable kWh fits exactly one of the generation's packs), or missing.

| Link | variant_links.yaml | rule | missing |
|---|---|---|---|
| battery_pack_id | 46% (124) | 15% (41) | 39% (106) |
| platform_id | 55% (150) | 13% (35) | 32% (86) |

Rows missing a link (106):

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
- `ds-3-e-tense-facelift-base`: platform: no link in this generation; pack: no pack linked in this generation
- `fiat-600e-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `fiat-600e-gen1-la-prima`: platform: no link in this generation; pack: no pack linked in this generation
- `fiat-600e-gen1-red`: platform: no link in this generation; pack: no pack linked in this generation
- `ford-capri-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `ford-explorer-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `ford-mustang-mach-e-gen1-premium`: pack: usable 82 kWh fits none of ford-mach-e-75/ford-mach-e-98
- `ford-puma-gen-e-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `genesis-gv60-gen1-advanced`: platform: no link in this generation; pack: no pack linked in this generation
- `genesis-gv60-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `genesis-gv60-gen1-performance`: platform: no link in this generation; pack: no pack linked in this generation
- `hyundai-ioniq-5-facelift-awd`: platform: no link in this generation; pack: no pack linked in this generation
- `hyundai-ioniq-5-facelift-base`: platform: no link in this generation; pack: no pack linked in this generation
- `hyundai-ioniq-5-facelift-n`: platform: no link in this generation; pack: no pack linked in this generation
- `hyundai-ioniq-6-gen1-awd`: pack: usable 72.6 kWh fits none of egmp-53/egmp-77-4
- `hyundai-ioniq-6-gen1-long-range`: pack: usable 72.6 kWh fits none of egmp-53/egmp-77-4
- `hyundai-kona-electric-sx2-long-range`: pack: usable 58 kWh fits none of hk-kona-sx2-48/hk-kona-sx2-65
- `hyundai-kona-electric-sx2-standard-range`: pack: variant has no usable kWh to compare
- `mercedes-cla-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqb-gen1-300-4matic`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqb-gen1-300-4matic-7-seater`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqb-gen1-350-4matic`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqb-gen1-350-4matic-7-seater`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqb-gen1-7-seater`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqb-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `mg-im6-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `mg-s5-gen1-luxury`: platform: no link in this generation; pack: no pack linked in this generation
- `nissan-ariya-gen1-engage`: platform: no link in this generation; pack: no pack linked in this generation
- `nissan-ariya-gen1-engage-87-kwh`: platform: no link in this generation; pack: no pack linked in this generation
- `nissan-ariya-gen1-engage-awd-e-4orce`: platform: no link in this generation; pack: no pack linked in this generation
- `nissan-ariya-gen1-engage-awd-e-4orce-87-kwh`: platform: no link in this generation; pack: no pack linked in this generation
- `nissan-ariya-gen1-nismo`: platform: no link in this generation; pack: no pack linked in this generation
- `nissan-ariya-gen1-nismo-b9`: platform: no link in this generation; pack: no pack linked in this generation
- `polestar-2-gen1-long-range-dual-motor`: pack: usable 75 kWh fits 2 packs cma-78/cma-82
- `polestar-2-gen1-long-range-single-motor`: pack: usable 75 kWh fits 2 packs cma-78/cma-82
- `polestar-2-gen1-performance-pack`: pack: usable 75 kWh fits 2 packs cma-78/cma-82
- `polestar-2-gen1-performance-pack-long-range-dual-motor`: pack: usable 75 kWh fits 2 packs cma-78/cma-82
- `polestar-4-gen1-long-range-dual-motor`: platform: no link in this generation; pack: no pack linked in this generation
- `polestar-4-gen1-long-range-single-motor`: platform: no link in this generation; pack: no pack linked in this generation
- `porsche-macan-electric-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `porsche-macan-electric-gen1-turbo`: platform: no link in this generation; pack: no pack linked in this generation
- `porsche-taycan-gen1-4s`: platform: no link in this generation; pack: no pack linked in this generation
- `porsche-taycan-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `porsche-taycan-gen1-turbo`: platform: no link in this generation; pack: no pack linked in this generation
- `porsche-taycan-gen1-turbo-gt`: platform: no link in this generation; pack: no pack linked in this generation
- `porsche-taycan-gen1-turbo-s`: platform: no link in this generation; pack: no pack linked in this generation
- `renault-4-e-tech-gen1-40-kwh`: platform: no link in this generation; pack: no pack linked in this generation
- `renault-4-e-tech-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `renault-5-e-tech-gen1-110-kw`: pack: no pack linked in this generation
- `renault-5-e-tech-gen1-40-kwh`: pack: no pack linked in this generation
- `renault-5-e-tech-gen1-base`: pack: no pack linked in this generation
- `renault-scenic-e-tech-gen1-60-kwh`: platform: no link in this generation; pack: no pack linked in this generation
- `renault-scenic-e-tech-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `skoda-elroq-gen1-base`: pack: no pack linked in this generation
- `skoda-elroq-gen1-rs`: pack: no pack linked in this generation
- `smart-3-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `toyota-bz4x-gen1-front-wheel-drive`: platform: no link in this generation; pack: no pack linked in this generation
- `toyota-bz4x-gen1-front-wheel-drive-all-wheel-drive`: platform: no link in this generation; pack: no pack linked in this generation
- `volkswagen-id-buzz-gen1-cargo`: pack: no pack linked in this generation
- `volkswagen-id-buzz-gen1-pro`: pack: no pack linked in this generation
- `volkswagen-id5-gen1-gtx`: platform: no link in this generation; pack: no pack linked in this generation
- `volkswagen-id5-gen1-pro`: platform: no link in this generation; pack: no pack linked in this generation
- `volkswagen-id7-gen1-pro`: pack: no pack linked in this generation
- `volkswagen-id7-gen1-tour`: pack: no pack linked in this generation
- `volvo-ec40-c40-base`: platform: no link in this generation; pack: no pack linked in this generation
- `volvo-ec40-c40-twin-motor`: platform: no link in this generation; pack: no pack linked in this generation
- `volvo-ec40-ec40-base`: platform: no link in this generation; pack: no pack linked in this generation
- `volvo-ec40-ec40-twin-motor`: platform: no link in this generation; pack: no pack linked in this generation
- `volvo-ex30-gen1-69-kwh`: platform: no link in this generation; pack: no pack linked in this generation
- `volvo-ex30-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `volvo-ex30-gen1-twin-motor`: platform: no link in this generation; pack: no pack linked in this generation
- `volvo-ex30-gen1-twin-motor-performance`: platform: no link in this generation; pack: no pack linked in this generation
- `xpeng-g6-gen1-awd-performance`: platform: no link in this generation; pack: no pack linked in this generation
- `xpeng-g6-gen1-awd-performance-2025`: platform: no link in this generation; pack: no pack linked in this generation
- `xpeng-g6-gen1-long-range`: platform: no link in this generation; pack: no pack linked in this generation
- `xpeng-g6-gen1-long-range-2025`: platform: no link in this generation; pack: no pack linked in this generation
- `xpeng-g6-gen1-standard-range`: platform: no link in this generation; pack: no pack linked in this generation
- `xpeng-g6-gen1-standard-range-2025`: platform: no link in this generation; pack: no pack linked in this generation
- `xpeng-g6-gen1-ultra-long-range`: platform: no link in this generation; pack: no pack linked in this generation
- `xpeng-g6-gen1-ultra-long-range-2025`: platform: no link in this generation; pack: no pack linked in this generation
- `zeekr-001-gen1-140-kwh-extended-range`: platform: no link in this generation; pack: no pack linked in this generation
- `zeekr-001-gen1-140-kwh-extended-range-2024`: platform: no link in this generation; pack: no pack linked in this generation
- `zeekr-001-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `zeekr-001-gen1-base-2024`: platform: no link in this generation; pack: no pack linked in this generation
- `zeekr-7x-gen1-100-kwh-extended-range`: platform: no link in this generation; pack: no pack linked in this generation
- `zeekr-7x-gen1-all-wheel-drive`: platform: no link in this generation; pack: no pack linked in this generation
- `zeekr-7x-gen1-all-wheel-drive-extended-range-all-wheel-drive-100-kwh`: platform: no link in this generation; pack: no pack linked in this generation
- `zeekr-7x-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `zeekr-x-gen1-all-wheel-drive`: platform: no link in this generation; pack: no pack linked in this generation
- `zeekr-x-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation

## Other sections

- **EPA range** (`epa_range_km`, compared with EPA figures only): 117 variants; 0 with 2+ agreeing sources, of which 0 through fueleconomy.gov.
- **Generation years vs Wikidata** (corroboration only, +/-1 year): 12 generations checked, 10 corroborated; 11 of 13 years agree.
- **Known issues** (RDW APK defects, NL): 62 generations, 185 first-registration-year cohorts (53 marked few reports), 25 defect codes.
- **Charging stats** `bnetza`: 2720 rows in, 2720 rows shipped.
- **Charging stats** `dft-charging`: 141 rows in, 141 rows shipped.
- **Consumption matrix** (Trip fit, all estimates): 237 variants (30 without a WLTP or test figure), cells by rung: measured 860, physics 430, wltp-ratio 2265; 916 tests; 63 KB gzip.
- **Towns + climate** (GeoNames, Meteostat): 10845 towns, 9641 with January climate (30 without P10), 1204 without a station in range.

## Shortlist scores (T-069, editorial)

271 variants x 18 profile combinations. Rule fields present:

| Field | Variants | Share |
|---|---|---|
| ac_kw | 265 | 98% |
| bidi | 0 | 0% |
| boot_l | 133 | 49% |
| charge_100_daily | 200 | 74% |
| cooling_id | 261 | 96% |
| dc_km_per_20min | 231 | 85% |
| fast_on_400v | 164 | 61% |
| heat_pump | 0 | 0% |
| length_mm | 264 | 97% |
| one_pedal | 0 | 0% |
| real_range_km | 239 | 88% |
| real_wh_km | 237 | 87% |
| winter_range_km | 237 | 87% |

| Profile | shortlist | consider | fallback | ruled-out | not-enough-data |
|---|---|---|---|---|---|
| daily-driver | 80 | 100 | 40 | 16 | 35 |
| road-tripper | 28 | 17 | 141 | 48 | 37 |
| runabout | 33 | 201 | 16 | 2 | 19 |

## Used price bands (T-081, estimates)

171 of 271 variants have a band in at least one country.

| Country | Model bands | Sampled bands (variant) | Sampled bands (generation) | Not enough data |
|---|---|---|---|---|
| BE | 335 | 0 | 89 | 431 |
| DE | 383 | 0 | 0 | 472 |
| ES | 358 | 0 | 0 | 497 |
| FR | 358 | 0 | 0 | 497 |
| IT | 369 | 0 | 0 | 486 |
| NL | 235 | 0 | 227 | 393 |
| UK | 3 | 0 | 0 | 852 |

Back-test against manual samples: 76 rows, median absolute error 10%, median error +2% (not a gate).
Hold-out (leave one generation out, as shown to visitors): 76 rows, median absolute error 11%, real median inside the shown P25-P75 51%.
