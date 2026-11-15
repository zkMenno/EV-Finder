# Spec — Bidirectional charging and plug standards

Status: Core phase 2 (filters + model-page block), with schema fields in phase 1. Owner: WS0. Research: `research/R-01-bidirectional-and-connectors.md`. Decision 011.

Builders read this file; the claude.ai spec tab "Bidirectional & connectors" mirrors it, and for builders this repo copy wins.

## 1. Why

- Bidirectional charging is moving from pilots to products in 2026 (France, Germany, UK live; NL pilots; US V2H live). Buyers ask "can this car power my house?", and the honest answer depends on **car + software version + battery size + wallbox type + country + energy contract**. No current site answers that per used car.
- From **1 Jan 2027** every new or renovated EU wallbox, home ones included, must speak **ISO 15118-20** (AFIR via Delegated Regulation 2025/656). That makes the wallbox protocol-ready for V2G, but **does not make it bidirectional**. We explain this plainly and never claim "all new chargers are bidirectional".
- US buyers need to know the plug: **CCS1 or native NACS (SAE J3400)**, per model year.

## 2. User-facing features

### 2.1 Explore filters (Simple mode labels; technical term underneath)

| Filter | Plain label | Logic |
|---|---|---|
| `bidi.v2l` | Powers appliances (V2L) | any row with mode `v2l`, status live |
| `bidi.v2h` | Can power your home (V2H) | mode `v2h`, status `live` in the selected country (toggle: "any country") |
| `bidi.v2g` | Can earn by feeding the grid (V2G) | mode `v2g`, status `live` in the selected country |
| `bidi.route_ac` | No expensive special box needed | route `ac_onboard` |
| `bidi.iso20` | Ready for the 2027 charger standard (ISO 15118-20) | car-side `iso15118_20` = yes |
| `bidi.include_pilots` | Include pilots and announced | widens status to `pilot`, `announced` |
| `connector.dc` / `connector.ac` | Fast-charge plug / home plug | from `ChargingPort` rows for the selected market |
| `connector.us_supercharger` | (US) Plugs into Tesla Superchargers | `native` or `adapter` (sub-filter "no adapter needed") |

Defaults: V2H/V2G filters mean **live in your country**. A car that only does V2G in France does not match V2G for a German user unless they widen it.

### 2.2 Caveat badges (shown on cards, table and model page)

Badges come from the `bidi_caveats` taxonomy, never free text in the UI:
`needs_dc_box` "Needs a special DC wallbox (≈€2,000–3,000)" · `maker_box_only` "Only with the maker's wallbox" · `tariff_required` "Needs a specific energy contract" · `software_min` "Needs software ≥ X — check the car" · `battery_min` "Large battery only (≥ X kWh)" · `build_date_from` "Only cars built from DD-MM-YYYY" · `discharge_cap` "Limited discharge allowance (warranty)" · `chademo_legacy` "Old CHAdeMO plug — boxes getting scarce" · `smart_meter_required` · `home_battery_required` "Only with the maker's home battery" · `pilot_only` · `announced_only`.

### 2.3 Model / variant page block "Power out"

- One row per mode (V2L/V2H/V2G): status per launch country (live / pilot / announced / not offered), max kW out, route (AC/DC/CHAdeMO), required box (name + price band), contract, caveats, sources with dates.
- **Used-car checklist** (Simple mode): "Ask the seller: software version, battery size (net kWh), build date; check the maker's eligibility page." Deep link to the maker's eligibility page.
- Nerd mode: protocol (ISO 15118-2 extension / -20 / CHAdeMO / proprietary), each Fact with source, confidence, retrieval date.

### 2.4 /learn pages (6 languages)

- `/learn/bidirectional-charging`: V2L vs V2H vs V2G in one picture; AC vs DC route and why the box price differs; what the country rules mean (DE grid fees from 2026, FR offers, UK tariffs); battery wear (state the maker's warranty terms, no speculation).
- Section in `/learn/charging-2026` → "Buying a wallbox from 2027": new wallboxes must speak ISO 15118-20; existing ones are fine; it doesn't make them bidirectional; your car must also support it.
- `/learn/plugs` (US focus first): CCS1 vs NACS/J3400, adapters, which Supercharger sites serve non-Teslas, model-year switch.

## 3. Data model (coordinator lane: packages/schema)

### 3.1 Taxonomies (data/taxonomy/, rows not code)

- `bidi_modes`: v2l, v2h, v2g, v2b (+ explainer per language).
- `bidi_routes`: ac_onboard, dc_offboard, chademo_dc, proprietary.
- `bidi_protocols`: iso15118_20, iso15118_2_ext, chademo, proprietary, not_disclosed.
- `bidi_caveats`: list in §2.2, with label + tooltip per language, optional `param` (number/date/version).
- `bidi_status`: live, pilot, announced, hardware_ready_not_enabled, not_offered, not_disclosed.
- `connector_types`: type1_j1772, type2, ccs1, ccs2, nacs_j3400, chademo, tesla_eu_legacy, gbt_ac, gbt_dc.
- `bidi_equipment`: approved boxes (id, maker, AC/DC, max kW, price band €, markets, compatible platforms, source). New boxes are new rows.

### 3.2 Entities

- `BidiCapability` (Fact-backed, many per variant, inherited from Platform when shared):
  `variant_or_platform_id, mode, route, protocol, max_kw_out, min_software, min_battery_net_kwh, build_date_from, model_years[], equipment_ids[], tariff_required, caveats[{id, param}], market_status{country: status}, sources[]`.
- `ChargingPort` (per variant **per market and model year**): `ac_inlet, dc_inlet (connector_types), native_or_adapter, supercharger_access (native | adapter | magic_dock | none | not_disclosed), adapters_included[]`.
- Variant field `iso15118_20_support`: yes / no / not_disclosed (Fact). Default `not_disclosed`; never inferred from model year.
- Rule: a used car's eligibility is shown as **conditions**, never a plain ✓, whenever `min_software`, `min_battery_net_kwh` or `build_date_from` is set.

### 3.3 Sources (WS1: data/sources.yaml)

Primary = maker eligibility pages and press (VW, BMW, Renault/Mobilize, Mercedes, Nissan, Kia/Hyundai, Ford, GM Energy, Tesla). Fallbacks = The Mobility House list, energy-company pages (E.ON, Octopus, Elli, Vattenfall), electrive. Two sources per headline field (mode + status per country). Re-check every release: this changes monthly; facts older than 90 days get a "may be out of date" flag.

## 4. Phasing (scope guard)

- **Core phase 1:** taxonomies + schema fields; "Buying a wallbox from 2027" section in `/learn/charging-2026`; `ChargingPort` for EU (CCS2/Type 2/CHAdeMO) on the top-40 used models.
- **Core phase 2:** BidiCapability seed for top-40 used models + all 2025–26 models that offer it; Explore filters + badges; model-page block; `/learn/bidirectional-charging`.
- **Next (phase 4, US/AU):** US `ChargingPort` per model year, Supercharger filter, `/learn/plugs`, US V2H rows (Ford, GM, Kia, Tesla, Volvo/Polestar).
- **Later/parked:** our own V2G earnings calculator; tariff comparison; GB/T.

## 5. Acceptance

- Five-person normie test: people can say, for a used VW ID.3 58 kWh vs ID.4 77 kWh, which one can power a house in Germany and what extra box it needs.
- No V2G/V2H claim without a source dated within 90 days, or it shows "may be out of date".
- Filters respect the selected country; switching country changes results.
