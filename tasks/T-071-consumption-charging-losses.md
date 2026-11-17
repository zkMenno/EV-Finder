# T-071 Derived WLTP consumption includes charging losses
Role: builder   Lane: pipeline/ev_pipeline/derive   Wave: 9 (launch data fix)
Status: review (WS1 5th chat, 2026-11-17)

## Goal
When no official WLTP consumption exists, our estimate must be on the same basis as the official figure (wall, incl. charging losses), not battery basis.

## Acceptance criteria
- [x] `consumption_estimate` = net kWh / WLTP range x 100 x a calibrated charging-loss factor; the factor and its fit are documented next to it
- [x] qa.json `profile_fields.consumption_kwh_100km.estimate_vs_official_wltp`: our estimate vs official WLTP on rows that have both (n, median abs %, mean signed %, worst 5)
- [x] Dry run on release 1 and an out-of-sample check in the PR
- [x] Tests with fixtures; no network

## Inputs
WS2 INBOX 2026-11-17 10:02 (Model Y LR 11.0, Ioniq 6 53 kWh 10.1); audits/A-32 (WLTP consumption −11 % median on 45); Decision 041 (wall x 0.88 = battery).

## Out of scope
Wrong WLTP inputs (Model Y LR 719 km from OpenEV: fixed by T-110 / PR #60 with type-approval figures); the DC km basis question (T-070).

## Handoff notes
- Root cause: 58 of 226 rows in release 1 had no official consumption; we derived it as net kWh / WLTP km, which is battery basis. Official WLTP is measured at the wall. On the 138 rows that have an official figure, a real WLTP and a net capacity, official / battery-basis = **1.159 median** (IQR 1.13–1.20). Factor set to 1.16 (`metrics.WALL_PER_BATTERY_WLTP`, Decision 047).
- Back-test on release 1 (n 138): median abs error **13.8 % → 3.1 %**, mean signed −13.9 % → −0.2 %. Out of sample (factor fitted on half the models, tested on the other half, 200 splits): median abs error 3.2 % (2.4–4.6).
- Effect: the 58 derived rows rise by 16 %; downstream `consumption_motorway_kwh_100km` (x 1.30), `ac_km_per_h` and `dc_km_per_10/20min` move with them. These rows now sit on the same basis as the 140 rows with an official figure, which already worked this way.
- Lowest after the fix: Ioniq 6 53 kWh 11.7 (WLTP estimated from EPA id 48363: 🔴 the EPA match may be the long-range car; WS3 to cite the type approval), Model Y LR / Juniper 12.8 (bad OpenEV WLTP 719 km: #60 replaces it with RDW TGK 16.9 / 14.8).
- Release diff (T-123): these 58 rows show as changes in release 2; they need a release-scoped approval with the rest of A-32.
- Pre-existing, not changed here: DC km per 10/20 min divides battery-side energy by a wall-basis motorway figure on all rows (≈ 12–14 % low). T-070 moves DC km to the matrix's battery-basis motorway cell.

## Review
