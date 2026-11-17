# A-36 — Launch review 2 (QA, 2026-11-17)

**Reviewer:** QA chat (fresh agent, no build context) · **Commit reviewed:** `main` @ `be2de6f` · **Release:** 2 (`latest` = 2, data-v2, generated 2026-11-17T20:50Z) · **Checklist:** `REVIEW.md` read from `origin/main` · **Brief:** `workstreams/QA/INBOX.md` "QA launch review 2" + `START.md` · **Scope:** `docs/spec/launch-scope.md` **rev 2** (English only, Decision 082)

**Verdict: not ready for public launch. 4 blockers** (2 of them already have work in flight: #105, T-137). Release 2 fixed the data gaps from A-35: used prices, winter range and release scores are in, the budget changes the result, Model Y is plausible, and every hero card has a reason line and a listings link. What still fails is **what the ranking rewards**: a car with no data at all is the only road-tripper pick at €15k in all five countries walked. The provenance popover also names the wrong source for every hand-entered fact.

Ratings follow REVIEW.md: **must-fix** (blocks launch), **should-fix** (before public), **nit**, **pre-existing**. Every finding names the check that caught it or **would have** caught it (T-122 rule register).

## What was run (evidence)

| Check | Result |
|---|---|
| Pipeline `uv run pytest` (after `ev release fetch latest`) | 1551 passed, 1 xfailed (48 s). Without the fetch, `test_committed_release_passes_blocking_qa` fails on a missing `facts.parquet`: local setup only, CI fetches first (#95) |
| `python -m ev_pipeline.qa check-release data/releases/latest` | pass: provenance 6642 values, licence gate 14 sources / 44 689 facts, release diff vs 1: 0 blocking |
| Web `pnpm lint` · `typecheck` · `test` | pass · pass · 413 / 413 |
| Web `pnpm build` (`APP_URL_TEST_BUILD=1`, release 2 via `fetch-release`) | pass, 8325 static pages |
| Web `pnpm e2e` (136 tests) | 113 passed, 20 skipped, 3 failed: `a11y` hero-nl-360 and hero-en-nerd-360 (dark) timed out under load and **pass on re-run** (4/4); `security.spec.ts:98` canonical URL fails only on a local test build without `APP_URL` (same as A-35) |
| Hero walk | NL, DE, FR, ES, IT × 4 profiles × €15k / €35k × 1280 / 360 px = 80 runs, 794 cards, on `/{cc}/en` (English only, rev 2). Script: `workstreams/QA/tools/hero-walk.mjs`. Screenshots: `audits/A-36-screens/hero-*.png` |
| Catalogue walk | `workstreams/QA/tools/catalogue-walk.mjs`: Nerd mode on 5 variant pages, price modes, /learn, 10 language routes, dark theme. Plus a provenance popover check on 10 numbers across 5 variant pages |
| R0 on the fix PRs merged after A-35 | #91, #95, #96, #97, #99, #100, #101, #102, #103: every check run on the PR head is success or skipped |
| R1 conflict markers | none (`.githooks/pre-push`) |

### Hero walk in numbers (1280 px; 360 px identical lists, 0 px sideways scroll, 0 page errors)

| | €15k | €35k |
|---|---|---|
| Runs with 10 cards | 18 of 20 (NL road-tripper 9, NL kerbside 8: fewer models qualify, said on the page) | 20 of 20 |
| Shortlist size (priced picks, max 5) | road-tripper and kerbside **1** in every country; daily driver 4–5; runabout 5 | 5 everywhere |
| Shortlisted card over budget | 0 | 0 |
| €15k list = €35k list | 0 of 20 (A-35: 14 of 16) | |
| Cards with winter range | 6–8 of 10 | 7–10 of 10 |
| Price basis over all 794 cards | band (counted listings) 56 · estimate 448 · new 2 · none 288 | |
| Reason line / "See listings" link | 794 / 794 | 794 / 794 |
| "≈ €X a month" | DE, FR, ES, IT yes; **NL no** (S4) | |

## Blockers (must-fix)

### B1 · A car with no data is the #1 road-tripper and kerbside pick at €15k, in every country · owner WS2 (code) + WS0 (rule) + WS3 (data) · **T-138**
- At €15k the road-tripper and kerbside shortlists hold one car in NL, DE, FR, ES and IT: **Dacia Spring 2024 facelift** (`dacia-spring-gen1-facelift-65`). Its card says real range "not known yet", winter range "not known yet", and the reason line is "The newest version, €1,000 under budget" (screenshot `hero-fr-roadtripper-15k-360.png`). The road-tripper is "main car that also does the holidays (fast charging, winter range, space)"; the Spring has the smallest battery and slowest fast charging in the catalogue.
- Cause: `presetCheck()` in `apps/web/src/lib/shortlist.ts` lets unknown values pass ("unknown values pass"), and release 2's facelift row has no WLTP, real range, DC or boot figure at all. The **pre-facelift** Spring rows, which have data (195 km real range, 38 km per 20 min DC), are correctly filtered out. Missing data is rewarded over known bad data.
- Below the one pick, the €15k road-tripper list fills with unpriced premium cars (Zeekr 001, Audi A6 e-tron, Tesla Model S, Porsche Macan Electric): see S5.
- **Would have caught it:** a profile-fit acceptance test on the published release (REVIEW R4 second half): "every numbered card for a profile has a known value on at least one of that profile's preset fields". `hero.spec.ts` checks budget, ranks and order, not whether the pick fits the profile. Proposed rule in the list at the end.

### B2 · Every hand-entered fact names "Volkswagen Ireland, ID. heat pump page" as its source · owner WS1 (+ WS2 popover) · **T-139**
- Release 2 `catalogue.json` `sources[id=manual]`: name "Manual entries (hand-entered, cited by URL): Volkswagen Ireland, ID. heat pump page", URL `volkswagen.ie/.../heat-pump.html`. All manual citations share the id `manual`, so the release keeps the first one's name and URL for all of them: **134 values on 40 variants**.
- Visible on the site: Tesla Model Y Juniper LR AWD real range 457 km → "Source: Manual entries …: Volkswagen Ireland, ID. heat pump page, EV Finder estimate models"; Hyundai Ioniq 5 77.4 kWh AWD "5 min" the same (`/de/en/ev/tesla/model-y/juniper/long-range-awd`, `/nl/en/ev/hyundai/ioniq-5/gen1/77kwh-awd`). Data rule 1 ("every number is traceable") is broken in public, with a wrong citation rather than none.
- Cause: `pipeline/ev_pipeline/manual/facts.py` `_source_dict()` puts the per-fact name and URL on a source dict keyed only by `manual`.
- **Would have caught it:** a blocking release QA check "one source id maps to exactly one name and URL", and D7 checking that the popover source of a cited fact matches its `source_url`. `check-release` passes because it checks that a source exists, not that it is the right one.

### B3 · `main` cannot build the web image, so release 2 can't be deployed · owner WS2 / WS1 · **PR #105 open**
- `Images` on `main` failed on `fd18fb0`, `026cc04`, `da06593`, `d6e9cdf`: the Dockerfile catalogue stage reads `data/releases/<latest>/catalogue.json` from git, and release 2 is manifest-only (T-064 / A-35 S7 fix). WS2 reported it at 21:19 UTC (WS0 INBOX). #105 fetches by manifest before the image build.
- Staging still serves the last image built before release 2, so nothing a visitor sees has been checked on staging yet.
- **Would have caught it:** D1 for a release PR should include "the deploy image builds on this release" (Images job on the release PR, not only CI). Release 2 (#91) changed what is in git without the image job running.

### B4 · Draft translations are still public; the scope now says English only · owner WS2 · **T-137 (PR #111 open)**
- `/nl/nl`, `/de/de`, `/fr/fr`, `/es/es`, `/it/it`, `/be/fr` all answer 200 with `<html lang>` in that language; English pages show a "Language" picker. Launch scope rev 2 / Decision 082: every country serves `/{country}/en/`, other languages hidden until reviewed. A-35 B5 (missing strings) is fixed (no-english e2e passes), but the drafts are unreviewed and must not ship.
- Already tasked (T-137); listed here so the launch gate counts it.

## A-35 findings: fixed or not

| A-35 | Status on release 2 | Evidence |
|---|---|---|
| B1 release older than launch data | **fixed** | Release 2 generated 2026-11-17T20:50Z; `used_prices.json`, `shortlist_scores.json` present; winter range on 237 / 271 rows; 794 hero cards: 0 "used prices aren't in yet" |
| B2 budget has no effect | **fixed** (but see new B1) | €15k ≠ €35k in 20 / 20 runs; 0 shortlisted cards over budget; unpriced cards never numbered (288 unpriced cards, all `data-rank` null) |
| B3 hero scores a different basis | **fixed** | `hero-nerd-source` names `shortlist_scores.json` (e2e `hero: Nerd shows how the score is built` passes); T-114 review on 7 answer sets |
| B4 Model Y LR AWD implausible | **fixed** | gen1 LR 533 km / 16.9 kWh per 100 km / 79 kWh; Juniper LR AWD 586 km / 14.8; plausibility gate in qa.md withholds 5 rows, flags 33 |
| B5 DE/FR/ES/IT untranslated, ES/IT not served | **fixed, then superseded** | `no-english.spec.ts` and `es-it.spec.ts` pass; scope rev 2 makes it English only → B4 / T-137 |
| S1 Decision 060 lost its 17 Nov line | **fixed** | DECISIONS.md:722 restored, marked "Restored 2026-11-17 by WS0" |
| S2 marketplace samples had no sources.yaml entry | **fixed** (entries) | `data/sources.yaml:120–123` marktplaats + 2dehands with terms and `use: aggregates-only`. T-111's S2 checkbox is still unticked; I did not re-test the `used_price.py` gate |
| S3 popover: no licence, no retrieval date, no Nerd on spec pages | **open** | 5 variant pages with `?level=nerd`: 0 `num-nerd` nodes; 10 popovers: source + confidence + release date, no licence, no retrieval date (`cat-variant-provenance-popover.png`) |
| S4 parked price modes visible | **open** | Buy outright / Loan per month / **Lease per month** buttons on `/nl/en` and generation pages; `?pay=lease` adds a Lease column and "Lease offers for this car" (`cat-explore-pay-lease.png`) |
| S5 /learn beyond scope, all drafts | **open** | `/nl/en/learn` lists 6 guides incl. plugs-and-bidirectional, chemistries, voltage-classes; all 6 say draft. Glossary still has parked-feature entries (v2g, v2h, v2b, v2l, lease, private-lease, trip-fit, known-issues, registrations-nl) |
| S6 NL hero has no monthly estimate | **open** | NL: "We have no official typical loan rate for this country yet"; DE 8.91 %, FR 6.11 %, ES 7.54 %, IT 10.78 % shown |
| S7 release files tracked in git | **half** | Release 2: 7 small files in git (manifest-only) ✓. Release 1: still 99 tracked files (`git ls-files data/releases/1`). And the fix caused B3 |
| S8 catalogue rows | **half** | Ioniq 5 77.4 kWh rows now have figures ✓; MG4 Standard Long Range 16.0 vs 16.6 ✓. Still: Ioniq 5 facelift base/AWD 72.6 kWh (84 kWh pack 🟡 from memory), Ioniq 5 N 78 kWh (84 🟡), `ioniq-5-gen1-73kwh-awd` row has no figures at all, no XPENG P7 / P7+ in the release |

## Should-fix (before public)

| # | Finding | Evidence | Owner | Check that catches it |
|---|---|---|---|---|
| S1 | A-35 S3 open: no licence or retrieval date per number; Nerd does nothing on spec pages | see table above | WS2 (+ WS0 schema: `FieldProvenance` date) | D7 |
| S2 | A-35 S4 open: Buy / Loan / Lease toggle | see table above | WS2 (parked flag) | D9 |
| S3 | A-35 S5 open: /learn and glossary beyond scope, all drafts | see table above | WS3 + Menno review | D6 / D9 |
| S4 | A-35 S6 open: NL monthly estimate missing | see table above | WS3 (`finance_profiles.yaml`, sourced NL APR) | launch acceptance per country |
| S5 | Unpriced premium cars fill the €15k list: Zeekr 001, Audi A6 e-tron, Tesla Model S, Porsche Macan Electric in NL road-tripper €15k. They have no NL price, so the sibling check passes, although the A6 e-tron Avant has a DE new price of €77,250 in the release; Macan and Zeekr have no price anywhere | `hero-nl-roadtripper-15k-1280.png`; `hero.spec.ts:228` only reads NL prices | WS2 | the same e2e, reading any country's known price |
| S6 | Most used prices are estimates from list price and depreciation: 448 of 506 priced cards say "Rough estimate", 56 come from counted listings. Labelled honestly; the launch card asks for a used price band per build year | walk totals above | WS1 / WS3 (more samples per country) | release QA: share of priced rows with `band` per country |
| S7 | Ioniq 5 facelift and N rows carry pre-facelift packs; one Ioniq 5 row is empty; no XPENG P7 / P7+ (A-35 S8 remainder; WS0 follow-up list) | catalogue rows above | WS3 | D4 |
| S8 | Release 1's 99 files still tracked in git (A-35 S7 remainder) | `git ls-files data/releases/1 \| wc -l` → 99 | WS1 | repo check: ignored path tracked |

## Nits

- **N1** Hero cards listed parked bidirectional features in "Not known yet: … power out (V2L), powering a home (V2H/V2G)". **Fixed in this PR** (`Hero.tsx` drops parked factors from that line; they still count in the release score) with an e2e test in `parked.spec.ts` (fails on the old build, passes on the new one).
- **N2** A-35 N2 still there: Ioniq 5 real range shows "estimate" and "2 sources agree" together.
- **N3** Dacia Spring facelift card: heading "2024–now", price "built 2024–2025", variant name "Spring 45 / 65 (2024 facelift)" (two power levels in one row).
- **N4** `a11y.spec.ts` hero-360 runs take ~25 s each and time out when the machine is busy (30 s limit). Raise their timeout or split the pages.
- **N5** Task numbers: the brief gave QA T-130–T-139, but WS0 used T-130–T-137 for the staging feedback (`4bde363`). QA used T-138 and T-139; other follow-ups below are unnumbered for WS0 to assign.

## HANDOFF "Follow-ups noted": launch blockers or not

| Follow-up | Launch blocker? |
|---|---|
| €15k road-tripper list thin (one priced pick) | **Yes**, as A-36 B1: the one pick has no data |
| Ioniq 5 facelift rows carry pre-facelift figures | No; should-fix S7 (wrong battery on a popular car, but labelled single source) |
| Model Y winter vs real range on different bases | No; should-fix (WS1 design). Juniper LR: real 457 km, winter estimate shown separately |
| EV6 GT TGK consumption 24.2 (+43 %) | No; should-fix with an estimate label |
| Approvals check id/field/type, not values | No; process should-fix (it would not have caught B2 either) |
| cite_paths required on every non-manual source | No; should-fix |
| maker-docs: 11 seed citations are third-party copies | No for launch day, but before public: provenance quality, same family as B2 |
| Car pages: English data labels on non-English pages | No longer relevant (English only, T-137) |
| FR loan.warning wording (Q-072), IT CCD2 cite | No (English only; wording question stays with Menno) |
| CI ranking e2e skips without a scores file | No; CI now fetches release 2 with scores, so it runs |
| #59 staging runbook, #90 infra docs | No |
| eafo upstream 429 | No |
| Main image build broken | **Yes**, B3 (#105) |

## Passed

- R0 on all post-A-35 fix PRs; R1; pipeline, web unit, lint, types, build.
- D5: release 2 loads in the web app; release QA blocking checks pass.
- D8: no sideways scroll at 360 px in 40 / 40 hero runs; axe clean on the a11y suite in light and dark (re-run of the two timeouts: 4 / 4 pass).
- D9: `/top`, `/charging` still 404, charging links, known issues and registrations block off (`parked.spec.ts` passes); trip fit off by default.
- Hero structure: top 10 (fewer only when fewer models qualify, and the page says how many), top 5 marked, reason line, variant + build years, winter range where known, price band or labelled estimate, "See listings" on every card (AutoScout24 NL / IT, mobile.de, leboncoin, Wallapop); Compare + diff-only and Explore URL state covered by e2e (pass).

## Proposed rules for WS0 (T-122 register)

1. **R4 sharpened (profile fit):** the launch acceptance test checks that each numbered pick has known data on its profile's preset fields, on the published release (B1).
2. **Release QA: one source id = one citation** (blocking): a source id maps to one name and URL across a release (B2).
3. **D1 sharpened:** a release PR runs the Images job (deploy image builds on the new `latest`) before merge (B3).
4. **Task-number blocks:** WS0 records which block each chat owns in the INBOX brief and doesn't hand out the same block twice (N5).

## Follow-ups

- **T-138** hero: unknown must-have data is never a ranked pick (B1) · WS2 + WS0 + WS3
- **T-139** manual facts show their own citation (B2) · WS1 (+ WS2)
- Unnumbered for WS0: S2 price-mode flag (WS2), S3 /learn + glossary to scope (WS3), S4 NL APR (WS3), S5 unpriced premium cars (WS2), S6 used-price band share per country (WS1), S8 untrack release 1 (WS1).
