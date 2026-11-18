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

- 2026-11-18 WS3 (task 2, approved by Menno 2026-11-18 + WS0 08:58): 86 missing models added to `data/seed/models.yaml` (20 new makes), plus EEA spelling aliases on 13 existing models. Coverage count (Decision 048): **models 99 → 182, generations 122 → 208, seed variants 129 (unchanged; release variants come from WS1's T-073), EU BEV registrations matched 86.7 % → 97.7 %** (EEA 2010-2025, R-41's coverage.py, 9,079,365 cars).
  - Every new generation is `uncertain: true` with its EEA registrations by year in `notes` (years follow the seed's 5 % rule on first-registration years; not yet checked against maker documents). Splits per Decision 057: e-up! (32 kWh 2019), Model X (Palladium 2022), e-tron GT (2024 facelift, 105 kWh).
  - Left out on purpose: van-based people carriers (EQV, ë-Berlingo, e-Rifter, Combo-e Life, eVito Tourer, e-NV200, Proace (City) Verso, Kangoo E-Tech, SpaceTourer, Traveller, Zafira Life, EQT: ~65k cars, 0.7 %) because product scope says "vans Later"; question to WS0. SEAT Mii electric (15k) and Cupra filed as SEAT in EEA (5k): adding a SEAT make would break KBA's 'SEAT BORN' → Cupra mapping (find_by_source_alias runs only for makes the seed lacks); matcher change asked of WS1. Toyota 'PRIUS' / 'AURIS HYBRID' (EEA misfiles), Tesla 'MODEL' (ambiguous), tail makes under ~1k cars.
  - EEA cannot tell the EQE/EQS saloon from the EQE/EQS SUV: EEA counts go to the saloon models; the SUV models match only names with 'SUV'.
  - Fix found on the way: ~4.5k 'EQ FORFOUR' cars were counted as the fortwo; they now match the new forfour model.
  - Pipeline guard tests updated (8 cases, None → the new model id: e-tron GT, e:Ny1, Ioniq 9, forfour); cross-lane, flagged to WS1.
  - Next release (WS1 nightly) will add the new generations; their release-diff approvals go in a separate gate PR.

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts. -->
