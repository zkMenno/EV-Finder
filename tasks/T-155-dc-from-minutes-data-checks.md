# T-155 DC speed from cited 10–80 % minutes and three data checks
Role: builder   Lane: pipeline/ (WS1)   Wave: launch
Status: todo

## Goal
Cars with a cited 10–80 % charge time but no curve still get a road-tripper score, and three data oddities from T-151 are checked.

## Acceptance criteria
- [ ] **DC from minutes:** when a variant has no charge curve but a cited `dc_minutes_10_80`, derive the DC fields the scores use (dc_avg, km per 10 / 20 min) from it, marked as derived with the source of the minutes. Repro (G-51): Hyundai Ioniq 5 facelift base / AWD, release 4: road-tripper "not enough data" now; expected a score again (it was 66.2 consider / 52.3 fallback with the old car's 220 kW curve). Quote before / after in the PR body, with a D3 dry run on the latest release and its back-test line in qa.json.
- [ ] **ë-SpaceTourer:** RDW and ADEME name the 50 and 75 kWh alike, so registry WLTP and TGK consumption spread over both rows. Keep cited WLTP deciding; make sure TGK consumption doesn't mix batteries (split by battery when the record says it, else hold it with a review-queue line).
- [ ] **Leaf e+:** TGK gives `wltp_range_km_worst` 410 > best 385. Find out why (later extension?) and either fix the mapping or hold the record; add a QA rule that flags worst > best.
- [ ] **Popularity back-test:** qa.json gets a popularity back-test section (Spearman vs the web ranking; #179 had 0.964 as a dry run), per REVIEW D3.
- [ ] Same-data rebuild diff (G-43), `ev verify --base main` in the PR body; tests with fixtures.

## Inputs
WS0 INBOX 2026-11-19 03:32 UTC (batch: T-151, asks 1–3) and 03:02 UTC (batch: #171/T-149/T-150, item 3); rule G-51; REVIEW D3.

## Out of scope
T-153's matcher work (another chat). Verify / merge tools (T-158). Schema changes: ask WS0 in the INBOX with the exact field.

## Handoff notes

## Review
