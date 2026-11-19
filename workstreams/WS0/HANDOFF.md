# WS0 handoff (2026-11-19 11:40 UTC, coordinator https://claude.ai/code/session_01JuyZEWR468Ux4ydBhjKYsp)

Resumed 11:15 UTC after a short pause (09:30–10:58). Pause procedure: G-58 (HANDOFF + an INBOX line + every open task Status).

Repo: **zkMenno/EV-Shortlist** (use it for add_repo and every `gh api repos/zkMenno/EV-Shortlist/...`; GraphQL and branch deletion are blocked by the proxy, use REST). Shallow clones: `git merge origin/main` can say "unrelated histories"; `git fetch --deepen=50 origin main` fixes it.

## How we work
One named chat: the coordinator (WS0). Everything else is a throwaway batch chat (one task or a small batch, merges included, fresh subagent review before every merge, G-52 behind_by check in its own step). Every prompt: "Attach the repo with push access (add_repo zkMenno/EV-Shortlist, access push)". Menno: one mobile screen, plain language, 🟢/🟡/🔴, paste prompts in code blocks. The coordinator may merge its own docs / gate PRs after a fresh PASS.

## State
- Data release 3 is live (`data-v3`); **release 4 not built yet**. Its approvals: #177, #184, #189, and #190 once merged.
- Decisions up to **088** (trim-line version rule). Next free WS0 decision: **089**.
- Tasks up to **T-161**; next free **T-162**. Rules up to **G-60**; next free **G-61**.
- Done: T-149 to T-155. Open PRs: **#190 (gate) + #191 (T-156)**, not reviewed yet.

## Next batch chats (prompts given to Menno 2026-11-19 11:40 UTC)
1. Catalogue: review + merge #190 then #191 (T-156), then **T-160** (Elroq alias + hold removal in ONE change first).
2. Data matching: **T-159** (ties, other trims' versions, year-only splits, Model Y Performance WLTP, optional fingerprint).
3. Data rules + tools: **T-161** (Decision 088, DC claim mark, nits, wording), then **T-158** (verify / merge tools, G-52–G-57, lock nits).
- After those: build and publish **release 4**, then **T-157** (WS2: popularity from release, unpack images.tar).

## Parked / later
- OpenEV `markets` filter: parked (zero-diff allowlist design in INBOX 2026-11-18 19:14).
- T-142 data pipeline hardening (report first) and a QA review on the newest release.
- PR-body checker recounting "main has N" claims (T-155 retro): parked.
- T-158 optional: the stale-lock takeover race (#185 nit 3).
- BOARD.md "Now" list is from 17 Nov: refresh it.

## Coordinator doc should-fixes (small, batch into one docs PR)
- R-30:85 wording; stale lines in lane START files; G-44 / G-41 and REVIEW D4 / D8 wording; G-38 "Enforced by" names parked T-117.
- infra/AGENTS.md rules 1–2 out of date since CI deploys staging (gate PR); infra/README.md old "apply by hand" wording.
- T-158 edits docs/process/README.md (WS0 file): log it in rules.md when it lands.

## Menno by hand
- Delete branches `fix/agents-t141-ariakit` and `t-136-extra-models-2nd-chat` in the GitHub UI (proxy blocks deletion).

## Runs on its own when idle
GitHub Actions only (no Claude tokens): weekly data refresh (Mondays 03:17 UTC) opens or updates a data release PR; Dependabot patch / minor PRs merge themselves when green. Data PRs wait for a chat to review and merge them.
