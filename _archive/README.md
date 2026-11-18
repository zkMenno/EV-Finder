# _archive — do not read

**Agents and chats: never read, search or cite anything in this folder** unless Menno asks for a specific file. Nothing here is current; every rule, decision and status it once held lives in a live file (docs/process/, docs/spec/, DECISIONS.md, QUESTIONS.md, BOARD.md, workstreams/).

Things are moved here, never deleted, so history stays one click away for Menno.

| Path | What | Superseded by |
|---|---|---|
| `project-docs/` | Former claude.ai project docs (operating rules, decisions log + open items, 15 Nov handoff, project instructions v1.4), verbatim | docs/process/README.md, docs/spec/product-decisions.md, docs/process/project-instructions.md |
| `workstreams/OVERNIGHT/`, `workstreams/OVERNIGHT2/` | Finished overnight runs 1 and 2 (addenda, MORNING reports) | BOARD.md, CHANGELOG.md |
| `docs/spec-workflow-tab.md` | Spec "Workflow" tab mirror (15 Nov) | docs/process/README.md |
| `questions-closed.md` | Closed and triaged questions (Q-001…Q-092) | QUESTIONS.md (open), DECISIONS.md |
| `workstreams-<lane>-{START,STATUS,HANDOFF,INBOX}.md` (WS1–WS5, UX, QA; WS4/WS5/QA had no HANDOFF) | Per-lane start prompts, status logs + retros, handoffs and inboxes of the long-running lane chats, retired 2026-11-18 when every chat but the coordinator became a batch chat (#122) | `workstreams/<lane>/START.md` (lane briefs), open inbox items at the end of `workstreams/WS0/INBOX.md`, task files and PRs |

Archiving: `git mv` the file here, add a row above, fix live links that pointed to it. Owner: WS0.
| design-assets/tram-*.svg | 2026-11-17 | UX: tram illustration replaced by an electric bus (Menno) |
