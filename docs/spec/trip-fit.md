<!-- Mirror of the claude.ai spec doc, tab "Trip fit" (rev 1), exported 2026-11-15 by WS0. For builders this repo copy wins; product changes start in the doc and WS0 mirrors them here. Transcribed from the export; if a figure looks off, check the doc tab. -->

# Trip fit — the range you truly need

Status: proposed 15 Nov 2026. Quick version = Core 1, routes = Core 2. Lanes: WS1 data + model, WS2 UI, WS3 content. Legend: 🟢 verified · 🟡 reasoned / secondary source · 🔴 unsure, check before building.

**One line:** tell us where you drive and how you'll use the car; we show which EVs (every variant, new and used) do those trips in winter without charging, and re-rank the Explore table for your life.

## 1. Why this, and what already exists

- **EV Database** shows fixed range estimates per car (cold/mild × city/highway/combined). Fixed scenarios, not your routes. 🟡
- **ABRP EV comparison** (launched 2026): up to three cars on one route with weather, elevation and chargers. 🟢
- **Motability UK range tool**: plan a route and see if a car on their scheme does it without charging. 🟢
- **Our gap:** the whole catalogue at once (\~1,500 variants, used included), several recurring trips weighted by how often you drive them, winter as the default, used-battery health, and the answer drives the shortlist and ranking. Detailed trip planning with chargers stays ABRP's job: we deep-link (already planned in Charging buildout).

## 2. What the research says

| Finding | Number | Conf. |
| --- | --- | --- |
| Average range kept at 0 °C (Recurrent, 18k US cars) | \~80% | 🟢 |
| With heat pump vs without | \~83% vs \~75% kept | 🟢 |
| Newer Recurrent study (Nov 2025, 30k cars) | 0 °C: 78% avg (best 88, worst 69); −7 °C: 70% avg | 🟡 secondary |
| Spread by model (older Recurrent) | 16–46% loss | 🟢 |
| NAF El Prix winter 2025 | most cars 15–30% below WLTP | 🟢 |
| NAF El Prix winter 2026 (down to −32 °C) | average −38% vs WLTP | 🟢 |
| Speed: 90 → 120 km/h (Bjørn Nyland tests) | consumption +32% to +50% | 🟢 per test, 🟡 as rule |
| Cold hurts short town trips most; at motorway speed air drag dominates | qualitative | 🟡 |
| Preheating while plugged in is the biggest fix | qualitative | 🟢 |

**Takeaway:** 20–30% is right for a normal 0 °C day, but the model must not use a flat percentage. Loss = temperature × speed × trip length × heater type, and a cold snap or fast motorway driving pushes it past 35%.

## 3. UX flow

Principles: optional, never a gate · about 60 seconds · every step skippable with sensible defaults · anonymous, saved in the browser · mobile first.

**Entry points:** button "Find cars for my trips" above the Explore table · once set, a profile chip at the top of the table and a filter "Does my trips in winter" · widget on model pages "Will this car do my trips?" · /learn "Winter range explained".

**Step 1 — How you'll use it** (profile picker, five taps, section 4).

**Step 2 — Your places.** Home = town search or map pin. Then add places (quick chips: Work, Family, Holiday spot, Airport; up to 10). Per place:

- How often: Weekly · Monthly · A few times a year · Must reach without charging
- Can you charge there? No (round trip counts) · Slow / overnight · Fast charger nearby
- Optional via-stops

Frequency decides how hard the rule is: weekly, monthly and "must reach" are hard requirements (a car that fails drops out of "fits"); "a few times a year" is soft (one short charging stop is fine, we show its time).

**Step 3 — Winter.** "A normal January day near you: 4 °C" (from climate normals, editable) · toggle "check a cold snap" (colder 10th-percentile day) · "I preheat on the plug" yes/no · how I drive: a bit slower / at the limit / a bit faster · arrival buffer (default 10%).

**Step 4 — Result.**

- Card **"The range you truly need"**: X km in winter on your mix (Y km in summer), "≈ Z km WLTP" so people can compare with ads. A bar of your km by road type plus total climb.
- Explore table re-ranked; new column **Your trips** (✓ all · ⚠ tight · ✗ needs a stop) and a **Fit** score; filter "only cars that do my must-do trips in winter". Failing cars stay visible, greyed, with the reason.
- Expand a row: per trip, % of battery used with an uncertainty band.
- "Why this order" panel shows the weights; sliders to change them.

**Step 5 — Keep it.** Edit any time from the profile chip; share link holds summaries only, never places; account (optional) syncs it.

**Model page widget:** same trips for one car, plus "Used: assumes 90% battery health — change" (or the real figure from a battery report).

## 4. Usage profile picker

| Question | Options | What it changes |
| --- | --- | --- |
| This car will be | Our only car · Main car · Second car | Second car: road-trip weight off unless asked. Only car: road trips and DC speed weigh more |
| Long trips (300 km+) | Never · 1–3 a year · Monthly · Often | DC km in 20 min, winter 10–80% time, battery size, 800 V, cooling (air-cooled flagged), "1,000 km in winter" time |
| Where you'll charge | Home · Work · Public only | Start charge level; AC onboard charger (11/22 kW) weight; public-only raises DC and efficiency weight; LFP / "charge to 100% daily" bonus |
| Your driving | Mostly town · Mixed · Mostly motorway | Road mix when no trips are entered (auto-filled from trips when they are) |
| Extras (multi) | Tow · Roof box · Full car often · Snow / mountain roads · Keep 8+ years | Towing filter + big range penalty (🔴 calibrate); roof box penalty (🔴); AWD / clearance; battery-risk and warranty weight |

Budget stays in the existing filters.

## 5. The range model

Per trip, per variant, per condition:

**Energy needed** = Σ over road bands (km in band × consumption at that speed and temperature) + warm-up energy per cold start + climb energy

- **Road bands** from the route: town (≤ 50 km/h roads), rural (60–90), motorway (100+). Speed per band = country speed profile (e.g. NL 100 by day, FR 130, DE advisory 130, UK 70 mph) adjusted by driving style (−10 / 0 / +10 km/h).
- **Consumption (Wh/km)**, fallback ladder (rung shown in Nerd mode):
  1. Measured for this variant at that speed and temperature (Bjørn Nyland 90/120 km/h, ADAC, NAF El Prix, other condition-tagged tests)
  2. Same platform / pack measured, scaled for mass and wheel size
  3. Physics: drag ½ρ·Cd·A·v², rolling resistance, drivetrain efficiency, auxiliary load; cold raises air density and tyre losses 🟡
  4. WLTP × class-average real-world ratio
- **Temperature curve** per heater type (heat pump / resistive / unknown), fitted to Recurrent and El Prix ratios; replaced by the car's own curve when it has a winter test.
- **Warm-up energy**: fixed kWh per cold start for cabin and battery (more without a heat pump), dropped if preheated on the plug. Order of 1–3 kWh 🔴 — fit from data.
- **Climb**: mass × g × height gained ÷ efficiency, minus regen on the way down (\~60% recovered 🟡).

**Energy available** = usable kWh × battery health × (start charge − arrival buffer).

- Weekly / monthly trips start at the daily limit: 80% for NMC, 100% where the variant's "charge to 100% daily" is true.
- Occasional and must-reach trips start at 100%.
- Round trip without charging = there + back; slow charging at destination = each leg on its own.

**Verdict per trip:** ✓ margin ≥ 15% of usable · ⚠ 0–15% or the band crosses zero · ✗ short → show "1 stop, about N min" from winter DC data.

**Range you truly need** = the biggest must-do trip in winter plus buffer, shown as km on your mix and as WLTP-equivalent (using the median WLTP ratio for that mix).

**Uncertainty:** P10–P90 band from the rung's confidence. Simple mode shows only ✓/⚠/✗ and one number.

**Validation gate:** back-test on El Prix routes (known town / motorway / mountain mix) and Bjørn Nyland tests; median error under 10% for the top-40 used models before launch (joins Data QA gap 9).

## 6. Profile → Fit score

Weights live in an editable table `usage_profiles` (a new row, not new code). Winter margin on your must-do trips is a hard rule, then:

| Profile | Price | Efficiency | DC km/20 min (winter) | 1,000 km winter time | AC speed | Battery risk |
| --- | --- | --- | --- | --- | --- | --- |
| Second car, town, home charging | high | med | low | off | low | med |
| Main car, monthly road trips | med | med | high | high | low | med |
| Only car, often long trips | med | med | very high | very high | low | high |
| Public charging only | med | high | high | med | high | med |
| Keep 8+ years (add-on) | — | — | — | — | — | +1 step, + warranty |

Always explainable: "ranked 3rd because: does all your trips with 24% spare, fast in winter, cheaper than the two above".

## 7. Tech and data

- **Routing: self-hosted Valhalla** (open source, OpenStreetMap, gives road class, speed and elevation per segment). Hosted free APIs are out for production: the openrouteservice free plan (2,000 routes/day) and GraphHopper's free plan are both non-commercial. ORS free is fine for prototyping on staging 🟡.
- **Where:** a separate small Hetzner Arm box, not the shared CAX31 (already \~1 GB over its worst-case budget in the job window). Routing-only guidance: 4–8 GB RAM and 10–50 GB disk per small country; NL+BE+LU+DE+FR+UK needs a sizing test 🔴. Monthly tile rebuild. Cost \~€5–15/month 🔴 check Hetzner prices.
- **Geocoding:** no Nominatim (Europe needs \~64 GB RAM). Town search from GeoNames cities (CC BY 4.0) plus a map pin. Basemap: OpenFreeMap or Protomaps PMTiles 🟡.
- **Scoring runs in the browser:** the server returns a route summary per trip (km per band, climb, descent, number of starts); the browser multiplies it with a per-variant consumption matrix (\~1,500 variants × 3 bands × 5 temperatures, static JSON). Re-ranking every car is instant; server load = one route call per trip edit.
- **Climate:** Meteostat climate normals (licence page now says CC BY 4.0; older docs said CC BY-NC → confirm before ingest 🟡); fallback Copernicus ERA5 monthly means.
- **Privacy:** addresses never stored on the server; coordinates rounded to \~200 m before routing; no request logging on the route endpoint; accounts store trip names + summaries only; share links carry summaries, not places. Add to the GDPR gap (7).
- **New data:** taxonomies `road_classes` (OSM highway → band), `speed_profiles` (per country), `temperature_bands`, `heater_types`, `usage_profiles`; variant fields `heat_pump` (standard / option / none / not disclosed), `drag_coefficient`, `frontal_area`, `kerb_mass`, `wheel_size`, `usable_kwh`; condition-tagged `consumption_tests` (speed, temperature, wheels, source, date); derived `consumption_model` per variant with rung + confidence; `climate_normals` per town / grid cell.
- **ABRP:** per trip, "Plan this in ABRP" deep link with the car pre-selected (uses the abrp\_typecode work already queued).

## 8. Simple / Detailed / Nerd

- **Simple:** ✓/⚠/✗ and "needs about 210 km in winter; this car has about 260".
- **Detailed:** per-trip bars, summer vs winter, stop time if any, what the profile changed.
- **Nerd:** Wh/km per band, temperature curve, rung and source per number, P10–P90, JSON download.

## 9. Phasing and tasks

- **Core 1 — Quick range check (no map):** profile picker + three inputs (longest regular round trip in km, share of motorway, home town for temperature) → same model, new Explore column. Needs consumption matrix v1.
- **Core 2 — Trips with routes:** Valhalla box, places + frequency, destination charging, cold snap, model-page widget, Fit score.
- **Next:** 1,000 km winter time score (driving + charging), towing / roof box calibration, ABRP three-car compare link, "this week's forecast" for saved trips.
- **Parked:** our own charger-aware route planner (ABRP does this well).

**WS1:** consumption\_tests ingest with conditions · consumption\_model builder + ladder · temperature curves per heater type · climate normals ingest + licence check · back-test harness · Valhalla sizing test + deploy. **WS2:** profile picker · trips flow · result card · Explore column + filter · model-page widget · three detail modes · browser storage + account sync. **WS3:** copy in 6 languages · /learn "Winter range explained" · heat\_pump field for top-40 used models (incl. option fitted or not) · speed\_profiles per launch country.

## 10. Risks

- **False precision:** always "about" plus a band; never a promise. Clear note that weather, tyres and load change results.
- **Unknown heat pump on used cars** (often an option): show both cases until the owner confirms.
- **Overlap with ABRP:** we pick the car, ABRP plans the trip; link, don't compete.
- 🔴 Valhalla sizing and cost · 🟡 Meteostat licence · 🔴 warm-up energy and towing factors need data.

## Sources

- [Recurrent winter study via InsideEVs](https://insideevs.com/news/747374/ev-range-loss-cold-heat-pump-data/) · [KBB summary](https://www.kbb.com/car-news/study-the-average-ev-keeps-80-of-its-range-in-the-cold) · [Selectra on Recurrent Nov 2025](https://selectra.co.uk/energy/news/electric-car-winter-range-0c) · [Recurrent 16–46% spread](https://autoremarketing.com/?p=64717)
- [El Prix winter 2025 (InsideEVs)](https://insideevs.com/news/747548/ev-winter-range-test-norway-2025/) · [El Prix winter 2026 (GreenFleet)](https://www.greenfleet.net/node/20095) · [NAF](https://www.naf.no/elbil/elbil-nytt/ev-range-and-charge-test)
- Bjørn Nyland speed tests: [ID.3](https://insideevs.com/news/445471/vw-id3-range-test-range-efficiency/) · [Kia EV6](https://insideevs.com/news/572096/kia-ev6-rwd-range-test/) · [Model 3 SR+](https://insideevs.com/news/501789/2021-tesla-model3-srp-range/)
- [ABRP EV comparison](https://abetterrouteplanner.com/resources/article/2026-02-15_car-comparison-guide) · [Motability range tool](https://news.motability.co.uk/?p=13779)
- [openrouteservice plans](https://openrouteservice.org/plans/) · [GraphHopper plans](https://docs.graphhopper.com/openapi/section/plans-and-rate-limits) · [Routing hardware guide](https://sumguy.com/self-hosted-maps-stack-picker/) · [Nominatim Europe sizing](https://community.openstreetmap.org/t/osm-valhalla-and-curvature-server/117482)
- [Meteostat licence](https://dev.meteostat.net/license) · [Meteostat normals](https://dev.meteostat.net/bulk/normals.html)
