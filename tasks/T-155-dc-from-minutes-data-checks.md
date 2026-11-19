# T-155 DC speed from cited 10–80 % minutes and three data checks
Role: builder   Lane: pipeline/ (WS1)   Wave: launch
Status: review (batch: data T-155, 2026-11-19)

## Goal
Cars with a cited 10–80 % charge time but no curve still get a road-tripper score, and three data oddities from T-151 are checked.

## Acceptance criteria
- [x] **DC from minutes:** when a variant has no charge curve but a cited `dc_minutes_10_80`, derive the DC fields the scores use (dc_avg, km per 10 / 20 min) from it, marked as derived with the source of the minutes. Repro (G-51): Hyundai Ioniq 5 facelift base / AWD, release 4: road-tripper "not enough data" now; expected a score again (it was 66.2 consider / 52.3 fallback with the old car's 220 kW curve). Quote before / after in the PR body, with a D3 dry run on the latest release and its back-test line in qa.json.
- [x] **ë-SpaceTourer:** RDW and ADEME name the 50 and 75 kWh alike, so registry WLTP and TGK consumption spread over both rows. Keep cited WLTP deciding; make sure TGK consumption doesn't mix batteries (split by battery when the record says it, else hold it with a review-queue line).
- [x] **Leaf e+:** TGK gives `wltp_range_km_worst` 410 > best 385. Find out why (later extension?) and either fix the mapping or hold the record; add a QA rule that flags worst > best.
- [x] **Popularity back-test:** qa.json gets a popularity back-test section (Spearman vs the web ranking; #179 had 0.964 as a dry run), per REVIEW D3.
- [x] Same-data rebuild diff (G-43), `ev verify --base main` in the PR body; tests with fixtures.

## Inputs
WS0 INBOX 2026-11-19 03:32 UTC (batch: T-151, asks 1–3) and 03:02 UTC (batch: #171/T-149/T-150, item 3); rule G-51; REVIEW D3.

## Out of scope
T-153's matcher work (another chat). Verify / merge tools (T-158). Schema changes: ask WS0 in the INBOX with the exact field.

## Handoff notes
Batch: data T-155 (2026-11-19). Gate PR #189 (one release-4 approval), data PR follows it. Same staging (refresh 2026-11-19 09:04 UTC) for every number below.
- **DC from minutes** (`derive/rows.py`, `metrics.avg_from_minutes`): no curve and no sourced average but a sourced `dc_minutes_10_80` and a net battery → `dc_avg_10_80_kw = net x 0.7 / minutes x 60`, derived from the minutes' facts (note `MINUTES_NOTE`); km per 10 / 20 min follow with "from the 10-80% time (<source>)". It runs before the generic default curve, so a real time beats the default shape; a curve still beats the time; an average above the published peak still goes to validation.csv. Ioniq 5 facelift base / AWD (Hyundai UK 18 min): dc_avg 196 kW, km/20 min 282.7 / 269.2; road-tripper not-enough-data 61.1 / 49.0 → **73.2 shortlist / 59.0 consider** (release 3 with the old car's 220 kW curve: 66.2 consider / 52.3 fallback). 🟡 Hyundai's "as little as" is a best case on a 350 kW charger (the manual fact says so in its notes); the row's provenance does not mark it as a claim, so 196 kW is optimistic next to curve-based averages (WS0: a `claim` mark on derived DC fields would be a schema/derive follow-up). No other row has minutes without a curve or average.
- **Version guard** (`qa/value_guard.guard_versions`, 5th guard in `run_guards`): (a) a TGK version whose own best-case WLTP is > 15 % from the row's shipped WLTP is another battery or approval family: its consumption and worst-case WLTP go to review (conflicts.csv), never the row; (b) a worst case above the shipped best case goes to review. ë-SpaceTourer: on today's staging the matcher already puts 50 kWh versions (238 / 234 km) on the 50 row and 75 kWh (339 / 370 km) on the 75 row, so nothing moved there; the guard now holds any cross-battery version that lands on the wrong row (test). Leaf e+: TGK's 2022 extension (e9*2007/46*6537*08, A07) has best 449 / worst 410; the row ships 385 from the 2019–2021 versions, so 410 came from another version: held (and its 14.7 consumption). Leaf 40 kWh had the same bug (worst 287 from the 2022 A06 version, best 300, next to 270): held by (b). 13 rows change (list in the data PR); 1 blocking diff line (Taycan Turbo S consumption 20.6 → 22.3) approved in #189.
- **QA rule** `wltp_worst_gt_best` in `qa/checks.impossible_values` (outliers check, report only): 0 hits on the branch build; main's build would flag Leaf e+ (410 > 385) and Leaf 40 kWh (287 > 270).
- **Popularity back-test** (`backtest/popularity.py`, qa.json `backtest_popularity`, qa.md line, listed by `ev verify`): Spearman of `generations[].popularity` vs the web build's ranking (popularity.ts on top40.yaml, ported) = **0.953** over 87 generations, median rank move 4, top-10 overlap 9/10. Report only, no gate. Biggest moves are new cars (Elroq 13 vs 49, EV3 16 vs 47): the release counts the whole fleet, top40.yaml only RDW first admissions 2018–2024.
- Review round 1 (#192 at 1b7e475): PASS; fixed should-fix 2 (guard reads a version's own best case from the untouched facts). Deferred: claim mark on minutes-derived DC (should-fix 1), minutes-above-peak fallback to the default curve (nit 4), popularity port half-rounding / id filter (nit 5), verify changed-rules globs (nit 6, T-158).
- For WS1 / T-153 (matcher, not touched here): the guard's review rows show versions of other trims landing on a row, e.g. Ioniq 5 N gets 530–570 km versions, e-tron 55 gets Q8 e-tron versions (629 km), Inster 49 gets a 293 km (42 kWh) version, Taycan gen1 rows get facelift versions (665–676 km). They are now held, not shipped; the matching fix is T-153's lane.

## Review
