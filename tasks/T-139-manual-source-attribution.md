# T-139 Manual facts show their own citation, not "Volkswagen Ireland, ID. heat pump page"
Role: builder   Lane: WS1: pipeline/ev_pipeline/manual/, pipeline/ev_pipeline/release/ (+ WS2 for the popover)   Wave: launch fixes (A-36)
Status: todo

## Goal
Every number that comes from a hand-entered, cited fact names that fact's own source on the site (A-36 B2).

## Acceptance criteria
- [ ] The release `sources` list no longer collapses every manual citation into one entry named after the first one (`manual/facts.py` `_source_dict` builds a per-fact name and URL under the shared id `manual`; release 2 shows "Manual entries (hand-entered, cited by URL): Volkswagen Ireland, ID. heat pump page" for 134 values on 40 variants, Tesla and Hyundai included)
- [ ] Either one source id per cited publisher, or the per-fact URL and name travel in the row provenance and the popover shows them (WS2)
- [ ] Release QA check: one source id maps to exactly one name and URL across all facts in a release (blocking)
- [ ] Test with two manual facts from different URLs on different cars
- [ ] Next release carries the fix; fresh review (REVIEW.md from origin/main) passes; `## Review` marks A-36 B2 fixed

## Inputs
audits/A-36-launch-review-2.md B2; `data/releases/2/catalogue.json` `sources[id=manual]`; AGENTS.md data rule 1; REVIEW D7

## Out of scope
New sources.

## Handoff notes

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-36 B2 fixed. -->
