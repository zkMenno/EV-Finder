# WS1 status

- **State:** active (7th session, https://claude.ai/code/session_01JuyZEWZpw9k11fdnaAKr2X)
- **Now:** T-073 in review (PR #127)
- **Next:** R-41 task 5 long tail (stretch, Decision 048); older HANDOFF items
- **In review:** none (#105, #108, #109, #110 merged)
- **Blocked:** T-063 (schema ac_kw_optional), T-064 part 2 (Data publish + WS4 Dockerfile fetch), EV3/Inster rows (Q-047), launch gate (Q-059)
- **Last updated:** 2026-11-17 11:00 UTC by WS1 (5th)

## Log
- 2026-11-18 10:25 UTC · 8th: PRs #131 (retired-id manual facts), #133 (image sha check), #134 (photo-only nights), #135 ('+' → 'plus'), all green. Same-data rebuild proof for #135 (16 sources fetched).
- 2026-11-18 10:00 UTC · Menno: coverage 95 %+. Model-level coverage added to #127: main 86.7 %, WS3 t-136 branch 95.7 %. Gap list to WS3.
- 2026-11-18 09:50 UTC · 8th session opened (https://claude.ai/code/session_01JuyZEUgHKypBRfx6deGhfu) next to the 7th (T-073, #127, left alone). Taking HANDOFF item 5 + WS3 asks: '+' → 'plus' name key first.
- 2026-11-18 09:40 UTC · #110 merged after real-data run (120/120 photos valid, schema-valid attach, night refresh fetches photos). All 6th-session PRs merged.
- 2026-11-18 10:05 UTC · PR #127 T-073: 390 groups, 96 candidate variants (271 → 367), 84.3 % of 9.11 M EU BEVs on TGK versions of seed generations.
- 2026-11-18 09:15 UTC · 7th session opened. Decision 048 (Menno's catalogue target), Decision 049 (Q-039 default). Claimed T-073.
- 2026-11-17 23:10 UTC · #108 T-136 R-41 report (measured EEA/RDW), #109 Pillow (gate), #110 T-134 pipeline side. Handoff written.
- 2026-11-17 21:30 UTC · 6th session opened (https://claude.ai/code/session_01JuyZEVR92pcMFzUGsz5wzo). PR #105: images.yml fetches release catalogue by manifest (WS2 URGENT 21:19). Claimed T-136.
- 2026-11-17 11:00 UTC · PR #67 T-072 winter range row field (196/226 in dry run). Handoff written.
- 2026-11-17 10:45 UTC · #58 reviewed (pass). PR #66 T-071 consumption charging losses. Claimed T-072. T-116 back to WS1 after its blockers merge.
- 2026-11-17 10:15 UTC · 5th session opened (https://claude.ai/code/session_01JuyZEXwrHCn4kh6fda8bso). No WS0 answer on T-113/T-116 yet; no t-113/t-116 branches. Reviewing #58.
- 2026-11-17 10:35 UTC · T-111 already taken by WS0's subagent (#61): dropped mine, cross-check comment on #61. Handoff written.
- 2026-11-17 10:20 UTC · #44/#51 merged by WS0. Reviewed #49 (pass). T-063 PR #58. Claimed T-111, T-113.
- 2026-11-17 09:50 UTC · 4th session opened. #15/#21 merged via #39. #44/#49/#51 green but conflicting with main.
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

## Retro 2026-11-17 (4th WS1 run)
- Slowed down: claimed T-111 in INBOX 6 minutes after WS0's subagent had started it; the claim channel (INBOX) is slower than branch creation. Also three PRs needed main merged in twice while WS0 merged around them.
- Menno did by hand: re-sent the queue mid-turn (already in progress).
- Rule that would have prevented it: before building a task, `git ls-remote origin 'refs/heads/t-<id>*'` and open PRs; a branch is the claim. Proposed for docs/process/rules.md.
- What a check missed: A-35's proposed thresholds (> 8 km/kWh, DC vs generation median) would have withheld ~30 real figures; only the G-10 dry run caught it. Check: every new QA threshold PR quotes its hit list on the latest release (count + names).

## Retro 2026-11-15 (second WS1 run)
- Went well: three queue items in ~90 minutes, no PR chain (both PRs branch from main), CI green on #15 first try.
- Friction: the rules' thresholds sat on a different data basis than our fields; caught only by the dry run on real rows. Proposed rule: every derived score or band gets a dry run on the latest release rows before tests are written (pipeline/AGENTS.md).
- Friction: two PRs both append to DECISIONS.md and STATUS.md. Proposed rule: STATUS/HANDOFF changes go in the last PR of a session only.

## Retro 2026-11-15 (first WS1 run)
- Went well: queue items 1–7 done in one run as a PR chain; live fetches checked every licence line and memory (< 400 MB peak).
- Friction: one-task-one-PR on a single moving base made a 9-PR chain; WS0 must merge in order. Proposed rule: WS0 merges WS1 PRs as soon as CI is green, or WS1 batches small housekeeping into the task PR it belongs to.
- Friction: `gh pr create` fails in these sessions (GraphQL blocked); `gh api repos/.../pulls` works. Worth a line in operating-rules.
- Found by the back-test, not by review: model/rung inconsistency (22 %) and wrong EPA matches. Proposed rule: every new derived model ships with a back-test section in qa.json.

## Retro 2026-11-17 (5th WS1 run)
- Slowed down: release 1 has no consumption matrix asset, so the winter dry run had to rebuild the matrix without staging EPA tests (approximate).
- Menno did by hand: nothing.
- Rule that would have prevented the consumption bug: a derived field that copies an official field's name must sit on the same basis; back-test it against the official values where both exist (now in qa.json for consumption). Proposed for docs/process/rules.md.
- What a check missed: the consumption estimate shipped 14 % low on 58 rows; no check compared derived vs official on overlapping rows. Check: qa.json `estimate_vs_official_wltp` (T-071), and REVIEW D3 could name "same basis as the official field" explicitly.

## Retro 2026-11-17 (6th WS1 run)
- Slowed down: T-136 was on both WS1's and WS3's list; I took it by branch first and told WS3. T-134 had no input format from T-133 yet, so I set the contract myself.
- Menno did by hand: nothing.
- Rule that would have prevented it: a task shared by two lanes names one lead lane in its task file.
- Own miss: edited data/sources.yaml without regenerating apps/web's sources.generated.json; CI `web` caught it. Proposed check: pipeline `pre-push` (or WS1 verify skill) runs `node apps/web/scripts/sources.mjs` + `git diff --exit-code` when data/sources.yaml changed.
- What a check missed: release 2 shipped with latest=2 but the image build still read catalogue.json from git; no CI job built the web image on the data-publish PR. Check: the data-publish PR (or the release PR) runs `build web (linux/arm64)` before `latest` moves.
