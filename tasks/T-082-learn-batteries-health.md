# T-082 /learn "Batteries and used battery health"
Role: WS3   Lane: content/learn   Wave: 10
Status: merged (PR #35); fresh review via QA A-35; earlier note: WS3, 2026-11-15

## Goal
The third launch /learn page: chemistries in plain words, how batteries age, what to check on a used EV.

## Acceptance criteria
- [ ] Six languages (EN + NL reviewed), every claim linked to its source (Battery & voltage guide tab, R-21, Aviloo/Recurrent public reports)
- [ ] Covers NMC vs LFP care, air-cooled packs, what battery health means, Belgium Car-Pass battery test, warranty left
- [ ] Glossary tooltips; linked from variant pages and the hero result cards

## Inputs
docs/spec/battery-and-voltage-guide.md, Decision 051.

## Out of scope
Battery test referrals (after launch).

## Handoff notes
2026-11-15, WS3 (https://claude.ai/code/session_01JuyZEW2aV2H7ifmpaT5Pfr), branch t-082-learn-batteries.
- New page content/learn/batteries-health: EN + NL by WS3, DE/FR/ES/IT drafted by translation subagents (review: needed). Sources: Geotab 2025, Aviloo 2026 report (labelled as a seller of tests), Recurrent 2024, ADAC ID.3 160,000 km test, VW warranty page, Car-Pass. Covers NMC vs LFP care, air-cooled packs, SoH, Car-Pass, warranty left, used-car checklist. Linking from variant pages and hero cards is WS2 (glossary id `soh` and article slug `batteries-health`).
- EN + NL still need Menno's read before `review: done`.

## Review
- Reviewed by QA, 2026-11-17 (main @ d086d49, REVIEW.md draft R0–R3 + triggered D items): changes needed — all /learn guides incl. EN/NL show "Draft: review needed"; 3 extra guides are beyond launch scope (A-35 S5).
