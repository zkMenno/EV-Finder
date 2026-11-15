# A-20 · Review of `proto/overnight-1` (overnight prototype 1)

**Reviewed:** `origin/proto/overnight-1` at commit `8b48bd7c44cac991a8bd4d93bf27ff01b8b4bdf8` ("MORNING: seed quality"), against base `5b171d5`. 355 files, +40k / −3k lines. Reviewer: fresh-eyes auditor, 2026-11-15. Line numbers refer to that commit.

**Verdict: not mergeable yet, but close. One blocker.** The pipeline test suite is red on the branch tip: the committed release 1 was not rebuilt after the last seed-quality commit, so the release does not match the seed and code that ship with it (and MORNING.md describes a result the release does not contain). Fix that and the branch is mergeable as a draft-quality prototype. The data rules hold up well: every fact in release 1 has source, retrieved date, confidence and licence. The licence gate fails closed. No ODbL is in the release, and a test guards that. Nyland data stays out (the fixture is synthetic). Tests never touch the network. No secrets, rates or sampling targets are in the tree. Schema changes are purely additive, and the generated types match a fresh regeneration. The should-fix items are mostly licence and wording matters that must be settled **before anything goes public**, not before merge.

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
