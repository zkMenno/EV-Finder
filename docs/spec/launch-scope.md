<!-- Spec tab "Launch scope" (rev 2), 2026-11-17, Menno + WS0 (staging feedback, docs/spec/feedback-2026-11-17-staging.md). Rev 1: 2026-11-15, Decision 051. This tab wins over every other tab when they disagree about what ships at launch. -->

# Launch scope (strict)

**The brief:** EV Database, but with better UX, a few more features, and more countries. Anything not on the launch list below waits until after launch, however good the idea. New ideas go to ROADMAP.md, not into a task.

## What ships at launch

### 1. The hero: three steps to a shortlist
**Rev 2 (staging feedback):** the questions and answer chips get a cleaner design: fewer questions on screen at once, clear answer chips, results easy to scan (UX designs first, T-132). The steps below stay the same.

1. **Country** (NL, DE, FR, BE, UK, ES, IT; Decision 066; sets currency, prices and marketplace links).
2. **Profile**, from a 4-tap picker (car role, long trips, where you charge, where you live; Decision 050, `data/editorial/shortlist_rules.yaml`, research/R-33). It lands on one of four profiles:
   - **Road-tripper**: main car that also does the holidays (fast charging, winter range, space)
   - **Daily driver**: main car, holidays by train, rental or a second car (winter range for the longest normal day, efficiency, heat pump)
   - **Runabout**: second car for short trips (price, size, efficiency, battery health of cheap older EVs)
   - **Kerbside charger**: no charger at home; stacks on top of the other three (efficiency, 50–150 kW DC, 11 kW AC, LFP)
   "Where you live" (city / town / countryside) shifts the range floors. Optional add-on: "keep it 8+ years". Each profile preselects filter chips the visitor can edit.
3. **Budget**: a price (used and new). Under each price, a rough **"≈ €X/month"** loan estimate with fixed defaults per country, labelled as an estimate with the CCD2 warning. No lease figures at launch.
4. **Optional refine** (collapsed, all skippable), the same filters as Explore: body type and seats, minimum winter range, towing, new or used and build years, brands to include or exclude, and the other EV Database-style filters.

**Result:** a **top 10** of models with the specific variant and build years that fit the budget in that country, with the **top 5 highlighted as "your shortlist"**. Each card shows why it ranks there in one line ("does long trips in winter with 20 % spare, fast charging, €2k under budget"), its real winter range, its used price band for those build years, and a "See listings" link. One tap adds a car to Compare; the whole result is a shareable URL.

### 2. Browse the whole catalogue (like EV Database, done better)
- **Landing page:** no full car list. A **"Popular used EVs"** section (generation level, roughly Menno's own list of EV generations; T-131) and a **"Show all cars"** button to the catalogue page.
- **Catalogue page** (T-130): filters, default sort **popularity** (registration counts from `data/seed/top40.yaml`: RDW, DfT, KBA, EEA; blended with Menno's picks, Decision 038), user sorts by price, range, battery, charging speed and year.
- **Car photos** on cards and pages: maker press photos, Wikimedia Commons fallback, a credit under every photo (Decision 081; T-133–T-135).
- **Catalogue size:** aim for every EV variant sold in Europe since about 2011, at trim × year level, from open, licensed sources only (EEA CO2 monitoring, RDW type approval, KBA, OpenEV; never EV Database or marketplaces). Step 1 is a report with the expected count and licences (T-136); building waits for that report.
- **Explore** table and cards with filters, sort, Simple / Detailed / Nerd, filters in the URL.
- **Model, generation and variant pages** with our real-world range (summer and winter), real DC charging, used price band per country, sources on every number.
- **Compare** (up to 4) with a "differences only" toggle.
- **Glossary tooltips** on every term.

### 3. Countries, languages, data
- Seven countries (NL, DE, FR, BE, UK, ES, IT; Decision 066). **English only at launch** (Decision 082): every country serves `/{country}/en/`; other languages return after launch with no URL changes.
- Used price bands per country by build year (free price indices + manual samples) and pre-filled marketplace searches.
- Data pipeline: refresh, releases, quality checks, sources and licences (as built).
- **Open data download** (CC BY 4.0) at launch.
- **A few /learn pages**: winter range, charging in 2026, batteries and used battery health.

## After launch (parked, in rough order)
Translations: NL, DE, FR, ES, IT (strings exist as drafts; Decision 082) · Trip fit with routes and the Valhalla box · lease per month and full price modes · charging country pages and charts · charging link-out block on every page · bidirectional (V2H/V2G) filters and badges · variant "spot it in an ad" box, "which one is it?" finder, NL plate lookup · ABRP deep links with the car selected · accounts, favourites, alerts · rankings pages · known-issues block · more /learn pages.

## Later
Listing-link paste · US, Australia, NZ, Canada · emerging markets · paid API · owner data and reviews · our own charger map (never, as decided).

## What this means for the build
- Builders only take tasks tagged **Launch** on BOARD.md. A task for anything else needs Menno's yes first.
- Work already built for parked features stays in the code but switched off by default (feature flags), so nothing is thrown away.
- The ranking uses the shortlist rules (Decision 038: gates, weighted factors, bands; back-tested on Menno's own picks, 80 % band agreement for the road-tripper) on our published fields, filtered by budget and country. Hard filters first, then score; factors without data score neutral, never a guess. Every rank is explainable, and the UI says the road-tripper rules come from one owner's picks. Tasks T-066–T-069.
