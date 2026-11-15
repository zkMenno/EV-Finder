# Workstreams

Long-running chats that build EV Finder in parallel. They talk to each other through files in this repo, never through Menno. The rules behind this live in the claude.ai project doc `claude/operating-rules.md`; the parts every workstream needs are repeated here and in each `START.md`.

Menno opens a workstream by pasting one line into a new chat: **"Read workstreams/<ws>/START.md and go."**

| Id | Workstream | Runs in | Start prompt |
|---|---|---|---|
| WS0 | Coordinator: spec, research, planning, review, merges | claude.ai project chat, repo attached | (the coordinator chat itself) |
| WS1 | Data pipeline: sources, matching, releases, coverage, models | Claude Code on the repo | [WS1/START.md](WS1/START.md) |
| WS2 | Web app: Explore, pages, compare, rankings, i18n, Trip fit UI | Claude Code on the repo | [WS2/START.md](WS2/START.md) |
| WS3 | Catalogue curation: seed, taxonomies, maker-doc facts, glossary, /learn texts, country config | Claude Code or project chat | [WS3/START.md](WS3/START.md) |
| WS4 | Infra: AppInfra add-an-app, deploy, backups, monitoring, routing box | chat with AppInfra rights | [WS4/START.md](WS4/START.md) |
| WS5 | Partnerships and growth: permissions, marketplaces, name, SEO, launch | claude.ai project chat | [WS5/START.md](WS5/START.md) |

## Files per workstream

- `START.md` — its start prompt (owned by WS0; a workstream proposes changes in WS0's INBOX).
- `STATUS.md` — owned by that workstream. Top block always: **State · Now · Next · Blocked · Last updated**. Update after every task and at least every 30 minutes on long tasks.
- `INBOX.md` — append-only messages *to* that workstream. Anyone may append; nobody edits or deletes old lines. Format: `- YYYY-MM-DD HH:MM UTC · from WSx · message`. The owner marks handled items by appending `→ done (commit/PR)` under them, never by deleting.
- `HANDOFF.md` — written before a chat gets long (see START.md, "Context hygiene").

## Message bus rules

1. Read your INBOX at the start and after every task.
2. Need something from another workstream? Append to **its** INBOX. Never ask Menno to relay.
3. Need Menno? Add a question to `QUESTIONS.md` (via WS0's INBOX if you don't own it) and carry on with the next unblocked task.
4. Read a file right before you write it; make small edits, not rewrites; write only files your workstream owns (table below).
5. Every chat attaches the repo with **push access** (`add_repo zkMenno/EV-Finder, access: push`) before anything else.

## File ownership

One owner per path. Others write to the owner's INBOX. Builders also append handoff notes to the `## Handoff notes` section of their own task file.

| Path | Owner | Notes |
|---|---|---|
| `AGENTS.md`, `CLAUDE.md`, `BOARD.md`, `QUESTIONS.md`, `DECISIONS.md`, `ROADMAP.md`, `CHANGELOG.md` | WS0 | QUESTIONS: others ask through WS0's INBOX; Menno answers inline |
| `docs/spec/` | WS0 | Mirror of the claude.ai spec doc; repo copy wins for builders |
| `packages/schema/` | WS0 | Only the coordinator changes the schema (AGENTS.md) |
| `tasks/` | WS0 | WS0 creates task files; the claiming builder edits Status + Handoff notes of its own task |
| `research/`, `audits/` | WS0 | WS0 numbers new R-/A- files; any workstream may write one it was assigned |
| `workstreams/README.md`, `workstreams/*/START.md` | WS0 | |
| `.github/` | WS0 | except `.github/workflows/image*.yml` → WS4 |
| `pipeline/` (except `pipeline/Dockerfile`) | WS1 | |
| `data/sources.yaml`, `data/field_sources.yaml`, `data/SOURCES.md`, `data/releases/`, `data/review/` | WS1 | |
| `apps/web/` (except `apps/web/Dockerfile`) | WS2 | |
| `data/seed/`, `data/manual/`, `data/taxonomy/`, `content/`, `config/` | WS3 | Affiliate tags in `config/` come from WS5 via WS3's INBOX; secrets never (Decision 004) |
| `infra/`, `pipeline/Dockerfile`, `apps/web/Dockerfile`, `.github/workflows/image*.yml` | WS4 | |
| `docs/outreach/`, `docs/growth/`, `docs/brand/` | WS5 | Anything sent in Menno's name is a draft until he approves |
| `workstreams/<ws>/STATUS.md`, `HANDOFF.md` | that workstream | |
| `workstreams/<ws>/INBOX.md` | append-only, everyone | |
