# T-161 Trim-line version rule (Decision 088), minutes-derived DC marked as a claim, manual terms wording
Role: builder   Lane: pipeline/derive, data/sources.yaml (WS1)   Wave: launch
Status: todo

## Goal
A new entry trim no longer marks higher trims as "older", DC figures derived from a maker's "as little as" minutes are labelled as such, and the sources file matches Decision 087.

## Acceptance criteria
- [ ] **Decision 088:** `version_flags` in `pipeline/ev_pipeline/derive/shortlist.py` compares the same trim line (same model, same drivetrain, power within ±15 %). Back-test (`backtest_rules.py`) at or above today; the R-32 pairs (G6, EV6, IONIQ 5) keep their flags; e-tron GT 2024 S / RS / RS performance lose `older-version`. Approvals for moved scores in their own gate PR, scoped to a release not yet built (G-54).
- [ ] **Minutes-derived DC** (T-155 review should-fix 1): DC fields derived from a cited 10–80 % time carry the same "maker claim" marking that maker figures get today (find how the release marks them). If that needs a schema field, stop and write the exact field in WS0's INBOX; WS0 adds it.
- [ ] **Wording:** `data/sources.yaml` `manual` terms say Decision 087 (any number of single facts per car; never a whole table, range table or price list).
- [ ] Same-data rebuild diff (G-43), `ev verify --base main` in the PR body; tests with fixtures.

## Inputs
Decision 038, 087, 088; WS0 INBOX 2026-11-19 09:15 (ask 2, 3) and 10:38 (ask 1); T-155 Handoff notes.

## Out of scope
Matching (T-159). New seed variants (T-160).

## Handoff notes

## Review
