# R-23 VIN and plate lookup: what the VIN tells us, RDW open data, and privacy

Researched 2026-11-15 by a WS1/WS3 researcher agent for T-049 (spec `docs/spec/variant-finder.md` §2 features 4–5, §6). **Not legal advice.** Confidence: 🟢 official/primary source opened · 🟡 secondary source or my own inference from a primary source · 🔴 unsure / not verified.

## Answer

1. **RDW plate → exact variant works, and it's free and open.** 🟢
   - `Gekentekende_voertuigen` (m9d7-ebf2) gives, per plate, `typegoedkeuringsnummer` + `variant` + `uitvoering`.
   - Those three fields join exactly onto the TGK type-approval tables: base, drive, energy source and manufacturer trade name.
   - Tested live on a 2024 Tesla Model 3.
   - The licence is CC0 per RDW's own page and data.overheid.nl. The Socrata metadata says "Public Domain".
2. **RDW has no battery kWh field anywhere.** 🟢 It does have:
   - motor power (net, 30-min / 15-min)
   - WLTP range and consumption
   - masses and dimensions
   - type-approval code chains

   Battery size has to come from our own variant table, matched on the TGK keys.
3. **⚠️ One licence oddity.** 🟢 RDW's "bijsluiter" says that "as part of CC0" reusers may **not state that the data come from the RDW**, and may not use RDW's logo or house style. This clashes with our "every number has a source" rule.
   - My reading: this is meant as "don't suggest RDW endorses you". That reading is 🔴 unconfirmed.
   - Ask RDW (draft a question for Menno to send) before we show "Source: RDW" in the UI.
   - Until then, label it neutrally ("Dutch vehicle register open data, CC0") and keep full provenance internally. 🟡
4. **Plates and VINs are personal data whenever someone can reasonably link them to a person.** 🟡
   - The CJEU's Scania judgment (C-319/22, 9 Nov 2023) says a VIN is not personal data in itself, but becomes personal data for anyone who "reasonably has means" to link it to a person.
   - A Dutch plate is the same kind of identifier. RDW, police, insurers and the owner can link it, and so can anyone who saw the car.
   - So **design as if it's personal data**: look it up in the browser, never send it to our server, never log or store it. That makes us neither collector nor controller of the plate.
5. **The VIN gives battery size only for a few makes, and only on US-market VINs.**
   - **Battery or pack clue in US filings** 🟢:
     - Nissan Leaf: position 4 = battery (24/30/40/62/60 kWh by model year).
     - Kia EV6: position 5 = "Light (58.0 kWh), Wind (77.4 kWh)", and position 8 = pack voltage + motor.
     - Hyundai Ioniq 5 / Kona Electric: position 8 = pack voltage and Ah + motor kW.
   - **Motor/drive only** 🟢:
     - Tesla: position 8.
     - VW ID.4 and Audi Q4/Q6: position 5, with trim in position 4.
     - Polestar 2/3: positions 4–5.
     - Fiat 500e (US): position 8.
     - BMW i4/iX/i7: positions 4–7 together = the exact model variant.
   - **No public decoding found** 🔴: Renault, Peugeot/Stellantis EU, MG/SAIC, Skoda, Cupra. None of them sells these models in the US, so there's no 49 CFR 565 filing, and the EU has no equivalent public filing that I found.
   - **EU-market VINs** (Berlin/Shanghai Teslas, Sunderland Leafs, EU-spec VW group cars) are **not covered** by the US filings. Treat them as unknown until checked against real EU VINs. 🔴

**Recommendation:**
- Build NL plate lookup as a **client-side call from the browser straight to `opendata.rdw.nl`** (CORS is open: `Access-Control-Allow-Origin: *` 🟢). Use a `$select` that fetches only the type-approval fields.
- Do the TGK joins in the browser, then match against our published variant table, which we ship as a static file.
- Nothing about the plate reaches our server, logs, analytics or URLs. Details in §3.4.
- **VIN:** only use the US 565 patterns as a "strong" clue for US-built/US-market cars. For EU VINs, use only WMI (positions 1–3) and model year (position 10) as weak clues, until a staff member verifies EU patterns against real registration papers.

---

## 1. VIN: which positions encode motor or battery

### 1.1 The rules behind it

- **US (49 CFR 565.15(b)).** Positions 4–8 (the VDS) must make these decipherable for passenger cars: "Make, line, series, body type, engine type, and all restraint devices and their location". For MPVs, GVWR is added. The manufacturer picks which characters go where, but must file the decoding with NHTSA (§565.16(c)). Those filings are public in vPIC. **Battery capacity is not a required attribute.** Some makers include it voluntarily under "engine type". 🟢
- **EU.** I found no rule that makes EU decodings public. VINs follow ISO 3779 (WMI / VDS / VIS). The same model often carries a different VDS, and sometimes a different WMI, on EU-market cars. 🔴 I couldn't verify the specific EU law in this session because the search budget ran out. WS3 follow-up.
- **vPIC decoder fields.** vPIC has EV fields:
  - `BatteryKWh` / `BatteryKWh_to` (variables 59/134)
  - `BatteryType` (2)
  - `BatteryV` (58/133)
  - `EVDriveUnit` (72)
  - `ElectrificationLevel` (126)
  - `ChargerLevel` / `ChargerPowerKW` (127/128)

  🟢 They're filled only when the maker's pattern data includes them. Live partial-VIN tests (2026-11-15):
  - **Kia EV6 2024:** returned `BatteryKWh = 58` to `77.4`.
  - **Tesla Model 3 2023 (pos 8 = B):** returned `EVDriveUnit = Dual Motor` and `BatteryType = Li-Ion`.
  - **Nissan Leaf 2021:** returned *no* kWh, even though Nissan's filing has it.

  So vPIC alone under-reports. 🟢 Use the filings as the source and vPIC as a cross-check.

### 1.2 Per make (top-20 used EVs)

| Make | Market / WMI | Position(s) | What it encodes | Battery? | Source | Conf. |
|---|---|---|---|---|---|---|
| Tesla (S/3/X/Y) | US: 5YJ (S, 3), 7SA (X, Y from MY2023) | 8 | Motor/drive unit, e.g. MY2025: A = Model 3 single motor, B = Model 3 dual standard, T = Model 3 dual performance, D/E/F = Model Y single/dual/dual perf; 5/6 = S/X P2 dual/tri. Pos 7 = fuel (E = electric) | **No** (motor only; codes reused across years, so always read with pos 10) | Tesla 565 filings MY2019, 2021, 2024, 2025 | 🟢 |
| Tesla | EU-built XP7 (Berlin), China-built LRW | ? | Not in any US filing; community decoders don't define them | Unknown | teslatap.com (says VIN can't reveal battery type) | 🔴 |
| Volkswagen ID.4 | US: 1V2 (Chattanooga), WVG (Europe-built for US) | 4 = trim (C = RWD Pro, V = RWD Pro S, D = AWD Pro, W = AWD Pro S, J = AWD Pro S Plus, MY2026); 5 = engine type (R = ID.4 RWD 282 hp, S = AWD 335 hp); 7–8 = E8 (ID.4) | Trim + motor | Not in MY2026. The MY2023 change log mentions separate 62 kWh trims via the 4th character | VWoA 565 MY2026; VWoA 565 MY2023 change log | 🟢 (MY2026) / 🟡 (62 kWh, from change log only) |
| Audi Q4 / Q6 e-tron | US: WA1 (Audi AG Europe MPV) | 4 = trim (Q4 45: A/B; Q4 55 quattro: K/L/M; Sportback 55: 4/2/3); 5 = engine type (Q4 RWD = 5, 282 hp; Q4 quattro = U, 335 hp; Q6 = 2/4, SQ6 = 5) | Trim + motor | No | Audi AG 565 MY2025 | 🟢 |
| VW ID.3, Skoda Enyaq/Elroq, Cupra Born, EU-spec ID.4/Q4 | EU (WVW, WVG, TMB, VSS…) | ? | No public decoding found. Many EU VW group VINs are said to carry filler characters in the VDS (not verified) | Unknown | none opened | 🔴 |
| Hyundai Ioniq 5 | US: KM8, pos 4 = K | 5 = series (M SE, N SEL, R Limited); 6 = body 2WD/4WD; **8 = powertrain: A/B = 653 V or 523 V, 111.2 Ah + RR 168 kW; C/D = same packs + FR 74 kW / RR 165 kW** | Pack voltage/Ah + motors | **Yes, indirectly**: V × Ah ≈ 72.6 vs 58.2 kWh nominal (my arithmetic) | Hyundai 565 MY2022 | 🟢 filing / 🟡 kWh |
| Hyundai Kona Electric | US: KM8, pos 4 = K | 8 = G: "HMC Battery [Li-PB] 356 V, 180 Ah + traction motor 150 kW" (MY2021) | Pack + motor | Yes, indirectly (≈ 64 kWh) | HATCI 565 MY2021 | 🟢 / 🟡 kWh |
| Kia EV6 | US: KND, pos 4 = C | **5 = series: 3 = "Light (58.0 kWh), Wind (77.4 kWh)"**, 4 = GT-Line, 5 = GT; 6 = body 2WD/4WD; **8 = A–E: 111.2 Ah, 697 V or 522.7 V, RR 160 kW / FR 70 + RR 160 / FR 160 + RR 270 kW** | Pack voltage + motors | **Yes**: pos 8 voltage separates 77.4 from 58 kWh (my inference from V × Ah) | Kia 565 MY2024 | 🟢 / 🟡 mapping |
| Hyundai/Kia EU-market (Ioniq 5, Kona, EV6, Niro, e-Soul) | EU WMIs (e.g. KMH, KNA, TMA, U5Y, not checked) | ? | Not in US filings | Unknown | — | 🔴 |
| Nissan Leaf | US: 1N4 (Smyrna, to MY2025); JN1 (Tochigi, MY2026) | **4 = "engine type" = motor + battery**: MY2017 A = 24 kWh, B = 30 kWh; MY2019–22 A = 40, B = 62; MY2023–25 A = 40, C = 60; MY2026 new Leaf A = 75 kWh. Pos 5 = Z (Leaf). The filing writes "BAT:40kw", meaning kWh | **Yes, explicit** | Nissan 565 MY2017, 2021, 2023, 2026 | 🟢 |
| Nissan Leaf (EU, Sunderland) / Ariya EU | EU: SJN etc. (not checked) | ? | Not in US filings | Unknown | — | 🔴 |
| Nissan Ariya | US: JN8 | 4 = motor + battery: filing lists BAT 66 / 91 (kWh) variants | Yes | Nissan 565 MY2026 (layout hard to parse; code letters not extracted) | 🟡 |
| BMW i4 / iX / i7 / i5 | US: WBY (i cars), WB5 / WBX MPV | **Positions 4–7 together = model variant**, e.g. i4 eDrive35 = 4 3 A W, eDrive40 = 7 3 A W, M50 = 3 3 A W (WBY); iX xDrive50 = 2 3 C F (WB5) | Exact variant (motor/power) | Not stated; battery follows from the variant via our table | BMW AG 565 MY2023 | 🟢 variant / 🟡 battery via table |
| BMW i3 | US | Filings exist (MY2018–21, BMW NA) but I didn't parse them | ? | ? | — | 🔴 |
| Polestar 2 / 3 | US/Canada: YSM (Polestar 2), YSR (3) | **4–5 = motor code** (FD = AWD 320 kW, FE = FWD 200 kW, FG = AWD 340 kW; EA/EE = Polestar 3); 6 = 3 (BEV); 7 = model; 8 = trim | Motor/power | No (filing says "long range" for all MY2024 codes) | Polestar 565 MY2024 | 🟢 (US) / 🔴 EU-market VINs |
| Fiat 500e (2024+) | US: ZFA (FCA Italy, Mirafiori) | **8 = engine: 4 = electric 87 kW, 6 = electric 113.7 kW**; 5–7 = brand/series/body | Motor | No | Stellantis Europe 565 MY2024 | 🟢 (US). EU cars also ZFA; same scheme 🔴 unverified |
| Renault (Zoe, Megane E-Tech, Scenic, R5), Dacia Spring | EU only: no US filing | — | No public decoding found | Unknown | — | 🔴 |
| Peugeot e-208/e-2008, Opel Corsa-e, Citroën ë-C4 | EU only | — | No public decoding found | Unknown | — | 🔴 |
| MG4, MG ZS EV, MG5 (SAIC) | EU/UK only | — | No public decoding found | Unknown | — | 🔴 |

**Takeaways for the clue table (spec §3):**
- **Decisive:** Nissan Leaf pos 4 on US VINs; Kia EV6 pos 5 + 8 on US VINs.
- **Strong:** Hyundai pos 8; Tesla pos 8 (separates drive variants, not battery); VW/Audi pos 4–5; BMW pos 4–7; Polestar pos 4–5.
- **Weak (all EU-market VINs):** WMI → maker and plant, pos 10 → model year.
- Positions change meaning between model years: always key patterns on (WMI, model year, position).

## 2. RDW open data

### 2.1 Licence and terms

- **Licence: CC0 1.0.** 🟢
  - RDW bijsluiter: "Op de dataset is de licentie Creative Commons Zero van toepassing."
  - data.overheid.nl lists "CC-0 (1.0)" for 11441 Gekentekende voertuigen.
  - Socrata metadata for every RDW dataset below shows `licenseId: PUBLIC_DOMAIN`.
- **Odd clause** 🟢 (text): "Als onderdeel van Creative Commons Zero is het bij hergebruik niet toegestaan te vermelden dat de gegevens afkomstig zijn van de RDW, en is het niet toegestaan het logo of de huisstijl van de RDW te gebruiken". CC0 itself contains no such rule, so this is RDW's own condition. 🔴 Interpretation and enforceability are unclear. See Answer point 3.
- **Other terms** 🟢:
  - free of charge
  - "Performance vindt plaats op basis van fair use"
  - no availability guarantee
  - RDW may stop a dataset without explanation
  - building services on the data is at the user's own risk
- **Rate limits / app tokens** 🟢 (Socrata docs):
  - Without a token, requests share an IP-based pool with "a much lower throttling limit".
  - With a token, each token gets its own pool and isn't throttled unless abusive.
  - Throttled calls get HTTP 429.
  - No numbers are published.

  **For a client-side lookup that's fine:** each visitor uses their own IP pool. Don't put an app token in browser code. Getting one needs an account, so ask Menno first, and a leaked token "counts against your quota".

### 2.2 Datasets and how they join

Join path:

```
plate → m9d7-ebf2 (typegoedkeuringsnummer, variant, uitvoering)
      → TGK tables on (typegoedkeuringsnummer, codevarianttgk, codeuitvoeringtgk[, volgnummerrevisieuitvoering])
```

Live check (2026-11-15): a 2024 Model 3 had TGK `e4*2007/46*1293*39`, variant `H6LR`, uitvoering `BFB1S5T1W`.

- That matched exactly one row each in byxc-wwua and x5v3-sewk (`handelsbenamingfabrikant = MODEL 3`).
- 4by9-ammk returned motorcode 3D7, electric = J.
- gr7t-qfnb returned codeenergiebron E, 30-min power 88 kW.

🟢 Gotchas:
- In x5v3-sewk the variant column is spelled **`codevariantgk`** (no "t").
- Among passenger cars first admitted after 2020-01-01, 30,659 of 3,285,553 (≈0.9 %) have no `typegoedkeuringsnummer`, e.g. individually approved imports. The finder must fall back to the trade name + kW + date clues.
- The Ioniq 5 sample rows came back without TGK fields in my `$select`. Check coverage per make before promising "exact".

### 2.3 Battery and energy fields

- No dataset has battery capacity (kWh) or battery chemistry. 🟢
- The nearest proxies:
  - net / 30-min / 15-min power
  - WLTP electric range and consumption (min–max per uitvoering in gr7t-qfnb, per plate in 8ys7-d773)
  - mass
  - `massa_alt_aandr` (extra mass for the alternative drive)

### 2.4 Fields to avoid (data minimisation)

m9d7-ebf2 also carries owner-related or history fields:
- `datum_tenaamstelling` (date of last owner registration)
- `tellerstandoordeel` / `jaar_laatste_registratie_tellerstand` (odometer judgement)
- `vervaldatum_apk`
- `wam_verzekerd`
- `export_indicator`
- `openstaande_terugroepactie_indicator`

The finder doesn't need any of them. Always use a `$select` limited to the fields in table (b). 🟡 (design choice)

## 3. Privacy: are plates and VINs personal data?

### 3.1 What I found

- **CJEU C-319/22 *Gesamtverband Autoteile-Handel v Scania* (9 Nov 2023)** 🟡 (law-firm summaries; I couldn't open the judgment text):
  - A VIN is not personal data in itself.
  - It "becomes personal data as regards someone who reasonably has means of enabling that datum to be associated with a specific person".
  - For manufacturers it isn't personal data "where the vehicle … does not belong to a natural person".
  - The test follows *Breyer* (C-582/14): all means reasonably likely to be used, by the controller or anyone else.
- **EDPB Guidelines 1/2020 on connected vehicles** (consultation version, para 28) 🟢: technical vehicle data "by cross-referencing with other files and especially the vehicle identification number (VIN), can be related to a natural person". In the same document, licence plates are treated as identifying data that should be separated from raw telematics data. The EDPB's June 2026 "at a glance" sheet stresses local processing over cloud processing. 🟢
- **RDW** 🟢:
  - Vehicle data are public ("De gegevens over voertuigen zijn gratis door iedereen in te zien").
  - Personal data (name, address of the registered keeper) go only to the keeper and to parties named in law; anyone else needs written consent.
  - The open-data platform is described as "niet gevoelige gegevens".
  - RDW's own feedback form says not to enter "persoonlijke gegevens, zoals uw naam, adres of kenteken". In other words, RDW itself treats a plate as personal input.
- **NL practice** 🟡: Den Haag's privacy notice for parking scan cars gives "een kenteken dat wordt gescand" as an example of personal data. In the Arnhem parking case (Rb. Gelderland ECLI:NL:RBGEL:2023:2969, via Binnenlands Bestuur, 21 Jul 2025) the AP found no GDPR breach, but the processing was still assessed under the GDPR.
- **Autoriteit Persoonsgegevens' own pages:** 🔴 not opened (the site rejected automated requests). The R-04 open question still applies: the lead authority is probably the CNIL, not the AP.

**Conclusion** 🟡: for us, a plate typed by a visitor is very likely personal data. It identifies one car, the visitor may be its keeper or a would-be buyer, and the car can be linked to a person by many parties. The same goes for a VIN. The RDW *catalogue* data (type approvals) is not personal data.

### 3.2 Who processes what in the recommended design

If the browser calls RDW directly, our server never receives the plate. We then don't process it (GDPR art. 4(2)). The visitor's browser talks to RDW/Socrata under RDW's own terms. 🟡 The only thing we serve is static JS and our variant table.

Residual exposure:
- **RDW/Tyler (Socrata, AWS eu-west-1) see the visitor's IP + plate.** Disclose this in the privacy notice: "plate lookups go directly from your browser to the RDW open-data service".
- **Our code must not leak the plate.** That means no URL state, no analytics events, no error reports with the query.

### 3.3 Is a server-side proxy ever needed?

Only if RDW throttling bites, or if CORS changes. In that case:
- proxy with no logging (Caddy `log` off for that route)
- no caching keyed by plate
- in-memory only
- app token kept on the server

Without the proxy we hold nothing. With it we're a controller with a short transient record. Prefer client-side. 🟡

### 3.4 Recommended privacy-safe design (for WS2/WS4)

| # | Rule | Why | Conf. |
|---|---|---|---|
| 1 | The browser fetches `opendata.rdw.nl/resource/m9d7-ebf2.json?kenteken=…&$select=<allow-list>` directly; TGK joins also in the browser | Plate never reaches our server | 🟢 CORS verified |
| 2 | Allow-list `$select` only (table b fields); never request `datum_tenaamstelling`, odometer, APK, insurance or export fields | Data minimisation; no ownership-history signals | 🟡 |
| 3 | Plate never goes in the URL, history state, local storage, share links, Umami events or GlitchTip breadcrumbs; the result may be shared as **variant id only** | Matches the R-04 §6 rules for Trip fit | 🟡 |
| 4 | No hashing "for stats": a hash of a 6-character plate is trivially reversible, so it's still personal data | Hashes ≠ anonymous here | 🟢 (keyspace is small) / 🟡 |
| 5 | Count only "lookup used / matched / not matched" as a no-payload Umami event, if anything | Usage metric without the plate | 🟡 |
| 6 | Client-side debounce (submit button, ≥1 s between lookups); no autocomplete-as-you-type against RDW | Fair use; avoids per-keystroke partial plates leaving the device | 🟡 |
| 7 | Show only type-approval-level facts ("This plate is a Model 3 RWD, type approval …"), never keeper or history data; add a "Not your car? Ask the seller for the plate" note | Purpose limitation; no link to the owner | 🟡 |
| 8 | Privacy notice line + tooltip: "Lookups go straight from your browser to RDW open data. We don't see or keep the plate." | Transparency (art. 13 spirit) | 🟡 |
| 9 | Static `Content-Security-Policy connect-src` adds `https://opendata.rdw.nl` only | Containment | 🟡 |
| 10 | Tests use fixture JSON, never the live API (AGENTS.md) | Rule | 🟢 |
| 11 | VIN input: decode **locally** against our own pattern table (from the 565 filings), no call to vPIC from the browser with the full VIN; send only WMI + positions 4–8 + 10 if a remote check is ever needed. Positions 12–17 (serial) never leave the device | The serial is what identifies one car | 🟡 |

## 4. Open items

| # | Item | Owner | Conf. |
|---|---|---|---|
| 1 | Draft a question to RDW (opendata forum or contact) on the "may not state the data come from RDW" clause; Menno sends it | WS1 drafts, Menno sends | 🔴 |
| 2 | Verify EU-market VIN patterns (Tesla XP7/LRW, VW group EU, Hyundai/Kia EU, Leaf SJN, Polestar EU, Fiat ZFA EU) against real registration-paper samples from staff or partners, never scraped | WS3 | 🔴 |
| 3 | Parse the remaining filings: BMW i3, Nissan Ariya code letters, Hyundai Ioniq 5 MY2023–26, Kia Niro EV, VW ID.4 MY2021–23 (62 kWh trims) | WS3 | 🟡 |
| 4 | Check per-make coverage of `typegoedkeuringsnummer` / `variant` / `uitvoering` for EVs in m9d7-ebf2 | WS1 | 🟡 |
| 5 | Lawyer list (R-03 §6 / R-04 §8 #13): confirm the "client-side lookup = we don't process the plate" reasoning | Menno | 🟡 |
| 6 | The web search budget ran out mid-task: the EU VIN law (Reg. 2018/858 / UNECE / ISO 3779) and AP pages weren't verified; redo in a fresh session | WS0 | 🔴 |

## Sources (all opened 2026-11-15 unless marked)

**VIN**
- 49 CFR 565 (eCFR versioner API, part 565, current to 2026-11-01): https://www.ecfr.gov/api/versioner/v1/full/2026-11-01/title-49.xml?part=565 🟢
- vPIC GetParts (565 filing index): https://vpic.nhtsa.dot.gov/api/vehicles/GetParts?type=565&fromDate=1/1/2017&toDate=11/15/2026&manufacturer=tesla&format=json 🟢
- vPIC variable list: https://vpic.nhtsa.dot.gov/api/vehicles/GetVehicleVariableList?format=json 🟢
- vPIC DecodeVinValues (partial-VIN tests), e.g. https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/KNDC34*RR5?format=json&modelyear=2024 🟢
- Tesla MY2025: https://vpic.nhtsa.dot.gov/mid/home/displayfile/6ce6db08-3e3b-432e-8c4b-8cd7b6bd49f9 🟢
- Tesla MY2024: https://vpic.nhtsa.dot.gov/mid/home/displayfile/9e960dca-5b88-4e55-9c9e-4609dd2ae93a 🟢
- Tesla MY2021: https://vpic.nhtsa.dot.gov/mid/home/displayfile/b523d13b-86a0-41d0-b24e-afbf5aa0c301 🟢
- Tesla MY2019: https://vpic.nhtsa.dot.gov/mid/home/displayfile/08d92abf-3aeb-45ba-ba92-b5ad54b06ff5 🟢
- VW (VWoA) MY2026: https://vpic.nhtsa.dot.gov/mid/home/displayfile/4bb6e581-1ca4-4087-a0fe-583fe6961468 🟢
- VW (VWoA) MY2023 change log: https://vpic.nhtsa.dot.gov/mid/home/displayfile/520e230e-7dc6-4317-ae12-04ee0283f722 🟢
- Audi AG MY2025: https://vpic.nhtsa.dot.gov/mid/home/displayfile/0735db50-6440-461b-8e6b-7e2af6168b49 🟢
- Hyundai Ioniq 5 MY2022: https://vpic.nhtsa.dot.gov/mid/home/displayfile/28cb9a74-b467-423d-9787-0a352dc6e87c 🟢
- Hyundai Kona Electric MY2021: https://vpic.nhtsa.dot.gov/mid/home/displayfile/2caa4b11-5fca-4a69-a90d-082be660486b 🟢
- Kia EV6 MY2024: https://vpic.nhtsa.dot.gov/mid/home/displayfile/5a21ba6b-7d21-46a6-8159-358df4497a65 🟢
- Nissan MY2017: https://vpic.nhtsa.dot.gov/mid/home/displayfile/890f439d-5613-4c5b-8a36-1912d86be216 🟢
- Nissan MY2021: https://vpic.nhtsa.dot.gov/mid/home/displayfile/15c5f14e-2cdf-4160-a931-10f601780cca 🟢
- Nissan MY2023: https://vpic.nhtsa.dot.gov/mid/home/displayfile/2384a939-6a24-4fa0-bc54-2d2f579e8018 🟢
- Nissan MY2026: https://vpic.nhtsa.dot.gov/mid/home/displayfile/033e4f3a-4ac8-4f78-a279-c672b1c710df 🟢
- BMW AG MY2023: https://vpic.nhtsa.dot.gov/mid/home/displayfile/0fc2c1f0-7f69-4002-bf4e-298b1bc45622 🟢
- Polestar MY2024: https://vpic.nhtsa.dot.gov/mid/home/displayfile/2bc18620-e40e-4c6b-905c-1d7b204dbeb7 🟢
- Stellantis Europe (Fiat 500e) MY2024: https://vpic.nhtsa.dot.gov/mid/home/displayfile/74d29bda-da87-4554-874c-1f2412264fdb 🟢
- TeslaTap VIN decoder (community): https://teslatap.com/vin-decoder/ 🟡

**RDW**
- RDW bijsluiter (licence, fair use, attribution clause): https://www.rdw.nl/over-rdw/dienstverlening/open-data/bijsluiter 🟢
- data.overheid.nl, 11441 Gekentekende voertuigen (CC-0 1.0): https://data.overheid.nl/dataset/11441-open-data-rdw--gekentekende-voertuigen 🟢
- Socrata metadata + live queries:
  - https://opendata.rdw.nl/api/views/m9d7-ebf2.json
  - …/8ys7-d773.json
  - …/byxc-wwua.json
  - …/4by9-ammk.json
  - …/gr7t-qfnb.json
  - …/x5v3-sewk.json
  - …/kyri-nuah.json
  - …/7ug8-2dtt.json
  - resource endpoints `https://opendata.rdw.nl/resource/<id>.json` 🟢
- RDW dataset catalogue: https://opendata.rdw.nl/api/catalog/v1?limit=200&only=datasets 🟢
- RDW, "Gegevens die de RDW registreert": https://www.rdw.nl/over-rdw/privacy-en-security/privacyverklaring/gegevens-die-de-rdw-registreert 🟢
- Socrata app tokens and throttling: https://dev.socrata.com/docs/app-tokens 🟢
- Socrata throttling clarification (2016): https://dev.socrata.com/changelog/2016/06/04/clarification-of-throttling-limits 🟢

**Privacy**
- Matheson on CJEU C-319/22: https://www.matheson.com/insights/detail/cjeu-considers-whether-vehicle-identification-numbers-constitute-personal-data 🟡
- Van Bael & Bellis on C-319/22: https://vbb.com/insights/cjeu-reiterates-relative-nature-of-what-is-personal-data-in-case-on-access-to-vehicle-spare-part-i 🟡
- EDPB Guidelines 1/2020 connected vehicles (consultation version): https://edpb.europa.eu/sites/default/files/consultation/edpb_guidelines_202001_connectedvehicles.pdf 🟢
- EDPB "Guidelines at a glance: connected vehicles & mobility data" (June 2026): https://www.edpb.europa.eu/system/files/2026-11/edpb-guidelines-at-a-glance-connected-vehicles-mobility-data_en.pdf 🟢
- Gemeente Den Haag, privacy notice for parking scan cars: https://www.denhaag.nl/nl/privacyverklaringen/privacyverklaring-parkeercontrole-met-scanvoertuigen/ 🟡
- Binnenlands Bestuur, "Gratis parkeren op kenteken inbreuk op privacy?" (21 Jul 2025): https://www.binnenlandsbestuur.nl/juridisch/gratis-parkeren-op-kenteken-inbreuk-op-privacy 🟡

**Tried, not retrieved:**
- opendata.rdw.nl home page and autoriteitpersoonsgegevens.nl "wat zijn persoonsgegevens": WebFetch permission not granted; the AP site also rejected curl.
- EUR-Lex text of C-319/22: empty response.
- raadvanstate.nl 202304226: site error.
- EDPB final v2.0 connected-vehicles PDF: 404 at the guessed path.

---

## Ready-to-import tables

### (a) vin_patterns

| make | market | wmi | position | meaning | values | source_url | retrieved_at | confidence |
|---|---|---|---|---|---|---|---|---|
| Tesla | US | 5YJ;7SA | 8 | motor/drive unit (MY2025) | A=M3 single std/perf; B=M3 dual std; T=M3 dual perf; D=MY single; E=MY dual std; F=MY dual perf; 5=S/X P2 dual; 6=S/X P2 tri | https://vpic.nhtsa.dot.gov/mid/home/displayfile/6ce6db08-3e3b-432e-8c4b-8cd7b6bd49f9 | 2026-11-15 | green |
| Tesla | US | 5YJ;7SA | 8 | motor/drive unit (MY2024) | same as MY2025 | https://vpic.nhtsa.dot.gov/mid/home/displayfile/9e960dca-5b88-4e55-9c9e-4609dd2ae93a | 2026-11-15 | green |
| Tesla | US | 5YJ | 8 | motor/drive unit (MY2021) | 1=S single std; 3=S single perf; 2=S/X dual std; 4=S/X dual perf; 5=S/X P2 dual; 6=S/X P2 tri; A=M3 single; B=M3 dual std; C=M3 dual perf; D=MY single; E=MY dual std; F=MY dual perf | https://vpic.nhtsa.dot.gov/mid/home/displayfile/b523d13b-86a0-41d0-b24e-afbf5aa0c301 | 2026-11-15 | green |
| Tesla | US | 5YJ | 8 | motor/drive unit (MY2019) | 1=S single std; 3=S single perf; 2=S/X dual std; 4=S/X dual perf; A=M3 single; B=M3 dual | https://vpic.nhtsa.dot.gov/mid/home/displayfile/08d92abf-3aeb-45ba-ba92-b5ad54b06ff5 | 2026-11-15 | green |
| Tesla | US | 5YJ;7SA | 7 | fuel type | E=electric | https://vpic.nhtsa.dot.gov/mid/home/displayfile/6ce6db08-3e3b-432e-8c4b-8cd7b6bd49f9 | 2026-11-15 | green |
| Tesla | EU/CN-built | XP7;LRW | 4-8 | unknown | unknown | https://teslatap.com/vin-decoder/ | 2026-11-15 | red |
| Volkswagen | US | 1V2;WVG | 4 | ID.4 trim (MY2026) | C=RWD Pro; V=RWD Pro S; D=AWD Pro; W=AWD Pro S; J=AWD Pro S Plus | https://vpic.nhtsa.dot.gov/mid/home/displayfile/4bb6e581-1ca4-4087-a0fe-583fe6961468 | 2026-11-15 | green |
| Volkswagen | US | 1V2;WVG | 5 | engine type (MY2026) | R=ID.4 RWD 282 hp; S=ID.4 AWD 335 hp | https://vpic.nhtsa.dot.gov/mid/home/displayfile/4bb6e581-1ca4-4087-a0fe-583fe6961468 | 2026-11-15 | green |
| Volkswagen | US | 1V2;WVG | 7-8 | model (MY2026) | E8=ID.4 | https://vpic.nhtsa.dot.gov/mid/home/displayfile/4bb6e581-1ca4-4087-a0fe-583fe6961468 | 2026-11-15 | green |
| Volkswagen | US | 1V2 | 4 | ID.4 trim incl. 62 kWh trims (MY2023) | change log only: "ID.4 Standard RWD 62 kWh and ID.4 S RWD 62 kWh trims"; letters not extracted | https://vpic.nhtsa.dot.gov/mid/home/displayfile/520e230e-7dc6-4317-ae12-04ee0283f722 | 2026-11-15 | yellow |
| Volkswagen group (VW, Skoda, Cupra, Audi) | EU | WVW;WVG;TMB;VSS;WAU | 4-8 | unknown | unknown | | 2026-11-15 | red |
| Audi | US | WA1 | 4 | Q4/Q6 trim (MY2025) | A,B=Q4 45 e-tron; K,L,M=Q4 55 quattro; 4,2,3=Q4 Sportback 55 quattro; 1,2,3=Q6/SQ6 | https://vpic.nhtsa.dot.gov/mid/home/displayfile/0735db50-6440-461b-8e6b-7e2af6168b49 | 2026-11-15 | green |
| Audi | US | WA1 | 5 | engine type (MY2025) | 5=Q4 e-tron RWD 282 hp; U=Q4 quattro 335 hp; 2=Q6 e-tron 322 hp; 4=Q6 quattro 456 hp; 5=SQ6 509 hp (read with pos 4) | https://vpic.nhtsa.dot.gov/mid/home/displayfile/0735db50-6440-461b-8e6b-7e2af6168b49 | 2026-11-15 | green |
| Hyundai | US | KM8 | 8 | powertrain Ioniq 5 (MY2022) | A=653 V 111.2 Ah + RR 168 kW; B=523 V 111.2 Ah + RR 168 kW; C=653 V + FR 74/RR 165 kW; D=523 V + FR 74/RR 165 kW | https://vpic.nhtsa.dot.gov/mid/home/displayfile/28cb9a74-b467-423d-9787-0a352dc6e87c | 2026-11-15 | green |
| Hyundai | US | KM8 | 8 | derived battery Ioniq 5 (MY2022) | A,C≈72.6 kWh nominal (653×111.2); B,D≈58.2 kWh (523×111.2) | https://vpic.nhtsa.dot.gov/mid/home/displayfile/28cb9a74-b467-423d-9787-0a352dc6e87c | 2026-11-15 | yellow |
| Hyundai | US | KM8 | 8 | powertrain Kona Electric (MY2021) | G=Li-Po 356 V 180 Ah + 150 kW motor (≈64 kWh derived) | https://vpic.nhtsa.dot.gov/mid/home/displayfile/2caa4b11-5fca-4a69-a90d-082be660486b | 2026-11-15 | green |
| Kia | US | KND | 5 | EV6 series (MY2024) | 3=Light (58.0 kWh) / Wind (77.4 kWh); 4=GT-Line; 5=GT | https://vpic.nhtsa.dot.gov/mid/home/displayfile/5a21ba6b-7d21-46a6-8159-358df4497a65 | 2026-11-15 | green |
| Kia | US | KND | 8 | EV6 powertrain (MY2024) | A=111.2 Ah RR 160 kW 697 V; B=RR 160 kW 522.7 V; C=FR 70/RR 160 kW 697 V; D=FR 70/RR 160 kW 522.7 V; E=FR 160/RR 270 kW 697 V | https://vpic.nhtsa.dot.gov/mid/home/displayfile/5a21ba6b-7d21-46a6-8159-358df4497a65 | 2026-11-15 | green |
| Kia | US | KND | 8 | derived battery EV6 (MY2024) | 697 V→77.4 kWh; 522.7 V→58.0 kWh (inferred via V×Ah) | https://vpic.nhtsa.dot.gov/mid/home/displayfile/5a21ba6b-7d21-46a6-8159-358df4497a65 | 2026-11-15 | yellow |
| Hyundai/Kia | EU | unknown | 4-8 | unknown | unknown | | 2026-11-15 | red |
| Nissan | US | 1N4 | 4 | motor + battery, Leaf (MY2017) | A=24 kWh; B=30 kWh | https://vpic.nhtsa.dot.gov/mid/home/displayfile/890f439d-5613-4c5b-8a36-1912d86be216 | 2026-11-15 | green |
| Nissan | US | 1N4 | 4 | motor + battery, Leaf (MY2021) | A=40 kWh; B=62 kWh | https://vpic.nhtsa.dot.gov/mid/home/displayfile/15c5f14e-2cdf-4160-a931-10f601780cca | 2026-11-15 | green |
| Nissan | US | 1N4 | 4 | motor + battery, Leaf (MY2023) | A=40 kWh; C=60 kWh | https://vpic.nhtsa.dot.gov/mid/home/displayfile/2384a939-6a24-4fa0-bc54-2d2f579e8018 | 2026-11-15 | green |
| Nissan | US | JN1 | 4 | motor + battery, new Leaf (MY2026) | A=160 kW motor, 75 kWh | https://vpic.nhtsa.dot.gov/mid/home/displayfile/033e4f3a-4ac8-4f78-a279-c672b1c710df | 2026-11-15 | green |
| Nissan | US | 1N4;JN1 | 5 | line | Z=Leaf | https://vpic.nhtsa.dot.gov/mid/home/displayfile/15c5f14e-2cdf-4160-a931-10f601780cca | 2026-11-15 | green |
| Nissan | US | JN8 | 4 | motor + battery, Ariya (MY2026) | 66 kWh / 91 kWh variants; letters not extracted | https://vpic.nhtsa.dot.gov/mid/home/displayfile/033e4f3a-4ac8-4f78-a279-c672b1c710df | 2026-11-15 | yellow |
| Nissan | EU (Sunderland) | SJN | 4-8 | unknown | unknown | | 2026-11-15 | red |
| BMW | US | WBY | 4-7 | model variant (MY2023) | 43AW=i4 eDrive35; 73AW=i4 eDrive40; 33AW=i4 M50; 53EJ=i7 xDrive60 | https://vpic.nhtsa.dot.gov/mid/home/displayfile/0fc2c1f0-7f69-4002-bf4e-298b1bc45622 | 2026-11-15 | green |
| BMW | US | WB5 | 4-7 | model variant (MY2023) | 23CF=iX xDrive50; 33CF=iX M60 | https://vpic.nhtsa.dot.gov/mid/home/displayfile/0fc2c1f0-7f69-4002-bf4e-298b1bc45622 | 2026-11-15 | green |
| Polestar | US/CA | YSM;YSR | 4-5 | motor code (MY2024) | FD=PS2 AWD 320 kW; FE=PS2 FWD 200 kW; FG=PS2 AWD 340 kW; EA=PS3 AWD 360 kW; EE=PS3 AWD 380 kW | https://vpic.nhtsa.dot.gov/mid/home/displayfile/2bc18620-e40e-4c6b-905c-1d7b204dbeb7 | 2026-11-15 | green |
| Polestar | US/CA | YSM;YSR | 6 | version divider | 3=BEV | https://vpic.nhtsa.dot.gov/mid/home/displayfile/2bc18620-e40e-4c6b-905c-1d7b204dbeb7 | 2026-11-15 | green |
| Fiat | US | ZFA | 8 | engine (500e, MY2024) | 4=electric 87 kW; 6=electric 113.7 kW | https://vpic.nhtsa.dot.gov/mid/home/displayfile/74d29bda-da87-4554-874c-1f2412264fdb | 2026-11-15 | green |
| Fiat | EU | ZFA | 8 | same scheme as US? | unverified | https://vpic.nhtsa.dot.gov/mid/home/displayfile/74d29bda-da87-4554-874c-1f2412264fdb | 2026-11-15 | red |
| Renault;Dacia | EU | VF1;UU1 | 4-8 | unknown (no public decoding found) | unknown | | 2026-11-15 | red |
| Peugeot;Opel;Citroen | EU | VF3;W0L;VF7 | 4-8 | unknown (no public decoding found) | unknown | | 2026-11-15 | red |
| MG (SAIC) | EU/UK | LSJ | 4-8 | unknown (no public decoding found) | unknown | | 2026-11-15 | red |
| all | all | any | 10 | model year (ISO 3779 / 49 CFR 565.15) | letter/digit code per year, e.g. R=2024, S=2025, T=2026 | https://www.ecfr.gov/api/versioner/v1/full/2026-11-01/title-49.xml?part=565 | 2026-11-15 | green |

Note: the EU WMIs in the red rows (VF1, UU1, VF3, W0L, VF7, LSJ, SJN, TMB, VSS, WAU) are given as lookup hints from general knowledge, **not verified** in this session. Check them before import or leave them blank.

### (b) rdw_fields

| dataset_id | dataset_name | field | meaning | join_key |
|---|---|---|---|---|
| m9d7-ebf2 | Gekentekende_voertuigen | kenteken | plate (uppercase, no dashes); never store | kenteken |
| m9d7-ebf2 | Gekentekende_voertuigen | merk | make | — |
| m9d7-ebf2 | Gekentekende_voertuigen | handelsbenaming | trade name as registered | — |
| m9d7-ebf2 | Gekentekende_voertuigen | type | type code | — |
| m9d7-ebf2 | Gekentekende_voertuigen | typegoedkeuringsnummer | EU type-approval number, e.g. e4\*2007/46\*1293\*39 | typegoedkeuringsnummer |
| m9d7-ebf2 | Gekentekende_voertuigen | variant | TGK variant code | → codevarianttgk |
| m9d7-ebf2 | Gekentekende_voertuigen | uitvoering | TGK version code | → codeuitvoeringtgk |
| m9d7-ebf2 | Gekentekende_voertuigen | volgnummer_wijziging_eu_typegoedkeuring | EU TGK amendment sequence | — |
| m9d7-ebf2 | Gekentekende_voertuigen | datum_eerste_toelating | first admission date (YYYYMMDD) | — |
| m9d7-ebf2 | Gekentekende_voertuigen | massa_ledig_voertuig | empty mass (kg) | — |
| m9d7-ebf2 | Gekentekende_voertuigen | massa_rijklaar | mass in running order (kg) | — |
| m9d7-ebf2 | Gekentekende_voertuigen | massa_alt_aandr | additional mass for alternative drive (kg) | — |
| m9d7-ebf2 | Gekentekende_voertuigen | catalogusprijs | NL list price at registration (€) | — |
| m9d7-ebf2 | Gekentekende_voertuigen | wielbasis | wheelbase (cm) | — |
| m9d7-ebf2 | Gekentekende_voertuigen | europese_voertuigcategorie | EU vehicle category (M1…) | — |
| m9d7-ebf2 | Gekentekende_voertuigen | datum_tenaamstelling | date of last keeper registration: DO NOT request (owner-related) | — |
| m9d7-ebf2 | Gekentekende_voertuigen | tellerstandoordeel | odometer judgement: DO NOT request | — |
| 8ys7-d773 | Gekentekende_voertuigen_brandstof | brandstof_omschrijving | fuel/energy, e.g. Elektriciteit | kenteken |
| 8ys7-d773 | Gekentekende_voertuigen_brandstof | netto_max_vermogen_elektrisch | net max electric power (kW) | kenteken |
| 8ys7-d773 | Gekentekende_voertuigen_brandstof | nominaal_continu_maximumvermogen | rated continuous max power (kW) | kenteken |
| 8ys7-d773 | Gekentekende_voertuigen_brandstof | max_vermogen_15_minuten | max 15-min power (kW) | kenteken |
| 8ys7-d773 | Gekentekende_voertuigen_brandstof | elektrisch_verbruik_enkel_elektrisch_wltp | WLTP electric consumption (Wh/km) | kenteken |
| 8ys7-d773 | Gekentekende_voertuigen_brandstof | actie_radius_enkel_elektrisch_wltp | WLTP electric range (km) | kenteken |
| 8ys7-d773 | Gekentekende_voertuigen_brandstof | klasse_hybride_elektrisch_voertuig | hybrid/electric class | kenteken |
| byxc-wwua | TGK Basis Uitvoering | typegoedkeuringsnummer | type-approval number | typegoedkeuringsnummer |
| byxc-wwua | TGK Basis Uitvoering | codevarianttgk | variant | codevarianttgk = m9d7-ebf2.variant |
| byxc-wwua | TGK Basis Uitvoering | codeuitvoeringtgk | version | codeuitvoeringtgk = m9d7-ebf2.uitvoering |
| byxc-wwua | TGK Basis Uitvoering | volgnummerrevisieuitvoering | revision sequence | volgnummerrevisieuitvoering |
| byxc-wwua | TGK Basis Uitvoering | begindatumrevisieuitvoering / einddatumrevisieuitvoering | validity window of that revision | — |
| byxc-wwua | TGK Basis Uitvoering | massarijklaarondergrens / massarijklaarbovengrens | running-order mass range (kg) | — |
| byxc-wwua | TGK Basis Uitvoering | paramrijweerstandf0/f1/f2 (onder/bovengrens) | WLTP road-load coefficients | — |
| 4by9-ammk | TGK Aandrijving Uitvoering | motorcode | manufacturer motor code, e.g. 3D7 | TGK triple + volgnummerrevisieuitvoering |
| 4by9-ammk | TGK Aandrijving Uitvoering | volgnummeraandrijving | drive sequence (1 per motor/drive) | volgnummeraandrijving |
| 4by9-ammk | TGK Aandrijving Uitvoering | elektromotorindicator | electric motor J/N | — |
| 4by9-ammk | TGK Aandrijving Uitvoering | hybridemotorindicator | hybrid J/N | — |
| 4by9-ammk | TGK Aandrijving Uitvoering | enkelelektrischschakelingind | pure-electric J/N | — |
| 4by9-ammk | TGK Aandrijving Uitvoering | externoplaadbaarindicator | externally chargeable J/N | — |
| gr7t-qfnb | TGK Energiebron Uitvoering | codeenergiebron | energy source code (E = electricity) | TGK triple + volgnummerrevisieuitvoering + volgnummeraandrijving |
| gr7t-qfnb | TGK Energiebron Uitvoering | maximumnettovermogenogr / bgr | max net power range (kW) | — |
| gr7t-qfnb | TGK Energiebron Uitvoering | maximumvermogen30minogr / bgr | max 30-min power range (kW) | — |
| gr7t-qfnb | TGK Energiebron Uitvoering | verbruikvolledigelekwltpogr / bgr | WLTP electric consumption range (Wh/km) | — |
| gr7t-qfnb | TGK Energiebron Uitvoering | actieradiusvolledigelekwltpogr / bgr | WLTP electric range, min–max (km) | — |
| gr7t-qfnb | TGK Energiebron Uitvoering | elektrischeactieradiusnedc | NEDC electric range (km), older approvals | — |
| x5v3-sewk | TGK Handelsbenaming Fabrikant | handelsbenamingfabrikant | manufacturer trade name, e.g. MODEL 3 | typegoedkeuringsnummer + **codevariantgk** (sic) + codeuitvoeringtgk |
| x5v3-sewk | TGK Handelsbenaming Fabrikant | typeaanduidingfabrikant | manufacturer type designation | — |
| kyri-nuah | TGK Merk Uitvoering | merkcoderdw | RDW make code | TGK triple + volgnummerrevisieuitvoering |
| 7ug8-2dtt | Gekentekende_voertuigen_bijzonderheden | bijzonderheid_code / _variabele_tekst | per-plate remarks (free text): not needed, avoid | kenteken |
