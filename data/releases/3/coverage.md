# Coverage, release 3

375 variants. Share of variants per field (count in brackets). 'estimate only' = our model or ratio, no source; derived values count by their weakest input.

| Field | 2+ agreeing sources | 1 source | estimate only | missing |
|---|---|---|---|---|
| battery_kwh_net | 21% (77) | 77% (288) | 2% (6) | 1% (4) |
| wltp_range_km | 28% (104) | 54% (202) | 0% (0) | 18% (69) |
| epa_range_km | 0% (0) | 43% (162) | 0% (0) | 57% (213) |
| consumption_kwh_100km | 2% (9) | 55% (208) | 32% (120) | 10% (38) |
| ac_kw | 29% (110) | 69% (257) | 0% (0) | 2% (8) |
| ac_kw_optional | 0% (0) | 0% (0) | 0% (0) | 100% (375) |
| dc_peak_kw | 22% (84) | 70% (263) | 0% (0) | 7% (28) |
| dc_avg_10_80_kw | 0% (0) | 1% (4) | 93% (349) | 6% (22) |
| ac_km_per_h | 2% (8) | 55% (207) | 32% (119) | 11% (41) |
| dc_km_per_10min | 0% (0) | 0% (0) | 86% (323) | 14% (52) |
| real_range_km | 0% (0) | 0% (0) | 89% (335) | 11% (40) |
| real_range_winter_km | 0% (0) | 0% (0) | 88% (331) | 12% (44) |
| power_kw | 0% (0) | 93% (347) | 0% (0) | 7% (28) |
| accel_0_100_s | 0% (0) | 71% (266) | 0% (0) | 29% (109) |
| boot_l | 0% (0) | 44% (164) | 0% (0) | 56% (211) |
| length_mm | 22% (84) | 72% (270) | 0% (0) | 6% (21) |
| weight_kg | 2% (6) | 66% (246) | 0% (0) | 33% (123) |
| towing_kg | 0% (0) | 19% (71) | 0% (0) | 81% (304) |
| seats | 33% (122) | 67% (252) | 0% (0) | 0% (1) |
| registered_count_nl | 0% (0) | 96% (361) | 0% (0) | 4% (14) |
| dc_minutes_10_80 | 0% (0) | 2% (6) | 93% (347) | 6% (22) |
| dc_km_per_20min | 0% (0) | 0% (0) | 86% (323) | 14% (52) |
| dc_peak_held_min | 0% (0) | 0% (0) | 93% (347) | 7% (28) |
| consumption_motorway_kwh_100km | 0% (0) | 0% (0) | 90% (337) | 10% (38) |
| voltage_nominal_v | 0% (0) | 15% (57) | 0% (0) | 85% (318) |
| voltage_max_v | 0% (0) | 0% (0) | 0% (0) | 100% (375) |
| charger_400v_kw | 0% (0) | 3% (13) | 0% (0) | 97% (362) |

## Battery pack and platform links

Per row: linked in data/seed/variant_links.yaml, linked by rule (same generation; for packs, usable kWh fits exactly one of the generation's packs), or missing.

| Link | variant_links.yaml | rule | missing |
|---|---|---|---|
| battery_pack_id | 35% (132) | 11% (41) | 54% (202) |
| platform_id | 42% (158) | 10% (38) | 48% (179) |

Rows missing a link (202):

- `audi-a6-e-tron-gen1-avant`: platform: no link in this generation; pack: no pack linked in this generation
- `audi-a6-e-tron-gen1-sportback`: platform: no link in this generation; pack: no pack linked in this generation
- `audi-e-tron-gt-gen1-quattro`: platform: no link in this generation; pack: no pack linked in this generation
- `audi-e-tron-gt-gen1-rs`: platform: no link in this generation; pack: no pack linked in this generation
- `audi-q6-e-tron-gen1-quattro`: platform: no link in this generation; pack: no pack linked in this generation
- `audi-q6-e-tron-gen1-quattro-sportback`: platform: no link in this generation; pack: no pack linked in this generation
- `audi-q6-e-tron-gen1-sq6`: platform: no link in this generation; pack: no pack linked in this generation
- `bmw-i5-gen1-edrive40`: platform: no link in this generation; pack: no pack linked in this generation
- `bmw-i5-gen1-m60`: platform: no link in this generation; pack: no pack linked in this generation
- `bmw-i7-g70-m70`: platform: no link in this generation; pack: no pack linked in this generation
- `bmw-i7-g70-xdrive60`: platform: no link in this generation; pack: no pack linked in this generation
- `bmw-ix-gen1-m60`: platform: no link in this generation; pack: no pack linked in this generation
- `bmw-ix-gen1-xdrive40`: platform: no link in this generation; pack: no pack linked in this generation
- `bmw-ix-gen1-xdrive50`: platform: no link in this generation; pack: no pack linked in this generation
- `bmw-ix1-gen1-xdrive30`: platform: no link in this generation; pack: no pack linked in this generation
- `bmw-ix2-gen1-xdrive30`: platform: no link in this generation; pack: no pack linked in this generation
- `bmw-ix3-gen1-ix3`: platform: no link in this generation; pack: no pack linked in this generation
- `byd-atto-3-gen1-standard-range`: pack: usable 49 kWh fits none of byd-blade-60
- `byd-atto-3-gen1-standard-range-2025`: pack: usable 49.92 kWh fits none of byd-blade-60
- `byd-dolphin-gen1-boost`: platform: no link in this generation; pack: no pack linked in this generation
- `byd-dolphin-gen1-comfort-extended-range`: platform: no link in this generation; pack: no pack linked in this generation
- `byd-dolphin-gen1-premium-extended-range`: platform: no link in this generation; pack: no pack linked in this generation
- `byd-dolphin-gen1-standard`: platform: no link in this generation; pack: no pack linked in this generation
- `byd-han-gen1-flagship`: platform: no link in this generation; pack: no pack linked in this generation
- `byd-seal-gen1-dynamic`: platform: no link in this generation; pack: no pack linked in this generation
- `byd-seal-gen1-performance`: platform: no link in this generation; pack: no pack linked in this generation
- `byd-seal-gen1-premium`: platform: no link in this generation; pack: no pack linked in this generation
- `byd-seal-gen1-standard`: platform: no link in this generation; pack: no pack linked in this generation
- `byd-seal-gen1-standard-performance`: platform: no link in this generation; pack: no pack linked in this generation
- `byd-tang-gen1-flagship`: platform: no link in this generation; pack: no pack linked in this generation
- `cadillac-lyriq-gen1-all-wheel-drive`: platform: no link in this generation; pack: no pack linked in this generation
- `cadillac-lyriq-gen1-rear-wheel-drive`: platform: no link in this generation; pack: no pack linked in this generation
- `citroen-e-berlingo-gen3-base`: platform: no link in this generation; pack: no pack linked in this generation
- `citroen-e-c3-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `citroen-e-c3-gen1-electric-200`: platform: no link in this generation; pack: no pack linked in this generation
- `citroen-e-spacetourer-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `cupra-tavascan-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `cupra-tavascan-gen1-vz`: platform: no link in this generation; pack: no pack linked in this generation
- `ds-3-e-tense-facelift-base`: platform: no link in this generation; pack: no pack linked in this generation
- `fiat-600e-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `fiat-600e-gen1-la-prima`: platform: no link in this generation; pack: no pack linked in this generation
- `fiat-600e-gen1-red`: platform: no link in this generation; pack: no pack linked in this generation
- `ford-capri-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `ford-e-tourneo-courier-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `ford-explorer-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `ford-mustang-mach-e-gen1-premium`: pack: usable 82 kWh fits none of ford-mach-e-75/ford-mach-e-98
- `ford-puma-gen-e-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `genesis-gv60-gen1-advanced`: platform: no link in this generation; pack: no pack linked in this generation
- `genesis-gv60-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `genesis-gv60-gen1-performance`: platform: no link in this generation; pack: no pack linked in this generation
- `gwm-ora-03-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `hongqi-e-hs9-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `hyundai-ioniq-5-facelift-awd`: pack: usable 84 kWh fits none of egmp-63
- `hyundai-ioniq-5-facelift-base`: pack: usable 84 kWh fits none of egmp-63
- `hyundai-ioniq-5-facelift-n`: pack: usable 84 kWh fits none of egmp-63
- `hyundai-ioniq-6-gen1-awd`: pack: usable 72.6 kWh fits none of egmp-53/egmp-77-4
- `hyundai-ioniq-6-gen1-long-range`: pack: usable 72.6 kWh fits none of egmp-53/egmp-77-4
- `hyundai-ioniq-9-gen1-long-range-awd`: platform: no link in this generation; pack: no pack linked in this generation
- `hyundai-kona-electric-sx2-long-range`: pack: usable 58 kWh fits none of hk-kona-sx2-48/hk-kona-sx2-65
- `hyundai-kona-electric-sx2-standard-range`: pack: variant has no usable kWh to compare
- `leapmotor-b10-gen1-160-kw`: platform: no link in this generation; pack: no pack linked in this generation
- `leapmotor-b10-gen1-56-2-kwh`: platform: no link in this generation; pack: no pack linked in this generation
- `leapmotor-b10-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `leapmotor-c10-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `lexus-rz-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `lexus-rz-gen1-luxury`: platform: no link in this generation; pack: no pack linked in this generation
- `lexus-rz-gen1-premium`: platform: no link in this generation; pack: no pack linked in this generation
- `lexus-ux-300e-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `lotus-eletre-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `lotus-eletre-gen1-r`: platform: no link in this generation; pack: no pack linked in this generation
- `lotus-eletre-gen1-s`: platform: no link in this generation; pack: no pack linked in this generation
- `lotus-emeya-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `lucid-air-gen1-pure`: platform: no link in this generation; pack: no pack linked in this generation
- `lucid-air-gen1-pure-grand-touring`: platform: no link in this generation; pack: no pack linked in this generation
- `lucid-air-gen1-pure-sapphire`: platform: no link in this generation; pack: no pack linked in this generation
- `lucid-air-gen1-pure-touring`: platform: no link in this generation; pack: no pack linked in this generation
- `lucid-gravity-gen1-grand-touring`: platform: no link in this generation; pack: no pack linked in this generation
- `lucid-gravity-gen1-touring`: platform: no link in this generation; pack: no pack linked in this generation
- `maserati-grecale-folgore-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-cla-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqb-gen1-300-4matic`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqb-gen1-300-4matic-7-seater`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqb-gen1-350-4matic`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqb-gen1-350-4matic-7-seater`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqb-gen1-7-seater`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqb-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqe-gen1-350`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqe-gen1-500-4matic`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqe-gen1-53-amg`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqe-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqe-suv-gen1-500-4matic`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqe-suv-gen1-53-amg`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqe-suv-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqs-gen1-53-amg`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqs-gen1-580-4matic`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqs-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqs-suv-gen1-53-amg`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqs-suv-gen1-580-4matic`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqs-suv-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqv-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-eqv-gen1-long-range`: platform: no link in this generation; pack: no pack linked in this generation
- `mercedes-g-580-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `mg-cyberster-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `mg-im6-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `mg-s5-gen1-luxury`: platform: no link in this generation; pack: no pack linked in this generation
- `nio-es8-gen1-100-kwh`: platform: no link in this generation; pack: no pack linked in this generation
- `nio-es8-gen1-150-kwh`: platform: no link in this generation; pack: no pack linked in this generation
- `nio-es8-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `nio-et5-gen1-100-kwh`: platform: no link in this generation; pack: no pack linked in this generation
- `nio-et5-gen1-150-kwh`: platform: no link in this generation; pack: no pack linked in this generation
- `nio-et5-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `nio-et7-gen1-100-kwh`: platform: no link in this generation; pack: no pack linked in this generation
- `nio-et7-gen1-150-kwh`: platform: no link in this generation; pack: no pack linked in this generation
- `nio-et7-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `nissan-ariya-gen1-engage`: platform: no link in this generation; pack: no pack linked in this generation
- `nissan-ariya-gen1-engage-87-kwh`: platform: no link in this generation; pack: no pack linked in this generation
- `nissan-ariya-gen1-engage-awd-e-4orce`: platform: no link in this generation; pack: no pack linked in this generation
- `nissan-ariya-gen1-engage-awd-e-4orce-87-kwh`: platform: no link in this generation; pack: no pack linked in this generation
- `nissan-ariya-gen1-nismo`: platform: no link in this generation; pack: no pack linked in this generation
- `nissan-ariya-gen1-nismo-b9`: platform: no link in this generation; pack: no pack linked in this generation
- `nissan-micra-ev-gen6-52-kwh`: platform: no link in this generation; pack: no pack linked in this generation
- `nissan-micra-ev-gen6-base`: platform: no link in this generation; pack: no pack linked in this generation
- `peugeot-e-3008-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `peugeot-e-3008-gen1-dual-motor`: platform: no link in this generation; pack: no pack linked in this generation
- `peugeot-e-3008-gen1-long-range`: platform: no link in this generation; pack: no pack linked in this generation
- `peugeot-e-408-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `peugeot-e-5008-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `peugeot-e-5008-gen1-dual-motor`: platform: no link in this generation; pack: no pack linked in this generation
- `peugeot-e-5008-gen1-long-range`: platform: no link in this generation; pack: no pack linked in this generation
- `polestar-2-gen1-long-range-dual-motor`: pack: usable 75 kWh fits 2 packs cma-78/cma-82
- `polestar-2-gen1-long-range-single-motor`: pack: usable 75 kWh fits 2 packs cma-78/cma-82
- `polestar-2-gen1-performance-pack`: pack: usable 75 kWh fits 2 packs cma-78/cma-82
- `polestar-2-gen1-performance-pack-long-range-dual-motor`: pack: usable 75 kWh fits 2 packs cma-78/cma-82
- `polestar-3-gen1-long-range-dual-motor`: platform: no link in this generation; pack: no pack linked in this generation
- `polestar-3-gen1-long-range-dual-motor-performance-pack`: platform: no link in this generation; pack: no pack linked in this generation
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
- `renault-kangoo-e-tech-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `renault-scenic-e-tech-gen1-60-kwh`: platform: no link in this generation; pack: no pack linked in this generation
- `renault-scenic-e-tech-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `rolls-royce-spectre-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `rolls-royce-spectre-gen1-black-badge`: platform: no link in this generation; pack: no pack linked in this generation
- `skoda-elroq-gen1-base`: pack: no pack linked in this generation
- `skoda-elroq-gen1-rs`: pack: no pack linked in this generation
- `smart-1-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `smart-3-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `tesla-model-x-palladium-long-range`: platform: no link in this generation; pack: no pack linked in this generation
- `tesla-model-x-palladium-plaid`: platform: no link in this generation; pack: no pack linked in this generation
- `toyota-bz4x-gen1-front-wheel-drive`: platform: no link in this generation; pack: no pack linked in this generation
- `toyota-bz4x-gen1-front-wheel-drive-all-wheel-drive`: platform: no link in this generation; pack: no pack linked in this generation
- `vinfast-vf6-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `vinfast-vf6-gen1-eco`: platform: no link in this generation; pack: no pack linked in this generation
- `vinfast-vf6-gen1-plus`: platform: no link in this generation; pack: no pack linked in this generation
- `vinfast-vf8-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `vinfast-vf8-gen1-eco-awd`: platform: no link in this generation; pack: no pack linked in this generation
- `vinfast-vf8-gen1-plus-awd`: platform: no link in this generation; pack: no pack linked in this generation
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
- `volvo-ex90-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
- `voyah-free-gen1-base`: platform: no link in this generation; pack: no pack linked in this generation
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

- **EPA range** (`epa_range_km`, compared with EPA figures only): 162 variants; 0 with 2+ agreeing sources, of which 0 through fueleconomy.gov.
- **Generation years vs Wikidata** (corroboration only, +/-1 year): 12 generations checked, 10 corroborated; 11 of 13 years agree.
- **Known issues** (RDW APK defects, NL): 84 generations, 232 first-registration-year cohorts (75 marked few reports), 26 defect codes.
- **Charging stats** `bnetza`: 2720 rows in, 2720 rows shipped.
- **Charging stats** `dft-charging`: 141 rows in, 141 rows shipped.
- **Charging stats** `eafo`: 898 rows in, 898 rows shipped.
- **Consumption matrix** (Trip fit, all estimates): 333 variants (38 without a WLTP or test figure), cells by rung: measured 1090, physics 545, wltp-ratio 3360; 1262 tests; 86 KB gzip.
- **Towns + climate** (GeoNames, Meteostat): 10847 towns, 9643 with January climate (30 without P10), 1204 without a station in range.
- **Charging stats to review**: 102 figures (step over 15 %, fall, revision or gone since the last release) in `data/review/charging_changes.csv`.

## Shortlist scores (T-069, editorial)

375 variants x 18 profile combinations. Rule fields present:

| Field | Variants | Share |
|---|---|---|
| ac_kw | 367 | 98% |
| bidi | 0 | 0% |
| boot_l | 164 | 44% |
| charge_100_daily | 259 | 69% |
| cooling_id | 361 | 96% |
| dc_km_per_20min | 323 | 86% |
| fast_on_400v | 172 | 46% |
| heat_pump | 0 | 0% |
| length_mm | 354 | 94% |
| one_pedal | 0 | 0% |
| real_range_km | 335 | 89% |
| real_wh_km | 333 | 89% |
| winter_range_km | 331 | 88% |

| Profile | shortlist | consider | fallback | ruled-out | not-enough-data |
|---|---|---|---|---|---|
| daily-driver | 129 | 130 | 54 | 17 | 45 |
| road-tripper | 43 | 26 | 197 | 60 | 49 |
| runabout | 48 | 277 | 19 | 2 | 29 |

## Used price bands (T-081, estimates)

194 of 375 variants have a band in at least one country.

| Country | Model bands | Sampled bands (variant) | Sampled bands (generation) | Not enough data |
|---|---|---|---|---|
| BE | 376 | 0 | 89 | 628 |
| DE | 426 | 0 | 0 | 667 |
| ES | 399 | 0 | 0 | 694 |
| FR | 399 | 0 | 0 | 694 |
| IT | 410 | 0 | 0 | 683 |
| NL | 276 | 0 | 227 | 590 |
| UK | 3 | 0 | 0 | 1090 |

Back-test against manual samples: 76 rows, median absolute error 10%, median error +2% (not a gate).
Hold-out (leave one generation out, as shown to visitors): 76 rows, median absolute error 11%, real median inside the shown P25-P75 51%.
