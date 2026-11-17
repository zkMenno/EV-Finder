# R-40 Used EV price anchors and free price-index terms (T-056, T-081)

WS1, 2026-11-15. Time-boxed: about 6 searches. Question: what can calibrate a used price band per variant, build year and country without scraping marketplaces (Decision 004)?

## 1. Free price indices (layer 0): terms check

| Index | What it publishes | Licence / terms | Use |
|---|---|---|---|
| AutoScout24 AGPI (DE, AT, CH) | Monthly average asking price by fuel type (BEV October 2026: €39,658, +1.7 % m/m), based on ~700,000 DE listings | Press release, no named licence | Internal sanity check only |
| Autotrader Retail Price Index (UK) | Monthly average used price and like-for-like YoY by fuel type (used EV July 2026 £24,946, +3.3 % YoY) | Press release, no named licence | Internal sanity check only |
| Indicata Market Watch / white papers (13 countries) | Retail price index by fuel type, Dec 2024 = 100 (Europe ex-UK BEV: 92.56 April 2026, 93.42 June 2026) | White papers, no named licence | Internal sanity check only |
| AUTO1 Group Price Index | European wholesale index, Jan 2015 = 100 (136.4 in August 2026) | Press release, all fuels | Not useful (no BEV split) |

🟡 None of them names a licence. Under Decision 009 their values don't reach a public release. Showing them as a trend line (spec §8, layer 0) needs written permission: a WS5 outreach item. They measure the country's average asking price across all ages and models, so they can't give depreciation by age anyway.

## 2. Depreciation anchors (share of the list price)

| Age | Value | Source (as reported) | Country |
|---|---|---|---|
| 1 year | ~75 % (first-year loss ~25 %) | Allianz, via Autohero (2026) | DE |
| 3 years | 51.5 % on average for BEVs (petrol 62.7 %, diesel 61.1 %) | DAT, reported by autohaus.de 28 Sep 2026 and Autohero | DE |
| 3 years | 45–55 % for volume EVs | DAT-Report 2026 + Bähr & Fess Forecasts 2026, via fahrzeugschein.de | DE |
| 3 years | 50–60 % (a €50k EV worth €25–30k) | AutoScout24 NL advice page | NL |
| 5 years | 40–47.5 % for EVs sold in 2020 (100–150k km) | ING, via Accountancy van Morgen | NL |
| 5 years | ID.3 lost 58 %, Model 3 59 % | Study reported by Automobile Propre | FR |
| <3 years | Average used price €32,702 vs new €38,695 (Jan–May 2026, mixed ages and models) | Avere-France / Mobilians, via Auto Infos | FR |

🟢 The 3-year DAT figure is the firmest anchor. 🟡 Years 6–10 have no clean EV source; we extrapolate (about −8 % a year, in line with general "older cars approach 30–35 % of new" statements) and mark them low confidence.

Spread: DAT/B&F give 45–55 % at 3 years for volume EVs (≈ ±10 % around the middle), and DAT counts each extra 5,000 km a year as roughly −3 to −5 %. We use P25/P75 = median × (1 ∓ 0.12).

## 3. What this means for T-081
- Method: list price at registration (RDW catalogusprijs for NL; cited maker prices for DE/FR) × an age curve built from the anchors above. Every band is an estimate with `samples: 0` until manual samples exist.
- Manual samples (layer 2) are what turns an estimate into a measured band. They must be aggregates (count, P25, median, P75 per build year), noted by a person from our own pre-filled searches, with URL and date.
- Refit the curve when the DAT 3-year figure moves by more than 3 points or manual samples disagree by more than 15 % median.
- Price shock caveat: the 2026 fuel-price shock lifted used BEV prices (Indicata, DAT). The anchors are from autumn 2026, so they already include it.
