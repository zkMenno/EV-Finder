# WS3 handoff (2026-11-15, end of first session)

Session: https://claude.ai/code/session_01JuyZEW2aV2H7ifmpaT5Pfr. Next chat: "Read workstreams/WS3/HANDOFF.md and START.md and go."

## State: PRs open for review
| Task | PR | What |
|---|---|---|
| T-068 seed gaps for picks | #31 | 36 models (8 new makes), EV6/Ioniq 5/G6 facelift generations (Decision 057), picks importer `--remap` + ±1 year nearest (Decision 058). One line in pipeline/tests (flagged WS1). |
| T-031 heat pump (launch part) | #32 | 16 cited heat_pump generation facts in data/manual/heat-pump/; temperature_bands + heater_types taxonomy with 6-language labels (Decision 059). |
| T-041 listing templates | #33 | Patterns checked from indexed URLs + Menno's La Centrale links; tap checklist workstreams/WS3/T-041-checklist.md. One WS2 test line. |
| T-100 glossary sweep | #34 | 10 hero/profile terms; used-price text matches T-081. |
| T-082 batteries + health /learn | (this branch) | EN + NL, plus DE/FR/ES/IT drafts for batteries-health, winter-range (T-039) and charging-2026 (T-027). |

## Waiting on Menno
- T-041: tap the 22 links in the checklist, say which fail. Then set `verified: true` + date.
- T-081 manual price samples: layer 2 means a person notes prices (R-03 Q10). An agent reading listings would be automated access (Decision 004), so WS3 did not collect any. Needs Menno or a helper; WS3 can prepare per-model search links and a sample form.
- Q-008 (maker documents / manual facts releasable?): blocks every fact in data/manual, incl. heat pump fitment.
- EN + NL /learn texts are `review: needed` until he reads them.

## Asked of other workstreams
- WS1: tokenise `+` as `plus` (P7 vs P7+); KBA/DfT/EEA aliases for new models from staging; rebuild release + top40; optional `years` span on manual facts (10 heat pump rows wait); review test line.
- WS2: apply slug_overrides to {MAKE}/{MODEL} (La Centrale); attach the new glossary ids on hero steps and profile chips; review test line.

## Next steps (START.md §3 order)
1. After #31 merges: heat_pump fact for volkswagen-id5-gen1 (option, VW IE page) in data/manual/heat-pump/.
2. Heat pump gaps: maker price lists for Ioniq 6 (non-UK), Niro EV SG2, Mach-E, Q4, EX40, MG4, Highland per variant (needs variant split or `years`).
3. DE/FR/ES/IT for the 10 new glossary terms and for heater/temperature `long` texts.
4. La Centrale / AutoScout24 slug overrides for the top 40 once the tap check shows which names fail.

## Decisions logged
057 (facelift with new packs = generation), 058 (picks importer nearest year + remap), 059 (heat pump as manual facts; heater/temperature labels as taxonomy).
