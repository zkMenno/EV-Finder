# T-123 Release diff test (release N vs N-1) with approved changes
Role: WS1   Lane: pipeline/ev_pipeline/release, pipeline/tests   Wave: process
Status: review (WS1, 2026-11-17)

## Goal
No data release ships a change nobody intended: every value that changed between releases is either on an approved list or blocks QA.

## Acceptance criteria
- [x] `ev release diff --from N-1 --to N` compares catalogue, scores, used prices, consumption matrix and towns per id and field; ignores noise (key order, float rounding at a set precision, generated_at).
- [x] Output `data/review/release_diff.csv` + a short summary in qa.json: added / removed / changed per file and field, biggest moves.
- [x] `config/approved_changes.yaml`: entries by id/field/pattern with a reason and the PR or Decision that approved them; approved changes don't block.
- [x] Unapproved removals of ids, field changes beyond a threshold per field (in config), and any number losing its source → blocking QA.
- [x] Runs in the data-refresh workflow and in CI's data-qa job when data/pipeline/config changed; the "Data release N" PR body gets the summary.
- [x] Tests with two tiny fixture releases (one approved change, one unapproved, one removal).
- [x] Extend the charging release diff (Decision 040 item 4) into the same mechanism, still review-only for charging.

## Inputs
Article: differential tests (old vs new on the same inputs, normalise irrelevant differences, keep a list of approved changes). Handoff gap #9 "release diff checks". A-20 B1.

## Handoff notes
2026-11-17 WS1 (session_01JuyZEWFXbkeYSii8dVSWnx), Decision 044.
- Code: `pipeline/ev_pipeline/release/differ.py` (pure, no network). Hooked into `qa/release_step.finish_release` (every `ev release`) and `qa/check_release` (CI data-qa, rollback) as the blocking check `release_diff`. No workflow edits: data-refresh already pastes `ev release diff` + qa.md into the PR body, and CI data-qa already runs check-release.
- Config: `config/approved_changes.yaml` (record sets, ignore keys, precision, thresholds, approvals). Env `EV_RELEASE_DIFF_CONFIG` overrides the path (tests).
- Blocking: unapproved removal (retired_ids redirect = `retired`), beyond threshold, cleared thresholded value, `source_lost`, `file_removed`. Unthresholded changes = review. Charging = review only.
- Fail closed: bad config, or an N-1 whose files don't match its manifest → check fails.
- Dry run on the real release 1 vs an identical copy: 0 changes, 1.1 s, 235 MB peak. Copy with 5 planted faults: 3 WLTP +10 %, 1 removal, 1 lost source → blocking; +3 km WLTP and a registration count → review.
- Expect: the first refresh after merge blocks on everything changed since release 1 (T-068 etc.). Read the list, add one release-scoped approval with the PR number.
- Follow-up (gate change, not done here): data-refresh doesn't upload `data/review/` when a release is blocked. For now the blocking list goes into the error message, so it shows in the workflow log.
- Tests changed in other files (strengthened, not weakened): test_release now expects the block, then approves; test_qa_check_release expects the new check id; test_t062 re-packages release 1 after editing it so its sha256 matches.

## Review
