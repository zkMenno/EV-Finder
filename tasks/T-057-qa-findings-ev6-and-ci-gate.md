# T-057 Qa findings ev6 and ci gate
Role: WS1   Lane: pipeline/ev_pipeline/qa, .github   Wave: proposed by overnight 1
Status: todo

## Goal
Fix the QA finding (Kia EV6 77 kWh AWD usable 80 kWh > pack gross 77.4) and run the release QA in CI on every PR that touches data.

## Acceptance criteria
- [ ] EV6 row fixed via pack link or source review
- [ ] CI job runs `ev release --dry-run` + QA and fails on blocking checks
- [ ] Tests cover it (fixtures, no live network calls)

## Inputs
MORNING.md, data/review/coverage-gaps.md, QUESTIONS.md, audits/.

## Out of scope
Anything not named above.

## Handoff notes

## Review
