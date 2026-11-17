# T-119 Serve /es/es and /it/it
Role: builder   Lane: WS2: apps/web/ (routing, country picker)   Wave: launch fixes (A-35)
Status: todo

## Goal
Spain and Italy are selectable and served in their own language (Decision 066).

## Acceptance criteria
- [ ] `countries.generated.json` includes es and it; routes /es/es and /it/it build; the country picker lists them; hreflang + sitemap include them
- [ ] Spanish and Italian appear only for Spain and Italy (no /nl/es style routes)
- [ ] Hero walk for ES and IT at two budgets; axe clean
- [ ] Depends on T-118 config and T-117 strings
- [ ] Verify skill run for the lane; evidence pack in the PR; `Verified:` line on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes; `## Review` line marks the A-35 finding(s) fixed

## Inputs
Decision 066; audits/A-35 B5

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-35 B5 fixed. -->
