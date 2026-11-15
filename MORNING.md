# Good morning — overnight prototype 1

_Working title EV Shortlist (Decision 018). Branch `proto/overnight-1`, draft PR [#1](https://github.com/zkMenno/EV-Finder/pull/1). This file is refreshed after every item; the newest state is at the top of each section._

## 0. Do this first (2 minutes)
1. **Nothing to undo on `main`.** The first hour of work landed on `main` by mistake (Q-030). WS0 has built on top of it, so it stays; everything since then is in PR #1.
2. **One GitHub setting:** Settings → Actions → General → tick "Allow GitHub Actions to create and approve pull requests", so the weekly data-refresh workflow can open its PR (Q-079).
3. **Paste the project instructions v1.3** (sent in chat) into Project Settings if you haven't yet.
4. **Answer the questions** in section 5 when you have time. Nothing is blocked on you tonight.

## 1. What works now
Run it locally (needs Node 22, pnpm 10, Python 3.12 + uv):

```bash
git clone https://github.com/zkMenno/EV-Finder && cd EV-Finder && git checkout proto/overnight-1
pnpm install
pnpm --filter @ev/web dev          # http://localhost:3000 → redirects to /nl/nl
# optional: rebuild the data release from recorded samples (no network)
cd pipeline && uv sync && uv run ev release
# refresh from the live open sources (network): only what is due and changed
uv run ev refresh
```

Checks: `pnpm --filter @ev/web test`, `pnpm --filter @ev/web e2e`, `cd pipeline && uv run pytest`.

## 2. Screens
| Route | What it is |
|---|---|
| `/nl/nl` (11 pairs: nl/nl, nl/en, de/de, de/en, fr/fr, fr/en, be/nl, be/fr, be/de, be/en, uk/en) | Explore: one table of new + used EVs, table/cards toggle, filters (price, era, segment, body, real range, battery, DC km in 20 min, boot, length, towing, voltage class, chemistry, cooling, "fast on older 400 V chargers", "charge to 100% daily"), Simple / Detailed / Nerd, hearts, compare tray that never resets |
| `/nl/nl/ev/<make>/<model>` | Model overview with generations |
| `…/<generation>` | Generation page: change markers, spec diff per year, See listings, registrations per country, Known issues (RDW defects), source + confidence on every number |
| `…/<variant>` | Full spec sheet with price modes (buy / loan / lease) |
| `/nl/nl/compare?ids=…` | Up to 4 side by side, differences highlighted, share + print |
| `/nl/nl/top` | Rankings: longest real range under €30k, fastest DC (km in 20 min), most registered in NL |
| `/nl/nl/learn` | 5 articles (draft) + 88 glossary terms |
| `/de/de/charging`, `/uk/en/charging` | Public charging points over time and by power band (BNetzA, DfT) |
| `/nl/nl/about` | What we are, how numbers are made, credits for every source |
| `/health` | Health check for the server watchdog |
| `/staff/review` | Review queue (only with `STAFF_PAGES=1`) |

## 3. Data
Release 1: **244 variants** across 81 generations of 63 models (the 40 from the brief + 23 added from registration evidence). 5,258 static pages.

| Source | Ran | Licence | Used for |
|---|---|---|---|
| Open EV Data (open-ev-data-dataset) | live | CDLA-Permissive-2.0 | base specs |
| Open EV Data (KilowattApp) | live | MIT + attribution | specs, 51 non-default charge curves (estimates) |
| RDW | live | CC0 | NL fleet, WLTP (10% sample), NL catalogue price, inspection defects |
| EEA CO₂ monitoring | live | CC BY 4.0 | new registrations NL/DE/FR/BE |
| KBA FZ10 | live | dl-de/by-2-0 | DE new registrations |
| DfT VEH0120 | live | OGL v3 | UK fleet |
| ADEME Car Labelling | live | Licence Ouverte | FR prices (7 variants), fallback specs |
| fueleconomy.gov (EPA) | live | US public domain | EPA range cross-check |
| Wikidata | live | CC0 | generation-year check |
| Bundesnetzagentur, DfT charging | live | CC BY 4.0, OGL v3 | charging statistics (aggregates) |
| EAFO | sample | blocked (third-party data) | not released |
| Seed (hand-entered) | — | CC BY 4.0 | older cars, confidence **low** |
| Bjørn Nyland | importer only | permission pending | never in a release |

Honest caveats: 🟡 every real-range and DC figure is an **estimate** tonight (ratio model, default or unverified curves). 🔴 About half of all numbers rest only on the hand-entered seed (low confidence). Coverage per field: `data/releases/1/coverage.md`.

Research (all on the branch): R-02 launch countries, R-06 future markets, R-07 European expansion. Coverage gaps: `data/review/coverage-gaps.md`; top-40 list: `data/seed/top40.yaml`.

## 4. Not done, and why
- **Used prices:** no open source exists; layer 0 indices and partner feeds are next (T-056). PriceBand shows "not enough data".
- **Real range and DC charging are estimates:** every real-world test source needs permission (Bjørn, NAF, ADAC, Spritmonitor; T-055). KilowattApp curves are unverified.
- **Two-source agreement is low:** 0–25% of top-40 headline fields have 2+ agreeing sources (target 80%). Most fields rest on one source or the hand-entered seed.
- **Pre-2020 specs:** no open licensed source yet (Q-007, T-052).
- **Per-car bidirectional data, clue table, lookalike groups:** schemas are in; data is WS3 work (T-019, T-046, T-047).
- **Deploy:** files written, nothing applied (WS4). 🟢 arm64 images build in CI (Images workflow green on the PR).
- **EAFO and maker documents:** blocked on licences (Q-077, Q-008).

## 5. Questions for Menno (most important first, max 7)
1. **Q-008** · Can single facts cited from maker documents (spec sheets, price lists) go into public releases? Unlocks prices, boot space, warranty and the hand-entered facts path.
2. **Q-037** · RDW's notice says reusers may not state the data comes from RDW. How should we label it? (Interim: "Dutch vehicle register (RDW open data, CC0)".)
3. **Q-036** · RVO is CC BY-SA (share-alike). Keep it as a cross-check only, or ask RVO for permission?
4. **Q-047 / Q-059** · Some KilowattApp values may come from ev-database.org, and its MIT data sits inside our CC BY bundle. Keep, limit, or drop?
5. **Q-077** · Email the Commission (DG MOVE) to reuse EAFO data?
6. **Q-079** · Tick the GitHub setting so the weekly data PR can open (see section 0).
7. **Q-002 / Q-003** · Confirm pnpm + uv, and require PRs with green CI on `main`.

All 70+ open questions are in [QUESTIONS.md](QUESTIONS.md); most only record a default and need no answer.

## 6. Suggested wave 5
1. T-055 real-range permissions (drafts for Menno to send) — the biggest quality gap.
2. T-056 used prices layer 0 (free indices) so PriceBand and the "under €15k" rankings can show data.
3. T-051 part 2 + T-060: finish seed coverage and pack/platform links.
4. T-052 a licensed pre-2020 spec source to replace hand-entered seed data.
5. T-057 make release QA a CI gate on data PRs; fix the EV6 pack mismatch.
6. WS2: show Known issues, EPA range, generation-year badges and charging charts in the UI.
7. WS4: apply the deploy (database, Caddy, staging), using the runbook notes in Q-070/Q-073.

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
| — | T-053 registration history | done | KBA FZ10 2019–2026 (2018 file names no licence → skipped), EEA 2018–2025 (final years = high confidence); RDW change probe: weekly refetch drops from ~265 s to ~1 s when unchanged |
| — | T-051 part 2: 15 more big models | done | ID.7, Elroq, Q6, Tavascan, A6 e-tron, i5, EV3, R5, ID. Buzz, Inster, bZ4X, CLA, Puma Gen-E, Macan Electric, Scenic; placed share NL fleet 82%, UK 81%, DE 2025 81%; EQE skipped (KBA mixes saloon + SUV); segments best-effort (Q-083) |
| — | T-057 QA findings + CI gate | done | EV6 AWD/GT back to 77.4 kWh: KilowattApp's 80 kWh is the 2024 facelift 84 kWh pack, now kept out by a pack-gross guard (Q-084); new `data-qa` CI job re-runs the blocking checks on the committed release |
| 2–4 + "if time" | Explore polish, compare, rankings, dark theme, axe | done | axe 0 findings on 8 pages × 2 themes; dark "Night drive" from design tokens; empty state names the filter to remove; compare share/print/differences tested (lost `pay=` fixed); "under €15k/20k/25k" pages ready but hidden until ≥ 5 cars have used prices |
| — | T-054 RDW split by type code | done | NL price records 366 → 1,257; a power gate (Q-086) sends records without a matching-power row to review instead of guessing (Model Y 378 kW, Q6 Performance, ID.4 4MOTION) |
| — | R-08 + RDW TGK (pre-2020 specs, T-052) | done | RDW type approvals (CC0) cover 96.5% of NL BEVs incl. all 17 pre-2020 targets; NEDC, worst-case WLTP and running-order mass are separate fields (Decision 023); WLTP now on 178 rows, 25 rows reach "sourced" (was 2); older cars like Zoe ph1 still need aliases to attach |
| — | T-061 web: Known issues, EPA, year badge, charging | done | defect rates per first-registration year vs all EVs of that year; "EPA range (US test)" never mixed with WLTP; Wikidata year badge; `/{country}/{lang}/charging` with hand-written SVG charts for DE + UK |
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


## Retro (5 lines, light version at 03:45)
- **Slowed me:** the push clone sat on `main` for an hour, so early work landed there (Q-030); and two decision/question/task number clashes with WS0 working on `main` at the same time.
- **Menno had to do by hand:** grant push access mid-run, and paste the project instructions.
- **Rule that would have prevented it:** "Before the first push, `git branch --show-current` must equal the brief's branch; push by explicit refspec only." And "before adding a decision, task or question number, fetch `main` and take the next free one on both sides" (WS0 already added this in addendum 7).
- **What worked:** lanes per folder plus a fresh reviewer per wave caught real bugs (Nyland fixture, e-tron GT, DC honesty, junk RDW rows) before they shipped.
- **Next time:** give builders one shared clone path in the brief (agents kept seeing two working directories).
