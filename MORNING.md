# Good morning — overnight prototype 1

_Working title EV Shortlist (Decision 018). Branch `proto/overnight-1`, draft PR [#1](https://github.com/zkMenno/EV-Finder/pull/1). This file is refreshed after every item; the newest state is at the top of each section._

## 0. Do this first (2 minutes)
1. **Nothing to undo on `main`.** The first hour of work landed on `main` by mistake (Q-030). WS0 has built on top of it, so it stays; everything since then is in PR #1.
2. **Answer the starred questions** in section 5 when you have time. Nothing is blocked on you tonight.

## 1. What works now
Run it locally (needs Node 22, pnpm 10, Python 3.12 + uv):

```bash
git clone https://github.com/zkMenno/EV-Finder && cd EV-Finder && git checkout proto/overnight-1
pnpm install
pnpm --filter @ev/web dev          # http://localhost:3000 → redirects to /nl
# optional: rebuild the data release from recorded samples (no network)
cd pipeline && uv sync && uv run ev release
```

Checks: `pnpm --filter @ev/web test`, `pnpm --filter @ev/web e2e`, `cd pipeline && uv run pytest`.

## 2. Screens
| Route | What it is |
|---|---|
| `/nl` (also `/de`, `/fr`, `/be`, `/uk`) | Explore: one table of new + used EVs, table/cards toggle, filters (price, era, segment, body, real range, battery, DC km in 20 min, boot, length, towing, voltage class, chemistry, cooling, "fast on older 400 V chargers", "charge to 100% daily"), Simple / Detailed / Nerd, hearts, compare tray that never resets |
| `/nl/ev/<make>/<model>` | Model overview with generations |
| `/nl/ev/<make>/<model>/<generation>` | Generation page: change markers, spec diff per year, See listings, registrations per country, source + confidence on every number |
| `/nl/ev/…/<variant>` | Full spec sheet |
| `/nl/compare?ids=…` | Up to 4 side by side, differences highlighted, share + print |
| `/nl/top` | Rankings: longest real range under €30k, fastest DC (km in 20 min), most registered in NL |
| `/nl/learn/<term>` | Glossary pages |
| `/nl/about` | What we are, how numbers are made, credits for every source |
| `/health` | Health check for the server watchdog |
| `/staff/review` | Review queue (only with `STAFF_PAGES=1`) |

## 3. Data
Release 1: **218 variants** across 62 generations of 48 models across 55 generations of the 40 seed models.

| Source | Ran | Licence | Used for |
|---|---|---|---|
| Open EV Data (open-ev-data-dataset) | live | CDLA-Permissive-2.0 | base specs |
| Open EV Data (KilowattApp) | live | MIT + attribution | specs, 51 non-default charge curves (estimates) |
| RDW | live | CC0 | NL fleet counts |
| EEA CO₂ monitoring | live | CC BY 4.0 | new registrations NL/DE/FR/BE |
| KBA FZ10 | live | dl-de/by-2-0 | DE new registrations |
| DfT VEH0120 | live | OGL v3 | UK fleet |
| ADEME Car Labelling | live | Licence Ouverte | FR prices (7 variants), fallback specs |
| Seed (hand-entered) | — | CC BY 4.0 | older cars, confidence **low** |
| Bjørn Nyland | importer only | permission pending | never in a release |

Honest caveats: 🟡 every real-range and DC figure is an **estimate** tonight (ratio model, default or unverified curves). 🔴 About half of all numbers rest only on the hand-entered seed (low confidence). Coverage per field: `data/releases/1/coverage.md`.

Research (all on the branch): R-02 launch countries, R-06 future markets, R-07 European expansion.

## 4. Not done, and why
_(filled in at the end of the run)_

## 5. Questions for Menno (most important first)
_(final list at the end of the run; all are in QUESTIONS.md)_

## 6. Suggested wave 5
_(at the end of the run)_

## Addenda 4 + 5
| Item | Status | Notes |
|---|---|---|
| A4.0 sync with main, R-02 rename, Q-030 closed | done | merged main twice; my schema decision renumbered to 019 |
| A4 T-018 bidi + ports schema | done | Decision 020 |
| A4 T-023 charging stats schema | done | |
| A4 T-030 Trip fit schema | done | |
| A4 T-024 charging taxonomies + country links | done | 3–4 links per country, URLs only from the spec; DE link may be a start page, not the map (Q-057) |
| A4 T-019 bidi taxonomies (coordinator half) | done (partial) | 7 tables; 12 wallbox rows held back until their sources are releasable (Q-008); per-car rows are WS3 |
| A4 T-026 charging link-out block | done | Explore, learn and model pages; plain ABRP link; UTM tag (Q-056) |
| A4 T-036 Trip fit quick check (flag, fixture matrix) | done | behind `TRIP_FIT=1`; fixture matrix + 20 towns typed from memory, labelled PROVISIONAL; keep off in production (Q-055) |
| A5.1 country + language URLs | done | `/{country}/{lang}/…`, 11 country × language pairs, hreflang + sitemap, Accept-Language banner only; 4,301 static pages (closes Q-033/Q-034) |
| A5.2 price modes | done | Buy / Loan / Lease control in URL + storage; loan calculator with CCD2 warning; APRs from ECB/BoE consumer-credit series (not car-only); NL asks for a rate (Q-060); lease = placeholder |
| A5.3 open data bundle | done (pipeline) | `data/releases/1/open/`: CSV + JSON, 195 rows, ATTRIBUTION, LICENSE, README; ODbL test; `/data` page queued for web |
| A5.4 /learn drafts | done, rendered on /learn | 5 articles × EN + NL, 43 sources; spec vs source disagreements (NIO semi-solid, El Prix %, VW box) in Q-061 |
| A5.5 release QA | done | blocking checks pass; flags EV6 77 kWh AWD usable 80 > gross 77.4 (data bug); 0 of top-40 have 2+ agreeing sources on all headline fields |
| A5.6 security baseline | partial | done: Actions least privilege + pinned SHAs, audit job (warn only), safe fetch (host allowlist, SSRF guard, size caps); strict CSP without unsafe-inline (nonces + build-time hashes), staff basic-auth guard; server items for WS4 in audits/A-02 |
| A5.7 back-test skeleton | done | leave-one-out on synthetic fixtures; skipped on real data (no licence-cleared tests yet) |

## Bottomless backlog
| # | Item | Status | Notes |
|---|---|---|---|
| 5 | Seed coverage gaps | done | `data/review/coverage-gaps.md`: seed covers 62% of NL/UK fleet, 39% of DE 2025; top-20 missing models listed |
| 8 | Test depth (pipeline) | done | derive/release/qa/opendata/backtest 100% line coverage; 673 tests |
| 1 | Glossary sweep | done (data), wiring queued | 49 → 88 terms; ~35 UI labels need their ⓘ wired (list in `data/review/glossary-sweep.md`) |
| 6 | Source-scoped aliases | done (on) | +80 matched records; EEA VW make alias places +62,301 registrations; no record moved to a wrong model; MG4 trim duplicates (Q-062) |
| 7 | EEA as corroboration | done (off) | with the flag on, sourced rows 2 → 6, but EEA averages blend variants, so it stays off (Q-019) |
| 9 | Docs for new builders | done | root, pipeline, infra READMEs; every command run; web README queued |
| — | T-051 part 1: 8 missing top-40 models | done | 40/40 top-40 now in the seed; rows 197 → 218; NL used fleet placed 79% → 87%, UK 63% → 72%, DE 2025 39% → 49%; segments are best-effort (Q-081) |
| 10 | Proposed tasks | done | T-051–T-060 on BOARD under "Proposed by overnight 1" |
| — | Seed quality (MG4 dupes, year evidence, shared years) | done | MG4 8 → 6 rows; ID.4 starts 2020 and Soul SK3 ends 2024 (RDW counts in notes); 10,413 NL cars in shared years now counted at model level instead of dropped; new BMW i3 in RDW/EEA not invented (Q-065) |
| — | RDW WLTP + catalogue price (from item 5) | done | 56 variants get an RDW WLTP figure, 25 an NL price (catalogusprijs incl. VAT + BPM); wide-spread groups dropped; WLTP from a 10% plate sample (no joins possible) |

## Addenda 6 + 7 (WS0, picked up 03:10)
| Item | Status | Notes |
|---|---|---|
| A7.1 decision clash | done | overnight schema decision renumbered 019 → 020 (main's 019 = Variant finder) |
| A7.2 task numbers | done | overnight task files start at T-050 |
| A7.3 T-044 VariantClue + LookalikeGroup schema | done | + ClueType taxonomy row; release checks left for T-047 (WS1), clue_types validator for T-046 (WS3) |
| A6 P1–P4 refresh, snapshots, rollback/diff, source health, weekly data-refresh workflow | done | `ev refresh`: 7 sources in 288 s first run (RDW 267 s), unchanged sources skipped via git HEAD / HTTP 304; peak memory 223 MB (+122 MB git); rollback/diff/list tested; drift fails closed per source; weekly PR workflow needs a GitHub setting (Q-079) |
| A6 P5 top-40 initial dataset + Wikidata | done | `data/seed/top40.yaml` from RDW (2018–24) + DfT fleet; 8 of the top 40 missing from the seed (EX30, iX1, iX3, Mokka-e, EQB, Taycan, iX, Explorer); top-40 coverage: only NL/DE registrations reach 80% two-source; Wikidata corroborates years for 5 models |
| A6 P6 RDW defects, fueleconomy.gov, charging stats (EAFO, BNetzA, DfT) | done (staging) | RDW defects 1,469 counts (aggregates, plates never stored); EPA 1,684 BEVs (attach-only, consumption ignored: not WLTP); BNetzA 218,113 points 1 Oct 2026; DfT 121,171 chargers 1 Jul 2026; EAFO blocked (third-party data, Q-077); DVSA skipped. Integrated into release 1 (T-059): EPA range on 84 rows; Known issues for 47 generations; Wikidata years agree on 7 of 9 checks; 2,861 charging-stat rows |
| A6 P7 manual facts path + review ids | done | `data/manual/<topic>/*.yaml` with URL + date + quote required; source `manual` blocked until Q-008; review CSVs get `review_id` + `status`, decisions kept in `data/review/status.yaml` |

