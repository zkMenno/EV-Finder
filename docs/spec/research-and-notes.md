<!-- Mirror of the claude.ai spec doc, tab "Research & notes" (rev 29), exported 2026-11-15 by WS0. For builders this repo copy wins; product changes start in the doc and WS0 mirrors them here. -->

# Used-EV Finder — Product Spec

Nov 14, 2026 · @Menno van Ginkel

## TL;DR

Build a used-first EV finder for Europe: every model grouped by generation, linked to live second-hand listings and price history per country, with a Gem Score that surfaces under-priced ex-lease cars with healthy batteries.

- **The gap:** ev-database.org has excellent spec data but is a new-car catalogue. It has no used listings, no generation view, no depreciation curves and no battery-health signal.
- **The wedge:** the off-lease wave. The 2020–2022 EV cohort (Zoe, e-208, Model 3, Spring) is now hitting the used market in volume via lease returns and fleet renewals.
- **The hard constraint:** ev-database.org forbids crawling and only licenses data to registered companies, unmodified, with attribution. Scraping it is off the table. Decision: build on open specs plus our own real-world range and charge-speed stats, and cross-check against EV Database by hand.
- **MVP scope:** Europe and UK first (NL, DE, FR, UK), \~40 high-volume models, generation pages, shortlists and saved comparisons, Top 10 rankings, then listings, price bands and Gem Score. Later: US, China, Australia, Southeast Asia.

Confidence key used in this doc: 🟢 verified from a source, 🟡 reasoned estimate, 🔴 unsure, needs checking.

## Audit of ev-database.org

The data is the moat; the interface is a single long list of cards with filters bolted on. [Homepage](https://ev-database.org) reviewed 2026-11-14.

**What it does well** 🟢

- Deep, consistent specs: real-world range, 1-stop range, Wh/km, usable battery, DC peak, AC kW, towing, cargo, weight, V2L/V2H/V2G, heat pump, chemistry (LFP/NCA/NMC).
- Useful derived metrics: price per km of range, 1-stop range.
- Rich filter set (segment, body, availability, \~80 makes, 9 numeric ranges) and 17 sort orders.
- Country prices for NL, UK, DE; metric/imperial toggle; saved filters; 4-car compare.
- Keeps discontinued models, which is the raw material for a used-car product.

**UX problems**

| Problem | Effect | Fix in our version |
| --- | --- | --- |
| One flat list, cards packed with \~15 numbers, no hierarchy | Hard to scan; everything looks equally important | Card shows 4 hero numbers chosen by the user's goal; rest on hover/detail |
| Up to 3 prices per card with no country label | Reader can't tell which price is which | One price in the user's chosen country + currency, others on demand |
| Unexplained codes (V2XLH, asterisks), no legend | Jargon wall for non-experts | Inline glossary chips, plain-language badges ("Can power your house") |
| Filters hidden under "More filters", duplicate controls | Power users fine, everyone else lost | Goal-based presets first ("Family car under €20k used"), advanced drawer second |
| Placeholder states ("- €", "Loading vehicles...") | Feels broken on slow connections | Skeleton loaders, server-rendered first page |
| Each model-year variant is its own card | 2019 and 2021 Model 3 look like unrelated cars | Model → Generation → Variant hierarchy (next sections) |
| Inconsistent naming ("Škoda" vs "Skoda") | Search misses | Canonical make/model IDs with aliases |

**Missing features**

- No used listings or used prices, anywhere.
- No generation grouping or "what changed between years" view.
- No depreciation or price history.
- No battery degradation data or SoH signal.
- No total cost of ownership (energy, insurance, tax by country).
- No alerts ("tell me when a 2021+ Ioniq 5 under €25k with heat pump appears").
- No buyer's checklist per model (known faults, recalls, software support status).

## Market opportunity

Used EVs are now cheap, plentiful and confusing, and the main trust gap is the battery.

- **Supply wave** 🟢 The first mass-market EVs (2020–2022) are arriving on the used market via lease returns and fleet renewals ([Electra](https://www.go-electra.com/ca/newsroom/used-electric-cars-with-prices-falling-is-now-the-time-to-take-the-plunge/)). In France the average used EV was €22,955 at end-2025, close to €20k below an equivalent new car, and La Centrale's used-EV listings grew 38% in a year.
- **Heavy depreciation, now stabilising** 🟢 UK 2022 EVs fell \~63% from list to 2026, versus 38% for petrol ([AutoUncle](https://www.autouncle.co.uk/en-gb/insights/market-analysis/uk-used-ev-stock-shrinks-prices-climb-2026-08/)). UK used-EV prices turned upward again from May 2026 ([Electric Car Scheme / Autotrader](https://www.electriccarscheme.com/blog/used-electric-car-prices-are-falling-fast)). Takeaway: price timing matters, so price history per model is a real feature, not decoration.
- **Big price gaps between countries** 🟢 Used EVs from low-RV markets like Germany are moved to the Nordics where used demand is stronger ([JD Power/Autovista](https://www.dev.jdpower.com/insight-segment/aftermarket/page/2/)). Cross-border price comparison is a buyer feature that dealers already exploit.
- **Battery trust gap** 🟢 Same model and mileage can differ by up to 13.5% in state of health ([AVILOO study](https://www.am-online.com/news/why-two-identical-used-evs-shouldn-t-have-the-same-price-ad-feature)). Certified used EVs sold up to 36% faster in AVILOO's 2024 study. Ayvens Carmarket now attaches SoH certificates to its ex-lease EVs in six EU countries ([Ayvens](https://www.ayvens.com/en-fi/about-us/news/battery-state-of-health-certification-for-used-evs/)).
- **Regulatory tailwind** 🟢 The EU Battery Passport becomes mandatory on 18 Feb 2027 for new EV batteries; SoH reporting in the passport phases in from Aug 2028 ([tracker](https://esprregistry.pages.dev/battery-delegated-act-tracker)). It only covers batteries placed on the market after that date, so the 2018–2026 used stock gets nothing from it 🟡. That gap is exactly where this product sits for the next 5+ years.

**Who it's for:** private buyers with €10–30k, first-time EV owners, and cross-border-curious buyers in NL/BE/DE/FR. Secondary: small independent dealers sourcing stock.

## Global markets

About 40 markets are worth covering, in five tiers. The used-EV boom of 2026 is real and wide: global EV sales passed 20 million in 2025, a quarter of new cars ([IEA](https://www.iea.org/reports/global-ev-outlook-2026/trends-in-electric-cars)), and the oil-price shock from the Strait of Hormuz disruption (from 28 Feb 2026) pushed used-EV demand up in most markets at once ([AutoUncle](https://www.autouncle.co.uk/en-gb/insights/market-analysis/used-ev-sales-surge-europe-april-2026/)).

**Two kinds of used-EV market** (this changes the product):

- **Home-grown supply:** used EVs come from the country's own new-car and lease sales (EU core, UK, US, China, Australia, Korea). Needs: local listings, price index, battery health.
- **Import-fed:** used EVs mostly arrive from abroad (Poland, Ukraine, New Zealand, Jordan, Nepal, Ethiopia). Needs: source-country prices, import cost calculator, age and tax rules, right- vs left-hand drive.

**Readiness score per market** (1–5 each): used-EV supply depth, momentum, price affordability, data access (structured listings, registries), and how cheaply we can serve it (language, existing sources).

| Market | Tier | Key signal | Type |
| --- | --- | --- | --- |
| Netherlands, Germany, France, UK, Belgium | 1 – launch | Germany's used-BEV transactions +126% YoY (Apr 2026); UK sold 197,653 used EVs Jan–Jul 2026 vs 288,350 in the US ([EV Fleet World](https://evfleetworld.co.uk/?p=69167)); Belgium's company-car EVs now hitting lease end ([NewMobility](https://newmobility.news/en/2026/04/28/belgiums-company-car-fleet-turns-electric-faster-than-anywhere-else/)) | Home-grown |
| Denmark, Sweden, Finland, Norway | 1b – early add | Used-BEV share of used sales Apr 2026: DK 63.4%, FI 26.3%, SE 20.1% | Home-grown, exporters |
| Portugal, Spain, Austria, Switzerland, Ireland, Italy | 2 – Europe expansion | PT 20.0% used-BEV share; Spain used-BEV +93% YoY; Italy's new-BEV wave reaches used stock from late 2027 | Home-grown |
| Poland | 2 | Germany supplies 52.2% of used imports ([WBJ](https://wbj.pl/imports-of-used-cars-fell-by-89procent-yy-in-april-lowest-in-3-years/post/149768)); EVs exempt from excise | Import-fed (from DE/NL) |
| Ukraine | 2 (volatile) | 56,610 EVs imported in 2024; collapsed after 20% VAT returned Jan 2026, recovering ([Interfax](https://en.interfax.com.ua/news/economic/1200126.html)) | Import-fed (EU, US) |
| United States | 3 – big English market | Record 3.3% of used sales in Sept 2026, avg listing $36,767 ([InsideEVs](https://insideevs.com/news/812497/record-used-ev-sales-september-2026/)); lease returns ramping to 2028 | Home-grown |
| Canada | 3 | Used EVs peaked at 5.7% of used sales in April; sell faster than any fuel type ([Clutch](https://clutch.ca/blog/posts/clutch-used-car-pricing-report-jun-2026)) | Home-grown |
| Australia | 3 | Used EV sales +54.6% H1 2026 ([NRMA](https://www.mynrma.com.au/open-road/news/2026/used-ev-sales-surge)); new BEV share 24.2% in Sept | Home-grown, RHD |
| New Zealand | 3 | Used EV imports +136% YTD, mostly Leafs from Japan ([AutoTrader NZ](https://autotrader.co.nz/news/most-popular-used-imports-october-2026)) | Import-fed (Japan), RHD |
| South Korea | 3 | Used EV transactions +48.7% in Q1 ([Herald](https://mbiz.heraldcorp.com/article/10783479)) | Home-grown, exporter |
| China | 3 (partner only) | 1.6M used NEVs in 2025; used NEV penetration 11.6% by Apr 2026 ([China Daily](https://global.chinadaily.com.cn/a/202607/21/WS6a5f22c1a310986e2b466771.html)) | Home-grown; closed ecosystem (Guazi, Dongchedi) |
| Singapore, Vietnam, Thailand | 4 – emerging boom | New BEV share Q1 2026: SG 53%, VN 41%, TH 33% ([SCSP](https://www.scsp.ai/?p=7166)); used market still thin, early cohort 2022–23 | Home-grown (future), RHD for SG/TH |
| Indonesia, Malaysia, Philippines | 4 | Indonesia 117,108 EV sales H1 2026, region's largest ([SeasiaStats](https://seasiastats.com/statistic/southeast-asian-countries-with-the-highest-ev-sales-bQXU3)) | Home-grown (future), RHD |
| Türkiye | 4 | BEV \~19% of new sales; EV fleet nears 500,000 ([Hürriyet](https://www.hurriyetdailynews.com/turkiyes-electric-car-fleet-nears-500-000-228152)) | Home-grown |
| Israel | 4 | BEV share fell from 25% (2024) to \~12%; importers dumped unsold EVs as "used" ([Ynet](https://www.ynetnews.com/business/article/sjmcc7m31g)) — a bargain market | Home-grown |
| Jordan | 4 | EVs are 55% of vehicle imports; 150,000+ EVs on the road ([trade.gov](https://www.trade.gov/market-intelligence/jordan-automotive-ev-market-trends-and-policy-shifts)) | Import-fed (China, Korea) |
| Brazil | 4 | 473,362 electrified light vehicles; used BEVs now sell faster than combustion cars ([AutoPapo](https://autopapo.com.br/curta/eletricos-quebram-tabu-e-ja-vendem-mais-rapido-que-carros-flex-no-mercado-de-seminovos/)) | Home-grown |
| Mexico, Colombia, Uruguay, Costa Rica, Chile | 4 | Uruguay over 40% EV share, Costa Rica 22%, Colombia over 20% in Q2 2026 ([CleanTechnica](https://cleantechnica.com/2026/08/05/latin-america-ev-sales-report-10-ev-market-share-surpassed-in-q2/)) | Home-grown (young) |
| Ethiopia, Nepal, Sri Lanka, India, Japan | 5 – watchlist | Ethiopia banned petrol/diesel car imports; Nepal 63,280 EVs registered; Japan a supply source, not a buyer market | Mixed |

**Expansion order** 🟡

1. **Europe core + UK** (tier 1): one spec database, AutoScout24-type sources cover DE, AT, IT, ES, FR, BE, NL, LU.
2. **Rest of Europe** (tiers 1b–2): mostly translation and new listing partners; add Poland and Ukraine with the cross-border import calculator.
3. **US, Canada, Australia, New Zealand** (tier 3): English, big used volumes. Recurrent is the US competitor; add miles and RHD.
4. **Southeast Asia, Türkiye, Israel, Jordan, Latin America** (tier 4): Chinese and local brands dominate (BYD, VinFast, Togg), so spec coverage for those brands comes first.
5. **China and Korea** only through a local partner.

**Product changes this forces**

- Drive side (LHD/RHD) as a field and filter; Japanese-market variants (JDM Leaf) for NZ.
- Import calculator: duty, VAT and age rules per country (e.g. Jordan's 7-year limit for imported EVs, Ukraine's 20% VAT since Jan 2026).
- Miles as a display option for the US and UK; metric stays the default.
- Strong coverage of Chinese, Korean, Vietnamese and Turkish brands. 🔴 Check OpenEV coverage of these early.

## Competitor landscape

Nobody combines all three things this product needs: EV-specific specs, used-market pricing across countries, and battery health. Each competitor does one or two of them well.

| Player | Type | Markets | Steal this | Gap we fill |
| --- | --- | --- | --- | --- |
| [ev-database.org](https://ev-database.org) | EV spec database | EU, UK | Real-world range, deep filters, 1-stop range | No used market, no accounts, comparisons reset |
| [EVKX](https://evkx.net) | EV spec database + rankings | Worldwide | Rankings you can open as a search and adjust | No used market, no price data 🟢 |
| whattherange.com, evspecifications.com, evspecs.org | Spec and range sites | Mixed | Closest sites to ev-database.org by audience overlap ([Similarweb](https://www.similarweb.com/de/website/ev-database.org/competitors/)) | Not reviewed in depth 🔴 (whattherange blocks automated access) |
| [Green Cars Compare](https://greencarscompare.com/global/) | Global EV hub | Global | 1,000+ EVs, EV-vs-petrol cost calculator, comments, marketplace "coming soon" | Shallow used and price layer |
| [AutoUncle](https://www.autouncle.com/) | Used-car aggregator with price ratings | 14 EU markets | 10.6M listings rated "Super Price" to "Too Expensive", alerts, favourites, plate check, direct-to-dealer (not a marketplace) | Not EV-specific: no battery, range or charging logic |
| [Electrifying.com](https://www.electrifying.com/car-dealers-signup) | EV media + used marketplace | UK | Trusted EV expert brand, dealers pay per lead, no listing fees | UK only, media-first |
| [car360](https://octopus-used-evs.car360.co.uk/why-car360) | Used-EV retailer | UK | AVILOO or ClearWatt battery report on most cars | Sells its own stock only |
| [Recurrent](https://www.recurrentauto.com/questions/how-do-i-prove-my-evs-battery-is-healthy-when-selling) | Battery health reports | US | Free owner reports that compare a car to others of the same model and age, paid by dealers and auctions | 🟡 No European consumer equivalent at this depth |
| AutoScout24, mobile.de, Marktplaats, Leboncoin | General marketplaces | EU | Supply; their own price labels | EV buyers must do all the battery and range homework themselves |

AVILOO, Generational, ClearWatt and BCA test batteries for dealers and auctions. They are partners, not competitors.

**Positioning:** the independent place to build an EV shortlist and hunt it down. AutoUncle's independence plus ev-database.org's EV depth plus Recurrent's battery focus, for Europe and the UK first.

## Business model

Keep the product free for buyers and earn from the seller and partner side, like AutoUncle and Electrifying.com do. Trust is the product, so paid placement never changes a Gem Score or a ranking.

| Revenue line | Who already does it | Fit | When |
| --- | --- | --- | --- |
| Lead fees from dealers and lease remarketers | Electrifying.com: no listing fees, dealers pay for leads 🟢 | High: shortlisters are ready to buy | v1 |
| Affiliate traffic to marketplaces | AutoUncle sells buyer traffic to marketplaces 🟢 | High, easy to start | v1 |
| Battery-test referrals | AVILOO, Generational, ClearWatt sell tests to dealers | High: natural next step after "I like this car" | v2 |
| Finance, leasing, insurance, home-charger referrals | Used-EV salary sacrifice and contract hire are growing fast in the UK ([The EV Report](https://theevreport.com/battery-health-certificates-uk-used-evs)) | Medium | v2 |
| Paid buyer tier (more alerts, cross-border alerts, price-history export) | 🟡 Untested for EVs | Medium; keep the core free | v2 |
| B2B API and widgets: price rating, EV range-for-this-car, Gem Score | AutoUncle sells a price-rating widget and valuation API to dealers, portals and DMS vendors 🟢; Recurrent sells reports via auctions and Experian 🟢 | High long-term; needs scale | v3 |
| Display ads | Common on spec sites | Low: hurts trust and speed | Avoid |

🟡 The B2B data line is probably the biggest long-term value: once you have real-world range and used prices per generation and country, dealers and marketplaces will want to embed them.

## Generations model

Use two layers: **Eras** (fixed year bands across all cars, for browsing) and **Generations** (per model, defined by real hardware changes, for correctness). Year bands alone mislead: a 2019 and a 2020 Zoe can carry a 41 or 52 kWh battery depending on build month.

**Hierarchy:** Make → Model → Generation → Variant (battery/motor/trim, by model year) → Listing (a specific used car).

**Eras** 🟡 (proposed bands, tune with data)

| Era | Years | What typically defines it | Used-buyer angle |
| --- | --- | --- | --- |
| Pioneer | up to 2017 | 16–30 kWh packs, CHAdeMO common, rarely heat pump, 40–50 kW DC | City cars under €8k; check charge port and battery lease contracts |
| Early mainstream | 2018–2020 | 40–64 kWh, CCS becomes standard, first long-range mass models | Sweet spot for value; SoH spread is widest here |
| Platform era | 2021–2022 | Dedicated EV platforms (MEB, E-GMP), heat pumps and OTA common | The ex-lease wave; best gem hunting ground |
| Maturity | 2023–2024 | LFP widespread, cheaper models, more Chinese brands, Plug & Charge | Young, warrantied, falling fast in price |
| Current | 2025+ | 800 V spreading, V2X, cheaper LFP | Near-new; compare against new-car deals |

**Generation rules** — a new generation is created when any of these change:

1. Platform or body (new chassis, new model code).
2. Usable battery capacity by more than \~10%, or battery chemistry.
3. Charging architecture (CHAdeMO → CCS, 400 V → 800 V, DC peak +30%).
4. A facelift that changes powertrain or efficiency by more than \~5%.

Minor model-year updates (heat pump added, new infotainment) stay inside a generation but appear as **change markers** on the generation timeline, so buyers can see "heat pump from MY2021 onward". 🔴 Example cut-off dates (Zoe ZE40 → ZE50, Model 3 heat pump) need checking against the spec source before launch.

**Generation page shows:** spec diff vs previous/next generation, known issues, recall list, software support status, real-world range and degradation curve, live used listings and price band per country.

## Data strategy

Build on four data layers, each with a legal route. Never scrape ev-database.org: its terms ban crawlers and automated collection, monitor traffic, and require free-tier data to be published unmodified ([EV Database Data Services](https://ev-database.org/de/data-services-api)) 🟢.

| Layer | Best source | Access | Licensing risk |
| --- | --- | --- | --- |
| Specs (range, kWh, DC, etc.) | [EV Database licence](https://ev-database.org/uk/data-services-api): JSON via custom endpoint, European Superset, companies only | Paid licence; attribution optional on paid tier | Low once licensed 🟢 |
| Specs (open fallback) | [OpenEV Data](https://open-ev-data.github.io/1.4.x/governance), dataset under CDLA-Permissive-2.0, Rust API, Docker | Free, self-host | Low; coverage of pre-2018 models 🔴 unknown |
| Specs (alt) | [Chargeprice API](https://www.github.com/chargeprice/open-ev-data) /v2/vehicles; [cars-data.com](https://cars-data.com/ar/api) EU specs incl. EV data and price history | API key / paid export | Low–medium |
| Used listings | AutoScout24, mobile.de, Marktplaats, Leboncoin, La Centrale | No public API on AutoScout24 ([dev.to](https://dev.to/devil_scrapes/how-to-scrape-autoscout24de-car-listings-germany-to-jsoncsv-15f9)); third-party scrapers exist on Apify | **High** if scraped; aim for affiliate or dealer-feed partnerships 🟡 |
| Ex-lease stock | Leasing remarketers (Ayvens Carmarket, others) | Partnership / feed | Low; strong "gem" signal 🟡 |
| Valuation & residuals | [Autovista API](https://autovista.com/?p=937) (pay-per-use, mileage-adjusted), Indicata | Paid | Low; costly 🟡 |
| Battery health | AVILOO certificates via dealer listings; user-submitted OBD/app readings; EU Battery Passport (new batteries from Feb 2027) | Partnership + crowdsourcing | Medium (data quality) |
| Registration & recalls | NL RDW open data (per-plate, first registration, recalls), UK DVLA/MOT, FR HistoVec | Open / free APIs | Low 🟡 (check per country) |
| Running costs | Eurostat electricity prices, national tax/insurance tables | Open | Low |

**Phased approach**

1. **v0 – no listing data stored.** Build generation pages on open specs and generate pre-filtered deep links into each marketplace ("2021+ Ioniq 5, heat pump, under €25k, NL"). Zero data-copying risk, useful on day one.
2. **v1 – own price index.** Collect listing prices via partner feeds or affiliate APIs; store price, mileage, first registration, country, seller type, days on market. Join to generations by make/model/year/battery.
3. **v2 – trust layer.** SoH from certificates and crowdsourcing; Autovista or Indicata valuations as a benchmark once revenue covers the cost.

**Matching listings to generations** is the core technical problem: listing titles are messy ("Kona EV 64kWh Premium"). Use a rules + fuzzy-match pipeline on make, model, year, power (kW) and battery size; flag low-confidence matches for manual review. Where a plate or VIN is available (RDW in NL), resolve exactly.

## Real-world range and charge speed

Decision: build our own real-world range and charging stats from consumption data, and use EV Database only as a manual cross-check. Range is derived, not copied, so it is ours.

```latex
\text{range}_{km} = \frac{\text{usable kWh} \times \text{SoH}}{\text{consumption}_{kWh/100km}} \times 100
```

SoH = 1 for a new car; a used listing uses its measured SoH, or the generation's expected SoH at that mileage.

**Three range numbers per variant**, because one number lies: mild weather mixed driving, cold weather motorway (worst case), and city. Each shows how many drivers it is based on.

**Consumption sources**

| Source | What it gives | Access |
| --- | --- | --- |
| Our own users ("My EV" log) | Trips and kWh per car, with season and road type | Ours; grows with the product |
| [Spritmonitor](https://www.wikipedia.org/wiki/Spritmonitor) | Crowdsourced real consumption; used by ICCT and T&E in studies, e.g. Dacia Spring \~14.1 kWh/100 km from 147 users ([elektroauto-news](https://www.elektroauto-news.net/news/7-eautos-verbrauch-sparsam-alltag-reale-daten)) | 🔴 Copyrighted by Fisch und Fischl; ask permission for systematic use |
| Published range tests (Bjørn Nyland, ADAC Ecotest) | Controlled reference points per model | 🔴 Check terms; use as calibration, cite |
| WLTP × correction factor | Fallback when data is thin | Open |

When few drivers report a model, blend toward the WLTP-based estimate and show a lower-confidence badge. Data improves as users join.

**Cross-check with EV Database:** compare a sample by hand against their published figures and review anything off by more than \~10%. Don't automate it and don't publish their numbers. 🟡 Mention it when you contact them.

**Charge speed as km per hour** (a headline stat; ev-database.org doesn't lead with it):

- **AC km/h** = AC kW ÷ consumption × 100. Example: 11 kW at 17 kWh/100 km ≈ 65 km of range per hour on a home wallbox.
- **DC km per 10 min** = average 10→80% power ÷ consumption × 100 ÷ 6. Example: 100 kW average at 18 kWh/100 km ≈ 556 km/h ≈ 93 km in 10 minutes.
- **10→80% time** and a **road-trip score** (km driven in 3 hours including one charge).

Use average charging power, not peak; peak kW flatters cars that only hold it briefly. Charging curve sources: user-submitted sessions and published tests 🔴 (licensing to check).

## Data model

Seven core tables; specs hang off Variant, market data hangs off Listing and is rolled up to Generation.

| Entity | Key fields | Notes |
| --- | --- | --- |
| Make | id, name, aliases\[\] | Fixes "Škoda/Skoda" |
| Model | id, make\_id, name, segment, body |  |
| Generation | id, model\_id, code, start\_date, end\_date, era, platform, change\_markers\[\] | change\_markers = dated events ("heat pump std", "CCS added") |
| Variant | id, generation\_id, model\_years, battery\_usable\_kwh, chemistry, motor\_kw, drive, wltp\_km, real\_range\_km, wh\_per\_km, dc\_peak\_kw, ac\_kw, connector, heat\_pump, v2l/v2h/v2g, towing\_kg, cargo\_l, new\_price\_by\_country{} | From licensed or open spec source; keep source + version per field |
| Listing | id, source, url, country, variant\_id, match\_confidence, price\_eur, price\_local, mileage\_km, first\_reg\_date, seller\_type (dealer/private/lease-remarketer), ex\_lease\_flag, soh\_pct, soh\_source, first\_seen, last\_seen, price\_history\[\] | Deduplicate across sites by VIN/plate or photo+spec fingerprint |
| PriceIndex | generation\_id, country, age\_band, mileage\_band, p25/p50/p75, n, date | Weekly snapshot; powers charts and Gem Score |
| SoHObservation | variant\_id, mileage\_km, age\_months, soh\_pct, method (certificate/OBD/app), country | Builds a degradation curve per generation |

Store every metric with **source and date**. Users trust a number they can trace; it also keeps licensing clean.

## Data pipeline and redundancy

Our own canonical database, fed by several sources per field so no single source going away breaks a page. Every value keeps its source, date and confidence.

&#91;embedded content: data pipeline · 7 stages, review loop\]

Raw data is stored untouched, so the merge can be re-run when rules change. Only conflicts, new cars and outliers reach a human.

**Sources by field** (target: at least 2 per field)

| Field group | Primary | Backup / cross-check |
| --- | --- | --- |
| Core specs (kWh, kW, dimensions, boot) | OpenEV Data | Chargeprice API, cars-data.com, manufacturer spec sheets |
| Efficiency (Wh/km) | EEA CO₂ monitoring data, open and annual 🟡 | WLTP from manufacturer sheets |
| Real-world range | Owner logs ("My EV") | Bjørn Nyland tests, fallback model (next section); EV Database by hand |
| Charging curve, 10→80% time | Bjørn Nyland tests | Owner charging sessions |
| Battery degradation | Owner SoH readings, test certificates | Bjørn Nyland degradation tab |
| New-model existence | National registries (NL RDW, UK DVLA) | OpenEV releases, unmatched marketplace listings |
| Used prices | Listing feeds | Second listing source per country |

**Merge rules per field**

1. **Priority:** each field has a ranked source list; the highest-ranked fresh value wins.
2. **Votes:** if 3+ sources disagree, take the median and flag outliers beyond ±5%.
3. **Recency:** a newer manufacturer value beats an older one (spec changes mid-year).
4. **Overrides:** a human-reviewed value is locked until a source changes it again.

**Automatic new-car detection**

- Daily: unmatched make/model strings in listings and registries create a **candidate car**.
- Weekly: pull new rows from OpenEV releases and Bjørn's sheet; diff against the database.
- The candidate is auto-filled from every source that knows it and gets a confidence score. Above a threshold it publishes as "new, data incomplete"; below it, it waits in the review queue.
- Field changes are versioned, so you can show "MY2026 update: +5 kWh" on generation timelines automatically.

## Range fallback model

Every car gets a real-world range, even with zero owner data, by falling back through five levels. The UI shows which level was used as a confidence badge.

| Level | Method | Confidence |
| --- | --- | --- |
| 1 | Owner data for this variant (30+ drivers) | High |
| 2 | Bjørn Nyland test of this exact variant, temperature-corrected | High |
| 3 | Test of a sibling variant on the same platform, scaled by usable kWh and wheel size | Medium |
| 4 | Ratio model: real ÷ WLTP for the same brand × body type × drivetrain, applied to this car's WLTP | Medium–low |
| 5 | Ratio for the body type only (e.g. all SUVs) | Low |

**Source: Bjørn Nyland's public test sheet.** He links his [range, banana-box and other test results](https://docs.google.com/spreadsheets/d/1V6ucyFGKWuSQzvI8lMzvvWJHrBS82echMVJH37kwgjE/edit?usp=sharing) under his videos. A community explorer, [tb-data](https://github.com/tordar/tb-data), shows it covers 14 test categories and 650+ vehicles, including range, degradation, cargo (banana boxes), and the 1000 km and 500 km challenges. It re-imports the sheet as CSV weekly via a GitHub Action, which is the same pattern we'd use.

**How the tests work** 🟢 Constant-speed runs at 90 km/h and 120 km/h in Norway; the 90 km/h run goes until the display shows 0%, and the 120 km/h range is estimated from consumption and battery capacity ([InsideEVs](https://insideevs.com/news/565641/bmw-i4-m50-range-cold/)). Each result records temperature and tyres. Example: VW ID.3 did 413 km at 90 km/h and 271 km at 120 km/h, a 34.4% drop ([InsideEVs](https://insideevs.com/news/445471/vw-id3-range-test-range-efficiency/)).

**Building the ratio model**

1. For every tested car: r90 = range at 90 km/h ÷ WLTP, and r120 = range at 120 km/h ÷ WLTP.
2. Normalise to \~15 °C using cars tested in both summer and winter; winter tests at around 0 °C typically cut range by 20–30% ([EV Magazine](https://www.evmagazine.eu/real-world-highway-range-which-evs-actually-go-furthest-90-and-120-kmh)) 🟢.
3. Take the median r90 and r120 per brand × body type × drivetrain, with at least 3 cars per group; otherwise drop to the body-type group.
4. Estimate an untested car's range as WLTP × group ratio, for mild, cold and motorway conditions.
5. Back-test: hide each tested car, predict it from the rest, report the error. Publish the model only if the median error is under \~10% 🟡.

**Bonus uses of the same sheet:** 1000 km challenge times feed the road-trip score directly; the banana-box test is a practical cargo measure for the "Biggest boot" ranking; the degradation tab seeds battery-health curves.

**Licence** 🔴 The tb-data README says the data belongs to Bjørn and the project isn't endorsed by him. A fetch of the sheet page suggested a CC0 tag, but I couldn't confirm it. Ask him for written permission, credit and link to him on every page that uses his numbers, and consider sponsoring him. It's good for trust, and his audience is exactly your users.

## Gem Score

A 0–100 score per listing: how much car, and how much battery confidence, you get for the price compared with the same generation in the same country. Weights are a 🟡 starting point to tune against what users actually save and click.

```latex
\text{Gem} = \min\Big(\text{cap},\ \sum_i w_i \, s_i\Big), \quad s_i \in [0, 100]
```

| Component | Weight | How it's scored |
| --- | --- | --- |
| Price vs market | 40% | Percentile of price against PriceIndex for the same generation, country, age band and mileage band. Below p25 scores high. |
| Battery confidence | 20% | Measured SoH vs the generation's expected SoH at that mileage. No SoH = neutral 50, certificate present = bonus. |
| Spec value | 15% | € per km of real-world range, heat pump, DC speed vs others in the same era. |
| Provenance | 10% | Ex-lease or fleet, dealer warranty, service history, one owner. |
| Warranty left | 10% | Months and km left on the battery warranty (typical terms 8 years / 160,000 km 🟡 vary by brand). |
| Cross-border | 5% | Cheaper than the buyer's home-country p50 after estimated transport and registration costs. |

**Red flags cap the score at 40** (shown as plain warnings, not hidden):

- Battery rental contract (common on older Renault Zoe in France) — the low price hides a monthly fee.
- CHAdeMO-only fast charging in a market where CCS dominates.
- Known battery or drive-unit defect for that generation with no repair proof.
- Manufacturer has ended app or software support.
- Price below p10 with no explanation (possible scam or damage).

Show the breakdown on every listing card as a small bar, so the score is explainable, never a black box.

## UX spec

Start from the buyer's situation, not the spec sheet. Five screens carry the product.

1. **Start / goal picker.** Three questions: budget (€), what the car is for (city, family, long trips, towing), country. Output: a pre-filtered results page. Experts skip straight to filters.
2. **Results.** Toggle between *Models* (one card per generation) and *Listings* (actual cars for sale). Cards show 4 hero numbers matched to the goal (e.g. long trips → real range, 1-stop range, DC peak, price). Sticky filter bar with an Era slider (pre-2018 → 2025+), price, range, "heat pump", "ex-lease only", "SoH certified". Plain-language badges replace codes ("Powers your house" for V2H).
3. **Generation page.** Timeline strip of the model's generations with change markers; spec diff table vs neighbours; price band chart per country (p25–p75 over 24 months); degradation curve (SoH vs km); known issues and buyer checklist; live listings below.
4. **Listing detail.** Gem Score breakdown, price vs market position on a band, SoH with source, warranty left, red flags, total cost of ownership over 4 years in the buyer's country, link out to the seller.
5. **Compare (up to 4).** Mixes generations and listings; highlights only the rows that differ; "which one fits me" summary from the goal picker answers.

**Cross-cutting**

- Alerts: save any filter as an email/push alert, with a "new gem" threshold (score ≥ 80).
- One currency and one country at a time; others on demand. Metric and Celsius by default; km and kWh/100 km or Wh/km as a user choice.
- Mobile first: filters as a bottom sheet, cards one per row, compare as swipeable columns.
- Every number has a tooltip with its source and date.
- Multilingual from the start: NL, EN, DE, FR.

## Shortlist, accounts and saved comparisons

The shortlist is the core of the product: everything a buyer does should feed it, and nothing they select should ever reset.

**The hunting workflow**

1. **Explore** generations and rankings, and heart the ones that fit.
2. **Shortlist** them into named lists, e.g. "Family car under €15k" or "Second car, city only".
3. **Compare** shortlisted generations and listings side by side, then save the comparison.
4. **Hunt**: alerts for new listings, price drops and new gems on each shortlist.
5. **Track** specific cars with a status: Watching → Contacted → Test drive → Bought or Rejected, with private notes.

**Accounts**

- Sign in by passkey or email link, no passwords. Anonymous use works too: favourites and comparisons are kept on the device and merge into the account at sign-up.
- Profile settings: country, currency, units, home charging (yes/no, AC kW), and typical trip length. These personalise hero numbers and rankings.
- Share a shortlist with a partner (view and comment). Export to CSV or PDF.

**Saved comparisons** (fixes ev-database.org's reset problem)

- Every filter, sort and comparison lives in the URL and auto-saves to the account. Back button, refresh and new tabs keep state.
- Named, saved comparisons with a shareable link; prices and listings update live, with an optional snapshot to freeze them.
- "Highlight differences" by default; pin the rows you care about.

**My EV (owner mode)**

- Owners log trips, charging sessions and SoH readings. That feeds the real-world range and degradation data, and gives owners a battery report to show buyers when they sell, as Recurrent does in the US. Buyers who become owners keep the product useful, and the data improves for everyone.

## Rankings (Top 10 lists)

Each Top 10 is a saved search the reader can open and adjust (EVKX's best idea), shown per country, with a one-line method note and a minimum data threshold. Rankings are also the main SEO entry points.

| List | Ranked by | Adjustable filters |
| --- | --- | --- |
| Best used EVs under €10k / €15k / €20k | Gem Score of live listings, grouped by generation | Budget, era, body, country |
| Most range for your money (used) | € per km of real range, at the generation's median used price | Budget, era, segment |
| Best new EVs under €25k / €35k | Real range, charge speed and efficiency, at list price | Price cap, segment |
| Fastest road-trip chargers | km added in 10 min DC (average power, not peak) | Era, price, segment |
| Best on a home wallbox | AC km per hour | Price, segment |
| Longest real range | Cold-weather motorway range | Era, price, body |
| Most efficient | Real Wh/km | Segment, era |
| Biggest boot | Litres (rear + frunk), per segment | Segment, length, price |
| Compact for city parking | Length (mm) with range ≥ a chosen minimum | Max length, min range |
| Best family EV | 5 seats, boot ≥ 450 L, ISOFIX count, range | Budget, new/used |
| Best for towing | Braked towing kg, with range while towing when known | Budget, era |
| Biggest battery per segment | Usable kWh | Segment, era |
| Holds its value best | Depreciation from new over 3 years, per country | Segment |
| Healthiest batteries | Median SoH at 100,000 km (once enough data) | Era, chemistry |

Editorial picks ("our favourite second-hand gem this month") go in a separate, labelled block, never mixed into data rankings.

## Architecture and stack

A small, boring stack is enough; the hard part is the matching step, highlighted below.

&#91;embedded content: system architecture · 4 sources, 1 database, 1 app\]

Everything flows through one matching step that ties messy listings to a generation and variant; scores are recomputed weekly from the database.

**Suggested stack** 🟡

- **Frontend:** Next.js with server rendering, so generation pages rank in search.
- **Search:** Typesense or Meilisearch for fast faceted filters.
- **Database:** Postgres; OpenEV Data's Docker image can run alongside as a spec service.
- **Workers:** Python (rapidfuzz for matching, pandas for the price index), scheduled jobs.
- **Hosting:** EU provider such as Hetzner or Scaleway; keeps data in the EU and costs low.
- **Growth channel:** programmatic pages per generation × country ("used Ioniq 5 2021–2023 price Netherlands"). These are the queries used-EV buyers type, and ev-database.org doesn't answer them.

## Roadmap

Ship a useful v0 with no scraped data, then earn the right to the expensive layers. Durations are 🟡 solo-builder estimates.

1. **v0 – Generation browser (4–6 weeks).** \~40 high-volume models across NL, DE, FR, UK. Open spec data, own real-range and charge-speed model, Eras and Generations, generation pages, Top 10 rankings, accounts with shortlists and saved comparisons, goal picker, deep links into marketplaces. Gate: 1,000 monthly visitors and clear demand for alerts.
2. **v1 – Used market layer (2–3 months).** First listing feed partnership or affiliate API, listing matching pipeline, PriceIndex, price band charts, Gem Score v1, alerts. Gate: one data partner signed; match accuracy above 90% on a hand-checked sample.
3. **v2 – Trust layer (3–6 months).** SoH from certificates and user submissions, degradation curves, TCO per country, cross-border comparison, dealer-facing "price my stock" view as the first paid product.
4. **v3 – Scale.** EV Database licence or paid valuation API if revenue allows, more countries (BE, AT, Nordics, UK), Battery Passport integration as post-2027 cars reach the used market.

**Revenue options** 🟡: affiliate fees from marketplaces and lease remarketers, paid alerts tier, dealer analytics subscription, lead fees for SoH tests and EV-specialist inspections.

## Risks and open questions

The biggest risk is data access, not code.

| Risk | Why it matters | Mitigation |
| --- | --- | --- |
| Marketplaces refuse feeds | Without listings, no Gem Score | v0 works on deep links; approach smaller sites and lease remarketers first; they want buyers |
| Scraping temptation | EU database rights and site terms; account bans; reputational damage | Treat as a no-go for production data 🟡 (get a legal check before any collection) |
| Spec licence cost | EV Database pricing is not public 🔴 | Price it early; OpenEV Data as fallback |
| Listing-to-generation mismatch | Wrong generation = wrong price band = bad Gem Scores | Confidence score, manual review queue, exclude low-confidence matches from scoring |
| Sparse SoH data | Battery confidence becomes mostly "unknown" | Neutral default; partner with test providers; crowdsource from owners |
| Price whiplash | UK used-EV prices fell for 40 months then rose from mid-2026 | Weekly index, show trend direction, avoid "buy now" claims |

**Open questions**

- [ ] What does an EV Database licence cost for a small company, and does it cover discontinued models?
- [ ] How complete is OpenEV Data for pre-2020 European models?
- [ ] Which marketplaces in NL/DE/FR offer affiliate or partner listing feeds?
- [ ] Is AVILOO (or a competitor) open to sharing anonymised SoH-by-model data?
- [ ] Brand name and domain.

## Still to spec

Ten workstreams are still open; the first three block the build.

| # | Workstream | What needs deciding | Priority |
| --- | --- | --- | --- |
| 1 | Data permissions | Written OK from Bjørn Nyland and Spritmonitor; EV Database licence quote; OpenEV coverage check | Blocks v0 |
| 2 | Back-office tool | Review queue UI, override and lock flow, source health dashboard, audit log | Blocks v0 |
| 3 | Site structure and SEO | URL scheme (/nl/used/hyundai/ioniq-5/gen-1), page templates per generation × country, structured data, hreflang for NL/EN/DE/FR | Blocks v0 |
| 4 | Owner data collection | Manual log vs OBD dongle vs connected-car APIs; consent; anti-gaming (one car, one vote) | v1 |
| 5 | Privacy and legal | GDPR for accounts and owner data, terms of use, disclaimer on price ratings and range estimates | v1 |
| 6 | Listing partnerships | Which partner per country, feed format, deduplication across sites | v1 |
| 7 | Country cost data | Electricity prices, road tax, insurance bands, incentives for the TCO calculator | v2 |
| 8 | Brand and design system | Name, domain, visual identity, components, accessibility (WCAG AA) and speed targets | Before launch |
| 9 | Metrics | North-star metric (e.g. shortlists with an alert set), activation, retention, data coverage % | Before launch |
| 10 | Go-to-market | EV owner communities, Reddit and forums, YouTubers, launch content from the Top 10 lists | Before launch |

**Suggested next step:** do 1 (emails out this week; they take time to come back) while drafting 3, since site structure shapes the database IDs.

## Sources

- [ev-database.org homepage](https://ev-database.org) (reviewed 2026-11-14)
- [EV Database Data Services (DE)](https://ev-database.org/de/data-services-api) and [(UK)](https://ev-database.org/uk/data-services-api)
- [OpenEV Data governance and licensing](https://open-ev-data.github.io/1.4.x/governance)
- [Chargeprice open-ev-data](https://www.github.com/chargeprice/open-ev-data)
- [cars-data.com data licensing](https://cars-data.com/ar/api)
- [AutoScout24 has no public API (dev.to)](https://dev.to/devil_scrapes/how-to-scrape-autoscout24de-car-listings-germany-to-jsoncsv-15f9)
- [Electra: used EV prices in France](https://www.go-electra.com/ca/newsroom/used-electric-cars-with-prices-falling-is-now-the-time-to-take-the-plunge/)
- [AutoUncle: UK used-EV stock and prices, Aug 2026](https://www.autouncle.co.uk/en-gb/insights/market-analysis/uk-used-ev-stock-shrinks-prices-climb-2026-08/)
- [Electric Car Scheme: used EV prices 2026](https://www.electriccarscheme.com/blog/used-electric-car-prices-are-falling-fast)
- [AVILOO battery-health study (AM Online)](https://www.am-online.com/news/why-two-identical-used-evs-shouldn-t-have-the-same-price-ad-feature)
- [Ayvens Carmarket SoH certificates](https://www.ayvens.com/en-fi/about-us/news/battery-state-of-health-certification-for-used-evs/)
- [EU Battery Passport timeline tracker](https://esprregistry.pages.dev/battery-delegated-act-tracker)
- [Autovista asset risk and API](https://autovista.com/?p=937)
- [JD Power/Autovista on cross-border RVs](https://www.dev.jdpower.com/insight-segment/aftermarket/page/2/)

* [Similarweb: sites like ev-database.org](https://www.similarweb.com/de/website/ev-database.org/competitors/)
* [EVKX](https://evkx.net)
* [Green Cars Compare](https://greencarscompare.com/global/)
* [AutoUncle](https://www.autouncle.com/) and [AutoUncle B2B](https://b2b.autouncle.com/improve-your-websites-conversions)
* [Electrifying.com for dealers](https://www.electrifying.com/car-dealers-signup)
* [car360 / Octopus used EVs](https://octopus-used-evs.car360.co.uk/why-car360)
* [Recurrent battery reports](https://www.recurrentauto.com/questions/how-do-i-prove-my-evs-battery-is-healthy-when-selling)
* [The EV Report: UK battery certificates and used-EV finance](https://theevreport.com/battery-health-certificates-uk-used-evs)
* [Spritmonitor (Wikipedia)](https://www.wikipedia.org/wiki/Spritmonitor) and [elektroauto-news on Spritmonitor data](https://www.elektroauto-news.net/news/7-eautos-verbrauch-sparsam-alltag-reale-daten)

- [Bjørn Nyland test results sheet](https://docs.google.com/spreadsheets/d/1V6ucyFGKWuSQzvI8lMzvvWJHrBS82echMVJH37kwgjE/edit?usp=sharing)
- [tb-data: explorer for Bjørn Nyland's test data](https://github.com/tordar/tb-data)
- [InsideEVs: ID.3 range test](https://insideevs.com/news/445471/vw-id3-range-test-range-efficiency/) and [i4 M50 cold test method](https://insideevs.com/news/565641/bmw-i4-m50-range-cold/)
- [EV Magazine: real-world highway range at 90 and 120 km/h](https://www.evmagazine.eu/real-world-highway-range-which-evs-actually-go-furthest-90-and-120-kmh)
