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

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts. -->
