# WS2 — Web app: start here

You are **WS2**, the web-app workstream for EV Finder. You run in Claude Code on this repo for hours at a time. You build the Next.js app: Explore table, model/generation/variant pages, compare, rankings, /learn, charging pages, bidirectional filters and the Trip fit flow, in six languages, simple by default and nerdy on demand.

## 0. First five minutes
1. Attach the repo with push access (`add_repo zkMenno/EV-Finder`, access `push`) and clone it.
2. Read, in this order: `AGENTS.md` · `REVIEW.md` (from `origin/main`; what reviewers check) · open PRs + your HANDOFF.md · `apps/web/AGENTS.md` · `workstreams/README.md` (message bus + file ownership) · this file · `workstreams/WS2/INBOX.md` · `workstreams/WS2/STATUS.md` · `BOARD.md` · `DECISIONS.md` 008, 010–013 · `QUESTIONS.md` (Open, anything tagged T-008…T-012 or WS2).
3. Read the spec only where your task points: `docs/spec/master-spec-v2.md` §3–4 and §9–11, `docs/spec/charging-buildout.md` ("What we build", "Link rules"), `docs/spec/trip-fit.md` §3–8, `docs/spec/bidirectional-and-connectors.md`.
4. Write `STATUS.md` (State: active, Now: <task>) and start the first unblocked task below.

## 1. Lane
You own `apps/web/` (except `apps/web/Dockerfile`, WS4) and your `STATUS.md`/`HANDOFF.md`.
The app reads the published catalogue JSON (`data/releases/<latest>/`, Decision 008), glossary and copy from `data/taxonomy/` and `content/` (WS3), and country config from `config/countries/` (WS3). Need a field or a release change? Ask WS1. Need copy or a glossary term? Ask WS3 (meanwhile show the plain label; never crash on a missing term). Need a schema change? Ask WS0.

## 2. Hard rules
- Strict TypeScript, server components by default, Vitest + Playwright, pnpm (Decision 007).
- Instant before clever: Explore loads fast and works without sign-up. Filters, compare tray and display level live in the URL; the compare tray never resets.
- Simple by default: plain label first, technical term underneath, ⓘ tooltip from `glossary_terms`. Detail switch Simple / Detailed / Nerd. Nerd shows sources, dates, confidence, fallback rung.
- Metric units and euros by default; six languages (EN, NL, DE, FR, ES, IT); no hard-coded brand name (config).
- Show uncertainty: estimates are labelled, ranges say "about", DC charging is never peak kW alone.
- Privacy: cookie-less analytics only. Trip fit: addresses stay in the browser, coordinates rounded ~200 m before any request, no logging on the route endpoint, share links carry summaries, never places.
- Link-outs open in a new tab with `rel="noopener"`, text links only, no third-party logos without permission.
- One task = one branch (`t-0NN-slug`) = one PR, CI green before review. Never push to `main`.

## 3. Task list (updated 2026-11-15 11:00 by WS0 for the strict launch scope, Decision 051; in order, skip blocked ones)
**Read `docs/spec/launch-scope.md` first.** Only tasks tagged Launch on BOARD.md; anything else needs Menno's yes. Built work for parked features stays behind feature flags, off by default.

1. Overnight leftovers queued in your INBOX (theme tokens, Q-033/Q-034 now answered by Decision 015).
2. **T-080** the hero: country → profile picker → budget (+ "≈ €X/month") → optional refine → top 10 with the top 5 marked "Your shortlist". The landing page.
3. **T-067** profile picker + "Suggested" sort on Explore + Owner's note (shared with T-080; build the picker once).
4. **T-045** Compare "differences only" toggle (+ change timeline only if it's free from existing data).
5. **T-043 (loan part only)** "≈ €X/month" under every price: price, default deposit and term, typical rate per country from `finance_profiles`, CCD2 warning; no lease figures, no UK finance links.
6. **T-050 / T-012** check country + language URLs, hreflang and i18n on every launch page; EN + NL complete.
7. Render the three launch /learn pages (T-039, T-027, T-082) from `content/learn/` with glossary tooltips.
8. Open data page `/[country]/[lang]/data` (Decision 016) if not done.
Feature-flag off (don't delete): charging link-out block, Trip fit quick check (superseded by T-080), bidi bits, known issues, registration charts, rankings pages.

**Numbers you may use without asking:** decisions 052–056, tasks T-090–T-099. Fetch `main` before numbering anything.

## 4. Definition of done (per task)
Acceptance criteria ticked · unit tests + a Playwright check for key flows · works at 360 px wide · all strings in the i18n dictionaries (EN + NL filled, others fall back cleanly) · lint, type check, build green · PR opened with the template filled · handoff notes in the task file · STATUS.md updated · requests for other lanes written to their INBOX.

## 5. Check-in rhythm
- Every ~30 minutes on long tasks: commit, push your branch, update STATUS.md.
- After every task: read your INBOX, update STATUS.md, append "T-0NN PR #x ready for review" to `workstreams/WS0/INBOX.md`.
- Loop guard: the same error 3 times or 30 minutes without progress → stop that path, log it in STATUS.md, try one different approach, otherwise park it and move on.
- Never wait idle: take the next unblocked task.

## 6. Context hygiene
Before the chat gets long (many big tool results, hours of work, any compaction warning) write `workstreams/WS2/HANDOFF.md` (state, decisions, open threads, next steps), commit and push it, and tell Menno in one line: "Open a new chat: Read workstreams/WS2/HANDOFF.md and START.md and go."

## Retro (end of every session)
Answer four questions in STATUS.md: what slowed you down; what Menno had to do by hand; which rule would have prevented it; **what did a check miss, and which check would have caught it?** Proposals go to `workstreams/WS0/INBOX.md`; WS0 records them in `docs/process/rules.md`.
