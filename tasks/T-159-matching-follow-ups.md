# T-159 Matching follow-ups: motor-count ties, other trims' TGK versions, year-only splits
Role: builder   Lane: pipeline/ (WS1)   Wave: launch
Status: doing (batch: data T-159, https://claude.ai/code/session_01JuyZEXeG7iyPafXic4NHT3, 2026-11-19)

## Goal
TGK versions land on the right trim: ties split by motor count, other trims' versions stop landing on a row, and rows that differ only by year get their per-year RDW records.

## Acceptance criteria
- [ ] **Ties by motor count / drivetrain** (T-154 ask): extend `pipeline/ev_pipeline/match/tgk_split.yaml` so these resolve, or stay tied with a reason: Kia EV3 LR vs AWD, EV6 facelift RWD vs AWD, MINI Countryman E vs SE ALL4, Hyundai Inster 42 vs 49. Repro (G-51): tie count for the four before / after on the current seed.
- [ ] **Other trims' versions** (T-155 ask 2, now held by T-155's guard): Ioniq 5 N gets 530–570 km versions, e-tron 55 gets Q8 e-tron 629 km, Inster 49 a 42 kWh 293 km version, Taycan gen1 facelift 665–676 km versions. Fix the matching so they land on their own trim (or no row); the guard's held count drops.
- [ ] **Year-only splits** (T-156 ask): an RDW per-year record is placed by year when only years separate two rows (e.g. the 2026 e-Tourneo Courier record, unplaced now).
- [ ] **Model Y gen1 Performance:** its 507 km WLTP comes from the RDW 2021 aggregate (T-153 Handoff notes); place or drop that value so the Performance row shows its own figure.
- [ ] **Fingerprint** (T-153 follow-up 6): `ev variants propose` counts a group as `have` when every version is on its right row, so Model Y / e-208 / Corsa leave `several`. Only if time allows; else leave it in Handoff notes.
- [ ] Split into two PRs if large (ties + other trims / year splits + Model Y + fingerprint). Same-data rebuild diff (G-43), queue numbers before / after (tie, several, have), `ev verify --base main` in the PR body; tests with fixtures.

## Inputs
WS0 INBOX 2026-11-19 09:15 (batch: catalogue T-154, ask 1), 10:38 (batch: data T-155, ask 2), 10:45 (batch: catalogue T-156, WS1 ask), 10:54 (batch: data T-153, WS1 follow-ups); T-153 and T-155 Handoff notes.

## Out of scope
The Elroq alias (T-160, WS3). Version-rule change (T-161). `ev verify` tools (T-158).

## Handoff notes

## Review
