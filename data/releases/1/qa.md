# Release QA, release 1

Overall: **review** (fail = blocked; review = published, items to check). Details in qa.json.

| Check | Blocking | Status | Summary |
|---|---|---|---|
| Provenance completeness | yes | pass | 4193 values checked; 0 problem(s) |
| Licence gate re-check | yes | pass | 12 sources, 8846 facts; 0 problem(s) |
| Diff vs previous release | no | skipped | first release: nothing to compare |
| Outliers and impossible values | no | flag | 2 impossible value(s), 31 outside P1-P99 (reference: this release) |
| Coverage of the top-40 used models | no | info | 40 models; 2+ agreeing sources on every headline field: 0 (0%, target 80% before launch) |
| New sections (T-059) | no | flag | EPA 84 rows (12 with a 2nd EPA source via fueleconomy); years 6/8 generations corroborated; known issues 152 cohorts; charging stats 2861 rows |
| Back-test (real range) | no | skipped | no real condition-tagged tests from licence-cleared sources yet (the measured-test sources are still waiting for permission); harness tested on fixtures only |

## Impossible values (first 10)

- audi-q4-e-tron-gen1-40-sportback: 10.6 km/kWh > 10
- kia-ev6-gen1-77kwh-awd: usable 80.0 > gross 77.4 kWh
