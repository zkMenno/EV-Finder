# WS0 handoff (2026-11-17 16:30 UTC, A-35 fixes chat)

Mission: fix QA A-35 launch blockers. Done = release 2 published (`latest` = 2, diff vs 1), hero walk passes on it (winter range + used band on most NL cards; road-tripper NL €15k vs €35k differ), Model Y passes the plausibility gate, /de/de /fr/fr /es/es /it/it show no English UI, CI green, A-35 findings marked fixed in task `## Review` lines. Then hand Menno a prompt for QA launch review 2.

## Merged today (this chat)
#62 T-111 gate · #63 depreciation params · #58 T-063 · #68 · #66 T-071 · #71 schema ES/IT + used_prices · #67 T-072 winter range · #72 T-117 strings · #75 wording · #73 T-118 ES/IT data · #76 schema scope · #74 price year · #64 T-113 estimate · #65 T-112 maker prices (Autotijd held) · #69 T-114 hero release scores.
Decisions logged: 069 (generation band stands in), 080 (Autotijd held, Menno).
Default taken: a reviewed PR whose files don't overlap with what landed on main since its green CI may merge without another CI run; overlap → merge main in + CI.

## Open PRs and next action
| PR | What | State | Next |
|---|---|---|---|
| #78 | used-price hold-out years | CI green, fresh review running | merge, then #79 |
| #79 | gate: used_price_params ES/IT + refit | CI green, review running | merge after #78 |
| #80 | manual source releasable (068), third-party held, CC BY bundle leak fix | CI green, review running | merge |
| (new) fix/manual-price-years | WS3 subagent adding `year:` to ~100 price rows | building | review → merge |
| #70 | T-115 budget rule | review: must-fix Nerd estimate text names wrong source; should-fix generation-band label, unpriced models at €15k, e2e allows empty | WS2 subagent fixing |
| #77 | T-119 ES/IT routes | review pass (df7baa5); needs main (#69) + HAS_SCORES switch on ES/IT hero tests | WS2 subagent fixing, then CI → merge |
| #59 | T-040 staging runbook (WS4) | changes needed | waits WS4 |

## Then: release 2 (T-116, WS1 lane, subagent-run)
After #78/#79/#80 + price years merge: `gh workflow run data-refresh.yml --ref main`; QA blocks on release diff vs 1; read blocking list from the job summary; approve real data changes (Decision 047 consumption ×1.16, T-068 Ioniq 5 year_end, used bands #64/#79, maker prices #65/#80) in a gate PR to config/approved_changes.yaml; fix, never approve: 19 lost wltp_range_km, rdw-tgk SnapshotError, meteostat timeouts. Re-run → "Data release 2" PR → review → merge → data-publish → latest = 2. Then hero walk on release 2 and the QA review 2 prompt.

## Follow-ups noted
- FR loan.warning: French wording (Code conso L312-5) differs from Belgian → per-country warning; Menno to confirm (Q-072).
- IT CCD2 text: cite the Official Journal, not dirittobancario.it.
- Car pages: some data labels still English on non-English pages (voltage, cooling, glossary long text) — needs release rebuild + a task.
- `{country}` shows own-language country name (FR pages "en Nederland") — WS2 code follow-up.
- CI ranking e2e skips on release 1 (34 tests) → add a release-like fixture step (gate PR).
- maker-docs source: 11 seed citations are third-party copies → WS3 source_id.
- ±12 % used-price spread holds ~53 % of real medians; wording could say "estimate range".
