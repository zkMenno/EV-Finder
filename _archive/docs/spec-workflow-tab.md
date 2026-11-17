<!-- Mirror of the claude.ai spec doc, tab "Workflow" (rev 1), exported 2026-11-15 by WS0. For builders this repo copy wins; product changes start in the doc and WS0 mirrors them here. Transcribed from the export; if a figure looks off, check the doc tab. -->

# Agent workflow

How the project gets built: a solo owner (Menno) plus AI agents that talk to each other through markdown files in one GitHub repo. The goal is the opposite of draining: **you read one file, answer questions, and approve gates.** Everything else runs between the agents.

## Principles

1. **The repo is the memory.** Chats and Claude Code sessions forget; files don't. Every handoff, question and decision lives in a file.
2. **Few roles, clear lanes.** Five roles; each builder owns a folder, so agents never edit the same files.
3. **One task = one branch = one session.** Small tasks (half a day of agent work at most), each with acceptance criteria.
4. **Tests are the first gate.** A pull request that fails the tests never reaches a reviewer.
5. **You touch three things only:** `QUESTIONS.md`, the daily digest and phase gates.

## Roles

| Role | Does | Reads | Writes | Where it runs |
| --- | --- | --- | --- | --- |
| Coordinator | Turns the spec into tasks, plans waves, keeps the board, merges, changes the shared schema | Spec, `BOARD.md`, task files, review notes | `BOARD.md`, `tasks/`, `DECISIONS.md`, `QUESTIONS.md` | One long-running chat in this project + a Claude Code session for merges |
| Researcher | Answers one research question, no code | Task file, spec | `research/R-xx-slug.md` | Chat or Claude Code |
| Builder | Does one task in its lane on its own branch, opens a pull request | Task file, `AGENTS.md`, its lane's `AGENTS.md` | Code in its lane + handoff notes in the task file | Claude Code (web or desktop) |
| Reviewer / tester | Fresh agent: checks the pull request against acceptance criteria, runs and extends tests | Task file, diff | Review notes in the task file; approve or send back | Claude Code |
| Auditor | Security review, dependency check, load test, data-quality check | Whole repo, release | `audits/A-xx.md` + new tasks for findings | Claude Code, scheduled |

Preparation is part of the coordinator's job: a well-written task file *is* the prep.

## Repo files

```
AGENTS.md            shared rules for every agent (stack, style, how to hand off)
BOARD.md             one screen: Now / Next / Blocked / Done (coordinator only)
QUESTIONS.md         questions for Menno; he answers inline
DECISIONS.md         every decision with date and reason
CHANGELOG.md         what shipped, per wave
tasks/T-012-slug.md  one file per task
research/R-04-slug.md
audits/A-02-slug.md
apps/web/**/AGENTS.md, pipeline/**/AGENTS.md   lane rules (nested)
```

## Task file template

```
# T-012 RDW source adapter
Role: builder   Lane: pipeline/sources/rdw   Wave: 3
Status: todo | doing (agent-name, date) | review | done | blocked

## Goal
One sentence.

## Acceptance criteria
- [ ] Fetches the RDW open data endpoint into raw storage
- [ ] Normalises to Fact rows that pass schema validation
- [ ] Tests cover one real sample file

## Inputs
Links to spec sections, research files, sample data.

## Out of scope
What not to touch.

## Handoff notes
Builder writes what was done, what's left, anything surprising.

## Review
Reviewer writes pass / changes needed, with reasons.
```

## Task lifecycle

`todo` → builder claims it by writing its name and date in Status → `doing` → pull request opened → `review` → reviewer passes it → coordinator merges → `done`. If an agent is blocked, it sets `blocked`, writes the question in `QUESTIONS.md` with the task id, and stops; it does not guess.

## Waves and lanes

Work runs in waves of roughly a week:

1. **Plan:** the coordinator writes the wave's tasks (one per lane at most) and freezes `packages/schema`.
2. **Build:** builders run in parallel, each in its own lane.
3. **Review:** one reviewer per 3–4 builders; tests first, then criteria.
4. **Merge:** a queue, one pull request at a time, rebased on the latest main.
5. **Close:** changelog entry, board refresh, schema changes for the next wave, audit if due.

**Parallelism:** start with 3–5 builders in Phase 0 (it is mostly sequential: schema → pipeline skeleton → first import). Widen toward 10–15 from Phase 1, when pages, data sources and countries become independent lanes. 🟡 Check plan usage limits before going past 5.

**Starting lane map**

| Lane | Folder | First tasks |
| --- | --- | --- |
| Schema (coordinator only) | `packages/schema` | Make → Model → Generation → Variant → Market variant → Fact |
| Pipeline core | `pipeline/core` | Merge, validate, release |
| Sources | `pipeline/sources/<name>` | One lane per source: OpenEV, RDW, EEA, KBA, DfT… |
| Range model | `pipeline/models/range` | Fallback ladder + back-test |
| Web: Explore | `apps/web/explore` | Table, filters, compare tray |
| Web: pages | `apps/web/vehicles` | Model / generation / variant pages |
| Web: accounts | `apps/web/me` | Phase 2 |
| Staff | `apps/web/staff` | Vehicle editor, review queue |
| Infra | `infra/` | Hetzner, Coolify, backups, CI |

## Audits

An audit runs after every phase gate and after roughly every 10 merged tasks, whichever comes first, plus a weekly scheduled dependency check.

- **Security:** auth flows, secrets in code, dependency vulnerabilities, OWASP top 10 on public routes.
- **Stress:** load test the Explore page and API against the targets in section 13 of the spec.
- **Data quality:** release diff, outliers, missing facts, back-test error of the range model.

Findings become new tasks; anything critical blocks the next merge.

## Your touchpoints

| When | What you do | Time |
| --- | --- | --- |
| Daily | Read the 5-line digest (scheduled task) | 2 min |
| When pinged | Answer `QUESTIONS.md` inline | 5–15 min |
| End of wave | Skim the changelog, glance at the preview site | 15 min |
| Phase gate | Approve or send back | 30 min |

## Setup steps

1. Create the GitHub repo; run the agentic-scaffold init for `AGENTS.md`, `DECISIONS.md`, `CHANGELOG.md`.
2. Add `BOARD.md`, `QUESTIONS.md`, the task template and `tasks/`, `research/`, `audits/` folders.
3. Nest lane `AGENTS.md` files with agentic-scaffold nest.
4. CI: lint, type check, tests on every pull request; preview deploy per branch.
5. Coordinator writes wave 1 (Phase 0, 3–5 tasks).
6. Scheduled tasks: daily digest, weekly dependency audit.
