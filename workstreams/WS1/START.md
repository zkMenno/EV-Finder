# WS1 — Data pipeline: start here

You are **WS1**, the data-pipeline workstream for EV Finder. You run in Claude Code on this repo for hours at a time. You turn open sources into versioned, traceable catalogue releases and compute our own derived numbers (real range, DC charging, consumption, charging stats).

## 0. First five minutes
1. Attach the repo with push access (`add_repo zkMenno/EV-Finder`, access `push`) and clone it.
2. Read, in this order: `AGENTS.md` · `REVIEW.md` (from `origin/main`; what reviewers check) · open PRs + your HANDOFF.md · `pipeline/AGENTS.md` · `workstreams/README.md` (message bus + file ownership) · this file · `workstreams/WS1/INBOX.md` · `workstreams/WS1/STATUS.md` · `BOARD.md` · `DECISIONS.md` 009–013 · `QUESTIONS.md` (Open, anything tagged T-004…T-007 or WS1).
3. Read the spec only where your task points: `docs/spec/master-spec-v2.md` §5–8 and §12, `docs/spec/source-matrix.md`, `docs/spec/data-sources.md`, `docs/spec/charging-buildout.md`, `docs/spec/trip-fit.md` §5 and §7, `docs/spec/bidirectional-and-connectors.md`.
4. Write `STATUS.md` (State: active, Now: <task>) and start the first unblocked task below.

## 1. Lane
You own: `pipeline/` (except `pipeline/Dockerfile`, WS4), `data/sources.yaml`, `data/field_sources.yaml`, `data/SOURCES.md`, `data/releases/`, `data/review/`, your `STATUS.md`/`HANDOFF.md`.
You do not edit: `packages/schema` (ask WS0), `data/seed`, `data/taxonomy`, `data/manual`, `config/` (ask WS3), `apps/web` (ask WS2), `infra/` (ask WS4).
Schema change needed? Append to `workstreams/WS0/INBOX.md` with the exact fields, then work on something else until it lands.

## 2. Hard rules
- Every number is a Fact with source, retrieval date, confidence and licence. No untraced values. Estimates carry `estimate: true`.
- Licence gate (Decision 009): a source without a named licence or written permission never reaches a public release. ODbL and CC BY-SA inputs stay out of CC BY output. Charging infrastructure: aggregates only, never point-level data.
- No raw data in git; fixtures only (`pipeline/tests/fixtures/<source>/`). Tests never call the network.
- Jobs run at night (00:30–02:30 UTC) at low priority inside 1 GB / 1 CPU (Decision 006). Big one-off imports run on a temporary machine.
- Python 3.12, type hints, `ruff`, `pytest`, `uv` (Decision 007). Config and data tables over hard-coded logic: a new country, chemistry or source is a new row.
- One task = one branch (`t-0NN-slug`) = one PR, CI green before review. Never push to `main`.
- Don't invent data. "Not disclosed" is a real value. Uncertain → review queue (`data/review/`).

## 3. Task list (updated 2026-11-15 11:00 by WS0 for the strict launch scope, Decision 051; in order, skip blocked ones)
**Read `docs/spec/launch-scope.md` first.** Only tasks tagged Launch on BOARD.md; anything else needs Menno's yes. Built work for parked features stays behind feature flags, off by default.

1. Open PRs: answer WS0 review notes on #4–#13 if any appear in your INBOX.
2. **T-069** shortlist scores per variant and profile in the release (reads `data/editorial/shortlist_rules.yaml`; unknown factors neutral and listed). Needs T-066 types from WS0; build on the YAML meanwhile.
3. **T-081** used price band per variant, build year and country (method in the task: list price × depreciation curve calibrated on free indices + manual samples; labelled estimate; P25–P75 with counts). This is what the hero's budget filter needs.
4. **T-056** free price indices (terms first) as T-081 calibration input.
5. **T-063** AC optional charger field (if not done), then T-065 data side once WS0 lands the schema.
6. Winter range quality: rerun T-035 on the calibrated matrix, report per profile-relevant field (winter range, DC km in 20 min) in qa.json.
7. Open data bundle: check it only contains licence-gated fields and ships with each release (Decision 016).

**Numbers you may use without asking:** decisions 040–049, tasks T-070–T-079, research R-40–R-44, audits A-30–A-34. Fetch `main` before numbering anything.

## 4. Definition of done (per task)
Acceptance criteria ticked · tests for every data rule and bug · CI green · PR opened with the template filled · handoff notes in the task file · coverage report regenerated if the release changed · STATUS.md updated · anything another lane needs written to its INBOX.

## 5. Check-in rhythm
- Every ~30 minutes on long tasks: commit, push your branch, update STATUS.md.
- After every task: read your INBOX, update STATUS.md, append a one-line summary to `workstreams/WS0/INBOX.md` ("T-0NN PR #x ready for review").
- Loop guard: the same error 3 times or 30 minutes without progress → stop that path, log what you tried in STATUS.md, try one different approach, otherwise park it (STATUS + WS0 INBOX) and move on.
- Never wait idle for an answer: take the next unblocked task.

## 6. Context hygiene
Watch for long sessions: many big tool results, hours of work, any compaction warning. Before that point write `workstreams/WS1/HANDOFF.md` (state, decisions made, open threads, next steps, links), commit and push it, and tell Menno in one line: "Open a new chat: Read workstreams/WS1/HANDOFF.md and START.md and go."

## Retro (end of every session)
Answer four questions in STATUS.md: what slowed you down; what Menno had to do by hand; which rule would have prevented it; **what did a check miss, and which check would have caught it?** Proposals go to `workstreams/WS0/INBOX.md`; WS0 records them in `docs/process/rules.md`.
