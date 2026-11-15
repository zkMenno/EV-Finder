# WS2 — Web app: start here

You are **WS2**, the web-app workstream for EV Finder. You run in Claude Code on this repo for hours at a time. You build the Next.js app: Explore table, model/generation/variant pages, compare, rankings, /learn, charging pages, bidirectional filters and the Trip fit flow, in six languages, simple by default and nerdy on demand.

## 0. First five minutes
1. Attach the repo with push access (`add_repo zkMenno/EV-Finder`, access `push`) and clone it.
2. Read, in this order: `AGENTS.md` · `apps/web/AGENTS.md` · `workstreams/README.md` (message bus + file ownership) · this file · `workstreams/WS2/INBOX.md` · `workstreams/WS2/STATUS.md` · `BOARD.md` · `DECISIONS.md` 008, 010–013 · `QUESTIONS.md` (Open, anything tagged T-008…T-012 or WS2).
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

## 3. Task list (in order; skip blocked ones, come back later)
1. **Overnight leftovers**: after WS0 merges `proto/overnight-1`, read `MORNING.md` and the T-008–T-012 handoff notes; fix anything WS0 queued in your INBOX first (Q-033/Q-034 static model pages, Q-035 staff page auth, Q-026 default level once Menno answers).
2. **T-026** charging link-out block (Core 1): per-country block from `config/countries/*` on country, model and /learn pages; plain ABRP link.
3. **T-027 (web half)** render `/learn/charging-2026` from WS3's content files.
4. **T-036** Trip fit quick range check (Core 1): profile picker (5 taps), three inputs (longest regular round trip, motorway share, home town), "range you truly need" card, Explore column ✓/⚠/✗ + filter, using WS1's consumption matrix (stub with fixture until T-033 lands).
5. **T-020** bidirectional filters + caveat badges + model-page "Power out" block (wave 6, after T-019).
6. **T-028** country charging pages (Core 2, after T-025): headline cards + 3 charts, one definition per series, as-of date and source on every number.
7. **T-038** Trip fit with routes (Core 2, after T-037 Valhalla box): places + frequency, destination charging, winter step, Fit score with "why this order", model-page widget, browser storage.

## 4. Definition of done (per task)
Acceptance criteria ticked · unit tests + a Playwright check for key flows · works at 360 px wide · all strings in the i18n dictionaries (EN + NL filled, others fall back cleanly) · lint, type check, build green · PR opened with the template filled · handoff notes in the task file · STATUS.md updated · requests for other lanes written to their INBOX.

## 5. Check-in rhythm
- Every ~30 minutes on long tasks: commit, push your branch, update STATUS.md.
- After every task: read your INBOX, update STATUS.md, append "T-0NN PR #x ready for review" to `workstreams/WS0/INBOX.md`.
- Loop guard: the same error 3 times or 30 minutes without progress → stop that path, log it in STATUS.md, try one different approach, otherwise park it and move on.
- Never wait idle: take the next unblocked task.

## 6. Context hygiene
Before the chat gets long (many big tool results, hours of work, any compaction warning) write `workstreams/WS2/HANDOFF.md` (state, decisions, open threads, next steps), commit and push it, and tell Menno in one line: "Open a new chat: Read workstreams/WS2/HANDOFF.md and START.md and go."
