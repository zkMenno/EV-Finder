# R-26 Charging data licences and card-payment rules

**Question.** (1) What licence, attribution and reuse limits apply to the official charging-statistics sources we plan to ingest (T-025) or cite (T-027, T-028)? (2) What do the US, Australia and the EU require on card/contactless payment at public chargers?

Researched 2026-11-15 by a WS0 research agent. Time-boxed at about 1 h. Every link below was opened on 2026-11-15 unless marked "not reachable". Confidence: 🟢 seen on the primary page · 🟡 reasoned or one indirect source · 🔴 unsure, check before release.

## Answer

**Licences.** Four sources are clean enough to go live. Bundesnetzagentur Ladesäulenregister is **CC BY 4.0, credit "Bundesnetzagentur.de"** 🟢. UK DfT EV charging infrastructure statistics are **OGL v3.0** 🟢. NDW (Netherlands) open data is **CC0 1.0** by default, with no attribution required 🟢. US AFDC station data **"may be used for any purpose whatsoever"** under NLR terms, and data.gov lists it as CC BY 4.0 🟢. EAFO is a Commission (DG MOVE) site, so the **Commission reuse policy (CC BY 4.0 unless otherwise indicated)** covers it, but the underlying point data comes from Eco-Movement (a third party) and EAFO itself states no licence. Treat EAFO aggregates as 🟡 CC BY 4.0 and ask EAFO in writing before release. Belgium's National Access Point datasets show **"License: Not specified"** 🔴, so we use EAFO for Belgium. For New Zealand, EECA publishes CSVs and NZTA runs the EVRoam API, but **neither states a licence** 🔴: blocked.

**Payment.** The US rule (23 CFR 680.106(f)) covers NEVI and Title 23-funded chargers only. It requires **contactless payment that accepts major debit and credit cards**, plus a toll-free phone or SMS option, **no membership**, and no throttling by payment method 🟢. Australia has **no general federal rule** that we could find 🟡. NSW fast-charging grants (round 4, Dec 2025) require **credit/debit card payment with no registration, membership or app, and it must work without mobile signal** 🟢. A 2023 national minimum standard for government-funded fast chargers mentions "standardised payment" but we could not find its details 🔴. The EU (AFIR Art. 5(1)) is the only rule for **all** new public chargers: **≥50 kW needs a card reader or a contactless card device** (new from 13 Apr 2024). Below 50 kW, an internet-based payment such as a QR code is enough. **Existing ≥50 kW points on the TEN-T network must be retrofitted by 1 Jan 2027** 🟢.

---

## 1. Licences per source

| Source | Licence | Attribution | Reuse limits / notes | Conf. |
|---|---|---|---|---|
| **EAFO** (European Commission, DG MOVE) | Commission reuse policy: content owned by the EU is under **CC BY 4.0** "unless otherwise indicated" ([Commission legal notice](https://commission.europa.eu/legal-notice_en), linked from the EAFO footer) | Credit + indicate changes. Suggested: "Source: European Alternative Fuels Observatory (European Commission), [date]" | The EAFO FAQ ([node/62](https://alternative-fuels-observatory.ec.europa.eu/node/62)) says recharging-point data comes mainly from **Eco-Movement**, "directly from CPOs". The legal notice adds: "To use or reproduce content that is not owned by the EU, you may need to seek permission directly from the rightholders." EAFO gives no dataset-level licence. Graph data downloads are CSV/XLS. Our aggregate-only use is low-risk, but the EU's ownership of the numbers is unconfirmed | 🟡 |
| **Bundesnetzagentur Ladesäulenregister** (DE) | **CC BY 4.0**: "Die Daten sind durch eine Creative Commons Namensnennung 4.0 International Lizenz lizenziert" ([BNetzA Ladesäulenkarte page](https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/E-Mobilitaet/Ladesaeulenkarte/start.html); [licence](https://creativecommons.org/licenses/by/4.0/deed.de)) | **"Bundesnetzagentur.de"** (required wording) | Free download, no login. XLSX (29 MB) and CSV (53 MB); latest file dated 12.11.2026. BNetzA disclaims accuracy. The page covers the full point list. We derive counts from it, which CC BY allows | 🟢 |
| **UK DfT EV charging infrastructure statistics** | **OGL v3.0**: "This publication is licensed under the terms of the Open Government Licence v3.0 except where otherwise stated" ([1 July 2026 release](https://www.gov.uk/government/statistics/electric-vehicle-charging-infrastructure-statistics-1-july-2026/public-electric-vehicle-charging-infrastructure-statistics-1-july-2026); [OGL v3](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)) | Without a specific statement from the provider: **"Contains public sector information licensed under the Open Government Licence v3.0."** | Data comes from CPOs and is collated by **Zapmap** for DfT. Use only the official EVCI tables. Zapmap "industry estimates" quoted in the release "fall outside the scope of official statistics", so don't ingest them. Third-party copyright needs separate permission. **The definition changed on 1 Jan 2026 from devices to chargers (EVSE)**: 121,171 chargers vs 97,266 devices at 1 Jul 2026. The series is quarterly (next release was due Nov 2026), plus monthly "faster indicators" (last updated 11 Nov 2026) ([collection](https://www.gov.uk/government/collections/electric-vehicle-charging-infrastructure-statistics)) | 🟢 |
| **US AFDC station data** (DOE; run by NLR, formerly NREL) | The NLR data-download terms say the data "may be used for any purpose whatsoever" ([AFDC data download](https://afdc.energy.gov/data_download)). data.gov metadata: **CC BY 4.0** ([catalog entry](https://catalog.data.gov/dataset/alternative-fueling-station-locations)) | Use CC BY wording to be safe: "Source: U.S. DOE Alternative Fuels Data Center". **No-endorsement clause**: "The names DOE/NLR/Alliance shall not be used … to endorse or promote any entity that adopts or uses the Data." | The counts file is static, needs no form: `https://afdc.energy.gov/files/docs/historical-station-counts.xlsx` (linked from [stations/states](https://afdc.energy.gov/stations/states)). The bulk station download form asks for name, email and use: **ask Menno first (form submission)**. Provided "AS IS" | 🟢 |
| **US AFDC / NLR Developer API** (alt-fuel-stations v1) | Same data terms as above (🟡: the API docs page was not reachable from here) | As above | **API key required** (40 characters, "should be kept private"; sent as `X-Api-Key` header or `api_key` param) ([api-key docs](https://developer.nrel.gov/docs/api-key)). Default limit **1,000 requests/hour** per key ([rate limits](https://developer.nlr.gov/docs/rate-limits)). Key signup is account creation: **ask Menno**. Domain moving from developer.nrel.gov to developer.nlr.gov. We don't need it for counts | 🟡 |
| **NDW / DOT-NL** (Netherlands) | **CC0 1.0** by default: "Tenzij bij een specifieke dataset … uitdrukkelijk anders is vermeld … Creative Commons Zero (CC0 1.0)". "Bronvermelding is niet verplicht, maar wordt door NDW gewaardeerd" ([NDW data terms](https://docs.ndw.nu/algemeen/data-gebruiksvoorwaarden/)) | Not required. Courtesy credit: "Bron: NDW" | DOT-NL is the AFIR data platform for public points; data "can be consumed free of charge by anyone" ([DOT-NL FAQ](https://docs.ndw.nu/en/faq/DOT-NL/)). Daily files on [opendata.ndw.nu](https://opendata.ndw.nu/): `charging_point_locations.geojson.gz` (5 MB) and `charging_point_locations_ocpi.json.gz` (18 MB), both dated 15 Nov 2026. **This is the licence-clean alternative to RVO** (share-alike) for a Dutch count series, but these are point files, so we'd count them ourselves and the definition is ours | 🟢 |
| **Belgium National Access Point** (transportdata.be) | **None stated.** The Gireve EVCI dataset shows "License Not specified"; Gireve "offers … a fee-based reuse license" ([transportdata.be/dataset/evci](https://transportdata.be/dataset/evci)). The Eco-Movement AFIR static dataset has no licence, and its page lists no resources ([dataset](https://transportdata.be/dataset/afir-static-dataset-selected-cpos)) | — | Blocked. Use EAFO for the Belgian series | 🔴 |
| **New Zealand: EECA public EV charger dashboard** | **None stated** on the page ([dashboard](https://www.eeca.govt.nz/insights/data-tools/public-ev-charger-dashboard/)) | — | 4 CSVs (Public EV chargers, Co-funded chargers, metrics by region/district), updated quarterly (page last updated 16 Oct 2026). Data is mainly from EVRoam. Charging points are *estimated* ("a necessary underestimation"). The data.govt.nz entry ([public-ev-chargers](https://catalogue.data.govt.nz/dataset/public-ev-chargers)) was **not reachable** (bot wall), so it may state a licence. Check by hand | 🔴 |
| **New Zealand: NZTA EVRoam** | **None stated** ([EVRoam FAQ](https://nzta.govt.nz/planning-and-investment/planning/transport-planning/planning-for-electric-vehicles/evroam/evroam-faqs/)) | — | An outward API exists; access by emailing NZTA, which would be sent in Menno's name, so draft only. NZTA aims to "freely distribute the information". The data.govt.nz entry was not reachable | 🔴 |

**What this means for T-025:** EAFO, BNetzA and DfT loaders can be built now. BNetzA and DfT are releasable. Keep EAFO `blocked` until EAFO replies in writing (or WS0 accepts the Commission notice as enough). This is a reversible default.

## 2. Card / contactless payment rules

| Market | Rule | Scope | Exact requirement | Conf. |
|---|---|---|---|---|
| **US: NEVI** | [23 CFR 680.106(f)](https://www.ecfr.gov/current/title-23/chapter-I/subchapter-G/part-680/section-680.106) "Payment methods" | Projects funded under NEVI or Title 23 (§680.100). **Not** privately funded chargers. Exempt if charging is "permanently provided free of charge" | "(1) … at a minimum shall include a **contactless payment method that accepts major debit and credit cards**, and either an automated toll-free phone number or a short message/messaging system (SMS)…; (2) **Not require a membership** for use; (3) Not delay, limit, or curtail power flow … on the basis of payment method or membership; (4) Provide access for users that are limited English proficient and accessibility for people with disabilities." eCFR shows every section of Part 680 unchanged since 30 Mar 2023 (checked 15 Nov 2026) | 🟢 |
| **Australia: federal** | No general payment rule found | Grants only | A 2023 national minimum standard for government-funded fast chargers "includes stipulations about a standardized payment system", detail not given ([electrive, 27 Nov 2023](https://www.electrive.com/2023/11/27/australia-sets-reliability-standards-on-fast-chargers)). The federal DRIVEN Charger Grant Stream (closed 28 Aug 2026) requires 98% uptime but says nothing on payment ([business.gov.au](https://business.gov.au/grants-and-programs/driven-charger-grant-stream)) | 🔴 |
| **Australia: NSW** | NSW EV fast charging grants round 4 guidelines, Dec 2025 ([PDF](https://www.energy.nsw.gov.au/sites/default/files/2025-12/202512-NSW-DCCEEW-EV-fast-charging-grants-round-4-funding-guidelines.pdf), p. 13) | Grant-funded fast chargers (150–175 kW class) | "Payment must be possible via **credit/debit card, with no requirement for a registration, membership, or app download**. Payment must be possible **without the user having mobile or internet signal**." Fees must be displayed without needing signal. OCPP 2.0.1 required. The kerbside (AC) round 3 only asks applicants to "address … the use of contactless payment" ([nsw.gov.au](https://www.nsw.gov.au/grants-and-funding/ev-kerbside-charging-grants-round-3)) | 🟢 |
| **EU: AFIR** | Reg. (EU) 2023/1804 Art. 5(1), 2nd and 3rd subparagraphs ([text, DE](https://gesetze.legal/eu/vo_eu_2023_1804/5); EUR-Lex not reachable from here) | **All** publicly accessible points, regardless of funding | Ad hoc charging must be possible with a payment instrument widely used in the Union. Points **≥50 kW deployed from 13 Apr 2024**: payment card reader **or** contactless device that reads at least payment cards. **<50 kW** deployed from 13 Apr 2024: may instead use an internet-based secure payment, such as a QR code. **From 1 Jan 2027**, existing ≥50 kW points on the **TEN-T road network** (and secure parking areas), including those built before 13 Apr 2024, must meet the card-reader/contactless rule | 🟢 |

**For the /learn page (T-027):** the plain-language contrast is that the EU makes tap-to-pay a rule for all new fast chargers. The US and NSW require it only where public money paid for the charger. US and AU rows can now be written, with the Australian federal row marked "no national rule".

## Open items

1. 🟡 EAFO: send DG MOVE/EAFO a short email asking whether published EAFO aggregates may be reused under CC BY 4.0 given the Eco-Movement data (draft for Menno to approve).
2. 🔴 NZ: re-check catalogue.data.govt.nz in a normal browser for a stated licence. NZ government data is often CC BY 4.0, but that is not seen, so don't assume it.
3. 🔴 Australia federal "standardised payment" detail: find the 2023 Energy and Climate Change Ministerial Council or DCCEEW standard document.
4. Not reachable from here (bot wall, 429 or proxy): EUR-Lex AFIR HTML, developer.nlr.gov API docs, catalogue.data.govt.nz, a second EAFO page (rate-limited 429).
5. Note for the spec owner: the EAFO homepage news (29 Oct 2026) gives **1,176,554 public points in EU27**, preliminary, newer than the spec table's 1,155,861.

## Sources (all opened 2026-11-15)

- EAFO homepage (footer: managed by DG MOVE; legal notice link): https://alternative-fuels-observatory.ec.europa.eu/
- EAFO FAQ (data sources): https://alternative-fuels-observatory.ec.europa.eu/node/62
- European Commission legal notice (reuse policy, CC BY 4.0): https://commission.europa.eu/legal-notice_en
- Bundesnetzagentur Ladesäulenkarte / register download and licence: https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/E-Mobilitaet/Ladesaeulenkarte/start.html
- CC BY 4.0 (DE deed): https://creativecommons.org/licenses/by/4.0/deed.de
- DfT, Public EV charging infrastructure statistics 1 July 2026: https://www.gov.uk/government/statistics/electric-vehicle-charging-infrastructure-statistics-1-july-2026/public-electric-vehicle-charging-infrastructure-statistics-1-july-2026
- DfT collection page: https://www.gov.uk/government/collections/electric-vehicle-charging-infrastructure-statistics
- Open Government Licence v3.0: https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
- AFDC data download (NLR terms): https://afdc.energy.gov/data_download
- AFDC station counts by state (historical counts xlsx link): https://afdc.energy.gov/stations/states
- data.gov, Alternative Fueling Station Locations: https://catalog.data.gov/dataset/alternative-fueling-station-locations
- NREL/NLR API key usage: https://developer.nrel.gov/docs/api-key
- NLR web service rate limits: https://developer.nlr.gov/docs/rate-limits
- NDW data terms (CC0): https://docs.ndw.nu/algemeen/data-gebruiksvoorwaarden/
- NDW DOT-NL FAQ: https://docs.ndw.nu/en/faq/DOT-NL/
- NDW open data portal: https://opendata.ndw.nu/
- transportdata.be, Gireve EVCI: https://transportdata.be/dataset/evci
- transportdata.be, AFIR static dataset selected CPOs: https://transportdata.be/dataset/afir-static-dataset-selected-cpos
- EECA public EV charger dashboard: https://www.eeca.govt.nz/insights/data-tools/public-ev-charger-dashboard/
- NZTA EVRoam FAQs: https://nzta.govt.nz/planning-and-investment/planning/transport-planning/planning-for-electric-vehicles/evroam/evroam-faqs/
- 23 CFR 680.106 and 680.100 (eCFR, current; version history API): https://www.ecfr.gov/current/title-23/chapter-I/subchapter-G/part-680/section-680.106
- NSW EV fast charging grants round 4 guidelines (Dec 2025): https://www.energy.nsw.gov.au/sites/default/files/2025-12/202512-NSW-DCCEEW-EV-fast-charging-grants-round-4-funding-guidelines.pdf
- NSW EV kerbside charging grants round 3: https://www.nsw.gov.au/grants-and-funding/ev-kerbside-charging-grants-round-3
- DRIVEN Charger Grant Stream: https://business.gov.au/grants-and-programs/driven-charger-grant-stream
- electrive, Australia sets reliability standards (27 Nov 2023): https://www.electrive.com/2023/11/27/australia-sets-reliability-standards-on-fast-chargers
- AFIR Art. 5 (German text reproduction): https://gesetze.legal/eu/vo_eu_2023_1804/5

## Ready-to-import rows for data/sources.yaml

```yaml
  - {id: eafo, name: European Alternative Fuels Observatory (EAFO), owner: European Commission (DG MOVE), licence: CC-BY-4.0 (to confirm), access: bulk, cadence: monthly, status: blocked,
     terms: "Commission reuse policy (CC BY 4.0 unless otherwise indicated); point data from Eco-Movement (third party), so EU ownership unconfirmed. Aggregates only. Attribution: 'Source: European Alternative Fuels Observatory (European Commission)'. Ask EAFO in writing before release (R-26), 2026-11-15."}
  - {id: bnetza-lsr, name: Bundesnetzagentur Ladesäulenregister, owner: Bundesnetzagentur (DE), licence: CC-BY-4.0, access: bulk, cadence: monthly, status: active,
     terms: "Licence stated on the Ladesäulenkarte page, 2026-11-15. Required attribution: 'Bundesnetzagentur.de'. XLSX/CSV full point list; we publish derived counts only. No accuracy warranty."}
  - {id: dft-evci, name: DfT electric vehicle public charging infrastructure statistics, owner: UK Department for Transport / OZEV, licence: OGL-UK-3.0, access: bulk, cadence: quarterly, status: active,
     terms: "OGL v3.0 stated on the release, 2026-11-15. Attribution: 'Contains public sector information licensed under the Open Government Licence v3.0.' Official EVCI tables only; Zapmap industry estimates excluded. Definition changed to chargers (EVSE) from 1 Jan 2026 (uk_dft_evse_2026 vs uk_dft_device_pre2026)."}
  - {id: afdc-stations, name: AFDC station counts (historical-station-counts.xlsx), owner: US DOE / National Laboratory of the Rockies (NLR), licence: CC-BY-4.0, access: bulk, cadence: monthly, status: active,
     terms: "NLR download terms: 'may be used for any purpose whatsoever'; data.gov lists CC BY 4.0, 2026-11-15. Attribution: 'Source: U.S. DOE Alternative Fuels Data Center'. Must not imply DOE/NLR endorsement. Static xlsx needs no form; the bulk download form needs Menno's OK."}
  - {id: afdc-api, name: NLR Developer API alt-fuel-stations v1, owner: US DOE / NLR, licence: CC-BY-4.0 (to confirm), access: api, cadence: monthly, status: blocked,
     terms: "API key required (env var, keep private), default 1,000 requests/hour. Key signup = account creation, ask Menno first. Not needed for counts (use afdc-stations)."}
  - {id: ndw-dot-nl, name: NDW open data / DOT-NL public charging points, owner: NDW for Ministerie van IenW (NL), licence: CC0-1.0, access: bulk, cadence: daily, status: active,
     terms: "NDW data terms: CC0 1.0 unless a dataset states otherwise; attribution not required, courtesy 'Bron: NDW', 2026-11-15. Point files (GeoJSON/OCPI); we derive counts with our own definition. Licence-clean alternative to RVO."}
  - {id: be-nap, name: transportdata.be (Belgian National Access Point) charging datasets, owner: FPS Mobility (BE) / publishing CPOs and platforms, licence: none, access: bulk, cadence: daily, status: blocked,
     terms: "Datasets show 'License Not specified' (Gireve offers a fee-based reuse licence), 2026-11-15. Use EAFO for Belgium."}
  - {id: nz-eeca-chargers, name: EECA public EV charger dashboard CSVs, owner: EECA (NZ), licence: unknown (to confirm), access: bulk, cadence: quarterly, status: blocked,
     terms: "No licence stated on the dashboard page, 2026-11-15; data.govt.nz entry not reachable. Charging points are estimates. Confirm the licence first."}
  - {id: nz-evroam, name: NZTA EVRoam, owner: NZ Transport Agency Waka Kotahi, licence: none, access: api, cadence: daily, status: blocked,
     terms: "No licence stated; API access by email request to NZTA (would be sent in Menno's name, so draft only), 2026-11-15."}
```
