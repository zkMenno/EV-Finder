# WS5 lane brief: partnerships and growth

For any batch chat whose prompt touches this lane. Owner: WS0 (the coordinator). How chats work: [docs/process/README.md](../../docs/process/README.md) §3; rules: [rules.md](../../docs/process/rules.md). The lane gets the permissions and partners the data depends on, prepares the brand and domain choice, and plans SEO and launch. Menno does marketing himself: the lane researches, drafts and plans; he approves anything that goes out in his name.

## Start
1. Attach the repo with push access (`add_repo zkMenno/EV-Shortlist`, access `push`); add your row to `CHATS.md`. Usually a claude.ai project chat.
2. Read `AGENTS.md`, `REVIEW.md` (from `origin/main`), `docs/process/README.md`, your task files, this brief, `BOARD.md`, `QUESTIONS.md`, `docs/spec/product-decisions.md`.
3. Before each task: check open PRs and `git ls-remote --heads origin | grep <task-id>`; stop if another chat has it (G-41). Check `docs/outreach/`, `docs/growth/`, `docs/brand/` for work already started.
4. Spec: `docs/spec/master-spec-v2.md` §1–2 and §14–16, `marketplaces.md`, `source-matrix.md` (sources needing permission), `charging-buildout.md` (SEO page ideas).

## What the lane owns
`docs/outreach/`, `docs/growth/`, `docs/brand/`. Affiliate tags and marketplace terms (for WS3's country config), permission outcomes (for WS1's source status) and decisions: one line each in `workstreams/WS0/INBOX.md`. Decision numbers: ask WS0 for a sub-range of 070–079.

## Lane rules
- Nothing is sent, posted or registered in Menno's name without his approval. Drafts live in `docs/outreach/drafts/` with status `draft` → `approved` → `sent` (Menno sets approved).
- Money over ~€50/month or €200 one-off, the brand name and domain, public launch and any legal or licence risk go to Menno as a question (via WS0's INBOX for QUESTIONS.md). Never buy a domain.
- Honesty: no invented traffic numbers or claims; say what we are and aren't (a finder, free for buyers, no paid rankings, no ads).
- Use the marketing skills in the chat (copywriting, SEO, launch, co-marketing, cold-email); run prose that goes out under Menno's name through the unslop skill.
- Partner and affiliate credentials never go in the repo (Decision 004). Never scrape marketplaces.
- Time-box research; cite sources with links and dates; mark 🟢 verified / 🟡 reasoned / 🔴 unsure.

## Verify before every push
- Every claim in a doc has a link and a date; decisions Menno must take are listed at the top. Relative links resolve.
- Commits end with `Verified: <how>`.

## Done (per task)
Document in the lane with sources · Menno's decisions listed at the top · PR · Status + Handoff notes in the task file · what's ready and what needs Menno in one WS0 INBOX line.

## Finish the batch
State lives in task files and PRs, not here. When the batch is done or blocked: one line in `workstreams/WS0/INBOX.md` (`- YYYY-MM-DD HH:MM UTC · from <chat link> · …`, with the four retro answers), then stop. No STATUS or HANDOFF files.

## Open lane threads (WS0 turns them into tasks; the lane has not run yet)
- Outreach drafts: Bjørn Nyland, Fastned, NAF/Motor (El Prix), Spritmonitor, Euro NCAP, EV Database (cross-check), ABRP, then the marketplace groups Autonex, Adevinta, Vend, OLX Group. One file each in `docs/outreach/drafts/`.
- Affiliate programmes per launch country → `docs/growth/affiliates.md`.
- Name + domain follow-up once Menno picks from `docs/brand/name-shortlist.md`: trademark classes 9/35/42 in EUIPO, BOIP, UKIPO.
- SEO plan → `docs/growth/seo-plan.md`; launch and growth plan → `docs/growth/launch-plan.md`; partnership one-pager for marketplaces.
