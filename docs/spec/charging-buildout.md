<!-- Mirror of the claude.ai spec doc, tab "Charging buildout" (rev 10), exported 2026-11-15 by WS0. For builders this repo copy wins; product changes start in the doc and WS0 mirrors them here. Transcribed from the export; if a figure looks off, check the doc tab. -->

# Charging buildout

Nov 15, 2026 · @Menno van Ginkel

Many buyers still picture the 2019 network. We show each country's real public charging buildout from official statistics, with history, and link out to existing maps and route planners for individual chargers. We never run our own charger map.

## What we build

Three pieces, all read-only and fed by official statistics. None of them shows individual chargers.

1. **Country charging page** (`/charging/{country}`, six languages). Headline cards first, charts below, link-outs at the bottom.
   - Headline cards: public charging points now; DC fast points now; share of DC points at 150 kW+; growth in the last 12 months; "then vs now" (2020 vs latest, as a multiplier, e.g. "3.3× more public points than 2020").
   - Charts: public points over time, AC vs DC stacked (they sum to the total); DC split by power band (50–149 kW, 150–349 kW, 350 kW+) where the source gives it; EVs per public point over time (lower is better); kW of public power per EV (the IEA metric, where available); reliability (share of points technically available) only where an official source publishes it, today France.
   - Plain-language notes on the page: what a "charging point" is, why countries count differently, and that most charging still happens at home.
2. **"Find a charger / plan a trip" block.** Per country: the official map if one exists, the best local app, and the pan-European ones. Shown on the country page, in the footer of every model page, and on /learn. Pure links from the country config; no API calls.
3. **Car-page hooks.**
   - "Plan a trip with this car in ABRP": a deep link that pre-selects the car model (ABRP publishes URL deep-link parameters for origin, destination, car model and state of charge). Needs an `abrp_typecode` on the variant; null means a plain ABRP link.
   - "How this car fits the network" (Next): one line per country, e.g. "about half of UK rapid-or-faster points are 150 kW+; this car averages 95 kW 10–80%". Reuses our real DC numbers; never peak kW alone.

Plus a **/learn page, "Charging in 2026: what's changed"**, for first-time buyers: tap-to-pay, no subscriptions needed, plugs, prices, motorway coverage (content in the First-time buyers section below).

Europe-wide comparison (Next): one chart from EAFO with every supported country on the same definition, linked from each country page.

The page also feeds growth: "How many EV chargers are there in {country}? ({year})" is a natural programmatic SEO page, refreshed monthly. Handed to WS5.

## Key numbers now

All five launch countries have passed 100,000 public points (Belgium only when semi-public points count), and fast charging grows faster than the total wherever the source splits it out. Figures are not comparable across rows: each country counts differently (see Data model). These are research numbers for the spec and the launch copy; the site computes its own from the pipeline.

| Country | Public points now | Fast / DC | Then | As of | Source |
| --- | --- | --- | --- | --- | --- |
| Netherlands | \~210,000 (public + semi-public + fast) | not in source | \~63,000 in 2020 (3.3×) | 2025 | [RVO via ANP](https://www.welingelichtekringen.nl/economie/laadpunten-elektrische-auto-s-verdrievoudigd-in-vijf-jaar) |
| Germany | 209,605 (155,264 normal + 54,341 fast) · 9.04 GW | 26% are fast (>22 kW, German definition) | 165,295 on 1 Jan 2025 | 1 Jul 2026 | [Bundesnetzagentur](https://www.bundesnetzagentur.de/ladeinfrastruktur.html?nn=659906) |
| Germany (latest) | 212,064 | — | +17% a year, very steady | 1 Aug 2026 | [netzwelt, citing BNetzA](https://www.netzwelt.de/news/258313-212000-ladepunkte-deutschland-autobahn-trotzdem-schnellladern-fehlt.html) |
| France | 202,804 open to the public (300 per 100,000 people) | \~13% DC above 150 kW (Jul 2026) · 89% technically available | 185,501 end 2025; 100,000 was reached about three years before 200,000 | end Sep 2026 | [Avere-France via L'Automobiliste](https://lautomobiliste.fr/24/10/2026/recharges-electriques-automobilistes/), [Electra](https://www.go-electra.com/fr/newsroom/how-many-ev-charging-points-in-france-2026/) |
| Belgium | >126,000 (public + semi-public) | — | \~50,000 in Apr 2024 | H1 2026 | [EV Belgium via Brussels Times](https://www.brusselstimes.com/news/2222534/belgium-adds-20000-ev-charging-points-in-six-months) |
| United Kingdom | 121,171 public EV chargers (174.9 per 100,000 people) | 28,887 rapid or above (50 kW+) | 119,080 on 1 Apr 2026 | 1 Jul 2026 | [DfT](https://www.gov.uk/government/statistics/electric-vehicle-charging-infrastructure-statistics-1-july-2026/public-electric-vehicle-charging-infrastructure-statistics-1-july-2026) |
| United Kingdom (fast) | — | 15,335 ultra-rapid (150 kW+), +39% a year; 1,070 hubs of 8+ rapid chargers | — | end Sep 2026 | [Zapmap via EV Infrastructure News](https://www.evinfrastructurenews.com/ev-fleet-charging/zapmap-uk-installed-8-686-new-ev-chargers-through-q1-q3-2026) |
| United States | 250,406 public ports at 80,543 locations | 75,293 DC fast ports (28 Jul 2026); Tesla \~52% of them | — | Jun 2026 | [AFDC via EVTrader](https://evtrader.com/en-gb/ev-news/us-public-ev-charging-250000-ports-2026), [AFDC via State of Charge](https://evchargingstations.com/chargingnews/us-75000-dc-fast-charging/) |
| Australia | 11,602 public connectors at 4,268 locations | \~1,560 fast or ultra-fast locations, +18% a year | +175% connectors vs Jun 2025 | Jun 2026 | [EV Council, State of EVs 2026](https://www.pv-magazine-australia.com/press-releases/state-of-evs-2026-an-ev-bought-every-100-seconds-as-car-choice-charging-and-innovation-accelerate/), [The Conversation via Unimelb](https://findanexpert.unimelb.edu.au/news/158343-australian%20electric%20car%20and%20bus%20sales%20soar%20e28093%20but%20trucks%20lag%20far%20behind) |
| EU27 | 1,176,554 public points (EAFO, 29 Oct 2026, R-26; earlier preliminary 1,155,861) | — | \~287,000 in 32 European countries, end 2020 (wider scope) | mid 2026 | [EAFO](https://alternative-fuels-observatory.ec.europa.eu/node/1536), [electrive on EAFO 2020](https://www.electrive.com/2021/03/05/eafo-study-charging-infrastructure-in-the-eu) |
| World | >7 million public points | — | +33% in 2025 alone (\~1.8 million added) | end 2025 | [IEA Global EV Outlook 2026](https://www.iea.org/reports/global-ev-outlook-2026/electric-vehicle-charging-chap-6-and-10) |

New Zealand and Canada: not researched yet (Phase 4 extras). AFDC also covers Canada; for New Zealand the IEA Data Explorer is the fallback.

**Context worth a line on the page.** UK public chargers now considerably outnumber fuel pumps ([DfT, Feb 2026](https://www.gov.uk/government/publications/comparing-fuel-pumps-to-electric-vehicle-public-chargers/comparing-fuel-pumps-to-electric-vehicle-public-chargers)). German public points run at about 12% average utilisation ([BDEW](https://www.pv-magazine.de/unternehmensmeldungen/bdew-zahlencheck-anzahl-oeffentlicher-ladepunkte-keine-sorge-bei-der-reise-in-den-sommerurlaub/)). France added fewer points in H1 2026 than in H1 2025, so its 400,000-by-2030 target looks out of reach at today's pace ([L'Automobiliste](https://lautomobiliste.fr/12/08/2026/voitures-electriques-la-france-depasse-desormais-les-200-000-bornes-de-recharge-sur-la-voie-publique/)). Honest pages show slowdowns too.

## Data sources per country

Each country series comes from one official primary source; EAFO is the EU-wide harmonised fallback and the only source for cross-country comparison; IEA is the global fallback for any market. We only take published aggregates (counts, power, per-capita), never charger locations. All licences pass the licence gate before public release (🟢 seen, 🟡 likely, 🔴 unknown).

| Country | Primary | Fallback | Format and cadence | Licence |
| --- | --- | --- | --- | --- |
| All EU + UK, NO, CH, TR | [EAFO](https://alternative-fuels-observatory.ec.europa.eu/transport-mode/road/european-union-eu27/country-comparison) (AFIR definitions, data from Eco-Movement) | IEA | Monthly, around the 15th; downloads per graph; history from 2020 | 🟡 EC reuse policy, check |
| Netherlands | [RVO dashboard](https://www.rvo.nl/onderwerpen/duurzaam-ondernemen/energie-en-milieu-innovaties/elektrisch-rijden/stand-van-zaken/cijfers) (public, semi-public, fast, home) | EAFO | Monthly; history from 2019 | 🟡 government open data, check |
| Germany | [Bundesnetzagentur Ladesäulenregister](https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/E-Mobilitaet/start.html): "Ladeinfrastruktur in Zahlen" xlsx + full list csv | EAFO | Monthly; counts by power class and state, total GW | 🟡 check the stated licence on the download |
| France | [Avere-France barometer](https://www.avere-france.org/) (with the ministry, data from Gireve) | EAFO; data.gouv.fr IRVE dataset | Monthly PDF (fragile to parse) → enter by hand or use EAFO for the series | 🔴 PDF figures: cite and link, enter by hand |
| Belgium | EAFO | EV Belgium press releases | Monthly | 🟡 |
| United Kingdom | [DfT EV charging infrastructure statistics](https://www.gov.uk/government/statistics/electric-vehicle-charging-infrastructure-statistics-1-july-2026) (data from Zapmap) | [Zapmap stats](https://www.zapmap.com/ev-stats/ev-charging-statistics) (cite, don't copy) | Quarterly ODS by power band and local authority | 🟡 OGL is the gov.uk norm, check |
| United States | [AFDC](https://afdc.energy.gov/stations/states) station counts + historical-station-counts.xlsx | EIA Monthly Energy Review table | Monthly-ish; history back to 2007 | 🟡 US government, likely public domain |
| Canada | AFDC (covers Canada) / NRCan | IEA | Monthly | 🔴 not checked |
| Australia | EV Council "State of EVs" report | IEA | Yearly (mid-year) → enter by hand | 🔴 report figures: cite and link |
| New Zealand | 🔴 not researched | IEA | — | 🔴 |
| Any later market | [IEA Global EV Data Explorer](https://www.iea.org/data-and-statistics/data-tools/global-ev-data-explorer) | — | Yearly with the Global EV Outlook; CSV download | 🟢 CC BY 4.0 |

**Deliberately not used:** Open Charge Map and other point-level databases. Open Charge Map licenses each location separately, most under CC BY-SA, which clashes with our CC BY 4.0 output ([OSM wiki](https://wiki.openstreetmap.org/wiki/Open_Charge_Map), [Zapmap licensing](https://www.zapmap.com/data-licensing)). We don't need points: aggregates answer the question and the link-outs cover the rest.

## Where we link out: maps and route planners

We link to the tools people already use instead of building a map. Each tool does one job well, and the block groups them by job so a first-time buyer knows which one to open. Links live in the country config; no API keys, no affiliate tags.

| Tool | Job | Coverage | Cost | Why we link it |
| --- | --- | --- | --- | --- |
| [A Better Routeplanner (ABRP)](https://abetterrouteplanner.com/) | Trip planning with charging stops | Global | Free, premium extras | The reference planner; [URL deep links](https://abetterrouteplanner.com/resources/api) for origin, destination, car model and state of charge, so model pages can open a plan with the right car |
| Car's own navigation | Trip planning in the car | Per car | Included | Most current EVs plan charging stops and precondition the battery on the way; we say so on the learn page rather than link |
| [PlugShare](https://www.plugshare.com/) | Find a charger + check-ins | Global, strongest in US | Free | Community check-ins show broken chargers; [rated the top ABRP alternative](https://alternativeto.net/software/a-better-routeplanner) |
| [Chargemap](https://chargemap.com/) | Find a charger, community map | Europe, \~850,000 points, \~1,800 networks ([Electra](https://www.go-electra.com/cs/newsroom/best-ev-charging-station-app-our-top-7-in-2026/)) | Free; also sells a charging pass | Most-used map in France |
| [Electromaps](https://www.electromaps.com/) | Find a charger | Europe, 360,000+ chargers | Free | Strong in Spain and Italy for later markets |
| [Chargeprice](https://www.chargeprice.app/) | Compare the price of a session by card or app | Europe | Free, premium extras | The only tool that compares session prices by payment method; answers "is contactless dearer than an app here?" |
| [Open Charge Map](https://openchargemap.org/) | Open-data map | Global | Free | Open, non-commercial option |
| [Zapmap](https://www.zapmap.com/) | UK map, live status, route planner | UK | Free, premium extras | Data source for the official UK statistics |
| [AFDC Station Locator](https://afdc.energy.gov/stations) | Official map | US, Canada | Free | Government source, no ads |
| [Bundesnetzagentur Ladesäulenkarte](https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/E-Mobilitaet/start.html) | Official map | Germany | Free | Government register |
| Google Maps (EV filter) | Find a charger | Global | Free | Already on every phone; one link only if user testing shows people expect it |

**Per country, the block shows at most five links**, in this order: official or local map, ABRP, PlugShare or Chargemap (whichever is stronger locally), Chargeprice (Europe only), Open Charge Map.

| Country | Local or official first link | Then |
| --- | --- | --- |
| Netherlands | Chargemap (no single official map found 🔴) | ABRP, Chargeprice, PlugShare |
| Germany | Bundesnetzagentur Ladesäulenkarte | ABRP, Chargemap, Chargeprice |
| France | Chargemap | ABRP, Chargeprice, Electromaps |
| Belgium | Chargemap | ABRP, Chargeprice, PlugShare |
| United Kingdom | Zapmap | ABRP, PlugShare |
| United States | AFDC Station Locator | ABRP, PlugShare |
| Canada | AFDC / NRCan locator 🟡 | ABRP, PlugShare |
| Australia | PlugShare; Chargefox app 🟡 | ABRP |
| New Zealand | PlugShare 🔴 | ABRP |

**Link rules.** New tab with `rel="noopener"`; plain URLs plus our UTM tag; text links only (no logos without permission); a monthly link check in the pipeline flags dead links to staff; the list is reviewed every six months because apps come and go.

## Aggregators and trackers

Aggregators give the cross-country view and the quality signals (reliability, price, corridor coverage) that national counts lack. We ingest the open ones and cite the commercial ones in page text with a link, never copying their tables.

| Aggregator | Covers | What it adds | How we use it |
| --- | --- | --- | --- |
| [EAFO](https://alternative-fuels-observatory.ec.europa.eu/) (European Commission) | EU27 + UK, NO, CH, IS, LI, TR | Same AFIR definitions for every country, monthly, history from 2020; data from Eco-Movement, which sources it from charge point operators | Ingest: the only fair cross-country series |
| [IEA Global EV Data Explorer](https://www.iea.org/data-and-statistics/data-tools/global-ev-data-explorer) | World | Public points by speed, EVs per point, kW per EV; >7 million public points end 2025 | Ingest (CC BY 4.0): fallback for every market and the world context line |
| Eco-Movement | Europe | Point-level data from operators | Skip: commercial; we get it second-hand through EAFO |
| [Paren](https://www.evinfrastructurenews.com/charging-installation/us-fast-charging-network-q3-2026-tesla-market-share) | US fast charging | Quarterly ports, reliability index, price per kWh, network shares: 80,964 DC ports at 14,614 stations, reliability 93.9, average $0.54/kWh (Q3 2026) | Cite with a link on the US page |
| [Zapmap statistics](https://www.zapmap.com/ev-stats/ev-charging-statistics) | UK | Monthly, by power band, network and region; the source behind DfT's numbers | Cite; DfT is the ingested series |
| [Avere-France barometer](https://www.avere-france.org/) | France | Monthly count plus technical availability and power mix | Enter by hand monthly |
| [Nationale Leitstelle Ladeinfrastruktur](https://nationale-leitstelle.de/en/bestand-ausbau/afir/) and BDEW | Germany | AFIR progress, utilisation (\~12%) | Cite |
| [T&E AFIR tracking](https://www.electrive.com/2026/07/20/only-one-eu-country-misses-afir-charging-target/) | EU | Share of the TEN-T core meeting the 150 kW / 60 km rule: 79% in June 2026 | Cite on the Europe page |
| EV Council "State of EVs" | Australia | Yearly locations and connectors | Enter by hand yearly |

Rule: one series per chart, from one source. A commercial or press figure can appear as a dated callout beside a chart, never as a point on it.

## First-time buyers: how charging works now

The headline message: **at fast chargers in Europe and the UK you can now pay with a bank card or phone, like at a fuel pump; no subscription and no stack of charging cards needed.** This becomes a /learn page ("Charging in 2026: what's changed"), linked from every country page and the footer of every model page, with a one-line version on the country page itself.

**What the rules now guarantee**

| Region | Pay without an account | Price shown | Reliability and data | Since |
| --- | --- | --- | --- | --- |
| EU (AFIR) | New public points of 50 kW+ must take bank cards (card reader or contactless); below 50 kW an ad-hoc web/QR payment is enough. From 1 Jan 2027, existing 50 kW+ points on TEN-T roads must have card payment too ([plugchoice](https://plugchoice.com/en/news/afir-explained-data-and-payment-rules-for-public-charging), [electrive](https://www.electrive.com/2024/04/13/the-european-alternative-fuels-infrastructure-regulation-afir-comes-into-force)) | At 50 kW+, ad-hoc price per kWh, shown before charging; a per-minute idle fee may come on top | Charger data via national access points | 13 Apr 2024 |
| EU corridors (AFIR) | — | — | A charging pool of 400 kW with at least one 150 kW point every 60 km on the TEN-T core, each direction, by end 2025; 600 kW and two 150 kW points by end 2027 ([Nationale Leitstelle](https://nationale-leitstelle.de/en/bestand-ausbau/afir/)). 79% of the core met it in June 2026 ([electrive/T&E](https://www.electrive.com/2026/07/20/only-one-eu-country-misses-afir-charging-target/)) | 31 Dec 2025 |
| UK (Public Charge Point Regulations 2023) | Contactless on all public points of 50 kW+ and on new points of 8 kW+ ([Greenfleet](https://greenfleet.net/node/13288)); at least one roaming option | Total price in pence per kWh, including fees; can't rise once charging starts ([gov.uk](https://www.gov.uk/guidance/regulations-public-charge-points), [Autotrader](https://www.autotrader.co.uk/content/news/new-law-to-make-electric-car-charging-easier)) | 99% average reliability across each operator's rapid network, published; open live data | Nov 2023–Nov 2024 |
| US | 🟡 Federally funded (NEVI) sites must take contactless; others vary by network | Varies | Paren reliability index 93.9 (Q3 2026) | 🔴 to research |
| Australia | 🔴 to research | 🔴 | 🔴 | — |

**Plain-language points for the learn page** (draft content for WS3; each one gets a tooltip-length version)

1. **Most charging happens at home or work.** Public charging is for trips and for people without a driveway.
2. **Paying:** at fast chargers, tap your bank card or phone. In cities, slower AC posts may still ask you to scan a QR code and pay on a web page; that works without an account too.
3. **Do you still want an app or card?** Optional. One roaming app or card (it works across many networks) can be cheaper or handy where there's no terminal. Subscriptions only pay off if you fast-charge often. Chargeprice shows which way is cheapest at a given charger.
4. **Plugs:** in Europe, UK and Australia every new EV uses Type 2 for AC and CCS2 for DC fast charging; the cable for fast chargers is fixed to the charger. In North America the industry is moving to the Tesla-style NACS (SAE J3400) plug, with adapters for older cars. 🟡
5. **Prices** are per kWh, shown before you start (EU at 50 kW+, UK everywhere). Fast charging costs more than home charging; idle fees apply if you stay plugged in after charging.
6. **Speed:** the charger's kW is a ceiling, not a promise. What matters is the car's average speed from 10 to 80%; our model pages show it in minutes and km added.
7. **Trips:** the car's own navigation usually plans charging stops; ABRP gives more control. On European motorways a 150 kW+ charger every 60 km is now the legal baseline on main corridors.
8. **Broken chargers:** check PlugShare or Chargemap check-ins before you rely on one; France reports 89% of points technically available, UK rapid networks must hit 99%.

**Tone:** reassuring and factual, no cheerleading. Every claim links to its rule or statistic. Gaps (AC posts without card readers, regional deserts like Wallonia or rural Australia) are stated plainly.

## Data model, pipeline and definition rules

Charging stats are a small, separate fact table, so new countries and new metrics are rows and config, not code.

**Tables**

| Table | Holds | Key fields |
| --- | --- | --- |
| `charging_stats` | One number per country (or region), date, metric and power band | country, region (nullable), period\_end, metric, power\_band, value, unit, source\_id, definition\_id, confidence, entered\_by (pipeline or staff) |
| `charging_metrics` (taxonomy) | What can be counted | `public_points`, `public_points_dc`, `public_devices`, `public_locations`, `installed_kw`, `points_per_100k_people`, `evs_per_point`, `kw_per_ev`, `technical_availability_pct`, `reliability_index` |
| `charging_definitions` (taxonomy) | How a source counts | e.g. `afir_recharging_point`, `uk_dft_evse_2026`, `uk_dft_device_pre2026`, `de_bnetza_ladepunkt`, `nl_rvo_public_semipublic`, `us_afdc_port`, `au_evc_connector` |
| `power_bands` (taxonomy) | Bands per source, mapped to ours | Ours: AC <22 kW, AC 22 kW, DC 50–149, DC 150–349, DC 350+ |
| `country_charging_links` (config) | The link-out block | country, tool, url, job, order, deep\_link\_template |
| variant field `abrp_typecode` | ABRP car model for deep links | nullable |

**Pipeline.** One `charging_stats` job per source in `data/sources.yaml`, monthly, inside the existing 00:30–02:30 UTC window (each run is tiny). Raw files go to object storage as usual. Annual or PDF-only sources (Avere-France, EV Council, Belgium press figures) are entered by staff through Sveltia in `data/manual/charging/*.yaml`, with the source URL required. Release diff check: flag any month-on-month change above 15% or any drop, for review before publishing.

**Definition rules (the part that goes wrong)**

1. **A point is not a device is not a location is not a connector.** A device can hold several points; a point can have several connectors; only one car charges per point at a time. We count points (EVSE) wherever the source allows, as AFIR, DfT (since 2026) and EAFO do.
2. **Never mix definitions in one line.** Belgium shows why: about 22,000 fully public 24/7 points versus 126,000 public plus semi-public points in the same period. A chart draws one `definition_id`; a change of definition starts a new series with a marked break (UK: devices until 2025, EV chargers from 2026).
3. **"Fast" means different things.** Germany: above 22 kW. UK: rapid 50–149 kW, ultra-rapid 150 kW+. US: DC fast. We map each source band into ours and show the source's own label in Nerd mode.
4. **Public vs semi-public.** Supermarket and car-park chargers count as public under AFIR; workplace and dealership chargers usually don't. The definition record says which.
5. **Comparisons across countries use EAFO (Europe) or IEA (world) only**, never national series side by side.
6. **Every number shows its as-of date and source** (Simple mode: date + source name; Nerd mode: definition, licence, download).
7. **Per-EV ratios need the fleet number from the same date**, from our existing registrations sources; if dates differ by more than a quarter, we don't compute the ratio.

## Phasing, scope guard and open questions

The cheap, high-value parts land in Core; anything that needs per-car modelling waits for Next; a charger map of our own stays Later (parked) because it breaks the finder-only rule and the licence model.

| Piece | Tier | Phase | Why there |
| --- | --- | --- | --- |
| Link-out block (country config) + ABRP plain link | Core | 1 | Config only, no data |
| /learn "Charging in 2026" page (6 languages) | Core | 1 | Text and links; answers the 2019 picture directly |
| Country charging pages for NL, DE, FR, BE, UK (cards + 3 charts) | Core | 2 | Needs the pipeline job and the taxonomy |
| ABRP deep link with car model (`abrp_typecode`) | Core | 2 | One field per variant, filled for the top 40 used models first |
| Europe-wide comparison from EAFO | Next | 3 | One more chart once EAFO ingest is stable |
| "How this car fits the network" line | Next | 3 | Needs DC curves and per-band counts together |
| US, Canada, Australia, New Zealand pages | Next | 4 | With the Phase 4 countries |
| Own charger map, live availability, prices per charger | Later | parked | Tools above already do it; point data licences clash with CC BY |

**Owners:** WS1 the job and taxonomy; WS2 the pages and the block; WS3 the learn text and link list; WS5 the SEO pages ("How many EV chargers in {country}").

**Open questions** (decided defaults in brackets; none need Menno)

- [ ] Licences for EAFO, RVO, Bundesnetzagentur, DfT and AFDC downloads: confirm before public release (default: cite and link until confirmed, publish our derived series only after).
- [ ] Netherlands, Belgium, New Zealand: is there an official public charger map worth linking? (default: Chargemap / PlugShare.)
- [ ] US and Australia payment rules for the learn page (default: leave those rows out until researched).
- [ ] ABRP deep-link parameter for the car model: confirm the typecode format and get permission to link with it (default: plain ABRP link).
- [ ] Should the learn page mention specific roaming apps by name? (default: no names, link Chargeprice for comparison, to stay neutral.)

## Sources

Official and regulatory: [Bundesnetzagentur](https://www.bundesnetzagentur.de/ladeinfrastruktur.html?nn=659906) · [DfT EV charging statistics, 1 July 2026](https://www.gov.uk/government/statistics/electric-vehicle-charging-infrastructure-statistics-1-july-2026/public-electric-vehicle-charging-infrastructure-statistics-1-july-2026) · [DfT FAQ on chargers vs devices](https://www.gov.uk/government/publications/electric-vehicle-charging-device-statistics-information/electric-vehicle-charging-infrastructure-statistics-frequently-asked-questions) · [gov.uk Public Charge Point Regulations guidance](https://www.gov.uk/guidance/regulations-public-charge-points) · [RVO stand van zaken](https://www.rvo.nl/onderwerpen/duurzaam-ondernemen/energie-en-milieu-innovaties/elektrisch-rijden/stand-van-zaken/cijfers) · [EAFO](https://alternative-fuels-observatory.ec.europa.eu/node/1536) · [IEA Global EV Outlook 2026, charging](https://www.iea.org/reports/global-ev-outlook-2026/electric-vehicle-charging-chap-6-and-10) · [Nationale Leitstelle Ladeinfrastruktur on AFIR](https://nationale-leitstelle.de/en/bestand-ausbau/afir/)

Industry and press: [Avere-France via L'Automobiliste](https://lautomobiliste.fr/24/10/2026/recharges-electriques-automobilistes/) · [Electra on French figures](https://www.go-electra.com/fr/newsroom/how-many-ev-charging-points-in-france-2026/) · [EV Belgium via Brussels Times](https://www.brusselstimes.com/news/2222534/belgium-adds-20000-ev-charging-points-in-six-months) · [Zapmap via EV Infrastructure News](https://www.evinfrastructurenews.com/ev-fleet-charging/zapmap-uk-installed-8-686-new-ev-chargers-through-q1-q3-2026) · [Paren Q3 2026 via EV Infrastructure News](https://www.evinfrastructurenews.com/charging-installation/us-fast-charging-network-q3-2026-tesla-market-share) · [AFDC counts via EVTrader](https://evtrader.com/en-gb/ev-news/us-public-ev-charging-250000-ports-2026) · [EV Council State of EVs 2026](https://www.pv-magazine-australia.com/press-releases/state-of-evs-2026-an-ev-bought-every-100-seconds-as-car-choice-charging-and-innovation-accelerate/) · [T&E AFIR coverage via electrive](https://www.electrive.com/2026/07/20/only-one-eu-country-misses-afir-charging-target/) · [AFIR payment rules (plugchoice)](https://plugchoice.com/en/news/afir-explained-data-and-payment-rules-for-public-charging) · [ABRP API and deep links](https://abetterrouteplanner.com/resources/api) · [Open Charge Map licensing (OSM wiki)](https://wiki.openstreetmap.org/wiki/Open_Charge_Map)

Most figures above were read from search extracts of these pages; WS1 re-reads each primary download when building the job.
