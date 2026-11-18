# T-136 Catalogue size: every EU EV variant since ~2011 (report first)
Role: builder   Lane: WS1 + WS3: research/   Wave: launch (staging feedback 2026-11-17)
Status: review (WS1 6th session, 2026-11-17)

## Goal
Know how many EV variants we can cover from open, licensed sources before building.

## Acceptance criteria
- [x] Research note `research/R-xx-catalogue-coverage.md`: for EEA CO2 monitoring data, RDW type approval, KBA, OpenEV (and other open sources found): licence, coverage years, fields, trim × year granularity, estimated variant count after de-duplication
- [x] Expected total count (vs ~1500 on EV Database) with the method, and what each source adds
- [x] Never scrape EV Database or marketplaces
- [x] Proposal for the build tasks; WS0 approves before building (scope and licence check)
- [ ] Verify skill for the lane; evidence pack in the PR; `Verified:` on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes

## Inputs
docs/spec/feedback-2026-11-17-staging.md item 5; Decisions 009, 068

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes
- 2026-11-17 WS1 (6th): research/R-41-catalogue-coverage.md + measurement scripts in research/R-41-catalogue-coverage/. Measured live (EEA Discodata 2010–2025 grouped, RDW grouped, OpenEV/Kilowatt shallow clones); nothing raw committed.
- Headline: 9.11 M EU BEVs 2010–2025; our 92 seed models match 86.7 %; expected total ~900–1,200 buyer variants (🟡, EEA make+type+power ≥ 200 = 1,024); ~600 variants reach ~95 % of registrations.
- WS3 asked: the ~40 missing models list is in R-41 (task 2 of the proposal is your lane). SEAT 21k is probably Cupra Born filed as SEAT (alias check).
- 🔴 For WS0: 22 KilowattApp rows cite ev-database.org; proposal 3 excludes them and asks the maintainer (WS5 email, Menno's name → needs his ok).
- Build proposal (5 tasks) waits for WS0 approval; nothing built.

- 2026-11-18 WS3 4th chat (task 2, approved WS0 08:58, Decision 048 soft-launch bar), PR on branch `t-136-missing-models`: **35 models / 37 generations** added from R-41's list (makes Jeep and Mazda new), EU BEV registrations matched **86.7 % → 95.6 %** (EEA 2010-2025, R-41 coverage.py + the pipeline matcher). Release (ev verify, fresh staging): +37 generations, +40 rows, 0 blocking, so no gate PR.
  - Years from EEA (CC BY 4.0) and RDW (CC0) registrations; rule in the comment above `jeep` in models.yaml. Every generation `uncertain: true`, counts by year in its notes. No specs, no seed variants: rows come from OpenEV/KilowattApp.
  - Splits: Model X (EEA type 002 → 004 in 2022, `-palladium` like the Model S). e-up! stays one generation (battery change without facelift = marker, Decision 057; VW press cited). **e-tron GT stays one generation for now**: Audi's 2024 pack (105/97 kWh, cited) is a Decision 057 split, but OpenEV's 2024-2025 files still carry the old 85/93.4 kWh pack, so a facelift generation would show wrong figures. Next: facelift seed variants with cited packs, then split.
  - EQE / EQS: saloon and SUV are separate models (OpenEV splits them); EEA and RDW names do not, so register counts land on the saloon (`name_excludes: [SUV]` keeps fueleconomy's '(SUV)' names off it). WS1's type-approval split (E2EQEW/X, E2EQSW/X) can separate them.
  - Left out: **Leapmotor T03** (OpenEV has China-market files only: markets CN, NEDC/CLTC; six non-EU variants would ship; needs an OpenEV market filter, WS1); **SEAT Mii** (a SEAT make breaks KBA's 'SEAT BORN' → Cupra, find_by_source_alias runs only for makes the seed lacks; WS1).
  - Vans: EQV, ë-Berlingo, e-Rifter are in (R-41's list, M1 passenger versions); WS3 2nd chat asked WS0 whether "vans Later" excludes them. Each is one block to drop if so.
  - Guard tests: 3 files expected "e-tron GT not in the seed"; now they expect audi-e-tron-gt, never audi-e-tron (cross-lane, WS1 told).
  - Stretch (not in this PR): the 2nd chat's branch `t-136-extra-models-2nd-chat` (+51 models, 13 alias fixes on existing models incl. 'EQ FORFOUR' counted as the fortwo). Next: a second PR absorbing it after this one merges.
- 2026-11-18 WS3 2nd chat, branch `t-136-extra-models-2nd-chat` (absorbed below; kept as written) (task 2, approved by Menno 2026-11-18 + WS0 08:58): 86 missing models added to `data/seed/models.yaml` (20 new makes), plus EEA spelling aliases on 13 existing models. Coverage count (Decision 048): **models 99 → 182, generations 122 → 208, seed variants 129 (unchanged; release variants come from WS1's T-073), EU BEV registrations matched 86.7 % → 97.7 %** (EEA 2010-2025, R-41's coverage.py, 9,079,365 cars).
  - Every new generation is `uncertain: true` with its EEA registrations by year in `notes` (years follow the seed's 5 % rule on first-registration years; not yet checked against maker documents). Splits per Decision 057: e-up! (32 kWh 2019), Model X (Palladium 2022), e-tron GT (2024 facelift, 105 kWh).
  - Left out on purpose: van-based people carriers (EQV, ë-Berlingo, e-Rifter, Combo-e Life, eVito Tourer, e-NV200, Proace (City) Verso, Kangoo E-Tech, SpaceTourer, Traveller, Zafira Life, EQT: ~65k cars, 0.7 %) because product scope says "vans Later"; question to WS0. SEAT Mii electric (15k) and Cupra filed as SEAT in EEA (5k): adding a SEAT make would break KBA's 'SEAT BORN' → Cupra mapping (find_by_source_alias runs only for makes the seed lacks); matcher change asked of WS1. Toyota 'PRIUS' / 'AURIS HYBRID' (EEA misfiles), Tesla 'MODEL' (ambiguous), tail makes under ~1k cars.
  - EEA cannot tell the EQE/EQS saloon from the EQE/EQS SUV: EEA counts go to the saloon models; the SUV models match only names with 'SUV'.
  - Fix found on the way: ~4.5k 'EQ FORFOUR' cars were counted as the fortwo; they now match the new forfour model.
  - Pipeline guard tests updated (8 cases, None → the new model id: e-tron GT, e:Ny1, Ioniq 9, forfour); cross-lane, flagged to WS1.
  - Next release (WS1 nightly) will add the new generations; their release-diff approvals go in a separate gate PR.

- 2026-11-18 WS3 4th chat (owner, after the collision): the 2nd chat's branch is merged into `t-136-missing-models` (PR #129) and van-based people carriers are added (Menno, WS3 INBOX 10:30).
  - Merge rule: our ids where both exist (jeep-avenger, opel-frontera, renault-twingo and the 29 models both chats added), their extra name_aliases unioned in; their 50 other models and 13 alias fixes taken; leapmotor-t03 stays out (OpenEV China-only); e-tron GT stays one generation (their 2024 split waits for cited packs).
  - People carriers (M1 only, cargo vans out): eVito Tourer, EQT / eCitan Tourer, e-NV200 / Evalia, Townstar EV, Kangoo E-Tech, Combo-e Life, Zafira-e Life (+ Vivaro-e Combi), Proace Verso, Proace City Verso, ë-SpaceTourer (+ ë-Jumpy Combi), e-Traveller (+ e-Expert Combi), Partner Tepee Electric, e-Doblò, e-Ulysse (+ e-Scudo Combi), E-Tourneo Custom (+ Transit Custom Kombi), E-Tourneo Courier, PV5 Passenger; plus the B9 Berlingo Electric generation (2017-2020). EQV, ë-Berlingo, e-Rifter, ID. Buzz were already in. Years from EEA by the rule above `jeep`; e-NV200 2014 (4.2 %) falls under the 5 % start rule, so it starts 2015 (judgement: rule kept).
  - Combi / Life pairs share one model because EEA names them alike ('VIVARO ZAFIRA LIFE', 'JUMPY SPACETOURER', 'EXPERT TRAVELLER'); say if Menno wants them apart.
  - Coverage (R-41 coverage.py, EEA 2010-2025, 9,079,365 BEVs): main 86.7 %, 4th chat 95.6 %, 2nd chat 97.7 %, merged 97.9 %, **with people carriers 98.5 %** (201 models, 227 generations, 192 models hit).
  - Release: isolated rebuild (main seed vs this seed, same fresh staging 2026-11-18): +105 generations, +79 rows, 21 blocking = all smart-eq-fortwo used-price bands (forfour split). Approvals in gate PR `t-136-gate-approvals` (release: 3); with them 0 blocking. Spot cars (EV6, Ioniq 5, MG4, Model Y, P7/P7+) unchanged.
  - For WS1 🟡: ë-SpaceTourer base row reads 46 kWh with 341 km WLTP and 24.5 kWh/100 km (pack and range look mixed from two versions); E-Tourneo Courier 350 km WLTP looks high. Rows come from OpenEV/Kilowatt, not the seed.
  - Still out: SEAT (Mii, Cupra-as-SEAT; matcher change with WS1), Leapmotor T03, Tesla 'MODEL', Spanish 'NUEVO ...' names (next alias gains), Maxus (not van-based).

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts. -->
