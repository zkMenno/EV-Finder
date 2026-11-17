# Changelog — EV Finder

What shipped, per wave. Written at the end of each wave, not per commit. Focuses on what changed and why.

---

## 2026-11-15 — Overnight prototype 1 (waves 1–4, addenda 4–7, backlog)

A working prototype on `proto/overnight-1` (PR #1). Summary for humans in workstreams/OVERNIGHT/MORNING.md.

- **Data pipeline:** one schema (JSON Schema → TS + Pydantic) and live adapters for Open EV Data (both datasets), RDW (fleet, WLTP sample, catalogue price, type approvals, inspection defects), EEA, KBA, DfT, ADEME, fueleconomy.gov, Wikidata, Bundesnetzagentur and DfT charging statistics. Match → merge → derive → QA → release with a licence gate that fails closed, conflicts never averaged, per-field source rules, and coverage and QA reports per release. `ev refresh` updates only what changed, with snapshots, source health checks, rollback and a weekly data-PR workflow (Decisions 009, 010, 020, 021, 023, 024).
- **Catalogue:** 63 models, 81 generations, 244 variants. Top-40 used models from registration data; generations from registration and Wikidata evidence; nothing new entered from memory. Older cars still lean on low-confidence seed values.
- **Web app:** Explore with filters, cards, Simple/Detailed/Nerd, compare tray; model/generation/variant pages with Known issues, registrations per country and price modes; compare with print; rankings; /learn articles and 95 glossary terms; charging page; about/credits. Country + language URLs with hreflang (Decision 015), 5,000+ static pages, strict CSP, dark theme, axe-clean, under the 200 KB JS budget.
- **Research:** official data sources for launch countries (R-02), future markets (R-06), European expansion (R-07) and pre-2020 specs (R-08).
- **Infra:** arm64 Dockerfiles, compose and Caddy files for AppInfra (not applied), image workflow, least-privilege SHA-pinned CI with data QA, e2e and perf budget.

## 2026-11-15 — Repo set up

Created the public repo with an AGPL-3.0 licence for code and CC BY 4.0 for published data (Decision 002). Added the agent scaffold and the workflow files from the spec: AGENTS.md, CLAUDE.md, BOARD.md, QUESTIONS.md, DECISIONS.md, ROADMAP.md, a task template, and `research/` and `audits/` folders (Decision 001).

Added a CI workflow that runs repo checks on every push and pull request, and turns on web and pipeline jobs automatically once `apps/web` and `pipeline` exist. Added Dependabot for GitHub Actions, issue templates (bug, data issue, idea), a PR template, CODEOWNERS, SECURITY.md and CONTRIBUTING.md. Security settings (secret scanning, push protection, Dependabot alerts, private vulnerability reporting) and the `main` ruleset are switched on by hand in GitHub settings.

<!-- Agentic Scaffold v0.5.0 | https://github.com/montymerlin/agentic-scaffold-plugin -->
