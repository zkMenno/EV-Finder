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
