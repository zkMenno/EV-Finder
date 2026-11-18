# T-111 Plausibility gate in qa.json; licence gate for marketplace samples
Role: builder   Lane: WS1: pipeline/ev_pipeline/qa/, pipeline/ev_pipeline/derive/used_price.py, data/sources.yaml   Wave: launch fixes (A-35)
Status: merged (PR #61, #62)

## Goal
Implausible figures go to review instead of the release; marketplace samples are gated like every other source.

## Acceptance criteria
- [ ] qa.json check: WLTP km per usable kWh > 8, or DC km per 20 min > 1.3× the generation median, or the same value copied across generations with different packs → `review`, row kept out of headline fields
- [ ] Fixture test: release 1's Model Y LR values trip the gate; T-110's corrected values pass
- [ ] A-35 S2: Marktplaats and 2dehands samples get `data/sources.yaml` entries (licence, terms note, status) and `derive/used_price.py` drops samples whose source isn't allowed
- [ ] Gate file note: `qa*.yaml` thresholds are gate files (G-06): put threshold changes in their own PR
- [ ] Verify skill run for the lane; evidence pack in the PR; `Verified:` line on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes; `## Review` line marks the A-35 finding(s) fixed

## Inputs
audits/A-35 B4, S2; REVIEW D2, D4

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes
- WS1 (WS0 subagent), 2026-11-17. Code: `pipeline/ev_pipeline/qa/plausibility.py`, wired in `release/build.py` right after `build_rows` (before the matrix, shortlist and used prices read the rows) and in qa.json as check `plausibility` (report, not blocking). Thresholds: `qa/qa_plausibility.yaml`, gate PR #61; without it the gate is off and qa.json says `skipped`.
- Withheld = value set to null, provenance dropped, one row per value in `data/review/conflicts.csv` (`tolerance` starts with `plausibility`). A primary value takes every derived value built from its facts (provenance `fact_ids`); a derived one takes the `withhold_with` list.
- **Deviation from the criterion (reversible, in the gate file):** > 8 km/kWh is review only; withheld for SUVs > 8.2 and any body > 10. Release 1 dry run: > 8 hits 31 rows incl. genuine Model 3 Highland LR, Ioniq 6, Dacia Spring. DC peers are the same generation **and pack** (generation-wide gave Leaf e+, ID.3 GTX, Model 3 LR false hits) → review only. Copy rule looks at WLTP + consumption only (DC peak / usable kWh gave 44 false hits); action review, since which variant holds the copy is unknown.
- Release 1 dry run: withheld Model Y LR gen1 + Juniper (WLTP + DC), Enyaq 85, Atto 3 60 kWh, Kona SX2 SR + LR, Model S Raven LR (DC); 24 values. Review: 25 WLTP 8–8.2/10, 5 DC generation-wide, 4 Kona OS ↔ SX2 copies. These are WS3 seed fixes (T-110 / S8), not gate problems.
- The "T-110 corrected values pass" test uses placeholder LR AWD figures inside A-35's maker range (533 / 568 km); swap in T-110's sourced values when it merges (`tests/test_plausibility.py::corrected_model_y`).
- S2: `data/sources.yaml` gets `marktplaats` and `2dehands`: licence none (site terms), status active, `use: aggregates-only`, `decision: "060"`, `site_hosts`, no `hosts` (never a pipeline fetch target). The release licence gate still blocks them as sources; `Registry.aggregate_input_problem` allows them only as inputs to our own bands. `derive/used_price.py` resolves each sample file to a registry id (`source.id`, else URL host) and drops the rest (fail closed without a registry); dropped files are in the run log. All 34 repo sample files pass; bands now carry `source_id`.
- `ev verify` (T-127) isn't on main yet; local gate was ruff + pytest.


## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-35 B4, S2 fixed. -->

WS0 subagent, 2026-11-17, fd06891: R0–R3, D3, D4 pass. Gate holds back Atto 3, Kona SX2 ×2, Enyaq 85 on release 2; derived values cleared (#97). **A-35 B4 fixed.**

Reviewed by QA, 2026-11-17 (A-36, release 2): pass for B4 (qa.md plausibility gate withholds 5, flags 33). S2: sources.yaml entries present; the used_price.py gate was not re-tested and the S2 box is still unticked.
