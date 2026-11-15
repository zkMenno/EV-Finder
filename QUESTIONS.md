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

**Overnight result:** option (a) is built and **off by default** (`EV_EEA_CORROBORATION=1` turns it on). EEA's range/consumption averages now ride along as `kind: corroboration` records (never mass); the matcher keeps one per generation and field (the country with the most registrations), and merge counts EEA as +1 agreeing source only when that average is within the field's tolerance (WLTP 2 %, consumption 3 %) of a variant's merged value and the variant was on sale that year. It never sets or moves a value, never raises confidence, never makes a conflict. Measured on tonight's data: **sourced rows 2 → 6** (+4: Cupra Born base, Model S Palladium LR, Model Y Juniper LR RWD, ID.3 Pro 2023); 13 rows get a 2nd WLTP or consumption source; 0 values change. Why still off: all 13 sit in generations with several variants, so the agreement is with a blend (e.g. EV6 58 kWh and 77 kWh both "agree" on consumption with one average). A stricter rule (single-variant generations only) would add 0 rows. Turn it on if a blended average is good enough as a 2nd source; otherwise option (b) or Q-039's per-type-approval rows.

**Answer:**

### Q-020 · `fast_on_400v` for `charger_400v.mode: native` · T-007 · builder · 2026-11-15
The rule given was "class 400v, or booster/limited with kW ≥ 50". **Default:** `native` (an 800 V car that charges at full speed on 400 V) also counts as fast. Unknown mode on an 800 V car → null. OK?

**Answer:**

### Q-021 · Seed aliases for registration-style names · T-003 / seed · builder · 2026-11-15
RDW and EEA use names the seed does not match, e.g. `FIAT 500`, `PEUGEOT 208`/`2008`, `OPEL CORSA`, `KIA NIRO`/`SOUL`, `HYUNDAI KONA, KAUAI`, `VOLKSWAGEN GOLF`, `AUDI Q4 40 E-TRON`, `BMW IX3`. These datasets hold only BEVs, so `500` means the 500e there, but adding `500` as a general alias could mis-match spec sources. **Default:** no fuzzy matching in the pipeline; they sit in `data/review/unmatched.csv`. Should the seed get source-scoped aliases (e.g. `rdw_aliases`), or plain `name_aliases`?

**Overnight result:** source-scoped aliases are built and **on by default** (`EV_SCOPED_ALIASES=0` turns them off). Each model can carry `aliases_by_source: {rdw: [...], eea: [...], kba-fz10: [...], dft-veh: [...]}` (bare name = whole-name match, `{match: prefix}` for leading words, optional note), which replaces `bev_only_aliases` + `source_aliases` for that model (both migrated; a test checks nothing was lost), plus `make_aliases_by_source` on makes. Flag off vs on, same staging: matched records 2,541 → 2,621; unmatched RDW 2,225 → 2,208, EEA 1,417 → 1,368, OpenEV 990 → 975; registrations placed RDW +173 (smart fortwo coupe/cabrio ED, MG ROEWE ZS EV, RDW typos), EEA +62,301 (make `VOLKSWAGEN, VW` = ID.3/ID.4 in DE/BE, `AUDI AG`, FR `CLASSE EQA`); OpenEV +15 MG4 records (make `MG Motor`). KBA, DfT, ADEME unchanged. No record moved to a different model or generation. Side effect: the MG4 OpenEV records add 4 rows whose names don't line up with the seed's (see Q-062), which moves 1 KilowattApp MG4 record to review (tie) and 1 to the new "Standard Range" row. Plain `name_aliases` were not used for any of these.

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


### Q-035 · Staff review page: reads pipeline files, no auth yet · T-008 (wave 4) · builder · 2026-11-15
`/staff/review` (read-only table of `data/review/unmatched.csv` and `conflicts.csv`) reads those files directly, which `apps/web/AGENTS.md` rule 5 otherwise forbids; I noted it there as the one exception. It is off unless `STAFF_PAGES=1` (404 otherwise), `noindex` plus `X-Robots-Tag`, and has no login. In the Docker image the CSVs aren't there (it shows "not found" unless `REVIEW_DIR` points at a mount). **Default:** keep `STAFF_PAGES=0` in production until staff auth exists; use it locally. OK, or should it sit behind Caddy basic auth on staging?

**Update (overnight, A-02):** the app now has a basic guard: with `STAFF_PAGES=1`, `/staff/*` also needs HTTP Basic credentials from `STAFF_BASIC_AUTH` (`user:pass`, env only; constant-time compare in `src/proxy.ts` / `src/lib/staff-auth.ts`). Without `STAFF_BASIC_AUTH` it answers 401 (fails closed). Still noindex, `no-store`, never linked. Caddy `basic_auth` on top stays a WS4 option.

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

### Q-061 · /learn drafts: spec figures that sources contradict, and missing glossary ids · addendum 5 item 4 (T-021 / T-027 / T-039) · content builder · 2026-11-15
No answer needed unless you disagree. EN + NL drafts are in `content/learn/` (`review: needed`). While checking sources I found spec text that the sources don't support. **Defaults taken:** the drafts follow the source, not the spec. (1) **NIO semi-solid:** the Battery & voltage guide says "NIO already sells a 150 kWh semi-solid pack". electrive (17 Nov 2025) says NIO stopped making it after a few hundred units and it won't come to Europe. The draft says "offered from 2023, stopped in 2025". Please fix the spec tab and `chemistries.yaml` if needed. (2) **El Prix winter 2025:** trip-fit §2 says "most cars 15–30 % below WLTP". The cited InsideEVs article says 18 of 24 cars were 11–23 % short. The draft uses 11–23 %. (3) **VW bidirectional:** VW's own page now names a different approved DC box from the ones in R-01, and says Software 6 works with every battery size. The ChargeLine BiDi price in R-01 (€2,990 / €1,990) isn't in electrive's 23 Jun 2026 article ("price not disclosed"), and Elli said on 3 Nov 2026 that it is leaving the hardware business. The drafts don't name a box or a price. R-01 should be refreshed before T-019 seeds equipment rows. (4) **Missing glossary ids:** the drafts mark only ids that already exist. These terms appear in the text without an ⓘ and should be added to `glossary_terms.yaml` (EN + NL): `v2l`, `v2h`, `v2g`, `bidirectional-charging`, `iso15118-20`, `type-2`, `ccs2`, `chademo`, `afir`, `ad-hoc-payment`, `roaming`, `idle-fee`. T-021 already lists most of the bidi ones. Once they exist, WS3 adds the `[[id|…]]` marks.

**Answer:**

### Q-062 · MG4: OpenEV trim names don't line up with the seed variants · match / seed (Q-021 follow-up) · builder · 2026-11-15
No answer needed unless you disagree. With the `MG Motor` make alias, OpenEV's MG4 records match now, but OpenEV names its trims "Standard", "Standard Range", "Standard Long Range", "Trophy", "XPower", while the seed has "Standard Range (51 kWh)", "Long Range (64 kWh)", "Extended Range (77 kWh)", "XPower". So release 1 has 4 extra MG4 rows (`mg-mg4-gen1-standard-2023`, `-standard-range`, `-standard-long-range`, `-trophy`) next to the seed rows; 49 kWh "Standard"/"Standard Range" and 61 kWh "Standard Long Range"/"Trophy" are probably the same packs as the seed's 51/64 kWh rows. **Default:** left as is (no fuzzy merging). Fix is a seed change, not code: rename or alias the seed variants to OpenEV's names (WS3), or add variant-level aliases to the schema. Which?

**Answer:**

### Q-063 · Glossary sweep: id and label choices · addendum 5 backlog 1 · content/data builder · 2026-11-15
No answer needed unless you disagree. The glossary now has 88 terms: 39 were added, EN complete, NL label and short. All Q-061 ids exist, so part (4) of Q-061 is done. The full map is in `data/review/glossary-sweep.md`. **Defaults taken:** (1) The glossary id is `type-2`, as Q-061 asked, but the connector row is `type2`. Both are kept, and no taxonomy id was renamed. All other plug and two-way rows (`ccs2`, `chademo`, `v2l`, `v2h`, `v2g`, `v2b`, `iso15118-20`) use the same id in both places. (2) The "Weight" field became the term `kerb-weight`, with the plain label "Weight". It doesn't say whether a driver is included, because sources define weight differently and we don't record which definition each one uses. (3) A new `battery-capacity` term is offered for the "Battery" column (the label problem from Q-024). Switching to it is up to the web builder. (4) The validator now fails if a glossary id equals a `/learn` article slug, or if a `[[id]]` marker in `content/learn` doesn't resolve.

**Answer:**

### Q-064 · Variant clue and look-alike group schema: judgement calls · T-044 / Decision 019 · schema delegate (WS0) · 2026-11-15
No answer needed unless you disagree; the coordinator may log these in DECISIONS. **Defaults taken:** (1) The task's `clue_type` field is named `clue_type_id`, like every other taxonomy reference (`mode_id`, `metric_id`, `status_id`). (2) The task's `source` is `sources[]` (at least one `ClueSourceRef`: catalogue source id + exact page URL + locator + date), so a clue can cite two sources, as the product rules ask. (3) `market` is a `CountryCode` or the word `global`. (4) A clue has either `value` (number, text, code, yes/no) or `range` (`min`/`max`, numbers or `YYYY-MM` dates, null = open-ended). "Exactly one of the two" and "shape fits the clue type's `value_kind`" are checked at release time (T-047), not in the schema, because conditional schema rules broke the generated TypeScript before (Decision 020). (5) Each clue type row also carries `value_kind`, `unit`, `found_in` (ad, photos, papers, car, vin), `paper_fields` per country (FR "P.2"), the "ask the seller" template, a default strength, and the usual label/short/explainer, so T-046 doesn't need another schema change. (6) Look-alike `reason` is a fixed list (`same-generation`, `same-badge`, `same-marketing-name`), not a taxonomy table, because the spec names exactly three. (7) PublishedVariant gains optional `lookalike_group_ids` and `clue_count`, so the web app can skip the "spot it" box without loading every clue.

**Answer:**

### Q-065 · A "BMW i3" registered in 2025-26 with no seed generation · seed (coverage-gaps finding 7) · data builder · 2026-11-15
Registration data has cars named i3 after the i3 (I01) ended in 2022: RDW 2026: 210 cars `I3 50 XDRIVE`; EEA DE 2025: 119 (`I3 50 XDRIVE` 93, `I3 40 XDRIVE` 22, `I3 40L` 4); KBA 2026: 1 `I3`. No generation was added, because what this car is has not been checked against a primary source (it could be a new model sold as "i3", an import of a car sold elsewhere, or a data error). **Default:** the counts stay in `unmatched.csv` ("year outside every generation") and the gap is written in the `bmw-i3-i01` notes in `data/seed/models.yaml`. Should WS3 check it with a primary source and add a generation or model?

**Answer:**

### Q-066 · RDW shared-year cars now counted at model level · match / web (coverage-gaps finding 6) · data builder · 2026-11-15
No answer needed unless you disagree. RDW cars from a year that two generations share, with no name or battery clue, are no longer dropped (Q-041) and never split by a ratio. They are counted for the model: an extra NL entry with `level: model` on every generation of that model, with the note "shared year, generation unknown". That is 10,413 NL cars (Niro 2022 3946, Zoe 2019 2720, Kona 2023 1743, Model S 2016 964, e-Golf 2017 823, Soul 2019 217). `registered_count_nl` stays the generation-level count. EEA still sends a shared year to review (its 2025/2026 files have none). **For the web builder (WS2):** (1) a row can now have two RDW NL entries with the same period (generation + model level), so the React key in `Registrations.tsx` (kind-period-source) is no longer unique; add `level`. (2) The `reg.modelLevel` label reads as "the whole model", but this RDW entry is only the shared-year cars. A label like "1 year, generation unknown" would fit better. The schema needs no change.

**Answer:**

### Q-067 · MG4: what stays split after the Q-062 fix · seed (variants) · data builder · 2026-11-15
No answer needed unless you disagree. Seed variants can now list the names other sources use for the same car (`source_names` in `data/seed/variants.yaml`). MG4 goes from 8 rows to 6. Two splits stay on purpose: (1) OpenEV "Standard Long Range" has the same 64 kWh pack as the Long Range but 125 kW instead of 150 kW, so it stays its own row. It has no pack link, because `variant_links.yaml` only takes seed variant ids. (2) The Standard Range has a year band for 2023+, because OpenEV gives DC 135 kW for 2023-2025 and the seed and KilowattApp give 117 kW for 2022 (KilowattApp also has a 2022 "51 kWh" record at 87 kW). That band has no pack link either. Both are worth a check against a primary source.

**Answer:**

### Q-068 · RDW WLTP + NL price records: how matching should take them · match (coordinator) · coverage-gaps findings 3–4 · pipeline builder (rdw) · 2026-11-15
No answer needed from Menno; this is for the coordinator / match builder. `ev normalise rdw` now also emits `kind="spec"` records: `wltp_range_km`, `consumption_kwh_100km` (one field per record) and `price_new` (country NL, EUR), per make × trade name × year of first admission, confidence medium, each with a `registered_count` weight (the cars behind the median; `_add_spec_facts` skips it). Groups whose spread is wide (IQR > 5 % of the median) or too small (< 5 cars) emit nothing. **Open point:** `rdw` is not in `ATTACH_ONLY_SOURCES`, so as it stands each record becomes a new `<generation>-base` variant (no `variant_name`). **Default (recommended):** add `rdw` to `ATTACH_ONLY_SOURCES` before the next release, so a record attaches to the generation's only variant or the one its WLTP km points to. If that can't land first, run the release without these records (filter `kind == "spec"` for `rdw`). Two smaller points: (1) the WLTP values come from a 10 % plate sample (Socrata refuses joins and has no percentile function), the price median from the full group; (2) an RDW app token would unlock nothing useful (SODA3 needs one, but joins were not tested there), so no account is needed.

**Answer:**

### Q-069 · Manual facts and review-queue ids: judgement calls · addendum 6 P7 · pipeline builder · 2026-11-15
No answer needed unless you disagree. Hand-entered facts now go in `data/manual/<topic>/*.yaml` (one cited fact each: URL, retrieved date, quote or page, entered_by, confidence) and `ev manual check` validates them. **Defaults taken:** (1) **Internal only:** the new source `manual` is `blocked` in `data/sources.yaml`, so the release drops these facts. It follows your answer to Q-008: if cited single facts from maker documents may ship, set `manual` to `active` with a licence line. (2) **Strict units:** a manual fact must use the field's canonical unit (km, not mi), so nothing is converted by hand. (3) **Rank:** once released, a manual fact ranks above the unchecked seed and below EEA/OpenEV, unless `field_sources.yaml` says otherwise. (4) **Review queue:** every row of `data/review/*.csv` now starts with `review_id` + `status` (open / done / wont-fix). Decisions are kept in `data/review/status.yaml`, so rebuilds never lose them. **For the web builder (WS2):** the staff page (Q-035) shows the two new columns as plain text; filtering on `status` would help. It stays read-only, so staff still set a status by editing status.yaml or a CSV.

**Answer:**

### Q-070 · Static pages need a rebuild per release · T-050 / Decision 015 · web builder · 2026-11-15
Model, generation, variant and learn pages are now static and baked from the release present at build time (Q-033/Q-034). Explore and `/data/catalogue-<n>.json` still read `data/releases/latest` at run time, so if `latest` moves on the server without a new image, Explore would show the new release while static pages show the old one (and links to new variants would 404). **Default:** treat a release like code: the release job commits it, CI builds and deploys a new image; rollback = previous image. Server-side `latest` swaps without a rebuild should stop (WS4 to confirm in the deploy runbook). Alternative if hourly freshness is needed later: ISR with on-demand revalidation per release (more moving parts, and the CSP hash manifest from T-050 would then need a different approach). OK?

**Answer:**

### Q-071 · Language URL details: x-default, Belgium and the remembered language · T-050 · web builder · 2026-11-15
Judgement calls in T-050: (1) `x-default` points to English in the Netherlands (`/nl/en/…`): prices in EUR, English text. (2) Belgium serves NL, FR **and DE** (German is an official language there) plus EN; `default_language: nl`. The German UI still falls back to EN key by key. (3) `/{country}` redirects (307) to the language the visitor picked before (cookie set by the language switcher) if that country serves it, else to `default_language` from config; old `/{country}/…` URLs redirect (308) to the default language, or to `?lang=` when served. A language a country doesn't serve (e.g. `/uk/nl/…`) redirects to its default. (4) hreflang uses `lang-REGION` tags (`fr-BE`, `en-GB`). (5) `Accept-Language` never redirects: a small dismissible banner, written in the suggested language, offers the switch. **Default:** as built. Change any of these?

**Answer:**

### Q-072 · CCD2 warning in German and French, and Belgium's own wording · T-043 / Decision 017 · web builder · 2026-11-15
The loan calculator shows the CCD2 warning in the page language: EN "Borrowing money costs money." and NL "Let op! Geld lenen kost geld." (as given in the task). DE and FR have no reviewed wording yet, so they fall back to the English sentence (keys `loan.warning` missing in `de.json` / `fr.json` on purpose). Belgium may require its own national wording in Dutch and French (Code of Economic Law), which could differ from the Dutch "Let op! Geld lenen kost geld." used on `/be/nl`. **Default:** EN fallback for DE/FR, NL text on `/be/nl`, until R-03 (lawyer question) gives the exact wording per country and language; then add per-country keys. Needs a legal check before launch (CCD2 applies from 20 Nov 2026).

**Answer:**

### Q-073 · CSP: hashes for static pages, nonces for the rest; Caddy must stop replacing it · A-02 / T-050 · web builder · 2026-11-15
The app now sends a strict CSP without `'unsafe-inline'` for scripts (`src/proxy.ts`, `src/lib/csp.ts`): a per-request nonce on dynamic pages, and on static pages the sha256 hashes of that page's inline scripts, computed after `next build` by `scripts/csp-hashes.mjs` into `.next/server/csp-hashes.json` (~0.8 MB for 4,235 pages; also copied into the standalone output). Trade-offs: (1) if the manifest is missing (build step skipped), the proxy logs an error and falls back to the old policy with `'unsafe-inline'` so the site keeps working; (2) `style-src` keeps `'unsafe-inline'` (style attributes); (3) **`infra/deploy/ev.caddy` sets its own CSP with `defer`, which replaces the app's header**, so in production the strict policy would be lost (and with `'unsafe-inline'` still in Caddy's copy). **Default:** WS4 removes `Content-Security-Policy` from `ev.caddy` (keep the other headers) and lets the app own it. OK?

**Answer:**

### Q-074 · Top-40 used models: how to rank DE/FR/BE, and 8 models to add to the seed · ADDENDUM-6 P5 · data builder · 2026-11-15
No answer needed unless you disagree. `data/seed/top40.yaml` ranks the top-40 used EVs from registration data we already have. **Defaults taken:** (1) **"Used" = 2–8 years old in 2026 = first registered 2018–2024.** Only the Dutch register (RDW) has that year, so the score uses NL (RDW, 2018–2024) and UK (DfT fleet, all ages, because the UK file has no year), averaged. (2) **Germany, France and Belgium are shown but not scored**: the only data we have there counts *new* cars sold in 2025–2026, which would push brand-new models to the top. **Recommended next step (no cost, open data):** fetch the KBA FZ10 and EEA files for 2018–2024 so DE/FR/BE get a "sold new 2018–2024" count as a used-stock stand-in (KBA/EEA adapter lanes). (3) **8 of the 40 are not in the seed yet:** Volvo EX30, BMW iX1, BMW iX3, Opel/Vauxhall Mokka Electric, Mercedes EQB, Porsche Taycan, BMW iX, Ford Explorer EV. Default: the coordinator adds them in the next seed wave (seed lane). (4) **Wikidata stays corroboration-only** (not in the matcher's `CORROBORATION_SOURCES`): only 12 of 43 items carry a year, and one is a concept year (Enyaq 2017). Coverage today: only registrations NL and DE reach the 80 % "2+ sources" target; spec fields are at 0–12 % (`data/review/coverage-gaps.md`, top-40 section).

**Answer:**

### Q-075 · P6 sources: what the coordinator needs to integrate · ADDENDUM-6 P6 / T-025 · pipeline builder · 2026-11-15
No answer needed from Menno; coordinator to-dos. (1) **Two id spaces for charging sources.** The CLI/sources.yaml ids are `bnetza` and `dft-charging`, but `charging_definitions` and `power_bands` use `bnetza-ladesaeulenregister` and `dft-ev-charging-infrastructure`. **Default:** ChargingStat `source_id` = the taxonomy id (so a stat's source matches its definition's source); the sources.yaml entries carry `aliases: [<taxonomy id>]`. Pick one id per source and drop the alias. (2) **Shared helper** `ev_pipeline/sources/eafo/charging_stats.py` (taxonomy check, validity window, jsonschema validation, writer) sits in the eafo folder only because of lane limits; move it to `sources/_common` if you like. (3) **Outputs in staging, not SourceRecords:** `data/staging/{eafo,bnetza,dft-charging}.charging_stats.jsonl` (+ `.meta.json` with licence, download, status, `releasable`) and `data/staging/rdw-defects.defects.jsonl` (kinds `defect_group` / `defect_count`, shape in the adapter docstring). The release step must read them and keep EAFO out (`releasable: false`). (4) **fueleconomy** records are `kind: spec`, country empty, `;market=us` in record_key. Its `consumption_kwh_100km` is EPA wall-to-wheels on the 5-cycle test, not WLTP: keep fueleconomy out of the primary/fallback list for consumption in `data/field_sources.yaml` (agreement counts only); `epa_range_km` already lists it. Its pack sizes are `battery_kwh_gross`, confidence low.

**Answer:**

### Q-076 · Charging taxonomy gaps found while loading · T-025 / T-024 · pipeline builder · 2026-11-15
No answer needed unless you disagree. **Defaults taken:** values with no taxonomy id are skipped and counted in the run log, never forced into a nearby band. Gaps: (a) **power bands** missing for EAFO AC slow/medium/fast and DC < 50 kW, BNetzA's 8 classes (sheet 3.3: 0–3.7, >3.7–15, >15–22, >22–49, >49–59, >59–149, >149–299, >299 kW; note >149–299 and >299 don't line up with our 150–349 / 350+) and DfT Standard (3–<8 kW) / Standard plus (8–<50 kW). (b) **`uk-dft-evse-2026` valid_from 2026-01-01**, but DfT's EVCI0101 counts EV chargers on the same definition back to 2025-01-01; 180 rows (4 quarters) are dropped by the window. Moving valid_from to 2025-01-01 adds them on the next normalise. (c) **DfT "50kW+"** (rapid + ultra-rapid) is loaded as `public-points-dc` with no band and a note that DC below 50 kW is excluded; a `dc-50-plus` band or a `public-points-50kw-plus` metric would be cleaner. "50kW+ per 100k" has no metric and is skipped. (d) EAFO year rows are read as 31 December, the newest year as the last day of the month in the file title (🟡: the file doesn't say).

**Answer:**

### Q-077 · EAFO charging data: ask the Commission for reuse permission? · T-025 · pipeline builder · 2026-11-15
EAFO's AFIR recharging-points file has no licence of its own. The EC legal notice makes EU-owned content CC BY 4.0 but excludes third-party works, and EAFO says its main source is Eco-Movement (commercial). It's the only fair cross-country series (spec), so it matters for the Europe comparison (Next). **Default:** `eafo` is `blocked` in data/sources.yaml; the loader runs and stages 898 rows marked `releasable: false`; the fixture uses invented numbers. Options: (1) recommended: an email to DG MOVE / EAFO asking whether the AFIR dataset may be reused under CC BY 4.0 (a coordinator can draft it; it goes out in your name, so you approve it); (2) keep EAFO blocked and use national sources only.

**Answer:**

### Q-078 · RDW defects: young cars look "clean" because they haven't had an APK yet · ADDENDUM-6 P6 · pipeline builder · 2026-11-15
No answer needed unless you disagree. Defect counts cover cars first registered at least 3 calendar years before the fetch (2023 and older tonight), but many 2023 cars have not had their first APK yet (e.g. Model Y 2023: 23 of 1,453 sampled cars with any defect, vs Model 3 2019: 1,308 of 2,554). **Default:** rows keep `sample_cars` and `cars_with_any_defect` per group, so the "Known issues" view must compare cars of the same first-registration year only and should hide cohorts where few cars have reports. Raising `MIN_AGE_YEARS` to 4 in the adapter is a one-line change if you prefer. The RDW naming clause (Q-037) applies here too.

**Answer:**

### Q-079 · Weekly data refresh: let GitHub Actions open "Data release N" pull requests? · ADDENDUM-6 P4 · pipeline builder · 2026-11-15
One settings switch for you, no cost. `.github/workflows/data-refresh.yml` runs every Monday (and on demand), refreshes the open sources and opens a PR with only the new release folder and its QA report. **To make it work:** GitHub → repo Settings → Actions → General → tick "Allow GitHub Actions to create and approve pull requests". **Good to know:** PRs opened by the workflow's own token don't start CI by themselves; close and reopen the PR (one click) to run CI before you merge. Later option: a small GitHub App token so CI starts on its own (no cost, a bit of setup). **Default until you answer:** the workflow runs; if the setting is off, the PR step fails and the run's summary page still shows what changed. Also open: the S3 snapshot backend (Scaleway) is an interface only tonight; raw snapshots stay on the machine that runs the refresh (Decision 021).

**Answer:**

### Q-080 · T-059 new sources in the release: judgement calls · T-059 · pipeline builder · 2026-11-15
No answer needed unless you disagree; coordinator/WS2 notes. **Defaults taken:** (1) **EPA range is now a row field** (`epa_range_km`, additive schema change): merged only with other EPA figures (fueleconomy primary, OpenEV fallback, 2 % tolerance), never with WLTP. 84 variants have one; 12 gain a 2nd agreeing EPA source through fueleconomy. fueleconomy attaches several US trims and model years to one variant, so 280 EPA values land in `conflicts.csv` (never averaged; the earliest model year of the primary wins). (2) **Wikidata years** go on `generations[].years_corroboration` (corroborated = every Wikidata year within ±1 of the nearest seed boundary of that kind); years never change. 9 checks on 8 generations: 7 agree, 2 disagree (Enyaq 2017 = concept year; ID.3 2024 = the China-only "Chuzhong" item), both flagged in qa.json `sections`. (3) **Known issues** ship as `catalogue.known_issues.by_generation` (cohort = generation × first-registration year, rates per 100 *sampled* cars, top 5 codes, each with the same-year baseline over all sampled BEVs; `few_reports` = year with < 10 % of cars reported or < 10 cars with a report: hide by default). A year shared by two generations is placed only when exactly one has catalogue rows, else skipped. Source id `rdw-defects` (the adapter's `SOURCE` says `rdw`; the release renames it so it doesn't clash with the registrations source, adapter owner may align it). Labels are RDW's Dutch text only (hx2c-gt7k has no English column). (4) **Charging stats** ship as `data/releases/<n>/charging_stats.json` (new schema def `ChargingStatsRelease`); stat `source_id` keeps the taxonomy id and resolves through the new `aliases` support in the licence gate; `source_aliases` in the file maps it back. EAFO stays out (status blocked). **For WS2:** the web app can read `known_issues`, `years_corroboration`, `epa_range_km` and `charging_stats.json` now; RDW naming clause (Q-037) applies to the known-issues view.

**Answer:**

### Q-081 · T-051 seed: segments and two split generations are judgement calls · T-051 · data builder · 2026-11-15
No answer needed unless you disagree. The 8 missing top-40 models are now in `data/seed/models.yaml` (EX30, iX1, iX3, Mokka-e, EQB, Taycan, iX, Explorer EV), built only from staged data. **Defaults taken:** (1) **Segment** is required by `validate_seed.py`, but no source gives one. Rule used: the segment of the existing seed model with the nearest OpenEV length, same body family. Results: EX30 J-small, iX1 J-medium, iX3 J-medium, iX J-large, **EQB J-large** (I-Pace 4682 mm vs EV6 4680 mm, J-medium; the EQA is J-medium, so J-medium is defensible too), Taycan F. Mokka-e has no length anywhere: J-small from Wikidata (mini SUV / supermini, item for all Mokkas). **Explorer EV has no size source: J-medium as a placeholder.** (2) **Year rule:** start = first RDW first-admission year with ≥ 5 % of the cars, one year earlier when RDW has cars then and Wikidata or a spec model year agrees (so OpenEV 2023 EX30 records still match). (3) **Two generations, not one,** where all registration sources switch names: iX3 (plain "IX3" to 2025, "IX3 50 XDRIVE"/"IX3 40" from 2026) and EQB → "GLB" (from 2026). The new halves start in 2026, not 2025, because the matcher picks a generation by year and would move all 2025 cars to the variant-less new generation; about 780 EEA 2025 iX3 and 164 GLB cars with the new names therefore sit on the old generation. Both new halves and the Mokka-e have **no variant rows** (no OpenEV record; KilowattApp/ADEME/RDW only attach). (4) OpenEV lists the Explorer EV with 7 seats / 3 rows: worth a check against a primary source.

**Answer:**

### Q-082 · T-053 registration history: KBA 2018 has no licence line; two smaller calls · T-053 · pipeline builder · 2026-11-15
No answer needed unless you disagree. KBA FZ10 now goes back to 2019 and EEA to 2018 (final data per year), one registrations entry per year. **Defaults taken:** (1) **KBA 2018 is skipped.** The December 2018 file names no licence at all (only "© Kraftfahrt-Bundesamt, Flensburg"); from 2019 on the files say "Datenlizenz Deutschland – Namensnennung 2.0". Germany 2018 is still covered by EEA (34,398 BEVs counted). Option: accept 2018 under the same licence as the rest of the FZ10 series (🟡 likely, not stated in the file) by asking KBA, or leave it out (recommended, nothing lost but one DE source for one year). (2) **KBA "/", "." and "X" cells** (not reliable / secret / not comparable; 13–25 small rows a year in 2021–2024, 64–383 cars) are treated as *no count*, never as 0. (3) **EEA final years are confidence high**, the 2025 provisional table stays medium. Per-year counts are in `data/SOURCES.md`.

**Answer:**

### Q-083 · T-051 part 2: segments, placeholders and EQE left out · T-051 · data builder · 2026-11-15
No answer needed unless you disagree. 15 more models are in `data/seed/models.yaml` (ID.7, Elroq, Q6 e-tron, Tavascan, A6 e-tron, i5, EV3, Renault 5, ID. Buzz, Inster, bZ4X, electric CLA, Puma Gen-E, Macan Electric, Scenic E-Tech), picked by NL used + UK fleet + DE 2025 new share from staging, with the same rules as Q-081. **Defaults taken:** (1) **Segment order:** a Wikidata size class comes first (executive car → **E** for ID.7, i5, A6 e-tron; compact crossover SUV → J-medium for bZ4X; subcompact crossover → J-small for Puma; "city car" → J-small for Inster), because the nearest-length rule can never give E (no E model in the seed) and would put ID.7/A6/i5 in F. (2) **Placeholders, no size or body source:** Elroq, Macan Electric and ID. Buzz (mpv) J-medium; **Kia EV3 has no body source at all** (no OpenEV record, Wikidata only "car model"): body `suv` and J-medium are placeholders. Tavascan: OpenEV body `coupe`, segment from the nearest length of any body (Enyaq, J-medium). (3) **Mercedes EQE skipped** although it ranks 12th: KBA's E-KLASSE BEV column holds both EQE saloon and EQE SUV, and RDW/EEA/DfT names don't separate them, so neither the KBA mapping nor a saloon/SUV split is grounded. Scenic E-Tech took the 15th place. (4) **Start years by the RDW rule**, so Elroq and Puma Gen-E start in 2025 although KBA (Elroq, 46 cars) or OpenEV/KilowattApp (Puma, Elroq) show 2024; Scenic starts 2024 although EEA FR has 31 cars in 2023. (5) RDW 2026 "CLA 200"/"CLA 250" (339 cars, no engine capacity) are counted as electric CLAs; EEA lists "CLA 200 WITH EQ TECHNOLOGY" as electric. (6) **Not mine, but seen:** with T-053's EEA history in staging, `tests/test_real_release.py::test_registrations_are_never_summed_across_sources_or_periods` fails for 57 models (old and new), because the test treats all EEA facts as one period; `tests/test_pack_guard.py` has 2 ruff E501 lines.

**Answer:**

### Q-084 · T-057 EV6 fix and CI data gate: three judgement calls · T-057 · pipeline builder · 2026-11-15
No answer needed unless you disagree. **Finding:** the EV6 77.4 kWh AWD row showed 80 kWh usable because KilowattApp lists the 2024+ facelift (84 kWh pack, 263 kW DC; records "EV6 Long Range AWD" MY2024 and "EV6 GT" MY2025) and the matcher put those model years on the 2021 variant; KilowattApp ranks above the seed, so its 80 won. 🟢 80 kWh is the facelift's usable figure, not a typo, but it can never belong to pack egmp-77-4 (77.4 gross). **Defaults taken:** (1) **A rule, not a hand edit:** a new pack guard (`pipeline/ev_pipeline/qa/pack_guard.py`) keeps any usable-kWh fact above the linked pack's gross out of the merge and lists it in `data/review/conflicts.csv` ("> pack … gross … kWh"). It touches 6 more rows' conflicts (two Audi e-tron, Model 3 LFP, Model S 85, ID.3 Pure) but changes no other published value. It needed a 4-line hook in `release/build.py` (outside my lane; the coordinator may move it). (2) **The facelift is not split out yet:** it should get its own variant or year band (models/variants lane; the matcher only splits on WLTP >5 % or DC >10 %, not battery size). Until then the facelift's numbers stay out of the 2021 rows. (3) **CI `data-qa` checks the committed release, not a rebuild:** staging is git-ignored, so CI can't run `ev release --dry-run`; instead it runs the seed / variant / taxonomy validators and re-runs the blocking QA (provenance, licence gate against today's sources.yaml) on `data/releases/latest`. **Heads-up:** `validate_taxonomy.py` fails today (25 new generations from T-051 part 2 have no variant link or generation default), so `data-qa` will be red until those links are added.

**Answer:**

### Q-085 · Used prices in the release (schema field) + Wave 5 web polish calls · T-050 · web builder · 2026-11-15
No answer needed unless you disagree. **(1) Used-price rankings need a release field.** The "best used EV under €15k / €20k / €25k" pages are built but hidden: release 1 has no used prices, and the schema has no used-price field. The web app reads an optional `used_prices` array from `catalogue.json` (per generation × country: `generation_id, country, currency, typical, low?, high?, samples, source_ids, retrieved_at, estimate?`; see `UsedPriceBand` in `apps/web/src/lib/used-rankings.ts`). Bad entries are dropped. A list appears (page, /top link, sitemap) only when at least 5 generations in that country have a sourced band with at least 5 samples. **Default:** the coordinator adds that shape to `packages/schema` when T-056 delivers prices (or renames it; the web side is one accessor, `catalogue.usedPrices()`). Ranked by km of real range per €1,000 of the typical used price (spec: "real range per €"), one row per generation, using the median-range variant. UK caps are £13k / £17k / £21k (about 0.86 £/€, rounded down). **(2) Theme approach (architectural, for DECISIONS):** colours come from `docs/design/tokens.json` via `apps/web/scripts/theme.mjs` → `src/app/tokens.generated.css`. `globals.css` points Tailwind's slate/blue/amber/green/red/white palette at those tokens, so existing classes follow Day trip / Night drive without touching every component. New code should use the tokens directly. The remembered choice is applied before first paint by a same-origin `/theme-init.js`, not an inline script, so the CSP stays as it is. Coordinator: please log this as a decision if you agree. **(3) No era badge exists** on model pages yet, so glossary sweep item 8 "era badge / timeline → `era`" has nothing to attach to. It is wired wherever an era label is shown (Explore column, cards).

**Answer:**

## Closed

### Q-033 · Model pages can't be static while the layout reads request headers · T-009 / T-012 · builder · 2026-11-15
The ev, top and learn pages have `generateStaticParams` for all 5 countries (1,552 paths), but `app/[country]/layout.tsx` calls `requestLang()` → `headers()`, so Next renders every route on demand (ƒ). This works and is fast (catalogue is cached in memory), but it is not static. **Default:** left as is; the pages turn static by themselves once language stops depending on the request (e.g. a `/[country]/[lang]` segment or language = country default plus a client switch). Is static output needed for launch?

**Answer (overnight, Decision 015):** Done in T-050. URLs are now `/{country}/{lang}/…`; the language comes from the URL, never from request headers, so the root layout (`app/[country]/[lang]/layout.tsx`, which renders `<html lang>`) reads no headers. Model, generation, variant, learn, rankings and about pages are static again (SSG ●, `generateStaticParams` over the served country × language pairs from `config/countries/*.yaml`): 4,235 pages with release 1 (variants 2,167 = 197 × 11 pairs). Explore and Compare stay on demand because they render from the query string. Closed.
### Q-034 · Static model pages (Q-033): skipped for now, needs a decision · T-008 (wave 4) · builder · 2026-11-15
Tried to make the ev, top and learn pages static. **Not done**, for three reasons: (1) `<html lang>` sits in the root layout, which can only learn the language from the request, so a static page needs the language as a route segment, which means a layout restructure (multiple root layouts or a hidden `[lang]` segment the proxy rewrites to); (2) static pages bake the catalogue in at build time, but the app re-reads `data/releases/latest` at runtime (Decision 008: releases swap atomically and roll back by pointing `latest` back), and the Docker build stage has no `data/releases`, so in the image the pages would be built from the dev fixture; (3) one copy per language would mean 1,552 × 6 paths. **Default:** pages stay on-demand (ƒ, fast: the catalogue is cached in memory). **Proposal if static is wanted:** proxy rewrites `/{country}/…` to a hidden `/{lang}/{country}/…` tree (public URLs, `?lang` and the cookie stay as they are), `generateStaticParams` only for each country's default language, others on demand with ISR, `revalidate` on a release change, and `data/releases` copied into the build stage. Needs a Decision entry first. Is static output needed for launch?

**Answer (overnight, Decision 015):** Done in T-050, along the lines proposed, with these choices: (1) `<html lang>`: the root layout moved to `app/[country]/[lang]/layout.tsx` (plus `app/staff/layout.tsx` and `app/global-not-found.tsx`; `experimental.globalNotFound`), so no hidden segment or rewrite is needed. (2) Release swaps: static pages are built from the release in the build, and the Docker build stage now copies `data/releases/<latest>` in, so **a new release (or a rollback) means a new image** (rollback = redeploy the previous image). If the release is missing or half-written while `data/releases/latest` exists, `next build` now fails instead of silently using the dev fixture, and a post-build check fails on any catalogue page that came out as a 404 (this happened once tonight when the pipeline rewrote the release mid-build). Follow-up for WS4 in **Q-070**. (3) Paths: only served pairs (each country's own languages + EN = 11 pairs), not 30. Closed.

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

