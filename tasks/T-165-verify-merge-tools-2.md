# T-165 Tools round 2: seed-pinned tests in data_qa, missing-input flag report, merge_ready stuck checks, CI runs approvals
Role: builder   Lane: pipeline/ (WS1); cross-lane, flag them: `data/seed/data_qa.sh` (WS3), `scripts/merge_ready.*` (WS0), `.github/workflows/ci.yml` (gate: its own PR)   Wave: launch
Status: todo

## Goal
The misses the 19 Nov afternoon batches hit by hand get checked by a tool.

## Acceptance criteria
- [ ] **G-61:** `data_qa.sh` runs the tests that pin seed state (`pytest -m seed`; mark `tests/test_t153_split.py`, `tests/test_t159_split.py` and any other seed-pinned test), so a seed change can't break them unseen until CI.
- [ ] **G-62:** `ev verify` lists rows whose derived flags change only because an input is missing (e.g. `power_kw` → Decision 088 "unknown → no flag"), with the input named.
- [ ] **G-63:** `merge_ready.sh` treats a check run with a `conclusion` and `completed_at` as completed even if its `status` still says `in_progress`, and says so in its output.
- [ ] **CI data-qa** runs `ev release approvals` (gate PR, ci.yml only).
- [ ] Tests with fixtures (no network).

## Inputs
WS0 INBOX 2026-11-19 15:05, 15:06, 16:05 UTC (retros); rules G-61–G-63.

## Out of scope
Matching and data (T-163).

## Handoff notes

## Review
