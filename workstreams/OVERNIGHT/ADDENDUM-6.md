# Overnight build 1 — addendum 6: data pipeline first (from WS0, 2026-11-15 01:20 UTC)

Menno: the data pipeline, the initial dataset and the way to keep it updated are the heart of the product. **Finish the addendum 5 item you are on, then do this addendum before the rest of addendum 5** (items 2–7 of addendum 5 come after this; the bottomless backlog stays last).

What already exists on your branch (good): adapters for OpenEV, KilowattApp OpenEV, RDW, EEA, KBA FZ10, DfT VEH, ADEME, a Nyland skeleton; match → merge → derive → release 1; licence gate. What's missing is the **update loop** and the **initial dataset coverage**.

## P1. One-command refresh (≈2 h)
- `ev-pipeline refresh [--sources …] [--dry-run]`: for each active source whose cadence is due (from `data/sources.yaml`), fetch → snapshot → parse → match → merge → derive → QA → build release N+1.
- Snapshots: write raw fetches to a local snapshot store (`$SNAPSHOT_DIR`, git-ignored) with content hash, URL, fetched_at, HTTP ETag/Last-Modified; an S3-compatible backend behind the same interface, configured by env vars only (Scaleway later; no credentials in the repo).
- Skip unchanged sources (same hash / 304) so a nightly run is cheap.
- Run log: `runs/<timestamp>.json` with per-step inputs, outputs, row counts, durations, errors (git-ignored; a summary goes into the release).
- Stays inside 1 GB RAM: stream large files, never load a whole registry into memory; measure peak RSS and report it in MORNING.md.
- Log a decision: CLI refresh now, pg-boss scheduling when the database arrives (Decisions 003, 008).

## P2. Releases you can trust and undo (≈1 h)
- Release numbering stays as set in the schema lane; `data/releases/latest` switches atomically (write to a temp dir, then rename/symlink).
- `ev-pipeline release rollback --to <n>` and `release diff <a> <b>` (human-readable summary + JSON).
- A release only becomes `latest` if the blocking QA checks pass (addendum 5 item 5; build the minimal blocking checks here if that item isn't done yet).

## P3. Source health and drift (≈1 h)
- Per source: last success, last change, row counts vs previous, schema fingerprint (column names/types). A changed fingerprint fails closed for that source (previous good data kept) and writes a review item.
- `data/releases/<n>/sources.json`: status per source for the staff page and the Nerd mode "as of" dates.
- `ev-pipeline sources check`: one table in the terminal.

## P4. Automatic updates before the server exists (≈1 h)
- GitHub Actions workflow `data-refresh.yml` (scheduled weekly + manual dispatch): runs `refresh` against live sources, then opens a PR "Data release N" containing only the new release folder and the QA report (never raw data). Least-privilege permissions; no secrets needed for the open sources; sources that need keys are skipped.
- Tests still never touch the network; this workflow is not a test.
- Write in `pipeline/README.md` how Menno or an agent updates data by hand: one command, what to check in the QA report, how to roll back.

## P5. Initial dataset: top-40 used models complete (≈2–3 h)
- Build the list of the top-40 used EV models for NL, DE, FR, BE, UK from registration data you already ingest (RDW, KBA FZ10, DfT VEH; fleet age 2–8 years), not from memory. Save as `data/seed/top40.yaml` with the counts and sources behind each pick.
- For each: generations with boundaries derived from data (RDW first-registration years per type approval, EEA type-approval years) plus Wikidata (CC0) as corroboration. Add a Wikidata adapter (models, generations, years, body type) if missing.
- Variants per generation: battery options, drivetrain, power, from OpenEV/KilowattApp/EEA/ADEME; gaps listed, never guessed.
- Coverage report for the top 40: per headline field, how many have ≥ 2 agreeing sources, 1 source, or none; target 80 % ≥ 2 sources. Write `data/review/coverage-gaps.md` with which source could fill each gap.
- Apply the Q-021 source-scoped aliases and the Q-019 option (a) corroboration behind flags if they raise the match rate; report before/after numbers.

## P6. More open sources (≈2 h, in this order)
1. RDW inspections + defects (CC0): counts of common defects by generation and age → "Known issues" facts (aggregates only).
2. fueleconomy.gov (US public domain): EPA range/consumption/usable-kWh as cross-check facts (market `us`), helps agreement counts on shared models.
3. DVSA MOT history: skip unless an API key env var is present (it isn't tonight).
4. EAFO / Bundesnetzagentur / DfT charging statistics into `charging_stats` (T-025), licence recorded per download; RVO stays blocked (share-alike).

## P7. Manual facts path (≈1 h)
- `data/manual/<topic>/*.yaml` format for hand-entered facts (value, unit, source URL, retrieved date, quote/page, entered_by), validated by the pipeline; manual facts are internal-only until Q-008 is answered.
- Review queue: `data/review/*.csv` gets a stable id per item and a status column so the staff page can work them off.

## Report
Add "Addendum 6" to MORNING.md: per item done/partial/skipped, peak memory, refresh time per source, match rate before/after, top-40 coverage numbers, new questions. Then continue with addendum 5 items 2–7, then the bottomless backlog.
