# WS0 handoff (2026-11-17 12:15 UTC)

Mission in flight: **fix the 5 launch blockers from QA A-35** (audits/A-35-launch-review-1.md), tasks T-110–T-119, Decisions 064–068. Done = release 2 published (`latest` = 2, release diff vs 1), hero walk passes on release 2 (winter range + used band on most NL cards; road-tripper NL €15k vs €35k differ), Model Y passes the plausibility gate, /de/de and /fr/fr show no English UI strings, CI green per PR head, A-35 findings marked fixed in task `## Review` lines. Then give Menno a prompt for QA launch review 2.

## Menno decided today (popups)
- B2 → Decision 064: budget compares real used band → depreciation estimate from new price → new price; no price = never top 5, listed last.
- B3 → Decision 065: web reads `shortlist_scores.json`; no web scoring copy.
- B5 → Decision 066: Spain + Italy become launch countries (/es/es, /it/it only).
- Q-008 → Decision 068: single cited maker facts may ship.

## Merged today
#42, #45 (verification layer), #46 (A-35), #44 T-123, #51 T-127, #49 T-124 (gate-ok), #57 (REVIEW R4 + D3/D4/D6/D12; G-34–G-39; approved_changes.yaml gated), #56 T-097, #61 T-111 thresholds, #60 T-110 Model Y + seed figures.

## Open PRs and next action
| PR | Task | State | Next |
|---|---|---|---|
| #62 | T-111 code | main merged in by WS0 (fd06891), 586 km swapped in; reviewed pass on 88d618a | Wait CI on fd06891 → merge (review comment: R0 re-run on new head) |
| #63 | T-113 gate (used_price_params.yaml) | CI green, **not reviewed** | Fresh review → merge |
| #64 | T-113 code (stacked on #62) | CI green, **not reviewed** | After #62: merge main in, fresh review → merge. Its PR body has the proposed `used_prices.json` schema shape (WS0 adds to packages/schema) |
| #65 | T-112 new prices (77 % coverage; BE 71, NL 95, DE 12, FR 14, UK/ES/IT 0) | CI e2e was running, **not reviewed** | Fresh review → merge. Needs: ES/IT in schema `Country` enum (WS0), manual loader accepts `observed_at` (WS1) |
| #58 | T-063 (WS1) | reviewed pass on d46df28; DECISIONS conflict with 067 | Merge main in (keep both), CI, merge |
| #69 | T-114 hero reads release scores | CI green, **not reviewed**; **conflicts with #56** (now on main: Nerd table, FactorScore) | Merge main in and adapt, fresh review → merge |
| #70 | T-115 budget rule (stacked on #69) | CI green, not reviewed | After #69 |
| #59 | T-040 staging runbook (WS4) | changes needed (auth fail-open, password in history, exact commands, Caddy ≥ 2.8, Caddyfile unvalidated) | Wait for WS4; then hand Menno the runbook in plain words |

## WS0's own to-dos
- packages/schema: add `es`, `it` to `Country`; add the `used_prices.json` shape from #64 (`basis: band | estimate`, method, source, date). One schema PR, fresh review.
- Next gate PR: rules.md G-06 "last fired 2026-11-17 (gate-ok on #49)".
- After merges: WS1 refits the depreciation curve with T-112 prices (`ev used-price fit`, params PR).
- T-116 release 2 belongs to WS1 (its chat), after #62/#63/#64/#65 merge; also sources.yaml per Decision 068.
- Then B5: T-117 strings (WS2 + WS3), T-118 Spain/Italy data (WS3), T-119 routes (WS2). Use one subagent per lane, one task per PR.
- Follow-ups noted: #51 spot-check table on failed rebuild; Kona SX2 battery 36.5 kWh looks wrong (WS3); keep-8-years add-on has no scores (WS1, T-069); verify-web feature map needs a no-scores flow (gate PR); #56 screenshots 1280/dark (WS2).
- T-128 Verified stamp; gate-guard → enforce on 2026-11-24 (follow-ups listed in T-121).

## Watch-outs learned today
- Session pushes often don't start CI: check runs after ~60 s, else `gh workflow run ci.yml --ref <branch>`. e2e can be cancelled by concurrency: re-run failed jobs.
- Rule numbers collide across chats: check rules.md on main right before adding a G-id.
- Other chats active: WS1 (5th) https://claude.ai/code/session_01JuyZEXwrHCn4kh6fda8bso, WS4, WS2. Read WS0 INBOX first.
