# WS1 handoff — 2026-11-17 ~23:10 UTC

Chat: https://claude.ai/code/session_01JuyZEVR92pcMFzUGsz5wzo (6th WS1 session). Next chat: "Read workstreams/WS1/HANDOFF.md and START.md and go."

## State
| PR | What | Where it stands |
|---|---|---|
| [#105](https://github.com/zkMenno/EV-Shortlist/pull/105) | images.yml fetches release catalogue.json by manifest before docker build (main could not build the web image since release 2) | `build web (linux/arm64)` green. Gate-only. Needs fresh review + merge. |
| [#108](https://github.com/zkMenno/EV-Shortlist/pull/108) | T-136 report: research/R-41-catalogue-coverage.md + scripts | Needs WS0 yes/trim on the 5 build tasks. |
| [#109](https://github.com/zkMenno/EV-Shortlist/pull/109) | Pillow dependency (gate-only) | Needs review + merge. |
| [#110](https://github.com/zkMenno/EV-Shortlist/pull/110) | T-134 pipeline side (based on #109) | Retarget to main after #109 merges, merge main in, CI. |

## Next for WS1 (in order)
1. After #109 merges: retarget #110 to main, merge main in, CI green, fresh review.
2. When WS0 lands `Generation.image`: check the held-back status flips to `attached` (dry run with one cached photo).
3. When WS3 lands photos.yaml / press-terms.yaml (T-133): add allowed makers' `photo_hosts` to `maker-press-photos.hosts` in data/sources.yaml, run `ev images check`, then `ev images fetch` on the night machine.
4. T-136 build tasks only after WS0 approves (R-41 proposal): variant split from RDW TGK/EEA (needs Q-039), Traficom FI adapter, Kilowatt rows citing ev-database.org excluded.
5. Older open items from the 5th handoff still apply (T-116 done by WS0; #58 follow-up test for the ac_kw_optional rows guard; WS3 asks '+' → 'plus', `years:` on manual facts).

## Findings worth keeping
- EEA Discodata POST works from these sessions; 16 grouped queries take ~10 min (scripts in research/R-41-catalogue-coverage/).
- 9.11 M EU BEVs 2010–2025; seed models match 86.7 %; EEA power field is inconsistent across countries (do not use as a variant key alone).
- 22 KilowattApp rows cite ev-database.org (🔴 provenance).
- Local full pytest needs release 2 assets: `cd apps/web && CATALOGUE_FILES=catalogue.json,catalogue.parquet,facts.parquet,charging_stats.json,consumption_matrix.json,run_log.json,shortlist_scores.json,sources.json,used_prices.json,refresh.json node scripts/fetch-release.mjs`.
