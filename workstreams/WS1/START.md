# WS1 — Data pipeline: start here

You are **WS1**, the data-pipeline workstream for EV Finder. You run in Claude Code on this repo for hours at a time. You turn open sources into versioned, traceable catalogue releases and compute our own derived numbers (real range, DC charging, consumption, charging stats).

## 0. First five minutes
1. Attach the repo with push access (`add_repo zkMenno/EV-Finder`, access `push`) and clone it.
2. Read, in this order: `AGENTS.md` · `pipeline/AGENTS.md` · `workstreams/README.md` (message bus + file ownership) · this file · `workstreams/WS1/INBOX.md` · `workstreams/WS1/STATUS.md` · `BOARD.md` · `DECISIONS.md` 009–013 · `QUESTIONS.md` (Open, anything tagged T-004…T-007 or WS1).
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

## 3. Task list (in order; skip blocked ones, come back later)
Task files in `tasks/` hold acceptance criteria. Claim a task by writing your name and date in its Status line.
1. **Overnight leftovers**: after WS0 merges `proto/overnight-1`, read `MORNING.md` and the T-004–T-007 handoff notes; fix anything WS0 queued in your INBOX first.
2. **T-019** taxonomy-seed-bidi: validation and release wiring for the bidi taxonomies WS3 seeds (WS3 writes the rows, you load and validate them). Needs T-018 (WS0).
3. **T-025** charging-stats-ingest: `charging_stats` job + loaders for EAFO, Bundesnetzagentur, DfT; manual YAML path for Avere-France and Belgium; licence check per download recorded in `data/sources.yaml`. Needs T-023 (WS0).
4. **T-032** consumption-tests-ingest: condition-tagged tests (speed, temperature, wheels, source, date) from licence-clean sources; Bjørn Nyland stays `waiting_permission`.
5. **T-033** consumption-model: per-variant matrix (3 road bands × 5 temperature bands), fallback ladder measured → platform → physics → WLTP ratio, temperature curves per heater type, rung + confidence per cell, static JSON in the release.
6. **T-034** climate-normals: Meteostat normals (confirm licence first; Copernicus ERA5 fallback), GeoNames cities (CC BY 4.0) for town search.
7. **T-035** back-test harness: real-range ratio model and consumption model against NAF El Prix routes and condition-tagged tests; report median error per top-40 used model; launch gate < 10 %.
8. Research for Phase 4 (only when 1–7 are done or blocked): US + AU sources (EPA fuel economy, state registrations, Australian data) as `research/R-NN-us-au-sources.md` (ask WS0 for the number).

## 4. Definition of done (per task)
Acceptance criteria ticked · tests for every data rule and bug · CI green · PR opened with the template filled · handoff notes in the task file · coverage report regenerated if the release changed · STATUS.md updated · anything another lane needs written to its INBOX.

## 5. Check-in rhythm
- Every ~30 minutes on long tasks: commit, push your branch, update STATUS.md.
- After every task: read your INBOX, update STATUS.md, append a one-line summary to `workstreams/WS0/INBOX.md` ("T-0NN PR #x ready for review").
- Loop guard: the same error 3 times or 30 minutes without progress → stop that path, log what you tried in STATUS.md, try one different approach, otherwise park it (STATUS + WS0 INBOX) and move on.
- Never wait idle for an answer: take the next unblocked task.

## 6. Context hygiene
Watch for long sessions: many big tool results, hours of work, any compaction warning. Before that point write `workstreams/WS1/HANDOFF.md` (state, decisions made, open threads, next steps, links), commit and push it, and tell Menno in one line: "Open a new chat: Read workstreams/WS1/HANDOFF.md and START.md and go."
