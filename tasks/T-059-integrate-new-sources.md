# T-059 Integrate new sources
Role: WS1   Lane: pipeline/ev_pipeline/{match,merge,release}   Wave: proposed by overnight 1
Status: todo

## Goal
Integrate the overnight sources that only reach staging so far: RDW defects (Known issues), fueleconomy.gov (agreement counts on shared models), charging stats (EAFO, BNetzA, DfT) into catalogue / charging_stats, Wikidata corroboration of generation years.

## Acceptance criteria
- [ ] Each source has a release path with provenance and the licence gate
- [ ] coverage.md and qa.json show the change
- [ ] Tests cover it (fixtures, no live network calls)

## Inputs
MORNING.md, data/review/coverage-gaps.md, QUESTIONS.md, audits/.

## Out of scope
Anything not named above.

## Handoff notes

## Review
