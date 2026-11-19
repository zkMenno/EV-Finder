# T-151 Fix ë-SpaceTourer, e-Tourneo Courier, Leaf 62 kWh and Ioniq 5 facelift data
Role: builder   Lane: data/seed, data/manual (WS3)   Wave: launch
Status: review (batch: T-151, claimed 2026-11-19; gate PR #177 + data PR)

## Goal
Four data errors found while building release 3 are fixed with cited maker figures, so no car shows another version's range or battery.

## Acceptance criteria
- [x] **Citroën ë-SpaceTourer:** `citroen-e-spacetourer-gen1-base` mixes the 50 kWh version with the 75 kWh version's WLTP (341 km, 24.5 kWh/100 km; RDW 'SPACETOURER' 2024, ADEME 'e-SPACE TOURER XL'). Split into a 50 kWh and a 75 kWh variant; old id retired to the variant the existing records belong to (`retired_ids.yaml`).
- [x] **Ford e-Tourneo Courier:** OpenEV says 51 kWh / 350 km; Ford (media.ford.com, 15.10.2024) says 43 kWh usable and up to 288 km. Cite Ford as manual facts (Decision 068) so OpenEV's values are withheld. The 2026 update (46.8 kWh / 320 km) becomes its own variant only with its own Ford document.
- [x] **Nissan Leaf 62 kWh:** `nissan-leaf-ze1-62-kwh` (110 kW, OpenEV) and `nissan-leaf-ze1-e-plus-62kwh` (160 kW, TGK) look like one car. Check against a Nissan document: if one car, merge into one variant (power from Nissan), retire the other id; if two, cite what tells them apart. Mind gate #159's release-3 approvals for the 62 kWh row: any cell that moves needs a new approval in its own gate PR.
- [x] **Hyundai Ioniq 5 facelift (base / AWD):** net 84 kWh (T-140 manual) sits next to gross 77.4 (WS0 guess, unchecked: the pre-facelift figure) and WLTP 507 / 546 from OpenEV, while manual / RDW say 570 for base. Take battery (gross and net) and WLTP per version from a Hyundai document; QA must no longer flag usable > gross. Quote the road-tripper score before / after for these rows.
- [x] Values from maker documents only (Decision 068); nothing from memory or third-party sites.
- [x] `sh data/seed/data_qa.sh` and `ev verify --base main` pass; matching regression run (0 unintended moves); coverage line before / after.

## Inputs
WS0 INBOX 2026-11-18 19:14 UTC (batch: data / release 3); Decision 068, 084; T-140; workstreams/WS3/START.md.

## Out of scope
Cargo versions (Decision 084). Matcher changes (WS1 asks go to WS0 INBOX).

## Handoff notes
2026-11-19, batch: T-151 (https://claude.ai/code/session_01JuyZEWYDTfurC8UVp9w9ew). Facts in `data/manual/specs/t151-van-leaf-ioniq5.yaml` (source `manual`, Decision 068); seed rows in `data/seed/variants.yaml`; approvals in gate PR #177 (release 4).
- **ë-SpaceTourer:** seed rows `citroen-e-spacetourer-gen1-50kwh` (46.3 kWh usable, 230 km) and `-75kwh` (68 kWh, 330 km): Citroën FR 12.06.2020 + UK 18.03.2024. `-base` retired to `-50kwh` (its OpenEV "Base" records are 46 kWh). New rows `stellantis-midsize-van` (platform name not read from a maker page, so not "EMP2") and packs `stellantis-van-50` / `-75`. RDW / ADEME / TGK name both batteries alike, so their WLTP spreads over both rows; the cited figure decides on each (12 / 38 conflicting values set aside). Launch WLTP cited; 2024 update figures (UK 139 mi, DE up to 350 km, RDW 341) in notes. Open: 75 kWh row has no DC peak (no maker figure read), so daily-driver = not-enough-data; consumption comes from TGK versions that may mix batteries.
- **E-Tourneo Courier:** Ford 15.10.2024: 43 kWh usable, 288 km, on the OpenEV-made id `ford-e-tourneo-courier-gen1-base`. The 2026 update (Ford: 46 kWh / 334 km, Feb 2026 news) is not a row yet: needs its own Ford data sheet and a year split.
- **Leaf 62 kWh: one car.** Nissan sells the 62 kWh battery only with the 160 kW e+ motor (Nissan Europe 09.01.2019: "160 kW (217 PS)", 385 km; Nissan USA 2025 press kit: 110 kW only with 40 kWh). OpenEV "62 kWh" joins `nissan-leaf-ze1-e-plus-62kwh` via `source_names`; `nissan-leaf-ze1-62-kwh` retired to it. The release-3 EPA matrix approval (&leaf62) is carried by #177 for the e+ row. Left as is: net battery 62 (KilowattApp) = Nissan's gross figure; TGK adds `wltp_range_km_worst` 410 > best 385 (a later-extension version; WS1 to check).
- **Ioniq 5 facelift 84 kWh:** OpenEV MY2025 "Base" / "AWD" are the pre-facelift car (72.6 / 77.4 kWh, 507 km, 220 kW): `source_holds` entry; the two ids are seed rows now (no URL change), linked to `egmp-84`. Hyundai gives one capacity figure, 84 kWh, which Hyundai CZ calls usable: no separate gross entered (QA `usable_gt_gross` no longer fires). Base WLTP 507 -> 570 (T-140 cite now wins; RDW F5E62 left-over stock was outvoting it with OpenEV). Power cited (168 / 239 kW), DC 10-80 = 18 min (Hyundai UK 18.07.2024). The old car's DC peak/curve, weight, EPA clear.
- **Road-tripper score (release 3 -> branch):** Ioniq 5 facelift base 66.2 consider -> 61.1 not-enough-data; AWD 52.3 fallback -> 49.0 not-enough-data (no facelift DC curve; needs WS1 to derive DC speed from a cited 10-80 time, INBOX). Leaf e+ 14.1 -> 20.1 fallback; old `-62-kwh` row was 0 ruled-out. E-Tourneo Courier 0 ruled-out (unchanged). ë-SpaceTourer: base 0 ruled-out -> 50 kWh 0 ruled-out / 75 kWh 0 ruled-out.
- **Evidence:** `ev verify --base main` with #177's file: 0 blocking, 186 approved, 15 retired; 1750 tests pass (after merging main); data_qa.sh 4/4; EPA proxy consumption 6.37 %, range 6.99 % (main 6.37 / 6.99). Models.yaml unchanged (0 model-id moves); built rows differ from main only on the 4 cars + Ioniq 5 N (gets `egmp-84` by the pack rule). Coverage (`ev variants propose`, fresh EEA): groups we have 228 -> 230, % EU registrations on groups we have 67.7 -> 67.9.
- **Cross-lane:** three maker press hosts added to `manual` cited_hosts in `data/sources.yaml` (WS1 file): www.media.stellantis.com, media.ford.com, europe.nissannews.com.

## Review
