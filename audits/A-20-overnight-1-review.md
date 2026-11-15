# A-20 · Review of `proto/overnight-1` (overnight prototype 1)

**Reviewed:** `origin/proto/overnight-1` at commit `8b48bd7c44cac991a8bd4d93bf27ff01b8b4bdf8` ("MORNING: seed quality"), against base `5b171d5`. 355 files, +40k / −3k lines. Reviewer: fresh-eyes auditor, 2026-11-15. Line numbers refer to that commit.

**Verdict: not mergeable yet, but close. One blocker.** The pipeline test suite is red on the branch tip: the committed release 1 was not rebuilt after the last seed-quality commit, so the release does not match the seed and code that ship with it (and MORNING.md describes a result the release does not contain). Fix that and the branch is mergeable as a draft-quality prototype. The data rules hold up well: every fact in release 1 has source, retrieved date, confidence and licence. The licence gate fails closed. No ODbL is in the release, and a test guards that. Nyland data stays out (the fixture is synthetic). Tests never touch the network. No secrets, rates or sampling targets are in the tree. Schema changes are purely additive, and the generated types match a fresh regeneration. The should-fix items are mostly licence and wording matters that must be settled **before anything goes public**, not before merge.

**Current verdict at `d06535a` (delta pass, 2026-11-15 ~05:00 UTC): mergeable as a draft prototype, no blocker.** B1 is fixed, and every test, lint and type check is green, also with the network switched off. The pre-public licence and wording items are still open. Two new should-fix items: the `rdw-tgk` credit names RDW, and `ev release` on a fresh checkout still publishes a crippled release. See "Delta pass" at the end.

---

## Blocker

### B1 · Pipeline tests fail on the branch tip: release 1 is stale against the seed
- **Where:** `pipeline/tests/test_real_release.py:410` (`test_mg4_has_one_row_per_real_car`) fails. `uv run pytest`: **1 failed, 696 passed, 1 skipped**. CI runs that same command (`.github/workflows/ci.yml:157`), so CI is red.
- **What's wrong:** commit `bc704c2` (seed quality) changed `data/seed/models.yaml`, `data/seed/variants.yaml` and the matcher, and added this test. It did not commit a rebuilt release. The last change to `data/releases/1/catalogue.json` is `df94db8`. The committed release still has the MG4 near-duplicates (`mg-mg4-gen1-standard-range`, `mg-mg4-gen1-trophy`, …), and it predates the ID.4 / Soul year moves and the 10,413 shared-year NL cars. MORNING.md:92 reports "MG4 8 → 6 rows", which is not what the release contains.
- **Rule:** AGENTS.md "CI must be green before review"; pipeline/AGENTS.md rule 3 (a run's outputs must match its inputs); honest reporting.
- **Fix:** rebuild release 1 from the same staging inputs (or publish it as release 2, see S7) with the seed-quality code, commit it, check `pytest` is green, and correct MORNING.md if the numbers differ.

---

## Should-fix

### S1 · RDW is credited by name while Q-037 is open
- **Where:** `data/releases/1/open/ATTRIBUTION.md:14` ("Dutch vehicle register (RDW open data, CC0)"), `data/releases/1/catalogue.json` `sources[rdw].attribution` ("Bron: RDW Open Data…"), `apps/web/src/lib/credits.ts:36`, plus `rdw` as a source id on every value in `variants.csv`.
- **What's wrong:** the RDW bijsluiter says reusers may not state that the data comes from RDW (Q-037, unanswered). Even the interim wording names RDW, and the catalogue's own attribution says "Bron: RDW".
- **Rule:** licence and terms (AGENTS.md data rule 3; project rule "flag licences and terms").
- **Fix:** no change needed to merge. Before any public release or `/data` download page, Menno answers Q-037 (or RDW is asked). Until then, make the catalogue attribution use the same wording as the web override.

### S2 · KBA deep link without the notice KBA asks for
- **Where:** `data/releases/1/open/ATTRIBUTION.md:10` links `kba.de/…/fz10_gentab.html`. `data/sources.yaml:48` itself records "KBA asks for notice before deep-linking kba.de". The About page builds its credits from the same release `sources[].url`.
- **Rule:** respect site terms (AGENTS.md "Web access").
- **Fix:** link to the KBA statistics start page, or log a QUESTIONS item to send KBA the notice (a draft for Menno, since it goes out in his name) before launch.

### S3 · Hand-entered seed values go into the public CC BY bundle
- **Where:** `data/releases/1/open/variants.csv` (for example boot, length, towing, seats, chemistry and platform on `audi-e-tron-ge-50` have `seed-manual` as their only source, confidence `low`). Release 1 has 1,178 seed-manual facts.
- **What's wrong:** they are labelled clearly (confidence `low`, `seed_manual_fields`, a README note), so this is not "presented as sourced". But data rule 1 says "no untraced values in published data". A seed-manual value has no document behind it (no URL or page), so a third party who downloads the bundle gets numbers nobody can check. It is also impossible to show that they were not recalled from a competitor's database (data rule 2, "derived, not copied").
- **Fix:** Menno to choose (recommended first): (a) leave seed-only values out of the open bundle (the website can still show them labelled), or (b) keep them in with the current labels and log that in a decision.

### S4 · A known-impossible value ships in release 1
- **Where:** `data/releases/1/qa.md:16`: `kia-ev6-gen1-77kwh-awd` usable 80.0 > gross 77.4 kWh (single source `kilowatt-openev`, confidence `medium`). It is published in `catalogue.json` and in the open bundle.
- **What's wrong:** QA finds it, but the outlier check is non-blocking (`pipeline/ev_pipeline/qa/checks.py:4`, `:355`), so the value goes out as if it were good.
- **Rule:** AGENTS.md data rule 5 ("anything uncertain goes to the review queue"). The spec's R-05 calls it a physical impossibility.
- **Fix:** make `impossible_values` withhold the field, or make it blocking. Or drop the conflicting KilowattApp fact for this variant and add it to `conflicts.csv`.

### S5 · An offline rebuild silently publishes a crippled release as `latest`
- **Where:** MORNING.md:16 says "rebuild the data release from recorded samples (no network)". `data/staging/` is git-ignored, so on a fresh checkout `uv run ev release` builds from the seed alone. I tried it in a scratch worktree (and reverted it): it published **release 2 with 123 of 199 variants**, NL registrations at 0 % and most fields down 40+ points, set `latest` to 2, and overwrote `data/review/*.csv`. QA reported only "review", because the diff check is non-blocking.
- **Rule:** addendum 6 P2 ("a release only becomes latest if…" you can trust it); pipeline/AGENTS.md rule 3.
- **Fix:** fail the release (or keep it off `latest`) when an `active` source has no staging input, or when the diff loses more than a set share of variants or of a field's coverage. Correct the MORNING/README wording.

### S6 · Licence check only knows about ODbL; share-alike is caught by status alone
- **Where:** `pipeline/ev_pipeline/opendata/bundle.py:161` blocks `"odbl"` by substring. A CC BY-SA source (RVO is one) is kept out today only because its `status` is `blocked`.
- **Rule:** data rule 3 (copyleft never mixed into CC BY output).
- **Fix:** treat every share-alike licence (`-SA`, `ODbL`, `GPL`-style) as incompatible in `source_allowed` and in the release gate, and add a test with an `active` CC-BY-SA source.

### S7 · Release 1 rewritten in place
- **Where:** `data/releases/1/*` has been rebuilt several times on this branch (catalogue.json grew from 1.97 MB to 3.28 MB). `latest` stays at 1.
- **Rule:** AGENTS.md "Versioning": data releases are numbered and can be rolled back.
- **Fix:** acceptable while nothing is public. Note in DECISIONS or the PR that release 1 is "pre-publication, mutable", and that from the first public deploy every rebuild is N+1.

### S8 · `kerb_mass_kg` is defined as mass in running order
- **Where:** `packages/schema/schemas/ev.schema.json:420–423` ("kerb_mass_kg kg (EU mass in running order)").
- **What's wrong:** kerb mass and EU mass in running order differ by about 75 kg (the driver), which is exactly the trap described in Q-039. The field name says one thing and the definition says the other.
- **Fix (coordinator, additive):** rename it to `mass_running_order_kg`, or define it as true kerb mass. The fact is not populated yet, so the change is cheap now.

### S9 · Task ticks don't match the handoff notes
- **Where:** `tasks/T-044-schema-variant-clue.md:11` ticks "Taxonomy `clue_types` validated at release time", but the same file's handoff and MORNING.md say that work is left for T-046 / T-047. T-026 and T-036 are in `review`, but none of their boxes are ticked.
- **Fix:** untick T-044's third box (or mark it "partial: schema only"), and tick or annotate the T-026 / T-036 boxes so the reviewer knows what to check.

### S10 · Staff page has no real guard yet, and CSP still allows inline scripts
- **Where:** `apps/web/src/app/staff/review/page.tsx:27` (only `STAFF_PAGES=1`, no basic auth); `apps/web/next.config.ts` CSP `script-src 'self' 'unsafe-inline'`.
- **What's wrong:** addendum 5 §6 asks for an "env-flagged basic guard" and a nonce CSP. MORNING lists both as "running", so the gap is reported honestly. With the flag on, anyone can read the review queue.
- **Fix:** keep `STAFF_PAGES=0` in production (as in `.env.example`) until auth exists. Track the nonce CSP and the basic guard as open A5.6 items.

---

## Nice-to-have

- **N1 · Brand hard-coded in source names.** `data/sources.yaml` names "EV Finder seed", "EV Finder estimate models" and "EV Finder contributors" reach the public `ATTRIBUTION.md:12,15`. Decision 018: take the brand from config.
- **N2 · Inches in a metric schema.** `wheel_size_in` (schema :421, :983). Rim size in inches is the industry code, which is fine, but log it as a named exception to data rule 6 in Decision 020.
- **N3 · `git clone` fetchers bypass `net.safe_client`.** `pipeline/ev_pipeline/sources/kilowatt_openev/adapter.py:212` and `openev/adapter.py:309` run `git clone` with a fixed URL and no timeout. Low risk (fixed URL, list args, licence-drift check), but add `timeout=` and note the exception in pipeline/AGENTS.md rule 5.
- **N4 · Release files in git are growing.** `catalogue.json` 3.3 MB and `open/variants.json` 1.2 MB are the only files over 1 MB under `data/`. Decision 007 allows this "for now"; plan the move to object storage before release 3–4.
- **N5 · KilowattApp MIT inside CC BY.** Already asked in Q-059 (4). The approach (carrying the notice in ATTRIBUTION.md) looks reasonable, but it is 🟡 until Menno confirms.
- **N6 · `<Num>` takes provenance as optional** (`apps/web/src/components/Num.tsx:15`), so a number can render without its source. Consider making it required, with an explicit `estimate` / `none` value.
- **N7 · MORNING numbers drift.** For example "195 rows" in the bundle (the actual count is 199) and "673 tests" (now 697). Refresh after B1.

---

## Checked and fine

- **Provenance:** all 7,887 facts in `facts.parquet` have `source_id`, `source_licence`, `retrieved_at` and `confidence` (0 missing). QA's blocking provenance check passes on 3,957 row values.
- **Licence gate:** `release/gate.py` fails closed (missing registry, non-`active`, "(to confirm)", "none"). `nyland` is hard-excluded. All 9 sources in release 1 are `active` with named licences. ODbL exclusion is tested (`tests/test_opendata.py:76`).
- **Nyland:** the release staging fixture was replaced with a synthetic "Testmake" record (licence `none`). No Nyland values are in release 1 or the open bundle. The sheet URL is env-only and scrubbed from errors.
- **No network in tests:** every HTTP test uses `httpx.MockTransport` or a stub resolver. All adapters default to `net.safe_client` (host allowlist from `sources.yaml`, SSRF guard, size caps).
- **Secrets / Decision 004:** no keys or tokens in the diff. `.env.example` holds placeholders only. Country configs hold only public "See listings" and charging deep links (allowed by 004). No affiliate ids, rates or sampling targets. Dockerfiles use an allowlist `.dockerignore`.
- **Raw data:** nothing under `data/raw`, `data/local` or `data/staging` is tracked. Fixtures are small (largest is the 16 KB KBA xlsx) and come from open-licence sources; the KilowattApp fixture carries its LICENSE.
- **Schema:** a semantic diff against base shows 0 removed defs or properties, no enum values lost, no new `required` on existing types and no narrowed types (50 new defs). `pnpm --filter @ev/schema gen` reproduces the committed TS and Python types byte for byte. Schema tests pass (66).
- **Invented data:** the Trip fit town temperatures and consumption matrix live in `apps/web/src/fixtures/`, carry `"status": "PROVISIONAL"` and a FIXTURE label, and sit behind `TRIP_FIT=0`. Finance APRs cite ECB/BoE series with dates, and NL is left null rather than guessed. The seed year changes cite RDW/EEA/KBA counts. The new BMW i3 was not invented (Q-065).
- **CI hardening:** `pull_request` only (no `pull_request_target`), per-job `permissions`, every third-party action pinned to a 40-character SHA, and the audit job is warn-only.
- **Lanes:** the branch acted as coordinator for the schema under addenda 4/5/7 (authorised). Decisions are renumbered without duplicates (no duplicate Decision or Q ids). No edits to `docs/spec/`, other workstreams' files or brand-design files.
- **Other checks:** web unit tests 183/183 pass; `tsc --noEmit` and ESLint are clean; ruff check and format are clean; registrations are kept per source and kind, never summed (tests present).

## Not checked

- Playwright e2e (`pnpm --filter @ev/web e2e`) and the web production build. Not run, to stay quick.
- CI status on GitHub for PR #1, and whether the branch still merges cleanly with the current `main` (no network or fetch used).
- Whether the live sources actually reproduce release 1 (`data/staging` isn't in git; see S5).
- The factual accuracy of individual seed values, the /learn drafts and the R-02/R-06/R-07 research citations.
- Addendum 6 P1–P7 (refresh, rollback/diff, source health, data-refresh workflow, top-40 list, Wikidata/RDW defects/fueleconomy, manual facts). MORNING lists these as running or queued, and none are on the branch except the CLI subcommand scaffold, so there was nothing to review.
- Accessibility (axe), performance budget and i18n completeness beyond the existing unit tests.

---

## Delta pass (d06535a, 2026-11-15 ~05:00 UTC)

**Reviewed:** `origin/proto/overnight-1` at `d06535a6e010a18ab497e7be0881867de04d97ab` ("Battery gate: contradicting records go to review"): 47 commits since `8b48bd7`, 362 files, +57k / −6k lines. Line numbers in this section refer to `d06535a`. The branch's own second review (`audits/A-05-overnight-review.md`, F1–F12, L1–L7) and its fixes were taken as read. I checked the fixes I relied on and don't repeat its findings.

**Checks run (worktree at d06535a):**

| Check | Result |
|---|---|
| `uv run pytest -q` | **1113 passed**, 0 failed, 0 xfail. Also 1113 passed with no network at all (`unshare -rn`, `uv run --offline`), so the tests really are offline |
| `ruff check` / `ruff format --check` | clean / 146 files formatted |
| `python -m ev_pipeline.qa check-release data/releases/latest` | pass (provenance 5,708 values, licence gate 13 sources / 40,104 facts) |
| `pnpm install --frozen-lockfile` | ok |
| `pnpm -C apps/web test` | 39 files, **281 passed** |
| web `tsc --noEmit` / ESLint | clean / clean |
| `pnpm --filter @ev/schema test` / `gen` | 74 passed / regenerated types match the committed ones byte for byte |
| Fresh-checkout `uv run ev release` (to re-test S5) | **published release 2 with 123 rows** (reverted; the worktree is removed) |
| Not run | Playwright e2e, axe, `next build`, the data-refresh workflow on GitHub |

### First-pass findings: status at d06535a

| Id | Status | Evidence |
|---|---|---|
| **B1** stale release, red tests | **Fixed** | 1113 passed; `test_mg4_has_one_row_per_real_car` passes; release 1 rebuilt (244 rows, matching MORNING.md:42) |
| S1 RDW named while Q-037 is open | **Still open, and wider** | `open/ATTRIBUTION.md:15` keeps the interim line. The new `rdw-tgk` line (`:16`) says "Bron: RDW Open Data" (see D1). Known-issues UI text names RDW too (`i18n/en.json:480,492`) |
| S2 KBA deep link | **Still open** | `open/ATTRIBUTION.md:11` and `catalogue.json` `sources[kba-fz10].url` still point at `…/fz10_gentab.html` |
| S3 seed-only values in CC BY bundle | **Still open** (Menno's call, Q-015 now at the top) | 140 of 244 rows in `open/variants.csv` still cite `seed-manual`. The new `cited:` block (Decision 026) is the right way out: 1 value cited so far (i3s battery) |
| S4 impossible value ships | **Fixed** | `qa/pack_guard.py` (T-057) and `qa/value_guard.py` (F7). `kia-ev6-gen1-77kwh-awd` is now 77.4 kWh; `qa.md:10` reports 0 impossible values. MORNING.md:110 still says it is flagged (N7) |
| S5 offline rebuild publishes a crippled `latest` | **Half fixed** | `ev refresh` refuses (`refresh/runner.py:509-521`). Plain `ev release` doesn't: reproduced (D2) |
| S6 licence check knows only ODbL | **Still open** | `opendata/bundle.py:161` and `release/gate.py:43-51` unchanged. A `-SA` source is kept out only by its status |
| S7 release 1 rewritten in place | **Still open** | Release 1 was rebuilt again in this delta, and there's no "pre-publication, mutable" note. The new data-refresh workflow writes N+1, which is right from now on |
| S8 `kerb_mass_kg` = running order | **Fixed** | Decision 023 adds `mass_running_order_kg`. Schema `ev.schema.json:339` now defines kerb mass as "without driver" |
| S9 task ticks vs handoff | **Still open** | `tasks/T-044…:11` still ticks "clue_types validated at release time", but only `schema_models.py` knows `clue_types`. T-026 / T-036 boxes are still unticked |
| S10 staff guard / inline-script CSP | **Fixed** | Basic auth in `proxy.ts:47-57`, again in `staff/layout.tsx` and `staff/review/page.tsx` (`requireStaff`, constant-time). The matcher has no header exemptions. `csp.ts` has no `'unsafe-inline'` for scripts (nonce or build-time hashes; styles keep it, which is acceptable) |
| N1 brand in source names | Still open | `ATTRIBUTION.md:13,17`; also `apps/web/src/lib/credits.ts:101` (`owner === "EV Finder"`) |
| N2 inches exception | Still open | Decision 020 (`DECISIONS.md:308`) names `wheel_size_in` but doesn't call it an exception to data rule 6 |
| N3 git clone outside safe fetch | Mostly fixed | `net.check_git_url` + `protocol.allow` flags (Decision 026, `tests/test_git_sources.py`). Still no `timeout=` at `kilowatt_openev/adapter.py:223` or `openev/adapter.py:320` |
| N4 release files in git | Worse | `catalogue.json` 3.3 → **7.8 MB**; new `charging_stats.json` 1.5 MB; `open/variants.json` 2.1 MB |
| N5 MIT inside CC BY | Still open | Q-059 (4) unanswered |
| N6 `<Num>` provenance optional | Still open | `components/Num.tsx:17` |
| N7 MORNING numbers drift | Still open | MORNING.md:106 "195 rows" (now 244), :116 "673 tests" (now 1113), :110 EV6 still "flagged" |

### New findings in the 47 commits

#### Blocker
None.

#### Should-fix

**D1 · The `rdw-tgk` credit says "Bron: RDW" while Q-037 is open**
- **Where:** `data/releases/1/open/ATTRIBUTION.md:16`; `catalogue.json` `sources[rdw-tgk].attribution` (also `rdw`, `rdw-defects`); `apps/web/src/lib/credits.ts:32-46`. `FALLBACK_WORDING` overrides `rdw` and `rdw-defects` but not `rdw-tgk`, so the About page shows the release's "Bron: RDW Open Data (opendata.rdw.nl), CC0." for the type-approval source.
- **Rule:** licence and terms (data rule 3; Q-037: "do not state the data comes from RDW").
- **Fix:** add `rdw-tgk` to the override. Better: keep the interim RDW wording in one config table that both the pipeline (release `attribution`, ATTRIBUTION.md) and the web read, so a new RDW dataset can't miss it. Not needed for merge; needed before anything public.

**D2 · `ev release` on a fresh checkout still publishes a crippled release as `latest` (S5 remainder)**
- **Where:** `pipeline/ev_pipeline/release/build.py:796-838` (`write_release` → `write_latest`). The missing-staging guard exists only in `refresh/runner.py:509-521`. MORNING.md:18-19 still tells a reader to run `uv run ev release` to "rebuild … from recorded samples (no network)".
- **Reproduced:** fresh worktree, no `data/staging`: `uv run ev release` printed `"rows": 123, "removed": 121`, `"outcome": "published data/releases/2"`, and `latest` became 2 (it also rewrites `data/review/*.csv`).
- **Rule:** addendum 6 P2 (only a trustworthy release becomes latest); pipeline/AGENTS.md rule 3.
- **Fix:** move the "active source has no staging input" check into `build_release` (or the `ev release` command), with an explicit `--allow-partial` for tests. Correct the MORNING/README wording: without staging, this command rebuilds from the seed only.

**D3 · The "~10 % plate sample" for Known issues is probably not 10 % for older years (🟡 plausible, not verified against RDW counts)**
- **Where:** `pipeline/ev_pipeline/sources/rdw_defects/adapter.py:85` (`kenteken like '___7%'`), described as a "deterministic ~10% plate sample" in `catalogue.json` `known_issues.sample_rule`.
- **What's wrong:** the filter needs a digit `7` in the 4th plate position. Dutch plate formats from about 2008 to 2015 (sidecodes 7 and 8, `99-XXX-9` and `9-XXX-99`) have a letter there, so cars plated in those years can never be sampled. Release 1 fits that pattern: 20 / 51 / 157 / 129 sampled cars for first-registration years 2013–2016, against 5,100–10,700 a year for 2019–2023. The few older cars that do get in are mostly imports plated later, so they don't represent their year. The same-year baseline shares the bias, so comparisons are less wrong than the absolute rates, but the label "~10 %" is not honest for those cohorts.
- **Rule:** data rule 5 (uncertain → review / labelled); "every number has a source" with an honest method.
- **Fix:** check the sampled share per year against the RDW fleet count. Then sample on something every plate format has (for example, a hash of the plate modulo 10, computed after fetch), or fetch all plates for small cohorts. Until then, mark cohorts whose sampled share is far below 10 % as `few_reports`.

#### Nice-to-have

- **D4 · `pipeline/.coverage` is committed** (53 KB SQLite, added in `9f3a8da`). It's a build artefact holding the builder's local absolute paths (`/home/claude/zkmenno/…`). Remove it and add `.coverage` to `.gitignore`.
- **D5 · The `.env.example` staff password is accepted.** `STAFF_BASIC_AUTH=staff:change-me` (`.env.example:17`) passes `checkStaff` (`apps/web/src/lib/staff-auth.ts:19-31`). Anyone who copies the example file and sets `STAFF_PAGES=1` gets a known password. Refuse the placeholder and very short values. Basic auth also has no rate limit (fine behind Caddy, but note it for WS4).
- **D6 · Known-issue rates from very small groups.** `min_sample_cars: 20` and `min_cars_per_code: 3` allow "15 per 100 cars" from 3 cars. `few_reports` hides some of these. Before going public, consider a higher minimum or a shown range (confidence interval).
- **D7 · DfT EVCI attribution says "data collated by Zapmap".** The OGL covers it "except where otherwise stated", and the builder found no third-party marking (`sources.yaml` dft-charging). Fine 🟡, but worth one line in QUESTIONS, since Zapmap is a commercial data owner.
- **D8 · EPA range is stored to 0.1 km** (`sources/fueleconomy/adapter.py:123`). EPA gives whole miles, so a figure like 550.4 km suggests more precision than the source has. R-28 rounds to whole km. Cosmetic.

### Focus checks (all fine unless noted)

- **KBA FZ10 back to 2019:** one `registrations[]` entry per data year, never summed. The licence line is checked per file and fails closed: the 2018 file names no licence, so it's skipped and logged (`kba_fz10/adapter.py:28-33`, Q-082). Fetching from `kba.de/SharedDocs` is fine. The deep *link* in credits is still S2.
- **EEA 2018+:** final dataset per year. 2018/2019 come from the all-years table filtered on `Status='F'` and the version file, with the SDI metadata record per year (`eea/adapter.py:7-13,79-80`). One entry per year.
- **Wikidata (T-051 / T-059):** CC0, corroboration only. "Never a value" is enforced (`merge/generation_years.py:14`). The 23 new models take their specs from OpenEV / KilowattApp / RDW / TGK, with no new uncited seed values. Their model notes cite registration counts with dataset ids and dates. The User-Agent names only the repo, no personal data.
- **RDW known issues:** the block carries `source_id`, `retrieved_at`, `confidence`, report window and sample rule. Plates are never stored. Comparison is within the same first-registration year only. See D3 and D6.
- **Charging stats:** EAFO stays `blocked`, and `release/charging_stats.py:7-10` ships a file only when its registry source passes the gate and its meta says `releasable`. BNetzA is CC BY 4.0 with "Bundesnetzagentur.de" attribution; DfT is OGL with its notice. Both are in `sources.json` (A-05 L5 fixed). Aggregates only (Decision 012).
- **No invented data:** the battery gate (Decision 027) results check out against known figures (Zoe R90 41 kWh, Q4 40 e-tron 77 kWh net, Mach-E ER 88 kWh). The i3s cited value has its URL, date and an exact quote.
- **No secrets / rates:** no tokens or keys found in the delta. `.env.example` holds dummies only. `data/snapshots/` and `data/runs/` are git-ignored, and nothing under `data/staging|raw|local` is tracked. The data-refresh workflow: `permissions: {}` at top; the `refresh` job is read-only; the `pr` job writes only the release folder plus `latest`, uses a masked one-off token header, and actions are pinned to SHAs. One new dev dependency (`@axe-core/playwright`, for the a11y checks, listed in MORNING).
- **CSP / staff guard:** see S10, fixed. The F2 prefetch bypass that A-05 found is closed (no `missing:` in the matcher, `proxy.test.ts`).
- **Finance calculator** (`data/taxonomy/finance_profiles.yaml`, untouched in these 47 commits) **vs `research/R-20-finance-rates.md`:** the **ECB values agree exactly**. DE 8.91 %, FR 6.11 %, BE 6.24 % (2026-09, same series `MIR.M.{CC}.B.A2B.A.C.A.2250.EUR.N`, same provisional flags, same 2026-08 values 8.99 / 6.14 / 6.55). UK is BoE IUMHPTL 7.11 % (2026-10) in both. The calculator turns the APR into a monthly rate as an effective annual rate, `(1+APR)^(1/12)−1` (`apps/web/src/lib/finance.ts:52-54`), which is right for an EU APRC. **Disagreements:**
  1. **NL:** the branch leaves the rate null and asks the user. R-20 proposes geld.nl's 7.29 % (🟡 comparison site). Keep null: it follows the file's "central bank only" rule, and a commercial site's figure has its own licence question.
  2. **Deposit default:** the branch uses 0 % (`finance.ts:48`, labelled assumption); R-20 suggests 10 % 🟡. Both pick 48 months for the term. Menno's choice, low stakes.
  3. **ECB licence:** the branch writes "(to confirm)"; R-20 rates free reuse with attribution 🟢. The branch could drop "to confirm" for ECB. BoE stays unconfirmed in both.
  4. **Source URL:** the branch links the human ECB page; R-20 used the data API (the page was blocked for R-20's agent). Both are fine.
- **EPA range:** `sources/fueleconomy/adapter.py:11,121-123` reads column **`range`** (miles × 1.609344) and never `rangeA`. That matches R-28 (BEV range is `range`; `rangeA` is empty for BEVs). EPA consumption is ignored (not WLTP), and EPA → WLTP-equivalent stays an `estimate` (A-05 L7).

### Not checked in this pass
Playwright e2e and axe, `next build` (CSP hash manifest, APP_URL checks), the data-refresh workflow on GitHub, whether live sources reproduce release 1, the factual accuracy of individual new-model values, and RDW fleet counts per year for D3.
