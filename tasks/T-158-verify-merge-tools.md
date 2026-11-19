# T-158 Verify and merge tools: `ev verify --keep`, approved_changes warning, merge_ready.sh
Role: builder   Lane: pipeline/ (WS1); scripts/merge_ready.sh (WS0-owned, built here, flag it)   Wave: launch
Status: todo

## Goal
The merge and verify tools stop the misses the 19 Nov batches hit by hand.

## Acceptance criteria
- [ ] **G-53:** `ev verify --keep <dir>` keeps its scratch build so a builder can trace where a value came from.
- [ ] **G-54:** approved_changes validation warns when an entry's `release` is ≤ the latest published release when its PR merges.
- [ ] **G-52:** `scripts/merge_ready.sh <pr>` exits non-zero when the PR branch is behind main (`compare main...head`, behind_by > 0) or CI on the head isn't green, with a plain message. Merge batches run it as its own step, before the merge command. Cross-lane (WS0 file), flagged in the PR.
- [ ] Tests with fixtures (no network: the script's GitHub calls are mocked or it takes JSON on stdin in tests); docs/process/README.md merge steps mention the script (one line, flagged).

## Inputs
WS0 INBOX 2026-11-19 03:32 UTC (batch: T-151, retro 4); rules G-52–G-54.

## Out of scope
Data changes (T-155). Branch protection settings (Menno's account).

## Handoff notes

## Review
