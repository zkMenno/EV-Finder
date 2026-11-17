# A-35 — Launch review 1 (QA, 2026-11-17)

**Reviewer:** QA chat (fresh agent, no build context) · **Commit reviewed:** `main` @ `d086d49` · **Checklist:** `workstreams/WS0/drafts/REVIEW.md` (draft, T-120; not yet on `main`) · **Brief:** `workstreams/QA/START.md` + `workstreams/QA/INBOX.md`

**Verdict: not ready for public launch. 5 blockers.** The code is in good shape (tests green, axe clean, parked features off, no sideways scroll at 360 px). The launch hero fails mainly on **data**. The published release is older than every launch data task. The hero also ranks on a different basis than the one that was back-tested, and DE/FR/ES/IT are mostly untranslated.

Ratings follow REVIEW.md: **must-fix** (blocks launch), **should-fix** (before public), **nit**, **pre-existing** (logged, not blocking the author). Every finding names the REVIEW item that caught it, or the item that **would have** caught it if it had run (for the T-122 rule register).

## What was run (evidence)

| Check | Result |
|---|---|
| Pipeline `uv run pytest` | 1389 passed (27.7 s) |
| Web `pnpm test` (Vitest) | pass |
| Web `pnpm lint` | pass |
| Web `pnpm build` (`APP_URL_TEST_BUILD=1`) | pass, 5137 static pages |
| Web `pnpm e2e` (90 tests) | 70 passed, 19 skipped (parked / flag-dependent), 1 failed: `security.spec.ts:98` canonical URL. That failure comes from my local test build without `APP_URL`; CI skips the test in that setup. Not a product bug. |
| Hero walk | 4 profiles × NL/UK × 15k/35k (UK budgets are £) × 360/1280 px = 32 runs, 320 cards. Screenshots in `audits/A-35-screens/hero-*.png` |
| Catalogue walk + axe (wcag2a/aa, 21aa) | hero results, NL hero, Explore, variant, /learn, Compare, DE hero, FR generation page, light and dark: **0 violations** (16 page × theme runs) |
| R0 CI on PR head | checked for every merged PR #4–#41 (see S8) |
| R1 conflict markers | `git grep -E '^(<{7}\|={7}\|>{7})( \|$)'`: none |

## Blockers (must-fix)

### B1 · Published release 1 is older than all launch data work · owner WS1 (+ WS4 staging)
- `data/releases/1/manifest.json`: `generated_at 2026-11-15T06:58Z`, 226 rows, 81 generations, QA status `review`. The release has no `used_prices.json` (T-081), no `shortlist_scores.json` (T-069) and no winter range (T-032/T-033/T-034). It also predates the T-068 seed (122 generations), the T-031 heat pump facts and the NL/BE price samples (#38).
- Effect on the hero, across all 320 cards: winter range "not known yet" on **320**, a used price band on **0**, a new price on **4**. The launch-scope result card ("real winter range, used price band for those build years") is not met. The page says so honestly ("Winter range is still being worked out", "Used prices aren't in yet").
- `ev release --dry-run` cannot rebuild it here (it would drop 102 rows without staging data), so it needs WS1 on staging.
- **Caught by:** D1 ("release rebuilt from the same inputs"). D1 never ran: #31 says "Release … not rebuilt here (needs staging) — WS1", and nobody followed up. **Would have caught it earlier:** a launch gate "latest release `generated_at` is later than the last merge touching `data/seed/**`, `data/manual/**`, `pipeline/ev_pipeline/derive/**`" (proposed rule R4). The build log also hid it: `fetch-release` printed `ready (catalogue.json, charging_stats.json, used_prices.json)` although the release has no `used_prices.json`. Fixed in this PR (it now warns).

### B2 · Budget has no effect on the hero · owner WS2 (code) + WS0 (decide the rule)
- `/nl/en?role=only&trips=monthly&charge=home&budget=15000`: the top 5 are Tesla Model Y LR AWD 2025, Audi A6 e-tron 2024–25 and Tesla Model 3 Performance 2024–25 (screenshot `hero-nl-roadtripper-15k-1280.png`). In **14 of 16** profile × country runs, the €15k and €35k lists are identical.
- Cause: `priceFit()` in `apps/web/src/lib/shortlist.ts` returns `over: false` when a car has no price, so unpriced cars pass the budget filter. With B1, almost every car is unpriced. Launch scope: "hard filters first … filtered by budget". "Neutral, never a guess" is about score factors, not the budget filter.
- Proposed fix (WS0 to decide): an unpriced car can't be in the top 5 when a budget is set, and appears only below priced cars, with its label.
- **Would have caught it:** a hero e2e test that asserts different results for 15k and 35k on the published release. `hero.spec.ts` only checks that known new prices are ≤ budget. Rule proposal: each launch-scope sentence gets an acceptance test on the real release, not on fixtures.

### B3 · The hero scores on a different basis than the back-tested rules · owner WS0 (decide one implementation), WS1/WS2
- Pipeline T-069 (`pipeline/ev_pipeline/derive/shortlist_params.yaml`) reads `winter_range_km` ×1.24, `real_wh_km` ×1.155 and `dc_km_per_20min` ×1.42 (`field_overrides` + `basis_scale`). That is the version back-tested at 60 % exact / 80 % within one band.
- The web hero (`apps/web/src/lib/shortlist.ts`, from `shortlist-rules.generated.json`) scores mild `real_range_km` against winter thresholds (road-tripper poor 300 / great 430) with no basis scale. What visitors see is therefore **not** the back-tested ranking. There are two implementations of one rule set.
- **Would have caught it:** D3 ("dry run on latest release rows; back-test") applied to the code path that ships. Sharpen D3: "the back-test runs the ranking the user sees". Proposed rule: one implementation per rule; the web reads `shortlist_scores.json` or calls the same parameters.

### B4 · Tesla Model Y Long Range AWD data is wrong, and it is the #1 road-tripper pick · owner WS1 (merge) / WS3 (seed)
- Release 1: `tesla-model-y-gen1` and `tesla-model-y-juniper` Long Range AWD both have WLTP **719 km**, **11.0 kWh/100 km**, real range 561 km, **387 km per 20 min DC**. These are implausible: about 6.5 km per kWh WLTP for a 2-tonne SUV, and nearly twice the DC figure of the Performance on the same pack (252 km). The maker's WLTP is in the 530–570 km range (🟡 from memory; check the maker page). The same values are copied across both generations.
- The car is #1 for road-trippers in NL and UK at every budget. PR #15 flagged it "to QA" on 2026-11-15; nothing happened.
- **Would have caught it:** D4 (its spot-check list names "Model Y LR vs Juniper"). Proposed QA gate: a plausibility check in `qa.json` (WLTP km per usable kWh > 8, or DC km/20 min more than 1.3× the generation median, goes to review).

### B5 · DE and FR are mostly English; ES and IT are not served at all · owner WS2 (strings) + WS3 (drafts) + WS0 (ES/IT routing decision)
- `apps/web/src/i18n/*.json` keys vs EN (736): NL 724 (only staff keys missing, fine), **DE 172, FR 172, ES 154, IT 154**. DE/FR cover only the hero; Explore, Compare, generation and variant pages, the footer, about and open data fall back to English. Example: `/fr/fr/ev/hyundai/ioniq-5/gen1` shows "Years", "Key facts", "Used price in France", "See listings" (screenshot `cat-fr-variant-light.png`).
- `countries.generated.json` serves no `es` or `it` path anywhere. Launch scope: "six languages (EN, NL, DE, FR, ES, IT; EN + NL fully reviewed)".
- **Caught by:** D6 ("all 6 languages present; draft is fine, missing is not"). It wasn't run: T-093 shipped hero-only drafts. `i18n.test.ts` checks NL coverage only. Proposed: that test checks every launch language for every public key.

## Should-fix (before public)

| # | Finding | Evidence | Owner | Check that catches it |
|---|---|---|---|---|
| S1 | The Decision 060 de-duplication (`e885fa0`) **deleted the newer entry**: the one with the 2026-11-17 robots/terms checks for 2dehands.be (used), leboncoin (not used) and kleinanzeigen (not used). Ten `be-2dehands-*.yaml` files are on `main`, so the log no longer records why BE scraping is allowed. AGENTS.md: never delete a decision. | `git show e885fa0` | WS0 (restore the consequences line) | D12 checks numbers only. Sharpen: "a de-dupe keeps the union of both texts". |
| S2 | Marketplace price samples (Marktplaats, 2dehands) have **no `data/sources.yaml` entry** (licence, terms, status). `derive/used_price.py` keeps only `name` + `url`, with no licence or status gate. They will reach the next release ungated. | `grep -i marktplaats data/sources.yaml` → none | WS1 + WS3 | D2 (should have fired on #38, a new source). |
| S3 | Provenance per number: the popover shows source, confidence and the **release** date, but **no licence** and no retrieval date. Generation and variant spec tables have **no Nerd level**: `?level=nerd` does nothing, because `Num` there doesn't use `LevelNum`/`useLevel`. | `/nl/en/ev/hyundai/ioniq-5/gen1/awd?level=nerd` → 0 `num-nerd` nodes (screenshot `variant-ioniq5-awd-nerd.png`) | WS2 (+ WS0 schema: `FieldProvenance` date) | D7. |
| S4 | **Parked "full price modes" are visible**: a Buy / Loan / **Lease** toggle on Explore, generation, variant and Compare pages (lease shows a placeholder). Launch scope parks "lease per month and full price modes"; only the hero's "≈ €X/month" ships. | `cat-variant-light.png`, `/nl/en?pay=lease` | WS2 (put the toggle behind a parked flag) | D9. |
| S5 | **/learn is beyond scope and unreviewed**: 6 guides are listed (launch: winter range, charging 2026, batteries). `plugs-and-bidirectional` (bidi is parked), `chemistries` and `voltage-classes` exist in EN + NL only. **All 6 say "Draft: review needed", EN and NL included** (scope: EN + NL fully reviewed). Glossary entries for parked features (lease, V2G/V2H, trip fit, known issues) are listed too. | `/nl/en/learn` | WS3 + Menno review | D6/D9 (scope list per page). |
| S6 | **NL hero has no monthly estimate** ("no official typical loan rate for this country yet"). Scope: a fixed default per country. DE/FR/BE/UK show one. | `/nl/en?…&budget=20000` | WS3 (`finance_profiles.yaml`, sourced NL APR) | Launch acceptance per country (see B2's rule). |
| S7 | T-064 is only half done: release 1's big files are still tracked in git (`catalogue.json` 7.4 MB, parquet files, 81 `catalogue/generations/*.json`), even though `.gitignore` excludes them. | `git ls-files data/releases/1` → 99 files | WS1 (T-064 part 2) | D1 / repo-checks (fail when an ignored path is tracked). |
| S8 | Catalogue rows (D4): Ioniq 5 "AWD"/"Base" 2023–2025 at 72.6 kWh (77.4 kWh from 2022, 84 kWh from the 2024 facelift); Ioniq 5 N at 78 kWh (84); the 77.4 kWh Ioniq 5 rows have no figures; MG4 "Standard Long Range" at 13.6 kWh/100 km vs 16.6 for the same 61 kWh pack; no XPENG P7/P7+ in the release. T-068 fixes the seed, but B1 keeps the fixes out. 🟡 kWh figures from memory; check the maker sheets. | release 1 rows | WS3 / WS1 | D4. |

## Nits

- **N1** `fetch-release` named files the release doesn't have. **Fixed in this PR**: it now warns about wanted files missing from the manifest and lists only real ones.
- **N2** The Ioniq 5 AWD real range shows "estimate" and "2 sources agree" together, which reads as a contradiction.
- **N3** `e2e/smoke.spec.ts:123` is still named "header links to Rankings and Compare" although Rankings is parked.
- **N4** R3 (accepted, noted): #31 changed an expectation in `pipeline/tests/test_registrations.py` outside its lane (flagged to WS1, no reply on file). `aaa1d5b` switched `test_manual.py` to `date.today()`, which is right for real repo data but makes the test date-dependent.
- **N5** The REVIEW.md draft's R2 points at an AGENTS.md "Verified:" stamp that doesn't exist yet. PR #42 already rewords it (T-128).
- **N6** `e2e/a11y.spec.ts` doesn't axe the hero **with results** (cards appear only after the picker). My run did (clean), but add it so it stays covered.

## Pre-existing (logged, not blocking the authors)

- **P1 (R0)** Merged with red CI on the PR head: #4, #5, #7 and #9 (web + e2e red), #11 (arm64 jobs build failed). #6 had no CI run at all. All of these predate REVIEW.md and the "push doesn't trigger CI" lesson. `main` is green now (`d086d49`: CI + Images success).
- **P2 (R2)** 17 of 20 launch PR bodies have no evidence section (the template didn't ask for one; #42 adds it). Claims checked against the code: #15's back-test numbers are in the PR, but the release it describes is not published (B1/B3). #31's "pytest 1353 passed" is consistent (1389 today).
- **P3 (D11)** Workflow changes rode along with code in #13 and #26 (before the gate-change rule). Every action is pinned to a SHA; permissions are `{}` or `contents: read`.

## Passed

- R1: no conflict markers.
- D5: schema changes since `ed3bfb2` are additive (no removed definitions or properties, no new `required`, nothing newly closed); release 1 still loads.
- D9: parked features hidden in a default build. `/top`, `/charging`, `/trip`, `/account` give 404; charging links, known issues and the registrations block are off (`e2e/parked.spec.ts` passes; curl checks). The deploy config sets no parked flag.
- D8 / accessibility: axe clean in both themes on the pages above; no sideways scroll at 360 px on all 16 hero runs; 0 page errors.
- Hero structure: 10 cards, top 5 marked, a reason line on each, variant + build years, "See listings" on all 320 cards (AutoScout24 NL, Autotrader UK; unverified links, T-041 tap check pending). The road-tripper "one owner's picks" disclaimer is shown.

## Proposed rules for WS0 (T-122 register)

1. **R4 release freshness:** CI fails a launch/deploy build when `latest` is older than the last merge into the release inputs (B1).
2. **D3 sharpened:** back-test the ranking the visitor sees; one implementation per rule (B3).
3. **D4 automated:** plausibility gates in `qa.json` for km/kWh and DC outliers (B4, S8).
4. **D6 test:** `i18n.test.ts` checks every launch language for every public key, plus a served-language check for all six (B5).
5. **D12 sharpened:** a de-dupe merges both texts; never drop the newer one (S1).
6. **Launch acceptance tests:** one e2e check per launch-scope sentence, run on the published release (B2, S6).
