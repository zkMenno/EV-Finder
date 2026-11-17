# Rule register

Every process rule, why it exists and what enforces it. Owner: WS0 (T-122). Add a row when a miss or retro creates a rule; prune once per phase (rules that never fire get merged or dropped). "Prose" = written rule only, no tool enforces it yet: those are the first candidates for a test, hook or CI check.

| Id | Rule | Incident behind it | Enforced by | Added | Status |
|---|---|---|---|---|---|
| P-01 | One owner per file; read right before writing; small edits | Two chats nearly overwrote the decisions file (15 Nov) | Prose (docs/process §4) | 2026-11-15 | active |
| P-02 | Spec mirrored in docs/spec/; repo copy wins for builders | Overnight build couldn't read the claude.ai spec | Prose | 2026-11-15 | active |
| P-03 | Chats talk through INBOX files, never via Menno | Menno relayed AppInfra answers by hand | Prose | 2026-11-15 | active |
| P-04 | Measure before sizing (server, memory) | Server facts guessed before measured | Prose | 2026-11-15 | active |
| P-05 | Project instructions live in a versioned file | Instructions lived only in a chat message | Prose (docs/process/project-instructions.md) | 2026-11-15 | active |
| P-06 | QUESTIONS.md holds only what Menno must answer | 83 "open" questions, ~76 of them engineering defaults (17 Nov) | Prose; candidate: CI warns when QUESTIONS has > 10 open | 2026-11-17 | active |
| P-07 | Decision numbers come from each workstream's block | 052–056 clashed twice; duplicate 060 | Prose; T-122 adds a CI duplicate check | 2026-11-17 | proposed |
| P-08 | Never rebase a pushed branch; merge main in | WS2: blocked force-push → messy merge | Prose | 2026-11-17 | active |
| P-09 | No merge-conflict markers in any pushed file | WS2: leftover markers after a merge | Prose; T-122 adds a CI check | 2026-11-17 | proposed |
| P-10 | After a session push, start CI with workflow_dispatch; trust the PR-head run | Session pushes don't trigger CI | Prose | 2026-11-17 | active |
| P-11 | HANDOFF.md goes straight to main; check open PRs before starting | A WS1 chat started from a stale HANDOFF in an unmerged PR and redid T-069 | Prose | 2026-11-17 | active |
| P-12 | Derived score/model: dry run on real release rows first; back-test section in qa.json | Thresholds on the wrong data basis; 22 % model inconsistency and wrong EPA matches found only by back-test | REVIEW D3 (draft); T-127 | 2026-11-17 | proposed |
| P-13 | Release must match its inputs; reports must match the release | A-20 B1: stale release, MORNING.md quoted numbers it didn't contain | CI pytest (test_real_release); T-123, T-127 | 2026-11-17 | partly |
| P-14 | No merge without a fresh review of the triggered REVIEW items | Launch tasks merged unreviewed while WS0 was idle | Prose; T-120, T-128 | 2026-11-17 | proposed |
| P-15 | Checks out of reach of the change (gate files in their own PR) | Article; builders could edit tests/CI in the same PR | T-121 gate-guard | 2026-11-17 | proposed |
| P-16 | Every commit ends with `Verified: <how>` | Unverified work wasn't findable | T-128 | 2026-11-17 | proposed |
| P-17 | Flaky tests: no skip/sleep/retry; fix or delete + log | Article: flaky tests teach rerunning | T-121 (observe), T-128 | 2026-11-17 | proposed |
| P-18 | Chat mentions: direct link + paste-ready code block every time | Menno had to ask twice (17 Nov) | Prose (docs/process/project-instructions.md) | 2026-11-17 | active |
| P-19 | One process doc, one decisions log per kind; project docs are pointers | Workflow described in 5 places, decisions in 2 (17 Nov) | Prose | 2026-11-17 | active |
| P-20 | If `gh pr create` fails, use `gh api …/pulls` | GraphQL blocked in sessions | Prose | 2026-11-17 | active |
| P-21 | Run the full local gate in the session before opening or updating a PR; one PR per batch; no "just to check" CI runs | GardenLayer burned ~2,900 Actions min in 17 days (#813), mostly re-running red PRs | Prose (docs/process/ci-budget.md); candidate: ci-ok warns if a PR gets > 3 pushes | 2026-11-17 | proposed |

## Pruned
_None yet._
