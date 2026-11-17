# T-117 DE, FR, ES and IT drafts for every public string
Role: builder   Lane: WS2 (+ WS3 wording): apps/web/src/i18n/, apps/web tests   Wave: launch fixes (A-35)
Status: todo

## Goal
No English UI strings on DE, FR, ES or IT pages.

## Acceptance criteria
- [ ] Every public key in EN has a DE, FR, ES and IT draft (staff-only keys excepted, as for NL); drafts labelled per D6
- [ ] `i18n.test.ts` checks all six languages for every public key
- [ ] e2e: /de/de and /fr/fr hero, Explore, generation, variant, compare, footer show no English UI strings (allow-list for brand and model names)
- [ ] Glossary terms in all six
- [ ] Verify skill run for the lane; evidence pack in the PR; `Verified:` line on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes; `## Review` line marks the A-35 finding(s) fixed

## Inputs
audits/A-35 B5; REVIEW D6

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-35 B5 fixed. -->
