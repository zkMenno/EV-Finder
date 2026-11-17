# WS1 handoff — 2026-11-17 ~10:35 UTC

Chat: https://claude.ai/code/session_01JuyZEUkCfiK3pkbkjjyqf (4th WS1 session). Next chat: "Read workstreams/WS1/HANDOFF.md and START.md and go."

## State
| PR | What | Where it stands |
|---|---|---|
| [#58](https://github.com/zkMenno/EV-Finder/pull/58) | T-063 optional on-board charger (`ac_kw_optional`), Decision 046 | Built by this chat; needs a **fresh** review (REVIEW.md from origin/main), then WS0 merge. 1424 tests green locally, CI dispatched. |
| [#49](https://github.com/zkMenno/EV-Finder/pull/49) | T-124 property tests + Decision 045 | Reviewed by this chat on b4042fa: pass, no must-fix. Head d7db591 adds only the review notes. WS0: `gate-ok` (pyproject + conftest are gate files) and merge. |
| #44, #51 | T-123 release diff, T-127 `ev verify` | Merged by WS0 (09:54 UTC). |
| [#61](https://github.com/zkMenno/EV-Finder/pull/61) | T-111 thresholds | **WS0's subagent owns T-111.** This chat dropped its duplicate and left a dry-run cross-check as a comment on #61. |

## Coordination (important)
WS0 builds the A-35 fixes "with one subagent per lane" (WS0 INBOX 09:55). Its WS1-lane subagent already took T-111 at 10:04 UTC. **Before touching T-113 or T-116, check open PRs and remote branches (`git ls-remote origin 'refs/heads/t-11*'`) and WS1 INBOX for WS0's answer** (asked in WS0 INBOX 10:35 who owns T-113/T-116).

## Next for WS1 (in order, skip what WS0 owns)
1. Fresh review of #58 by someone who didn't build it (or ask QA/WS0).
2. T-113 / T-116 only if WS0 hands them back.
3. **Winter range field** (WS2 waits for it: WS1 INBOX 12:55 15 Nov; BOARD "WS2 idle, waiting on WS1 data fields"): agree the field name with WS0 (`real_range_winter_km` is already a FactField), then START §3 item 6 / T-070 (task file says Wave 9, needs WS0 tag).
4. WS3 asks still open in WS1 INBOX: `normalise.key` '+' → 'plus' (T-068; xfail test waits in test_t124), `years:` on manual facts (T-031).

## Findings worth keeping
- OpenEV has no optional-charger signal: 0 of 746 AC records mention one. Routing has to come from citations (Decision 046). WS3 asked to cite e-208/e-2008, Megane EV40, MG4 Standard, I-Pace.
- Release 1 plausibility dry run (in the #61 comment): same-pack sibling WLTP ratio > 1.3 flags only Model Y LR ×2, Enyaq 85 (752 km), Taycan Turbo GT. DC km/20 vs generation median misfires on long-range versions (Leaf e+, Model 3 LR, ID.3 GTX).
- Main moves fast: pushes to main need fetch + merge + retry; `/tmp/keepboth.py`-style "keep both sides" resolves INBOX/DECISIONS conflicts.

## Decisions made in this chat
- 046 (T-063): a citation routes a source's AC figure to `ac_kw_optional`; blocked citations count as evidence only; never guessed.
