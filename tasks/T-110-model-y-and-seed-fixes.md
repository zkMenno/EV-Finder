# T-110 Model Y LR AWD and other A-35 seed figures from maker data
Role: builder   Lane: WS3: data/seed/, data/manual/   Wave: launch fixes (A-35)
Status: merged (PR #60)

## Goal
Correct the implausible Tesla Model Y Long Range AWD rows (gen1 and Juniper) and the A-35 S8 rows from maker data, so the #1 road-tripper pick is real.

## Acceptance criteria
- [ ] WLTP range, usable battery and consumption for `tesla-model-y-gen1` and `tesla-model-y-juniper` Long Range AWD from Tesla's own pages or homologation documents (archived URL + retrieval date + licence note); gen1 and Juniper no longer share copied values
- [ ] A-35 S8 checked against maker sheets: Ioniq 5 battery by year (58/72.6/77.4/84 kWh), Ioniq 5 N 84 kWh, 77.4 kWh rows get figures, MG4 Standard vs Long Range consumption; XPENG P7/P7+ present if the seed has them
- [ ] Each changed fact has source, date, confidence; pytest green
- [ ] Verify skill run for the lane; evidence pack in the PR; `Verified:` line on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes; `## Review` line marks the A-35 finding(s) fixed

## Inputs
audits/A-35 B4, S8; PR #15 note on the Model Y

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes
- **Model Y cause (WS1 lane, not fixed here):** Open EV Data's own files `src/tesla/model_y/2024|2025/model_y_long_range_awd.json` say `{"cycle": "wltp", "range_km": 719}`. 719 km is the Chinese CLTC figure. Our 11.0 kWh/100 km and 387 km per 20 min DC are derived from it (79 kWh / 719 km), and both generations read the same Open EV record.
- **Fix in this lane:** `data/manual/specs/t110-a35-maker-checks.yaml`. It has EU type-approval values from RDW TGK (CC0, opendata.rdw.nl). Gen1 LR AWD: 533 km, 16.9 kWh/100 km (2021 approvals: 542 km). Juniper LR AWD: 586/568 km, 14.8 kWh/100 km. InsideEVs (2025-02-21) reports Tesla's European figures as the same 586/568. `manual` is blocked (Q-008), so these values don't ship. Under Decision 031 they withhold the lone-source Open EV 719. So until WS1 attaches the RDW versions, the row shows no WLTP figure instead of a wrong one.
- **WS1 follow-ups:** (1) rdw-tgk Y5LD versions at 217 km/h (LR AWD, 533 km) are not attached to `tesla-model-y-gen1-long-range`, and some go to `-performance` (release 1 provenance). (2) Dual-motor approvals have two drivetrain rows (`volgnummeraandrijving` 1/2). On YS5LD ext 44-50, row 2 repeats the gen1 figures (533/169), so the adapter must take drivetrain row 1 or flag the mismatch. (3) Release 1 put YS5MD/YS5MA (dual motor) on `juniper-long-range-rwd`. (4) Derived consumption = net kWh / WLTP is battery-side, while WLTP consumption is at the plug. That accounts for MG4 "Standard Long Range" at 13.6 vs the maker's 16.0. (5) XPENG P7/P7+ have generations in the seed but no rows in release 1 (the '+' tokenisation issue noted in models.yaml).
- **Usable kWh (Model Y):** Tesla publishes no usable capacity; Tesla's pages render their figures client-side and returned nothing to a fetch. web.archive.org is blocked from this environment. Open EV's 79 kWh is left untouched.
- **Ioniq 5:** seed `source_names` joins Open EV "Base"/"AWD" (MY ≤2024) onto the 77.4 kWh seed rows. Open EV labels them 72.6 net / 77.4 gross. Hyundai EU (2022-06-01) gives 77.4 kWh, 507 km, 17.0/17.9 kWh/100 km. Ioniq 5 N: 84.0 kWh (Hyundai technical data 12/2023), against Open EV's 78.
- Not verified here: the effect on a rebuilt release. `ev release` needs staging data (B1, WS1/WS4).

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-35 B4, S8 fixed. -->

WS0 subagent reviews, 2026-11-17: #60 merged; on release 2 (#91 round 2, 42bb9d8) Model Y gen1 LR AWD 533 km, Juniper 586 km, plausibility gate passes. **A-35 B4 fixed.**

Reviewed by QA, 2026-11-17 (A-36, main be2de6f, release 2): pass for B4 (Model Y gen1 LR 533 km / 16.9, Juniper LR AWD 586 km / 14.8). S8 half: Ioniq 5 facelift / N packs and the empty gen1-73kwh-awd row remain (A-36 S7).
