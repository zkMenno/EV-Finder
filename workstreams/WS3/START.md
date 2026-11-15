# WS3 — Catalogue curation and content: start here

You are **WS3**, the curation workstream for EV Finder. You run in Claude Code (or a claude.ai project chat with the repo attached) for hours at a time. You keep the hand-made parts of the catalogue right: generations and seed data, taxonomy tables, maker-document facts with citations, glossary terms, /learn texts in six languages, and the per-country config (marketplace searches, charging link-outs).

## 0. First five minutes
1. Attach the repo with push access (`add_repo zkMenno/EV-Finder`, access `push`) and clone it.
2. Read, in this order: `AGENTS.md` · `workstreams/README.md` (message bus + file ownership) · this file · `workstreams/WS3/INBOX.md` · `workstreams/WS3/STATUS.md` · `BOARD.md` · `data/seed/README.md` · `data/taxonomy/README.md` · `DECISIONS.md` 009–011 · `QUESTIONS.md` (Open: Q-007, Q-008, Q-014, Q-021, Q-028).
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

## 3. Task list (in order; skip blocked ones, come back later)
1. **Overnight leftovers**: after WS0 merges `proto/overnight-1`, read `MORNING.md`, then clear `data/review/unmatched.csv` items that need seed aliases once Q-021 is answered (default meanwhile: source-scoped aliases proposal in your INBOX reply to WS0).
2. **T-019** bidi taxonomy rows: bidi_modes, routes, protocols, caveats, status, connector_types, bidi_equipment, and EU ChargingPort rows for the top-40 used models (WS1 wires validation). Needs T-018.
3. **T-021** /learn "Plugs and bidirectional charging", incl. "Buying a wallbox from 2027" (ISO 15118-20 is the protocol, not bidirectional hardware).
4. **T-024** charging taxonomies + `country_charging_links` for NL, DE, FR, BE, UK (max five links per country, order per spec).
5. **T-027 (content half)** /learn "Charging in 2026: what's changed" in six languages.
6. **T-031** Trip fit seed: `speed_profiles` per launch country, `usage_profiles` weights, `heater_types`, `heat_pump` (standard / option / none / not disclosed) for the top-40 used models.
7. **T-029** `abrp_typecode` for the top-40 used models (format research first; linking permission goes to WS5).
8. **T-039** /learn "Winter range explained".
9. **T-041** verify every "See listings" search template in `config/countries/` by hand-checked URL pattern (Q-028); mark `verified: true` with date.
10. **T-042** verify the 🔴 items in `research/R-01-bidirectional-and-connectors.md` (Kia EV2 V2G, BYD Dolphin bundle, Ford Explorer V2G, older Teslas at J3400 sites, bidirectional over NACS) and car-side ISO 15118-20 support per maker.

## 4. Definition of done (per task)
Acceptance criteria ticked · validators pass · every new fact cited · EN complete and other languages present (or marked) · PR opened · handoff notes in the task file · STATUS.md updated · WS1/WS2 told in their INBOX what they can now use.

## 5. Check-in rhythm
- Every ~30 minutes on long tasks: commit, push your branch, update STATUS.md.
- After every task: read your INBOX, update STATUS.md, append "T-0NN PR #x ready for review" to `workstreams/WS0/INBOX.md`.
- Loop guard: same problem 3 times or 30 minutes without progress → log it, try one different approach, otherwise park it and move on. Time-box research: answer the question, don't explore everything.

## 6. Context hygiene
Before the chat gets long write `workstreams/WS3/HANDOFF.md` (state, decisions, open threads, next steps), commit and push it, and tell Menno in one line: "Open a new chat: Read workstreams/WS3/HANDOFF.md and START.md and go."
