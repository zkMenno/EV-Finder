# WS1 status

- **State:** active; queue items 1–6 done or in review, rest blocked on merges/schema
- **Now:** EPA matching fix (A-30 follow-up); handoff written (workstreams/WS1/HANDOFF.md)
- **Next:** T-064 part 2 after #4 merges + Data publish; T-063 after schema; ERA5-Land once CDS key lands
- **In review (merge in this order):** #4 → #5 → #7 → #9 → #10 → #11 → #12
- **Blocked:** T-063 (schema ac_kw_optional), T-064 part 2 (merge + Data publish), EV3/Inster rows (Q-047), launch gate (Q-059)
- **Last updated:** 2026-11-15 10:30 UTC by WS1

## Log
- 2026-11-15 09:35 UTC · WS1 chat opened (https://claude.ai/code/session_01JuyZEUoRSsomn4V9CyYzLY), 1197 pipeline tests green on main. Claimed T-064.
- 2026-11-15 10:05 UTC · T-064 part 1 PR #4: manifest + per-generation split, publish/fetch/verify by sha256, workflows, web fetch script. 1232 tests green.
- 2026-11-15 09:50 UTC · PR #5 sources.yaml housekeeping; PR #7 T-025 (manual charging YAML, release diff to review, refresh fix). Proposed Decision 040 to WS0. (Earlier log line says 10:05 UTC; it was ~09:35.)
- 2026-11-15 10:25 UTC · PR #9 T-034 (7,654 towns, 7,203 with Jan mean + P10; ERA5-Land stub) and PR #10 T-032/T-033 (EPA tests, matrix 57 KB gzip). Schema requests + Decision 041 proposal to WS0; shapes to WS2; taxonomy defaults to WS3.
- 2026-11-15 10:30 UTC · PR #11 T-035 (EPA proxy back-test, calibration, A-30) and PR #12 T-062 pipeline part. EPA power gate tried and rejected (A-30 follow-up). HANDOFF.md written. T-051 part 2 was done overnight; its leftovers are Q-047/Q-083.
