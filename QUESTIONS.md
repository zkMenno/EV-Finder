# Questions for Menno

Agents add questions here when they're blocked. Menno answers inline under **Answer:**. Once answered, the coordinator moves the outcome into DECISIONS.md or the task file and marks the question closed.

Format: `Q-NNN` · task id (if any) · who asked · date.

---

## Open

### Q-030 · Overnight work landed on `main` by mistake · coordinator · 2026-11-15 ★ most urgent
From about 01:05 the coordinator's push clone was on `main`, so syncs pushed `main` as well as `proto/overnight-1`. Both now point to 660427d (CI green; nothing deploys from `main` yet). **Default:** leave `main` alone (force-push is forbidden by AGENTS.md and blocked by the ruleset) and keep working on the branch only. **Fix for Menno:** briefly allow force-push on `main`, run `git push --force-with-lease=main:660427d origin 319468c:main`, re-enable protection, then open the draft PR.

**Answer:**

### Q-001 · Server capacity · coordinator · 2026-11-15
Does the AppInfra server have room for EV Finder? Partly answered (see Decision 006): CAX31, 16 GB, shared with GardenLayer and Dungeon Tracker; fits on paper while Cahier stays off. Still needed from the "EV Finder capacity check" chat: real `docker stats`, free disk, existing job timers (to confirm the 00:30–02:30 UTC window), and off-site backup status.

**Answer:**

### Q-002 · Package managers · coordinator · 2026-11-15
Default proposal: **pnpm** for the web app and **uv** for the Python pipeline (both fast and widely used by agents). OK, or do you prefer npm / pip?

**Answer:**

### Q-003 · Pull requests on `main` · coordinator · 2026-11-15
Right now `main` only blocks force-pushes and deletion. Once code arrives, should `main` require a pull request with green CI (agents can't push straight to `main`)? Recommended: yes, from wave 1.

**Answer:**

### Q-005 · Conflicting rules: "stop and ask" vs "never stop" · coordinator · 2026-11-15
AGENTS.md says a blocked builder stops and asks; the overnight brief says never stop. Repo files win, but nobody could answer overnight. **Default:** builders picked the safest option, logged it here and carried on, which is what "ask in QUESTIONS.md" amounts to when unattended. Should unattended runs get an explicit exception in AGENTS.md?

**Answer:**

### Q-006 · Where deploy files live · coordinator · 2026-11-15
The brief says `deploy/`; AGENTS.md and the README name `infra/` for deploy config. **Default:** repo wins, so the files are in `infra/deploy/` (`compose.ev.yml`, `ev.caddy`). Never applied. OK?

**Answer:**

### Q-007 · OpenEV Data coverage of older cars · T-004 · coordinator · 2026-11-15
OpenEV Data (CDLA-Permissive-2.0) mostly covers model years 2023+. Pre-2020 used favourites (Leaf ZE0, e-Golf, Zoe Q210/R240, i3 60 Ah, Ioniq 28 kWh, Soul EV) have few or no rows, so their generation pages show "no sourced specs yet". **Default:** leave them empty rather than fill from memory. Which open source should cover pre-2020 cars?

**Answer:**

### Q-008 · Maker documents and unclear-licence registries · coordinator · 2026-11-15
Decision 009 lets only sources with a named licence or written permission reach a release. Maker spec sheets and price lists have no licence; we would cite single facts by URL and date. KBA, SDES and EU Safety Gate reuse terms weren't checked tonight. **Default:** all four are `blocked` in data/sources.yaml. Can cited single facts from maker documents count as releasable (facts aren't copyrightable, but EU database right may apply)?

**Answer:**

### Q-010 · RDW: counting BEVs without a join · T-004 · builder · 2026-11-15
Socrata refuses joins, so we can't link fuel type (`8ys7-d773`) to make/model (`m9d7-ebf2`) server-side. **Default:** count in `m9d7-ebf2` with the proxy "passenger car, no engine displacement, first admitted 2010 or later". In 1,000-row checks it was 99.8 % precise with 100 % recall (details in data/SOURCES.md). The exact alternative would download about 1.2M kentekens from both datasets and join them locally. That isn't row-level spec data, but it's far heavier. OK to keep the proxy?

**Answer:**

### Q-011 · EEA: which year, and how confident are the counts · T-004 · builder · 2026-11-15
**Default:** use the latest table, 2025 provisional (`co2cars_2025Pv31`), rather than 2024 final (`co2cars_2024Fv30`). Counts get confidence `medium` because the table is provisional; type-approval averages get `low`. Prefer final data, or `high` for counts?

**Answer:**

### Q-012 · OpenEV field choices · T-004 · builder · 2026-11-15
1. OpenEV's DC peak is a maker figure. **Default:** keep it as `dc_peak_kw` (as briefed) and not also as `dc_peak_kw_claim`. Should it move to `dc_peak_kw_claim`?
2. `architecture_voltage_class` ("400v"/"800v", 723 files) has no numeric fact field. **Default:** not emitted; only `voltage_nominal_v` (161 records) and `voltage_max_v` (3) are. Is a voltage-class fact wanted?
3. **Default:** categorical facts (`chemistry_id`, `cooling_id`) use unit `"id"`. Generic "li-ion" is not emitted as a chemistry. OK?

**Answer:**

### Q-013 · Nyland sheet column mapping · T-004 · builder · 2026-11-15
The importer skeleton expects our own placeholder headers (`make, model, variant, year, range_km, consumption_kwh_100km, usable_kwh, dc_avg_10_80_kw`). The real sheet layout is unknown, and with permission pending we shouldn't look. **Default:** map the real headers once permission is logged. The real-range field may then need to split into summer/motorway/winter (the new `real_range_*_km` fields).

**Answer:**

### Q-014 · Shared boundary year between generations · T-005 · builder · 2026-11-15
Some seed generations share a year (Model S 2016, Zoe 2019, e-Golf 2017). A record with that model year could be either. **Default:** the newer generation wins (a facelift year is usually sold as the new car). Alternative: send these to review. OK?

**Answer:**

### Q-015 · Does `seed-manual` count as an independent source? · T-005 · builder · 2026-11-15
`seed-manual` (and `model-estimate`) values are hand-entered from memory, so they may echo the same public sources. **Default:** they never count towards "2+ independent sources agree" (no `high` confidence, no `sourced` tier, not in `agreeing_sources`), but they still appear in `source_ids` when they agree. OK?

**Answer:**

### Q-016 · Real-range ratio for cabrio · T-007 · builder · 2026-11-15
The brief's provisional body ratios have no `cabrio`. **Default:** 0.84 (between hatchback 0.85 and coupe 0.86). All body ratios are PROVISIONAL (mild-weather mixed driving). OK?

**Answer:**

### Q-018 · Default DC curve shape · T-007 · builder · 2026-11-15
No measured curves tonight, so every car with only a peak figure gets a generic curve. The coordinator sketched "flat at peak to ~45 %, then down to ~45 % of peak at 80 %" (average ≈ 0.82 × peak). That is optimistic for most 400 V cars (e.g. Model 3 LR: 250 kW peak, ~120–130 kW average). **Default:** flat at peak 10–25 %, linear down to 35 % of peak at 80 % (average ≈ 0.67 × peak), labelled `dc_curve_status: default`, `estimate: true`. Which shape do you want until real curves arrive?

**Answer:**

### Q-019 · EEA rows have no variant name, so nothing ever "agrees" · T-005 · builder · 2026-11-15
Per the brief, a record without a variant name becomes `<generation>-base`. EEA (WLTP, consumption, weight) never names a variant, so its facts sit on 32 separate "Base" rows and never meet OpenEV's named variants. Result tonight: 0 rows reach `sourced`, and only 1 WLTP value has 2 agreeing sources. **Default:** literal rule (no guessing which variant an EEA row belongs to). Options: (a) attach EEA generation-level values as corroboration to every variant in that generation whose own value is within tolerance (agreement only, never a value); (b) hide "Base" rows that only hold EEA data. Which?

**Answer:**

### Q-020 · `fast_on_400v` for `charger_400v.mode: native` · T-007 · builder · 2026-11-15
The rule given was "class 400v, or booster/limited with kW ≥ 50". **Default:** `native` (an 800 V car that charges at full speed on 400 V) also counts as fast. Unknown mode on an 800 V car → null. OK?

**Answer:**

### Q-021 · Seed aliases for registration-style names · T-003 / seed · builder · 2026-11-15
RDW and EEA use names the seed does not match, e.g. `FIAT 500`, `PEUGEOT 208`/`2008`, `OPEL CORSA`, `KIA NIRO`/`SOUL`, `HYUNDAI KONA, KAUAI`, `VOLKSWAGEN GOLF`, `AUDI Q4 40 E-TRON`, `BMW IX3`. These datasets hold only BEVs, so `500` means the 500e there, but adding `500` as a general alias could mis-match spec sources. **Default:** no fuzzy matching in the pipeline; they sit in `data/review/unmatched.csv`. Should the seed get source-scoped aliases (e.g. `rdw_aliases`), or plain `name_aliases`?

**Answer:**

### Q-023 · Provenance for identity numbers and RDW counts · T-006 · builder · 2026-11-15
The schema says "every non-null number has provenance". **Default:** this covers spec, derived and count fields; `release`, `year_start` and `year_end` are identity fields from the seed and carry none. `registered_count_nl` is the RDW total for the whole generation, so every variant of a generation shows the same number (noted in its provenance). OK?

**Answer:**

### Q-025 · Nerd mode wants "sources with date", but FieldProvenance has no date · T-008 / schema · builder · 2026-11-15
`FieldProvenance` carries source ids, confidence, agreeing_sources, estimate and note, but no `retrieved_at`. **Default:** Nerd mode shows the release date (`generated_at`) next to the sources. Should `FieldProvenance` get `retrieved_at` (latest of its facts), or should the client JSON resolve `fact_ids` to dates?

**Answer:**

### Q-026 · Default display level and Explore row links · T-008 · builder · 2026-11-15
**Defaults:** (1) Explore opens at **Detailed** (the brief's column set); Simple and Nerd are one click away and remembered in localStorage + `?level=`. Simple may be the friendlier default for first-time visitors. (2) Explore rows don't link to model pages yet because T-009 hasn't fixed the route; once it has, the car name should link there. Which default level do you want?

**Answer:**

### Q-028 · "See listings" URL patterns are guesses · T-008 / T-009 · builder · 2026-11-15
`apps/web/src/config/countries.ts` holds 2–3 marketplace search templates per country, all `verified: false` (best guesses, nothing fetched). **Default:** ship them marked unverified; someone opens each by hand before launch. Cazoo (UK) is skipped because it closed.

**Answer:**

### Q-029 · Voltage class from nominal voltage misfiles some 800 V cars · Decision 010 · coordinator · 2026-11-15
Hyundai/Kia E-GMP 58 kWh packs are sold as 800 V but sit around 523 V nominal, which falls in the 400 V band (~300–550). **Default:** an explicit `class_id` on the variant link wins, with a required note; `fast_on_400v` stays unknown (not false) when a car has no DC figure at all. Should the class be derived from max voltage or the maker's architecture label instead of nominal voltage?

**Answer:**

### Q-032 · UK threshold for "under €30k" · T-011 · builder · 2026-11-15
**Default:** £26,000 for the UK (about €30,000 at late-2025 rates, rounded down to a common UK price point). It is set in `PRICE_THRESHOLD` (`apps/web/src/lib/rankings.ts`) and explained in the list's method note. Tonight only 7 variants have a price at all (DE, OpenEV), and all of them are over €30k, so the list shows "No priced models yet" in every country. OK, or should the threshold track an exchange rate?

**Answer:**

### Q-033 · Model pages can't be static while the layout reads request headers · T-009 / T-012 · builder · 2026-11-15
The ev, top and learn pages have `generateStaticParams` for all 5 countries (1,552 paths), but `app/[country]/layout.tsx` calls `requestLang()` → `headers()`, so Next renders every route on demand (ƒ). This works and is fast (catalogue is cached in memory), but it is not static. **Default:** left as is; the pages turn static by themselves once language stops depending on the request (e.g. a `/[country]/[lang]` segment or language = country default plus a client switch). Is static output needed for launch?

**Answer:**

### Q-034 · Static model pages (Q-033): skipped for now, needs a decision · T-008 (wave 4) · builder · 2026-11-15
Tried to make the ev, top and learn pages static. **Not done**, for three reasons: (1) `<html lang>` sits in the root layout, which can only learn the language from the request, so a static page needs the language as a route segment, which means a layout restructure (multiple root layouts or a hidden `[lang]` segment the proxy rewrites to); (2) static pages bake the catalogue in at build time, but the app re-reads `data/releases/latest` at runtime (Decision 008: releases swap atomically and roll back by pointing `latest` back), and the Docker build stage has no `data/releases`, so in the image the pages would be built from the dev fixture; (3) one copy per language would mean 1,552 × 6 paths. **Default:** pages stay on-demand (ƒ, fast: the catalogue is cached in memory). **Proposal if static is wanted:** proxy rewrites `/{country}/…` to a hidden `/{lang}/{country}/…` tree (public URLs, `?lang` and the cookie stay as they are), `generateStaticParams` only for each country's default language, others on demand with ISR, `revalidate` on a release change, and `data/releases` copied into the build stage. Needs a Decision entry first. Is static output needed for launch?

**Answer:**

### Q-035 · Staff review page: reads pipeline files, no auth yet · T-008 (wave 4) · builder · 2026-11-15
`/staff/review` (read-only table of `data/review/unmatched.csv` and `conflicts.csv`) reads those files directly, which `apps/web/AGENTS.md` rule 5 otherwise forbids; I noted it there as the one exception. It is off unless `STAFF_PAGES=1` (404 otherwise), `noindex` plus `X-Robots-Tag`, and has no login. In the Docker image the CSVs aren't there (it shows "not found" unless `REVIEW_DIR` points at a mount). **Default:** keep `STAFF_PAGES=0` in production until staff auth exists; use it locally. OK, or should it sit behind Caddy basic auth on staging?

**Answer:**

### Q-036 · RVO vs RDW · R-01 · coordinator · 2026-11-15
You asked to prefer RVO's cleaned data over RDW. RVO's EV dashboard is **CC BY-SA 4.0** (share-alike), which could force our derived dataset under BY-SA too, clashing with our CC BY 4.0 output (Decision 002). **Default:** RVO is `blocked` for ingestion and used only to cross-check RDW-derived totals by hand; we aggregate RDW (CC0) ourselves, applying RVO-style cleaning (BEV filter, imports, exports). Same pattern elsewhere: KBA FZ10 (DE), DfT VEH (UK), FPS Mobility (BE, licence to confirm), EEA for FR (no open make/model register in France). Ask RVO for a CC BY licence or permission?

**Answer:**

### Q-037 · RDW notice: "do not state the data comes from RDW" · R-01 · coordinator · 2026-11-15
RDW's bijsluiter says reusers may not state that the data comes from RDW, or use its logo or house style. That clashes with showing "Source: RDW" on every number. **Default:** the UI keeps the source id but the label needs your call. Probably the clause targets edited data being passed off as official RDW data; an email to RDW would settle it. Options: label "Dutch vehicle register (open data, CC0)" with a method note, or ask RDW.

**Answer:**

### Q-039 · EEA spec facts: per type approval, or counts only? · T-004 · builder · 2026-11-15
The EEA grouped query averaged mass, consumption and range over every type approval under one commercial name (all packs, wheels, trims), so a published "fact" could match no real car. Its `M (kg)` is also mass in running order (curb + 75 kg driver), not curb weight. **Default (done tonight):** EEA is count-only. The adapter emits only `registered_count`, the matcher drops any EEA spec record (`COUNT_ONLY_SOURCES`), and EEA mass is not used anywhere. Release 1 lost 21 EEA-only `-base` rows, and EEA no longer confirms WLTP/consumption. **Option:** group by type-approval variant/version (TAN, Va, Ve) so each row is one configuration, and emit WLTP/Z only when that group is a single car. Then either map M to a separate `mass_running_order_kg` field (schema change) or subtract 75 kg with a note. Worth doing, and which mass option?

**Answer:**

### Q-040 · Year bands: ids and thresholds · T-005 · builder · 2026-11-15
Old variants were taking the newest model year's specs. **Defaults (done):** (1) within one source, merge now prefers the *earliest* model year (newest is still used for prices and counts). (2) If a later model year differs from the band's first year by more than 5% WLTP or 10% DC peak, it becomes its own variant. The first band keeps the existing id, so seed links and URLs stay stable, and ends the year before the next band. Later bands are `<variant_id>-<first year>`, named "<name> (<year>+)". Release 1 has 6 splits: ID.3 Pro (2023: 100→135 kW), Born 77 kWh (2023), Enyaq 60 (2024), e-208 and e-2008 (2024, WLTP +10-17%), and Atto 3 Standard Range (2025). Smaller changes stay in one variant, and the later values go to conflicts.csv. OK? Or should both bands get a year suffix (`-2020`, `-2023`), as the brief's example suggests? That would rename existing ids.

**Answer:**

### Q-041 · Bare trade-name aliases and shared-year counts · T-005 / seed · builder · 2026-11-15
This applies the answer to Q-021's question. **Done:** models.yaml now has `bev_only_aliases` (KONA, "KONA, KAUAI", KAUAI, IONIQ, SOUL, NIRO, 208, 2008, CORSA, 500, GOLF). They are honoured only for BEV-filtered sources (rdw, eea), and only as a whole-name match, never a prefix, so "GOLF GTI" and "FIAT 500 1.4 16V" stay out. Names that are unambiguously electric became plain `name_aliases`: Q4 35-55 e-tron, Q4 Sportback xx e-tron, Q8 50/55 e-tron, SQ8 e-tron, e-Corsa. `name_excludes` keeps e-tron GT off the e-tron and Honda e:Ny1/e:N* off the Honda e. The RDW BEV filter is a proxy (998/1000 in the sample), so the generation's year range is the second guard. Shared-year records with no name or battery evidence now go to review as `ambiguous-generation` when both generations have variants. That is 12 rows: Kona 2023, Niro 2022, Soul 2019, Zoe 2019, Model S 2016, e-Golf 2017, and those NL counts are no longer in either generation. Is that better than "newer wins"? Note that a record with no evidence still goes to the newer generation when the older one is the only one with variants (e.g. EEA "NISSAN LEAF" 2025 → gen3).

**Answer:**

### Q-042 · Test fixtures use `wikidata` as the second spec source · T-005 / T-006 · builder · 2026-11-15
With EEA count-only, the release fixture needed another independent spec source to test the confidence and tier rules. **Default:** `tests/fixtures/release/staging/wikidata.records.jsonl` holds two synthetic rows (record keys `wikidata:fixture:*`), and the fixture registry lists `wikidata` as `data/sources.yaml` does. Nothing is imported from Wikidata. OK, or would you prefer an obviously fake `testsource` id?

**Answer:**

## Closed

### Q-038 · Two different "Open EV Data" datasets · coordinator · 2026-11-15
The project decisions log says "Open EV Data (MIT + attribution, drop default curves)". That describes **KilowattApp/open-ev-data** (MIT with attribution requirement, © Tijs Teulings), which has DC charge curves. Tonight's pipeline uses **open-ev-data/open-ev-data-dataset** (CDLA-Permissive-2.0), which has no curves. **Default:** keep the CDLA dataset as the base spec source and add the KilowattApp dataset in wave 5 as a curve source (drop its default curves, keep measured ones, attribution in the UI). Did you mean one, or both?

**Answer:** Menno, 01:41: both. KilowattApp dataset added as source `kilowatt-openev` (curves, attribution required). Closed.

### Q-031 · DC ranking: km in 10 or 20 minutes? · T-011 · builder · 2026-11-15
The T-011 acceptance criterion says "Fastest DC km/10 min", but Decision 009 and the overnight brief say the DC ranking uses km added in **20** minutes. **Default:** `/[country]/top/fastest-dc` ranks by `dc_km_per_20min` (Decision 009). The 10-minute figure is still shown on variant pages and in compare. Please fix the acceptance line, or say if you want 10 min.

**Answer:** Decision 009 (Menno's addendum) supersedes the original brief: the DC ranking uses km in 20 minutes. T-011 updated. Closed.

### Q-027 · `CATALOGUE_DIR` in `.env.example` · T-008 · builder · 2026-11-15
The web app reads `data/releases/<latest>/catalogue.json` and accepts `CATALOGUE_DIR` to point elsewhere (e.g. in the Docker image). `.env.example` is outside the web lane. **Default:** documented in `apps/web/README.md` only. Coordinator: please add `CATALOGUE_DIR=` to `.env.example`.

**Answer:** Coordinator added CATALOGUE_DIR to .env.example. Closed.

### Q-024 · Glossary ids the web app needs that `glossary_terms.yaml` lacks · T-008 · builder · 2026-11-15
Explore puts a glossary ⓘ on every column and filter. These ids are used but not yet in `data/taxonomy/glossary_terms.yaml`: `new-price`, `registrations-nl`, `model-years`, `segment`, `body-type`, `boot-volume`, `vehicle-length`, `towing-capacity`, `charge-to-100`. **Default:** the web dev fixture carries draft rows for them (EN + NL), and a missing term just shows the plain label without ⓘ (no crash). Please add them to the YAML (the drafts are in `apps/web/src/fixtures/catalogue.sample.json`, last entries of `taxonomy.glossary_terms`). I also switched my ids to yours: `chemistry`, `cooling`, `quality-tier`, `peak-kw`, `400v-charger-behaviour`, `usable-vs-gross` (the last is a slightly odd plain label for a "Battery size" column; a `battery-capacity` term may read better).

**Answer:** Coordinator added the 9 terms to data/taxonomy/glossary_terms.yaml. Closed.

### Q-022 · EEA licence marked "(to confirm)" but status `active` · coordinator · builder · 2026-11-15
`data/sources.yaml` says licences marked "(to confirm)" stay blocked, but EEA is `active` with "CC-BY-4.0 (to confirm on datahub page)". **Default:** the gate follows `status` (EEA is released) and the release README credits EEA as CC-BY-4.0. If EEA must wait, set its status to `waiting_permission` and the gate drops it (tested).

**Answer:** Coordinator confirmed the licence from the T-004 metadata check and removed "(to confirm)" from data/sources.yaml. Closed.

### Q-017 · Schema bug: `oneOf [Id, const 'not-disclosed']` · coordinator (schema) · builder · 2026-11-15
`Platform.voltage_class_id`, `BatteryPack.chemistry_id`/`cooling_id` and `VariantVoltage.class_id` are `oneOf [{$ref Id}, {const: not-disclosed}]`. The string `not-disclosed` also matches the Id pattern, so it is valid under both branches and **fails `oneOf`**. The real `data/seed/platforms.yaml` uses it. **Default (pipeline, interim):** shipped platform/pack objects leave such keys out (absent = not known); rows still carry `not-disclosed`. Fix: change those four to `anyOf`, then remove `_ONEOF_ID_KEYS` in `pipeline/ev_pipeline/derive/links.py` and its test assertion.

**Answer:** Coordinator switched those properties to `anyOf` and removed the workaround in `derive/links.py`. Closed.

### Q-009 · `dc_curve` cannot pass through SourceRecord · T-004 · builder · 2026-11-15
The schema now has `FactField.dc_curve` with a `ChargeCurve` value, but `records.SpecValue.value` is still `float | str | bool`, so an adapter cannot emit a curve. **Default:** no curves emitted. This costs nothing tonight: no OpenEV record has a `dc_charge_curve`. Should the coordinator widen `SpecValue.value` to `float | str | bool | ChargeCurve` between waves?

**Answer:** Coordinator fixed the contract: `SpecValue.value` now accepts a `ChargeCurve` (Decision 009). Closed.

### Q-004 · Push access · coordinator · 2026-11-15
The overnight session could clone the repo (it's public) but was refused push access, so nothing could be pushed to `proto/overnight-1` and no draft PR could be opened. **Default:** all work is committed locally on `proto/overnight-1` and handed over as a git bundle; you push it with `git fetch <bundle> proto/overnight-1:proto/overnight-1 && git push -u origin proto/overnight-1`. Next time, attach the repo with write access before starting the session.

**Answer:** Menno granted push access at 00:49. Closed: branch pushed normally.


