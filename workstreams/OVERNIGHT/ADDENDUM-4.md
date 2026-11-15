# Overnight build 1 — addendum 4 (from WS0, 2026-11-15 01:00 UTC)

Since your brief, `main` gained the full spec mirror, new decisions and tasks. Pick these up after your current wave, in this order. You act as the coordinator on your branch, so the schema work is yours tonight (WS0 will not touch `packages/schema` until your PR merges).

## 0. Sync first (5 min)
1. `git fetch --depth=50 origin main` and merge `origin/main` into `proto/overnight-1`.
2. Conflicts: BOARD.md, QUESTIONS.md, DECISIONS.md → keep both sides (main has Decisions 011–014; renumber nothing of main's). If your branch added decisions numbered 011+, renumber yours after 014 and fix references.
3. Rename your `research/R-01-official-ev-sources.md` → `research/R-02-official-ev-sources.md` (main's R-01 is bidirectional) and update references (Q-036, Q-037, data/sources.yaml comments).
4. Q-030: no force-push is needed any more. `main` moved on (bidi + workstreams commits on top of 660427d), so your branch merges normally through the PR. Mark Q-030 closed with that answer.

## 1. New inputs on main
- `docs/spec/*.md` — every spec tab (Master spec v2, Source matrix, Charging buildout, Trip fit, Battery guide, Marketplaces, …). Repo copy wins.
- `DECISIONS.md` 011 (bidi + plugs), 012 (charging stats, aggregates only), 013 (Trip fit: Valhalla box, browser scoring), 014 (workstreams + file ownership).
- `tasks/T-018` … `T-042`, `BOARD.md` waves 5–8, `workstreams/` (START/STATUS/INBOX per workstream).

## 2. Pick up tonight (each = own commit, tests green, handoff notes in the task file)
1. **T-018** schema-bidi-connectors (schema). Then the coordinator half of **T-019** if time: load/validate the bidi taxonomies (rows can be a minimal EN set; WS3 completes them).
2. **T-023** schema-charging-stats (schema).
3. **T-030** schema-trip-fit (schema).
4. **T-024** charging taxonomies + `country_charging_links` for NL, DE, FR, BE, UK (spec "Charging buildout" lists the links per country).
5. **T-026** web charging link-out block + plain ABRP link (Core 1; config only, no data).
6. **T-036** Trip fit quick range check with a **fixture** consumption matrix, behind a feature flag (Core 1 UI only; no real model tonight).

Skip for tonight (need permissions, live data or infra): T-025 ingest beyond fixtures, T-028, T-029, T-032–T-035, T-037, T-038, T-040.

## 3. Report
Add a section "Addendum 4" to MORNING.md: what was done, what was skipped and why, new questions (also in QUESTIONS.md). Then open/refresh the draft PR.
