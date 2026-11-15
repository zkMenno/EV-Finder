# Release QA, release 1

Overall: **review** (fail = blocked; review = published, items to check). Details in qa.json.

| Check | Blocking | Status | Summary |
|---|---|---|---|
| Provenance completeness | yes | pass | 3957 values checked; 0 problem(s) |
| Licence gate re-check | yes | pass | 9 sources, 7887 facts; 0 problem(s) |
| Diff vs previous release | no | skipped | first release: nothing to compare |
| Outliers and impossible values | no | flag | 1 impossible value(s), 31 outside P1-P99 (reference: this release) |
| Coverage of the top-40 used models | no | info | 40 models; 2+ agreeing sources on every headline field: 0 (0%, target 80% before launch) |
| Back-test (real range) | no | skipped | no real condition-tagged tests from licence-cleared sources yet (the measured-test sources are still waiting for permission); harness tested on fixtures only |

## Impossible values (first 10)

- kia-ev6-gen1-77kwh-awd: usable 80.0 > gross 77.4 kWh
