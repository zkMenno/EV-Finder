# T-020 Web: bidirectional + plug filters, caveat badges, "Power out" block
Role: builder (WS2)   Lane: apps/web   Wave: 6
Status: todo (blocked by T-018, T-019)

## Goal
Ship spec §2.1–2.3: country-aware filters, caveat badges, model-page "Power out" block with used-car checklist.

## Acceptance criteria
- [ ] Filters from spec §2.1 in the URL; V2H/V2G default to "live in selected country"; "include pilots/announced" toggle
- [ ] Conditional rows render as conditions, never a plain ✓ (spec §3.2 rule)
- [ ] Badges read bidi_caveats taxonomy; ⓘ tooltips from glossary terms (v2l, v2h, v2g, ac_bidirectional, dc_bidirectional, iso15118_20, ccs, nacs, chademo)
- [ ] "May be out of date" when the newest source is >90 days old
- [ ] Playwright: switching country DE→FR changes V2G results for Renault 5; VW ID.3 58 kWh does not match V2H, ID.4 77 kWh matches with "needs DC box" + "software ≥3.5"

## Inputs
docs/spec/bidirectional-and-connectors.md

## Out of scope
US Supercharger filter (phase 4), earnings calculator.

## Handoff notes

## Review
