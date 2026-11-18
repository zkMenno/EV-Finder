# Release QA, release 3

Overall: **review** (fail = blocked; review = published, items to check). Details in qa.json.

| Check | Blocking | Status | Summary |
|---|---|---|---|
| Provenance completeness | yes | pass | 9092 values checked; 0 problem(s) |
| Licence gate re-check | yes | pass | 14 sources, 59852 facts; 0 problem(s) |
| Diff vs previous release | no | flag | vs release 2: 271 -> 375 variants, +104 / -0; 2 flag(s) |
| Outliers and impossible values | no | flag | 2 impossible value(s), 72 outside P1-P99 (reference: release 2) |
| Coverage of the top-40 used models | no | info | 40 models; 2+ agreeing sources on every headline field: 0 (0%, target 80% before launch) |
| New sections (T-059) | no | flag | EPA 162 rows (0 with a 2nd EPA source via fueleconomy); years 10/12 generations corroborated; known issues 232 cohorts; charging stats 3759 rows |
| Plausibility gate (A-35 B4) | no | flag | 5 issue(s) withheld from the rows (in conflicts.csv), 35 to review |
| Car photos: licence, credit, stored files (Decision 081) | yes | pass | 119 photo(s) ok |
| Release diff vs previous release (T-123) | yes | pass | vs release 2: 0 blocking, 468 approved, 7245 review |
| Back-test (real range) | no | skipped | no real condition-tagged tests from licence-cleared sources yet (the measured-test sources are still waiting for permission); harness tested on fixtures only |

## Impossible values (first 10)

- hyundai-ioniq-5-facelift-awd: usable 84.0 > gross 77.4 kWh
- hyundai-ioniq-5-facelift-base: usable 84.0 > gross 77.4 kWh

## Plausibility (first 10 each)

- withheld: byd-atto-3-gen1-60kwh: WLTP 510 km / 60.5 kWh = 8.43 km/kWh > 8 (withheld above 8.2 for body suv)
- withheld: hyundai-kona-electric-sx2-long-range: WLTP 484 km / 58 kWh = 8.34 km/kWh > 8 (withheld above 8.2 for body suv)
- withheld: hyundai-kona-electric-sx2-standard-range: WLTP 305 km / 36.5 kWh = 8.36 km/kWh > 8 (withheld above 8.2 for body suv)
- withheld: skoda-enyaq-gen1-85: WLTP 752 km / 77 kWh = 9.77 km/kWh > 8 (withheld above 8.2 for body suv)
- withheld: tesla-model-s-facelift-raven-long-range: dc_km_per_20min 169.3 = 1.49x the generation + pack median 113.7 (3 variants) > 1.3x
- review: bmw-i3-i01-120ah: WLTP 310 km / 37.9 kWh = 8.18 km/kWh > 8
- review: bmw-i3-i01-i3s-94ah: WLTP 245 km / 27.2 kWh = 9.01 km/kWh > 8
- review: citroen-e-c3-gen1-electric-200: WLTP 232 km / 26 kWh = 8.92 km/kWh > 8
- review: citroen-e-c4-c41-54kwh: WLTP 418 km / 50.8 kWh = 8.23 km/kWh > 8
- review: dacia-spring-gen1-essential: WLTP 230 km / 26.8 kWh = 8.58 km/kWh > 8
- review: dacia-spring-gen1-essential-comfort: WLTP 230 km / 26.8 kWh = 8.58 km/kWh > 8
- review: dacia-spring-gen1-essential-extreme: WLTP 230 km / 26.8 kWh = 8.58 km/kWh > 8
- review: fiat-500e-332-24kwh: WLTP 190 km / 21.3 kWh = 8.92 km/kWh > 8
- review: fiat-500e-332-42kwh: WLTP 337 km / 37.3 kWh = 9.03 km/kWh > 8
- review: fiat-500e-332-icon: WLTP 320 km / 37.3 kWh = 8.58 km/kWh > 8

## Diff flags

- boot_l: filled share fell 5.3 points
- towing_kg: filled share fell 6.5 points

## Profile fields (winter range, real range, DC km in 20 min)

Report only. Ratios compare the catalogue figure with the calibrated consumption matrix (1.0 = same). The winter temperature step is unvalidated (needs winter road tests, Q-059).

- **Winter range** (matrix, t1): 331 of 375 variants; 20 °C consumption out of sample: 6.8 % median abs error (n 142); the temperature step is not validated.
- **Real range** (catalogue): 335 variants; vs EPA: 6.99 % median abs error (n 88); vs matrix mild range: median 1.105 (P10 1.017, P90 1.204), 174 of 331 differ by more than 10 %.
- **DC km in 20 min** (catalogue): 323 variants; curves default 268, estimated 53, None 2; its motorway consumption vs the matrix: median 0.955 (P10 0.918, P90 1.039), 44 of 319 differ by more than 10 %. No licence-clean charging test yet.
- **WLTP consumption**: 337 variants; EPA in sample 6.37 % median abs error (n 142), out of sample 6.8 % median abs error (n 142); our estimate (net kWh / WLTP x charging losses) vs official WLTP: 3.0 % median abs error (n 211).

## Release diff 2 -> 3 (T-123)

Status **pass**: 0 blocking, 468 approved, 0 retired, 7245 review. Full list: `data/review/release_diff.csv`.

| file | added | changed | charging | cleared | file_removed | filled | removed | source_lost |
|---|---|---|---|---|---|---|---|---|
| catalogue.json:generations | 138 |  |  |  |  | 2142 |  |  |
| catalogue.json:rows | 104 | 278 |  | 1560 |  | 1617 |  |  |
| charging_stats.json:series |  |  | 65 |  |  |  |  |  |
| consumption_matrix.json:variants | 96 | 163 |  |  |  |  |  |  |
| shortlist_scores.json:variants | 104 | 216 |  |  |  | 11 |  |  |
| towns/de.json:towns | 2 |  |  |  |  |  |  |  |
| used_prices.json:variants | 23 | 1074 |  | 120 |  |  |  |  |

Biggest moves:
- shortlist_scores.json hyundai-ioniq-5-facelift-n factors.road-tripper.winter-range: 0 -> 0.058 (new)
- shortlist_scores.json hyundai-ioniq-5-facelift-base factors.road-tripper.efficiency: 0.102 -> 0.463 (+353.9 %)
- shortlist_scores.json hyundai-ioniq-5-facelift-base factors.road-tripper.winter-range: 0.201 -> 0.907 (+351.2 %)
- shortlist_scores.json hyundai-ioniq-5-facelift-awd factors.road-tripper.winter-range: 0.153 -> 0.544 (+255.6 %)
- shortlist_scores.json nissan-leaf-ze1-62-kwh factors.road-tripper.efficiency: 0.104 -> 0.332 (+219.2 %)
- shortlist_scores.json hyundai-ioniq-5-gen1-73kwh-rwd factors.road-tripper.efficiency: 0.12 -> 0.355 (+195.8 %)
- catalogue.json smart-eq-fortwo-453-eq registrations.BE[new_registrations/2018/eea/generation].count: 75 -> 150 (+100.0 %)
- shortlist_scores.json hyundai-ioniq-5-gen1-73kwh-rwd factors.road-tripper.winter-range: 0.21 -> 0.382 (+81.9 %)
- shortlist_scores.json hyundai-ioniq-5-facelift-base scores.road-tripper+kerbside.rural.score: 40 -> 67.7 (+69.2 %)
- catalogue.json smart-eq-fortwo-453-eq registrations.NL[new_registrations/2019/eea/generation].count: 375 -> 124 (-66.9 %)
