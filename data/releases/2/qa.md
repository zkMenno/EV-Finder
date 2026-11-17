# Release QA, release 2

Overall: **review** (fail = blocked; review = published, items to check). Details in qa.json.

| Check | Blocking | Status | Summary |
|---|---|---|---|
| Provenance completeness | yes | pass | 6642 values checked; 0 problem(s) |
| Licence gate re-check | yes | pass | 14 sources, 44689 facts; 0 problem(s) |
| Diff vs previous release | no | flag | vs release 1: 226 -> 271 variants, +48 / -3; 2 flag(s) |
| Outliers and impossible values | no | flag | 0 impossible value(s), 45 outside P1-P99 (reference: release 1) |
| Coverage of the top-40 used models | no | info | 40 models; 2+ agreeing sources on every headline field: 0 (0%, target 80% before launch) |
| New sections (T-059) | no | flag | EPA 117 rows (0 with a 2nd EPA source via fueleconomy); years 10/12 generations corroborated; known issues 185 cohorts; charging stats 2861 rows |
| Plausibility gate (A-35 B4) | no | flag | 5 issue(s) withheld from the rows (in conflicts.csv), 33 to review |
| Release diff vs previous release (T-123) | yes | pass | vs release 1: 0 blocking, 249 approved, 3938 review |
| Back-test (real range) | no | skipped | no real condition-tagged tests from licence-cleared sources yet (the measured-test sources are still waiting for permission); harness tested on fixtures only |

## Plausibility (first 10 each)

- withheld: byd-atto-3-gen1-60kwh: WLTP 510 km / 60.5 kWh = 8.43 km/kWh > 8 (withheld above 8.2 for body suv)
- withheld: hyundai-kona-electric-sx2-long-range: WLTP 484 km / 58 kWh = 8.34 km/kWh > 8 (withheld above 8.2 for body suv)
- withheld: hyundai-kona-electric-sx2-standard-range: WLTP 305 km / 36.5 kWh = 8.36 km/kWh > 8 (withheld above 8.2 for body suv)
- withheld: skoda-enyaq-gen1-85: WLTP 752 km / 77 kWh = 9.77 km/kWh > 8 (withheld above 8.2 for body suv)
- withheld: tesla-model-s-facelift-raven-long-range: dc_km_per_20min 169.3 = 1.49x the generation + pack median 113.7 (3 variants) > 1.3x
- review: bmw-i3-i01-120ah: WLTP 310 km / 37.9 kWh = 8.18 km/kWh > 8
- review: bmw-i3-i01-i3s-94ah: WLTP 245 km / 27.2 kWh = 9.01 km/kWh > 8
- review: citroen-e-c4-c41-54kwh: WLTP 418 km / 50.8 kWh = 8.23 km/kWh > 8
- review: dacia-spring-gen1-essential: WLTP 230 km / 26.8 kWh = 8.58 km/kWh > 8
- review: dacia-spring-gen1-essential-comfort: WLTP 230 km / 26.8 kWh = 8.58 km/kWh > 8
- review: dacia-spring-gen1-essential-extreme: WLTP 230 km / 26.8 kWh = 8.58 km/kWh > 8
- review: fiat-500e-332-24kwh: WLTP 190 km / 21.3 kWh = 8.92 km/kWh > 8
- review: fiat-500e-332-42kwh: WLTP 337 km / 37.3 kWh = 9.03 km/kWh > 8
- review: fiat-500e-332-icon: WLTP 320 km / 37.3 kWh = 8.58 km/kWh > 8
- review: fiat-500e-332-la-prima: WLTP 320 km / 37.3 kWh = 8.58 km/kWh > 8

## Diff flags

- towing_kg: filled share fell 5.1 points
- dc_km_per_20min: 54 variants changed beyond tolerance (> 20)

## Profile fields (winter range, real range, DC km in 20 min)

Report only. Ratios compare the catalogue figure with the calibrated consumption matrix (1.0 = same). The winter temperature step is unvalidated (needs winter road tests, Q-059).

- **Winter range** (matrix, t1): 237 of 271 variants; 20 °C consumption out of sample: 7.22 % median abs error (n 104); the temperature step is not validated.
- **Real range** (catalogue): 239 variants; vs EPA: 7.32 % median abs error (n 68); vs matrix mild range: median 1.101 (P10 1.011, P90 1.198), 122 of 237 differ by more than 10 %.
- **DC km in 20 min** (catalogue): 231 variants; curves default 180, estimated 50, None 1; its motorway consumption vs the matrix: median 0.955 (P10 0.915, P90 1.037), 31 of 227 differ by more than 10 %. No licence-clean charging test yet.
- **WLTP consumption**: 241 variants; EPA in sample 6.47 % median abs error (n 104), out of sample 7.22 % median abs error (n 104); our estimate (net kWh / WLTP x charging losses) vs official WLTP: 2.9 % median abs error (n 152).

## Release diff 1 -> 2 (T-123)

Status **pass**: 0 blocking, 249 approved, 3 retired, 3938 review. Full list: `data/review/release_diff.csv`.

| file | added | changed | charging | cleared | file_removed | filled | removed | source_lost |
|---|---|---|---|---|---|---|---|---|
| catalogue.json:generations | 41 |  |  | 4 |  | 2 |  |  |
| catalogue.json:rows | 48 | 522 |  | 1868 |  | 1702 | 3 |  |

Biggest moves:
- catalogue.json tesla-model-y-gen1-long-range consumption_motorway_kwh_100km: 14.3 -> 22 (+53.8 %)
- catalogue.json tesla-model-y-gen1-long-range consumption_kwh_100km: 11 -> 16.9 (+53.6 %)
- catalogue.json kia-ev6-gen1-gt consumption_kwh_100km: 16.9 -> 24.2 (+43.2 %)
- catalogue.json kia-ev6-gen1-gt consumption_motorway_kwh_100km: 22 -> 31.4 (+42.7 %)
- catalogue.json kia-ev6-gen1-58kwh-rwd registered_count_nl: 12330 -> 7950 (-35.5 %)
- catalogue.json kia-ev6-gen1-77kwh-awd registered_count_nl: 12330 -> 7950 (-35.5 %)
- catalogue.json kia-ev6-gen1-77kwh-rwd registered_count_nl: 12330 -> 7950 (-35.5 %)
- catalogue.json kia-ev6-gen1-gt registered_count_nl: 12330 -> 7950 (-35.5 %)
- catalogue.json tesla-model-y-gen1-long-range dc_km_per_20min: 387.2 -> 251.7 (-35.0 %)
- catalogue.json tesla-model-y-gen1-long-range dc_km_per_10min: 196.7 -> 127.9 (-35.0 %)
