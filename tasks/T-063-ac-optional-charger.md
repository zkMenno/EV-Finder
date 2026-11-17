# T-063 Optional on-board charger field
Role: coordinator (schema) + WS1 + WS2   Lane: packages/schema, pipeline, apps/web   Wave: proposed by overnight 1
Status: review (WS1 pipeline part, 2026-11-17, 4th WS1 session); web part → WS2

## Goal
Decision 034: `ac_kw` = standard on-board charger; add `ac_kw_optional`. Route source values to the right field (field_sources rules per source), cite both where official sources give both, show "7.4 kW (11 kW optional)" in the web app.

## Acceptance criteria
- [x] Additive schema field `ac_kw_optional` (coordinator; FactField enum entry added by WS1 under WS0's 15 Nov delegation)
- [x] Per-source routing rules in field_sources.yaml; cited standard values win under Decision 028/031 (Decision 046, merge/ac_route.py)
- [ ] Web shows both through `Num` with provenance, EN + NL
- [x] Tests cover it (fixtures, no live network calls): tests/test_t063_ac_optional.py, 12 tests incl. one release build

## Inputs
DECISIONS.md 034, audits/A-06 follow-up table.

## Out of scope
Anything not named above.

## Handoff notes
- 2026-11-17 WS1: pipeline part done (Decision 046). `ac_kw_optional` is a FactField (kW), merges with its own policy row in data/field_sources.yaml, ships in rows with provenance, in the open data bundle, range 2–43 kW, and must be above `ac_kw` (rows drop it, QA flags it).
- Routing is citation-driven only: OpenEV/KilowattApp carry no option signal. No citation for `ac_kw_optional` exists yet, so **release values don't change until WS3 adds them** (verified: `grep -rn ac_kw_optional data/seed data/manual` = 0).
- WS3 ask (INBOX): cite standard + optional for e-208 / e-2008 (7.4 / 11, Stellantis 04-05-2023), Megane EV40 (7.4 / 22), MG4 Standard (6.6 / 11), I-Pace (year split). data/manual works today; seed `cited:` needs `ac_kw_optional` in validate_variants.py SPEC_RANGES (WS3 lane).
- WS2 ask (INBOX): show "7.4 kW (11 kW optional)" through `Num`, EN + NL.
- Dry run on real rows (G-10): 0 citations → 0 moves; check-release on release 1 passes. The fixture build test shows a routed row: option 11 shipped, standard empty, manual fact not shipped.

## Review
