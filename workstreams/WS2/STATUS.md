# WS2 status

- **State:** active
- **Now:** waiting on reviews; next: polish + whatever WS0 answers (owner's note, /learn list)
- **Next:** T-082 links from hero cards once WS3's content lands · owner's note on model pages if WS0 says it's launch
- **Blocked:** — (open PRs: #22 T-080 → then #23 T-067 and #29 T-092, both stacked on #22 · #25 T-090 · #28 T-091; #24 T-045 merged)
- **Last updated:** 2026-11-15 13:15 UTC by WS2

## Log
- 2026-11-15 11:35 UTC · WS2 chat opened (https://claude.ai/code/session_01JuyZEUSsvVozgE36R16xAS). Claimed T-080. Release 1 has no used prices and no winter-range field yet: the hero shows "not known yet" for both and never guesses (requests sent to WS1/WS0).
- 2026-11-15 12:55 UTC · T-080 done: hero above Explore, rules in the browser (parity with backtest_rules.py), EN + NL, 304 unit tests, hero e2e green. Decision 055. Asked WS1 for winter range + used prices, WS3 for rule units.
- 2026-11-15 12:35 UTC · PRs #22 (T-080), #23 (T-067 Suggested sort), #24 (T-045 differences only), #25 (T-090 /data page) open; CI green on #22–#24. T-043 loan part was already done (overnight); nothing left for launch. /learn pages render already (T-039/T-027/T-082 wait for WS3 content).
- 2026-11-15 13:15 UTC · #24 T-045 merged. New: #28 T-091 parked features behind flags, #29 T-092 hero used price per build year (reads WS1's used_prices.json). Hero got the UX v6 scene; Explore's panel gained seats/AC/build-year filters (same params as the hero). Hero decision renumbered to 055 (053 and 054 went to Dependabot decisions).
- 2026-11-15 14:15 UTC · New since last entry: #36 T-093 (hero /learn links + travel-map texture), #37 T-094 (variant page used price by build year, stacked on #29). All WS2 PRs green on their heads.

## Retro (first WS2 session, 2026-11-15)
- **What slowed us down:** decision numbers clashed twice (053, 054 went to Dependabot decisions while in my START range); pushes from this session don't trigger CI (runs started with workflow_dispatch); a rebase of a pushed branch then a blocked force-push cost a messy merge with leftover conflict markers; stacked PRs need re-merging after every main change.
- **What Menno had to do by hand:** nothing so far.
- **Proposed rules (for WS0 to add to operating-rules / AGENTS.md):** (1) each workstream owns a fixed decision block (e.g. WS2 = 055–069) listed in DECISIONS.md, and WS0 takes from its own block; (2) never rebase a pushed branch, merge main in instead; (3) grep for conflict markers before every push (or a pre-push hook); (4) after a push from a Claude session, start CI with workflow_dispatch and trust the run on the PR head.
