# T-140 Catalogue gaps from A-36 S7: Ioniq 5 packs and figures, XPENG P7 / P7+ rows
Role: builder   Lane: WS3: data/seed/, data/manual/   Wave: launch fixes (A-36)
Status: review (WS3, 2026-11-17)

## Goal
The rows QA flagged in release 2 (audits/A-36 S7, A-35 S8 remainder) carry cited maker or type-approval figures, and XPENG P7 / P7+ get rows.

## Acceptance criteria
- [x] Ioniq 5 facelift base / AWD: 84 kWh usable (Hyundai), WLTP and consumption from the EU type approval (RDW TGK), replacing Open EV Data's 72.6 kWh and the pre-facelift 507 km
- [x] Ioniq 5 N: the T-110 84 kWh fact and the T-112 price point at the live id `hyundai-ioniq-5-facelift-n` (they used the retired `hyundai-ioniq-5-gen1-n`, so neither applied)
- [x] `hyundai-ioniq-5-gen1-73kwh-awd` gets WLTP + consumption; 72.6 kWh RWD gets the type-approval figures (release had 451 km from one registration value)
- [x] Seed variants: Ioniq 5 facelift 63 kWh RWD, XPENG P7 RWD Long Range + AWD Performance, P7+ RWD Long Range + AWD Performance, with cited figures (no battery for P7+: sources disagree)
- [x] Every manual fact's variant id exists in release 2 or in the seed (script check, evidence in the PR)
- [x] validate_seed, validate_variants, `ev manual check` pass; verify-pipeline run (evidence in the PR)
- [ ] Fresh review (REVIEW.md from origin/main) passes; `## Review` marks A-36 S7 fixed

## Inputs
audits/A-36-launch-review-2.md S7; A-35 S8; Decisions 057, 068

## Out of scope
Matching fixes in the pipeline (WS1 INBOX): P7 / P7+ name key, facelift rows picking up 2025 F5E62 registrations.

## Handoff notes
- Cross-lane one line in `data/sources.yaml` (WS1): `a-cdn.xpeng.com/www/public/static/pdf/` added to `manual` cited_hosts (XPENG's own spec sheet). Flagged in WS1 INBOX.
- P7+ battery left out: XPENG's preliminary DE sheet (09/2025) says 76.8 kWh net, press says 74.9 kWh (gross or net, they disagree). P7+ Standard Range has no row: not in the Dutch register yet, no maker document found.
- 63 kWh battery is `low`: Hyundai says "63 kWh" without "usable".

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-36 S7 fixed. -->
