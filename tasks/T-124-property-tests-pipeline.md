# T-124 Property tests for the pipeline (Hypothesis)
Role: WS1   Lane: pipeline/tests   Wave: process
Status: todo

## Goal
Generated inputs try to break the rules we think always hold, so edge cases don't depend on the author's imagination.

## Acceptance criteria
- [ ] `hypothesis` as a dev dependency (licence MPL-2.0, fine for tests); a fixed seed profile in CI so runs are not flaky, a longer profile for nightly.
- [ ] Properties, at least:
  - Idempotency: merge/normalise/release run twice on the same staging = same output (byte-equal after sorting)
  - Round-trip: unit conversions (kWh/100 km ↔ Wh/km, km per 20 min ↔ km/h), name normalisation keys stable (incl. '+', accents, case)
  - Invariants on any generated variant: net battery ≤ gross; real range > 0 and ≤ WLTP × 1.1; every published value has source_id, retrieved_at, licence; estimates carry `estimate: true`; score in 0..100 and band matches score
  - Equivalence: optimised lookups (e.g. matcher index) = naive scan on small inputs
- [ ] Each failing example Hypothesis finds becomes a plain regression test too.

## Inputs
Article: property tests (round-trip, invariants, idempotency, equivalence).

## Handoff notes

## Review
