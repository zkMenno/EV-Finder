# T-123 Release diff test (release N vs N-1) with approved changes
Role: WS1   Lane: pipeline/ev_pipeline/release, pipeline/tests   Wave: process
Status: todo

## Goal
No data release ships a change nobody intended: every value that changed between releases is either on an approved list or blocks QA.

## Acceptance criteria
- [ ] `ev release diff --from N-1 --to N` compares catalogue, scores, used prices, consumption matrix and towns per id and field; ignores noise (key order, float rounding at a set precision, generated_at).
- [ ] Output `data/review/release_diff.csv` + a short summary in qa.json: added / removed / changed per file and field, biggest moves.
- [ ] `config/approved_changes.yaml`: entries by id/field/pattern with a reason and the PR or Decision that approved them; approved changes don't block.
- [ ] Unapproved removals of ids, field changes beyond a threshold per field (in config), and any number losing its source → blocking QA.
- [ ] Runs in the data-refresh workflow and in CI's data-qa job when data/pipeline/config changed; the "Data release N" PR body gets the summary.
- [ ] Tests with two tiny fixture releases (one approved change, one unapproved, one removal).
- [ ] Extend the charging release diff (Decision 040 item 4) into the same mechanism, still review-only for charging.

## Inputs
Article: differential tests (old vs new on the same inputs, normalise irrelevant differences, keep a list of approved changes). Handoff gap #9 "release diff checks". A-20 B1.

## Handoff notes

## Review
