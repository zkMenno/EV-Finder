# T-121 Gate guard: a change can't edit its own checks
Role: WS0   Lane: .github/workflows/ci.yml   Wave: process
Status: done (merged PR #42, 2026-11-17)

## Goal
PRs that change code and also weaken the checks that judge it get stopped for a separate WS0 review.

## Acceptance criteria
- [x] CI job `gate-guard` (in `ci.yml`, required by `all-green`): if a PR touches gate files **and** non-gate files, it fails with a plain message: "Split the gate change into its own PR".
- [x] Gate files listed in one config file (`config/gate-files.yaml`), not hard-coded: `.github/workflows/**`, `REVIEW.md`, `AGENTS.md`, `**/AGENTS.md`, `CLAUDE.md`, QA thresholds (`pipeline/**/qa*.yaml`, `*_params.yaml` gates), `audits/A-03` budget numbers, playwright/vitest/pytest config.
- [x] Also fails when a PR deletes a test file or adds `skip`/`xfail`/`.only`/`test.fixme`/`sleep(` in tests, unless the PR body has a `Test-change:` line explaining why (rule from T-128).
- [x] Modes: `off | observe | enforce` in the config. Start in **observe** for one week (log what it would block in the job summary), then switch to enforce and log a Decision.
- [x] Escape hatch: a `gate-ok` label applied by WS0 lets a mixed PR through (logged).
- [x] Tests for the path matcher (fixtures, no network).

## Inputs
Article: rules gating changes live where the change can't modify them; observe → enforce gates; after repeated blocks let the commit through with an explanation so agents don't get stuck.

## Out of scope
GitHub branch protection settings (Menno-only; WS0 may ask via QUESTIONS if wanted later).

## Handoff notes

## Review

### Review round 1 (subagent, 8f89304) → fixed
- Blocking: the PR template's comment text satisfied the `Test-change:` check. Now a real line `Test-change: <reason>` outside HTML comments is required (`has_marker`, test added).
- Fixed: nested `**/conftest.py` and `.github/dependabot.yml` are gate files; `sleep(` narrowed to `time.sleep(` / `waitForTimeout(`; the guard's own test data is exempt.
- Before enforce (2026-11-24): renamed/moved test files (diff-filter R) and removed asserts aren't caught yet; `gate-ok` label author isn't checked. Do these with the enforce switch.


## Review
WS0 subagents (fresh), 2026-11-17: R0–R3, D11, D12: pass (6b120ca), after 3 rounds (round 1 found the Test-change marker bypass; round 3 checked the merge of main). Details on PR #42.
