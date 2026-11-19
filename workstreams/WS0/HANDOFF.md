# WS0 handoff (2026-11-19 17:10 UTC, coordinator https://claude.ai/code/session_01JuyZEWR468Ux4ydBhjKYsp)

Resumed 11:15 UTC after a short pause (09:30–10:58). Pause procedure: G-58 (HANDOFF + an INBOX line + every open task Status).

Repo: **zkMenno/EV-Shortlist** (use it for add_repo and every `gh api repos/zkMenno/EV-Shortlist/...`; GraphQL and branch deletion are blocked by the proxy, use REST). Shallow clones: `git merge origin/main` can say "unrelated histories"; `git fetch --deepen=50 origin main` fixes it.

## How we work
One named chat: the coordinator (WS0). Everything else is a throwaway batch chat (one task or a small batch, merges included, fresh subagent review before every merge, G-52 behind_by check in its own step). Every prompt: "Attach the repo with push access (add_repo zkMenno/EV-Shortlist, access push)". Menno: one mobile screen, plain language, 🟢/🟡/🔴, paste prompts in code blocks. The coordinator may merge its own docs / gate PRs after a fresh PASS.

## State
- Data release 3 is live (`data-v3`); **release 4 not built yet**. Its approvals: #177, #184, #189, #190, #194, #196, #198 (+ any from open work).
- Decisions up to **088**; next free **089**. Tasks up to **T-165**; next free **T-166**. Rules up to **G-63**; next free **G-64**.
- Done: T-149–T-156, T-158, T-160, T-161 (claim item → T-163). Schema has `PublishedVariant.dc_speed_is_claim` (#205).
- **Not processed yet:** INBOX 17:40 UTC (batch: data T-159; part 2 was still in review at 17:00).

## Next batch chats (prompts given to Menno 2026-11-19 ~17:10 UTC)
1. Catalogue: **T-162** (re-cite MX-30 + EV6 63, Elroq 85 DC check, Model X gen1, Citigo e / Mii, EV9, Marvel R, Sealion 7).
2. Data: **T-163** (TGK variant codes, cited power / gross reach the release, `dc_speed_is_claim` + open data), after T-159 part 2 merges (same `match/` files); then **T-164** (WS3, cite power) can start.
3. Data tools: **T-165** (G-61 seed tests + pyproject marker, G-62, G-63, CI approvals; gate files in their own PR).
- After those: build and publish **release 4**, then **T-157** (WS2: popularity from release, images.tar, DC claim badge).

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
