# How we work

The one process doc for every chat and agent on EV Finder. It replaces the claude.ai project doc `claude/operating-rules.md`, `workstreams/README.md` and the spec's Workflow tab (17 Nov 2026). Engineering rules for code stay in [AGENTS.md](../../AGENTS.md); product decisions in [docs/spec/product-decisions.md](../spec/product-decisions.md); review checks in `REVIEW.md` (until adopted: [draft](../../workstreams/WS0/drafts/REVIEW.md)); the rule register in [rules.md](rules.md). Owner: WS0. Change it with a small edit plus a line in [rules.md](rules.md).

Short version for Project Settings: [project-instructions.md](project-instructions.md) (WS0 updates it and tells Menno to re-paste).

## 1. Decide, don't ask
- Reason, pick the recommended option, do it, and log it in DECISIONS.md (one entry: date, decision, why). Each workstream takes numbers from its own block (top of DECISIONS.md).
- Prefer future-proof choices: config and data tables over hard-coded logic; plan for growth, more countries, edge cases and stress.
- Ask Menno only for: money over ~€50/month or €200 one-off; irreversible or public steps (deleting data, launch, brand name and domain, legal or licence risk); anything sent in his name (draft it, he approves); scope or strategy changes; his own accounts and settings. Use question popups (max 4, recommended option first, one plain sentence of why) or a short entry in QUESTIONS.md.
- Engineering judgement calls are **not** questions. Take the reversible default, write it in the task file or DECISIONS, move on.
- Menno not there? Do the reversible default, park the irreversible part, keep going.

## 2. The repo is the message bus
- Menno never relays messages. Chats talk through files in this repo.
- Shared files: `BOARD.md` (status), `QUESTIONS.md` (only what Menno must answer), `DECISIONS.md`, `CHATS.md` (every chat with its link), `REVIEW.md`, `docs/process/`, `docs/spec/`.
- Per workstream: `workstreams/<ws>/START.md` (start prompt, owned by WS0), `STATUS.md` (top block: State · Now · Next · Blocked · Last updated), `INBOX.md` (append-only: `- YYYY-MM-DD HH:MM UTC · from WSx · message`; the owner marks handled items by appending `→ done`), `HANDOFF.md`.
- Read your INBOX at the start and after every task. Before starting, check open PRs and their HANDOFF/STATUS: the newest state may not be on main yet.
- Need another workstream? Append to its INBOX. Need Menno? Ask WS0 via its INBOX (or a popup if you're talking to him).
- Read a file right before you write it, make small edits, write only files you own (§4).
- Every chat attaches the repo with push access first (`add_repo zkMenno/EV-Finder`, access `push`) and adds its row to CHATS.md in its first commit.
- WS0 processes its INBOX at least once per working session. If WS0 has been idle more than a day, the next chat that notices tells Menno in one line.

## 3. Workstreams
Menno opens one by pasting: **"Read workstreams/<ws>/START.md and go."** Aim for a handful of long-running chats. Direct links: [CHATS.md](../../CHATS.md).

| Id | Workstream | Runs in | Start prompt |
|---|---|---|---|
| WS0 | Coordinator: spec, planning, merges, gate files, process | Claude Code on the repo | (coordinator chat) |
| WS1 | Data pipeline: sources, matching, releases, models | Claude Code on the repo | [WS1](../../workstreams/WS1/START.md) |
| WS2 | Web app: Explore, pages, compare, i18n | Claude Code on the repo | [WS2](../../workstreams/WS2/START.md) |
| WS3 | Catalogue + content: seed, taxonomies, cited facts, glossary, /learn | Claude Code on the repo | [WS3](../../workstreams/WS3/START.md) |
| WS4 | Infra: AppInfra, deploy, backups, monitoring | chat with AppInfra rights | [WS4](../../workstreams/WS4/START.md) |
| WS5 | Partnerships + growth: permissions, marketplaces, name, SEO, launch | claude.ai project chat | [WS5](../../workstreams/WS5/START.md) |
| UX | Brand + design system | its own chat | [UX](../../workstreams/UX/START.md) |
| QA | Fresh-eyes reviewer: walks the app, runs REVIEW.md, audits | Claude Code on the repo | [QA](../../workstreams/QA/START.md) |

Finished one-off runs: `workstreams/OVERNIGHT/`, `workstreams/OVERNIGHT2/` (archive, read-only).

## 4. File ownership
One owner per path; others write to the owner's INBOX. Builders also edit Status + Handoff notes of their own task file; reviewers only the `## Review` section.

| Path | Owner |
|---|---|
| `AGENTS.md`, `CLAUDE.md`, `BOARD.md`, `QUESTIONS.md`, `DECISIONS.md`, `ROADMAP.md`, `CHANGELOG.md`, `REVIEW.md`, `CHATS.md` rows (each chat its own) | WS0 |
| `docs/process/`, `docs/spec/`, `packages/schema/`, `tasks/`, `research/` + `audits/` numbering, `workstreams/*/START.md` | WS0 |
| `.github/` (except `workflows/image*.yml`), gate config | WS0 |
| `pipeline/` (except Dockerfile), `data/sources.yaml`, `data/field_sources.yaml`, `data/SOURCES.md`, `data/releases/`, `data/review/` | WS1 |
| `apps/web/` (except Dockerfile) | WS2 |
| `data/seed/`, `data/manual/`, `data/taxonomy/`, `content/`, `config/` (no secrets, Decision 004) | WS3 |
| `infra/`, Dockerfiles, `.github/workflows/image*.yml` | WS4 |
| `docs/outreach/`, `docs/growth/`, `docs/brand/` (anything in Menno's name stays a draft until he approves) | WS5 |
| `docs/design/` (brand decisions: project doc `claude/brand-design-decisions.md`) | UX |
| `audits/A-35…`, task `## Review` sections | QA |
| `workstreams/<ws>/STATUS.md`, `HANDOFF.md` | that workstream |
| `workstreams/<ws>/INBOX.md` | append-only, everyone |

## 5. Tasks and flow
- One task = one file in `tasks/` (template: [tasks/TEMPLATE.md](../../tasks/TEMPLATE.md)) = one branch = one PR. About half a day of agent work.
- `todo` → claimed (name + date) → `doing` → PR → `review` → fresh reviewer passes → merge → `done`.
- Only tasks in **Launch** on BOARD.md get built (Decision 051). New ideas go to ROADMAP.md.
- After roughly every 10 merged tasks or a phase gate: security review, dependency audit, load test, data-quality check (audits/).

## 6. Long work and loops
- Plan first, then work in chunks. About every 30 minutes: commit, push, update STATUS.md.
- Loop guard: the same error 3 times or 30 minutes without progress means stop that path, log it, try one alternative, otherwise park it (STATUS.md) and take the next unblocked task. Never sit idle.
- Time-box research: answer the question, don't explore everything.
- Git: never rebase a pushed branch (merge main in); grep for conflict markers before pushing; after a push from a Claude session, start CI with workflow_dispatch and trust the run on the PR head; if `gh pr create` fails, use `gh api repos/zkMenno/EV-Finder/pulls`.

## 7. Context hygiene and efficiency
- Watch for long chats (many big tool results, long documents, hours of work, any compaction warning). Before that: write `workstreams/<ws>/HANDOFF.md`, commit it **straight to main**, and give Menno a one-line prompt for a fresh chat with the link.
- Files are the memory; chats are disposable.
- Read only what you need (search, partial reads). Run independent steps in parallel; use subagents for parallel lanes. Reuse earlier decisions and AppInfra patterns.

## 8. Verify and learn
Verification is what lets many agents work at once without Menno checking every change. His role is to define "done" and look at evidence.

**Prove it.** Each lane has a `verify` skill near its code (T-126 web, T-127 pipeline). Run it before every commit that changes what users see or what the data says. Web: walk the flows the diff touches (`apps/web/e2e/feature-map.yaml`), screenshots 360/1280 px, light/dark, one non-English language. Data: rebuild the release from recorded inputs, release diff vs the previous one (T-123), back-tests, a dry run of changed rules on real rows, the tricky-car spot list. Put the evidence pack in the PR body. End every commit with `Verified: <how>` (`none (reason)` is allowed; leaving it out is not).

**Keep checks out of reach.** Gate files (CI workflows, REVIEW.md, AGENTS.md files, QA thresholds, test config, perf budgets) change only in their own PR, approved by WS0; `gate-guard` enforces it (T-121). Reviewers read REVIEW.md from main. Never delete or skip a test or loosen a check to get green; a test that is really wrong gets a `Test-change:` line in the PR body.

**Review.** No one merges unreviewed work, own PRs included. Reviewer = QA, another chat or a subagent without the build context, running the REVIEW.md items the diff triggers, with evidence per item, rated must-fix / should-fix / nit / pre-existing. Later rounds build on earlier findings. Up to 3 fix rounds, then escalate to WS0. Tune one reviewer; don't stack reviewers.

**Tests that teach the right thing.** Cheap checks first, heavy ones before commit and in CI. Prefer checks that are hard to fool: end-to-end flows, property tests (round-trip, invariants, idempotency, equivalence), release-to-release diffs with an approved-changes list. Flaky tests: never skip, sleep or retry until green; find the cause in 30 minutes or delete the test, log why in [rules.md](rules.md) and open a task. Tests never call the network.

**Every miss becomes a check.** A bug found after merge (QA, back-test, Menno, a revert) gets a row in [rules.md](rules.md) and a test, CI job, hook or REVIEW item that would have caught it. Prefer tools over prose.

**Retro** after each phase, overnight run or long session, four questions at the bottom of your STATUS.md: what slowed us down; what did Menno do by hand; what did a check miss; which rule or check prevents it. Proposals go to WS0's INBOX; WS0 accepts (and enforces) or rejects each within a day in [rules.md](rules.md), and prunes rules that never fire once per phase.

## 9. Product bar (every lane)
- Every number traces to a Fact with source, date, confidence and licence; 2+ sources per headline field where possible; estimates labelled.
- Simple by default, nerdy on demand: plain labels, ⓘ tooltip on every term, Simple / Detailed / Nerd.
- Metric units, euros by default, six languages (EN, NL, DE, FR, ES, IT), light and dark, colour-blind safe, WCAG 2.2 AA.
- Honesty: flag licences, terms and uncertainty; never invent data.

## 10. Talking to Menno
- One mobile screen, plain language, 🟢 verified / 🟡 reasoned / 🔴 unsure. Lead with anything he must do; end with one next step. No process recaps.
- Show evidence (screenshots, numbers, links), not claims.
- Mention a file → attach it or link it (`github.com/zkMenno/EV-Finder/blob/main/<path>`). Mention another chat → its direct link **and** the exact text to paste there in a code block, every time, next-step lines included.
