# T-156 Small catalogue fixes: e-Tourneo Courier 2026, ë-SpaceTourer 75 DC, e-GMP 84 pack, BYD Atto 3 photo
Role: builder   Lane: data/seed, data/manual, data/images (WS3)   Wave: launch
Status: doing (batch: catalogue T-156, https://claude.ai/code/session_01JuyZEWYDTfurC8UVp9w9ew, 2026-11-19)

## Goal
Four small gaps left by T-151 and T-149 are closed with cited maker or file-page facts.

## Acceptance criteria
- [ ] **Ford e-Tourneo Courier 2026** (46.8 kWh / 320 km): its own variant, split by year, only with a Ford data sheet.
- [ ] **Citroën ë-SpaceTourer 75 kWh:** DC peak from a Stellantis document.
- [ ] **`egmp-84` pack row:** Hyundai CZ calls 84 kWh usable while the pack row says gross; fix the pack row from a Hyundai document (gross and usable).
- [ ] **BYD Atto 3 photo:** `byd-atto-3-gen1`'s file page has only a user template; read `User:VulcanSphere/CC-BY-photos` and record the licence it states in photos.yaml, or pick another photo if it doesn't state one. The next release must keep a photo for it.
- [ ] **If time allows:** a cited maker list price (any launch country) for Lucid Gravity, Lotus Eletre or Porsche Macan Electric, so T-152's 2× rule can drop them from cheap-budget fill-ins.
- [ ] Maker documents only (Decision 068 / 087); `sh data/seed/data_qa.sh` and `ev verify --base main` pass; any approval in its own gate PR, scoped to a release not yet built (G-54).

## Inputs
WS0 INBOX 2026-11-19 03:32 UTC (batch: T-151, "Next for WS3") and 03:02 UTC (item 4); T-151 Handoff notes.

## Out of scope
T-154's list (another chat). Matcher changes (T-153 / T-155).

## Handoff notes

## Review
