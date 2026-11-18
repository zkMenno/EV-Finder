# WS3 handoff (2026-11-18 11:45 UTC, end of 4th chat)

Next chat: "Read workstreams/WS3/HANDOFF.md, STATUS.md and START.md and go."

## Open PRs (all wait for a fresh review)
| Task | PR | What |
|---|---|---|
| T-136 task 2 | #129 | 35 models / 37 generations from R-41, EU match 86.7 % → 95.6 %, ev verify 0 blocking (+37 gens, +40 rows), no gate PR needed. CI green (both runs on the head). |
| retro 1b | #130 | `data/seed/data_qa.sh`: the four CI data-qa steps in one command. |

## Waiting
- WS0: are EQV, ë-Berlingo, e-Rifter in scope ("vans Later")? If not, drop their three blocks from #129 (or a follow-up).
- WS1 (INBOX 11:20): OpenEV market filter (then add Leapmotor T03); SEAT make vs KBA 'SEAT BORN' (then add SEAT Mii); 3 guard tests changed in #129.
- Menno: T-041 tap check.

## Next steps
1. **T-136 stretch**: absorb branch `t-136-extra-models-2nd-chat` (WS3 2nd chat, +51 models, 20 new makes, 13 EEA alias fixes on existing models incl. 'EQ FORFOUR' counted as the fortwo) on a new branch after #129 merges. Keep #129 ids where both exist; its e-up!/Model X/e-tron GT splits differ from #129 (e-tron GT: keep one generation, see below); drop its vans only if WS0 says so. Re-run: matching regression (scripts below), coverage, ev verify main vs branch.
2. e-tron GT facelift: seed variants for S / RS / RS performance with cited 105/97 kWh packs (Audi eTD PDFs on uploads.audi-mediacenter.com), variant_links + pack, then split per Decision 057.
3. Generation-level platform links for the new models where a maker page names the platform (platforms.yaml already has `stellantis-stla-medium` and `mercedes-eva2` unused): e-3008/e-5008, EQE/EQS (+SUV). Cited only.
4. config/popularity.yaml is WS3's once #117 merges.
5. A-36 S4 NL loan rate only with an official sourced series; A-36 S3 /learn with Menno; older list (price samples DE/FR/BE/UK, heat pump gaps, La Centrale slugs).

## How this chat measured (reuse)
- EEA per-year registrations: `python3 -I research/R-41-catalogue-coverage/pull_eea.py /tmp/t136` (~8 min), then the coverage share with R-41's `coverage.py` logic.
- Matching regression: load main's and the branch's models.yaml with `ev_pipeline.match.seed.load_seed`, run `find_model_noted` / `find_by_source_alias` over every staging record (all sources), diff the model ids: must be 0 changes for previously matched records.
- `ev refresh --no-release --force` (~18 min), `ev verify --skip-tests` on main, then on the branch with `--base main`; the diff of the two reports is the change.
- RDW BEV years per name: `data/staging/rdw.records.jsonl`, only `record_key` starting `m9d7-ebf2:` (the others repeat the count per spec).
