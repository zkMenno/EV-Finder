# T-126 `verify` skill for the web app + evidence pack
Role: WS2   Lane: apps/web/.claude/skills/verify/, apps/web/e2e   Wave: process
Status: todo

## Goal
Before any commit that changes what users see, the agent runs the real app, walks the flows the diff touches and attaches evidence Menno can judge without reading code.

## Acceptance criteria
- [ ] `apps/web/.claude/skills/verify/SKILL.md` (close to the code): how to start the app on the current release and on the fixture, which Playwright helpers to use, how to pick flows from the diff, where to save output.
- [ ] `apps/web/e2e/feature-map.yaml`: user-facing features → route, steps, selectors, expected result (hero 4 profiles, Explore filters + URL state, model/generation/variant pages, compare + differences only, Simple/Detailed/Nerd, tooltips, theme, language switch). Used as guide and as grading rubric.
- [ ] `pnpm --filter @ev/web verify [--changed]` runs the matching flows and writes `verify-report.md`: step trace, pass/fail per expected result, screenshots 360 px + 1280 px, light + dark, plus one non-EN language. Failures read like "‘See listings’ link missing because used band was null", not "Timeout after 30s".
- [ ] The report (or its summary + artifact link) goes into the PR body as the evidence pack; commit stamp `Verified: verify-web` (T-128).
- [ ] Stress-test the skill itself: run it 3× on main, no flaky steps; fix or remove any that are.

## Inputs
Article: verify skill near the code, used before committing; E2E gives "hands and eyes"; feature map as rubric. QA START.md walk list (reuse it).

## Handoff notes

## Review
