# WS0 handoff (2026-11-19 01:25 UTC, coordinator https://claude.ai/code/session_01JuyZEU6vsVM15dKZLB6n6K)

Repo: **zkMenno/EV-Shortlist** (use it for add_repo and every `gh api repos/zkMenno/EV-Shortlist/...`; GraphQL and branch deletion are blocked by the proxy, use REST).

## How we work now
One named chat: the coordinator (WS0). Everything else is a throwaway batch chat (one task or a batch up to ~6–7 h, merges included). Merging is a batch job, not WS0's. Group prompts per workstream, few chats. Every prompt: "Attach the repo with push access (add_repo zkMenno/EV-Shortlist, access push)". Menno: one mobile screen, plain language, 🟢/🟡/🔴, paste prompts in code blocks.

## State
- Data release 3 is live (#169, latest = 3): 375 variants, 119 photos, 0 blocking. EU coverage ~99 % of BEV registrations matched to seed models.
- Decisions up to **086** (photo bundle). Next free in the WS0 block: **087**. Tasks up to **T-152**; next free **T-153**.

## Open PRs
- #171 (schema fields, Decision 086, T-149–T-152) and #165 (rules G-46 / G-47): **merged** 2026-11-19 by the data batch chat.
- **#59** WS4 staging runbook: probably obsolete (staging deploys from CI). Ask WS4 or close with a note.

## Batch chats briefed 2026-11-19 (prompts given to Menno)
1. Data: merge #171, review + merge #165, then T-149 (popularity, licences, PD-old, stray-template QA) and T-150 (photo bundle, 450-asset guard, `ev verify` main/PR in data PR bodies).
2. Catalogue: T-151 (ë-SpaceTourer 50/75 split, e-Tourneo Courier Ford facts, Leaf 62 kWh duplicate, Ioniq 5 facelift battery/WLTP).
3. Web: T-152 (no unpriced fill-ins priced > 2× budget, max 3).
Possibly still running from 18 Nov: web + design follow-ups (T-146 / T-147), catalogue batch (T-148), merge sweep.

## Parked / later
- OpenEV `markets` filter: parked (blunt skip strips 28 EU-sold variants; zero-diff allowlist design in INBOX 2026-11-18 19:14).
- After the base build: T-142 data pipeline hardening (report first) and a QA review on release 3.
- WS2 follow-up once a release carries `Generation.popularity`: switch `apps/web/scripts/popularity.mjs` to the release field.

## Menno by hand
- Delete branches `fix/agents-t141-ariakit` and `t-136-extra-models-2nd-chat` in the GitHub UI (proxy blocks deletion).

## Coordinator doc should-fixes (small, batch into one docs PR)
- R-30:85 wording; stale lines in lane START files; G-44 / G-41 and REVIEW D4 / D8 wording; G-38 "Enforced by" names parked T-117.
- infra/AGENTS.md rules 1–2 out of date since CI deploys staging (gate PR); infra/README.md old "apply by hand" wording.
