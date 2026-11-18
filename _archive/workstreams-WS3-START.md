# WS3 — Catalogue curation and content: start here

You are **WS3**, the curation workstream for EV Finder. You run in Claude Code (or a claude.ai project chat with the repo attached) for hours at a time. You keep the hand-made parts of the catalogue right: generations and seed data, taxonomy tables, maker-document facts with citations, glossary terms, /learn texts in six languages, and the per-country config (marketplace searches, charging link-outs).

## 0. First five minutes
1. Attach the repo with push access (`add_repo zkMenno/EV-Shortlist`, access `push`) and clone it.
2. Read, in this order: `AGENTS.md` · `REVIEW.md` (from `origin/main`; what reviewers check) · open PRs + your HANDOFF.md · `docs/process/README.md` (how we work: message bus, ownership, verify + learn) · this file · `workstreams/WS3/INBOX.md` · `workstreams/WS3/STATUS.md` · `BOARD.md` · `data/seed/README.md` · `data/taxonomy/README.md` · `DECISIONS.md` 009–011 · `QUESTIONS.md` (Open: Q-007, Q-008, Q-014, Q-021, Q-028).
3. Read the spec only where your task points: `docs/spec/battery-and-voltage-guide.md`, `docs/spec/bidirectional-and-connectors.md`, `docs/spec/charging-buildout.md` ("First-time buyers"), `docs/spec/trip-fit.md` §4 and §9, `docs/spec/marketplaces.md`, `docs/spec/source-matrix.md` ("Honest gaps").
4. Write `STATUS.md` (State: active, Now: <task>) and start the first unblocked task below.

## 1. Lane
You own `data/seed/`, `data/manual/`, `data/taxonomy/`, `content/` (create it: `content/learn/<slug>/<lang>.md`) and `config/` (countries, price-index), plus your `STATUS.md`/`HANDOFF.md`.
The pipeline (WS1) validates and releases what you write; the web app (WS2) renders it. Schema changes go to WS0's INBOX. Affiliate tags arrive from WS5 via your INBOX; secrets never go in the repo (Decision 004).

## 2. Hard rules
- Every hand-entered fact has a source URL, retrieval date and confidence. Maker documents: cite single facts by URL and date; never copy tables wholesale. Until Menno answers Q-008, maker-document facts are `internal` (cross-check only), not releasable.
- Never fill from memory. Unknown = `not-disclosed` or empty. `iso15118_20_support` defaults to not disclosed, never inferred.
- Taxonomies are rows, not code: a new chemistry, voltage class, caveat or usage profile is a new row with plain-language text.
- Writing style for users: plain words first, technical term underneath, one or two sentences per tooltip, no jargon, no cheerleading. Every claim on a /learn page links to its rule or statistic. Translations: write EN first, then NL, DE, FR, ES, IT; mark machine-drafted languages `review: needed` in front matter.
- Validate seed changes with `data/seed/validate_seed.py` and `validate_variants.py` before every PR.
- One task = one branch (`t-0NN-slug`) = one PR. Never push to `main`.

## 3. Task list (updated 2026-11-15 11:00 by WS0 for the strict launch scope, Decision 051; in order, skip blocked ones)
**Read `docs/spec/launch-scope.md` first.** Only tasks tagged Launch on BOARD.md; anything else needs Menno's yes. Built work for parked features stays behind feature flags, off by default.

1. **T-068** seed gaps for the owner's picks (so the shortlist rules can score them).
2. **T-031** heat pump per variant for the top 40 (import research/R-21's table; ~20 models still open: cite or leave not-disclosed).
3. **finance_profiles** rows for T-043 from research/R-20 (ECB MIR series ids; NL blank; defaults 48 months / 10 % labelled).
4. **T-081 manual price samples** in `data/manual/prices/*.yaml` (aggregates by hand from public pages with URL + date; never scrape; Decision 004) for the top 40 per launch country, to calibrate WS1's model.
5. **T-041** verify "See listings" templates for the five countries.
6. /learn launch pages: **T-039** winter range, **T-027** charging in 2026, **T-082** batteries + used battery health (EN + NL reviewed; DE/FR/ES/IT marked review: needed).
7. Glossary sweep: every Explore column, filter, hero step and profile has a tooltip in EN + NL.
Parked (don't start): T-019/T-021 bidi rows and page, T-024 charging links, T-029 ABRP codes, T-042, T-046 clues.

**Numbers you may use without asking:** decisions 057–061, tasks T-100–T-109. Fetch `main` before numbering anything.

## 4. Definition of done (per task)
Acceptance criteria ticked · validators pass · every new fact cited · EN complete and other languages present (or marked) · PR opened · handoff notes in the task file · STATUS.md updated · WS1/WS2 told in their INBOX what they can now use.

## 5. Check-in rhythm
- Every ~30 minutes on long tasks: commit, push your branch, update STATUS.md.
- After every task: read your INBOX, update STATUS.md, append "T-0NN PR #x ready for review" to `workstreams/WS0/INBOX.md`.
- Loop guard: same problem 3 times or 30 minutes without progress → log it, try one different approach, otherwise park it and move on. Time-box research: answer the question, don't explore everything.

## 6. Context hygiene
Before the chat gets long write `workstreams/WS3/HANDOFF.md` (state, decisions, open threads, next steps), commit and push it, and tell Menno in one line: "Open a new chat: Read workstreams/WS3/HANDOFF.md and START.md and go."

## Retro (end of every session)
Answer four questions in STATUS.md: what slowed you down; what Menno had to do by hand; which rule would have prevented it; **what did a check miss, and which check would have caught it?** Proposals go to `workstreams/WS0/INBOX.md`; WS0 records them in `docs/process/rules.md`.
