# R-29 Competitor teardown: who already helps used-EV buyers, and where the gap is

Researched 2026-11-15 by a WS0 researcher agent. All links below were opened on 2026-11-15 unless marked otherwise. Confidence: 🟢 verified on the competitor's own page · 🟡 reasoned / one secondary source / inferred · 🔴 unsure or not checked. "?" in tables = not checked this session (not the same as "no").

Spec: `docs/spec/master-spec-v2.md` §1–§2 (job: pick the right EV, find a good one, don't buy a lemon).

## Question

Who competes for the used-EV buyer's attention in our markets, what do they give that buyer, what do they say about data sources and reuse, and which gaps can EV Shortlist own?

## Answer

**No one joins the three things a used-EV buyer needs: a model catalogue that includes old generations, used prices per generation and country, and battery-health context.** Each competitor owns one piece. 🟡

- **Spec catalogues (EV Database, EVKX)** are strong on specs, real-world range and charge curves, but are **new-car shaped**: EV Database lists only cars "available to order" in its public site and shows no used prices; EVKX has no used features at all and its roadmap doesn't add any. 🟢
- **Listing aggregators (AutoUncle, Carwow, Electrifying)** have the cars and a per-listing price rating, but **no battery or generation context**: AutoUncle rates on asking prices against 100+ generic factors (fuel type, mileage, trim) and its EV page only says the battery "should be thoroughly checked". 🟢
- **Battery specialists (Aviloo, Recurrent; ADAC/ANWB as resellers of tests)** sell per-car health tests or reports, mostly **B2B or via partners**, and Recurrent is **US-only** by its own terms. None publishes open, model-level degradation curves for European buyers. 🟢

**Where we win:** be the free, multi-country, generation-aware "context layer" that sits *before* the listing click and *before* the battery test, and links out to both. **Where we must not compete:** hosting listings, per-car price ratings at AutoUncle's scale, our own battery testing hardware, or finance/leasing commissions. 🟡

Licence takeaway: **none of them offers open data we can copy.** EV Database's free tier needs prior permission, forbids automated collection and requires unmodified republishing; EVKX publishes no licence yet; Recurrent's terms forbid scraping and resale. This confirms principle 7 (derived, not copied). 🟢

## 1. EV Database (ev-database.org, /nl, /uk, /de)

| Item | Finding | Conf. |
|---|---|---|
| What it is | Free EV spec database run by a Dutch company (Schiphol-Rijk, KvK 66166349). Fast filterable table; "cheatsheets" ranking all cars by range, consumption, speed, towing, acceleration, price per km of range. | 🟢 |
| Countries / languages | Country selector: European Overview, Netherlands, UK, Germany; metric or imperial. Country versions are paths (`/nl`, `/uk`, `/de`) on the .org domain; NL cheatsheets are in Dutch. Separate `.nl`/`.uk` domains not checked. | 🟢 / 🔴 domains |
| Real-world range | Its own "practical range" model: six scenarios (city / highway at 110 km/h / combined × winter −10 °C with heating / summer 23 °C no climate), plus one headline figure at 9 °C, 88 km/h average. Tuned against "practical tests from various sources". | 🟢 |
| Data sources stated | Only general: "aims to gather as much real-world data as possible"; model "checked against practical tests from various sources". No per-number source shown on the pages read. | 🟢 |
| For used buyers | Little. Inclusion criteria require a car to be "available to order for the general public", BEV, M1, UK-available, ≥500 built; trims aren't listed separately. A discontinued-vehicle archive exists **in the paid data product**, not clearly on the public site. No used prices or listings seen. | 🟢 criteria / 🟡 archive on site |
| Business model | "Placing as few ads as possible to cover running costs"; says it is independent, not funded. Plus a **paid data export** (JSON endpoint, 10 modules, priced on request, registered companies only; clients: automotive, CPOs, research, media, consultancies). Local market data incl. pricing for DE, NL, UK. | 🟢 |
| Licence / terms | No ToS page; [Disclaimer](https://ev-database.org/disclaimer) only ("make no representations or warranties of any kind"). [Data services](https://ev-database.org/data-services-api): **"Free Use" needs prior permission, manual copying only, no automated collection, publish unmodified with attribution and link.** Paid use: attribution not required. | 🟢 |
| What a used buyer misses | Older generations and trims as a buyer saw them; used price per generation/country; battery degradation; known issues; sources per number; France/Belgium/other markets. Our spec also names comparisons resetting as its biggest UX pain (not re-verified here). | 🟢 / 🟡 UX |

## 2. EVKX (evkx.net)

| Item | Finding | Conf. |
|---|---|---|
| What it is | "Open-source platform" launched March 2023: EV specs, filters (drivetrain, charging speed, regen modes, bidirectional), data-driven top lists, editorials and buyer/ownership guides, curated creator videos. Operator not named on the About page. | 🟢 |
| Countries / languages | English plus 12: DA, SV, NO, FR, ES, DE, NL, PT-PT, PT-BR, FI, IT, PL. Availability tracked per trim and region; charge port type per country. | 🟢 |
| Data model | Modular JSON per model/variant (brand, variant, body, platform, production status). Battery size, cell type, layout; DC charge curves by SoC with **per-curve source (public test / manufacturer / EVKX testing) and status (Verified / Estimated / In progress)**; WLTP, EPA and real-world range fields; V2L/V2G/V2H. No separate generation level described. | 🟢 |
| Data sources stated | "Curated using verified data"; corrections via GitHub or contact. The "How we collect data" page failed to load. Only charge curves carry explicit source tags. | 🟢 / 🔴 collection page |
| For used buyers | Nothing used-specific on home or About. Roadmap: accounts, **EV Issue Tracker (known issues per model/variant)**, forums, data-quality reports. No used prices, battery health or listings on the roadmap. | 🟢 |
| Business model | Not stated. "Partner" and "Curated" creator posts; API in early access. | 🟢 (absence) |
| Licence / terms | No ToS link found. [API page](https://evkx.net/about/api): no licence published, "evaluating licensing options, open data policies, and partner tiers". Data model to be open-sourced, beta planned H2 2026. | 🟢 |
| What a used buyer misses | Everything after "which spec": used prices, generations as a unit, battery health, listings. **Closest overlap with our catalogue + bidirectional + charge-curve work, and possibly a future open-data source or partner** (licence still unknown). | 🟡 |

## 3. AutoUncle (autouncle.co.uk, .de, .it, .es, .pt, .fi, …)

| Item | Finding | Conf. |
|---|---|---|
| What it is | Danish (AutoUncle ApS, Aarhus, founded 2010) used-car search engine and price checker. Indexes listings from many sites; each listing gets a label from "Super price" to "Expensive"; links out ("View the car"). Doesn't sell cars or take commission. | 🟢 |
| Countries | 14 European consumer markets; B2B page: 10M+ live listings, 8.6M evaluated daily from 2,600+ websites. FAQ says 12 countries (older text). | 🟢 |
| Price method | Statistical comparison with similar cars currently for sale, 100+ factors (make, model, year, mileage, trim, engine, fuel type, gearbox); **asking prices, not transaction prices**. | 🟢 |
| EV features | Electric filter; listings show estimated range, power, kWh/100 km. **No battery, SoH, generation or charging filter seen**; page says the battery "should be thoroughly checked". UK electric search: ~41,000 cars. | 🟢 |
| Business model | Dealers use it as a lead generator; traffic partnerships with marketplaces (partner keeps "ownership of the visitor, the conversion and the data"); widgets (e.g. autobörse.de, Facebook Marketplace comparisons); Enterprise pricing tools and APIs; paid consumer features (Sales Prices, Car Valuation, Sales Times). | 🟢 |
| Licence / terms | [Terms of Service for AutoUncle Users](https://www.autouncle.it/it/purchase_terms): covers paid features; logins "strictly personal". No scraping clause or governing law found in that page. Privacy: [autouncle.co.uk/en-gb/privacy](https://www.autouncle.co.uk/en-gb/privacy) (not opened). | 🟢 / 🔴 privacy |
| What a used buyer misses | Whether the price is fair *for this battery and generation*; real winter range; charge speed; known issues; a battery check. AutoUncle's rating treats an EV like any car. **Also a potential partner** (traffic and price data, R-03 layer 1). | 🟡 |

## 4. Recurrent (recurrentauto.com)

| Item | Finding | Conf. |
|---|---|---|
| What it is | US battery-analytics company. **Recurrent Reports** per VIN: remaining battery warranty, current expected max range, projected range change; **Range Score** (e.g. 97 = 97% of original range); weather impact; dealer "Range Verified" label. Partnership with Experian AutoCheck (Jan 2023). | 🟢 |
| Data sources stated | VIN-level history and battery data, "more than 40 million real-world EV trips"; a "Research Fleet" of owners who connect their car via the manufacturer login through **Smartcar**; proprietary algorithm. | 🟢 |
| Business model | Month-to-month **dealer subscription** (fees not shown); reports offered to shoppers at partner dealers and via Experian. | 🟢 |
| Countries | [Subscription terms](https://www.recurrentauto.com/about/subscription-terms): "intended for users in the United States"; Washington State law. | 🟢 |
| Licence / terms | Forbids "web scraping, screen scraping, or other similar practices"; reports may not be sold, rented or licensed. | 🟢 |
| What a European buyer misses | Everything: US only. **Most relevant as a model for us**: connected-car owner fleet → model-level degradation and winter range (our Owner logs, spec §10, and battery context, §1 stage 5). Smartcar also covers Europe (not checked here). | 🟢 / 🔴 Smartcar EU |

## 5. Aviloo (aviloo.com), and the auto clubs that resell tests (ADAC, ANWB)

| Item | Finding | Conf. |
|---|---|---|
| Aviloo products | Austrian, brand-neutral battery diagnostics independent of manufacturer readouts. **FLASH test** (B2B licence, box, ~3 min, ±3% vs PREMIUM); **PREMIUM test** (B2C, rented box, full discharge cycle, SoH, range, certificate; sold via partners like auto clubs); **certificate** with QR verification, API into remarketing systems; **warranty** (1 year / 20,000 km / €3,000 if SoH falls below a car-specific limit), B2B only, UK and Ireland first, Europe "over the coming weeks". Claims 500,000+ tests, >95% EV/PHEV coverage. No retail prices on the pages read. | 🟢 |
| Aviloo terms | [Terms and conditions](https://aviloo.com/en/terms-and-conditions), [B2B licence terms (PDF)](https://shop.aviloo.com/files/webshop_b2b/ENG_General%20License%20Terms%20Standard%20V2_25%20%281%29.pdf). Linked from the business page, not opened. | 🔴 contents |
| ADAC (DE) | [Used-EV buying page](https://www.adac.de/rund-ums-fahrzeug/elektromobilitaet/kaufen/elektroautos-gebraucht-kaufen/): "herstellerunabhängigen und neutralen Batteriecheck" with Aviloo; free **Gebrauchtwagen-Informationsblätter for ~25 EV models** (known defects, breakdowns, recalls, history, workshop and running costs); Autotest real consumption incl. charging losses; a used-EV purchase contract; an online price calculator. **No listings**: points to mobile.de and AutoScout24. Funds itself through membership and services (inferred). | 🟢 / 🟡 model |
| ANWB (NL) | [EV accu check](https://www.anwb.nl/auto/elektrisch-rijden/elektrische-autos/ev-accu-check): battery test with **DEKRA**, ~15 minutes, 10% discount (member-benefit link). Report: SoH, remaining capacity, comparison with similar used EVs, negotiating position. Warns that a dealer's SoH comes from the manufacturer and isn't independent. Price not shown. | 🟢 |
| What a used buyer misses | Tests are per car, paid and after you've found the car. No public model-level "what SoH is normal at 5 years / 100,000 km for this generation" view. ADAC's 25 info sheets are the best known-issues content seen, but German-only and only 25 models. | 🟡 |

## 6. UK editorial + marketplace sites (Electrifying.com, Carwow)

| Item | Finding | Conf. |
|---|---|---|
| Electrifying.com | UK EV reviews (incl. used and long-term), used-EV marketplace, buying guide, "best used EVs under £20k", "Help me choose", calculators, glossary, saved "Showroom". Revenue: ads and finance commission (Electrifying Limited is an FCA appointed representative and credit broker). Campaigns for mandatory battery certificates; survey with the AA of 13,000+ drivers: **only 3% felt confident buying a used EV; 38% said an independent battery certificate would help** ([article, 25 Aug 2026](https://www.electrifying.com/blog/article/electric-groups-call-for-used-battery-health-checks)). ToS linked in footer, not opened. | 🟢 / 🔴 ToS |
| Carwow | UK used marketplace incl. electric, valuations, sell-my-car, history check, leasing and finance. Credit broker; dealer and partner commissions. Editorial on battery health ([20 Feb 2026](https://www.carwow.co.uk/news/10307/used-ev-battery-health-study-uk), citing Generational's index of 8,000+ EVs: average SoH 95.15%, median 85% at 8–9 years) tells buyers to get a certificate elsewhere; no battery data on listings seen. | 🟢 |
| What a used buyer misses | UK only; finance-driven; no cross-border, no per-generation price bands, no sourced spec data. | 🟡 |

Autovista/Schwacke: only a 2020 article found ([Autovista24](https://autovista24.autovistagroup.com/?p=10687)) on battery certificates lifting remarketing value (up to €450 per compact car) and BEV residual-value forecasts; B2B, no consumer product seen. Not a direct competitor; a possible B2B data buyer later. 🟡

## Gap table

✓ = has it · partial = limited (see note) · ✗ = not seen on pages read · ? = not checked.

| Feature (for a used-EV buyer) | EV Database | EVKX | AutoUncle | Recurrent | Aviloo | ADAC / ANWB | Electrifying / Carwow | **EV Shortlist (spec)** |
|---|---|---|---|---|---|---|---|---|
| Full EV spec catalogue | ✓ | ✓ | ✗ | ✗ | ✗ | partial (tests) | partial (reviews) | ✓ Core |
| Grouped by generation | ? | ✗ (model/variant) | ✗ | ✗ | ✗ | partial (info sheets) | ✗ | ✓ Core |
| Older / discontinued models on site | partial (paid archive) | ? | ✓ (listings) | ✓ (US) | ✓ | partial | ✓ (listings) | ✓ Core |
| Real-world range incl. winter | ✓ | partial (field) | ✗ (WLTP-ish estimate) | ✓ (US, weather) | partial (cert) | ✓ ADAC test | ? | ✓ Core |
| Charge curves / km per hour | ? | ✓ (sourced) | ✗ | ✗ | ✗ | ? | ? | ✓ Core |
| Bidirectional (V2L/V2G) | ? | ✓ | ✗ | ✗ | ✗ | ? | ? | ✓ Core |
| Source shown per number | ✗ | partial (curves) | ✗ | ✗ | n/a | ✗ | ✗ | ✓ Core |
| Used price band per generation × country | ✗ | ✗ | partial (per listing, asking) | ✗ | ✗ | partial (ADAC calculator, DE) | partial (valuation, UK) | ✓ Core→Next |
| Per-listing price rating | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | partial | Next (Gem Score) |
| Listings (link-out) | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ (links to portals) | ✓ (own marketplace) | ✓ Core (links) |
| Cross-border view | ✗ | partial (per-market data) | partial (separate country sites) | ✗ | ✗ | ✗ | ✗ | ✓ Core |
| Battery health test per car | ✗ | ✗ | ✗ | ✓ (US report) | ✓ | ✓ (resold) | ✗ | ✗ (link out) |
| Model-level degradation context | ✗ | ✗ | ✗ | partial (US, behind reports) | partial (data, not public) | partial (articles) | partial (articles) | Next |
| Known issues / recalls per generation | ✗ | planned | ✗ | ✗ | ✗ | partial (ADAC 25 models, DE) | partial (reviews) | Next |
| Saved compare / accounts | ? | planned | partial (paid login) | n/a | n/a | ✗ | partial (Showroom) | ✓ Core |
| Languages | EN, NL (DE?) | 13 | per country | EN | 11 | DE / NL | EN | 6 (EN NL DE FR ES IT) |
| Open data licence | ✗ (permission, manual) | ✗ yet (planned) | ✗ | ✗ (no scraping) | ✗ | ✗ | ✗ | ✓ CC-BY summary |
| Paid API / data | ✓ | early access | ✓ Enterprise | ✓ dealers | ✓ API | ✗ | ✗ | Later |

## Where we win

1. **Generation-aware used context in one place.** Catalogue + used price band per generation and country + battery and known-issue context, before the listing click. Nobody combines these. 🟡
2. **Older cars treated as first-class.** EV Database's public inclusion rules are "available to order"; the used market is 2015–2023 cars. 🟢 (rule) / 🟡 (implication)
3. **Traceable numbers and an open summary licence.** No competitor shows a source per value (EVKX only for charge curves) or offers open data. 🟢
4. **Continental, multi-language, cross-border.** UK sites are UK-only; ADAC/ANWB are national; Recurrent is US; AutoUncle keeps country sites separate. FR/BE/ES/IT used-EV buyers are underserved. 🟡
5. **The confidence gap is real and measured.** 3% of UK drivers confident buying used EVs; 38% want an independent certificate (Electrifying/AA). Model-level "what's normal for this generation" content plus a link to an Aviloo/DEKRA/ADAC/ANWB test answers that directly. 🟢 (survey) / 🟡 (our answer)

## Where we must not compete

1. **Hosting listings or a marketplace** (Carwow, Electrifying, portals): spec non-goal; link out. 🟢
2. **Per-listing price rating at scale** (AutoUncle: 8.6M listings a day from 2,600+ sites). Partner instead (traffic, widget or price data); our Gem Score stays EV-specific and Next. 🟡
3. **Battery testing hardware or certificates** (Aviloo, DEKRA, Recurrent): partner, link, maybe affiliate; an affiliate must never change a ranking (principle 5). 🟡
4. **Finance and leasing commission** (Electrifying, Carwow): spec non-goal. 🟢
5. **Copying EV Database or EVKX data.** EVDB free use forbids automated collection and modification; EVKX has no licence yet. Watch EVKX: if it opens its data under a compatible licence it becomes a source, not a rival. 🟢

## Follow-ups (suggested, not done)

- Check EVKX's licence when the data model beta ships (H2 2026); add to the open-data source list if compatible. 🟡
- AutoUncle as a layer-1 partner (R-03): traffic partnership page invites "Let's talk". Draft outreach for Menno's approval (WS5). 🟡
- Ask ADAC/ANWB/Aviloo about linking or embedding their battery test (WS5). 🟡
- Not checked this session: EV Database vehicle pages (charge curves, generations, compare), separate ev-database `.nl`/`.uk` domains, AutoUncle privacy and full ToS, Aviloo ToS contents, Electrifying ToS, Smartcar EU coverage. 🔴

## Sources (opened 2026-11-15)

- EV Database: [contact/about](https://ev-database.org/contact), [disclaimer](https://ev-database.org/disclaimer), [data services](https://ev-database.org/data-services-api), [range cheatsheet](https://www.ev-database.org/cheatsheet/range-electric-car), [practical range method (NL)](https://ev-database.org/nl/informatie/praktische-actieradius-elektrische-auto), [inclusion criteria (UK)](https://ev-database.org/uk/missing-vehicles)
- EVKX: [home](https://evkx.net/), [about](https://evkx.net/about/), [API](https://evkx.net/about/api), [roadmap](https://evkx.net/about/roadmap), [data model](https://evkx.net/about/data-model)
- AutoUncle: [UK electric search](https://www.autouncle.co.uk/en-gb/cars_search/f-electric), [FAQ](https://www.autouncle.co.uk/en-gb/faq), [autouncle.com](https://www.autouncle.com/), [about (careers)](https://careers.autouncle.com/pages/about-us), [B2B traffic](https://b2b.autouncle.com/autouncle-traffic-marketplaces), [terms (IT)](https://www.autouncle.it/it/purchase_terms)
- Recurrent: [coverage news (27 Feb 2023)](https://www.recurrentauto.com/news/recurrent-expands-coverage-used-ev), [Experian alliance (26 Jan 2023)](https://www.recurrentauto.com/news/new-experian-alliance-with-recurrent-empowers-dealers), [subscription terms](https://www.recurrentauto.com/about/subscription-terms), [research support](https://www.recurrentauto.com/research-support)
- Aviloo: [business](https://aviloo.com/en/aviloo-business), [warranty](https://aviloo.com/en/aviloo-warranty)
- ADAC: [used EV buying](https://www.adac.de/rund-ums-fahrzeug/elektromobilitaet/kaufen/elektroautos-gebraucht-kaufen/) · ANWB: [EV accu check](https://www.anwb.nl/auto/elektrisch-rijden/elektrische-autos/ev-accu-check)
- Electrifying: [battery certificate article](https://www.electrifying.com/blog/article/electric-groups-call-for-used-battery-health-checks) · Carwow: [battery health study](https://www.carwow.co.uk/news/10307/used-ev-battery-health-study-uk) · Autovista24: [battery certificates (14 Dec 2020)](https://autovista24.autovistagroup.com/?p=10687)

Could not open: ev-database.org home, recurrentauto.com home, autouncle.nl home (fetch blocked by the tool's link check), evkx.net data-collection page and AutoUncle "used EV market in numbers" (site error). Findings above don't rely on them.
