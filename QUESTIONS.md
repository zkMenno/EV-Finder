# Questions for Menno

Agents add questions here when they're blocked. Menno answers inline under **Answer:**. Once answered, the coordinator moves the outcome into DECISIONS.md or the task file and marks the question closed.

Format: `Q-NNN` · task id (if any) · who asked · date.

---

## Open

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

### Q-036 · RVO vs RDW · R-02 · coordinator · 2026-11-15
You asked to prefer RVO's cleaned data over RDW. RVO's EV dashboard is **CC BY-SA 4.0** (share-alike), which could force our derived dataset under BY-SA too, clashing with our CC BY 4.0 output (Decision 002). **Default:** RVO is `blocked` for ingestion and used only to cross-check RDW-derived totals by hand; we aggregate RDW (CC0) ourselves, applying RVO-style cleaning (BEV filter, imports, exports). Same pattern elsewhere: KBA FZ10 (DE), DfT VEH (UK), FPS Mobility (BE, licence to confirm), EEA for FR (no open make/model register in France). Ask RVO for a CC BY licence or permission?

**Answer:**

### Q-037 · RDW notice: "do not state the data comes from RDW" · R-02 · coordinator · 2026-11-15
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

### Q-043 · ADEME WLTP: best case only · sources (ademe) · builder · 2026-11-15
ADEME gives WLTP consumption and range as Min/Max per version (the low and high test vehicles of one homologation: options, wheels). **Default:** we emit only the best case (lowest kWh/100km, highest km), the figure makers quote, and never average. The worst case is dropped because the schema has no field for it. Add `wltp_range_km_worst` / a min–max pair to the schema, or keep best only?

**Answer:**

### Q-044 · What mass is `weight_kg`? · schema / sources (ademe) · builder · 2026-11-15
The schema doesn't say whether `weight_kg` includes the 75 kg driver. ADEME "Poids à vide" = "Masse en ordre de marche" − 75 kg on every electric row, so it excludes the driver; EEA type-approval mass includes it. **Default:** ADEME emits "Poids à vide" (no driver). Please fix the definition (EU kerb mass with driver, or without) so adapters can convert.

**Answer:**

### Q-045 · ADEME power not emitted · sources (ademe) · builder · 2026-11-15
For BEVs ADEME fills only "Puissance nominale électrique", the rated 30-minute power (57 kW on a Corsa-e whose peak is 100 kW); "Puissance maximale" is empty. **Default:** no `power_kw` from ADEME. Peak power sometimes appears in the description ("(204ch)"), but parsing it is fragile. OK to leave it out?

**Answer:**

### Q-046 · KBA period and DfT year semantics · sources (kba-fz10, dft-veh) · builder · 2026-11-15
**KBA:** the brief asked for the latest month plus the same month a year earlier. **Default:** we take the latest file's year-to-date (Jan–Oct 2026) plus last year's **December** file (full year 2025), so every year is complete or YTD and years never overlap. **DfT:** VEH0120 is fleet stock at quarter end (2026 Q2), not registrations in a year, so `year` is empty and the count sits on the model. For counts per year of first registration we would need VEH0124 (stock × year of first use) or VEH0160 (first registrations per quarter). OK as a first cut?

**Answer:**

### Q-047 · KilowattApp curves: provenance and likely ev-database.org origin · sources (kilowatt-openev) · builder · 2026-11-15
Upstream docs do not say how curves were obtained (no "measured" anywhere); its own tool generates template curves (`lib/vehicle_creator/charging_details.rb`). 22 records carry `url: https://ev-database.org/...` and `_manually_fixed_fields`, and the suggest form proposes ev-database.org as a source, so some values were probably taken from ev-database.org (no open licence). **Default:** import under the repo's MIT-with-attribution licence as a low-priority fallback; all curves `estimated`, confidence low; specs medium. Is that acceptable given rule 2 ("derived, not copied"), or should `kilowatt-openev` curves stay out of public releases until checked?

**Answer:**

### Q-048 · KilowattApp data-quality rules (judgement calls) · sources (kilowatt-openev) · builder · 2026-11-15
**Defaults applied** (all counted in the run log): (1) only `vehicle_type: car` (32 motorbikes, 7 microcars incl. Twizy/Microlino skipped); (2) DC max_power exactly equal to usable kWh is treated as a 1C placeholder: no `dc_peak_kw`, no curve (567 cars, e.g. Model 3 2023 "57.5 kW", Leaf 2022 "39 kW"); (3) unflagged curves with one of two exact generic shapes (0/50/80/100 % at 1.0/1.0/0.6/0.3 or 1.0/1.0/0.5/0.2 of peak) are dropped like default curves (292); (4) AC > 43 kW dropped (10), consumption outside 10–40 kWh/100km dropped (2, e.g. DS 3 Crossback 81.1). (5) Cycle of `average_consumption` is undocumented (kWh/100km; maybe WLTP, maybe an ev-database-style real figure); emitted as `consumption_kwh_100km`, but `field_sources.yaml` does not list kilowatt-openev for that field anyway. OK?

**Answer:**

### Q-049 · "No DC data" rule and Explore's Tab stops · T-008 / T-009 / T-010 review · builder · 2026-11-15
**Done (defaults):** (1) `hasDcData(row)` (`apps/web/src/lib/dc.ts`) is true when `dc_peak_kw`, `dc_avg_10_80_kw` or `dc_minutes_10_80` is a positive number. Without it, `charger_400v_mode`, `charger_400v_kw` and `fast_on_400v` read as missing everywhere (Explore, variant/generation pages, spec diff, compare, the "fast on 400 V" filter) and show "—" with screen-reader text "no DC charging data". The spec diff/compare drop the 400 V row when no car in it has DC data. (2) In the Explore **table**, numbers and the generation link are no longer Tab stops (they still open on hover/tap): a row is 3 stops (name link, heart, compare), 4 at Nerd level (+ one "Sources" button listing every number's source and confidence). Keyboard users reach a number's popover on the variant page; cards are unchanged. OK? Or should a car with only a derived `dc_km_per_20min` also count as "has DC data"?

**Answer:**

### Q-050 · Credits wording comes partly from `terms` text · About page · builder · 2026-11-15
The About page (`/[country]/about`) builds its credits from the release's `sources` array. When a release entry has no `attribution`, it falls back to `data/sources.yaml`, which has no `attribution:` field, so `apps/web/scripts/sources.mjs` takes the quoted text in `terms` ("attribution '…' required", "visible attribution to '…'", or a `terms` that starts with a quote). That gives the KilowattApp, KBA FZ10 and DfT lines. EEA ("© European Union, EEA, CC BY 4.0"), ADEME/SDES (Licence Ouverte), OGL and KilowattApp also have fixed fallback wording in `apps/web/src/lib/credits.ts`, added when the release text doesn't already contain it. RDW uses the interim wording "Dutch vehicle register (RDW open data, CC0)" until **Q-037** is answered (it overrides the release's "Bron: RDW Open Data"). **Suggestion for the coordinator:** add an explicit `attribution:` to each entry in `data/sources.yaml` (the extractor prefers it), and have the pipeline copy it into every release's `sources`. Is the RDW wording OK for now?

**Answer:**

### Q-051 · KBA model series read as BEV models · match (kba-fz10) / seed · builder · 2026-11-15
KBA FZ10 rows are Marke × Modellreihe, shared with ICE cars; only the BEV column is used. **Defaults** (source-scoped aliases in `data/seed/models.yaml`, valid for `kba-fz10` only, each with a note in the release provenance): `BMW 4ER` → i4, `AUDI Q4` → Q4 e-tron, `AUDI Q8` → Q8 e-tron, `MERCEDES GLA` → EQA, `SEAT BORN` → Cupra Born, `VW ID.4, ID.5` → ID.4 (the seed has no ID.5; the note says the count includes it). Cross-check against EEA DE 2025: i4 11,680 vs 11,690, Q4 11,776 vs 11,752, EQA 9,687 vs 9,682, Born 18,847 vs 18,811, so these readings hold. **`MINI MINI` is not mapped:** KBA has one series for every MINI, and its 2025 BEV count (15,495) is 2.4× EEA's Cooper SE/E count (6,570), so it includes the Aceman / Countryman E; it goes to unmatched.csv. A KBA year that two generations share without evidence (e.g. Model 3 2024) is counted at model level, with a note; a year outside every generation (KBA 2025 `VW GOLF` BEV: the e-Golf ended in 2020) goes to review. OK, or should MINI map anyway with a "may include" note?

**Answer:**

### Q-052 · ADEME and KilowattApp only add to existing variants · match / merge · builder · 2026-11-15
Their names never equal OpenEV/seed names (ADEME "e-208 (57Kw)", KilowattApp "LR"), so letting them create variants would duplicate rows. **Default:** "attach-only": a record joins one existing variant of its generation (same name, else the generation's only variant, else the single best on battery kWh / power kW / WLTP / shared name words; ties and no-evidence go to unmatched.csv with the reason). ADEME has no year, so multi-generation models (Model 3, Zoe, Niro, Soul, 500e) need battery evidence to pick a generation, else review. Result tonight: 24 ADEME records attached → FR prices on **7** variants (EV6 ×3, EQA ×2, 500e 42 kWh, Leaf ZE1); 357 KilowattApp records attached → **51** variants with a KilowattApp curve. The ADEME "(57Kw)"-style figure is nominal power, so it is (rightly) never matched to peak power. ADEME prices are current list prices but sit on variants whose specs come from the earliest model year (e.g. EQA 250 vs ADEME's 250+ facelift; the spec differences are in conflicts.csv). OK, or should ADEME create its own (FR-only) rows?

**Answer:**

### Q-053 · `registrations`: levels, periods and provenance shape · release · builder · 2026-11-15
**Defaults:** one `RegistrationCount` per source × country × period, never summed across sources, periods or kinds. RDW: `fleet`, generation level, period = RDW fetch date (snapshot), same number as `registered_count_nl`. DfT: `fleet`, period `2026-Q2`, matched on the DfT "Model" column (GenModel "HYUNDAI IONIQ" also holds Ioniq 5/6/9 and "AUDI E-TRON" the e-tron GT); no year, so a model's count repeats on every generation (`level: model`; `generation` for one-generation models). KBA: `new_registrations`, period `2025-01..12` / `2026-01..10`. EEA: `new_registrations`, period `2025`. Provenance: one entry per country, key `registrations.<CC>`, listing every source and fact id, with a note per count. This roughly doubles `catalogue.json` (1.9 → 3.1 MB raw, 92 → 143 KB gzip; budget 300 KB). Also: KilowattApp is treated as a BEV-only source (it holds only electric cars), so bare names like "Ioniq" match. OK, or prefer per-source provenance keys (`registrations.DE.kba-fz10`) or dropping fact ids from count provenance to save size?

**Answer:**

### Q-054 · Schema judgement calls for bidi, charging stats and Trip fit · T-018 / T-023 / T-030 · schema delegate (WS0) · 2026-11-15
No answer needed from Menno unless you disagree; the coordinator may log these in DECISIONS. **Defaults taken:** (1) Taxonomy ids use hyphens (`ac-onboard`, `iso15118-20`, `not-disclosed`), not the spec's underscores, because every id must match the `Id` pattern (Decision 010). (2) New entities use a new `CountryCode` (any 2-letter code, UK not GB) instead of the 5-country `Country` list, so US/AU rows need no schema change; charging stats also accept `EU27`, `EUROPE`, `WORLD`. (3) No separate `usable_kwh` fact: `battery_kwh_net` already is usable capacity. New fact names carry units like the existing ones (`frontal_area_m2`, `kerb_mass_kg`, `wheel_size_in` = rim size code). (4) Allowed values for `iso15118_20_support` / `heat_pump` facts are checked at release time, not in the schema, because a schema rule on `Fact` broke the generated TypeScript type. (5) Prices of bidirectional boxes are stored in euros as a min–max band, with the original price in a note.

**Answer:**

### Q-055 · Trip fit quick check runs on a hand-set fixture matrix · T-036 · builder · 2026-11-15
The quick check (behind `TRIP_FIT=1`, off by default) needs consumption multipliers per body × road band × temperature band. T-033's matrix isn't in the release yet, so `apps/web/src/fixtures/consumption-matrix.sample.json` holds hand-set values shaped after the spec's research table (≈ 0.85× WLTP in summer town driving up to ≈ 1.8× on a cold motorway), plus rough towing (×1.6) and roof-box (×1.15) factors and 1.5–2.5 kWh warm-up per cold start. Town temperatures in `towns.sample.json` are typed from memory, not sourced. Both files say PROVISIONAL, every result shows "estimate · fixture matrix", and nothing is published. Other defaults: used = `year_end` before this year → 90% battery health ("keep 8+ years" → 85%); daily start 80% (100% where `charge_100_daily`); 10% arrival buffer; "a stop, about N min" is not shown yet (no winter DC data), only "short by about N km"; car role, long trips and charging place are stored but change nothing until the Fit score (Core 2), and the card says so. **Default:** keep the flag off in production until T-033 replaces the matrix and the towns come from GeoNames + climate normals. OK?

**Answer:**

### Q-056 · UTM tag on official (government) charging links · T-026 · builder · 2026-11-15
T-024 put `charging_links` in `config/countries/<cc>.yaml` (job ids from `CountryChargingLink.job`); the web app reads, validates (`apps/web/scripts/charging-links.mjs`) and renders them. The spec's Link rules say "plain URLs plus our UTM tag" with no exception for government sites, so every link, the Bundesnetzagentur map included, gets `utm_source=evfinder&utm_medium=referral&utm_campaign=charging_links` unless its row sets `utm: false`. `official: true` drops `nofollow` (third parties keep `nofollow noopener`). Model pages drop ABRP from the block and show a plain ABRP line instead (no car pre-selection until T-029). **Default:** as described. Should official sites go without UTM (set `utm: false` on those rows)?

**Answer:**

### Q-057 · Charging links and charging/bidi taxonomies: judgement calls · T-024 / T-019 · builder · 2026-11-15
No answer needed unless you disagree. **Defaults taken:** (1) **Links per country follow the spec's per-country table**, not the generic five-slot order, so none gets Open Charge Map and the counts are NL 4, DE 4, FR 4, BE 4, UK 3 (UK has no Chargeprice in that table). Add Open Charge Map as a fifth link? (2) **Germany:** the spec's URL for the Bundesnetzagentur Ladesäulenkarte is the E-Mobilität start page, not the map itself; kept as given (no invented URLs). A direct map URL needs a spec update first. (3) **`verified: false` is not written** on links: the web loader (`apps/web/scripts/charging-links.mjs`) rejects unknown keys, so "not opened by hand" is a comment in each country file. (4) **Label shape differs:** schema `CountryChargingLink.label` is a LocalizedText, the web loader wants a plain string and also needs `tool`; the YAML follows the web loader and `validate_taxonomy.py` maps it to the schema shape when it checks. Coordinator/WS2: align one or the other. (5) **`bidi_equipment` is held back from releases** (0 of 12 rows ship) because its sources are maker pages and press that are not releasable in `data/sources.yaml` (maker documents are blocked, Q-008). A row ships automatically once all its `source_ids` are active there. (6) Box prices in pounds or dollars (Wallbox Quasar 2 ~£6,100, dcbel Ara US$9,999) are **not converted**: `price_band` stays `not-disclosed` and the original price sits in `notes`, since no rate is sourced. (7) Our five power bands have **no DC under 50 kW band**, so German "fast (>22 kW)" maps only to our DC bands; add a `dc-under-50` band? (8) Cited sources live in a new `data/taxonomy/taxonomy_sources.yaml` until WS1 moves them into `data/sources.yaml` with a checked licence.

**Answer:**

### Q-058 · Fetch allowlist: Nyland host and proxies · addendum 5 item 6 (A-02) · builder · 2026-11-15
No answer needed unless you disagree. Every HTTP fetcher now goes through `pipeline/ev_pipeline/net.py`, which only talks to the hosts listed under `hosts:` in `data/sources.yaml`. **Defaults taken:** (1) The Nyland sheet URL lives only in your env, so I guessed its hosts: `docs.google.com` + `*.googleusercontent.com` (a Google Sheets CSV export). If it lives elsewhere, the fetch fails with "FetchBlocked" and the fix is adding that host to the `nyland` entry. (2) The fetcher ignores `HTTPS_PROXY`/`HTTP_PROXY` (a proxy would defeat the private-address check). If the AppInfra server ever needs an egress proxy, WS4 should say so and it gets added on purpose. (3) Size caps: 32 MB per response by default, 256 MB for DfT (its file is about 65 MB today).

**Answer:**

### Q-059 · Release QA and open data bundle: judgement calls · R-05 §1 / T-035 / Decision 016 · pipeline builder · 2026-11-15
No answer needed unless you disagree. **Defaults taken:** (1) **"Top-40 used models"** has no list yet, so QA ranks the seed models in the release by RDW NL fleet (one count per generation), then the DfT UK fleet. This is a stand-in for "most bought used". A curated list would replace it. (2) **The brand in the open bundle** (LICENSE, README "how to cite", ATTRIBUTION) comes from the `EV_BRAND_NAME` env var, with the neutral fallback "the EV Finder project". Release 1 was built without it. Suggestion: a shared `config/brand.yaml` that the pipeline and the web app both read. (3) **The back-test in qa.json leaves out tests from sources that fail the licence gate**, because qa.json is published and the 10 worst list shows measured km. NAF, ADAC and Nyland tests can only be run locally (`python -m ev_pipeline.backtest file.jsonl`) until permission is logged. (4) **Licence check needed:** KilowattApp's licence is "MIT with attribution". The open bundle carries its copyright and permission notice in ATTRIBUTION.md, and that notice is part of LICENSE. Please confirm that it's OK to wrap MIT-licensed values in a CC BY 4.0 bundle this way. CDLA-Permissive-2.0 (OpenEV) is met by linking the licence text. (5) **RDW credit** in ATTRIBUTION.md uses the same interim wording as the web app until Q-037 is answered. (6) **Percentile outliers** use this release's own data when there is no previous release, and skip segments with fewer than 30 values. Measured against its own data, P1–P99 always flags about 2% of values, so release 1's 30 percentile flags are for review only.

**Answer:**

### Q-060 · Typical loan rates for the calculator · T-043 / Decision 017 · coordinator (schema delegate) · 2026-11-15
No answer needed unless you disagree. `data/taxonomy/finance_profiles.yaml` has rates from central-bank statistics only. **Defaults taken:** (1) **DE 8.91 %, FR 6.11 %, BE 6.24 %** (Sept 2026) are the ECB's average APRC on new consumer loans (all purposes, not only cars, not split into new and used). DE and FR Sept figures are still provisional. **UK 7.11 %** (Oct 2026) is the Bank of England's quoted APR on a £10,000 personal loan, not dealer PCP/HP. (2) **NL is empty.** The ECB/DNB series for Dutch consumer credit stopped (2010 / 2017) and no current DNB table turned up, so the calculator asks the user for a rate. Alternatives: use the euro area figure (8.46 % provisional, Sept 2026) labelled "euro area average", or a non-central-bank source. (3) **Term and deposit are empty everywhere**, because no source states them. The calculator uses the spec default (48 months, no deposit) and labels it. (4) **Licences:** ESCB and Bank of England reuse terms are marked "(to confirm)". (5) **Warning text:** NL "Let op! Geld lenen kost geld" (AFM, art. 2:2 Nrgfo), EN "Caution! Borrowing money costs money" (CCD2 Art. 8(1)). DE/FR/ES/IT fall back to EN until each country's CCD2 wording is checked. The AFM warning symbol is not used until its licence is checked.

**Answer:**

## Closed

### Q-030 · Overnight work landed on `main` by mistake · coordinator · 2026-11-15
From about 01:05 the coordinator's push clone was on `main`, so syncs pushed `main` as well as `proto/overnight-1`. Both now point to 660427d (CI green; nothing deploys from `main` yet). **Default:** leave `main` alone (force-push is forbidden by AGENTS.md and blocked by the ruleset) and keep working on the branch only. **Fix for Menno:** briefly allow force-push on `main`, run `git push --force-with-lease=main:660427d origin 319468c:main`, re-enable protection, then open the draft PR.

**Update 02:00:** WS0 has since pushed four commits to `main` on top of 660427d (spec mirror, workstreams, Decisions 011–014). Resetting `main` would now delete their work, so **don't force-push**. New default: keep `main` as is, merge `main` into `proto/overnight-1` (done, clean), and open the draft PR for the remaining overnight work.

**Answer:** WS0 (addendum 4): no force-push needed; `main` moved on, so the branch merges normally through PR #1. Closed.

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


