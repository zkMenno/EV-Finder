# SEO plan: [site name]

Status: proposed 2026-11-15 · Owner: WS5 growth · Builds: WS2 web, WS3 content, WS1 data · Legend: 🟢 verified · 🟡 reasoned · 🔴 unsure

**The answer.** Win the queries ev-database.org does not serve: used cars by generation and country. Publish one page per generation × country with sourced prices, winter range and real DC numbers. Index a page only when its data passes a gate, so we never ship thin pages. Put the same numbers into open CC BY datasets with method pages, so search engines and AI assistants have something citable. Start with five countries and the default language of each. Add other language versions only after a person has reviewed the templates. Search volumes are unmeasured 🔴: validate each page type in Search Console before scaling.

## 1. Where we win against EV Database

The spec's audit says ev-database.org is a new-car catalogue with no used market, no generation view and no depreciation or battery signal (research-and-notes.md, reviewed 2026-11-14).

| Angle | Page that carries it | Why it is hard for them to copy |
|---|---|---|
| Used-first | `/used/…` pages with price bands per country | Needs listing sampling and a price pipeline |
| Generations | Generation page with change markers ("heat pump from MY2021") | Needs a hand-checked generation model (top 40 first) |
| Real DC numbers | km added in 10 min, charge-curve facts | Our own derived metrics |
| Winter range | Winter motorway range with test conditions | Needs several test sources per car |
| Country prices | Same generation, five price bands | Needs per-country config and feeds |

We do not copy their data: their terms ban crawling, and every number of ours is derived and sourced.

## 2. Page types

| Type | Pattern | Data gate (indexable only if) | Phase |
|---|---|---|---|
| Model | `/{country}/ev/{make}/{model}` | At least 1 generation page indexable | 1 |
| Generation | `…/{model}/{gen}` | Core fields from 2+ sources or staff-checked; used band meets sample minimum | 1 |
| Variant | `…/{gen}/{variant}` | Distinct sourced values (range, charge curve); else `noindex,follow` | 2 |
| Used market | `/{country}/used/{make}/{model}/{gen}` | Price band with enough samples | 1–2 |
| Ranking | `/{country}/top/{list}` (10 launch lists) | Minimum data rule of that ranking | 1 |
| Learn | `/{country}/learn/{topic}` | Written and sourced by a person | 1 |
| Charging country page | "How many EV chargers in {country} ({year})" | Official statistic ingested | 2 |
| Winter range | Section on generation pages plus one hub ranking; standalone per model only if demand shows | 2+ test sources | 2 |
| V2G / V2H | Hub "Which EVs support V2G in {country}" plus a "Power out" block per model; standalone only for confirmed cars | Confirmed capability, with software and date caveats | 2 |
| Open data | `/data`, `/data/{dataset}` | Release published | 1–2 |

Rules that keep the set honest:

- **No standalone winter-range or V2G page per model at first.** It would compete with the model page for the same query. Promote a section to its own page only when Search Console shows its own impressions.
- **Used price band needs a sample minimum.** The spec does not set one. Proposal: at least 20 sampled listings in 30 days 🟡, stored in country config.
- **Text is computed from data.** No language-model filler. Uniqueness comes from numbers, change markers, cross-country comparison and similar-car links (AGENTS.md rule 5).

## 3. URLs, languages and hreflang

The spec defines `/{country}/…` only. Language handling is a new decision, to log in DECISIONS.md before building.

Proposal 🟡: the country's default language sits at `/{country}/…`. Other languages sit at `/{country}/{lang}/…`. The codes `en nl de fr es it` do not clash with route words (`ev`, `used`, `top`, `compare`, `learn`, `data`). Do not switch language through a query parameter, because Google needs a separate URL per version.

| Country | Default | Alternates | hreflang codes |
|---|---|---|---|
| NL | nl | en | `nl-NL`, `en-NL` |
| DE | de | en | `de-DE`, `en-DE` |
| FR | fr | en | `fr-FR`, `en-FR` |
| BE | nl | fr, en | `nl-BE`, `fr-BE`, `en-BE` |
| UK | en | none | `en-GB` |

- ES and IT: ship UI strings per spec, but publish no indexable ES/IT URLs until Spain and Italy open (Phase 4), apart from optional /learn pages tagged `es` / `it`.
- Google's rules ([localized versions](https://developers.google.com/search/docs/specialty/international/localized-versions?authuser=4)) 🟢: each version lists itself and all others; links must be reciprocal or are ignored; use full URLs; `x-default` points to a fallback such as a country picker; `UK` is reserved, so use `en-GB`.
- **Put hreflang in the sitemaps, not the HTML.** Google treats HTML tags, headers and sitemaps as equivalent, and five countries × up to three languages makes long tag blocks. Generate it from the same country config as the routes.
- Self-referencing canonical on each version. Translated versions are not duplicates, but an untranslated English fallback on a Dutch page is. Serve it `noindex` until translated.

## 4. Structured data

Render JSON-LD server-side from the same Fact records that fill the page. Markup must match visible text. Validate in the Rich Results Test and schema.org validator before each template ships.

| Page | Types |
|---|---|
| All pages | `BreadcrumbList` (Explore → make → model → gen → variant) |
| Home | `Organization`, `WebSite` |
| Model, generation, variant | `Product` with additional type `Car`. Specs as `additionalProperty` with units (km, kWh, kW). `AggregateOffer` (`lowPrice`, `highPrice`, `priceCurrency`, `offerCount`) only on pages that show a used price band |
| Ranking | `ItemList` of the linked generation pages, plus `BreadcrumbList` |
| /learn, method pages | `Article` with author, `datePublished`, `dateModified` |
| /data/{dataset} | `Dataset` with `name`, `description` (50–5,000 characters), `creator`, `license` as the versioned URL `…/by/4.0`, `distribution` as `DataDownload` (CSV, JSON) |
| Charging country page | `Dataset` for the series plus `Article` |

Facts from the docs I opened:

- Product markup supports pages about one product or its variants. `AggregateOffer` needs `lowPrice` and `priceCurrency`, and Google describes it as an aggregation of offers, such as one product from several merchants ([Google Product docs](https://developers.google.com/search/docs/appearance/structured-data/product-snippet)) 🟢. Our bands come from sampled listings, so keep `offerCount` equal to the visible sample size. No rich result is guaranteed.
- A third-party tracker reports Google retired vehicle-listing rich results in 2025 ([SchemaCheck](https://schemacheck.vercel.app/schema-types/vehicle-listing)) 🟡. Treat `Car` as meaning, not as a rich-result play.
- **FAQPage:** Google stopped showing FAQ rich results on 2026-05-07 ([SEJ](https://www.searchenginejournal.com/google-drops-faq-rich-results-from-search/574429/)) 🟢. Add it only where a page has real visible Q&A, as a low-priority aid for other engines. Never write questions for markup.
- Dataset markup needs only `name` and `description`; `license`, `creator` and `distribution` are recommended ([Google Dataset docs](https://developers.google.com/search/docs/appearance/structured-data/dataset)) 🟢. We add all of them.

## 5. Sitemaps and internal linking

- Sitemap index → one sitemap per country × page type, kept under the protocol limit of 50,000 URLs. `lastmod` changes only when published data changes.
- Only pages that pass the gate enter a sitemap. Gate failures return 200 with `noindex,follow` and no sitemap entry.
- **Hub and spoke:** Explore → make → model → generation → variant, with the used page and rankings as side hubs.
- Every generation page links to: previous and next generation, its used page, 3 comparable generations, each ranking it appears in, the country charging page, the relevant /learn page, and the same generation in other launch countries ("same car, cheaper in DE?").
- Rankings link to every listed generation and back. A CI check fails if an indexable page has no inbound link.

## 6. AI-search and LLM citation angle

Google says its AI features rest on core ranking and need no special markup, and that content written separately for AI risks the scaled-content policy (as summarised in the marketingskills ai-seo skill; not opened directly) 🟡. So the plan is the same content for people and machines:

- **Open data.** CC BY 4.0 summaries (real range, charge km/h, price bands, charger counts) with a download and a citation line. Datasets are easy to quote and link.
- **Number-first blocks.** Open each page and section with a 40–60 word answer containing a figure, its unit, its source and a date. Example: "In winter motorway driving the 2021 Hyundai Ioniq 5 77 kWh covers about N km (source, test date, 0 °C)."
- **Method pages and freshness.** One per metric with error rates (spec target: median range error under 10%). Visible "last updated" dates; monthly refresh for prices and charger counts.
- **Crawler access.** Allow GPTBot, ClaudeBot, PerplexityBot and Google-Extended in robots.txt. Optional `llms.txt` pointing to /data 🟡.
- **Presence and monitoring.** Assistants cite forums, Reddit and YouTube, so the launch plan seeds honest answers there. Each month, run 20 target queries in ChatGPT, Perplexity and Google and log whether we are cited.

## 7. Phased plan by workstream

Phases follow ROADMAP.md (0 foundations, 1–2 Core, 3–5 Next).

| Phase | WS2 web | WS3 content | WS5 growth |
|---|---|---|---|
| 0 | Country/lang routing and slug rules; ID-stable slugs; robots, sitemap index skeleton | Choose top 40 used models; generation definitions | Decision entry on URLs and hreflang; Search Console and Umami set up; keyword validation sample |
| 1 | Model and generation templates with gate; JSON-LD; hreflang sitemaps; breadcrumbs | 10 rankings with method notes; /learn: charging 2026, wallbox 2027, winter range, LFP | Internal-link CI check; baseline AI-citation log |
| 2 | Used and variant pages with gate; charging country pages; Dataset pages | Winter-range and V2G/V2H copy; method pages | Weekly Search Console review; promote sections on evidence; review non-default-language templates |
| 3+ | Listing-feed fields in schema | Known issues; battery health | Prune pages with no impressions after 6 months; add ES/IT at Phase 4 |

**Before scaling a page type:** pilot 50 pages, check they index within 4 weeks, then generate the rest.

## Sources

- Spec mirrors in `docs/spec/`: master-spec-v2.md (§2, §3, §14, §15), charging-buildout.md, trip-fit.md, bidirectional-and-connectors.md, research-and-notes.md
- [Google: localized versions](https://developers.google.com/search/docs/specialty/international/localized-versions?authuser=4) (opened 2026-11-15)
- [Google: Product snippet](https://developers.google.com/search/docs/appearance/structured-data/product-snippet) (opened 2026-11-15)
- [Google: Dataset](https://developers.google.com/search/docs/appearance/structured-data/dataset) (opened 2026-11-15)
- [SEJ: Google drops FAQ rich results](https://www.searchenginejournal.com/google-drops-faq-rich-results-from-search/574429/) (opened 2026-11-15)
- [SchemaCheck: Vehicle Listing (retired)](https://schemacheck.vercel.app/schema-types/vehicle-listing) (opened 2026-11-15; third-party)
