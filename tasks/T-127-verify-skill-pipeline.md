# T-127 `verify` skill for the pipeline
Role: WS1   Lane: pipeline/.claude/skills/verify/   Wave: process
Status: review (WS1, 2026-11-17)

## Goal
Before any commit that changes data, the agent proves the release still matches its inputs and the numbers still make sense on real rows.

## Acceptance criteria
- [x] `pipeline/.claude/skills/verify/SKILL.md`: rebuild the release from recorded staging (no network), run pytest, run the release diff (T-123), run back-tests, dry-run any changed rule on the latest release rows, spot-check the tricky-car list (EV6, Ioniq 5, MG4, Model Y LR vs Juniper, P7+).
- [x] `uv run ev verify` does the above and writes `verify-report.md`: diff summary, back-test median errors vs gates, spot-check table, memory peak.
- [x] Report summary in the PR body; commit stamp `Verified: verify-pipeline` (T-128).
- [x] Fails if MORNING/STATUS numbers quoted in the PR body differ from the report (A-20 B1).

## Inputs
WS1 retros (dry run on real rows, back-test per derived model). A-20 B1. A-30.

## Handoff notes
2026-11-17 WS1 (session_01JuyZEWFXbkeYSii8dVSWnx). Builds on T-123 (PR #44): branch from it, merge after it.
- `uv run ev verify [--data-dir D] [--skip-tests] [--pr-body FILE] [--base REF] [--out PATH] [--json]` → `pipeline/verify-report.md` + `verify-report-release-diff.csv` (both git-ignored). Exit 1 on: rebuild failure, tests failing, release diff blocking, a PR-body `key: number` claim that differs from the report.
- Rebuild: scratch copy of data/ (staging symlinked read-only, only the latest release copied, fetched by manifest if needed), full `build_release` + `write_release`, so QA, back-tests and the T-123 diff run exactly as in production. data/ is never written.
- No staging → fail with the command to record it (`ev refresh --no-release`, network, once).
- Spot checks: `ev_pipeline/verify/tricky_cars.yaml` (EV6, Ioniq 5, MG4, Model Y, P7+), old → new per headline field, notes for "real range > WLTP × 1.1", "no battery", gone/new.
- Back-tests: every back-test section in qa.json (EPA parts expanded) with n, medians and gate.
- Skill: `pipeline/.claude/skills/verify/SKILL.md` (name `verify-pipeline`), commit stamp `Verified: verify-pipeline`.
- Live run today (audits/A-32): release 2 from today's staging vs release 1 = **239 blocking**, mostly real data issues (19 variants lose WLTP, consumption −11 % median on 45). Release 2 can't ship until those are triaged.

## Review
