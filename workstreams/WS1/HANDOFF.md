# WS1 handoff — 2026-11-15 ~12:55 UTC

Chat: https://claude.ai/code/session_01JuyZEVuT84JYBi2Cty9CzW (2nd WS1 session). Next chat: "Read workstreams/WS1/HANDOFF.md and START.md and go."

## State: 2 PRs open, both branched from main

| PR | Branch | What |
|---|---|---|
| [#15](https://github.com/zkMenno/EV-Finder/pull/15) | `t-069-shortlist-scores` | T-069: `shortlist_scores.json` per release (18 profile combos per variant, reasons, unknowns, 0..1 factors), Decisions 040–042, CHATS row. CI green. |
| [#21](https://github.com/zkMenno/EV-Finder/pull/21) | `t-081-used-price-bands` | T-081 + T-056: `used_prices.json` (model bands per variant × build year × country, manual-sample override + qa.json back-test), Decision 043, research/R-40, audits/A-31, this handoff. |

Merge #15 first; #21 then has a two-line DECISIONS.md conflict (keep both entries).

## Waiting on others
- **WS0 schema (T-066/T-065):** `ShortlistScoresRelease`, `UsedPricesRelease` (shapes in WS0 INBOX 11:55 and 12:40), plus the earlier TownsRelease, ConsumptionMatrixRelease, retired_ids, ac_kw_optional (T-063 blocked).
- **WS0/Menno:** who notes manual price samples (layer 2)? Until someone does, every price band is a model estimate. Asked WS0 to put it in QUESTIONS.
- **WS3:** `unit` on road-tripper DC rows and the winter field in shortlist_rules.yaml; cited list prices (UK, Tesla) for price coverage; T-068 EV6/IONIQ 5 84 kWh split; manual price aggregates format (WS3 INBOX 12:40).
- **WS5:** permission to show AGPI / Autotrader RPI / Indicata as public trend lines (R-40 §1), only if wanted.
- **Menno (QUESTIONS):** Q-047 (KilowattApp provenance: also decides whether its 1,099 values stay in the open bundle, A-31), Q-059.

## Open work for WS1 (next, in order)
1. Review notes on #15 / #21 if they appear in the INBOX; rebase #21 after #15 merges.
2. START §3 item 6: winter range quality. Rerun T-035 (EPA proxy back-test) on the calibrated matrix and report per profile-relevant field (winter range, DC km in 20 min) in qa.json. Needs live staging: `EV_DATA_DIR=<dir> uv run ev fetch fueleconomy && uv run ev normalise fueleconomy` (plus openev, kilowatt-openev).
3. Refit `basis_scale` in `pipeline/ev_pipeline/derive/shortlist_params.yaml` after item 6 changes the matrix (method in Decision 042; the dry-run script pattern is in the T-069 handoff notes).
4. T-063 and T-064 part 2 once unblocked.

## Decisions made in this chat
- 040, 041 (charging defaults; climate + consumption basis) logged as proposed earlier.
- 042: shortlist scores = editorial release file; basis bridge (winter ×1.24, Wh/km ×1.155, DC ×1.42) keeps Menno's thresholds; unknown = 0.5 and listed; > half unknown → not-enough-data.
- 043: used price model = list price at registration × kept share (DAT/ING/Allianz anchors), ±12 % band, samples override, indices internal only.

## Data notes worth knowing
- Tesla Model Y LR gen1 and Juniper LR AWD rows both show WLTP 11.0 kWh/100 km and 387 km DC in 20 min: likely wrong (told WS0).
- Price facts carry `record_year` (RDW = first-registration year): the band uses that year's list price.
- Coverage holes that make scores neutral: bidi, heat_pump, one_pedal, frunk, width (0 rows each); boot_l 119/226.
