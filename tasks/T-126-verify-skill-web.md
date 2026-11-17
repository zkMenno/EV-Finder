# T-126 `verify` skill for the web app + evidence pack
Role: WS2   Lane: apps/web/.claude/skills/verify/, apps/web/e2e   Wave: process
Status: done (WS2, 2026-11-17; PR #47)

## Goal
Before any commit that changes what users see, the agent runs the real app, walks the flows the diff touches and attaches evidence Menno can judge without reading code.

## Acceptance criteria
- [x] `apps/web/.claude/skills/verify/SKILL.md` (close to the code): how to start the app on the current release and on the fixture, which Playwright helpers to use, how to pick flows from the diff, where to save output.
- [x] `apps/web/e2e/feature-map.yaml`: user-facing features → route, steps, selectors, expected result (hero 4 profiles, Explore filters + URL state, model/generation/variant pages, compare + differences only, Simple/Detailed/Nerd, tooltips, theme, language switch). Used as guide and as grading rubric.
- [x] `pnpm --filter @ev/web verify [--changed]` runs the matching flows and writes `verify-report.md`: step trace, pass/fail per expected result, screenshots 360 px + 1280 px, light + dark, plus one non-EN language. Failures read like "‘See listings’ link missing because used band was null", not "Timeout after 30s".
- [x] The report (or its summary + artifact link) goes into the PR body as the evidence pack; commit stamp `Verified: verify-web` (T-128).
- [x] Stress-test the skill itself: run it 3× on main, no flaky steps; fix or remove any that are.

## Inputs
Article: verify skill near the code, used before committing; E2E gives "hands and eyes"; feature map as rubric. QA START.md walk list (reuse it).

## Handoff notes
- Runner: `apps/web/scripts/verify.mjs` (pure helpers unit-tested in `src/lib/verify-map.test.ts`, which also fails when the map is invalid or a trigger matches no file). Needs a production build; starts its own `next start` on port 3199 (or `--url`). Output in `apps/web/verify-report/` (git-ignored): `verify-report.md`, `summary.md` (PR body), PNGs.
- Map: 14 flows in `apps/web/e2e/feature-map.yaml`. `@name` = data-testid; globs with brackets must be quoted (YAML flow lists). Counts tied to the number of cars are `on: release`.
- Extra checks on every final page: no page error, no raw dictionary key, right `<html lang>`, and no sideways scroll at 360 px (also in the second language).
- Stress test on main (1e0402b, release 1), 3 runs: 13 of 14 pass in every run. The steady failure is a real bug the tool found on its first run: Dutch Nerd hero is 7 px too wide at 360 px (score table words). Fixed in PR fix/hero-a11y-phone, with an e2e test.
- Two flaky causes found in the runner itself and fixed at the cause (no retries): the `lang` check read the old page before the language switch navigated (now waits); phone checks ran only with run 1's screenshots, so a steady failure looked flaky (now counted for every run).
- Not done here: CI artifact upload of the report (the `.github` lane is WS0's; request in WS0 INBOX). Until then the summary goes in the PR body and screenshots are attached by hand.
- Default taken: second language for screenshots is NL (`--lang` to change), because NL is the only complete non-EN dictionary.

## Review
