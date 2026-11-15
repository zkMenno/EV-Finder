# Release QA, release 1

Overall: **review** (fail = blocked; review = published, items to check). Details in qa.json.

| Check | Blocking | Status | Summary |
|---|---|---|---|
| Provenance completeness | yes | pass | 5771 values checked; 0 problem(s) |
| Licence gate re-check | yes | pass | 13 sources, 40114 facts; 0 problem(s) |
| Diff vs previous release | no | skipped | first release: nothing to compare |
| Outliers and impossible values | no | flag | 1 impossible value(s), 33 outside P1-P99 (reference: this release) |
| Coverage of the top-40 used models | no | info | 40 models; 2+ agreeing sources on every headline field: 0 (0%, target 80% before launch) |
| New sections (T-059) | no | flag | EPA 105 rows (0 with a 2nd EPA source via fueleconomy); years 10/12 generations corroborated; known issues 171 cohorts; charging stats 2861 rows |
| Back-test (real range) | no | skipped | no real condition-tagged tests from licence-cleared sources yet (the measured-test sources are still waiting for permission); harness tested on fixtures only |

## Impossible values (first 10)

- volkswagen-e-golf-mk7-24kwh: average 41.8 > peak 40.0 kW
