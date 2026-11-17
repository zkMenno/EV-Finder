# T-091 Parked features behind flags (off by default)
Role: WS2   Lane: apps/web   Wave: 10
Status: done (merged by WS2 with Menno's OK, 2026-11-17)

## Goal
Decision 051: built work for parked features stays in the code but is switched off by default (WS2 START.md §3).

## Acceptance criteria
- [x] Off by default: charging link-out block (`CHARGING_LINKS`), /charging page (`CHARGING_PAGES`), known issues (`KNOWN_ISSUES`), registration counts (`REGISTRATIONS`), rankings /top + nav link (`RANKINGS`); Trip fit stays behind `TRIP_FIT`
- [x] `PARKED=1` turns them all on; parked pages leave the sitemap when off
- [x] Nothing deleted; e2e for parked features skip unless `E2E_PARKED=1` (build with `PARKED=1`), and a new e2e proves they are hidden by default
- [x] Both modes green locally (default: 49 + skips; PARKED: 78)

## Out of scope
Bidirectional UI (none built in the web app yet); /learn articles beyond the three launch ones (WS3's content/learn/index.yaml).

## Handoff notes
- 2026-11-15 WS2: flags in `src/config/features.ts` (`parkedEnabled`). Static pages read them at build time, so a flag change needs a rebuild (same as a new release). Components return nothing when off (`ChargingLinks`, `KnownIssues`); registrations rows are skipped at the call sites; /charging and /top call `notFound()`, `/top/[list]` builds no params. Coverage of parked code now runs only in an E2E_PARKED build; WS0 may add a nightly CI job with `PARKED=1` + `E2E_PARKED=1` (`.github/` is WS0's).

## Review
- Reviewed by QA, 2026-11-17 (main @ d086d49, REVIEW.md draft R0–R3 + triggered D items): pass — /top, /charging, known issues, charging links and the registrations block are off in a default build (parked.spec + curl). The price-mode toggle is not covered (A-35 S4).
