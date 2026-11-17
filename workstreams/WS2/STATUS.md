# WS2 status

- **State:** working (T-126 → T-125, per Menno 2026-11-17)
- **Now:** #47 T-126 verify skill (review pending); fix PR for two hero bugs (NL Nerd 7 px overflow at 360 px, keep-8 ⓘ inside its label) being verified; then T-125 property tests; T-096 (hero compare-button label, found in review) queued
- **Next:** (a) link /learn/batteries from hero cards once WS3's #35 merges; (b) winter range on hero cards + T-045 deltas once WS1 publishes the field; (c) e2e for used price by build year once a release ships used_prices.json (WS1 #21/#38); (d) read `shortlist_score` from WS1's T-069 (#15) if WS0 wants it
- **Blocked:** — (waiting, not blocked: WS1 #21, #38, #15; WS3 #35)
- **Last updated:** 2026-11-17 05:41 UTC by WS2

## Log
- 2026-11-15 11:35 UTC · WS2 chat opened (https://claude.ai/code/session_01JuyZEUSsvVozgE36R16xAS). Claimed T-080. Release 1 has no used prices and no winter-range field yet: the hero shows "not known yet" for both and never guesses (requests sent to WS1/WS0).
- 2026-11-15 12:55 UTC · T-080 done: hero above Explore, rules in the browser (parity with backtest_rules.py), EN + NL, 304 unit tests, hero e2e green. Decision 055. Asked WS1 for winter range + used prices, WS3 for rule units.
- 2026-11-15 12:35 UTC · PRs #22 (T-080), #23 (T-067 Suggested sort), #24 (T-045 differences only), #25 (T-090 /data page) open; CI green on #22–#24. T-043 loan part was already done (overnight); nothing left for launch. /learn pages render already (T-039/T-027/T-082 wait for WS3 content).
- 2026-11-15 13:15 UTC · #24 T-045 merged. New: #28 T-091 parked features behind flags, #29 T-092 hero used price per build year (reads WS1's used_prices.json). Hero got the UX v6 scene; Explore's panel gained seats/AC/build-year filters (same params as the hero). Hero decision renumbered to 055 (053 and 054 went to Dependabot decisions).
- 2026-11-15 14:09 UTC · New since last entry: #36 T-093 (hero /learn links + travel-map texture), #37 T-094 (variant page used price by build year, stacked on #29). All WS2 PRs green on their heads.

## Retro (first WS2 session, 2026-11-15)
- **What slowed us down:** decision numbers clashed twice (053, 054 went to Dependabot decisions while in my START range); pushes from this session don't trigger CI (runs started with workflow_dispatch); a rebase of a pushed branch then a blocked force-push cost a messy merge with leftover conflict markers; stacked PRs need re-merging after every main change.
- **What Menno had to do by hand:** nothing so far.
- **Proposed rules (for WS0 to add to operating-rules / AGENTS.md):** (1) each workstream owns a fixed decision block (e.g. WS2 = 055–069) listed in DECISIONS.md, and WS0 takes from its own block; (2) never rebase a pushed branch, merge main in instead; (3) grep for conflict markers before every push (or a pre-push hook); (4) after a push from a Claude session, start CI with workflow_dispatch and trust the run on the PR head.
- 2026-11-17 04:14 UTC · Menno OK'd WS2 merging its own PRs (WS0 was idle). Merged #22 T-080, #23 T-067, #29 T-092, #36 T-093, #37 T-094, #28 T-091, each with main merged in, local e2e green and CI green on the PR head. Main f40d475: CI + Images green. START §3 #6 checked on main: hreflang + canonical + html lang right on 99 launch page × language combinations; NL complete except internal staff.review.* strings.
- 2026-11-17 05:41 UTC · #43 T-095 merged after a fresh-reviewer PASS (R0–R3, D6, D8, D10, D13) and green CI on head 699ceec. #47 T-126 opened: `pnpm --filter @ev/web verify`, 14 flows, 3× stress test stable; its first run found a real bug (Dutch Nerd hero too wide on phones), fix PR follows. Asked WS0 for a CI artifact step.
