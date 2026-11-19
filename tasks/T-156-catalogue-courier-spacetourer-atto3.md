# T-156 Small catalogue fixes: e-Tourneo Courier 2026, ë-SpaceTourer 75 DC, e-GMP 84 pack, BYD Atto 3 photo
Role: builder   Lane: data/seed, data/manual, data/images (WS3)   Wave: launch
Status: done (gate #190 merged 8abbbdf, data #191; batch: catalogue T-160, https://claude.ai/code/session_01JuyZEVd9J7FfZJTPaQQmnc, 2026-11-19)

## Goal
Four small gaps left by T-151 and T-149 are closed with cited maker or file-page facts.

## Acceptance criteria
- [x] **Ford e-Tourneo Courier 2026** (46.8 kWh / 320 km): its own variant, split by year, only with a Ford data sheet.
- [x] **Citroën ë-SpaceTourer 75 kWh:** DC peak from a Stellantis document.
- [x] **`egmp-84` pack row:** Hyundai CZ calls 84 kWh usable while the pack row says gross; fix the pack row from a Hyundai document (gross and usable).
- [x] **BYD Atto 3 photo:** `byd-atto-3-gen1`'s file page has only a user template; read `User:VulcanSphere/CC-BY-photos` and record the licence it states in photos.yaml, or pick another photo if it doesn't state one. The next release must keep a photo for it.
- [x] **If time allows:** a cited maker list price (any launch country) for Lucid Gravity, Lotus Eletre or Porsche Macan Electric, so T-152's 2× rule can drop them from cheap-budget fill-ins.
- [x] Maker documents only (Decision 068 / 087); `sh data/seed/data_qa.sh` and `ev verify --base main` pass; any approval in its own gate PR, scoped to a release not yet built (G-54).

## Inputs
WS0 INBOX 2026-11-19 03:32 UTC (batch: T-151, "Next for WS3") and 03:02 UTC (item 4); T-151 Handoff notes.

## Out of scope
T-154's list (another chat). Matcher changes (T-153 / T-155).

## Handoff notes
2026-11-19, batch: catalogue T-156. Data PR on branch `t-156-courier-spacetourer-atto3`, gate PR **#190** (`t-156-gate`). Both draft, **not reviewed, not merged**: Menno paused building at 09:30 UTC, 30 min after this batch started. On resume: fresh review of both, merge #190 first, then the data PR (check G-54: if release 4 is already published, move the approval to the next unbuilt release).
- **Courier 2026:** new seed row `ford-e-tourneo-courier-gen1-46kwh` (years 2026 onward), with its own link, platform `ford-courier-bev` and pack `ford-courier-46` (all not-disclosed except Ford's 46 kWh usable). Ford of Europe 16.02.2026 (fromtheroad.ford.com, Ford HQ): 46 kWh usable, up to 320 km WLTP, 10–80 % in 26 min on a 100 kW charger (`data/manual/specs/t156-courier-spacetourer.yaml`). Ford says **46**, not 46.8 (46.8 is only on third-party sites, not used). Power not restated by Ford for the update, left out. One-line cross-lane edit: `data/sources.yaml` manual `cited_hosts` + `www.fromtheroad.ford.com`, `ir.lucidmotors.com` (own line, so it does not collide with T-154's edit of the line above).
- **Courier side effect (gate #190):** RDW's per-year "FORD TOURNEO COURIER 2026" record (7 cars, NL price €42,048) has no battery / power / WLTP evidence, so with two rows it is left unplaced; Base loses that NL price and its used-price model. Approved as a correction (the price was the 2026 car's). WS1 ask: place such a record by year when only years separate the rows.
- **ë-SpaceTourer 75:** `dc_peak_kw` 100 from Citroën's order-opening press kit (Stellantis media, 02.09.2020): "Up to 100 kW – … a 75 kWh battery in 45 minutes."
- **egmp-84:** Hyundai's own documents disagree on the label. Hyundai Austria technical data (05/2025): "Nennkapazität 84", "Nennspannung 697 V"; Hyundai Australia 2026 spec sheet: 84 kWh, 697 V; Hyundai Czech (15.08.2024): 84 kWh "usable". No Hyundai document gives a separate usable figure. Pack row: gross 84 (nominal), usable not-disclosed, nominal_v 697 (was not-disclosed); Ioniq 5 facelift links now 697 V / 800v class. The variant fact `battery_kwh_net` 84 (CZ) stays but drops to confidence low, with the reason.
- **BYD Atto 3 photo:** the user template `User:VulcanSphere/CC-BY-photos` is `{{self|attribution=© VulcanSphere / Wikimedia Commons / CC BY 4.0|cc-by-4.0}}` (read with action=raw). photos.yaml now carries `licence_template: self|cc-by-4.0`, checked 2026-11-19, and the author's own credit line "© VulcanSphere / Wikimedia Commons / CC BY 4.0". `ev images check`: 0 problems.
- **List prices:** Lucid Gravity, Lucid's press release 08.09.2025 (ir.lucidmotors.com): Grand Touring €116,900 DE (medium), Touring €99,900 DE (low: announced before it could be ordered). Not done: Lotus Eletre (Lotus's 2022 price page now redirects to a news index) and Porsche Macan Electric (no euro price on the German Porsche releases read; Swiss release gives CHF only).
- **Evidence:** `sh data/seed/data_qa.sh` all four pass. `ev verify --base origin/main --skip-tests` on staging recorded 2026-11-19: without #190 2 blocking (the two Courier Base lines); with #190's file applied **0 blocking, 387 approved, 21 retired, 11594 review**, variants 399. Built rows: Courier 46 kWh 46 / 320 km / 26 min / real 256 km; Base 43 / 288; SpaceTourer 75 kWh DC peak 100 (was none); Gravity Touring / GT price DE 99,900 / 116,900. Pytest not run (no pipeline code changed).

- **Side effect, said here per review should-fix (batch catalogue T-160, 2026-11-19):** with `egmp-84` at 697 V the Ioniq 5 facelift rows are class 800v, so the 800v band thresholds apply (`data/editorial/shortlist_rules.yaml:33`, consider >= 63 vs default 50): against main the AWD's 6 road-tripper bands go consider -> fallback. Same as release 3; the rule working as written. Pre-existing follow-up: the Ioniq 5 facelift still ships `battery_kwh_net` 84 although Hyundai AT calls 84 nominal (now low confidence).
- **Numbers after merging main (8abbbdf, #190 in):** `ev verify --base origin/main --skip-tests`, staging 2026-11-19: 0 blocking, 372 approved, 21 retired, 11610 review, variants 399 (prev 375).

## Review
- 2026-11-19, fresh subagent review (batch catalogue T-160): R0–R3, D1, D2, D4. #190 PASS WITH NITS (3749b3e; merged as d6ead5b after a main merge, CI green, behind_by 0). #191 FAIL R2 on PR-body numbers only (868d7f2); fixed by pasting the refreshed Numbers block (verify --pr-body pass on the new head). Comments: PR #190 issuecomment-7010499468, PR #191 issuecomment-7010500003.
