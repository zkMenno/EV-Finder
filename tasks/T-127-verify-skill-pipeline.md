# T-127 `verify` skill for the pipeline
Role: WS1   Lane: pipeline/.claude/skills/verify/   Wave: process
Status: todo

## Goal
Before any commit that changes data, the agent proves the release still matches its inputs and the numbers still make sense on real rows.

## Acceptance criteria
- [ ] `pipeline/.claude/skills/verify/SKILL.md`: rebuild the release from recorded staging (no network), run pytest, run the release diff (T-123), run back-tests, dry-run any changed rule on the latest release rows, spot-check the tricky-car list (EV6, Ioniq 5, MG4, Model Y LR vs Juniper, P7+).
- [ ] `uv run ev verify` does the above and writes `verify-report.md`: diff summary, back-test median errors vs gates, spot-check table, memory peak.
- [ ] Report summary in the PR body; commit stamp `Verified: verify-pipeline` (T-128).
- [ ] Fails if MORNING/STATUS numbers quoted in the PR body differ from the report (A-20 B1).

## Inputs
WS1 retros (dry run on real rows, back-test per derived model). A-20 B1. A-30.

## Handoff notes

## Review
