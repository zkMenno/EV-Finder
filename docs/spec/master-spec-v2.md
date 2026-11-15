<!-- Mirror of the claude.ai spec doc, tab "Master spec v2" (rev 39), exported 2026-11-15 by WS0. For builders this repo copy wins; product changes start in the doc and WS0 mirrors them here. -->

# Used-EV Finder — Master spec v2

Nov 14, 2026 · @Menno van Ginkel

A finder, not a marketplace: the fastest way to build a shortlist of EVs and hunt down the best used (or new) one, starting in Europe and the UK. Built solo with AI coding agents on a lean, EU-hosted open-source stack; free for buyers, paid by partners; summary data published openly. Research, market data and earlier notes live in the Research & notes tab.

## 1. Vision and first principles

**The job buyers hire us for:** "Help me pick the right EV for my life and budget, find a good one near me (or just across the border), and not buy a lemon."

Used-EV buying is a knowledge problem more than a search problem. Listing sites already have the cars. What buyers lack is the context: which generation is good, what range they'll really get in winter, what a fair price is, and whether this specific battery is healthy. That context is what we build.

**The buyer journey we cover**

| Stage | Buyer question | What we give them | Depth |
| --- | --- | --- | --- |
| 1. Learn | What kind of EV fits me? | Goal picker, range simulator, rankings | Deep |
| 2. Shortlist | Which 3–5 models or generations? | Explore table, compare, favourites, shortlists | Deep |
| 3. Price | What should I pay, new or used? | Price bands per generation and country, new-vs-used check | Deep |
| 4. Hunt | Where are the good ones? | Listings overlay, Gem Score, alerts, cross-border view | Deep |
| 5. Check | Is this specific car OK? | Battery-health context, known issues per generation | Next |
| 6. Buy | How do I close the deal? | Link out to the seller | Link only |
| 7. Own | How is my car doing? Selling later? | Owner logs that feed our range and battery data | Later |

**First principles** (every design decision gets checked against these)

1. **Models first, listings second.** The canonical vehicle database (make → model → generation → variant) is the core asset. Listings, prices and owner data hang off it. Get the model right and everything else attaches cleanly.
2. **Every number is traceable.** Each value carries its source, date and confidence. Users see it on hover; staff see full history. Trust is the product.
3. **Instant before clever.** The landing page is a fast, filterable table you can use without signing up, like EV Database. Smart features sit one click deeper, never in the way.
4. **State never gets lost.** Filters and comparisons live in the URL; accounts make them permanent. Nothing resets.
5. **Independent by design.** Money never buys a ranking position, a Gem Score or a badge. Partners pay for leads, not for opinions.
6. **Local by default, cross-border on demand.** Prices, units and rules match the buyer's country; other countries are one toggle away.
7. **Derived, not copied.** We compute our own range, price and health stats from many sources rather than republishing someone else's database.
8. **Boring tech, sharp product.** One app, one database, one data pipeline. A solo builder with AI agents must be able to understand, run and fix all of it.
9. **Open where it helps the mission.** Summary data is open (CC-BY); detailed and real-time data funds the work.

## 2. Product pillars and scope guard

In one line: **EV Database, but built for finding used EVs, across more markets, with the features it's missing.** Everything else waits.

**Four pillars**

1. **The catalogue:** every EV, grouped Model → Generation → Variant, with our own real-world range and charge speed (km per hour).
2. **Compare and shortlist:** a fast table, side-by-side compare, favourites and saved comparisons that never reset.
3. **The used market:** fair used price per generation and country, live listings linked out, and a Gem Score to spot bargains.
4. **More markets:** the same experience per country (prices, currency, language), starting NL, DE, FR, UK, BE.

**Scope guard:** every feature is tagged **Core** (the first complete version, roadmap phases 0–2), **Next** (phases 3–5, when the data or users exist) or **Later** (parked until there's demand and revenue). Adding a Core item means removing one.

| Feature | Tag | Why |
| --- | --- | --- |
| Explore table, filters, Era filter, generations | Core | It's the product |
| Real-world range + km-per-hour charging | Core | Our headline difference |
| Compare, favourites, saved comparisons (no reset) | Core | Fixes EV Database's biggest UX pain |
| Top 10 rankings | Core | Entry points and SEO |
| Used market: "See listings" links now, price bands per generation and country as feeds land | Core | The used-market focus |
| Accounts (light): favourites, shortlists, saved comparisons | Core | Persistence across devices |
| Staff tools: vehicle editor + review queue | Core | Needed to keep data right |
| Listings feed + Gem Score + alerts | Next | Needs a data partner first |
| Battery-health context and degradation curves | Next | Needs data |
| Known issues, recalls per generation | Next | Content work |
| Owner logs and reviews | Later | Hook into existing communities first |
| Tools: TCO, import calculator, range simulator | Later | Nice, not core |
| Paid B2B API and widgets | Later | Needs scale |
| Forums or own community | Later | Use Reddit, owner clubs, forums via links |

**Non-goals:** hosting listings, messaging sellers, payments, financing, new-car leasing deals, our own forum.

**Vehicle scope:** battery-electric cars only at launch. PHEVs with a real electric range of 80 km or more are the most likely Next (the new long-range PHEVs do 150–200 km on electricity), with their own electric-range column so they never pollute BEV rankings. Vans are Later.

**Catalogue size:** everything, like EV Database (around 1,500 models and variants). Every variant carries a quality tier from its facts' confidence: *checked* (staff-reviewed), *sourced* (two or more agreeing sources) or *single source* (shown with a hint). The 40 most-bought used models get hand-checked first.

## 3. Site map

Three areas: public pages anyone can use without signing up, a light account area for saving, and a staff area for keeping the data right.

&#91;embedded content: site map · public, account and staff areas\]

The Explore table is the landing page and the hub; every model, ranking and comparison links back into it.

**URL scheme** (stable IDs inside, readable slugs outside; slugs can change, IDs never do)

| Page | URL pattern | Example |
| --- | --- | --- |
| Explore | `/{country}/` with filters in the query | `/nl/?era=2021-2022&used=1&max=15000` |
| Model | `/{country}/ev/{make}/{model}` | `/nl/ev/hyundai/ioniq-5` |
| Generation | `/{country}/ev/{make}/{model}/{gen}` | `/nl/ev/hyundai/ioniq-5/gen-1` |
| Variant | `/{country}/ev/{make}/{model}/{gen}/{variant}` | `/nl/ev/hyundai/ioniq-5/gen-1/77kwh-rwd` |
| Used market | `/{country}/used/{make}/{model}/{gen}` | `/de/used/tesla/model-3/gen-1` |
| Compare | `/{country}/compare/{id},{id},{id}` | `/fr/compare/v123,v456` |
| Ranking | `/{country}/top/{list}` | `/uk/top/best-used-under-10000` |
| Data and method | `/data`, `/data/{dataset}` | `/data/real-range` |

Language follows the country by default, with a manual switch. Six languages at launch: EN, NL, DE, FR, ES and IT (ES and IT ship with the UI and rankings first, so Spain and Italy can open in Phase 4 without a translation sprint). The country sets currency, prices and default units (metric everywhere; miles available as an option for UK and US users).

## 4. Landing page = Explore (Core)

The landing page is the product: within five seconds a visitor is filtering and comparing real cars, no signup, no marketing hero, no popups. Like EV Database, but cleaner and showing new and used prices side by side.

**Above the fold (desktop)**

1. **Header:** logo, model search box, country/currency switch, sign in.
2. **One-line promise:** "Every EV, new and used. Real range, real prices."
3. **Quick bar:** budget slider (€), Era chips (up to 2017 · 2018–20 · 2021–22 · 2023–24 · 2025+), body type chips, must-haves (heat pump, towbar, 5+ seats, fast DC).
4. **Preset chips** (each is a real, shareable URL): Best used under €10k · Family under €20k · Road-trip chargers · City cars · Longest real range · Biggest boot.
5. **Results**, with a **table/cards toggle** remembered per user. Rows are grouped by generation; expand to see variants.

**Default columns** (column picker to add or remove; every column sortable)

| Column | Shows | Notes |
| --- | --- | --- |
| Model · generation | Name, years, era badge | Click opens the generation page |
| New price | Current list price in this country, or "not sold new" |  |
| Used price | Typical band (e.g. €14–18k) and number of listings | Until a listing source covers the country: a "See listings" link that opens AutoScout24, mobile.de etc. with the right filters set |
| Real range | Mild / winter motorway, km | Confidence badge |
| Charging | km added in 10 min DC · km per hour AC | Our headline stat |
| Battery | Usable kWh |  |
| Boot | Litres |  |
| Efficiency | Wh/km (real) |  |

**Battery and voltage filters (EV Database lists these per car but can't filter on them):**

- **Voltage class:** chips read from the voltage\_classes table (400 V, 800 V, 900 V+), each with a short ⓘ explainer. An advanced slider on nominal voltage for enthusiasts.
- **Fast on older 400 V chargers:** yes/no, from the "400 V charger behaviour" fact.
- **Chemistry:** chips read from the chemistries table, each with an ⓘ popover listing the pros, cons and how to look after that battery. Emerging chemistries show a "new" badge with "limited long-term data".
- **Battery cooling:** liquid, refrigerant, air or passive. Air-cooled packs (such as early Nissan Leafs) are flagged on used listings, because they age faster in heat and with frequent fast charging.
- **Charge to 100% daily:** a derived yes/no from chemistry care tips (LFP and sodium-ion yes, most NMC no).

Each chemistry and voltage class also gets a /learn page listing every car that has it, so new technology gets a page the day its first row is added.

### Simple by default, nerdy on demand

The site is written for someone who has never owned an EV, and goes as deep as an enthusiast wants. One rule: **every term gets a plain-language tooltip, and every number can be opened to show where it comes from.**

- **Plain labels first.** "Real range in winter", not "WLTP × 0.72"; "Adds 250 km in 20 min", not "avg 142 kW 10–80%". The technical name appears under the label in small text.
- **Tooltips everywhere (ⓘ).** Hover on desktop, tap on mobile. One or two sentences, no jargon, written so a 14-year-old gets it. A "More" link opens the /learn page.
- **Detail level switch: Simple / Detailed / Nerd.** It's remembered per visitor and stored in the URL, so a shared link keeps the level.
  - **Simple:** headline numbers, plain words, a few filters.
  - **Detailed:** all filters and full spec tables.
  - **Nerd:** raw values and units (kWh gross/usable, nominal V, C-rate, cell format, supplier), charge-curve charts, every source with date and confidence, sources that disagree, the fallback rung used, and the CSV/JSON download.
- **Glossary as a table, like chemistries:** glossary\_terms (id, label, short explanation of 20 words or less, long explanation, nerd note, related terms, languages). Tooltips, the /learn pages and the filter popovers all read from it, so one edit fixes it everywhere. Written in all six languages, editable in Sveltia.
- **Explain the why, not only the what.** Example tooltip: "800 V: charges faster on the newest fast chargers. On older chargers some 800 V cars are slower, so check 'Fast on older chargers'."
- **Test with normies.** Before launch, five people who don't drive EVs try three tasks (find a used EV under €15k with 250 km of winter range; compare two cars; understand LFP). Fix every term they get stuck on.

**Row actions:** a heart to favourite, a checkbox to compare. Ticked cars collect in a **sticky compare tray** at the bottom (up to 4); it survives navigation, refresh and back-button, and only empties when the user clears it.

**Below the fold:** three ranking rows (e.g. best used under €10k, fastest chargers, biggest boot), a "How we get our numbers" strip linking to the method page, and community links (subreddits, owner forums) for popular models.

**Speed and feel**

- First 25 rows server-rendered for search engines and a fast first paint (target: largest content visible under 1.5 s on 4G).
- The whole catalogue (a few thousand variants) ships to the browser as compressed data, so filtering and sorting happen instantly on the device, with no server round-trip.
- Skeleton loaders instead of "Loading…" text; no empty "– €" placeholders.
- Mobile: cards by default, filters in a bottom sheet, compare tray as a bottom bar.
- Privacy-friendly analytics, so no cookie banner.
- Keyboard-navigable table; WCAG AA contrast.

## 5. Model, generation, variant and used-market pages (Core)

The generation page is the heart of the used-car experience: it answers "is this generation a good buy, and what should I pay?" Model and variant pages exist mainly to route people there.

| Page | Answers | Contents | Tag |
| --- | --- | --- | --- |
| **Model** | Which generation do I want? | Timeline strip of generations with era colours and change markers ("heat pump from MY2021"); one card per generation with years, range span, new price, used band; community links (subreddit, owner forum, top review videos) | Core |
| **Generation** | Is it a good buy, and at what price? | Summary card; variants table; "what changed" vs previous and next generation; real range (mild, winter, motorway) with confidence badge; charging stats; used price band per country; "See listings" links; similar cars people also compare | Core |
|  |  | Battery-health context and degradation curve; known issues and recalls; buyer checklist; live listings with Gem Score | Next |
| **Variant** | What exactly is this trim? | Full spec sheet with source and date on hover; new price per country; real range; charging; dimensions; towing; V2L/V2H/V2G in plain words | Core |
| **Used market** (country × generation) | What do they sell for here, and abroad? | Price band by age and mileage; number of listings; price trend; "cheaper in another country" box | Next (needs listing data) |

**Rules for every page**

- Plain-language badges instead of codes: "Can power your house" for V2H, "Heat pump" instead of an icon nobody understands.
- Every number has a tooltip: source, date, confidence. A "Report a data issue" link on every spec sheet sends corrections to the staff review queue.
- One price at a time, in the visitor's country and currency, labelled; other countries one click away.

### Variant finder (added 15 Nov 2026)

Tell variants apart and spot the right one in a used ad: a "differences only" toggle on generation pages and Compare, a variant change timeline, a "spot it in an ad" clue box per variant, and later a "which one is it?" finder and NL plate lookup. Clues live in one data table that also feeds listing matching (§8). Full tab: [variant-finder.md](variant-finder.md) (Decision 019).

## 6. Compare (Core)

Compare is where shortlists get decided, so it must never forget what you picked. The selection lives in three places at once: the URL (shareable), the device (survives refresh) and, once signed in, the account (survives devices).

**Behaviour**

- Up to 4 items: generations or variants now; specific listings once the used market is live (Next).
- Rows grouped: Price · Range and efficiency · Charging · Space · Features · Used market.
- "Show only differences" on by default; pin rows you care about; best value per row subtly highlighted.
- Suggestions: "People comparing these also looked at…" (from anonymous compare co-occurrence).
- Mobile: swipe between cars with the row labels fixed on the left.

**Saved comparisons** (account)

- Save with a name ("Family car shortlist"); listed on the dashboard.
- **Live** by default: prices and data update; an optional **snapshot** freezes the numbers with a date.
- Share as a read-only link (no account needed to view).

**What we fix compared to EV Database:** selections reset; prices without country labels; no way to save or share a named comparison.

## 7. Rankings and tools

Rankings are Core because they're cheap to build, double as search entry points, and each one is just a saved Explore query. Tools stay parked.

**How a ranking works:** a definition (filter + sort + minimum data rule + one-line method note) stored as data, rendered per country. Staff edit definitions in the rankings editor; no code change to add one. Each ranking opens as an Explore view you can adjust.

**Launch set (10)**

| Ranking | Ranked by |
| --- | --- |
| Best used EVs under €10k / €15k / €20k | Real range per € at the generation's typical used price (Gem Score once listings are live) |
| Most range for your money | € per km of real range (used) |
| Best new EVs under €30k | Real range, charging and efficiency at list price |
| Fastest road-trip chargers | km added in 10 min DC (average power) |
| Best on a home charger | km per hour AC |
| Longest real range | Winter motorway range |
| Most efficient | Real Wh/km |
| Biggest boot | Litres, per segment |
| Best family EV | 5 seats, boot ≥ 450 L, range |
| Best for towing | Braked towing kg |

**Tools (Later):** TCO calculator, import cost calculator (duty, VAT, age rules), "will it fit my life" range simulator, new-vs-used check. Their inputs (energy prices, tax rules) live in the country config from day one, so building them later is mostly UI.

### Charging buildout (added 15 Nov 2026)

Many buyers still picture the 2019 network. Each supported country gets a charging page from official statistics (points over time, AC vs DC, DC by power band, EVs per point), a /learn page on how charging works now (tap-to-pay at fast chargers, no subscriptions needed), and a link-out block to existing maps and route planners (ABRP, PlugShare, Chargemap, Chargeprice, official maps). Model pages get an ABRP deep link with the car pre-selected. No charger map of our own. Link-outs and the learn page are Core phase 1; country pages Core phase 2. Full spec: Charging buildout.

### Bidirectional charging and plugs (added 15 Nov 2026)

Buyers increasingly ask "can this car power my house or earn money from the grid?". The answer depends on the car, its software version, battery size, build date, the type of wallbox (AC: near-normal price; DC: about €2,000–3,000), the energy contract and the country. Explore gets filters for V2H, V2G, "no expensive special box" and "ready for the 2027 charger standard", defaulting to what works today in the user's country, with caveat badges and a used-car checklist on model pages. From 1 January 2027 every new or renovated EU wallbox, home ones included, must support ISO 15118-20: that is the communication standard that allows two-way charging, not two-way hardware, and the copy says so. US: CCS1 vs native NACS per model year and a "plugs into Tesla Superchargers" filter (Next). Schema, EU plug data and a "buying a wallbox from 2027" learn section are Core phase 1; the two-way filters Core phase 2. Full spec: Bidirectional & plugs.

## 8. Used market (Core links, Next data)

At launch the used market is a set of smart links: one pre-filled search per generation on the main marketplace of each country (AutoScout24 in NL, BE and DE, mobile.de in DE, La Centrale and Leboncoin in FR, AutoTrader UK, and so on). Price ranges come from those same searches, in three layers, and the app is built for full listing feeds from day one.

**Where used prices come from (decided: layers 1 + 3, with 2 as backup)**

| Layer | How | Status |
| --- | --- | --- |
| 1. Feeds | Affiliate or partner feeds where a marketplace offers one | 🟢 Clean; use wherever available |
| 2. Manual sample | Staff note about 20 prices per popular generation per country each month from the pre-filled searches | 🟢 Legal, slow; backup where 3 is off |
| 3. Automated sampling | A small job reads the result pages of our own pre-filled searches and keeps only counts and p25/p50/p75 per band | 🔴 Breaks most marketplace terms and can touch EU database rights |

Rules for layer 3, so the risk stays small: one request per search per day at most, respect robots.txt, identify the bot honestly, store aggregates only (never copies of listings, photos or seller details), a per-site kill switch, and a short legal check per country before it is switched on. If a marketplace objects, switch that site off the same day and fall back to layer 2. 🟡 Not legal advice; get a one-off opinion from an EU internet lawyer before Phase 3 (budget around €500–1,500).

**Layer 0, added after research round 2:** the marketplaces already publish free monthly used-price indices (Autotrader UK, AutoScout24, Indicata for 13 countries, Recurrent for the US). We show these as a country trend line ("used EV prices in DE: −3% this year") and use them to sanity-check our own bands. No legal risk.

**Partnerships first:** about eight groups own most marketplaces (see the Marketplaces tab). Four conversations (Autonex/AutoScout24, Adevinta, Vend, OLX Group) cover nearly all of Europe, so outreach moves forward to Phase 1. Layer 3 stays the fallback for sites that say no or don't answer.

**Stage A — launch: smart links (Core)**

- Every generation page and Explore row has "See listings" buttons per marketplace, with make, model, year range, battery and price filters already set.
- Links carry affiliate tags where programmes exist (first revenue).
- Clicks are counted per generation and country: this shows where demand is and which feed to chase first.

**Stage B — per country as feeds land: listings and price bands (Next)**

| Piece | How it works |
| --- | --- |
| Listing sources | Partner or affiliate feeds per country; we store only what we need (price, mileage, first registration, location, seller type, ex-lease flag, link) and always link back |
| Matching | Each listing is matched to a variant by rules first (make, model, year, kW, kWh), a language model only suggests when rules fail, and anything under the confidence threshold goes to Listing QA |
| De-duplication | Same car on several sites merged by VIN or plate when available, otherwise photo + spec + location fingerprint |
| Price bands | Asking prices grouped by generation × country × age band × mileage band; shows the middle 50% (p25–p75) and count; hidden below 8 listings; labelled "asking prices" |
| Gem Score v1 | Price vs its band (60%), value: real range per € and key features (20%), battery confidence: certificate or warranty left (20%); red flags (battery rental, CHAdeMO-only, price far below band) cap it at 40 and are shown |
| Alerts | Saved search → new match, price drop, new gem (score ≥ 80); instant, daily or weekly email |
| Listing tracker | Save a listing to a shortlist with status: Watching → Contacted → Test drive → Bought / Rejected, plus private notes |
| Cross-border view | "Cheaper in DE: typical €2.1k less" on generation pages, once two neighbouring countries have bands |

**Order of countries for feeds:** follow the click data from Stage A, not guesses.

### Ways to pay: outright, loan or lease (added 15 Nov 2026)

Many buyers don't pay cash: they lease, or put some money down and borrow the rest. Every price on Explore, model pages and Compare can switch between **Buy outright** (the used price band, as now), **Loan per month** and **Lease per month**. The choice is remembered and kept in the URL. It feeds the honest monthly cost-of-ownership view (the UX positioning).

| Mode | What we show | Where the number comes from | Phase |
| --- | --- | --- | --- |
| Buy outright | Used asking-price band, new price | Section 8 layers | Core |
| Loan per month | Our own estimate from the price, your deposit, term (default 48 months) and a typical interest rate per country, labelled "estimate, not an offer" | Calculator in the browser; typical rates in an editable `finance_profiles` table per country with source and date | Core 2 |
| Lease per month | "Used lease from about €X/month" plus a link to used-lease sites | Partner feeds only; plain link otherwise | Next |

**Used leasing exists in most launch countries.** NL: private occasion lease (Ayvens, Athlon), with a credit check and BKR registration under the Keurmerk Private Lease. DE: LeasingMarkt.de lists used EV leases, though 72% of its lease enquiries are for new cars. FR: Vivacar lists about 6,000 used EVs on LOA/LLD from about €90/month; Renault Renew offers used LOA. UK: used PCP/HP finance is common.

**Rules (legal, not advice):**

- From 20 Nov 2026 the EU consumer credit directive (CCD2) requires credit adverts that show cost figures to include a representative example and the warning "Borrowing money costs money". Our calculator is not an offer and names no lender, but it still shows the assumptions and that warning. Lawyer question added to research R-03.
- UK: introducing people to car finance or lease providers is credit broking and needs FCA authorisation. No UK finance or lease links until that is checked; the calculator only.
- No commission on loans at launch. Lease links are labelled and never change rankings (no paid rankings).

Plain-language tooltips: "loan", "lease", "private lease", "balloon payment / PCP", "residual value", "total cost over the term". Every monthly figure also shows the total paid over the term.

Sources (15 Nov 2026): [Ayvens private occasion lease](https://www.ayvens.com/nl-nl/private-lease-showroom/onze-autos/237573/kia-niro-ev/) · [Athlon EV occasions](https://www.athlon.com/nl/private-lease/kennisbank/ev-populair-bij-private-lease/) · [LeasingMarkt.de used EV leasing](https://www.leasingmarkt.de/e-auto/gebraucht) · [LeasingMarkt Rückspiegel 2025](https://www.leasingmarkt.de/wplm/wp-content/uploads/2022/03/pm-leasing-rueckspiegel-2025.pdf) · [Vivacar used EV LOA/LLD](https://www.vivacar.fr/voiture-occasion/electrique?page=67) · [iAutos on used LOA](https://iautos.fr/leasing/loa-electrique) · [EUR-Lex CCD2 summary](https://eur-lex.europa.eu/EN/legal-content/summary/consumer-credit-agreements-2023.html) · [FCA primary credit brokers](https://www.fca.org.uk/firms/authorisation/consumer-credit-brokers/primary-credit-brokers/printable/print)

## 9. Accounts and user dashboard (Core, light)

Accounts exist for one reason: so nothing a buyer collects gets lost between devices. Everything works without one first; signing up just makes it permanent.

**Anonymous first**

- Favourites, compare tray, recent views and settings are stored on the device.
- At sign-up they merge into the account automatically; nothing is asked twice.
- Gentle prompt only after real effort (e.g. 3+ favourites or a built comparison): "Save this so you don't lose it."

**Sign-in:** passkey or email magic link; no passwords to manage. Social login only if sign-up conversion turns out low.

**Dashboard (/me)**

| Block | Shows | Tag |
| --- | --- | --- |
| Your shortlists | Each list with its cars, used price band, change since last visit | Core |
| Saved comparisons | Name, cars, last updated, share link | Core |
| Favourites | Hearted models, generations, variants | Core |
| Recently viewed | Last 10 pages | Core |
| New matches and price drops | From saved searches and tracked listings | Next |
| Market moves | "Used Ioniq 5 gen 1 down 4% in NL this month" for your shortlisted generations | Next |

**Shortlists:** named lists ("Family car", "City runabout") of generations or variants, with private notes. Listings can be added with a status once the used market is live (Next).

**Settings:** country, language, currency, units (metric default; miles option), home charging (yes/no, AC kW), budget, typical longest trip. These personalise default columns and rankings (e.g. no home charging → DC stats move forward).

**Sharing:** any shortlist or comparison can get a read-only link.

**Privacy (GDPR):** export all my data, delete account in one click, email preferences, no tracking beyond privacy-friendly analytics, EU-hosted.

## 10. Owner data, reviews and community hooks

Borrow communities before building one. Owners already gather on Reddit, model-specific forums, owner clubs and YouTube; we link to them and let them correct us.

| Feature | What it is | Tag |
| --- | --- | --- |
| Community links per model | Curated links: subreddit, main owner forum, owner club, 2–3 best review videos (Bjørn Nyland first where he tested it) | Core |
| Report a data issue | One-click correction form on any number → staff review queue; reporter credited if they want | Core |
| Owner range and charging log | Owners submit trips (km, kWh, temperature, road type) and DC sessions; feeds the real-range model | Later |
| Battery health submission | Owner enters a certificate or app reading (SoH %, km, date); feeds degradation curves | Later |
| Model reviews | Structured short review (likes, dislikes, issues, would buy again) from verified owners | Later |
| Own forum | Not planned | Never, unless communities ask for it |

When owner data arrives, it needs anti-gaming rules from the start: one car = one voice, outlier checks, and a minimum number of owners before a figure is shown.

## 11. Staff dashboard (/staff)

The staff area exists to keep the data right with as little human time as possible: machines merge, humans only decide what machines can't. It's built inside the main app, because edits must go through the same provenance rules as automated data. A generic database admin tool (e.g. Directus) would let edits bypass those rules.

**Roles:** Admin (everything) and Editor (data and content). Every change is logged with who, when, old and new value.

| Module | What it does | Tag |
| --- | --- | --- |
| Data health | Each source: last run, rows in and out, failures, freshness; alerts when a source goes stale or breaks | Core |
| Review queue | One inbox for source conflicts, new-car candidates, outliers and user data reports; accept, override, or reject with one click | Core |
| Vehicle editor | Make → Model → Generation → Variant tree; per field: current value, every source's value, lock, history; publish creates a new data release | Core |
| Rankings and content | Ranking definitions, preset chips, community links, glossary of plain-language badges | Core |
| Users | Look up an account, handle export and delete requests, block abuse | Core |
| Listing QA | Low-confidence listing matches with suggested variant; confirm or fix; matching rules learn from fixes | Next |
| Partners | Affiliate links per marketplace and country, click and lead counts | Next |
| Country config | Currency, language, units, VAT, marketplaces, enabled features per country | Core (as a config file at first, screen later) |

**Weekly staff routine (target under 2 hours):** clear the review queue, check data health, approve new-car candidates, skim user reports.

## 12. Data platform

One canonical vehicle database, fed by many sources, published as versioned releases. Countries are a layer on top, never baked into the core model, so adding a market is configuration plus data, not new code.

**Core data model**

| Entity | Holds | Key point |
| --- | --- | --- |
| Make, Model | Names, aliases per language | Stable IDs; slugs can change |
| Generation | Code, start/end, era, platform, change markers | Defined by hardware changes (platform, battery ±10%, charging architecture) |
| Variant | One battery + motor + trim, global technical specs | Market-independent: physics doesn't change at the border |
| Market variant | Country-specific name, price, availability, test-cycle rating (WLTP, EPA), drive side | This is what makes US, UK, AU and later markets plug in cleanly |
| Fact | One value for one field from one source, with date and confidence | Every number on the site traces back to facts |
| Variant clue, look-alike group | How to tell a variant from its look-alikes in an ad or on papers; also feeds listing matching | See variant-finder.md (Decision 019) |
| Published variant | One wide, fast row per variant per release | What the website reads; rebuilt on every release |
| Listing, price band (Next) | See section 8 | Partitioned by country |
| User data | Accounts, favourites, shortlists, comparisons | Separate schema; never mixed with catalogue data |

### Platforms, battery packs, voltage and chemistry (future-proof)

Two extra entities, because many cars share them and facts about them should be entered once:

- **Platform** (MEB, E-GMP, PPE, SEA, Ultium, CMP…): maker group, default voltage class, years.
- **BatteryPack**: supplier, chemistry, cathode detail (for example NMC 811), cell format (cylindrical, prismatic, pouch, blade), cell-to-pack yes/no, gross and usable kWh, nominal and maximum voltage, cooling (liquid, refrigerant, air, passive), warranty. A Variant points to one Platform and one BatteryPack. Pack facts (charge curve shape, degradation, chemistry) are inherited by every variant that uses the pack, unless the variant has its own measured fact.

**Taxonomy tables instead of hard-coded lists.** New technology is a new row, not new code:

| Table | Columns | Starting rows |
| --- | --- | --- |
| voltage\_classes | id, label, min V, max V, status (current, emerging), explainer | 400 V class (about 300–550 V nominal), 800 V class (about 550–850 V), 900 V+ class (about 850–1,100 V). Bands are editable. |
| chemistries | id, family, label, status (mainstream, emerging, future), pros, cons, care tips (daily charge limit, cold behaviour), first year in cars, explainer | NMC, NCA, LFP, LMFP, LMO/NMC blend (early Leaf), sodium-ion, semi-solid-state, all-solid-state, LMR (future) |
| cooling\_types | id, label, explainer | liquid, refrigerant, air, passive |

**What we store per car:** the measured or stated nominal and maximum voltage, the maker's marketing label ("900V"), and the voltage class derived from the bands. Some cars are switchable (they split the pack for 400 V chargers), so that's a flag. "400 V charger behaviour" is its own fact: native, booster (with its kW), or limited (with its kW). For used buyers this matters more than the class: some early 800 V cars charge slowly on older 400 V chargers.

**Undisclosed is a real value.** Many makers don't publish chemistry or voltage. Then we show "not disclosed", or an inferred value from the cell supplier or platform marked low confidence, never a guess dressed as fact.

**Pipeline stages:** fetch → store raw (untouched, kept) → normalise units and names → match to canonical IDs → merge facts per field (priority, majority, recency, human locks) → validate (ranges, units, cross-checks like usable ≤ gross kWh) → review queue for anything doubtful → publish a numbered release. Releases swap in atomically and can be rolled back in one step.

**Derived metrics we compute ourselves:** real-world range (owner data → Bjørn Nyland tests → sibling variant → brand × body ratio → body ratio; see Research tab), charging km per hour (AC) and km per 10 min (DC, average power), € per km of range, used price bands, Gem Score.

**Real-range test sources.** Bjørn Nyland is the largest single source, but not the only one. Each test is stored with its conditions (speed, temperature, route type), so the range model can say "summer 90 km/h", "motorway 120 km/h" or "winter" instead of one blended number.

| Source | What it is | Conditions | Use |
| --- | --- | --- | --- |
| Bjørn Nyland | 1,000 km challenge and 90/120 km/h range tests, public sheet | Mostly Norway, mixed seasons | Core input; ask permission, credit, offer support |
| NAF + Motor El Prix | About 24 cars per edition, winter and summer every year | Norway, mixed roads, real cold | Winter and summer ratios |
| ADAC Ecotest + winter motorway test | Dyno tests; winter test replays the A9 Munich–Berlin route | 0 °C motorway, lab-controlled | German motorway figure |
| Edmunds | Same real-world loop for every EV, compared to EPA | US mixed driving | US markets |
| InsideEVs / Out of Spec | 70 mph (113 km/h) constant-speed tests | US highway | Motorway figure for US-only models |
| Consumer Reports | 70 mph tests on every EV they test | US highway | Cross-check |
| Spritmonitor | Owner fuel and charging logs, German site | Real owners, all seasons | Owner averages where users are enough |

Test results are facts, but the tables and videos are someone's work: take only the numbers we need, always credit and link, and ask each source before importing in bulk.

**Real DC charging.** A charge curve is stored as a Fact holding a list of (state of charge %, kW) points, plus its conditions: battery temperature or preconditioning, outside temperature, charger power, software version, source, and status (measured, estimated or default). From the curve we show:

- **Average kW from 10 to 80%** and **time from 10 to 80%**: the headline numbers, never peak kW alone.
- **km added in 10 and 20 minutes**, using motorway consumption, the same idea as the P3 Charging Index.
- **Peak held for:** for example "175 kW peak, above 150 kW for only 4 minutes". This is the honest answer to brochure peaks.
- **Claim vs measured:** the maker's 10–80% time next to the measured one (NAF El Prix, ADAC), with the gap in minutes.
- **Winter penalty:** the winter 10–80% time where a cold test exists.

Fallback ladder for curves: measured for this exact variant → same platform and battery pack (for example all MEB 77 kWh cars) → the maker's 10–80% time turned into an average kW → a generic curve shape, always labelled "estimated". The DC ranking uses km added in 20 minutes, not peak kW.

**Every data point has 1–2 primary sources plus fallbacks**, listed field by field in Source matrix. The code mirrors it in `data/sources.yaml` (one entry per source, with its licence) and `data/field_sources.yaml` (primaries, fallbacks, tolerance and merge rule per field). Each release produces a coverage report showing how many variants have two or more agreeing sources per field.

**New cars appear automatically:** unmatched names in listings, registries or source updates create a candidate; it's auto-filled from every source and published as "new, data incomplete" if confident enough, otherwise it waits in the review queue.

**Adding a country (target: a few days of work, no code changes)**

1. Country config: currency, languages, units (km or miles), drive side, VAT, test cycle shown (WLTP or EPA), enabled features.
2. Market variants: which variants are sold there, local names and prices.
3. Marketplaces: deep-link templates for "See listings" (later: a listing feed adapter).
4. Translations for any new language.
5. Rankings: price thresholds in local currency.

The US is the main stress test: different names, trims, EPA ratings, miles and °F. Designing market variants and per-country units now makes it a data job later. Australia and the UK add right-hand drive and imported models; emerging markets later add import-fed specifics (Japanese-market variants, import rules).

**Use of AI in the pipeline:** language models may extract specs from manufacturer PDFs, suggest listing matches and translate names. They only propose; rule checks validate, and anything uncertain goes to a human.

### Open data first (no paid or licensed data)

Every data need is met from free official sources, openly licensed datasets, our own users, or free partner feeds. Nothing is bought. Full catalogue: Data sources.

| Need | Free route | Gap |
| --- | --- | --- |
| Specs | OpenEV Data; EEA CO₂ dataset (WLTP Wh/km, range per model); RDW per-plate WLTP range; fueleconomy.gov for US EPA figures | Charging curves: Bjørn Nyland + owners |
| Real-world range | Fallback ladder (Bjørn Nyland, owner logs, WLTP ratios) | Permission from Bjørn |
| Sales per model per country | KBA (DE), DfT VEH0160 (UK), RDW (NL), FEBIAC (BE), SDES (FR), OFV (NO), CEC + WA (US), VFACTS via The Driven (AU) | FR per-model detail 🔴 |
| Fleet on the road per model and model year | RDW, DfT VEH0120, WA EV population, EAFO | Varies by country |
| Used transfers | RDW owner-change dates, KBA Besitzumschreibungen, SDES used registrations, FEBIAC used BEVs, OFV | Mostly by fuel, not model, outside NL/NO/BE |
| Recalls and inspections | RDW recalls and APK, NHTSA recalls, DVSA MOT data | EU-wide recall feed 🔴 |
| Used prices | Free affiliate/partner listing feeds; monthly public reports (AutoUncle, AA Cars, Cox, Carma) as cited context | **No free official source.** Per-generation bands need a feed; until then "See listings" links |

**What this unlocks (new features, cheap to build)**

- **Availability:** "About 4,800 Ioniq 5 gen 1 on Dutch roads" on every generation page, per country. Rare cars get a warning: few to choose from, parts and know-how may be scarce.
- **Lease-wave radar:** first-registration dates plus the share registered by companies (KBA publishes it) show when a model's ex-lease cars will flood the used market: "About 1,900 company-registered Model 3s from 2022 reach 4 years old in NL in the next 12 months." A strong buy-timing signal nobody else offers.
- **Popularity and trend:** monthly sales sparkline per model and country; new Top 10 "Most available used EVs".
- **Reliability hints:** recall count per generation; MOT/APK failure patterns where open (UK, NL).

🟡 Licences differ per source; the pipeline stores each source's licence and required attribution, and the method page credits every source.

## 13. Architecture and stack

A lean monolith with a separate data pipeline: one web app, one Postgres database, one Python pipeline, all on one EU server. It is small enough for one person with AI agents to understand completely, and each part can be scaled or split later without a rewrite.

&#91;embedded content: architecture · lean monolith + data pipeline\]

The pipeline writes catalogue releases into Postgres; the web app only reads them, and writes user data. Heavy work never runs inside the web app.

### Hosting: Menno's shared AppInfra server (Nov 2026)

This replaces the Coolify, Brevo and Dagster lines in the stack table below. The app moves in next to GardenLayer and Dungeon Tracker on the existing Hetzner CAX31 (Arm, 8 cores, 16 GB RAM, 160 GB disk), which AppInfra manages.

**What we reuse:**

- Caddy for HTTPS and routing.
- GitHub → CI Arm image → SSH deploy, with one-command rollback.
- Nightly backups (14 days) plus Hetzner server backups.
- The 5-minute watchdog, which checks each app's `/health` endpoint.
- Umami, Scaleway email and the Sveltia editor (for ranking texts and generation notes, so the staff area can stay smaller).
- Staging next to live, and the existing CLAUDE.md, BUILDER-START and Hub/Builder/Merge agent setup.

**What we keep separate:** our own database and login inside the shared Postgres 17 + PostGIS server (AppInfra's pattern: one server, a database, login and private network per app), plus our own email key, deploy key, OAuth clients and object-storage key. Connection pool: about 10 for live, 3 for staging and 3 for jobs, out of the server's 100.

**Starting memory and CPU limits** 🟡 (to check against real `docker stats`):

| Container | Memory | CPU | Runs |
| --- | --- | --- | --- |
| ev-web (live) | 768 MB | 1 | Always |
| ev-web-staging | 256 MB | 0.5 | Always |
| ev-jobs (pipeline) | 1 GB | 1, low priority | Nightly window only, 00:30–02:30 UTC (to confirm) |

AppInfra's check: existing limits are about 12.8 GB (13.8 GB if the paused Cahier app runs). With EV Finder that becomes about 13.8 GB during the day and 14.8 GB during the job window. That fits as long as Cahier stays off. Move up when `docker stats` shows more than 70% RAM or CPU on busy evenings for weeks, when GardenLayer needs a second worker, or when two apps launch publicly around the same time. The cheaper alternative is moving GardenLayer to its own server, which frees about 5 GB of limits.

**Pipeline:** scheduled Python jobs with pg-boss instead of Dagster. Raw source snapshots go to Scaleway Object Storage, not local disk. Big one-off imports run on a temporary Hetzner machine.

**CI minutes:** the repo (EV-Finder) is public, so its GitHub Actions minutes don't count against the 2,000 a month shared by the private apps. Even so, pull requests run lint and tests only, and the Arm image is built only on merge to main, to keep builds fast with many agents opening pull requests.

**Email:** magic links are cheap. Saved-search alerts in Phase 3 could use a large share of the shared 50,000-a-month allowance, so they default to a weekly digest.

**Stack** 🟡 (all open source, EU-hosted)

| Part | Choice | Why |
| --- | --- | --- |
| Web app | Next.js + TypeScript | Server-rendered pages for search engines, React for the table; AI agents know it best |
| Database | Postgres (+ pg\_trgm for fuzzy search, PostGIS later for distance) | One database for catalogue, users and jobs |
| Pipeline | Python + Dagster, DuckDB + Parquet files | Dagster tracks every dataset's lineage: that *is* our provenance |
| Raw storage | S3-compatible object storage (Hetzner) | Cheap, keeps every raw fetch |
| Jobs | pg-boss (queue inside Postgres) | No Redis needed |
| Search | Client-side for the catalogue; Meilisearch only once listings exceed \~100k | Don't run a search server before it's needed |
| Auth | Better Auth (passkeys, magic links) | Open source, runs in our app and database |
| Email | EU provider (Brevo or Scaleway) | GDPR-simple |
| Hosting | Hetzner server via Coolify; Bunny CDN | Cheap, EU, simple deploys |
| Monitoring | Umami (analytics), GlitchTip (errors), Uptime Kuma | Self-hosted, no cookie banner |

**Running cost at launch** 🟡 roughly €40–100 per month.

**Built for AI-agent development**

- One monorepo: `apps/web`, `pipeline/`, `packages/schema`.
- One schema definition (JSON Schema) generates both TypeScript and Python types, so the app and pipeline can't drift apart.
- AGENTS.md with rules, small modules, strict types, tests on every data rule, seed data for local runs, preview deploys per branch.

**When to scale (and only then)**

| Trigger | Step |
| --- | --- |
| Listings above \~100k or slow listing search | Add Meilisearch |
| Database CPU above \~60% sustained | Read replica for the web app |
| Pipeline runs collide with traffic | Move the pipeline to its own server |
| Many countries with heavy traffic | Second region or more CDN caching |

## 14. Open data and B2B API

Publish what we derive ourselves as open summaries; keep detailed and real-time data for paying partners. Never republish anyone else's raw data.

| Layer | What | Licence / access | Tag |
| --- | --- | --- | --- |
| Open summaries | Real-world range per variant, charging km/h, monthly used price bands per generation × country, degradation curves | CC-BY, CSV/JSON downloads + simple read API with attribution | Next |
| Method pages | How each number is computed, error rates, sources | Public | Core |
| Paid API | Listing-level data, daily price index, Gem Score, real-range for any variant via API | API keys, rate limits, monthly plans | Later |
| Widgets | "Real range" and "Fair price" badges for dealer and marketplace sites | Paid | Later |

Open summaries earn links and trust (journalists, researchers, EV communities) and make the brand the reference; that is cheaper marketing than ads.

**Licence (decided): CC BY 4.0** for everything we publish openly: real-range figures, price-band summaries, degradation curves and market counts. Anyone can reuse them with credit, which maximises links and citations. Data that comes in under ODbL (OpenStreetMap, for example) stays under its own licence and is never mixed into the CC BY sets.

## 15. Business model, metrics and risks

Free for buyers, paid by the seller side, with costs kept low enough that affiliate income covers hosting within months of launch.

**Revenue, in order of arrival**

| Stream | Starts | Note |
| --- | --- | --- |
| Affiliate and lead fees on "See listings" clicks | Launch | Marketplaces and lease remarketers |
| Battery-test referrals (AVILOO, Generational, ClearWatt) | Next | Natural step after "I like this car" |
| Supporter membership | Next | Mission-driven users fund open data; perks: early features, more alerts |
| Paid API and widgets | Later | See section 14 |

No display ads, no paid placement in rankings or scores.

**Success metrics**

| Metric | Definition | Early target 🟡 |
| --- | --- | --- |
| North star: active hunters | Weekly users who compare, favourite or save something | Growing 10% month on month |
| Compare rate | Sessions that open compare or tick 2+ cars | ≥ 25% |
| Outbound clicks | "See listings" clicks per 100 sessions | ≥ 15 |
| Data coverage | Variants with every core field from 2+ sources or reviewed | ≥ 95% for launch countries |
| Range model accuracy | Median error vs held-out tests | < 10% |
| Freshness | Sources updated within their schedule | ≥ 98% |

**Top risks**

| Risk | Mitigation |
| --- | --- |
| No listing-data partner for a long time | Smart links work without one; chase feeds in the countries the click data favours |
| Data permissions (Bjørn Nyland, Spritmonitor, EV Database) refused | Range fallback ladder works with owner data and WLTP ratios; ask early |
| Solo bandwidth | Strict scope guard (section 2); staff routine under 2 hours a week |
| SEO competition from EV Database and big marketplaces | Win long-tail used queries per generation × country, which they don't serve |
| Policy shocks per country (tax, incentives) | Country config holds rules; monitor monthly |

## 16. Roadmap

Public launch in roughly 14 weeks of solo work with AI agents; each phase must pass its gate before the next starts, so effort goes where the evidence says. Durations are 🟡 estimates.

&#91;embedded content: roadmap · 6 phases with gates, plus Later\]

Phases 2 and 3 can overlap if a listing feed arrives early; Phase 4 starts with the US and Australia because the market-variant model makes them mostly data work.

**Phase 0 checklist (start here)**

- [ ] Pick a working name and register the domain
- [ ] Email Bjørn Nyland (permission, credit and a sponsorship once revenue exists), NAF/Motor, Spritmonitor and EV Database
- [ ] Check open-data coverage for the full catalogue (around 1,500 variants), including pre-2020 generations
- [ ] List marketplace affiliate programmes and pre-filled search URLs per launch country (NL, DE, FR, BE, UK)
- [ ] Set up the monorepo, AGENTS.md, Hetzner server with Coolify, Postgres, backups
- [ ] Write the JSON Schema for Make → Model → Generation → Variant → Market variant → Fact
- [ ] Pipeline v0: OpenEV import, Bjørn Nyland sheet import, merge, validate, publish release
- [ ] Real-range fallback model and back-test report
- [ ] Define generations for every model (with change markers); hand-check the top 40 used models first
- [ ] Staff area v0: vehicle editor and review queue
- [ ] Book a one-off legal check on automated price sampling (layer 3) before it goes live
- [ ] Draft partner pitch for Autonex, Adevinta, Vend and OLX Group (send in Phase 1)
- [ ] data/sources.yaml + data/field\_sources.yaml from the Source matrix tab, plus a coverage report per release
- [ ] Charge-curve facts and derived charging metrics (10–80% average, km in 10/20 min, peak held for)
- [ ] Country config for the 5 launch countries; UI strings in EN, NL, DE, FR, ES and IT
