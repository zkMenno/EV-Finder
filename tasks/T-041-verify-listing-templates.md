# T-041 Verify "See listings" search templates
Role: WS3   Lane: config/countries   Wave: 6
Status: merged (PR #33); fresh review via QA A-35; earlier note: WS3, 2026-11-15; waits for Menno's tap check

## Goal
Replace guessed marketplace search URLs with checked patterns (Q-028).

## Acceptance criteria
- [ ] Each template opened by hand-checked URL pattern; verified: true + date, or removed
- [x] Filter map (make, model, year, fuel, mileage) noted per site (in config comments, from indexed URLs and Menno's own links)

## Inputs
docs/spec/marketplaces.md, QUESTIONS Q-028.

## Out of scope
Affiliate tags (WS5).

## Handoff notes
2026-11-15, WS3 (https://claude.ai/code/session_01JuyZEW2aV2H7ifmpaT5Pfr).
- No marketplace page was fetched. Patterns were checked against each site's own URLs as indexed by a search engine, and La Centrale against Menno's own saved searches (data/editorial). Evidence is a comment above each template.
- Changed: Marktplaats now searches inside the Auto's category (`/l/auto-s/q/...`, indexed). La Centrale gets name overrides from Menno's links (MEGANE, SCENIC, E-NIRO;KIA:NIRO, MG ZS;MG:ZS, XC40). mobile.de kept as free text (its SEO slugs for names like ID.3 are unknown). Gaspedaal and 2dehands: no evidence found.
- Blocker for La Centrale: `listings.ts` applies slug_overrides to {make}/{model} only; the template uses {MAKE}/{MODEL}. WS2 asked to apply overrides there too.
- One WS2 test expectation updated (`apps/web/src/lib/listings.test.ts`, Marktplaats URL) and `listings.generated.json` regenerated. Vitest src/lib: 244 passed.
- `verified` stays false: the "opened by hand" criterion needs a person. Checklist with 22 tap links: workstreams/WS3/T-041-checklist.md. When Menno says which work, set verified: true + date.
- Known gap: our model slugs ("megane-e-tech-electric") will not match AutoScout24's slugs for long names; per-model overrides for the top 40 need the tap check results first.

## Review
