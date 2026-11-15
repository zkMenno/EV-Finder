# Glossary sweep — every column, filter and badge → glossary id

Addendum 5, bottomless backlog item 1 (overnight, 2026-11-15). Lane: `data/taxonomy/glossary_terms.yaml` + `validate_taxonomy.py`. The web app was not touched (a web builder is active); what it needs is in the list at the end.

**Counts:** glossary 49 → **88 terms** (39 added, EN complete + NL label and short). All 12 ids from Q-061 now exist. `validate_taxonomy.py` is clean (0 errors) and `--self-test` passes 25/25, including two new checks:

- a glossary id may not reuse a `/learn` article slug (both live at `/learn/<slug>`);
- every `[[id]]` / `[[id|text]]` marker and front-matter `glossary:` id in `content/learn/**/*.md` must resolve.

**Status key:** **wired** = the term exists and the UI shows its ⓘ · **had, not wired** = the term exists but the UI doesn't attach it (or attaches the wrong one) · **added** = new tonight, UI still needs to wire it · **none needed** = a name or action, not a term · **still missing** = no row yet, with the reason.

Scanned: `apps/web/src` (Explore.tsx, spec-diff.ts `SPEC_FIELDS`, SpecValue, model / generation / variant / compare / rankings pages, TripModule, Num, QualityBadge, PriceBand, Switchers, `i18n/en.json`), `content/learn/*/*.md`, `docs/spec` (master spec §4, §8; trip-fit; bidirectional; charging-buildout), and `data/taxonomy` tables.

## Explore: table columns (`COLS`)

| Label (en.json) | Level | Glossary id | Status |
|---|---|---|---|
| Car (`col.car`) | all | — | none needed (name) |
| Generation | D/N | `generation` | wired |
| Variant | D/N | `variant` | wired |
| Years | all | `model-years` | wired |
| Era | D/N | `era` | wired |
| Real range | all | `real-range` | wired |
| Battery | D/N | `usable-vs-gross` | wired. Optional swap to **`battery-capacity`** (added; Q-024 said the plain label read oddly) |
| DC fast charge (km in 20 min) | all | `dc-km-20min` | wired |
| AC charge | D/N | `ac-charging` | wired |
| New price | all | `new-price` | wired |
| Registered (NL) | D/N | `registrations-nl` | wired |
| Voltage (class) | D/N | `voltage-class` | wired |
| Voltage (nominal) | N | `nominal-voltage` | wired |
| On 400 V chargers | N | `400v-charger-behaviour` | wired |
| Battery type | D/N | `chemistry` | wired |
| Cooling | N | `cooling` | wired |
| Platform | N | `platform` | had, not wired (`term` missing on the col) |
| Battery pack | N | `battery-pack` | had, not wired (`term` missing on the col) |
| Data quality (badge) | all | `quality-tier` | wired |
| Your trips (trip column) | all | `trip-fit` | **added** |

## Explore: filters, controls, chips

| Label | Glossary id | Status |
|---|---|---|
| Max new price | `new-price` | wired |
| Era chips | `era` | wired |
| Body chips | `body-type` | wired |
| Min real range | `real-range` | wired |
| Fast on older 400 V chargers | `400v-charger-behaviour` | wired |
| OK to charge to 100% daily | `charge-to-100` | wired |
| Segment chips | `segment` | wired |
| Charging voltage chips | `voltage-class` | wired (chips: 400v / 800v / 900v-plus rows) |
| Battery type chips | `chemistry` | wired (chips: chemistry rows) |
| Battery cooling chips | `cooling` | wired |
| Min battery (kWh) | `usable-vs-gross` | wired (optional swap to `battery-capacity`) |
| Min DC km in 20 min | `dc-km-20min` | wired |
| Min boot | `boot-volume` | wired |
| Max length | `vehicle-length` | wired |
| Min towing | `towing-capacity` | wired |
| Advanced: min / max battery voltage | `nominal-voltage` | wired |
| Only cars that do my trips in winter (filter) | `trip-fit` | **added** |
| Trip chip "Your trips: N km round trip" | `trip-fit` | **added** |
| Detail level: Simple / Detailed / Nerd | `detail-level` | **added** |
| View: Table / Cards | — | none needed (control) |
| Price mode: Buy / Loan / Lease (T-043, not built) | `price-mode` | **added** |

## Explore cards view

| Item | Glossary id | Status |
|---|---|---|
| Real range, DC km in 20 min, New price, Battery, DC peak, AC, Voltage, Battery type, Registered, Era, Cooling, On 400 V, Nominal voltage | same ids as the table (`peak-kw` for DC peak) | label only. The card uses the term's **label** but shows no ⓘ |
| Used price | `used-price` | **added** |
| DC km in 10 min | `dc-km-10min` | **added** |
| Platform / Battery pack | `platform` / `battery-pack` | had, not wired |
| Quality badge | `quality-tier` | label only, no ⓘ on cards |

## Number badges and popovers (`Num`, `QualityBadge`)

| Badge / label | Glossary id | Status |
|---|---|---|
| "N sources agree" | `sources-agree` | had, not wired |
| "1 source" / Single source tier | `quality-tier` | had, not wired in Num |
| "estimate" | `estimate` | had, not wired |
| "claim" | `claim` | had, not wired |
| Confidence high / medium / low | `confidence` | had, not wired |
| "Calculated by us" | `derived` | **added** |
| Range method / fallback rung (`rung.*`, `col.rung`) | `real-range-rung` | had, not wired |
| "release of {date}" (Nerd) | `data-release` | **added** |
| "not disclosed" | `not-disclosed` | had, not wired |
| Tiers: Checked / Sourced / Single source | `quality-tier` | wired on the Explore column only |

## Model, generation, variant pages and Compare (`SPEC_FIELDS`, shared)

| Field (`field.*`) | Current `term` in spec-diff.ts | Should be | Status |
|---|---|---|---|
| real_range_km | `real-range` | same | wired |
| wltp_range_km | `wltp` | same | wired |
| consumption_kwh_100km, consumption_motorway | `consumption` | same | wired |
| battery_kwh_net | `usable-vs-gross` | `battery-capacity` (optional) | wired |
| chemistry_id | `chemistry` | same | wired |
| charge_100_daily | `chemistry` | **`charge-to-100`** | had, wrong id |
| cooling_id | `cooling` | same | wired |
| cell_format | `cell-format` | same | wired |
| voltage_class_id | `voltage-class` | same | wired |
| voltage_label (maker's label) | none | `voltage-class` | had, not wired |
| voltage_nominal_v / voltage_max_v | `nominal-voltage` | same | wired |
| platform_name | `platform` | same | wired |
| dc_km_per_20min | `dc-km-20min` | same | wired |
| dc_km_per_10min | `dc-km-20min` | **`dc-km-10min`** | added, wrong id today |
| dc_peak_kw | `peak-kw` | same | wired |
| dc_avg_10_80_kw, dc_minutes_10_80 | `10-80` | same | wired |
| dc_peak_held_min | `charge-curve` | same | wired |
| charger_400v_mode / kw, fast_on_400v | `400v-charger-behaviour` | same (fast_on_400v has none) | wired / not wired |
| ac_kw, ac_km_per_h | `ac-charging` | same | wired |
| power_kw | none | `motor-power` | **added** |
| accel_0_100_s | none | `acceleration-0-100` | **added** |
| drivetrain | none | `drivetrain` | **added** |
| length_mm | none | `vehicle-length` | had, not wired |
| weight_kg | none | `kerb-weight` | **added** (label "Weight"; definition varies by source) |
| boot_l | none | `boot-volume` | had, not wired |
| seats | none | `seats` | **added** |
| towing_kg | none | `towing-capacity` | had, not wired |
| body | none | `body-type` | had, not wired |
| segment | none | `segment` | had, not wired |
| price_new | none | `new-price` | had, not wired |
| registered_count_nl | `registrations-nl` | same | wired |
| Used price in {country} (generation / variant) | — | `used-price` | **added** |
| Registrations in {country} | — | `registrations-nl` | wired on model / generation; not on variant / compare |
| "years not yet checked" badge | — | `model-years` | had, not wired |
| Era badge / timeline colours (model page) | — | `era` | had, not wired |
| V2L / V2H / V2G badges (variant page, bidi spec §3; not built) | — | `v2l`, `v2h`, `v2g`, `v2b`, `bidirectional-charging` | **added** |
| Plug type (variant page; not built) | — | `type-2`, `ccs2`, `chademo` | **added** |
| Compare: "differs", "show only differences", share, print | — | — | none needed (actions) |

## Rankings (`/top`, `/top/[list]`)

| Header / metric | Glossary id | Status |
|---|---|---|
| Rank, Car, Generation | — | none needed |
| Longest real-world range: "Real-world range" | `real-range` | had, not wired |
| … "New price" column | `new-price` | had, not wired |
| Fastest DC: "km added in 20 min" | `dc-km-20min` | had, not wired |
| Most available NL: "Registered in NL" | `registrations-nl` | had, not wired |
| "N of M values are estimates" | `estimate` | had, not wired |
| Planned per-country "best used under €15k / 20k / 25k" (backlog item 4) | `used-price` | **added** |

## Trip fit (TripModule, trip-fit spec)

| Label | Glossary id | Status |
|---|---|---|
| Find cars for my trips / Your trips / verdict ✓ ⚠ ✗ | `trip-fit` | **added** |
| The range you truly need | `range-you-need` | **added** |
| ≈ WLTP (winter / summer) | `wltp-equivalent` | **added** |
| margin {pct}% | `trip-margin` | **added** |
| start {pct}% · assumptions line | `start-charge` | **added** |
| health {pct}% · "Keep 8+ years: 85% battery health" | `soh` | had, not wired |
| Home town (winter temperature), "normal January day" | `climate-normal` | **added** |
| Town / Rural roads / Motorway · Wh/km per road band (Nerd) | `road-band` | **added** |
| Winter need P10–P90 (Nerd) | `uncertainty-band` | **added** |
| Rung / fixture matrix (Nerd) | `real-range-rung` | had, not wired |
| Share on the motorway, driving profile, car role, long trips, extras | — | none needed (plain questions) |
| Fit score, "Why this order" weights (Core 2, not built) | — | still missing: not built yet; write when `usage_profiles` lands |

## Price modes (Decision 017, T-043; UI not built)

| Label | Glossary id | Status |
|---|---|---|
| Buy outright / Loan per month / Lease per month | `price-mode` | **added** |
| Loan | `loan` | had (not built) |
| Lease / Private lease | `lease`, `private-lease` | had (not built) |
| Balloon / PCP | `balloon-pcp` | had (not built) |
| Residual value | `residual-value` | had (not built) |
| Total over the term | `total-cost-over-term` | had (not built) |
| Interest rate (APR) | `apr` | **added** |
| Deposit | `deposit` | **added** |
| Term (months) | `loan-term` | **added** |
| "Estimate, not an offer" | `estimate` | had (not built) |
| "Borrowing money costs money" (CCD2 warning) | — | none needed (legal text) |

## Content (/learn articles) and charging pages

| Term in the text | Glossary id | Status |
|---|---|---|
| V2L, V2H, V2G, two-way charging | `v2l`, `v2h`, `v2g`, `bidirectional-charging` | **added** (Q-061) |
| ISO 15118-20 | `iso15118-20` | **added** (Q-061) |
| Type 2, CCS2, CHAdeMO | `type-2`, `ccs2`, `chademo` | **added** (Q-061) |
| AFIR, pay without an account, roaming app/card, idle fee | `afir`, `ad-hoc-payment`, `roaming`, `idle-fee` | **added** (Q-061) |
| Plug & Charge | `plug-and-charge` | **added** |
| TEN-T core network | `ten-t` | **added** |
| Charging points (country table, `charging_metrics`) | `charging-point` | **added** |
| Mode 2 portable charger, smart meter, DIN 70121 | — | still missing: each appears once in a nerd aside. Not worth a tooltip yet |
| All other `[[id]]` markers in content/learn | existing ids | all resolve (now checked by the validator) |

## Taxonomy rows that are terms

- `bidi_modes` v2l / v2h / v2g / v2b, `bidi_protocols` iso15118-20 / chademo, `connector_types` ccs2 / chademo: the glossary rows use the **same id**, so a UI can link straight from the row id to `/learn/<id>`.
- `connector_types` **`type2`** ↔ glossary **`type-2`** (Q-061 asked for the hyphen; Decision 019 style). See Q-062.
- `bidi_status`, `bidi_caveats`, `bidi_routes`, `charging_metrics`, `charging_definitions`, `power_bands` carry their own `label` + `short`, so they need no glossary row. They can point to one through `glossary_id`, which the validator already checks. That field is in the WS3 / coordinator lane and was not set tonight.
- Non-EU plugs (`type1-j1772`, `ccs1`, `nacs-j3400`, `gbt-*`): still missing on purpose. They are parked or outside Europe, and the row's own `short` is enough.
- C-rate and cell supplier (Nerd, spec §4): still missing. There are no fields or data yet.

## For the web builder: labels that need a `<Term id>` wired

Data is ready in `glossary_terms.yaml`. A missing id already falls back to the plain label, so each of these is a safe, small change.

1. **Explore columns:** add `term: "platform"` to the `platform` col and `term: "battery-pack"` to the `pack` col.
2. **Explore trip column + filter + chip:** `trip-fit`.
3. **Detail-level switch (Switchers):** `detail-level`.
4. **Cards view:** show the ⓘ (not just the label) for every `item(term(...))`, plus `used-price` on "Used price", `dc-km-10min` on "DC km in 10 min", `platform` and `battery-pack`.
5. **`lib/spec-diff.ts` SPEC_FIELDS** (fixes variant, generation and compare at once):
   - `charge_100_daily` → `charge-to-100` (currently `chemistry`)
   - `dc_km_per_10min` → `dc-km-10min` (currently `dc-km-20min`)
   - `voltage_label` → `voltage-class`
   - `fast_on_400v` → `400v-charger-behaviour`
   - `power_kw` → `motor-power`
   - `accel_0_100_s` → `acceleration-0-100`
   - `drivetrain` → `drivetrain`
   - `length_mm` → `vehicle-length`
   - `weight_kg` → `kerb-weight`
   - `boot_l` → `boot-volume`
   - `seats` → `seats`
   - `towing_kg` → `towing-capacity`
   - `body` → `body-type`
   - `segment` → `segment`
   - `price_new` → `new-price`
   - optional: `battery_kwh_net` → `battery-capacity`
6. **Used price** on generation and variant pages: `used-price`. Add `registrations-nl` on the variant page "Registrations in {country}" row.
7. **Num popover / badges:** `sources-agree`, `estimate`, `claim`, `confidence`, `derived` ("Calculated by us"), `real-range-rung` (rung note), `data-release` ("release of {date}"), `not-disclosed`.
8. **Badges:** "years not yet checked" → `model-years`; era badge / timeline → `era`; quality badge outside the Explore header → `quality-tier`.
9. **Rankings headers:** `real-range`, `new-price`, `dc-km-20min`, `registrations-nl`; the estimates note → `estimate`.
10. **TripModule:** result card → `range-you-need`; "≈ WLTP" → `wltp-equivalent`; margin → `trip-margin`; start % → `start-charge`; health % → `soh`; home town / January temperature → `climate-normal`; road bands → `road-band`; P10–P90 → `uncertainty-band`; Nerd rung → `real-range-rung`.
11. **Price modes (T-043) when built:** `price-mode`, `loan`, `lease`, `private-lease`, `balloon-pcp`, `residual-value`, `total-cost-over-term`, `apr`, `deposit`, `loan-term`, `estimate`.
12. **Variant page bidi and plug block (when built):** `v2l`, `v2h`, `v2g`, `v2b`, `bidirectional-charging`, `type-2`, `ccs2`, `chademo`, `iso15118-20`.
13. **Possible bug seen while scanning (not fixed, outside the lane):** `ChemistryInfo` in `Explore.tsx` links to `` `/${ctx.country}/learn/chemistry` ``. That drops the language segment (Decision 015 routes are `/{country}/{lang}/…`). It should probably use `ctx.base`.

## For WS3 content

The Q-061 ids exist now, so the drafts can add `[[v2l|…]]`, `[[ccs2|…]]`, `[[afir|…]]` and so on. `[[plug-and-charge]]`, `[[ten-t]]` and `[[charging-point]]` are also available. The validator fails on any marker that doesn't resolve.
