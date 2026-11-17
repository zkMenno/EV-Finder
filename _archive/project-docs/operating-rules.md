# EV Finder — operating rules for every chat and agent

_Archived 2026-11-17: verbatim copy of the claude.ai project doc `claude/operating-rules.md` (17 Nov version), moved out of the project. Superseded by docs/process/README.md._

Read this first in every new chat. These rules beat defaults. Update them after each phase retro. The short version that lives in Project Settings is kept in claude/project-instructions.md.

## 1. Autonomy and decisions
- Default: reason through the options, pick the recommended one, do it, and log it in DECISIONS (one line: date, decision, why). Menno does not need to approve routine choices and often won't follow the technical detail.
- Each workstream takes Decision numbers from its own block (listed at the top of DECISIONS.md), so parallel chats never clash.
- Choose the option that is ready for the future: growth, more countries, edge cases, stress. Config and data tables over hard-coded logic.
- Ask Menno (question popups, max 4 at once, recommended option first) only when a choice is:
  - money: more than about €50/month or any one-off over €200;
  - irreversible or public: deleting data, public launch, the brand name and domain, legal or licence risk;
  - sent in his name: emails, outreach, posts (draft them, he approves sending);
  - a change of scope or strategy.
- If Menno isn't there to answer, take the recommended option where it's reversible, park it where it isn't, and keep going on everything else.

## 2. The message bus is the repo, not Menno
- Menno never relays messages between chats. Chats talk through markdown files in github.com/zkMenno/EV-Finder.
- Shared files: `BOARD.md` (status of everything), `QUESTIONS.md` (only things Menno must answer), `DECISIONS.md` (engineering + product decisions), `CHANGELOG.md`, `REVIEW.md` (review checklist), `docs/process/rules.md` (rule register), `docs/spec/` (the spec, exported from the claude.ai doc).
- Per workstream: `workstreams/<ws>/START.md` (its start prompt), `STATUS.md` (top lines: state, now, next, blocked, last updated), `INBOX.md` (append-only messages to that workstream: date, from, message).
- Every chat reads its INBOX at the start and after every task, and writes to another workstream's INBOX instead of asking Menno to pass it on.
- Before starting work, check open PRs and their HANDOFF/STATUS: the newest state may not be on main yet.
- Every new chat attaches the repo with **push access** (add_repo zkMenno/EV-Finder, access push) before doing anything else.
- File ownership to avoid overwrites: each file has one owning workstream (listed in BOARD.md). Others write to the owner's INBOX. Always read a file right before writing it, and make small edits instead of rewrites.
- WS0 processes its INBOX at least once per working session; if WS0 is idle for more than a day, the next chat that notices tells Menno in one line.

## 3. Workstreams (max about 7 long-running chats)
| Id | Workstream | Where it runs | Owns |
|---|---|---|---|
| WS0 | Coordinator: spec, research, planning, merges, gate files | claude.ai project chat with repo attached | BOARD, QUESTIONS, DECISIONS, REVIEW.md, docs/process/, docs/spec, workstreams/*/START.md, CI gate config, claude/project-instructions.md, claude/operating-rules.md |
| WS1 | Data pipeline: sources, matching, releases, coverage | Claude Code on the repo | pipeline/, data/ |
| WS2 | Web app: Explore, pages, compare, rankings, i18n | Claude Code on the repo | apps/web/ |
| WS3 | Catalogue curation: generations, maker-doc facts with citations, glossary and /learn texts | Claude Code or project chat | data/seed/, data/manual/, content/ |
| WS4 | Infra: AppInfra add-an-app, deploy, backups, monitoring | 🌐📱 chat with AppInfra rights | deploy/, infra notes |
| WS5 | Partnerships and growth: permissions, marketplace pitches, name and domain, SEO, launch | claude.ai project chat | docs/outreach/, docs/growth/ |
| QA | Fresh-eyes reviewer: walks the app, runs REVIEW.md, audits | Claude Code on the repo | audits/, `## Review` sections of task files |
Menno opens a workstream chat by pasting one line: "Read workstreams/<ws>/START.md and go."

## 4. Long tasks and loops
- Plan first, then work in chunks. About every 30 minutes on long tasks: commit, push, update STATUS.md.
- Loop guard: the same error 3 times, or no real progress in 30 minutes, means stop that path. Log what was tried, try one different approach, otherwise park it with a note in STATUS.md and QUESTIONS.md if Menno is needed, and move on to the next task.
- Time-box research: answer the question, don't explore everything.
- Never sit idle waiting for an answer: skip to the next unblocked task.
- Git: never rebase a pushed branch (merge main in instead); after a push from a Claude session, start CI with workflow_dispatch and trust the run on the PR head; if `gh pr create` fails, use `gh api repos/.../pulls`.

## 5. Context hygiene
- Long chats lose detail when they get compacted. Watch for it: many large tool results, several long documents read, hours of work, or any compaction warning.
- Before that point: write `workstreams/<ws>/HANDOFF.md` (state, decisions made, open threads, next steps, links), commit it **straight to main** (small docs commit, not inside an unmerged PR), and give Menno a one-line new-chat prompt that points to it.
- Files are the memory. Chats are disposable.

## 6. Efficiency (tokens, time, decisions)
- Read only what you need: search and partial reads over whole files. Don't paste big documents back into chat.
- Run independent tool calls in parallel; use subagents for parallel lanes inside a coding session.
- Reuse existing libraries, AppInfra patterns and earlier decisions; read DECISIONS before redesigning anything.
- Replies to Menno: one screen on mobile, plain language, 🟢 verified / 🟡 reasoned / 🔴 unsure, lead with anything he must do, end with one next step. Show evidence (screenshots, numbers, links), not claims.

## 7. Quality bar
- Every number traces to a Fact with a source; at least 2 sources per headline field where possible (see the Source matrix).
- Tests and CI green **on the PR head commit** before review; a fresh reviewer checks the REVIEW.md items the diff triggers. A review counts for one commit only.
- After each big batch (about 10 merged tasks or a phase gate): security review, dependency audit, load test, data-quality check.
- Simple by default, nerdy on demand: plain labels and tooltips everywhere.
- Metric units, euros by default, six languages, WCAG 2.2 AA.
- Honesty: flag licences, terms of service and uncertainty; never invent data; mark estimates.

## 8. Retro and keeping the rules alive
After each phase, overnight run or long session: five minutes, four questions.
1. What slowed us down?
2. What did Menno have to do by hand?
3. What did a check miss (bug found later by QA, a back-test, Menno or a revert)?
4. Which rule or check would have prevented it?
Write the answers at the bottom of your STATUS.md and send the proposals to WS0's INBOX. WS0 accepts (and enforces) or rejects each one within a day, records it in docs/process/rules.md, and adds lasting lessons to the list at the end of this file.
When a rule here changes in a way that affects the short version, WS0 also updates claude/project-instructions.md (new version + changelog line) and tells Menno to re-paste the block into Project Settings.

## 9. Verification and learning loops
Why: verification is what lets many agents work in parallel without Menno checking every change. The human role is to define "done" and look at evidence, not to read diffs. (Source: the Claude Code team's verification article, 17 Nov 2026 analysis; tasks T-120–T-129.)

**Prove it before you call it done**
- Each lane has a `verify` skill close to its code (apps/web, pipeline). Run it before every commit that changes what users see or what the data says.
- Web: walk the flows the diff touches from `apps/web/e2e/feature-map.yaml`; screenshots at 360 and 1280 px, light and dark, one non-English language.
- Data: rebuild the release from recorded inputs, run the release diff against the previous release, back-tests, a dry run of changed rules on real rows, and the tricky-car spot list.
- Put the evidence pack in the PR body. End every commit with `Verified: <how>` (`none (reason)` is allowed; leaving it out is not). Unverified work can be listed with `git log --grep="Verified: none"`.

**Keep checks out of reach of the change**
- Gate files (CI workflows, REVIEW.md, AGENTS.md files, QA thresholds, test config, perf budgets) change only in their own PR, approved by WS0. The `gate-guard` CI job enforces this (observe first, then enforce).
- Reviewers read REVIEW.md from `main`, never from the PR branch.
- Never delete or skip a test, raise a threshold or loosen a check to get green. If a test really is wrong, say so in a `Test-change:` line in the PR body.

**Review: one good reviewer, several rounds**
- No one merges unreviewed work, own PRs included. Reviewer = QA, another chat, or a subagent without the build context, running the REVIEW.md items the diff triggers (usually 3–10), with evidence per item.
- Rate findings must-fix / should-fix / nit / pre-existing. Pre-existing problems are logged, not blamed on the author.
- Later rounds build on earlier findings instead of starting over. Up to 3 fix rounds, then escalate to WS0.
- Tune the one reviewer (REVIEW.md, prompts) rather than stacking more reviewers.

**Tests that teach the right thing**
- Cheap checks first (lint, types, unit), heavy ones (e2e, release rebuild, back-tests) before committing and in CI.
- Prefer checks that are hard to fool: end-to-end flows, property tests (round-trip, invariants, idempotency, equivalence), and release-to-release diffs with an approved-changes list.
- Flaky tests: never skip, add sleeps or retry until green. Find the cause in 30 minutes, or delete the test, log why in the rule register and open a task to replace it.
- Tests never call the network; fixtures only.

**Every miss becomes a check**
- Any bug found after merge gets a row in `docs/process/rules.md`: what slipped, which check now catches it (test, CI job, hook or REVIEW item), owner, date.
- Prefer enforcement by tool (tests, CI, hooks) over a sentence in a rules file. Prose-only rules are marked as such in the register.
- After launch, test the reviewer itself against the bugs we really had (T-129): recall on known misses, false alarms on clean PRs.
- Prune each phase: rules, REVIEW items and tests that never fire or never catch anything are merged or removed, so the rules stay short enough to follow.

## Lessons so far
From the first build chat (Nov 2026):
- Two chats edited the same decisions file and nearly overwrote each other → file ownership + read-before-write.
- The overnight build couldn't read the claude.ai spec → export the spec into the repo (docs/spec/) and keep it in sync.
- Menno was relaying AppInfra answers by hand → workstream INBOX files.
- Server facts were guessed before they were measured → measure first (capacity check), then size.
- Project instructions lived only in a chat message → kept as a versioned file (claude/project-instructions.md).

From the 15–17 Nov workstream retros and the verification review (17 Nov):
- A stale release shipped with a report describing results it didn't contain (A-20 B1) → verify pipeline + release diff; reports must match the verify output.
- The worst data bugs (wrong EPA matches, 22 % model inconsistency) were found by back-tests, not reviewers → back-test section for every derived model; dry run on real rows first.
- Decision numbers clashed several times → number blocks per workstream + a CI duplicate check.
- A chat started from a stale HANDOFF that sat in an unmerged PR → HANDOFF straight to main; check open PRs first.
- Launch tasks were merged without a fresh reviewer while WS0 was idle → no merge without review; QA workstream; WS0 idle alert.
- Retro proposals sat in STATUS files and were never adopted → WS0 processes them within a day into the rule register.
