# Rule register (T-122, Decision 062)

Every rule we work by, the incident behind it, and **where it is enforced**. A rule that lives only in prose is marked *prose* and is a candidate for a real check. Add a row when a miss is found after merge (QA, back-test, Menno, a revert): the miss + the check added. Prune once per phase: rules that never fire get merged or dropped, with a note.

Find unverified work: `git log --grep="Verified: none" --oneline` (stamp lands with T-128).

| Id | Rule | Incident behind it | Enforced by | Owner | Added | Last fired |
|---|---|---|---|---|---|---|
| G-01 | Raw data never in git (5 MB cap); release files 25 MB cap | catalogue.json 7.1 MB turned main red (15 Nov) | CI repo-checks | WS0 | 2026-11-15 | 2026-11-15 |
| G-02 | No `.env` files committed | baseline | CI repo-checks | WS0 | 2026-11-14 | — |
| G-03 | No merge-conflict markers in tracked files | WS2 retro: markers left after a messy merge (15 Nov) | CI repo-checks + optional `.githooks/pre-push` | WS0 | 2026-11-17 | — |
| G-04 | Decision numbers unique | duplicate 019 (15 Nov), 039, 053/054, 060 | CI repo-checks | WS0 | 2026-11-17 | — |
| G-05 | Decision numbers come from the writer's own block (table at the top of DECISIONS.md) | WS2 retro: 053/054 taken by other chats | REVIEW D12 (+ G-04) | WS0 | 2026-11-17 | — |
| G-06 | A change can't edit the checks that judge it (gate files in their own PR) | article: gates out of reach of the change | CI `gate-guard` (observe → enforce, T-121) + REVIEW R3 | WS0 | 2026-11-17 | — |
| G-07 | Reviewers read REVIEW.md from `origin/main`; one review per commit (head SHA) | launch tasks merged without review (QA, 17 Nov) | REVIEW.md + AGENTS.md *prose* until T-128 | WS0 | 2026-11-17 | — |
| G-08 | Trust only the CI run on the PR head commit; start with `workflow_dispatch` after a session push | WS2 retro: session pushes don't start CI | REVIEW R0 | WS0 | 2026-11-17 | — |
| G-09 | Never rebase a pushed branch; merge main in | WS2 retro: rebase + blocked force-push | *prose* (AGENTS.md); force-push is blocked by the host anyway | WS0 | 2026-11-17 | — |
| G-10 | Every derived score/band/model: dry run on latest release rows before tests; back-test section in qa.json | WS1 retros: thresholds on a different data basis; 22 % rung inconsistency and wrong EPA matches found only by back-test | REVIEW D3 + pipeline/AGENTS.md | WS1 | 2026-11-17 | — |
| G-11 | Matching/attachment rule changes spot-check 5 tricky cars | A-30 EPA range class; T-068 '+' tokenising | REVIEW D4 | WS1 | 2026-11-17 | — |
| G-12 | Tests never call the network | baseline | REVIEW D13; *prose* otherwise (candidate: socket-blocking fixture) | WS1/WS2 | 2026-11-14 | — |
| G-13 | Every user-visible string in 6 languages (drafts allowed) + glossary tooltip for new terms | T-093 shipped unreviewed strings | REVIEW D6 | WS2/WS3 | 2026-11-17 | — |
| G-14 | Parked features (Decision 051) behind flags, off | launch scope | REVIEW D9; parked e2e only in `PARKED=1` builds | WS2 | 2026-11-17 | — |
| G-15 | Start of session: check open PRs + HANDOFF first | WS1 (3rd session) retro | START.md files *prose* | all | 2026-11-17 | — |
| G-16 | STATUS/HANDOFF/INBOX may go straight to main (docs only) | WS1 retro: two PRs appending to the same logs | AGENTS.md *prose* | all | 2026-11-17 | — |
| G-17 | Use `gh api …/pulls` when `gh pr create` fails | WS1 retro: GraphQL blocked in sessions | AGENTS.md *prose* (tip) | all | 2026-11-17 | — |
| G-18 | WS0 merges green + reviewed PRs at least once a day, in one pass; small housekeeping rides in its task PR | WS1 retro: 9-PR chain waiting on WS0 | *prose* (WS0 STATUS) | WS0 | 2026-11-17 | — |
| G-19 | Parked-feature e2e runs nightly in a `PARKED=1` build | WS2 retro: parked e2e only run by hand | to build: WS2 follow-up (T-095) | WS2 | 2026-11-17 | — |
| G-20 | Every number visible on a page has source + date + licence in Nerd mode | product principle | REVIEW D7 | WS2 | 2026-11-15 | — |
| G-21 | One owner per file; read right before writing; small edits (was P-01) | Two chats nearly overwrote the decisions file (15 Nov) | *prose* (docs/process/README.md) | all | 2026-11-15 | — |
| G-22 | Spec mirrored in docs/spec/; repo copy wins for builders (was P-02) | Overnight build couldn't read the claude.ai spec | *prose* | WS0 | 2026-11-15 | — |
| G-23 | Chats talk through INBOX files, never via Menno (was P-03) | Menno relayed AppInfra answers by hand | *prose* | all | 2026-11-15 | — |
| G-24 | Measure before sizing (server, memory) (was P-04) | Server facts guessed before measured | *prose* | WS4 | 2026-11-15 | — |
| G-25 | Project instructions live in a versioned file (was P-05) | Instructions lived only in a chat message | *prose* (docs/process/project-instructions.md) | WS0 | 2026-11-15 | — |
| G-26 | QUESTIONS.md holds only what Menno must answer (was P-06) | 83 "open" questions, ~76 engineering defaults (17 Nov) | *prose*; candidate: CI warns when > 10 open | WS0 | 2026-11-17 | — |
| G-27 | Release must match its inputs; reports must match the release (was P-13) | A-20 B1: stale release; MORNING.md quoted numbers it didn't contain | CI pytest (test_real_release); T-123, T-127 | WS1 | 2026-11-17 | — |
| G-28 | Every commit ends with `Verified: <how>` (was P-16) | Unverified work wasn't findable | to build: T-128 | WS0 | 2026-11-17 | — |
| G-29 | Flaky tests: no skip/sleep/retry; fix or delete + log (was P-17) | Article: flaky tests teach rerunning | CI `gate-guard` (observe) + T-128 | WS0 | 2026-11-17 | — |
| G-30 | Chat mentions: direct link + paste-ready code block every time (was P-18) | Menno had to ask twice (17 Nov) | *prose* (project instructions) | all | 2026-11-17 | — |
| G-31 | One process doc, one decisions log per kind; project docs are pointers (was P-19) | Workflow described in 5 places, decisions in 2 (17 Nov) | *prose* | WS0 | 2026-11-17 | — |
| G-32 | Run the full local gate in the session before opening or updating a PR; one PR per batch; no "just to check" CI runs (was P-21) | GardenLayer burned ~2,900 Actions min in 17 days (#813), mostly re-running red PRs | *prose* (AGENTS.md, docs/process/ci-budget.md); candidate: ci-ok warns if a PR gets > 3 pushes | WS0 | 2026-11-17 | — |

**Old P-ids** (verification chat's seed list, 17 Nov) map here: P-07→G-04/G-05 · P-08→G-09 · P-09→G-03 · P-10→G-08 · P-11→G-15/G-16 · P-12→G-10 · P-14→G-07 · P-15→G-06 · P-20→G-17 · P-21→G-32; the rest became G-21–G-31.

## Pruned
_None yet._

## Retro proposals processed (17 Nov 2026)

| From | Proposal | Verdict |
|---|---|---|
| WS1 | Dry run on latest release rows before tests for any derived score | Accepted → G-10 |
| WS1 | Back-test section in qa.json for every derived model | Accepted → G-10 |
| WS1 | WS0 merges WS1 PRs as soon as green, or WS1 batches housekeeping | Accepted with a change: green **and reviewed** (T-128) → G-18 |
| WS1 | STATUS/HANDOFF only in a session's last PR, or straight to main | Accepted: straight to main → G-16 |
| WS1 | Use `gh api` when `gh pr create` fails | Accepted → G-17 |
| WS1 (3rd) | START.md says "check open PRs and their HANDOFF first" | Accepted → G-15 (all START files) |
| WS2 | Fixed Decision block per workstream listed in DECISIONS.md | Accepted → G-05 + G-04 |
| WS2 | Never rebase a pushed branch | Accepted → G-09 |
| WS2 | Grep for conflict markers before every push | Accepted → G-03 (CI + hook) |
| WS2 | `workflow_dispatch` after a session push; trust the PR-head run | Accepted → G-08 |
| WS2 | Nightly `PARKED=1` e2e job | Accepted, to build → G-19 |

## Retro questions (every session end)
1. What slowed us down? 2. What did Menno have to do by hand? 3. Which rule would have prevented it? **4. What did a check miss, and which check would have caught it?** (answer 4 adds or sharpens a row here or a REVIEW.md item).
