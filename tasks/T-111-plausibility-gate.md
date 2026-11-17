# T-111 Plausibility gate in qa.json; licence gate for marketplace samples
Role: builder   Lane: WS1: pipeline/ev_pipeline/qa/, pipeline/ev_pipeline/derive/used_price.py, data/sources.yaml   Wave: launch fixes (A-35)
Status: todo

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

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-35 B4, S2 fixed. -->
