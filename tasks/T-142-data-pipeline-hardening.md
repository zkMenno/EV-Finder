# T-142 Data pipeline: leaner, faster, and robust when a source is down (report first)

Role: builder (report), then build tasks   Lane: WS1 (+ WS3 for seed/sources)   Wave: after the base catalogue build
Status: todo — starts after the base build lands (T-136c #138 merged, T-073 candidates reviewed, release 3 published)

## Goal
Menno, 2026-11-18: once the first build of data flows and the base EV list is done, make the pipeline lean and robust, so that keeping the catalogue current is mostly automatic: new models flow in, and one source being offline or changing never blocks a release or silently drops data.

## Acceptance criteria (report, research/R-xx-pipeline-hardening.md)
- [ ] Map of every source in data/sources.yaml: what it feeds (fields, variants, releases), how often it runs, how long it takes, how often it failed in the last 30 days of data-refresh runs (e.g. eafo 429, meteostat disconnects, rdw-tgk SnapshotError), and what a release loses today if it's down.
- [ ] Per critical field (WLTP, battery kWh, consumption, DC charging, registrations, used prices, photos): primary source, a licence-clean secondary/fallback source (or "none"), and the fallback rule (use last good snapshot with its date; switch to secondary; or hold back the value), never mixing licences (data rule 3).
- [ ] Single points of failure and fragile code paths (retries, timeouts, snapshot dirs, schema drift), plus a list of steps that can be cut, merged or cached (runtime and CI budget: where do the ~20–40 min refreshes go?).
- [ ] "New model in" path: how a model that appears in RDW/EEA/OpenEV becomes a review-queue candidate → seed → release with no hand work beyond review; what's missing today.
- [ ] Proposal for build tasks (each ≤ half a day, with acceptance criteria); WS0 approves before building.
- [ ] Evidence pack in the PR; `Verified:` on every commit; fresh review passes.

## Inputs
docs/process/README.md; pipeline/README.md (Keeping data fresh); data/sources.yaml; data-refresh run history (`gh run list --workflow data-refresh.yml`); Decisions 006, 035, 044, 068, 080; R-41.

## Out of scope
New paid sources (ask Menno: money), marketplace scraping (never), product features.

## Handoff notes

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts. -->
