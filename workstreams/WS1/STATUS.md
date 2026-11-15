# WS1 status

- **State:** active
- **Now:** T-035 back-test harness
- **Next:** T-051 part 2, T-062/T-063 if empty, R-21/R-22 follow-ups
- **In review (merge in this order):** #4 T-064 part 1 → #5 sources.yaml → #7 T-025 → #9 T-034 → #10 T-032/T-033. Then T-064 part 2 after Data publish of release 1.
- **Blocked:** —
- **Last updated:** 2026-11-15 10:25 UTC by WS1

## Log
- 2026-11-15 09:35 UTC · WS1 chat opened (https://claude.ai/code/session_01JuyZEUoRSsomn4V9CyYzLY), 1197 pipeline tests green on main. Claimed T-064.
- 2026-11-15 10:05 UTC · T-064 part 1 PR #4: manifest + per-generation split, publish/fetch/verify by sha256, workflows, web fetch script. 1232 tests green.
- 2026-11-15 09:50 UTC · PR #5 sources.yaml housekeeping; PR #7 T-025 (manual charging YAML, release diff to review, refresh fix). Proposed Decision 040 to WS0. (Earlier log line says 10:05 UTC; it was ~09:35.)
- 2026-11-15 10:25 UTC · PR #9 T-034 (7,654 towns, 7,203 with Jan mean + P10; ERA5-Land stub) and PR #10 T-032/T-033 (EPA tests, matrix 57 KB gzip). Schema requests + Decision 041 proposal to WS0; shapes to WS2; taxonomy defaults to WS3.
