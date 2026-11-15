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

## 3. Task list (updated 2026-11-15 10:30 by WS0, after overnight PR #1 merged; in order, skip blocked ones)
Overnight 1 built a lot: read `MORNING.md` and the handoff notes in each task file before you start. Claim a task by writing your name + date in its Status line; set `review` when your PR is open.
1. **T-064** releases out of git (Decision 035), ≈2 h. Release files to GitHub Release assets (tag `data-v<n>`) from a workflow with least-privilege `contents: write`; repo keeps `data/releases/<n>/manifest.json` + a tiny fixture release; web build fetches by manifest and checks sha256 (agree the loader change with WS2 via its INBOX, or make the change behind `CATALOGUE_SOURCE=manifest` so WS2 can review); split the catalogue per generation; rollback documented. CI release cap back to 5 MB when done (ask WS0 in its INBOX; WS0 owns `.github/`).
2. **T-025** finish charging stats, ≈1.5 h. Loaders exist (see handoff notes). Open: EAFO now allowed (Decision 037: `active_pending_confirmation`, credit line in the decision), manual YAML path `data/manual/charging/*.yaml`, release diff (>15 % change or any drop → review), wire into `ev refresh`. Answer Q-075/Q-076 defaults yourself if they're engineering choices and log them.
3. **Decision 036/037 housekeeping**, ≈20 min: update `data/sources.yaml` (EAFO, RDW attribution wording, ERA5-Land primary climate, Washington DOL internal-only, ECB MIR finance series ids from research/R-20).
4. **T-034** climate normals, ≈1 h: Meteostat bulk normals (CC BY 4.0, no key) for launch-country towns from GeoNames now; ERA5-Land loader stubbed behind an env key (Copernicus CDS key arrives via WS4, Q-093).
5. **T-032 + T-033** consumption tests + model, ≈2 h: licence-clean inputs only (WLTP from EEA/ADEME, EPA city/highway from fueleconomy.gov, physics rung from mass/Cd/frontal area where cited); Bjørn Nyland/NAF stay `waiting_permission`. Output the per-variant matrix (3 road bands × 5 temperature bands, rung + confidence) as static JSON in the release so WS2 can swap out T-036's fixture.
6. **T-035** back-test harness on real inputs where licence-clean; report in `qa.json` and `audits/` (number from WS0's INBOX, or use A-30–A-39).
7. **T-051 part 2**: the remaining top-20 models from `data/review/coverage-gaps.md` (ID.7, Elroq, EV3, Q6 e-tron, …), from staged source data only.
8. If time remains: T-062 (retired ids) and T-063 (AC optional charger) if their handoff notes are still empty; then research R-21/R-22 gap follow-ups that WS3 asked for in your INBOX.

**Numbers you may use without asking** (to avoid clashes): decisions 040–049, tasks T-070–T-079, research R-40–R-44, audits A-30–A-34. Fetch `main` before numbering anything.

## 4. Definition of done (per task)
Acceptance criteria ticked · tests for every data rule and bug · CI green · PR opened with the template filled · handoff notes in the task file · coverage report regenerated if the release changed · STATUS.md updated · anything another lane needs written to its INBOX.

## 5. Check-in rhythm
- Every ~30 minutes on long tasks: commit, push your branch, update STATUS.md.
- After every task: read your INBOX, update STATUS.md, append a one-line summary to `workstreams/WS0/INBOX.md` ("T-0NN PR #x ready for review").
- Loop guard: the same error 3 times or 30 minutes without progress → stop that path, log what you tried in STATUS.md, try one different approach, otherwise park it (STATUS + WS0 INBOX) and move on.
- Never wait idle for an answer: take the next unblocked task.

## 6. Context hygiene
Watch for long sessions: many big tool results, hours of work, any compaction warning. Before that point write `workstreams/WS1/HANDOFF.md` (state, decisions made, open threads, next steps, links), commit and push it, and tell Menno in one line: "Open a new chat: Read workstreams/WS1/HANDOFF.md and START.md and go."
