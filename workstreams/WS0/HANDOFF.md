# WS0 handoff (2026-11-18 10:00 UTC, merge chat https://claude.ai/code/session_01JuyZEY4DmyVTbG9HZHfzBP)

Repo: **zkMenno/EV-Shortlist** (use it for add_repo and every `gh api repos/zkMenno/EV-Shortlist/...`).

## Merged in this chat (fresh review PASS on each head, "Fresh review (WS0 subagent)" comments)
#90 #107 #108 #114 #117 #118 #112 #115 #116 #111 #120 #109 #119 #113 #106 #121.
- #111 (T-137): WS0 merged main (#117) in; #117's specs moved to `/{country}/en/cars`; the 360 px catalogue loop runs 7 launch countries in English while `ENGLISH_ONLY` (Test-change line in 937d9c3). Feature-map rubric change approved.
- WS0's own: #119 schema `GenerationImage` + optional `Generation.image` (Decision 081/083), #120 REVIEW D6 English only (Decision 082), #121 ROADMAP Ariakit + long-tail lines, process §9 English only.
- #108 R-41 tasks: 1 yes, 2 yes, 3 trimmed (no Kilowatt rows), 4 trimmed (field check first), 5 no (ROADMAP). Sent to WS1 + WS3 INBOX.

## Open
- **#110 (T-134 pipeline)**: main merged in (3292431); fresh review was running at handoff, see its PR comment. Merge if PASS + CI green. Known follow-up: licence allowlist may still be CC BY / CC BY-SA only (Decision 083 adds CC0 / worldwide PD).
- **#122 / #123** (process: one coordinator chat + batch chats; AGENTS gate) and **#124 / #125** (T-141 Ariakit brand picker + gate): opened 09:08–09:10 UTC by other chats, not in this batch, need fresh review. **#124 supersedes the "Ariakit parked" ROADMAP line from #121**: remove that line when #124 merges. Check #124's Decision 056 number (D12: number inside the writer's block, no duplicate).
- #59 staging runbook: still waits on WS4 (review asked for changes on 17 Nov; staging now deploys from CI, so it may be obsolete: ask WS4).

## Follow-ups noted
- infra/AGENTS.md rules 1–2 (agents never apply; no real domain) are out of date since CI deploys staging: gate PR (WS4 request 2026-11-17 20:05; #90 review). infra/README.md still has old "domain open / apply by hand" wording.
- Should-fixes sent: WS3 (#106 names, #113 CC0 re-pick, T-140 S7 partly fixed), WS2 (#118 redirect wording, #117 D8 screenshots in part 2), UX (#107 task files still todo), WS1 (R-41 repro scripts, #119 stricter fields).
- G-38 "Enforced by" still names `i18n.test.ts all six (T-117)`; T-117 is parked.
- My CHATS row commit trailer has a typo'd session id (log only, harmless).
- Lesson: INBOX lines pushed to main conflict with PRs that also append to INBOX/CHATS (#112 twice). Resolve by union; keep PRs off shared logs where possible.
- Older items from the previous handoff (EV6 GT versions, Ioniq 5 facelift WLTP, Model Y winter basis, cite_paths required, eafo 429, €15k road-tripper list) still stand.
