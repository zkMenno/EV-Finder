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

- 2026-11-18 WS3 5th batch chat (https://claude.ai/code/session_01JuyZEVcqV3ZZHZbnBVTP8x), branch `t-136c-extra-models` (stacked on #129; merge after it): **stretch done**. Models 134 → 198, generations 160 → 223 (main: 99 / 122), 20 new makes. EU BEV registrations matched **95.56 % → 98.51 %** (EEA 2010-2025, 9,079,365 cars, R-41 coverage.py logic + the pipeline matcher).
  - From the 2nd chat's branch: 50 models (its list minus Leapmotor T03, still WS1's OpenEV market filter, and its 3 duplicate ids: #129's jeep-avenger, opel-frontera, renault-twingo stay), its alias fixes on 13 existing models, and its guard-test updates (e:Ny1, Ioniq 9, forfour). #129's e-tron GT (one generation) and e-up! (one generation, Decision 057 marker) stay as they are.
  - Vans (Menno, WS0 INBOX 10:30, M1 passenger versions in, cargo out): 14 new models: eVito Tourer, EQT / eCitan Tourer, ë-SpaceTourer, e-Traveller, Combo-e Life, Zafira-e Life, Proace Verso, Proace City Verso, E-Doblò, E-Ulysse, e-NV200 Evalia, Kangoo E-Tech, E-Tourneo Custom, E-Tourneo Courier (~62k EU cars). Same year rule and evidence notes as #129. Bare names JUMPY / EXPERT / VIVARO / PROACE count as the passenger Combi because every register source here is passenger-only (EEA CO2 cars = M1; RDW filtered to `Personenauto`). Proace City Verso, E-Doblò, E-Ulysse end 2025 by the rule (no RDW 2026 cars); may still be on sale.
  - Guards added: BYD Seal `name_excludes: [DM, DM-i, DMI]` (RDW 'BYD SEAL U DM', 1 car, a plug-in hybrid, landed on the Seal); Zafira matched on ZAFIRA LIFE / ZAFIRA-E only (RDW 2012 'ZAFIRA TOURER' conversion).
  - Matching regression (main seed vs branch, every staging record of 9 sources + every EEA name): 85 records change model, **all** smart EQ forfour moving off the fortwo onto the new forfour model (intended). Everything else that matched before matches the same model.
  - Remaining big gaps: Leapmotor T03 (20k, WS1 market filter), SEAT make (21k: Mii + Cupra filed as SEAT, WS1 KBA alias clash), Tesla 'MODEL' (5k, ambiguous), Toyota hybrid misfiles in EEA (PRIUS, AURIS HYBRID, CT200H; not EVs).

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts. -->
