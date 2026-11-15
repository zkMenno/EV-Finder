# Coverage gaps: the 40 seed models (release 1)

Backlog item 5 of `workstreams/OVERNIGHT/ADDENDUM-5.md`. Written 2026-11-15 by an overnight data-review agent. Read-only review: no code, seed or data was changed.

**Inputs:** `data/seed/{models,variants,platforms,battery_packs,variant_links}.yaml`, `data/releases/1/{catalogue.json,coverage.md}`, `data/review/unmatched.csv`, `data/staging/*.records.jsonl` (for the counts), `data/sources.yaml`, `research/R-02`, `R-06` (future markets), `R-07` (Europe expansion), `docs/spec/source-matrix.md`.

**No values from memory.** Every count below comes from the staged records behind release 1. Where this file says a source "could fill" a gap, that is a pointer to a source, not a value.

## How this was produced (and one caveat about unmatched.csv)

- `unmatched.csv` hits its 1,900-row cap, so its detail rows are grouped (one row per source × make × model × reason) and `(Nx)` is the **number of records**, not the number of cars. To get car counts I re-ran the release-1 matcher (`ev_pipeline.match.matcher.match_records`) read-only in a scratch folder on the same staged records and the same source gate. It gives the same split as the release: 4,529 unmatched records for seed makes plus 2,680 for makes not in the seed. Each unmatched record was joined back to its staged `registered_count`.
- Count kinds are never added together (same rule as the release README): **NL** = RDW fleet on 2026-11-14, **UK** = DfT VEH0120 licensed BEVs 2026 Q2, **DE** = KBA FZ10 new BEV registrations (full year 2025, and 2026 Jan–Oct), **FR/BE** = EEA new registrations 2025 (provisional).
- `ᵐ` = DfT model-level count. DfT has no model year, so a multi-generation model shows the same UK total on every generation.
- KBA reports by *Modellreihe*. Where a KBA series name is not the car's own name (e.g. BMW `X1`, Mercedes `GLB`, `E-KLASSE`), it is read from the BEV column and mapped by me. Those mappings are marked 🟡.

**Legend for the field cells** (one count per variant row in release 1): **D** = 2+ agreeing outside sources · **S** = one outside source · **M** = `seed-manual` only (hand-entered, unchecked) · **E** = estimate only (`model-estimate`) · **–** = missing. Example: `D1 S2 M1` = 1 row double-sourced, 2 single-sourced, 1 seed-only. `?` after the years = generation marked `uncertain` in the seed.

## Summary

1. 40 models, 56 generations, 195 variant rows. `nissan-leaf-gen3` has **0 rows**: it has counts (RDW 264, KBA 7 + 719, EEA DE 26) but no spec record in any staged source.
2. **Real range has no outside source on any row** (110 estimate, 85 missing). Every filler with real tests (Nyland, NAF, Spritmonitor) is `waiting_permission`; ADAC is `blocked`.
3. **WLTP is missing on 98 of 195 rows**, almost all pre-2023 generations that OpenEV doesn't cover. Two `active` sources hold it but aren't imported yet: RDW's fuel table (per plate) and EEA (per type). Both are releasable today once their adapters are extended.
4. **Used prices: zero, in every country.** No used-price source is in `sources.yaml`. New prices exist only for FR (ADEME, 8 rows) and DE (OpenEV, 7 rows). NL new price (RDW `catalogusprijs`) is `active` but not imported. BE and UK have no new-price source at all.
5. **Alias bugs hide big counts for seed models:** EEA writes the make as `VOLKSWAGEN, VW` (ID.3: 31978 DE + 3235 BE; ID.4: 21769 DE + 5300 BE unplaced). OpenEV writes `MG Motor`, so 15 MG4 spec records are lost and MG4 WLTP is 0/4. KBA reports a single `MINI` series (15495 in 2025, 17209 in 2026 YTD), so Mini J01 has no DE count.
6. **Shared-year ambiguity drops real NL cars:** Kia Niro 2022 (3946), Renault Zoe 2019 (2720), Hyundai Kona 2023 (1743), Tesla Model S 2016 (964), VW e-Golf 2017 (823), Kia Soul 2019 (217). RDW type-approval data (`active`, fields not yet checked) is the likely tie-breaker.
7. **Generation years look wrong in registration data:** VW ID.4 has 2830 NL cars first registered in 2020 (seed starts 2021). Audi e-tron has 644 in 2018. Kia Soul SK3 is still registered after 2022 (RDW 197, EEA 49, KBA 40). A new BMW i3 shows up in 2025–26 (EEA 119, RDW 210) with no generation in the seed.
8. **Pack/platform links:** 72 of 195 rows have no `battery_pack_id`. 55 of them are variants added from OpenEV/KilowattApp that `variant_links.yaml` doesn't cover (so they have no platform either). The other 17 sit in generations whose default lists several pack options, so no pack gets chosen. 171 of 195 rows lack nominal voltage. Fillers are `maker-docs` (blocked, Q-008) and Nyland (waiting); OpenEV (`active`) can fill gross kWh and chemistry for 2023+ cars.
9. **Old generations have no DE/FR/BE counts** because only 2025/2026 files were fetched. KBA FZ10 goes back to 2012 and EEA to 2010 (R-02), both `active`, so this is a fetch job, not a licence job. A DE *fleet* count needs KBA FZ2/FZ6 (`blocked`). FR/BE fleet by model has no open source.
10. **Case for expanding the seed:** the seed places 62.4% of the NL BEV fleet, 62.9% of the UK fleet and 39.4% of 2025 DE new BEV registrations. The 20 largest missing models would add 17.3% (NL), 15.9% (UK) and 39.0% (DE 2025). All 20 have registration counts from `active` sources, and all 20 have at least one OpenEV, KilowattApp or ADEME spec record (Skoda Elroq, Kia EV3, Hyundai Inster and Citroen e-C3 only have 1–3 KilowattApp records).

## Filler key: which source can fill what, and is it releasable today

"Releasable today" = `status: active` in `data/sources.yaml`. "Adapter extension" = the source is active but the current adapter doesn't read that field yet.

| Source id | Status | Can fill (for the gaps below) | Note |
|---|---|---|---|
| `openev` | active ✅ | WLTP, net + gross kWh, AC, DC, chemistry, cooling, DE new price, 2023+ model years | Already merged. Misses most pre-2023 cars. Make alias `MG Motor` missing |
| `kilowatt-openev` | active ✅ | net kWh, AC, DC, consumption, charge curves (estimated), older model years | Already merged. Many records fail on variant ties (attach-only) |
| `rdw` | active ✅ | NL fleet (imported). **Adapter extension:** per-plate WLTP range + Wh/km (`8ys7-d773`, empty for NEDC-era cars per R-02), `catalogusprijs` (NL new price), type-approval keys (TGK, fields not checked) | Bijsluiter attribution issue (Q-037) |
| `eea` | active ✅ | FR/BE/NL/DE new registrations (imported, 2025 only). **Adapter extension:** electric range + Wh/km per type/variant/version; years since 2010 (R-02) | 2025 provisional. Make alias `VOLKSWAGEN, VW` / `AUDI AG` missing |
| `ademe` | active ✅ | WLTP, consumption, weight, FR new price | Current FR line-up only. Records without a year can't pick a generation |
| `kba-fz10` | active ✅ | DE new registrations by series. **More fetches:** monthly files back to 2012 (R-02) | Series are coarser than models (ID.4 row includes ID.5) |
| `dft-veh` | active ✅ | UK fleet by model text | No model year, so multi-gen models stay model-level. R-02 recommends VEH0124 (year of first use) to split per generation; not in the registry yet |
| `wikidata` | active ✅ (not imported) | generation boundaries, platform names 🟡 | Source matrix rates it 🟡 |
| `fueleconomy` | active ✅ (not imported) | EPA range (US cycle, US-sold models only) | Not WLTP and not real range |
| `model-estimate` | active ✅ | real range, consumption, curves, always labelled estimate | Today's only real-range "source" |
| `nyland`, `fastned`, `naf`, `spritmonitor` | waiting_permission ⏳ | real range, usable kWh, DC curves, pack voltage, real consumption | Nyland data must stay in `data/local/` |
| `maker-docs` | blocked ⛔ (Q-008) | pack voltage, chemistry, platform, generation boundaries, BE/UK/DE new prices | Single facts by URL + date once Q-008 is decided |
| `kba` (FZ2/FZ6/FZ28) | blocked ⛔ | DE fleet by make + trade name | Layouts not checked (R-02) |
| `be-mobilit` | blocked ⛔ | BE registrations by make + commercial model | Licence unconfirmed, captcha |
| `adac`, `euroncap`, `edmunds`, `insideevs`, `consumer-reports`, `aviloo`, `recurrent` | blocked ⛔ | real range, battery health | No open licence |
| used-price sources | **not in registry** | used asking prices per country | Source matrix: partner feeds (layer 1), free indices (Autotrader RPI, AutoScout24 AGPI, Indicata) for trends. Layer 3 sampling stays off (R-03 legal brief) |

R-06 (future markets) and R-07 (Europe expansion) add no source for NL/DE/FR/BE/UK. Their only overlap is EEA, which R-07 says to widen to more countries.

## Gaps shared by every seed model

These hold for all 40 models, so they aren't repeated per model below.

| Gap | Size in release 1 | Filler | Releasable today? |
|---|---|---|---|
| Real range not measured | 195/195 rows: 110 estimate, 85 missing | `nyland` / `naf` / `spritmonitor` (waiting) · `model-estimate` (labelled) | ⏳ no (only estimates) |
| Used price NL/DE/FR/BE/UK | 0 rows | none registered (partner feeds, price indices) | ⛔ no |
| New price NL | 0 rows | `rdw` `catalogusprijs` (adapter extension) | ✅ yes, after adapter work |
| New price FR | 8 rows | `ademe` (current models only) | ✅ yes |
| New price DE | 7 rows | `openev` (2023+); `maker-docs` | ✅ partly |
| New price BE, UK | 0 rows | none open (R-02); `maker-docs` | ⛔ no |
| WLTP on pre-2023 generations | 98/195 rows missing | `rdw` brandstof per plate; `eea` per type (both adapter extensions). NEDC-era type approvals have no WLTP field (R-02) | ✅ yes, after adapter work |
| Nominal / max pack voltage | 171/195 rows missing nominal; 195/195 missing max | `maker-docs` (blocked), `nyland` (waiting) | ⛔ no |
| UK count per generation | 78 rows only have the model-level count | DfT VEH0124 (needs a registry entry; OGL) | ✅ likely, after registry entry |
| DE/FR/BE counts for generations that ended before 2025 | 24 generations show none | `kba-fz10` back files 2012+, `eea` back years 2010+ (new registrations) · `kba` FZ2/FZ6 for DE fleet (blocked) · no open FR/BE fleet by model | ✅ new registrations yes · ⛔ fleet no |
| Row provenance for `price_new` | 14 rows have a price but no `provenance.price_new` entry (the facts exist in `facts.parquet`) | build fix, not a data gap | n/a |

## Part 1: per generation (release 1)

Variant counts are release-1 rows; the number in brackets is how many of them come from `seed-manual`. Registration counts are the generation's own totals. `–` in a count column = no record for that generation in that source.

| Generation | Years (seed) | Variants: release (seed-manual) | WLTP | Usable kWh | AC kW | DC peak | Real range | Pack / platform links | NL fleet (RDW) | UK fleet (DfT) | DE new 2025 (KBA) | DE new 2026 YTD (KBA) | FR new 2025 (EEA) | BE new 2025 (EEA) | New price in release |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `tesla-model-3-gen1` | 2019–2023 | 4 (4) | –4 | S4 | S4 | S4 | –4 | 3 pack(s); not-disclosed: gross 2, V 3, chem unset 1 | 44906 | 146205ᵐ | – | – | – | – | none |
| `tesla-model-3-highland` | 2024–now ? | 3 (0) | S3 | D1 S2 | D1 S2 | D1 S2 | E3 | 2 pack(s); 3 row(s) no pack; not-disclosed: gross 1, V 2, chem unset 1 | 20572 | 146205ᵐ | 6855 | 15466 | 6128 | 3634 | DE 1 |
| `tesla-model-y-gen1` | 2021–2024 | 4 (3) | S3 –1 | S4 | D1 S3 | D1 S2 M1 | E3 –1 | 2 pack(s); 1 row(s) no pack; 1 row(s) no platform; not-disclosed: gross 1, V 2, chem unset 1 | 41025 | 141091ᵐ | – | – | – | – | none |
| `tesla-model-y-juniper` | 2025–now ? | 3 (0) | S3 | D1 S2 | D1 S2 | S3 | E3 | 2 pack(s); 3 row(s) no pack; not-disclosed: gross 1, V 2, chem unset 1 | 18897 | 141091ᵐ | 12303 | 31998 | 19232 | 6124 | none |
| `tesla-model-s-gen1` | 2013–2016 ? | 3 (3) | –3 | S2 E1 | S2 –1 | S1 M1 –1 | E2 –1 | 3 pack(s); not-disclosed: usable 3, V 3 | 2432 | 9996ᵐ | – | – | – | – | none |
| `tesla-model-s-facelift` | 2016–2021 ? | 4 (4) | –4 | S4 | S4 | S2 M2 | E2 –2 | 2 pack(s); not-disclosed: usable 2, V 2 | 5565 | 9996ᵐ | – | – | – | – | none |
| `tesla-model-s-palladium` | 2022–2026 ? | 2 (2) | S2 | D2 | D2 | D2 | E2 | 1 pack(s); not-disclosed: gross 1, V 1 | 621 | 9996ᵐ | 124 | 166 | 47 | 54 | none |
| `renault-zoe-ph1` | 2013–2019 | 5 (5) | –5 | S5 | S5 | S4 –1 | –5 | 2 pack(s); not-disclosed: gross 2, V 2, chem unset 1 | 4794 | 26584ᵐ | – | – | – | – | none |
| `renault-zoe-ph2` | 2019–2024 ? | 2 (2) | M2 | S2 | S2 | S2 | E2 | 1 pack(s); not-disclosed: gross 1, V 1 | 7861 | 26584ᵐ | – | – | – | – | none |
| `renault-megane-e-tech-gen1` | 2022–now ? | 4 (2) | S2 –2 | S4 | S4 | D1 S3 | E2 –2 | 2 pack(s); 2 row(s) no pack; 2 row(s) no platform; not-disclosed: gross 2, V 2 | 9505 | 11969 | 502 | 775 | 9684 | 443 | none |
| `nissan-leaf-ze0` | 2011–2017 ? | 2 (2) | –2 | S2 | S2 | S2 | E2 | 2 pack(s); not-disclosed: V 1, chem unset 1 | 1967 | 60318ᵐ | – | – | – | – | none |
| `nissan-leaf-ze1` | 2018–2025 ? | 4 (2) | S2 M2 | S4 | S4 | S4 | E4 | 2 pack(s); 2 row(s) no pack; 2 row(s) no platform; not-disclosed: V 1 | 10200 | 60318ᵐ | – | – | 224 | 8 | FR 1 |
| `nissan-leaf-gen3` | 2025–now ? | 0 (0) | – | – | – | – | – | no rows; seed has 2 pack(s); not-disclosed: gross 2, V 2, cell 2 | – | – | – | – | – | – | none |
| `volkswagen-e-golf-mk7` | 2014–2017 | 1 (1) | –1 | S1 | S1 | S1 | E1 | 1 pack(s); not-disclosed: usable 1, V 1 | 425 | 7114ᵐ | – | – | – | – | none |
| `volkswagen-e-golf-mk75` | 2017–2020 | 1 (1) | M1 | S1 | S1 | S1 | E1 | 1 pack(s); not-disclosed: V 1 | 8149 | 7114ᵐ | – | – | – | – | none |
| `volkswagen-id3-gen1` | 2020–now ? | 5 (3) | S3 –2 | D2 S3 | D3 S2 | D1 S4 | E3 –2 | 3 pack(s); 2 row(s) no pack; 2 row(s) no platform; not-disclosed: V 3 | 29921 | 55453 | 31938 | 27165 | 8683 | 4 | none |
| `volkswagen-id4-gen1` | 2021–now ? | 3 (3) | S2 –1 | D2 S1 | D2 S1 | D1 S2 | E2 –1 | 2 pack(s); not-disclosed: V 2 | 21295 | 40864 | 26550 | 21772 | 6195 | 23 | none |
| `hyundai-ioniq-electric-gen1` | 2016–2022 ? | 2 (2) | M1 –1 | S2 | S2 | S2 | E2 | 2 pack(s); not-disclosed: usable 2, V 2, chem unset 2 | 4126 | 8531 | – | – | – | – | none |
| `hyundai-kona-electric-os` | 2018–2023 | 2 (2) | –2 | S2 | S2 | S2 | –2 | 2 pack(s); not-disclosed: gross 2 | 16736 | 45814ᵐ | – | – | – | – | none |
| `hyundai-kona-electric-sx2` | 2023–now | 2 (0) | S2 | S2 | S2 | D1 S1 | E2 | 2 pack(s); 2 row(s) no pack; not-disclosed: gross 2, V 2 | 7692 | 45814ᵐ | 6527 | 5896 | 4721 | 498 | none |
| `hyundai-ioniq-5-gen1` | 2021–now ? | 8 (5) | S3 –5 | D1 S2 M5 | D1 S2 M5 | D1 S2 M5 | E3 –5 | 3 pack(s); 3 row(s) no pack; 3 row(s) no platform; not-disclosed: usable 3 | 9637 | 23860 | 6608 | 4971 | 717 | 904 | none |
| `hyundai-ioniq-6-gen1` | 2022–now ? | 6 (3) | S3 –3 | S3 M3 | S3 M3 | S3 M2 –1 | E3 –3 | 2 pack(s); 3 row(s) no pack; 3 row(s) no platform; not-disclosed: usable 2, V 1 | 2241 | 5919 | 1016 | 811 | 176 | 311 | none |
| `kia-soul-ev-ps` | 2014–2019 ? | 2 (2) | –2 | S2 | S2 | S2 | E1 –1 | 2 pack(s); not-disclosed: usable 2, V 2, chem unset 1 | 282 | 4177ᵐ | – | – | – | – | none |
| `kia-soul-ev-sk3` | 2019–2022 ? | 2 (2) | –2 | S2 | S2 | S2 | –2 | 2 pack(s); not-disclosed: gross 2 | 1293 | 4177ᵐ | – | – | – | – | none |
| `kia-niro-ev-de` | 2018–2022 ? | 2 (2) | –2 | S2 | S2 | S2 | –2 | 2 pack(s); not-disclosed: gross 2 | 15412 | 48864ᵐ | – | – | – | – | none |
| `kia-niro-ev-sg2` | 2022–now | 1 (1) | –1 | M1 | M1 | M1 | –1 | 1 pack(s); not-disclosed: gross 1, V 1 | 12335 | 48864ᵐ | 522 | – | 540 | 137 | none |
| `kia-ev6-gen1` | 2021–now ? | 4 (4) | S3 –1 | S3 M1 | S3 M1 | S3 M1 | E3 –1 | 2 pack(s); not-disclosed: usable 2 | 12330 | 19919 | 3326 | 1512 | 830 | 800 | FR 3 |
| `bmw-i3-i01` | 2013–2022 ? | 4 (4) | –4 | S3 M1 | S3 M1 | S3 M1 | E3 –1 | 3 pack(s); not-disclosed: V 3 | 8620 | 17057 | – | – | – | – | none |
| `bmw-i4-g26` | 2021–now | 4 (3) | S4 | D4 | D4 | D4 | E4 | 2 pack(s); 1 row(s) no pack; 1 row(s) no platform; not-disclosed: gross 1, V 2 | 11179 | 43668 | 11680 | 10038 | 3038 | 5243 | DE 1 |
| `peugeot-e-208-p21` | 2019–now ? | 4 (2) | D1 S1 –2 | D1 S2 M1 | D1 S2 M1 | D1 S2 M1 | E2 –2 | 2 pack(s); 2 row(s) no pack; 2 row(s) no platform; not-disclosed: V 2 | 20035 | 17657 | 1887 | 3624 | 17929 | 457 | none |
| `peugeot-e-2008-p24` | 2020–now ? | 4 (2) | S2 –2 | D1 S2 M1 | D1 S2 M1 | D1 S2 M1 | E2 –2 | 2 pack(s); 2 row(s) no pack; 2 row(s) no platform; not-disclosed: V 2 | 12618 | 23028 | 1868 | 4025 | 8400 | 817 | none |
| `opel-corsa-e-f` | 2020–now ? | 2 (2) | –2 | M2 | M2 | M2 | –2 | 2 pack(s); not-disclosed: V 2 | 12079 | 21679 | 6804 | 6650 | 1673 | 261 | none |
| `fiat-500e-312` | 2013–2019 ? | 1 (1) | –1 | S1 | S1 | S1 | E1 | 1 pack(s); not-disclosed: usable 1, V 1 | 1278 | 10611ᵐ | – | – | – | – | none |
| `fiat-500e-332` | 2020–now ? | 7 (3) | S5 –2 | S6 M1 | S6 M1 | S6 M1 | E5 –2 | 2 pack(s); 4 row(s) no pack; 4 row(s) no platform; not-disclosed: usable 1, V 2 | 10564 | 10611ᵐ | 10550 | 8502 | 4457 | 248 | FR 1 |
| `skoda-enyaq-gen1` | 2020–now ? | 7 (4) | S5 –2 | D5 S1 M1 | D5 S1 M1 | D2 S4 M1 | E5 –2 | 2 pack(s); 3 row(s) no pack; 3 row(s) no platform; not-disclosed: V 2 | 27479 | 47813 | 25383 | 27226 | 4405 | 4573 | none |
| `mg-mg4-gen1` | 2022–now ? | 4 (4) | –4 | S4 | S4 | S4 | –4 | 3 pack(s); not-disclosed: gross 2, V 3 | 5845 | 48970 | 5567 | 4618 | 2615 | 1053 | none |
| `mg-zs-ev-gen1` | 2019–now ? | 3 (3) | –3 | S2 E1 | S2 M1 | S2 M1 | –3 | 3 pack(s); not-disclosed: usable 3, V 3 | 8002 | 29246 | 586 | – | 52 | – | none |
| `polestar-2-gen1` | 2020–now ? | 9 (4) | S5 –4 | D4 S1 M4 | D5 M4 | D2 S3 M4 | E5 –4 | 3 pack(s); 5 row(s) no pack; 5 row(s) no platform; not-disclosed: V 3 | 14932 | 38163 | 1658 | 1278 | 55 | 1003 | DE 5 |
| `audi-e-tron-ge` | 2019–2022 | 3 (3) | –3 | S3 | S3 | S3 | –3 | 2 pack(s); not-disclosed: usable 1, V 2 | 14614 | 25533ᵐ | – | – | – | – | none |
| `audi-e-tron-q8` | 2023–2025 ? | 6 (0) | S6 | S6 | D1 S5 | S6 | E6 | 2 pack(s); 6 row(s) no pack; not-disclosed: V 2 | 3298 | 25533ᵐ | 267 | – | 237 | 233 | none |
| `audi-q4-e-tron-gen1` | 2021–now ? | 8 (3) | S6 –2 | S8 | D3 S5 | D1 S7 | E6 –2 | 2 pack(s); 5 row(s) no pack; 5 row(s) no platform; not-disclosed: V 2 | 22022 | 64323 | 11776 | 11852 | 6493 | 5369 | none |
| `mercedes-eqa-h243` | 2021–now ? | 5 (2) | S4 –1 | S4 M1 | S4 M1 | S4 M1 | E4 –1 | 1 pack(s); 3 row(s) no pack; 3 row(s) no platform; not-disclosed: gross 1, V 1 | 7835 | 36944 | 9687 | 4556 | 3740 | 3613 | FR 2 |
| `mercedes-eqc-n293` | 2019–2023 ? | 1 (1) | –1 | S1 | S1 | S1 | –1 | 1 pack(s); not-disclosed: gross 1, V 1 | 2385 | 18223 | – | – | – | – | none |
| `jaguar-i-pace-x590` | 2018–2024 ? | 2 (1) | S1 –1 | D1 S1 | D1 S1 | D1 S1 | E1 –1 | 1 pack(s); 1 row(s) no pack; 1 row(s) no platform; not-disclosed: V 1 | 2811 | 28401 | – | – | – | – | none |
| `dacia-spring-gen1` | 2021–now ? | 6 (3) | D1 S2 –3 | D1 S2 M3 | S3 M2 –1 | S3 M3 | E3 –3 | 1 pack(s); 3 row(s) no pack; 3 row(s) no platform; not-disclosed: gross 1, V 1, chem 1, cell 1, cooling 1 | 6567 | 7739 | 5316 | 9392 | 7636 | 2240 | none |
| `smart-eq-fortwo-451` | 2012–2015 ? | 1 (1) | –1 | E1 | M1 | –1 | –1 | 1 pack(s); not-disclosed: usable 1, V 1, chem 1, cooling 1 | 8 | 4942ᵐ | – | – | – | – | none |
| `smart-eq-fortwo-453` | 2017–2024 ? | 1 (1) | –1 | S1 | S1 | S1 | –1 | 1 pack(s); not-disclosed: usable 1, V 1, chem 1, cooling 1 | 1594 | 4942ᵐ | – | – | – | – | none |
| `honda-e-gen1` | 2020–2024 ? | 2 (2) | –2 | E2 | M2 | M2 | –2 | 1 pack(s); not-disclosed: usable 1, V 1, chem 1 | 329 | 2064 | – | – | – | – | none |
| `mini-cooper-se-f56` | 2020–2023 | 2 (1) | S1 –1 | S1 M1 | S1 M1 | S1 M1 | E1 –1 | 1 pack(s); 1 row(s) no pack; 1 row(s) no platform; not-disclosed: V 1 | 7837 | 36640ᵐ | – | – | – | – | none |
| `mini-cooper-se-j01` | 2024–now | 1 (0) | S1 | S1 | S1 | S1 | E1 | 2 pack(s); 1 row(s) no pack; not-disclosed: V 2, chem 2, cooling 2 | 4687 | 36640ᵐ | – | – | 3479 | 766 | none |
| `cupra-born-gen1` | 2021–now ? | 5 (3) | S2 –3 | D1 S3 M1 | D1 S3 M1 | S4 M1 | E2 –3 | 3 pack(s); 2 row(s) no pack; 2 row(s) no platform; not-disclosed: V 3 | 9728 | 31456 | 18847 | 14257 | 5149 | 874 | none |
| `byd-atto-3-gen1` | 2022–now ? | 5 (1) | S4 –1 | S4 M1 | S4 M1 | S4 M1 | E4 –1 | 1 pack(s); 4 row(s) no pack; 4 row(s) no platform; not-disclosed: usable 1, V 1 | 4238 | 11015 | 1077 | 2677 | 633 | 116 | none |
| `volvo-xc40-recharge-gen1` | 2020–2023 ? | 5 (3) | S2 –3 | S3 M2 | D1 S2 M2 | D1 S2 M1 –1 | E2 –3 | 2 pack(s); 2 row(s) no pack; 2 row(s) no platform; not-disclosed: V 2 | 15764 | 22458ᵐ | – | – | – | – | none |
| `volvo-xc40-recharge-ex40` | 2024–now ? | 2 (0) | S2 | S2 | D1 S1 | S2 | E2 | 2 pack(s); 2 row(s) no pack; not-disclosed: V 2 | 15676 | 22458ᵐ | 2641 | 3059 | 1682 | 2941 | none |
| `ford-mustang-mach-e-gen1` | 2021–now ? | 7 (4) | S4 –3 | D2 S5 | D3 S4 | D2 S5 | E4 –3 | 2 pack(s); 3 row(s) no pack; 3 row(s) no platform; not-disclosed: V 2 | 7305 | 15350 | 564 | 591 | 368 | 814 | none |
| `citroen-e-c4-c41` | 2020–now ? | 3 (2) | S1 –2 | D1 M2 | D1 M2 | D1 M2 | E1 –2 | 2 pack(s); 1 row(s) no pack; 1 row(s) no platform; not-disclosed: V 2 | 6498 | 8459 | 447 | 200 | 2836 | 92 | none |

## Part 1b: model-specific gaps

Only what is visible in the source records. Counts = cars (registrations), "rec" = source records. Shared gaps from the section above are not repeated.

| Model | Gap | Evidence in source records | Could fill it | Releasable today? |
|---|---|---|---|---|
| Tesla Model 3 | gen1 WLTP 0/4 | No OpenEV record before 2023 | `rdw` brandstof, `eea` back years | ✅ adapter work |
| | Highland: 3 rows without a pack | Generation default lists 2 pack options | OpenEV gross kWh/chemistry; `maker-docs` | ✅ partly |
| | Cars outside the generation years | RDW 2017–2018: 12 cars (gen1 starts 2019) | `rdw` first-registration years, `wikidata` | ✅ |
| | ADEME records not placed | `TESLA|MODEL 3` 4 rec: no year, 2 generations | ADEME has no year: needs a name rule | n/a (matcher) |
| Tesla Model Y | gen1: 1 row without pack or platform | — | `variant_links.yaml` entry | n/a (seed) |
| | Variant tie | KilowattApp `MODEL Y` 2022: Long Range vs Long Range RWD (2 rec) | name rule | n/a (matcher) |
| | Cars outside the years | 2020: RDW 3 cars, KilowattApp 2 rec | `rdw`, `wikidata` | ✅ |
| | Juniper: 3 rows without a pack | Generation default lists 2 options | OpenEV; `maker-docs` | ✅ partly |
| Tesla Model S | gen1/facelift WLTP 0/7 | NEDC era | `rdw` brandstof (if filled) | ✅ adapter work |
| | 2016 shared year | RDW: 964 cars not placed (`TESLA MOTORS|MODEL S` 960 + 4) | `rdw` TGK type-approval keys (fields unchecked) | ✅ probably |
| | 2012 cars | RDW 2 cars, KilowattApp 5 rec (gen1 starts 2013) | `rdw`, `wikidata` | ✅ |
| | Variant evidence | KilowattApp: 8 rec (gen1) + 2 rec (facelift) without name/kWh match | name rules | n/a |
| | Usable kWh not disclosed | 5 packs (60/75/85/90/100) | `nyland` | ⏳ |
| Renault Zoe | 2019 shared year | RDW: 2720 cars not placed | `rdw` TGK keys | ✅ probably |
| | End year (seed: 2024) | 2025: EEA 39, KBA 7, RDW 2 cars | `rdw`, `eea` | ✅ |
| | ph1 WLTP 0/5, real range 0/5; ph2 WLTP seed-only 2/2 | NEDC era for ph1 | `rdw` brandstof, `eea` | ✅ adapter work |
| | Variant tie | KilowattApp 2013/2015: Q210 vs R240 (2 rec) | name rule | n/a |
| Renault Megane E-Tech | 2 rows without pack or platform | — | `variant_links.yaml` | n/a (seed) |
| | WLTP 2/4 | ADEME `MEGANE` 8 rec: no variant evidence | ADEME name rule; `rdw`, `eea` | ✅ |
| Nissan Leaf | **gen3 has no rows** | Counts exist: RDW 2026 264, KBA 2025 7 / 2026 719, EEA DE 2025 26. No OpenEV/KilowattApp/ADEME record for 2025+ | `eea` + `rdw` brandstof specs (adapter work); next OpenEV/KilowattApp refresh | ✅ adapter work |
| | ze1 WLTP 2/4 seed-only | ADEME `LEAF` 62 kWh: tie between 2 variants (2 rec) | name rule | n/a |
| VW e-Golf | 2017 shared year | RDW: 823 cars not placed (`GOLF` 817, `E-GOLF` 1, `VW GOLF` 5) | `rdw` TGK keys, battery size from brandstof | ✅ probably |
| | mk7 WLTP missing, pack usable kWh not disclosed | NEDC era | `nyland` | ⏳ |
| VW ID.3 | **EEA make alias** | EEA `VOLKSWAGEN, VW` 2025: DE 31978, BE 3235 cars unplaced (DE shows `–`, BE shows 4) | add EEA make alias | ✅ (alias) |
| | 2 rows without pack or platform | — | `variant_links.yaml` | n/a |
| | Variant tie | KilowattApp 2023: Pro vs Pro S | name rule | n/a |
| VW ID.4 | **EEA make alias** | EEA `VOLKSWAGEN, VW` 2025: DE 21769, BE 5300 unplaced | add alias | ✅ |
| | **Start year (seed: 2021)** | RDW 2020: 2830 cars (`ID.4 PRO 150 KW`); KilowattApp 1 rec | `rdw` | ✅ |
| | KBA count includes ID.5 | Seed note: KBA row is `ID.4, ID.5` | VW ID.5 as its own model (see Part 2) | ✅ |
| Hyundai Ioniq Electric | WLTP: 1 seed-only, 1 missing; usable kWh not disclosed (2 packs); chemistry unset | KilowattApp 2016/2019: 2 rec without evidence | `rdw` brandstof, `eea`; `nyland` | ✅ / ⏳ |
| | Name collision (OK) | DfT `HYUNDAI IONIQ` = Ioniq 9 (973 cars), correctly excluded. `IONIQ 3` (KBA 2026 438, RDW 122) is a new model, not in the seed | — | — |
| Hyundai Kona Electric | 2023 shared year | RDW: 1743 cars not placed (`KONA` 1667, `KONA, KAUAI` 76) | `rdw` TGK keys | ✅ probably |
| | OS: WLTP 0/2, real range 0/2; SX2: 2 rows without pack | KilowattApp `KONA ELECTRIC 48 KWH` no evidence | `rdw`, `eea`; OpenEV gross kWh | ✅ |
| Hyundai Ioniq 5 | kWh/AC/DC seed-only on 5/8 rows; WLTP 3/8 | KilowattApp 2021: 3 rec without variant evidence | OpenEV (2023+), `rdw`, `eea` | ✅ |
| | 3 rows without pack; usable kWh not disclosed on 3 packs | — | `nyland` | ⏳ |
| Hyundai Ioniq 6 | kWh/AC seed-only 3/6; WLTP 3/6; 3 rows without pack | No KilowattApp record matched | OpenEV, `rdw`, `eea` | ✅ |
| Kia Soul EV | **End year (SK3, seed: 2022)** | Still registered: RDW 2023–2025 197, EEA 2025 49, KBA 2025 34 + 2026 6 | `rdw`, `eea`, `wikidata` | ✅ |
| | 2019 shared year | RDW: 217 cars not placed | `rdw` TGK keys | ✅ probably |
| | WLTP 0/4 | ADEME `SOUL` 2 rec: no year | `rdw`, `eea` | ✅ adapter work |
| Kia Niro EV | 2022 shared year | RDW: 3946 cars not placed | `rdw` TGK keys | ✅ probably |
| | SG2: kWh/AC/DC seed-only (1/1), WLTP missing | ADEME `NIRO` 6 rec: no year. No KBA `NIRO` row in 2026 | OpenEV, `ademe` name rule, `eea` | ✅ |
| Kia EV6 | WLTP 3/4; usable kWh not disclosed on 2 packs; all 4 links uncertain | ADEME `EV6` 2 rec: no variant evidence | `rdw`, `eea`; `maker-docs` | ✅ / ⛔ |
| BMW i3 | **Missing generation (new i3)** | "Year outside every generation": EEA 2025 119 (`I3 50 XDRIVE` 93, `I3 40 XDRIVE` 22, `I3 40L` 4), RDW 2026 210, KBA 2026 1 | needs a new seed generation; specs from `eea`/`rdw` brandstof or the next OpenEV refresh | ✅ (counts) |
| | i01 WLTP 0/4; nominal V not disclosed on 3 packs | NEDC era for most years | `rdw` brandstof | ✅ adapter work |
| BMW i4 | 1 row without pack or platform | — | `variant_links.yaml` | n/a |
| Peugeot e-208 | 2 rows without pack; WLTP 2/4 | ADEME `208` 3 rec + KilowattApp `E-208` 2 rec without variant evidence; RDW 2012–2017 5 cars (outside years) | name rules; `rdw`, `eea` | ✅ |
| Peugeot e-2008 | 2 rows without pack; WLTP 2/4 | ADEME `2008` 4 rec + KilowattApp `E-2008` 4 rec without evidence; RDW 2016/2019 3 cars | name rules; `rdw`, `eea` | ✅ |
| Opel Corsa-e | **kWh/AC/DC seed-only 2/2, WLTP 0/2** | No OpenEV match. KilowattApp `OPEL / VAUXHALL|CORSA-E` 1 rec and ADEME `CORSA` 4 rec without evidence | name rules; `rdw`, `eea` | ✅ |
| Fiat 500e | 312: WLTP missing, usable kWh not disclosed; 332: 4 rows without pack | ADEME `500` 4 rec: no year; RDW 2010–2012 8 cars (outside years) | ADEME name rule; `rdw` | ✅ |
| Skoda Enyaq | 3 rows without pack; WLTP 5/7 | KilowattApp ties: 5 rec (60 vs 80; 80x vs 85 vs RS) | name rules | n/a |
| MG4 | **WLTP 0/4** | **OpenEV make `MG Motor` not mapped: 15 MG4 records (2023–2025) lost** | add OpenEV make alias | ✅ (alias) |
| | Name collision (OK) | `MG4 Urban` is separate: DfT 2101, KBA 2026 1086 | candidate new model | — |
| MG ZS EV | WLTP 0/3; usable kWh not disclosed (3 packs); 1 row estimate-only kWh | KilowattApp `ZS EV` 2022: 2 rec without evidence; RDW `ROEWE ZS EV` 5 + `ZS1` 1 car | name rules; `rdw`, `eea` | ✅ |
| Polestar 2 | kWh/AC/DC seed-only 4/9; 5 rows without pack | — | OpenEV (2023+), `rdw` | ✅ |
| Audi e-tron / Q8 e-tron | GE WLTP 0/3; Q8 6 rows without pack | Q8 generation default lists options | `rdw`, `eea`; OpenEV | ✅ |
| | Start year (GE, seed: 2019) | RDW 2018: 644 cars | `rdw` | ✅ |
| | End year (Q8, seed: 2025) | KBA 2026 3, RDW `SQ8 SPORTBACK E-TRON` 2026 1 | `rdw`, `kba-fz10` | ✅ |
| | Variant names | KilowattApp `ETRON 35/40/45`, `SQ8 E-TRON (SPORTBACK)`: ties or no evidence (8 rec) | name rules | n/a |
| | Name collision (OK) | e-tron GT correctly excluded (DfT 5470, RDW 689, KBA 1767): candidate new model | — | — |
| Audi Q4 e-tron | 5 rows without pack; WLTP 6/8 | EEA make `AUDI AG` 14 cars unplaced; KilowattApp ties 4 rec | alias + name rules | ✅ |
| Mercedes EQA | 3 rows without pack | RDW 2020 8 cars (outside years); EEA/RDW `GLA 250+` / `GLA 350 4MATIC (WITH EQ TECHNOLOGY)` names (about 30 cars) unclear whether EQA | review queue; `rdw` TGK | ✅ |
| Mercedes EQC | WLTP 0/1; **end year (seed: 2023)** | RDW 2024–2025 42, EEA 2025 10 cars | `rdw`, `eea` | ✅ |
| | Not an EQC (OK) | KBA `GLK, GLC` 2026 11772: a GLC-series BEV, not EQC 🟡 | — | — |
| Jaguar I-Pace | WLTP 1/2; **end year (seed: 2024)** | EEA 2025 43, RDW 2025 4; KilowattApp 2020 no evidence | `rdw`, `eea` | ✅ |
| Dacia Spring | 3 rows without pack; pack chemistry/cell/cooling not disclosed | RDW 2020 17 cars (seed starts 2021); ADEME + KilowattApp 1 rec each without evidence | OpenEV chemistry; `maker-docs` | ✅ / ⛔ |
| Smart EQ fortwo | 451: kWh estimate-only, AC seed-only, DC and WLTP missing; 453: WLTP missing | — | `rdw` brandstof; `nyland` | ✅ / ⏳ |
| | **RDW/KBA aliases** | RDW `FORTWO COUPE ED` 105, `FORTWO CABRIO ED` 52, `SMART FORTWO` 13, `FORTWO ELECTRIC` 1; KBA `FORTWO` 7 + 5 unplaced | add `rdw`/`kba-fz10` source aliases | ✅ |
| | End year (453, seed: 2024) | EEA 2025: 8 cars | `eea` | ✅ |
| | Forfour missing | RDW `FORFOUR ED`/`SMART FORFOUR` 180, DfT 111, KBA 1, KilowattApp 8 rec | candidate new model or generation | ✅ |
| Honda e | kWh estimate-only 2/2, AC/DC seed-only 2/2, WLTP 0/2 | No OpenEV/KilowattApp match (KilowattApp `E` 2020 and ADEME `E` 4 rec without evidence); EEA 2025 3 cars outside years | name rules; `rdw`, `eea` | ✅ |
| | Name collision (OK) | DfT GenModel `HONDA E` holds the e:Ny1 (`ENY1 ADVANCE/ELEGANCE`, 6800 cars); RDW 164, KBA 160 | candidate new model | — |
| Mini Cooper SE / E | **J01 has no DE count** | KBA has a single `MINI` series: 15495 (2025), 17209 (2026 YTD) | KBA can't split it; DE split by model needs `kba` FZ4/FZ2 (blocked) or EEA DE (J01 EEA DE 6570 is present) | ⛔ / ✅ EEA |
| | UK JCW Electric | DfT `MINI JOHN COOPER WORKS|JOHN COOPER WORKS ELECTRIC` 645 unplaced | `dft-veh` source alias | ✅ |
| | Start year (F56, seed: 2020) | RDW `COOPER SE` 2019: 159 cars | `rdw` | ✅ |
| | Variant ties | KilowattApp `COOPER E/SE` 2020–2023: 4 rec | name rules | n/a |
| Cupra Born | 2 rows without pack; WLTP 2/5 | — | OpenEV, `rdw`, `eea` | ✅ |
| BYD Atto 3 | 4 rows without pack; 1 seed variant only | KilowattApp 2022: tie 60 kWh vs Extended Range | name rule | n/a |
| Volvo XC40 / EX40 | gen1 2 + EX40 2 rows without pack; gen1 WLTP 2/5 | RDW 2018–2019 4 cars (`XC40 T5 AWD`, `XC40 TWIN78AWD SPORT`) outside years | `rdw` | ✅ |
| | Sister model missing | C40/EC40 not in seed: RDW 6458, DfT 7806 | candidate new model | ✅ |
| Ford Mustang Mach-E | 3 rows without pack; WLTP 4/7 | KilowattApp ties SR vs ER, GT vs Premium (5 rec); RDW 2020 16 cars | name rules; `rdw` | ✅ |
| Citroen e-C4 | kWh/AC/DC seed-only 2/3; 1 row without pack; WLTP 1/3 | ADEME `C4` + `C4 X` 4 rec without evidence (ë-C4 X may need its own variants) | OpenEV, ADEME name rule, `rdw` | ✅ |

"n/a (matcher)" / "n/a (seed)" = not a missing source. The record is staged; it needs a seed link, a source alias or a name rule (Q-021 source-scoped aliases would cover the alias rows).

## Part 2: the 20 largest BEV models not in the seed (NL, DE, UK)

The ranking uses each model's **average share** of three totals: NL fleet (922990), UK fleet (2015027) and DE new BEV registrations 2025 (540884). Fleet and new-registration counts are never added. All counts are cars, from records the matcher left unplaced. "Spec records" = unmatched staged spec records per source (records, not cars).

| # | Model (not in seed) | NL fleet (RDW) | UK fleet (DfT) | DE new 2025 (KBA) | DE new 2026 YTD (KBA) | EEA new 2025 NL / DE / FR / BE | Spec records: OpenEV / KilowattApp / ADEME | Why unmatched |
|---|---|---|---|---|---|---|---|---|
| 1 | VW ID.7 | 7706 | 12975 | 34563 | 26048 | 3613 / 34547 / 899 / 4550 | 4 / 7 / 0 | model not in seed (62 rec), make not in seed (19 rec) |
| 2 | Skoda Elroq | 18129 | 17342 | 25426 | 34441 | 11914 / 25421 / 8042 / 3955 | 0 / 3 / 0 | model not in seed (41 rec) |
| 3 | BMW iX1 | 15333 | 21401 | 18957 | 20534 | 4298 / 19041 / 8962 / 9145 | 4 / 2 / 0 | model not in seed (44 rec) |
| 4 | Kia EV3 | 16626 | 18143 | 9205 | 8261 | 10929 / 9199 / 3986 / 4110 | 0 / 1 / 0 | model not in seed (13 rec) |
| 5 | Volvo EX30 | 20436 | 24093 | 4749 | 6650 | 5263 / 4748 / 2891 / 3648 | 12 / 6 / 0 | model not in seed (51 rec) |
| 6 | Audi Q6 e-tron | 5456 | 20309 | 13571 | 15978 | 2657 / 13586 / 6226 / 5991 | 5 / 8 / 0 | model not in seed (101 rec), make not in seed (8 rec) |
| 7 | Ford Explorer EV | 5868 | 22058 | 10913 | 9854 | 3116 / 10895 / 2488 / 2043 | 2 / 3 / 0 | model not in seed (23 rec) |
| 8 | Cupra Tavascan | 2617 | 8929 | 14036 | 13214 | 1408 / 14035 / 2126 / 949 | 4 / 3 / 0 | model not in seed (18 rec), make not in seed (2 rec) |
| 9 | Renault 5 E-Tech | 9606 | 15966 | 7884 | 8202 | 4993 / 7882 / 40836 / 1804 | 6 / 3 / 0 | model not in seed (26 rec) |
| 10 | Audi A6 e-tron | 3278 | 4177 | 13778 | 17167 | 2411 / 12319 / 994 / 1870 | 4 / 6 / 0 | model not in seed (65 rec), make not in seed (1 rec) |
| 11 | Mercedes EQB / GLB | 5795 | 22410 | 7318 | 8911 | 1714 / 7315 / 2797 / 5180 | 18 / 4 / 2 | model not in seed (74 rec) |
| 12 | Hyundai Inster | 6969 | 6017 | 10064 | 11462 | 3627 / 10064 / 3629 / 413 | 0 / 2 / 0 | model not in seed (14 rec) |
| 13 | BMW i5 | 4103 | 10202 | 10476 | 8130 | 1318 / 10525 / 368 / 3030 | 4 / 6 / 0 | model not in seed (47 rec) |
| 14 | BMW iX3 | 11527 | 20580 | 1967 | 11055 | 212 / 2485 / 307 / 879 | 4 / 2 / 0 | model not in seed (44 rec), make not in seed (1 rec) |
| 15 | VW ID. Buzz | 2323 | 9388 | 8564 | 9421 | 524 / 8590 / 1020 / 1243 | 6 / 8 / 0 | model not in seed (102 rec), make not in seed (24 rec) |
| 16 | Opel/Vauxhall Mokka-e | 5761 | 23850 | 1985 | 1955 | 286 / 1985 / 1627 / 167 | 0 / 1 / 4 | model not in seed (35 rec) |
| 17 | BMW iX | 2968 | 20105 | 4337 | 3604 | 353 / 4348 / 343 / 1310 | 14 / 6 / 0 | model not in seed (92 rec) |
| 18 | Toyota bZ4X | 4628 | 13290 | 5005 | 4014 | 878 / 5010 / 1228 / 1108 | 6 / 1 / 0 | make not in seed (32 rec) |
| 19 | Porsche Taycan | 3984 | 22754 | 2799 | 1800 | 135 / 2808 / 247 / 311 | 14 / 16 / 24 | make not in seed (176 rec) |
| 20 | Citroen e-C3 | 6427 | 6257 | 5367 | 12521 | 3494 / 5368 / 21606 / 1332 | 0 / 2 / 0 | model not in seed (31 rec) |

KBA series mapped by me 🟡: BMW `X1` → iX1, `X3` → iX3, `5ER` → i5, `IX` → iX; Mercedes `GLB` → EQB/GLB, `CLA-KLASSE` → CLA; `SEAT|TAVASCAN` → Cupra Tavascan; `CITROEN|C3` → ë-C3; `AUDI|A6` → A6 e-tron (all read from the BEV column). The BMW iX3 and Mercedes EQB/GLB rows may mix two generations (old iX3 and the 2025+ iX3; EQB and the new electric GLB). That split needs RDW/EEA names, not KBA. The ID.5 has no KBA row of its own (it sits inside the seed's ID.4 row).

**Which sources cover them (all 20):** registrations from `rdw` (NL fleet), `dft-veh` (UK fleet), `kba-fz10` (DE new) and `eea` (NL/DE/FR/BE new 2025) are all **active, so releasable today**. Specs: `openev` and/or `kilowatt-openev` (active) for every model listed. Skoda Elroq, Kia EV3, Hyundai Inster and Citroen e-C3 only have 1–3 KilowattApp records and no OpenEV record. `ademe` (active) also covers Mokka-e, EQB and Taycan. WLTP and Wh/km could also come from `eea`/`rdw` (adapter extension). Pack, voltage and platform: `maker-docs` (blocked). Real range: waiting-permission sources only.

**Used-market staples also not in the seed** (fleet only, so they rank low on DE new registrations): BMW iX3 incl. the old G08 (NL 11521 / UK 20580), Volvo C40/EC40 (6458 / 7806), Nissan Ariya (2275 / 14451), Mercedes EQE (3654 / 8327), Tesla Model X (4665 / 5947), VW e-up! (4788 / 3065), Mazda MX-30 (2696 / 4906), Opel Ampera-e (2648 / 0), Seat Mii electric (2026 / 1332), Skoda Citigo-e (2278 / 317), Mercedes EQV (1640 / 964), Lexus UX 300e (268 / 3587), Audi e-tron GT (RDW 689 / DfT 5470 under GenModel `AUDI E-TRON`), Smart forfour EQ (180 / 111). Counts: RDW (NL) / DfT (UK), names as matched by pattern.

**Ranks 21–30** (same method): Mercedes CLA EV, Porsche Macan Electric, Renault Scenic E-Tech, Mercedes EQE, Ford Puma Gen-E, BYD Dolphin (incl. Surf), Polestar 4, Opel/Vauxhall Frontera, BYD Seal, BMW iX2.

## Suggested next steps (for the coordinator, not done here)

1. Add the three make aliases (EEA `VOLKSWAGEN, VW`, `AUDI AG`; OpenEV `MG Motor`), plus smart/Mini source aliases. Cheapest fix, and it recovers about 62000 DE/BE registrations and 15 MG4 spec records.
2. Extend the `rdw` adapter: brandstof WLTP + Wh/km, `catalogusprijs`, and TGK keys for the shared-year tie-breaks (about 10400 NL cars).
3. Extend `eea`: specs plus back years. Fetch older KBA FZ10 files so DE/FR/BE counts reach the older generations.
4. Fix seed years: ID.4 start, e-tron GE start, Mini F56 start, Soul SK3 / Zoe / EQC / I-Pace end years, plus a new BMW i3 generation. Check each against `rdw` first-registration years and `wikidata` before editing.
5. Seed expansion wave: the top 10 of Part 2 first (ID.7, Elroq, iX1, EV3, EX30, Q6 e-tron, Explorer, Tavascan, Renault 5, A6 e-tron).
