# R-31 Emerging-market readiness: Türkiye and South Korea

**Answer:** neither country is ready for a Phase 1–5 launch. Both have real used-EV volume, but neither has a licence-clean national registration feed broken down by model, and no marketplace offers a public affiliate or feed programme. 🟡 Türkiye stays the first emerging market to add once we reach the emerging-market wave (Roadmap "Later", after Phase 5; I call it Phase X here). It uses Latin script, takes few extra catalogue variants and has a used-EV pool growing fast from about 2025. Korea comes second: its open data is better (the charger API and municipal registrations carry KOGL / "no restriction" terms), but it needs a Korean UI, Korean-market variants (Porter EV, Ray EV, Casper Electric and so on) and the Ministry of Environment range figures rather than WLTP. **Cheapest 3 steps** (shared across both): (1) add the 8 source rows at the end as `blocked` so they are tracked, (2) have WS5 send two short partner enquiries (Encar via the CAR Group conversation already planned for carsales; sahibinden/arabam as one Türkiye email), which Menno approves first, (3) have WS3 list the 10 country-only EV variants per market in the catalogue backlog. No code yet.

Researched 2026-11-15, about 1 h time-box. Every link below was opened on 2026-11-15 unless marked *not opened*. The shared web-search budget ran out partway through the session, so a few points rest on general knowledge and are marked 🟡 or 🔴.

---

## 1. Türkiye

### 1.1 EV fleet and registrations

| Fact | Value | Source | Conf. |
|---|---|---|---|
| Share of new car registrations that were electric, 2025 | 16.7 % of 1,120,427 cars | TÜİK *Motorlu Kara Taşıtları, Aralık 2025*, via [alomaliye.com](https://www.alomaliye.com/2026/01/16/2025-yilinda-2-milyon-368-bin-538-adet-tasitin-trafige-kaydi-yapildi/) | 🟢 |
| Electric share of the registered car fleet, end 2025 | 2.1 % of 17,373,581 cars (about 365k, our calculation) | same | 🟢 share, 🟡 count |
| EVs registered, Dec 2025 | 373,733 | 2PLAN quoted in [CNN Türk, 23 Jan 2026](https://www.cnnturk.com/otomobil/2-el-arac-pazari-2025te-rekor-kirdi-2388338) | 🟡 (no primary source given) |
| EVs, May 2026 | 440,327 | EPDK *Şarj Hizmeti Piyasası, Mayıs 2026* via [alomaliye.com](https://www.alomaliye.com/2026/06/17/sarj-altyapisinda-buyume-suruyor-elektrikli-arac-sayisi-440-bini-asti/) | 🟢 (secondary report of EPDK) |
| Used car market 2025 | about 9.4 M transactions (+5.8 %); about 75 % estimated genuine | 2PLAN in [CNN Türk](https://www.cnnturk.com/otomobil/2-el-arac-pazari-2025te-rekor-kirdi-2388338) | 🟡 |
| Used EV sales 2024 | 18,620 (+122 %) | docs/spec/marketplaces.md (earlier round), not re-checked | 🟡 |

- **TÜİK** publishes a monthly *Motorlu Kara Taşıtları* bulletin with fuel-type shares and brand shares of new registrations. The model-level breakdown is not in the bulletin. The data portal now redirects from data.tuik.gov.tr to `veriportali.tuik.gov.tr` (HTTP 302, checked). 🟢
- **ODMD** (distributors' association) publishes monthly sales. Model rankings for BEVs come out as press tables, not as an open dataset. The odmd.org.tr site responds (302 to `web_2837_1/index.aspx`). 🟢 that the site exists, 🟡 on format.
- **Licence:** 🔴 No reuse licence was found for TÜİK, ODMD or EPDK. The TÜİK terms page was not found before the search budget ran out. Treat all three as `blocked` until someone reads their terms. Quoting single facts with a citation (a market share, a fleet total) is likely fine for editorial country pages 🟡. Bulk import is not.

### 1.2 Charging data

- EPDK publishes **monthly charging-market statistics** (*Şarj Hizmeti Piyasası Aylık İstatistikleri*): socket counts, AC/DC split, installed MW, kWh consumed, operators by socket count. May 2026: 44,175 sockets (25,125 AC, 19,050 DC). Dec 2025: 2,913 MW installed; ZES, Trugo and Eşarj were the top operators. Sources: [alomaliye](https://www.alomaliye.com/2026/06/17/sarj-altyapisinda-buyume-suruyor-elektrikli-arac-sayisi-440-bini-asti/), [motor1 TR](https://tr.motor1.com/news/784870/turkiye-ev-verileri-epdk/). 🟢
- **EPDK charging map / API:** 🔴 not confirmed. The subdomains I tried (`sarjhizmetleri.epdk.gov.tr`, `sarjharitasi.epdk.gov.tr`) failed at the proxy (502), and `epdk.gov.tr/Detay/Icerik/3-0-0/sarj-hizmetleri` redirects to the home page. Neither secondary article mentions a public API or map.
- **March 2026 rule change:** operators must publish real-time price and availability "through digital channels and at stations". The article names no central EPDK feed ([Milliyet, 24 Mar 2026](https://www.milliyet.com.tr/7559439)). 🟢 rule, 🔴 whether a central open feed follows.
- Practical route: OpenStreetMap / Open Charge Map for station points (ODbL / CC BY, kept separate per data rule 3) plus EPDK monthly totals for country pages. 🟡

### 1.3 Top EV models (new sales 2025, the future used pool)

ODMD 2025 full year, via [tamindir](https://www.tamindir.com/haber/turkiye-2025-en-cok-satilan-elektrikli-arabalar_104003/) 🟢: Tesla Model Y 31,509 · Togg T10X 27,583 · Togg T10F 11,437 · Mini Countryman 9,418 · KG Mobility Torres 8,416 · Kia EV3 7,654 · BYD Atto 3 6,346 · Opel Frontera 5,765 · BYD Seal U 4,522 · Hyundai Ioniq 5 4,186. Motor1 confirms the Model Y figure and Togg's 2nd and 3rd places.

- **Used pool today (🟡 reasoned):** Togg T10X (deliveries from 2023), Tesla Model Y and Model 3, MG4/ZS EV, Renault Zoe/Megane E-Tech, Hyundai Kona and Ioniq 5. No source with used-EV rankings by model was found.
- **Catalogue gap:** Togg T10X/T10F and possibly the KGM Torres EVX variants are thin or missing in EU/EEA-based data. Togg has to come from maker documents or TSE type approval. 🟡

### 1.4 Marketplaces

| Site | Notes | Affiliate / feed |
|---|---|---|
| sahibinden.com | Market leader (spec). robots.txt returned **403** to a plain fetch: strong bot protection. | 🔴 None found. Needs a direct partner enquiry. |
| arabam.com | Second car portal. robots.txt also 403. Has corporate dealer agreements ([kurumsal üyelik](https://www.arabam.com/kurumsal-uyelik-sozlesmesi), *not opened*). | 🔴 None found |
| Letgo, VavaCars, BorusanNext, Otokoç | Smaller or dealer channels (spec + EİDS list) | 🔴 unknown |

- **EİDS (Ministry of Trade electronic listing verification):** car ads are checked against the official ownership record through an "Araç API". As of 27 Jan 2026, 55 firms had integrated, including arabam.com, sahibinden, Letgo, Otokoç, BorusanNext and Doğuş ([list](https://www.alomaliye.com/2026/01/27/tasit-ilanlarinda-eidsye-entegre-olan-firmalara-iliskin-duyuru/)). 🟢 For us, listings on these sites are owner-verified, which is a trust signal we can mention. We never host listings, so EİDS does not apply to us 🟡 (check if we ever show listing data on our own pages).

### 1.5 Language, currency, units

- Turkish is not in our six languages. A TR locale would be number 7. Turkish casing (i/İ, ı/I) breaks naive `toLowerCase()` search and slugs, so use locale-aware compare. 🟢 known language property
- **TRY with high inflation:** store prices in TRY with their date and show a EUR conversion. A price band older than a month gets a "stale" badge. 🟡
- Units are metric. WLTP is the type-approval basis (EU-aligned). 🟡

### 1.6 Consumer-data regulation

- **KVKK (Law 6698)** is GDPR-like. Transfers of Turkish users' personal data abroad (our Hetzner server is in the EU) need a lawful transfer basis. The 2024 amendment introduced standard contracts that must be notified to the authority. 🟡 general knowledge, not re-checked this session. This is a legal-risk item for R-04 follow-up before any TR accounts exist. Anonymous browsing without cookies keeps exposure low.
- E-commerce and advertising rules (Law 6563) apply to marketplaces, not to a link-out finder. 🟡

---

## 2. South Korea

### 2.1 EV fleet and registrations

| Fact | Value | Source | Conf. |
|---|---|---|---|
| Registered EVs, end 2025 | 899,000 (+215k in the year) | MOLIT *자동차 등록 현황*, 29 Jan 2026, via [Newsis](https://mobile.newsis.com/view/NISX20260128_0003493411) | 🟢 |
| New EV registrations 2025 | 221,000 = about 13 % of 1,695,000 | same | 🟢 |
| New EV sales Jan–Sep 2026 | about 297,000 (above all of 2025) | KAMA via [Korea Times, 29 Oct 2026](https://www.koreatimes.co.kr/business/companies/20261029/evs-on-path-to-overcome-chasm-in-korea) | 🟢 |
| Used EV transfers Q1 2026 | 16,107 (+48.7 % YoY), out of 561,088 used transfers | Kaizen-You Data Research (from registration data), [Etnews](https://m.etnews.com/20260424000195) | 🟢 |
| Used EVs at K Car | sell in 81 % of the time an ICE car takes (Jan–Sep 2026) | K Car via Korea Times | 🟢 |

- **National model-level registrations:** 🔴 not found as open data. `stat.molit.go.kr` reset the connection. On data.go.kr I found only **municipal** fuel-type registration files (Daejeon monthly, Bucheon monthly, Yongin, Chungju, Asan and others). All of them carry **"이용허락범위 제한 없음"** (no restriction on scope of use), e.g. [Daejeon 15011919](https://www.data.go.kr/catalog/15011919/fileData.json), [Bucheon 15157531](https://www.data.go.kr/catalog/15157531/fileData.json). They give fuel and vehicle-type counts, not models. 🟢
- KOTSA publishes vehicle-standards statistics under the same unrestricted licence ([15150330](https://www.data.go.kr/dcat/metadata/15150330)). It contains no per-model fleet data. 🟢
- Per-model used-EV figures come from private firms (Kaizen-You, K Car, Daangn), and none of them carry a licence. Quoting single facts with a citation is the most we can do. 🟡

### 2.2 Charging data (strongest open asset)

- **KECO EV charger info API** [data.go.kr 15076352](https://www.data.go.kr/catalog/15076352/openapi.json) (Korea Environment Corporation). Covers station and charger IDs, type, address, lat/lon, opening hours, operator, power and **live charger status**. Format XML; updated 2026-07-21. Licence: **"제3자 권리 포함 : 저작권 표시, 공공저작물 : 출처표시 (제 1유형)"**, i.e. KOGL Type 1 (attribution) *with a third-party-rights flag*. 🟢 licence label; 🔴 which fields carry third-party rights (probably operator-supplied data).
- **KECO public fast-charger list** [15156662](https://data.go.kr/catalog/15156662/openapi.json): installation year, region, operator, fast-charge kW, connector type, lat/lon. Licence **"이용허락범위 제한 없음"**. Created 2025-12-17. 🟢
- KECO synthetic per-session charging data [15153595](https://www.data.go.kr/catalog/15153595/openapi.json): about 6.3 M real 2024 sessions turned into an **AI-test synthetic** set. Not usable as fact; it might help test charging-curve models. 🟢 description
- **KOGL Type 1** in general: attribution required; commercial use and modification allowed. 🟡 The kogl.or.kr page was linked from the metadata but **not opened** (fetch permission timed out). Confirm before setting `active`.
- ev.or.kr (MoE zero-emission vehicle portal) responds (HTTP 200), but its content was **not read**. From memory it holds per-model subsidy tables and certified range 🟡.

### 2.3 Top used EV models

- Daangn direct trades, Jan–Oct 2026: Tesla Model Y, Hyundai Ioniq 5, Tesla Model 3, Hyundai Porter II EV (no counts), [koreancenter.or.kr](https://www.koreancenter.or.kr/news/articleView.html?idxno=1434941). Completed used-EV trades +54 %, Model Y 2.7×. 🟢 ranking from one platform
- 🟡 Likely also large: Kia EV6, Niro EV, Ray EV, Kona Electric, Kia Bongo III EV, Casper Electric, Genesis GV60.
- **Catalogue gap:** Porter EV, Bongo EV (vans, which are parked in our roadmap), Ray EV and Casper Electric are Korea-only or barely in EU data. Korean range is the **MoE-certified figure** (환경부 인증), often shown with efficiency in km/kWh. It is not WLTP, so it needs its own fact type. 🟡

### 2.4 Marketplaces

| Site | Share (spec) | Affiliate / feed |
|---|---|---|
| Encar | about 53 % | Owned by CAR Group (as carsales). The only "partner" programme found is the **export-partner** scheme for certified exporters (licences, audits, 5+ years, 1,000+ shipments), [global.encar.com](https://global.encar.com/export-service/intro). No affiliate or API found. 🟢 export scheme / 🔴 affiliate. robots.txt is reachable (HTTP 200), not read. |
| K Car | about 21 % | Publishes a monthly price outlook (spec, layer 0). Affiliate 🔴 unknown |
| KB Chachacha | about 13 % | 🔴 unknown |
| Daangn (당근) | C2C | 🔴 unknown, but publishes used-EV trend data |

### 2.5 Language, currency, units

- Korean UI and Hangul fonts (Pretendard / Noto Sans KR). Sorting and search must handle Hangul. 🟡
- KRW has no minor unit. Listings quote prices in **만원** (10,000 KRW), e.g. "2,850만원". Display has to respect that habit. 🟡
- Metric. Efficiency is usually shown as km/kWh, so convert from our internal Wh/km at display time. Range follows the MoE cycle (see 2.3). 🟡

### 2.6 Consumer-data regulation

- **PIPA** is strict: separate consent per purpose, and overseas transfer needs consent or an adequacy-type basis. The 2023 amendment eased this somewhat; Korea and the EU have mutual adequacy (EU→KR decision 2021). 🟡 general knowledge, not re-checked.
- The **Location Information Act** applies if we use device location ("chargers near me"), and a location-business report may be needed. 🔴 check before any geolocation feature for KR.
- Licence plates and VINs count as personal data when linked to an owner. We don't handle them. 🟡

---

## 3. Verdict

| | Türkiye | South Korea |
|---|---|---|
| Used-EV pool | 🟢 growing fast (2025 new BEV share 16.7 %, fleet about 440k by May 2026) | 🟢 large (899k fleet, used transfers +49 %) |
| Open registration data by model | 🔴 none, licence unknown | 🔴 national none; 🟢 municipal by fuel (unrestricted) |
| Charging open data | 🟡 monthly totals only, licence unknown | 🟢 national API, KOGL Type 1 |
| Marketplace partner path | 🔴 none public, two big independents | 🔴 none public; 🟡 Encar via CAR Group |
| Catalogue fit | 🟡 mostly EU models + Togg | 🔴 many Korea-only variants, non-WLTP range |
| UI / locale | 🟡 new TR locale, Latin script | 🔴 new KO locale, Hangul, 만원 |
| **Ready for Phase X?** | **Not ready; "prepare" status.** First in line. | **Not ready.** Second; charging data could come earlier |

### Three cheapest steps (in order, all reversible)
1. **Register the sources** (rows below) as `blocked` / `waiting_permission`. Cost: 10 minutes for WS1, nothing more.
2. **Two partner enquiry drafts** (WS5): one to CAR Group covering Encar (folded into the planned carsales pitch), and one Türkiye email to sahibinden and arabam asking about deep-link or affiliate terms. These are drafts only; Menno approves before anything is sent.
3. **Catalogue backlog note** (WS3): about 10 market-only variants per country (Togg T10X/T10F, KGM Torres EVX, Porter/Bongo EV, Ray EV, Casper Electric, plus Korean-market battery variants), and a `range_mo_e_kr` fact type proposal for the coordinator. No schema change now.

### Open items for whoever picks this up
- Read the TÜİK, EPDK and ODMD terms of use; read the kogl.or.kr Type 1 text and the data.go.kr portal policy ([link](https://www.data.go.kr/ugs/selectPortalPolicyView.do), not opened); work out which KECO fields carry third-party rights.
- Find out whether MOLIT/KOTSA publish national registrations by make and model (try stat.molit.go.kr from another network).
- Check whether EPDK's 2026 real-time price rule leads to a central open feed.

---

## 4. Ready-to-import `data/sources.yaml` rows

```yaml
  - {id: keco-ev-chargers, name: "KECO EV charger info API (data.go.kr 15076352)", owner: Korea Environment Corporation (KR), licence: KOGL-Type-1 (to confirm; third-party rights flagged), access: api, cadence: daily, status: blocked,
     terms: "Metadata licence 'KOGL Type 1 + third-party rights' read 2026-11-15. Confirm KOGL text and which fields are third-party before active. Needs a data.go.kr service key (account: ask Menno)."}
  - {id: keco-fast-chargers, name: "KECO public fast-charger list (data.go.kr 15156662)", owner: Korea Environment Corporation (KR), licence: data.go.kr no-restriction (to confirm), access: api, cadence: yearly, status: blocked,
     terms: "Metadata says '이용허락범위 제한 없음', read 2026-11-15. Confirm portal policy text."}
  - {id: kr-municipal-registrations, name: "Korean municipal registrations by fuel (data.go.kr, e.g. 15011919 Daejeon)", owner: various KR local governments, licence: data.go.kr no-restriction (to confirm), access: bulk, cadence: monthly, status: blocked,
     terms: "Fuel/vehicle-type counts only, no models. Country-page context only."}
  - {id: molit-registrations, name: MOLIT vehicle registration statistics, owner: Ministry of Land, Infrastructure and Transport (KR), licence: unknown (to confirm), access: manual, cadence: monthly, status: blocked,
     terms: "stat.molit.go.kr unreachable 2026-11-15. Single facts cited via press release only."}
  - {id: kaizenyou, name: Kaizen-You used-car transfer stats, owner: Kaizen-You Data Research Institute (KR), licence: none, access: manual, cadence: quarterly, status: blocked,
     terms: "Private; cite single facts by URL + date only."}
  - {id: tuik-motor-vehicles, name: "TÜİK Motorlu Kara Taşıtları (monthly)", owner: Turkish Statistical Institute, licence: unknown (to confirm), access: bulk, cadence: monthly, status: blocked,
     terms: "Fuel shares of registrations and fleet; portal now veriportali.tuik.gov.tr. Reuse terms not found 2026-11-15."}
  - {id: epdk-charging-stats, name: "EPDK Şarj Hizmeti Piyasası monthly statistics", owner: Energy Market Regulatory Authority (TR), licence: unknown (to confirm), access: manual, cadence: monthly, status: blocked,
     terms: "Sockets AC/DC, MW, kWh, operators. No open API found 2026-11-15."}
  - {id: odmd, name: ODMD monthly sales by model, owner: Otomotiv Distribütörleri ve Mobilite Derneği (TR), licence: none, access: manual, cadence: monthly, status: blocked,
     terms: "Press tables only; cite single facts by URL + date."}
```
