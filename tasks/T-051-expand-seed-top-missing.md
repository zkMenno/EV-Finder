# T-051 Expand seed top missing
Role: WS3 + WS1   Lane: data/seed   Wave: proposed by overnight 1
Status: todo

## Goal
Add the biggest BEV models missing from the seed (VW ID.7, Skoda Elroq, BMW iX1, Kia EV3, Volvo EX30, Audi Q6 e-tron, Ford Explorer and the rest of the top-20 in data/review/coverage-gaps.md / data/seed/top40.yaml).

## Acceptance criteria
- [ ] Each new model has generations with years from registration evidence (RDW/KBA/EEA) and Wikidata corroboration, `uncertain` flags where needed
- [ ] No specs from memory: variants come from OpenEV/KilowattApp/RDW/ADEME records
- [ ] Release coverage of NL/UK fleet and DE new registrations reported before/after
- [ ] Tests cover it (fixtures, no live network calls)

## Inputs
MORNING.md, data/review/coverage-gaps.md, QUESTIONS.md, audits/.

## Out of scope
Anything not named above.

## Handoff notes

## Review
