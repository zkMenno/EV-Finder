# T-155 DC speed from cited 10–80 % minutes, three data checks, verify and merge tools
Role: builder   Lane: pipeline/ (WS1); scripts/merge_ready.sh (WS0-owned, built here, flag it)   Wave: launch
Status: todo

## Goal
Cars with a cited 10–80 % charge time but no curve still get a road-tripper score, three data oddities from T-151 are checked, and the merge / verify tools stop the misses the 19 Nov batches hit.

## Acceptance criteria
- [ ] **DC from minutes:** when a variant has no charge curve but a cited `dc_minutes_10_80`, derive the DC fields the scores use (dc_avg, km per 10 / 20 min) from it, marked as derived with the source of the minutes. Repro (G-51): Hyundai Ioniq 5 facelift base / AWD, release 4: road-tripper "not enough data" now; expected a score again (it was 66.2 consider / 52.3 fallback with the old car's 220 kW curve). Quote before / after in the PR body.
- [ ] **ë-SpaceTourer:** RDW and ADEME name the 50 and 75 kWh alike, so registry WLTP and TGK consumption spread over both rows. Keep cited WLTP deciding; make sure TGK consumption doesn't mix batteries (split by battery when the record says it, else hold it with a review-queue line).
- [ ] **Leaf e+:** TGK gives `wltp_range_km_worst` 410 > best 385. Find out why (later extension?) and either fix the mapping or hold the record; add a QA rule that flags worst > best.
- [ ] **Popularity back-test:** qa.json gets a popularity back-test section (Spearman vs the web ranking; #179 had 0.964 as a dry run), per REVIEW D3.
- [ ] **G-53:** `ev verify --keep <dir>` keeps its scratch build.
- [ ] **G-54:** approved_changes validation warns when an entry's `release` is ≤ the latest published release.
- [ ] **G-52:** `scripts/merge_ready.sh <pr>` exits non-zero when the PR branch is behind main (`compare main...head`, behind_by > 0) or CI on the head isn't green. Merge batches run it as its own step. Cross-lane (WS0 file), flagged in the PR.
- [ ] Same-data rebuild diff (G-43), `ev verify --base main` in the PR body; tests with fixtures.

## Inputs
WS0 INBOX 2026-11-19 03:32 UTC (batch: T-151, asks 1–3, retro 4) and 03:02 UTC (batch: #171/T-149/T-150, item 3); rules G-51–G-54; REVIEW D3.

## Out of scope
T-153's matcher work (another chat). Schema changes: ask WS0 in the INBOX with the exact field.

## Handoff notes

## Review
