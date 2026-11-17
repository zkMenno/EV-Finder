# T-128 "Verified:" stamp on every commit/PR + flaky-test policy
Role: WS0   Lane: AGENTS.md, .github/pull_request_template.md, ci.yml   Wave: process
Status: todo

## Goal
Anyone (WS0, QA, Menno) can see how each change was checked, and unchecked work is findable.

## Acceptance criteria
- [ ] AGENTS.md: every commit message ends with one line `Verified: <how>` — e.g. `verify-web`, `verify-pipeline`, `unit+e2e local`, `CI only`, `docs only`, or `none (<reason>)`. "none" is allowed but must say why.
- [ ] PR template: evidence pack section (verify report summary, screenshots link, back-test numbers), REVIEW items triggered, and `Test-change:` line if tests were removed/skipped.
- [ ] CI repo-checks warns (observe) when a PR has commits without a `Verified:` line; after a week, enforce for non-docs PRs.
- [ ] A one-liner in docs/process/ to list unverified commits: `git log --grep="Verified: none" --oneline`.
- [ ] Flaky-test policy in AGENTS.md: never skip, add sleeps or retry until green. Find the root cause; if you can't in 30 minutes, delete the test, log why in the rule register (T-122), and open a task to replace it.
- [ ] Self-merge rule: an author may merge only after a fresh reviewer (other chat or a subagent with no build context) passed the triggered REVIEW items, or after QA. Menno's "WS2 may merge its own PRs" stays valid for **green + reviewed** PRs.

## Inputs
Article: commit stamps incl. "none", observe → enforce, flaky tests teach rerunning instead of fixing. QA START.md: launch tasks merged without review.

## Handoff notes

## Review
