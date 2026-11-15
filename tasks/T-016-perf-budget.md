# T-016 Perf budget
Role: coordinator   Lane: audits/   Wave: 4
Status: review (reviewer agent, 2026-11-15)

## Goal
Explore JS < 200 KB, catalogue JSON gz < 300 KB; record actuals.

## Acceptance criteria
- [x] Numbers in audits/A-01
- [ ] Tests cover it (with fixtures, no live network calls)

## Inputs
Overnight brief (prototype 1), AGENTS.md, DECISIONS.md.

## Out of scope
Anything outside the lane above. No auth, no pg-boss, no Postgres tonight.

## Handoff notes
**Reviewer, 2026-11-15.** See `audits/A-03-performance.md`. On release 1 with `next start`:
- Explore `/nl` first-load JS (8 modern scripts, gzip -9): **159.2 KB** (155.5 KiB) — budget 200 KB: **pass**. 198.6 KB if the 39.4 KB noModule polyfills are counted. Playwright confirms no extra lazy chunks.
- Client catalogue `/data/catalogue-1.json`: **34.7 KB gzip** (915 KB raw, immutable) — budget 300 KB: **pass**. Full `data/releases/1/catalogue.json`: 97.0 KB gzip (1.97 MB raw).
- `/nl` HTML: 424 KB raw / 29.7 KB gzip. Render: 157 ms cold, ~23 ms warm median.

Acceptance line 2 ("tests cover it") is only partly met: there is no automated budget check. Proposed follow-up: a CI/Playwright test that fails above 200 KB gzip.

## Review
