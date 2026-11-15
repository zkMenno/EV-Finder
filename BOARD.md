# Board

One screen: what's happening. Coordinator only. Task details live in `tasks/`.

_Last updated: 2026-11-15 01:00 UTC by WS0. Waves 1–4 are being built by overnight prototype 1 on `proto/overnight-1`; status updates when it is reviewed and merged._

## Now
- Waves 1–4 — overnight prototype 1 (branch `proto/overnight-1`, review pending MORNING.md)
- WS0: T-018 schema-bidi-connectors, T-023, T-030 schemas
- Workstreams WS1–WS5 ready to open: `Read workstreams/<ws>/START.md and go.`

## Next
### Wave 1 — Foundations
- T-001 schema-v0 (coordinator, `packages/schema`)
- T-002 repo-plumbing (builder, `root config, .github, pipeline/pyproject.toml`)
- T-003 seed-models (builder, `data/seed`)

### Wave 2 — Data pipeline v0
- T-004 source-adapters (builder, `pipeline/sources`)
- T-005 match-merge (builder, `pipeline/ev_pipeline/merge`)
- T-006 validate-release (builder, `pipeline/ev_pipeline/release`)
- T-007 derived-metrics (builder, `pipeline/ev_pipeline/derive`)

### Wave 3 — Web prototype
- T-008 explore (builder, `apps/web (explore)`)
- T-009 model-pages (builder, `apps/web (ev pages)`)
- T-010 compare (builder, `apps/web (compare)`)
- T-011 rankings (builder, `apps/web (top)`)
- T-012 i18n (builder, `apps/web (i18n)`)
- T-013 health-docker-deploy (builder, `apps/web/Dockerfile, infra/`)

### Wave 4 — Harden
- T-014 review (reviewer, `tasks/ (review notes)`)
- T-015 tests-smoke (coordinator, `apps/web/e2e`)
- T-016 perf-budget (coordinator, `audits/`)
- T-017 security-pass (coordinator, `audits/`)

### Wave 5 — Bidirectional + plugs (Decision 011, docs/spec/bidirectional-and-connectors.md)
- T-018 schema-bidi-connectors (WS0, `packages/schema`)
- T-019 taxonomy-seed-bidi (WS3 rows + WS1 validation, `data/`) — after T-018
- T-021 learn-bidi-plugs (WS3, `content/`)
- T-042 bidi-verify-red-items (WS3, `data/manual`, `research/`)
- T-022 us-ports-nacs (parked to phase 4)

### Wave 6 — Charging buildout Core 1 + bidi filters + schemas
- T-023 schema-charging-stats (WS0, `packages/schema`)
- T-030 schema-trip-fit (WS0, `packages/schema`)
- T-044 schema-variant-clue (WS0; overnight run tonight)
- T-024 charging-taxonomies-seed (WS3, `data/taxonomy`, `config/`) — after T-023
- T-026 web-charging-linkouts (WS2, `apps/web`) — after T-024
- T-027 learn-charging-2026 (WS3 content + WS2 page)
- T-020 web-bidi-filters (WS2, `apps/web`) — after T-019
- T-041 verify-listing-templates (WS3, `config/countries`)
- T-040 appinfra-add-app + EV staging (WS4, `infra/`)

### Wave 7 — Data for charging and Trip fit
- T-025 charging-stats-ingest (WS1) — after T-023, T-024
- T-031 trip-fit-seed (WS3) — after T-030
- T-032 consumption-tests-ingest (WS1) — after T-030
- T-033 consumption-model (WS1) — after T-031, T-032
- T-034 climate-normals (WS1)
- T-035 back-test-harness (WS1) — after T-033
- T-029 abrp-typecode-top40 (WS3) — after T-023
- T-036 web-trip-quick-check (WS2, Core 1) — fixture matrix until T-033
- T-039 learn-winter-range (WS3)
- T-037 valhalla-box (WS4)
- T-028 web-country-charging-pages (WS2, Core 2) — after T-025

- T-045 web-differences-timeline (WS2, Core) — Variant finder, Decision 019
- T-046 clue-types-and-top40-clues (WS3) — after T-044
- T-047 lookalike-groups (WS1) — after T-044, T-046
- T-049 rdw-plate-vin-research (WS1 + WS3)
- T-043 price-modes (WS3 finance_profiles + WS2 UI; schema WS0)

### Wave 8 — Trip fit Core 2
- T-048 web-spot-it-box (WS2) — after T-046, T-047
- T-038 web-trip-routes (WS2) — after T-033, T-034, T-037

## Blocked
- Overnight review (step 4 of the handoff) waits for MORNING.md on `proto/overnight-1`.
- Real data in production waits for off-site backups (AppInfra #93).

## Workstreams and file ownership

Workstreams talk through `workstreams/<ws>/INBOX.md`, never through Menno (Decision 014). Full table and rules: [workstreams/README.md](workstreams/README.md).

| Owner | Paths |
|---|---|
| WS0 coordinator | AGENTS.md, CLAUDE.md, BOARD.md, QUESTIONS.md, DECISIONS.md, ROADMAP.md, CHANGELOG.md, docs/spec/, packages/schema/, tasks/, research/, audits/, workstreams/README.md + */START.md, .github/ (not image workflows) |
| WS1 pipeline | pipeline/ (not Dockerfile), data/sources.yaml, data/field_sources.yaml, data/SOURCES.md, data/releases/, data/review/ |
| WS2 web | apps/web/ (not Dockerfile) |
| WS3 curation | data/seed/, data/manual/, data/taxonomy/, content/, config/ |
| WS4 infra | infra/, pipeline/Dockerfile, apps/web/Dockerfile, .github/workflows/image*.yml |
| WS5 growth | docs/outreach/, docs/growth/, docs/brand/ |
| UX design | docs/design/ |
| each WS | its own workstreams/<ws>/STATUS.md and HANDOFF.md; INBOX.md files are append-only for everyone |

## Done
- 2026-11-15: spec mirrored to docs/spec; workstreams WS0–WS5 set up; Decisions 012–014
- 2026-11-15: GitHub repo, licences, scaffold, CI skeleton, templates, security settings
