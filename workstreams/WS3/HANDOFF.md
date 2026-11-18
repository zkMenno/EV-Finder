# WS3 handoff (2026-11-17 23:15 UTC, end of 3rd chat)

Next chat: "Read workstreams/WS3/HANDOFF.md, STATUS.md and START.md and go."

## Open PRs (all wait for a fresh review)
| Task | PR | What |
|---|---|---|
| T-140 (A-36 S7) | #115 | Cited Ioniq 5 facelift 84 kWh + type-approval WLTP/consumption, 72.6 kWh rows, N facts moved off the retired id, seed + cited rows for Ioniq 5 63 kWh, XPENG P7 (2) and P7+ (2). One flagged line in data/sources.yaml (WS1). |
| T-140 gate | #116 | 14 release-3 approvals in config/approved_changes.yaml (gate file). With #115: 0 blocking, 197 approved. Merge right after #115. |
| T-131 | #106 | data/editorial popular_used.yaml |
| T-133 | #113 | photos.yaml + press-terms.yaml |

## Waiting
- WS0: approve T-136 task 2 (missing-model seed, ~40 models from R-41 / #108); answer CC0 / public-domain Commons photos; renumber T-140 if needed.
- WS1: facelift base WLTP stays 507 km (RDW F5E62 stock matched by year); `ev manual check` should error on retired ids; P7 '+' name key.
- Menno: T-041 tap check; Q-008 answered (Decision 068), so manual facts ship now.

## Next steps
1. T-136 task 2 once WS0 says yes (R-41 list; cite from maker documents or RDW TGK, never memory).
2. A-36 S4: NL used-car loan rate (finance_profiles.yaml) only if an official sourced series exists (R-20 says the DNB/ECB NL series stopped).
3. A-36 S3 (with Menno): /learn and glossary beyond launch scope; English only now (Decision 082).
4. Older list (2026-11-15 handoff): price samples DE/FR/BE/UK via robots-allowed pages, heat pump gaps, La Centrale slug overrides after the tap check.

## How to verify data changes (worked this session)
`cd pipeline && uv run ev refresh --no-release` (~20 min, all 16 sources) once, then `uv run ev verify`. Run it on main too: the diff of the two is your change. Approvals go in their own gate PR.
