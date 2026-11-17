# T-124 Property tests for the pipeline (Hypothesis)
Role: WS1   Lane: pipeline/tests   Wave: process
Status: review (WS1, 2026-11-17)

## Goal
Generated inputs try to break the rules we think always hold, so edge cases don't depend on the author's imagination.

## Acceptance criteria
- [x] `hypothesis` as a dev dependency (licence MPL-2.0, fine for tests); a fixed seed profile in CI so runs are not flaky, a longer profile for nightly.
- [x] Properties, at least:
  - Idempotency: merge/normalise/release run twice on the same staging = same output (byte-equal after sorting)
  - Round-trip: unit conversions (kWh/100 km ↔ Wh/km, km per 20 min ↔ km/h), name normalisation keys stable (incl. '+', accents, case)
  - Invariants on any generated variant: net battery ≤ gross; real range > 0 and ≤ WLTP × 1.1; every published value has source_id, retrieved_at, licence; estimates carry `estimate: true`; score in 0..100 and band matches score
  - Equivalence: optimised lookups (e.g. matcher index) = naive scan on small inputs
- [x] Each failing example Hypothesis finds becomes a plain regression test too.

## Inputs
Article: property tests (round-trip, invariants, idempotency, equivalence).

## Handoff notes
2026-11-17 WS1 (session_01JuyZEWFXbkeYSii8dVSWnx).
- `tests/test_t124_properties.py` (19 tests) + `tests/conftest.py` (profiles: `ci` = 200 examples, derandomised, no example database, the default; `nightly` = 5000, via `HYPOTHESIS_PROFILE=nightly`). hypothesis 6.170.15 in both dev lists (MPL-2.0, tests only).
- Properties: name keys (idempotent; case, accents and punctuation ignored; slug matches the schema Id), unit round-trips (Wh/km, miles, km in 20 min vs km/h, battery cap), invariants (net ≤ gross, real range in (0, WLTP × 1.1] on every rung with a source kept, band monotonic in score), equivalence (prefix keys = naive scan, token run = substring search), merge order-independent + picks a real value, idempotent normalise + release (byte-equal), invariants on the committed release's real rows.
- **Found (nightly profile):** the sibling-variant rung scaled by battery only, so a same-pack, lower-WLTP sibling got more real km than its own WLTP × 1.1. Fixed per Decision 045 (WLTP ratio). Pinned as `test_regression_same_pack_sibling_scales_by_wltp_not_battery`. Three older tests changed: two derive tests now give WLTP in step with battery (their subject is sibling choice, not the ratio); the back-test expectation moves from 333.3 to 340.4 km (closer to the synthetic measurement, 340).
- `'+'` property is `xfail(strict=True)`: `key('P7+') == key('P7')` until WS3's T-068 ask is done. Then the marker has to go (strict).
- Not done (gate change, WS0/WS4): a nightly CI job with `HYPOTHESIS_PROFILE=nightly`.

## Review
