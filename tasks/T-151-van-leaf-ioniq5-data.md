# T-151 Fix ë-SpaceTourer, e-Tourneo Courier, Leaf 62 kWh and Ioniq 5 facelift data
Role: builder   Lane: data/seed, data/manual (WS3)   Wave: launch
Status: todo

## Goal
Four data errors found while building release 3 are fixed with cited maker figures, so no car shows another version's range or battery.

## Acceptance criteria
- [ ] **Citroën ë-SpaceTourer:** `citroen-e-spacetourer-gen1-base` mixes the 50 kWh version with the 75 kWh version's WLTP (341 km, 24.5 kWh/100 km; RDW 'SPACETOURER' 2024, ADEME 'e-SPACE TOURER XL'). Split into a 50 kWh and a 75 kWh variant; old id retired to the variant the existing records belong to (`retired_ids.yaml`).
- [ ] **Ford e-Tourneo Courier:** OpenEV says 51 kWh / 350 km; Ford (media.ford.com, 15.10.2024) says 43 kWh usable and up to 288 km. Cite Ford as manual facts (Decision 068) so OpenEV's values are withheld. The 2026 update (46.8 kWh / 320 km) becomes its own variant only with its own Ford document.
- [ ] **Nissan Leaf 62 kWh:** `nissan-leaf-ze1-62-kwh` (110 kW, OpenEV) and `nissan-leaf-ze1-e-plus-62kwh` (160 kW, TGK) look like one car. Check against a Nissan document: if one car, merge into one variant (power from Nissan), retire the other id; if two, cite what tells them apart. Mind gate #159's release-3 approvals for the 62 kWh row: any cell that moves needs a new approval in its own gate PR.
- [ ] **Hyundai Ioniq 5 facelift (base / AWD):** net 84 kWh (T-140 manual) sits next to gross 77.4 (WS0 guess, unchecked: the pre-facelift figure) and WLTP 507 / 546 from OpenEV, while manual / RDW say 570 for base. Take battery (gross and net) and WLTP per version from a Hyundai document; QA must no longer flag usable > gross. Quote the road-tripper score before / after for these rows.
- [ ] Values from maker documents only (Decision 068); nothing from memory or third-party sites.
- [ ] `sh data/seed/data_qa.sh` and `ev verify --base main` pass; matching regression run (0 unintended moves); coverage line before / after.

## Inputs
WS0 INBOX 2026-11-18 19:14 UTC (batch: data / release 3); Decision 068, 084; T-140; workstreams/WS3/START.md.

## Out of scope
Cargo versions (Decision 084). Matcher changes (WS1 asks go to WS0 INBOX).

## Handoff notes

## Review
