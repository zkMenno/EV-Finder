# T-095 Hero follow-ups from WS3 (T-041, T-082, T-100)
Role: WS2   Lane: apps/web   Wave: 10
Status: done (WS2, 2026-11-17; PR #43)

## Goal
Close three WS2 inbox items unblocked by WS3 merges (#33, #34, #35).

## Acceptance criteria
- [x] `buildListingUrl` applies `slug_overrides` to {MAKE}/{MODEL}, value used as written (La Centrale: Kia Niro EV → `E-NIRO;KIA:NIRO`); test fails on the old code
- [x] Hero /learn links include `batteries-health` (T-082 slug)
- [x] ⓘ tooltips with T-100 glossary ids on hero: profile (base + kerbside layer), home area, keep 8+ years, budget, "Your shortlist", "In winter"; render nothing until the release carries the term

## Handoff notes
- 2026-11-17 WS2: release 1 has none of the nine T-100 terms; checked on a copy of release 1 with the terms from data/taxonomy/glossary_terms.yaml injected (25 ⓘ in the hero, all open with NL text, axe 0 violations at 360/1280 px × light/dark). They appear on the live site with the next release.
- Seen, not mine: chemistry tooltips show EN pros/cons on NL pages (release taxonomy content, WS3).

## Review
