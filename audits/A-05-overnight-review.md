# A-05 Overnight review (second wave): data honesty, licence gate, security, refresh, web

**Type:** data quality + security review · **Date:** 2026-11-15 · **Auditor:** fresh reviewer agent (has not seen the build), branch `proto/overnight-1` · **Data:** release 1 (`data/releases/latest` = `1`, 244 rows, generated 03:46 UTC)

**Scope:** work since the first review wave (MORNING.md "Addenda 4 + 5", "Addenda 6 + 7", "Bottomless backlog"; commits `3cea565`..`9c35fd5`). Highest-risk pieces picked: attach-only matcher (power gate, `tgk_pick`), merge `SPREAD_SOURCES`, `derive/rows.py`, release licence gate, CSP + staff guard, safe fetch, GitHub workflows, refresh/rollback, country/lang URLs, loan calculator, 15-row spot check.

**Left out:** `apps/web/src/lib/used-rankings.ts`, `PriceBand`, `data/taxonomy/glossary_terms.yaml` (another builder is editing them). The working tree also has uncommitted edits by that builder in about ten more web files (KnownIssues, YearsBadge, charging page, generation/variant pages, top list page, catalogue.ts). Anything I say about those files is about the working tree, not a commit.

**Tests added:** `pipeline/tests/test_a05_review.py`: 1 passing test that pins down the root cause of F1, plus 2 `xfail(strict=True)` tests that reproduce F1 and F6. They turn into XPASS errors once fixed, so remove the marker in the same commit as the fix.

## Check runs

| Check | Result |
|---|---|
| `pnpm install --frozen-lockfile` | ok |
| `pnpm --filter @ev/schema test` | 74 passed |
| `pnpm --filter @ev/web lint` / `typecheck` | clean / clean (working tree includes the other builder's edits) |
| `pnpm --filter @ev/web test` | 35 files, 256 passed |
| `uv run ruff check .` / `ruff format --check .` | clean / 141 files formatted |
| `uv run pytest` | 1031 passed before my tests; with `test_a05_review.py` 1032 passed, 2 xfailed |
| `ev_pipeline.qa check-release ../data/releases/latest` | pass (provenance 5,811 values, licence gate 13 sources / 41,578 facts); 3 non-blocking impossible values (see F7) |
| web `build` / `e2e` | **not run.** The other builder's in-progress files are in the tree, and `pnpm build` regenerates committed `*.generated.json` files. F2 was reproduced on `next dev` instead. |

## Findings

### Critical

**F1. Records with no variant name are treated as an exact name match for any variant called "base". Blended RDW model-year WLTP and consumption, and EPA ranges, land on the entry trim.**
`pipeline/ev_pipeline/match/matcher.py:271-274` (`VariantInfo.named`: `k = key(name or "base")`), used at `:960` (`exact = [c for c in pool if ...named(sid, rec_name)]`).
- RDW coarse records (`[merk|handelsbenaming|jaar]`) have `variant_name=None` and no power evidence, so the Q-086 power gate is skipped (`:951-952`). The `exact` shortcut then picks the OpenEV variant named `base` before any evidence is scored. The coarse WLTP is the median of a plate sample over every trim of that year (the RDW adapter docstring, `sources/rdw/adapter.py:40-42`, says other trims "are not represented"), so it is usually the best-selling long-range trim's figure.
- Reproduced: Volvo EX30 base (51 kWh, real WLTP 337–344 km per OpenEV, RDW type split and about 10 TGK versions) is published with **475 km WLTP** (the Extended Range figure). Its real range (389 km), motorway consumption and km-per-10/20-min follow from that. The note says "16 conflicting value(s) not used".
- Size: 470 published values cite a coarse RDW record; **138 of them are on `*-base` variants**. Their WLTP comes only from coarse RDW on 19 base rows: e-C4, Born, Tavascan, Puma Gen-E, I-Pace, CLA (743 km), EQA, EQB (from an "EQB 300 4MATIC" record), Leaf ZE1, e-2008, e-208, Macan, Taycan, R5, Mégane, Scénic, Elroq, EX30, XC40 Recharge. Consumption is wrong on about 22 rows. The same path puts `fueleconomy` records with no variant name on `base` (EQB base shows the EPA range of "EQB 350 4matic").
- Merge then lets that single record win: `data/field_sources.yaml:27-29` makes `rdw` primary with `merge: priority`, so one blended value beats 16–23 agreeing values from OpenEV, TGK and RDW's own type-split records.
- **Fix:** (a) in `named()`, return False when `name` is empty or None (never alias a missing name to "base"); (b) make coarse RDW groups (no type/variant codes, no power) never attach to a variant: either generation-level corroboration only, or drop WLTP and consumption at the coarse level and keep only the T-054 type-split records; (c) in merge, when the priority winner disagrees with 2+ independent sources that agree among themselves, send the field to review or fall back to majority, instead of publishing the priority value. Then remove the xfail marker on `test_nameless_rdw_group_does_not_land_on_base_by_name`.

**F2. Staff Basic-auth bypass: one request header skips `proxy.ts`, and the auth runs only there.**
`apps/web/src/proxy.ts:71-80` (`matcher.missing` for `next-router-prefetch` and `purpose: prefetch`) together with `:58-66` (the staff guard lives only in the proxy). `src/app/staff/review/page.tsx` checks only `staffPagesEnabled()`.
- Reproduced on `next dev` with `STAFF_PAGES=1 STAFF_BASIC_AUTH=u:secretpw`: a plain `GET /staff/review` returns **401**. The same request with `Purpose: prefetch` returns **200 and 1.1 MB of review-queue HTML** (review ids such as `um-b9866b1c95` included), with no CSP header.
- The same header also strips the CSP (and the language redirects) from any public page. A `<link rel=prefetch>` document can be reused for the navigation, so pages can be served without the policy.
- **Fix:** move the staff check out of the proxy's skippable path. Either drop the `missing:` conditions for `/staff` (a separate matcher entry without `missing`), or better, check `checkStaff(headers().get("authorization"))` in `app/staff/layout.tsx` / the page as well (defence in depth; the page is `force-dynamic` already). Keep the prefetch exemption only for real RSC prefetches (`next-router-prefetch` together with the `RSC` header), never for `purpose: prefetch`. Add an e2e test: `/staff/review` with `Purpose: prefetch` must be 401 or 404.

### High

**F3. Canonical, hreflang and sitemap URLs point at `http://localhost:3000` in the production image.**
`apps/web/src/lib/site-paths.ts:23` falls back to localhost when `APP_URL` is unset. `apps/web/Dockerfile:53` builds without `APP_URL` (no `ARG`, and `.github/workflows/images.yml` passes no build-args), and model, generation, variant and learn pages are static. Their metadata and `sitemap.xml` are therefore baked at build time; the runtime `web.env` (`infra/deploy/compose.ev.yml:51`) comes too late.
**Fix:** add `ARG APP_URL` + `ENV APP_URL=$APP_URL` in the build stage and pass it from `images.yml`. Make `siteUrl()` throw when `NODE_ENV=production` and `APP_URL` is missing or `localhost` (fail the build, don't ship a wrong canonical). Add a CI assertion on one built HTML file.

**F4. TGK "NEDC" is often the WLTP figure, published as NEDC.**
`pipeline/ev_pipeline/sources/rdw_tgk/adapter.py:475-477`. In staging, 168 of the 598 TGK versions that carry both values have NEDC equal to WLTP (±1 km). In release 1, 7 of the 39 rows with `nedc_range_km` show exactly the WLTP figure (Kona 64 kWh "NEDC 484", whose real NEDC is about 546; Ioniq 5 58 kWh, EV6 58 kWh, Atto 3, MG ZS LR, Kona 39 kWh, i3s), and 15 NEDC rows start in 2020 or later. RDW evidently fills the NEDC column with the WLTP value on WLTP-only approvals. This breaks the spirit of Decision 023: what is shown as NEDC is WLTP.
**Fix:** in the adapter, emit no `nedc_range_km` / `nedc_consumption_kwh_100km` when they equal that version's WLTP best case (±1 km / ±0.1 kWh), or when the approval is under 2018/858 with a first admission after 2020. Log the drop count in the run log and add a fixture test (Kona 64 kWh).

**F5. 1,016 published values come only from `seed-manual`, which is "written from model knowledge, no sources fetched".**
`data/seed/variants.yaml:2` and the `merge/merge.py` docstring ("hand-entered from memory"). In release 1, 1,016 of 6,794 provenance entries list only `seed-manual`, among them 79 `power_kw`, 37 `dc_peak_kw` and 33 `battery_kwh_net`. Polestar 2 LR single has battery, power and DC from the seed alone; so do Ioniq 5 58 kWh battery and DC, and Model 3 SR+ battery. All are `confidence: low`, none `estimate: true`, and they go into the CC BY open bundle. The source name says "unchecked", but hard rule 1 ("no value from memory") is still broken. This predates the second wave but is not resolved (Q-015 still unanswered).
**Fix:** treat `seed-manual` numbers as `estimate: true` with an "unverified" badge in `Num`, keep them out of `open/variants.*`, and exclude them from rankings. Track their replacement with TGK, EEA or OpenEV data as a task: count per field per release in `qa.json`, target 0 for headline fields.

### Medium

**F6. A `SPREAD_SOURCES` source whose own vote conflicts can still confirm the value (`high` confidence).**
`pipeline/ev_pipeline/merge/merge.py:163-170`: followers or spread versions that agree with the winner join `agreeing` even when that source's vote (its earliest version) is in `conflicts`. Reproduced in `test_tgk_whose_vote_conflicts_does_not_confirm_the_value`: openev 400 against TGK vote 340 plus a later TGK version at 400 gives `confidence high`, and `rdw-tgk` is listed both as a conflict and as an agreeing source.
**Fix:** when a spread source's vote is a conflict, its agreeing versions may back `fact_ids` but must not count in `independent`. Compute `independent` from the voters only.

**F7. Impossible values are non-blocking, and they are symptoms of wrong attachment.**
`pipeline/ev_pipeline/qa/check_release.py:12`. Release 1 flags Mégane 40 kWh (WLTP 467 km from an RDW `uitvoering` record, which is the 60 kWh car's figure), Q4 40 Sportback (battery 48 kWh with WLTP 508 km) and Kona SX2 SR (36 kWh with 380 km).
**Fix:** make `km/kWh > 10` (WLTP / usable kWh) a blocking check, or at least drop the offending field into the review queue before publishing. Never publish both halves of a pair that cannot both be true.

**F8. Generic name words decide attach-only picks (fueleconomy, ADEME, KilowattApp).**
`matcher.py:815-830` (`_STOP_TOKENS`) and `_best_candidate:1173-1201`. "range", "long" and "standard" are not stop words, so "Model S **Standard Range**" (EPA 458.7 km) lands on "Raven **Long Range**" (EPA about 595 km) through the shared word "range". The WLTP equivalent and the estimated consumption of that row are then derived from the wrong EPA figure.
**Fix:** add trim-neutral words (range, long, standard, extended, plus, max) to the stop list, or require kWh, power or WLTP evidence beyond name words for non-gated sources.

**F9. Spot-check source errors on single-source values.**
- Zoé ph1 R110 `dc_peak_kw` 150 kW (`kilowatt-openev`). The car has no DC charging; the ZE50 (2020) had 50 kW CCS.
- Cupra Born 45 kWh: battery from a KilowattApp record named "110 kW - 55 kWh".
Single-source DC peaks that are not backed by OpenEV should fall back to review.
**Fix:** add a range check by generation (no DC before the generation's `ccs` change marker), and send single-source `dc_peak_kw` from `kilowatt-openev` that contradicts the seed's `charge_port` to review.

**F10. CSP fails open to `'unsafe-inline'` in production when the hash manifest is missing.**
`apps/web/src/proxy.ts:23,33`. One missed build step silently removes the main XSS protection.
**Fix:** in production, fail closed: serve the nonce-only policy (static pages lose inline scripts but stay safe), or refuse to start and make `/health` fail when the manifest is missing. Add a Docker smoke test that the manifest exists in the runtime image.

**F11. The data-refresh job keeps a `contents: write` token on disk while it runs third-party data and code.**
`.github/workflows/data-refresh.yml:42` (checkout without `persist-credentials: false`). `ev refresh` runs `git clone` of two third-party repos and parses downloaded XLSX, CSV and JSON while the write token sits in `.git/config`.
**Fix:** `persist-credentials: false` on checkout, and in the PR step push with `git push "https://x-access-token:${GH_TOKEN}@github.com/${GITHUB_REPOSITORY}" ...`. Or split it into two jobs: refresh (read-only, uploads the release folder as an artifact), then PR (write, no pipeline code run).

**F12. `tgk_pick` still has two guess-like tie-breaks.**
`matcher.py:1132` lets candidates of unknown battery with any name word join battery-fitted ones, and the name count can then beat the battery evidence. `:1147-1150`: "no 30-minute power → prefer AWD" infers from a missing field. Decision 024 says only unique fits attach. Both are documented, but they are heuristics, not evidence.
**Fix:** when both battery-fit and name-only candidates survive, go to review. Make the AWD rule narrow the pool only, never break a tie on its own (or gate it behind a flag and measure).

### Low

- **L1. Rollback accepts QA status `unknown` and skips the licence re-check.** `commands/releases.py:74` refuses only `fail`, `missing` or `unreadable`, so a `qa.json` without a `status` passes. A rollback to an old release is also not re-checked against today's `sources.yaml` (a source blocked since then would come back). **Fix:** allow only `pass` (and `warn`, if that exists), and run `check_release()` on the target before `write_latest`.
- **L2. `write_latest` does not fsync** (`release/build.py:754-759`). It is atomic for readers, but after a power loss the pointer can be empty or old. **Fix:** fsync the temp file and the directory.
- **L3. The used-price ranking value is shown without `Num`** (`app/[country]/[lang]/top/[list]/page.tsx:217`, `e.value.toLocaleString`, a derived km-per-price figure with no provenance or estimate badge). The pages are hidden today and the file is in the other builder's working tree. **Fix:** wrap it in `Num` with derived provenance and `estimate`.
- **L4. hreflang on used-price lists** lists every served pair, but `/top/under-…` exists only where enough prices exist (`sitemap.ts` filters them; `pageMeta` does not). **Fix:** build the `alternates` languages from `visibleUsedRankings` per country.
- **L5. Release `sources.json` omits the charging-stats sources** (`bnetza`, `dft-charging`). The licence gate covers them through `charging_stats.json`, but the source-health doc is incomplete. The taxonomy keeps `source_id: eafo` on `charging_definitions[afir-recharging-point]` and three `power_bands` (labels only, no EAFO data). **Fix:** add the charging sources to `sources.json`; mark EAFO taxonomy rows `gated: true` so the UI never offers an EAFO series.
- **L6. `git clone` in the `openev` and `kilowatt_openev` adapters bypasses `net.py`** (hard-coded GitHub URLs, so the risk is low; git honours environment proxies). **Fix:** assert that the host of `REPO_URL` is in that source's `hosts:` before cloning, and pass `-c protocol.allow=never -c protocol.https.allow=always`.
- **L7. EPA → WLTP-equivalent estimate** (`derive/rows.py:362-365`) feeds consumption and real range when WLTP is missing. It is labelled `estimate` with a note and never written to `wltp_range_km`, so it complies, but F8 shows its input can be the wrong trim.

## Verified clean

- **Licence gate:** `sources.json` lists 13 sources, all `registry_status: active` with a named licence. `nyland` and `manual` appear nowhere in `data/releases/1/` (catalogue, charging_stats, open/, qa, run_log). `eafo` appears only as taxonomy labels and source_ids on definitions and bands (L5), never as data. `charging_stats.json` holds only `bnetza-ladesaeulenregister` (2,720) and `dft-ev-charging-infrastructure` (141), both active (CC-BY-4.0, OGL-UK-3.0). `check-release` re-checks the licence gate against today's `sources.yaml`.
- **NEDC never fills WLTP** (adapter, matcher and rows: separate fields, separate policy). **Running-order mass never fills `weight_kg`** (TGK never emits `weight_kg`; only ADEME "poids à vide" and OpenEV curb weight do). **EPA never merges with WLTP** (`epa_range_km` has its own policy and row field). F4 is the opposite problem: WLTP filling NEDC.
- **Power gate (Q-086):** tolerance, the no-match → review path, and the unknown-power-needs-evidence path are correct and tested. Its gap is records with no power (F1).
- **`tgk_pick`:** ties and misfits go to review with reasons; only `len(pool) == 1` attaches (apart from F12).
- **Registrations:** one entry per (source, country, period, kind); sums only within one source, period and country group; the web never sums (`registrations.ts`). A6 e-tron DE shows EEA and KBA side by side.
- **Estimates labelled:** derived `consumption`, `motorway`, `real_range` and DC km entries carry `estimate: true` and a `model-estimate` source.
- **CSP:** `script-src 'self'` + nonce or sha256 hashes, no `'unsafe-inline'` for scripts when the manifest exists; `object-src 'none'`, `frame-ancestors 'none'`, `base-uri 'self'`, `form-action 'self'`; `'unsafe-eval'` only in dev. The manifest is also written into the standalone output (`scripts/csp-hashes.mjs:78-79`).
- **Staff guard logic** (`staff-auth.ts`): SHA-256 then `timingSafeEqual` (constant time, no length leak); fails closed when `STAFF_BASIC_AUTH` is missing or malformed; `STAFF_PAGES` off gives a 404. The flaw is only where it runs (F2).
- **Safe fetch:** every HTTP adapter builds its client with `client or net.safe_client(NAME, …)` (13 adapters + refresh runner + probe); no `requests`, `urllib` or bare `httpx.Client(` outside `net.py`. Https only on the default port; IP literals and user info refused; every resolved address must be public (IPv4-mapped included) and is pinned on connect; redirects re-checked (max 5); size cap counted on the wire and after gzip; total time budget; `trust_env=False`.
- **Workflows:** no `pull_request_target`; top-level `permissions: contents: read` (`{}` for data-refresh); per-job permissions; every third-party action pinned to a commit SHA; `persist-credentials: false` in ci and images; image push only on `main` with `packages: write`. Data-refresh stages only `data/releases/N` + `latest`, and runs on schedule or dispatch only (F11 aside).
- **Refresh and rollback:** the release is built in `.tmp-N`, QA runs before `rename`, a blocking QA failure raises and removes tmp, and `latest` is switched by temp file + `os.replace`. Rollback refuses `fail`, `missing` and `unreadable` (L1) and logs to `releases.jsonl`.
- **URLs:** `routeLang` gives 307 for `/` and `/{country}` (cookie-dependent, `Vary: Cookie`) and 308 otherwise. There is no open redirect (segments come from a validated country slug, empty segments are dropped). hreflang tags are `lang-REGION` with `uk → GB`, plus an `x-default` of `/nl/en`. The sitemap covers every served pair × page, has fewer than 50k URLs and leaves out compare and staff pages.
- **Loan calculator** (`lib/finance.ts`): `r = (1 + APR)^(1/12) − 1` (the effective-rate convention; APRC per CCD2 is an effective annual rate, so this is right); annuity `P·r / (1 − (1+r)^−n)` with the `r = 0` case; input bounds checked. The CCD2 warning (`LoanWarning`) is always rendered with figures. NL `typical_apr: null` gives an empty field asking for a rate (none invented). On UK pages `financeLinksAllowed` stops lease and finance links (the only link is the BoE statistics source at Nerd level). I did not check that the ECB MIR series codes are the APRC series rather than the AAR/NDER series. Worth one manual check.
- **Spot check, 15 random rows (seed 20261115), up to 9 fields each:** every non-derived value equals its staged record's value and unit (kWh, km, kW, kg, kWh/100km; no unit slips). Wrong-variant cases found: EQB base (F1), Elroq base WLTP from the "ELROQ 85" record (fits only because OpenEV's "Base" is 77 kWh), Model S Raven LR EPA from "Standard Range" (F8), Model Y Performance WLTP 507 from the coarse Model Y year group (the Long Range figure, `high` because Performance's 514 is within 2 %). Source errors: Zoé R110 DC 150 kW, Born 45 kWh (F9). Ioniq 5 58 kWh NEDC = WLTP (F4). Correct rows: Q8 50 Sportback, Model 3 SR+ (TGK), Zoé R240 (TGK NEDC 240, mass 1,502), Ioniq 6 SR, Atto 3 (apart from NEDC), Model 3 Highland Performance, R5 base.

## Suggested tasks

1. **T-0xx (blocker, WS1):** F1 (a)–(c) + rebuild release 1. Re-check the 19 base rows by hand; expected change: EX30 base WLTP 475 → about 337–344.
2. **T-0xx (blocker, WS2/WS4):** F2: staff auth inside the app plus the matcher change; e2e test with `Purpose: prefetch`.
3. **T-0xx (WS4):** F3 + F10: `APP_URL` build arg with a fail-closed `siteUrl()`; CSP manifest presence check in the image smoke test.
4. **T-0xx (WS1):** F4 NEDC = WLTP drop; F7 make the km/kWh check blocking; F6 merge independence; F8 stop words; F12 tie-breaks.
5. **Coordinator:** F5 `seed-manual` policy (answer Q-015, decide on the estimate badge and open-bundle exclusion); F11 workflow split.
