# R-33 EV usage profiles: who needs what

Date: 2026-11-15 · Author: WS0 (picks chat) · Rules: `data/editorial/shortlist_rules.yaml` · Decision 050 · Builds on R-32 (Menno's picks = the road-tripper profile)

## Bottom line

Four base profiles, one "where you live" modifier and a few ticked extras cover the real differences. The fourth profile is **no charger at home**. It is the biggest split in EV ownership after "does it do road trips", and it stacks on top of the other three rather than replacing them.

| Profile | Picker answers | What decides it | Preset filters (editable chips) |
|---|---|---|---|
| **Road-tripper**: main car that also does the holidays | only/main car + long trips yes | Fast charging (km/h), winter range, space, one-pedal | ≥200 km in 20 min DC · ≥350 km real range · boot ≥380 L |
| **Daily driver**: main car, holidays by train, rental or a second car | only/main car + long trips never | Winter range for the longest normal day, space, efficiency, heat pump, battery health | ≥250 km real range · boot ≥300 L |
| **Runabout**: second car for short trips | second car | Price, size, efficiency, battery health of cheap old EVs; DC optional | ≥150 km real range · length ≤4.3 m · cheapest first |
| **Kerbside charger**: no charger at home (stacks on 1–3) | charge at work or public only | Efficiency (public kWh costs more), DC at 50–150 kW town chargers, 11 kW AC, LFP | ≥120 km in 20 min DC · AC ≥11 kW |

**Where you live** (city / town / countryside) shifts the bars: the countryside raises the range floors (daily driver 200 → 250 km, runabout 120 → 160 km), adds weight on heat pump and home AC charging, and penalises cars too wide for lanes. The city adds weight on size and suggests the kerbside profile.

**Extras** (from the trip-fit picker): drive a lot (25,000+ km/yr), often a full car, tow, snow / steep / unpaved roads, keep 8+ years, buying used on a fixed budget.

## Why these lines

- **Daily distances are short, rural ones much longer.** 🟢 A Dutch car driver averages about 16 km a day (2024), from 14 km in the urban West to 23 km in Drenthe ([CBS 84710ENG](https://www.cbs.nl/en-gb/figures/detail/84710ENG?q=bicycle)). In France the commute is about 29 km in rural areas vs 18 km in big cities ([Ipsos Flair 2023](https://www.ipsos.com/en/flair-collection/node/1001226)), and rural households drive most of their km on 10–100 km trips ([SDES EMP 2019](https://www.statistiques.developpement-durable.gouv.fr/mobilite-des-personnes)). → The rural modifier raises range floors.
- **Long trips are a third of the km.** 🟢 French residents travel about 4,200 km a year on long trips vs 8,920 km locally ([SDES EMP 2019](https://www.statistiques.developpement-durable.gouv.fr/media/5735/download?inline)). Leaving long trips to another mode (daily driver) removes the hardest requirement, DC speed, and opens up cheaper 400 V cars.
- **Second cars need much less range.** 🟢 In German and Swedish driving logs, 220 km of range covers all the driving of about 70% of second cars, vs 390 km for the average car ([Jakobsson et al., Transportation Research C, 2016](https://research.chalmers.se/publication/232139)). → The runabout drops the DC gate; old Zoe, i3, e-208 and Leaf become valid, with a battery-health factor instead.
- **No home charger is common and costly.** 🟢 17% of EV drivers in France (and Europe) have no home charger ([Roland Berger EV Charging Index 2025, France](https://www.rolandberger.com/en/Insights/Publications/EV-Charging-Index-2025-Expert-insights-from-France.html)). In French towns a third of car-owning households have no private parking, while rural detached houses make home charging easy ([Insee via Maire-info, Nov 2025](https://www.maire-info.com/vehicules-electriques-le-nombre-de-points-de-charge-accessibles-au-public-a-augmente-de-69--en-un-an-article2-30242)). In the UK, 87% of drivers with a driveway find their EV much cheaper to run vs 50% without ([EVA England 2025 via Zemo](https://www.zemo.org.uk/news-events/news,eva-driver-survey-shows-growing-divide-between-those-who-can-charge-at-home_4789.htm)). → Efficiency gets heavier, and so does charging well on the 50–150 kW chargers at supermarkets.
- **Countryside chargers are for topping up.** 🟢 Public points per 10,000 people: 21 urban vs 16 rural in France (same Insee study), and 75% of points are under 50 kW. → Rural road-trippers and daily drivers need range margin more than charger density.
- **High mileage is fine for modern batteries.** 🟡 Liquid-cooled packs degrade slowly after the first years, and LFP holds up better than NMC ([InsideEVs](https://insideevs.com/news/797638/high-mileage-ev-battery-degradation/)). → "Drive a lot" is an extra (efficiency, battery health, warranty km left), not its own profile.

## Considered and not made a profile

- **High-mileage / work car**: same needs as road-tripper or daily driver, plus efficiency and battery weight → extra.
- **Family hauler / tower**: a space or towing filter on any profile → extras (already in trip-fit §4).
- **Budget first EV**: a price band, not a usage pattern → filter + "used, fixed budget" extra.

## Uncertain / to calibrate

- 🔴 Only the road-tripper is back-tested (80% on Menno's picks). Daily driver, runabout and kerbside thresholds come from the statistics above, not from anyone's picks. Calibrate them in the five-person normie test (R-30), ideally with one person per profile.
- 🟡 "Real range" is the published mixed figure until Trip fit's winter model lands; the gates assume winter is about 20–25% lower.
- 🟡 Width is not in the schema yet, so the "too big for lanes" penalty can't fire (T-066).
