# Decisions — EV Finder

Engineering decisions for this repo, in a light ADR (Architectural Decision Record) format. Each entry has a number, status, date, context, decision and consequences. Never edit an accepted decision; supersede it with a new one.

**Product decisions** (scope, markets, business) live in the project decisions log and the Master spec v2: https://claude.ai/artifact/3HiNR86a22Fnm2kHxpfctx. This file records the ones that shape the code.

**Statuses:** Proposed · Accepted · Superseded by NNN

---

## Decision 001: Adopted agentic scaffold and the agent workflow

**Status:** Accepted
**Date:** 2026-11-15

**Context:** The project is built by one person with many AI agents. Chats and sessions forget; files don't. Agents need shared rules, clear lanes and a place to hand off work.

**Decision:** Use the Agentic Scaffold pattern (AGENTS.md as canon, CLAUDE.md as wrapper, DECISIONS, CHANGELOG, ROADMAP) plus the workflow from the spec's Workflow tab: `BOARD.md`, `QUESTIONS.md`, `tasks/`, `research/`, `audits/`, five roles, one lane per builder.

**Consequences:**
- Agents have clear instructions from session one.
- Menno touches three things: `QUESTIONS.md`, the daily digest and phase gates.
- A few extra files, each with one job.

**Alternatives considered:** README only (not enough for agents); a project-management tool outside the repo (agents can't read it reliably).

---

## Decision 002: Public repo; AGPL-3.0 for code, CC BY 4.0 for published data

**Status:** Accepted
**Date:** 2026-11-15

**Context:** A public repo gets GitHub Actions minutes free on standard runners, plus free secret scanning. The project is mission-driven and open-source-first, but a closed clone of the hosted site would undercut it.

**Decision:**
- Repo is public.
- Code is licensed under **GNU AGPL-3.0** (`LICENSE`): anyone running a modified version as a network service must publish their changes.
- Data we publish openly is licensed under **CC BY 4.0** (`DATA_LICENSE.md`). Third-party inputs keep their own licences; ODbL inputs are never mixed into CC BY sets.
- Outside contributions require agreeing to the relicensing clause in `CONTRIBUTING.md`, so the maintainer can still change the licence later.

**Consequences:**
- Free CI and security tooling.
- Competitors can read the code, but can't run a closed fork as a service.
- Strategy-sensitive config must stay out of the repo (see 004).

**Alternatives considered:** MIT (allows closed SaaS clones); FSL/BSL source-available (not OSI open source, less community goodwill); no licence (blocks contributions).

---

## Decision 003: Lean monolith + separate data pipeline, one EU server

**Status:** Accepted
**Date:** 2026-11-15 (product decision 2026-11-14)

**Context:** A solo builder with AI agents must be able to understand, run and fix everything.

**Decision:** One monorepo with `apps/web` (Next.js + TypeScript), `pipeline/` (Python + Dagster, DuckDB + Parquet), `packages/schema` (JSON Schema → generated TS and Python types) and `infra/`. One Postgres database. pg-boss for jobs (no Redis). Better Auth for passkeys and magic links. Hosted on Hetzner via Coolify, Bunny CDN, S3-compatible object storage for raw fetches. Self-hosted Umami, GlitchTip and Uptime Kuma.

**Consequences:**
- The pipeline writes catalogue releases; the web app only reads them (and writes user data).
- Scale steps happen only on triggers (spec §13): Meilisearch above ~100k listings, a read replica above ~60% DB CPU, the pipeline on its own server if runs collide with traffic.

---

## Decision 004: Keep sampling targets and partner secrets out of the public repo

**Status:** Accepted
**Date:** 2026-11-15

**Context:** Automated used-price sampling (layer 3) carries ToS and EU database-right risk and needs a legal check before going live. Publishing exactly which sites we sample, and how often, adds risk and gives away strategy. Affiliate and partner credentials are secrets.

**Decision:** The code for sampling is generic and public. Target sites, URL templates for sampling, rates, kill-switch state and all partner/affiliate credentials live in runtime config (Coolify environment, or a private config repo), never in this repo. "See listings" deep-link templates (public, user-facing links) may live in the country config.

**Consequences:** `.env.example` documents variable names only. Reviewers reject PRs that hard-code targets or keys. GitHub secret scanning and push protection are on.

---

## Decision 005: Build images in GitHub Actions, not on the server

**Status:** Proposed
**Date:** 2026-11-15

**Context:** The app will share an existing Hetzner ARM server running Coolify. Building Next.js on the server peaks at 2–4 GB RAM and can starve other services. Public repos get free Actions minutes, including arm64 runners.

**Decision:** CI builds arm64 Docker images for `apps/web` and `pipeline`, pushes them to GitHub Container Registry, and Coolify pulls and runs them. Run the Dagster UI only on demand at first.

**Consequences:** Likely no server upgrade at launch (to be confirmed once current free RAM is known). Adds a deploy workflow in Phase 0 (`infra` lane).

**Open:** confirm server tier and free RAM → accept or revise.

<!-- Agentic Scaffold v0.5.0 | https://github.com/montymerlin/agentic-scaffold-plugin -->
