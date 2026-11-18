# WS2 status

- **State:** active
- **Now:** T-130 part 2 PR #126 (fresh review running); then #111 merge-main, verify tooltip fix, T-131
- **Next:** T-131 Popular used EVs, T-135 photo cards, T-132 hero redesign; #111 needs main merged in
- **Blocked:** — (waiting, not blocked: WS1 #21, #38, #15; WS3 #35)
- **Last updated:** 2026-11-18 09:35 UTC by WS2 (5th chat)

## Log
- 2026-11-15 11:35 UTC · WS2 chat opened (https://claude.ai/code/session_01JuyZEUSsvVozgE36R16xAS). Claimed T-080. Release 1 has no used prices and no winter-range field yet: the hero shows "not known yet" for both and never guesses (requests sent to WS1/WS0).
- 2026-11-15 12:55 UTC · T-080 done: hero above Explore, rules in the browser (parity with backtest_rules.py), EN + NL, 304 unit tests, hero e2e green. Decision 055. Asked WS1 for winter range + used prices, WS3 for rule units.
- 2026-11-15 12:35 UTC · PRs #22 (T-080), #23 (T-067 Suggested sort), #24 (T-045 differences only), #25 (T-090 /data page) open; CI green on #22–#24. T-043 loan part was already done (overnight); nothing left for launch. /learn pages render already (T-039/T-027/T-082 wait for WS3 content).
- 2026-11-15 13:15 UTC · #24 T-045 merged. New: #28 T-091 parked features behind flags, #29 T-092 hero used price per build year (reads WS1's used_prices.json). Hero got the UX v6 scene; Explore's panel gained seats/AC/build-year filters (same params as the hero). Hero decision renumbered to 055 (053 and 054 went to Dependabot decisions).
- 2026-11-15 14:09 UTC · New since last entry: #36 T-093 (hero /learn links + travel-map texture), #37 T-094 (variant page used price by build year, stacked on #29). All WS2 PRs green on their heads.

- 2026-11-17 09:39 UTC · New WS2 chat (https://claude.ai/code/session_01JuyZEY92VBv8zzhiK2gGQR). T-097 done: Nerd Value column shows the car's own figure with units in 6 languages; PR #56. Push access was missing at first (patch kept, applied after Menno granted it).

- 2026-11-17 10:36 UTC · 2nd WS2 chat (https://claude.ai/code/session_01JuyZEX8cuXWPhPXbCY6bGD). #56 CI e2e had failed (360 px NL overflow 18 px + axe scroll region); fixed with short cooling words + breakable unit, fresh review passed on 76ebe52, Menno merged #56. Follow-up #68: test the served routes (review found /nl/de redirects). Flagged to WS1: consumption_kwh_100km too low (Model Y LR 11.0).

- 2026-11-17 11:42 UTC · #68: the served-route test caught a real DE bug (16 px clip on CI, font-dependent); fixed with breakable words + nowrap numbers, merged Points×Weight column, 12 % wider-text pass in the 360 px test. Review passed. My self-merge was blocked by the session permission check; Menno merges.

- 2026-11-17 21:48 UTC · 3rd WS2 chat (https://claude.ai/code/session_01JuyZEUgDrkg5ED4ZkeyEzg). T-137: all countries English only via config (served list), picker/banner hidden for single-language countries, e2e english-only.spec.ts for 7 countries. PR #111.

- 2026-11-18 08:55 UTC · 5th WS2 chat (https://claude.ai/code/session_01JuyZEW7knztpvwmHJjJ3mb). Started T-130 part 2.
- 2026-11-18 09:12 UTC · 6th WS2 chat (https://claude.ai/code/session_01JuyZEWZuyZEW). No part-2 branch found on origin; starting T-130 part 2 on t-130-catalogue-visual.

- 2026-11-18 09:35 UTC · T-130 part 2 PR #126: filter groups, phone sheet, pills, one card per generation, used price + winter filters. Full e2e 132 passed, verify 6/6.

## Retro (first WS2 session, 2026-11-15)
- **What slowed us down:** decision numbers clashed twice (053, 054 went to Dependabot decisions while in my START range); pushes from this session don't trigger CI (runs started with workflow_dispatch); a rebase of a pushed branch then a blocked force-push cost a messy merge with leftover conflict markers; stacked PRs need re-merging after every main change.
- **What Menno had to do by hand:** nothing so far.
- **Proposed rules (for WS0 to add to operating-rules / AGENTS.md):** (1) each workstream owns a fixed decision block (e.g. WS2 = 055–069) listed in DECISIONS.md, and WS0 takes from its own block; (2) never rebase a pushed branch, merge main in instead; (3) grep for conflict markers before every push (or a pre-push hook); (4) after a push from a Claude session, start CI with workflow_dispatch and trust the run on the PR head.
- 2026-11-17 04:14 UTC · Menno OK'd WS2 merging its own PRs (WS0 was idle). Merged #22 T-080, #23 T-067, #29 T-092, #36 T-093, #37 T-094, #28 T-091, each with main merged in, local e2e green and CI green on the PR head. Main f40d475: CI + Images green. START §3 #6 checked on main: hreflang + canonical + html lang right on 99 launch page × language combinations; NL complete except internal staff.review.* strings.
- 2026-11-17 23:58 UTC · WS2 (https://claude.ai/code/session_01JuyZEUuCTBUyPNJ74C3iRD): T-130 part 1 PR #117 (+ gate PR #118). Next: T-130 part 2 (design's visual layer), then T-131. Asked WS1 for a release popularity field.
- 2026-11-18 00:45 UTC · #117 ready to merge (re-review PASS, CI green on da6521b); merge blocked in this session, asked WS0/Menno. Then #118.
- 2026-11-18 08:55 UTC · #117 + #118 merged (T-130 part 1 done). Next: T-130 part 2 in a fresh WS2 chat.
