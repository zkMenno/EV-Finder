# WS1 status

- **State:** active (3rd session, https://claude.ai/code/session_01JuyZEWFXbkeYSii8dVSWnx)
- **Now:** T-127 (`ev verify` + pipeline verify skill), then T-124 (Hypothesis property tests)
- **In review:** T-123 release diff (Decision 044), PR on branch `t-123-release-diff`
- **Blocked:** T-063 data side (WS0 delegated FactField entries, still to do), T-064 part 2 (Data publish + WS4 Dockerfile fetch)
- **Last updated:** 2026-11-17 by WS1

## Log
- 2026-11-17 · 3rd session. #15 and #21 merged (in #39); item 6 done in #27. T-123: release diff, blocking `release_diff` QA check, config/approved_changes.yaml, Decision 044. 1412 tests green.
- 2026-11-15 09:35 UTC · WS1 chat opened (https://claude.ai/code/session_01JuyZEUoRSsomn4V9CyYzLY), 1197 pipeline tests green on main. Claimed T-064.
- 2026-11-15 10:05 UTC · T-064 part 1 PR #4: manifest + per-generation split, publish/fetch/verify by sha256, workflows, web fetch script. 1232 tests green.
- 2026-11-15 09:50 UTC · PR #5 sources.yaml housekeeping; PR #7 T-025 (manual charging YAML, release diff to review, refresh fix). Proposed Decision 040 to WS0. (Earlier log line says 10:05 UTC; it was ~09:35.)
- 2026-11-15 10:25 UTC · PR #9 T-034 (7,654 towns, 7,203 with Jan mean + P10; ERA5-Land stub) and PR #10 T-032/T-033 (EPA tests, matrix 57 KB gzip). Schema requests + Decision 041 proposal to WS0; shapes to WS2; taxonomy defaults to WS3.
- 2026-11-15 10:30 UTC · PR #11 T-035 (EPA proxy back-test, calibration, A-30) and PR #12 T-062 pipeline part. EPA power gate tried and rejected (A-30 follow-up). HANDOFF.md written. T-051 part 2 was done overnight; its leftovers are Q-047/Q-083.
- 2026-11-15 10:40 UTC · PR #13 EPA range-class matching rule (fixes EV6/Ioniq 5 wrong attachments). Retro below.
- 2026-11-15 11:30 UTC · 2nd session opened; #4–#13 merged by WS0. Claimed T-069.
- 2026-11-15 11:55 UTC · PR #15 T-069: shortlist_scores.json (18 combos, basis bridge, Decision 042; back-test 6/10 exact). Decisions 040–042 logged.
- 2026-11-15 12:40 UTC · PR #21 T-081 + T-056: used_prices.json (model bands for 99/226 variants, Decision 043, research/R-40); index terms: none licensed.
- 2026-11-15 12:55 UTC · Item 7 open data bundle check: pass (audits/A-31), Q-047 risk noted. HANDOFF.md rewritten.

## Retro 2026-11-15 (second WS1 run)
- Went well: three queue items in ~90 minutes, no PR chain (both PRs branch from main), CI green on #15 first try.
- Friction: the rules' thresholds sat on a different data basis than our fields; caught only by the dry run on real rows. Proposed rule: every derived score or band gets a dry run on the latest release rows before tests are written (pipeline/AGENTS.md).
- Friction: two PRs both append to DECISIONS.md and STATUS.md. Proposed rule: STATUS/HANDOFF changes go in the last PR of a session only.

## Retro 2026-11-15 (first WS1 run)
- Went well: queue items 1–7 done in one run as a PR chain; live fetches checked every licence line and memory (< 400 MB peak).
- Friction: one-task-one-PR on a single moving base made a 9-PR chain; WS0 must merge in order. Proposed rule: WS0 merges WS1 PRs as soon as CI is green, or WS1 batches small housekeeping into the task PR it belongs to.
- Friction: `gh pr create` fails in these sessions (GraphQL blocked); `gh api repos/.../pulls` works. Worth a line in operating-rules.
- Found by the back-test, not by review: model/rung inconsistency (22 %) and wrong EPA matches. Proposed rule: every new derived model ships with a back-test section in qa.json.
