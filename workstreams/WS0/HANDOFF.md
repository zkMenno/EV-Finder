# WS0 handoff: PAUSED (2026-11-19 09:30 UTC, coordinator https://claude.ai/code/session_01JuyZEWR468Ux4ydBhjKYsp)

**Building is paused** (Menno, 2026-11-19: limited tokens, other projects; maybe weeks). Last running work: the T-153 data batch chat (PRs #185, #186). Nothing else should be running. On resume, start with "First thing on resume" below.

Repo: **zkMenno/EV-Shortlist** (use it for add_repo and every `gh api repos/zkMenno/EV-Shortlist/...`; GraphQL and branch deletion are blocked by the proxy, use REST). Shallow clones: `git merge origin/main` can say "unrelated histories"; `git fetch --deepen=50 origin main` fixes it.

## How we work
One named chat: the coordinator (WS0). Everything else is a throwaway batch chat (one task or a small batch, merges included, fresh subagent review before every merge, G-52 behind_by check in its own step). Every prompt: "Attach the repo with push access (add_repo zkMenno/EV-Shortlist, access push)". Menno: one mobile screen, plain language, 🟢/🟡/🔴, paste prompts in code blocks. The coordinator may merge its own docs / gate PRs after a fresh PASS.

## State at pause
- Data release 3 is live; release 4 is approved but not yet built / published (approvals #177, #184; first night re-publishes every photo, Decision 086 bundle).
- Decisions up to **087** (any number of single facts per car from a maker document, never a whole table / price list). Next free WS0 decision: **088**.
- Tasks up to **T-158**; next free **T-159**. Rules up to **G-55**; next free **G-56**.
- Done 19 Nov: T-149, T-150, T-151, T-152 (status set), T-154 (merged #182–#184, #187; **Status still `review` → set `done`**).

## First thing on resume
1. Check T-153: are #185 / #186 merged? Read the T-153 batch's INBOX line and process it. If T-153 merged: remove the **Elroq source hold** on OpenEV "Base" (T-154 put it there; "cited power wins" replaces it) and start T-158.
2. Check whether data release 4 is published (`latest` on GitHub Releases). If yes, T-157 can start.
3. Process the INBOX line of **2026-11-19 09:15 UTC (batch: catalogue T-154)**; its asks are not done yet:
   - WS1: ties left without motor count / drivetrain evidence (EV3 LR vs AWD, EV6 facelift RWD vs AWD, Countryman E vs SE ALL4, Inster 42 vs 49) → add to T-153 follow-up or a new task.
   - **WS0 decision needed:** Decision 038's newest-version rule compares versions model-wide, so the 2025 e-tron GT entry trim made the 2024 S / RS / RS performance "older" (~−10 points). Narrow it to generation or pack before going public (new decision, reversible engineering call).
   - WS1: `manual` terms in `data/sources.yaml` still say "one figure per car per document"; update to Decision 087.
   - Retro proposals: `ev verify --base-release-from <ref>`; data_qa runs `load_config` on approved_changes.yaml → accept / reject in rules.md (gate PR).
   - Catalogue left (T-154 Handoff notes): MX-30, smart forfour 453, Model X gen1, EV6 63 kWh, Citigo / Mii, EV9, Marvel R, Sealion 7.

## Ready to start (prompts: write fresh from the task file, same shape as 19 Nov)
- **T-155** (WS1): DC speed from cited 10–80 % minutes, ë-SpaceTourer / Leaf data checks, popularity back-test.
- **T-156** (WS3): Courier 2026, SpaceTourer 75 DC, egmp-84 pack, BYD Atto 3 photo, optional list prices.
- **T-158** (WS1): `ev verify --keep`, approved_changes warning, `scripts/merge_ready.sh`. After T-153 (same verify code).
- **T-157** (WS2): web popularity from release + unpack images.tar. After release 4.

## Parked / later
- OpenEV `markets` filter: parked (zero-diff allowlist design in INBOX 2026-11-18 19:14).
- T-142 data pipeline hardening (report first) and a QA review on the newest release.
- BOARD.md "Now" list is from 17 Nov: refresh it on resume.

## Coordinator doc should-fixes (small, batch into one docs PR)
- R-30:85 wording; stale lines in lane START files; G-44 / G-41 and REVIEW D4 / D8 wording; G-38 "Enforced by" names parked T-117.
- infra/AGENTS.md rules 1–2 out of date since CI deploys staging (gate PR); infra/README.md old "apply by hand" wording.
- T-158 edits docs/process/README.md (WS0 file): log it in rules.md when it lands.

## Menno by hand
- Delete branches `fix/agents-t141-ariakit` and `t-136-extra-models-2nd-chat` in the GitHub UI (proxy blocks deletion).

## Runs on its own during the pause
GitHub Actions only (no Claude tokens): weekly data refresh (Mondays 03:17 UTC) opens or updates a data release PR, Dependabot patch / minor PRs merge themselves when green. Data PRs wait for a chat to review and merge them.
