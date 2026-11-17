# T-122 Retro → rule pipeline + rule register
Role: WS0   Lane: docs/process/, AGENTS.md, .githooks/   Wave: process
Status: todo

## Goal
Every miss and every retro proposal ends as an enforced check or a rejected idea within a day, and rules get pruned.

## Acceptance criteria
- [ ] `docs/process/rules.md`: one table, one row per rule: id, rule, incident behind it, where enforced (test / CI job / hook / REVIEW item / prose), owner, added, last time it fired. Prose-only rules are marked as such.
- [ ] Process the retro proposals still pending (accept → enforce, or reject with a reason):
  - WS1: dry run on latest release rows before tests for any derived score; back-test section in qa.json for every derived model; merge WS1 PRs as soon as green / batch housekeeping; STATUS/HANDOFF only in a session's last PR, or straight to main; use `gh api` when `gh pr create` fails
  - WS2: fixed Decision number block per workstream (listed at the top of DECISIONS.md); never rebase a pushed branch, merge main in; grep for conflict markers before every push; start CI with workflow_dispatch after a session push and trust the PR-head run; nightly PARKED=1 e2e job
  - WS1 (3rd): START.md says "check open PRs and their HANDOFF first"
- [ ] Enforce by tool where possible: conflict-marker check in CI repo-checks (and an optional `.githooks/pre-push`); duplicate Decision number check in CI.
- [ ] Add a 4th retro question everywhere (START template, operating rules): "What did a check miss, and which check would have caught it?"
- [ ] Every bug found after merge (QA, back-test, Menno, revert) gets a row: the miss + the check added (test, REVIEW item or hook).
- [ ] Prune once per phase: drop or merge rules that never fire; note it in the register.

## Inputs
workstreams/WS1/STATUS.md and WS2/STATUS.md retros; WS0 INBOX lines from 15–17 Nov; article "turn misses into rules" + "prune".

## Handoff notes

## Review
