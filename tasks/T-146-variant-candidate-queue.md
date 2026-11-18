# T-146 Variant candidate review queue, biggest EU registrations first
Role: builder   Lane: data/seed, data/manual (WS3)   Wave: launch
Status: doing (batch: variant queue, https://claude.ai/code/session_01JuyZEXkdc6m6bZgzVV874S, 2026-11-18)

## Goal
Work `data/review/variant-candidates.csv` (T-073) from the biggest EU registrations down: fix seed rows that make the matcher tie or miss, add cited variants for generations that have none, and record a decision for each group worked.

## Acceptance criteria
- [ ] Each group worked has an outcome: seed fix (PR), new cited variant (PR), or a `done` / `wont-fix` status with the reason (status.yaml, WS1 file: one INBOX line).
- [ ] No value from memory: every new or changed spec is cited (maker doc, type approval via RDW, or OpenEV) or left out.
- [ ] `sh data/seed/data_qa.sh` and `ev verify --base main` pass for each PR; matching regression run (0 moves for already matched records, except intended ones).
- [ ] Coverage line (variant-coverage.json) before / after in each PR.

## Inputs
WS0 INBOX 2026-11-18 16:14 UTC "batch: catalogue" (item 6 triage); pipeline/README.md (variant-candidates.csv); ev_pipeline/variants/propose.py; workstreams/WS3/START.md.

## Out of scope
Matcher changes (WS1: asks go to INBOX). Prices. Photos.

## Handoff notes

## Review
