<!-- Spec tab "Variant finder" (rev 1), written 2026-11-15 in the repo first at Menno's request. WS0: add it as a tab in the claude.ai spec doc. -->

# Variant finder: tell variants apart, and spot the right one in an ad

Status: accepted 15 Nov 2026 (Menno), Decision 019. Lanes: WS1 data + matching, WS2 UI, WS3 content, UX design. Legend: 🟢 verified · 🟡 reasoned · 🔴 unsure, check before building.

**One line:** keep one card per variant, but show variants grouped by generation with only their differences highlighted. Add an "how to spot it in an ad" box and a finder that turns what an ad says into the matching variant.

## 1. The problem

- EV Database shows every variant as its own card. That is correct, but you can't see what actually differs between, say, two Ioniq 5 77 kWh cars from different years. 🟢 (Menno's own use)
- Used ads rarely give the official variant name. They give a year, kW, kWh, a trim name (which differs per country) and photos. 🟢
- The costly traps are silent mid-cycle changes: bigger battery, faster charger, heat pump, a new pack chemistry, all without a new name. 🟢 (common pattern, e.g. model-year updates)

## 2. Features and tags

| # | Feature | What the visitor gets | Tag |
|---|---|---|---|
| 1 | **Differences only** toggle | On generation pages and in Compare, hide every spec all variants share; highlight what differs, with plain-language deltas ("+13 kWh, about +70 km winter range") | Core (extends the existing variants table, §5) |
| 2 | **Variant change timeline** | Strip on the generation page: what changed when ("Heat pump standard from 03/2021", "11 kW charger from MY2022") | Core (reuses generation change markers, §12) |
| 3 | **Spot it in an ad** box | Per variant: the 3–5 clues that tell it apart from its look-alikes (see §3) | Core for the 40 hand-checked models; Next for the rest |
| 4 | **"Which one is it?" finder** | Enter what the ad says (year, kW, kWh, trim, country) → one match, or "A or B: check the charger rating in the ad" | Next |
| 5 | **Plate lookup (NL first)** | Enter a Dutch plate → exact variant from RDW open data (type approval + uitvoering) | Next, 🟡 licence and privacy check first (WS1) |
| 6 | **Paste a listing link** | Paste an AutoScout24 / Leboncoin / mobile.de link → we fill the finder | Later, 🔴 marketplace terms: only through a partner deal or the visitor's own pasted text |
| 7 | **Used-buyer notes** | Per variant: known weak points, battery warranty left by year, recalls | Next (already in spec §5 "Next" row; linked here) |

## 3. What a clue is

A clue is a fact a buyer can read in an ad, on the registration papers or on the car itself.

| Clue type | Example | Where the buyer finds it |
|---|---|---|
| Build or first-registration date range | 06/2021–02/2022 | Ad, registration papers |
| Power in kW | 160 kW | Registration papers (FR carte grise P.2, NL kenteken data), most ads |
| Battery (net/gross kWh) | 77.4 kWh net | Ad, often wrong or missing: low weight 🟡 |
| Trim name per market | "Lounge" (NL) = "Techno" (FR)? | Ad title |
| Type-approval / version code | e-number, variant/version codes | FR carte grise D.2, NL RDW data 🟡 |
| VIN position | A character in the VIN that encodes battery/motor | VIN in ad or on the car 🔴 per make, research needed |
| Visible feature | Wheel size, charge-port flap, badges, heat-pump pipework | Photos |
| Onboard charger | 7.4 vs 11 kW AC | Ad, spec sticker |

Each clue has a **strength** (decisive / strong / weak) and lists which look-alike variants it rules out. Clues are Facts like any other: source, date, confidence.

## 4. Data model (future-proof: one table, two uses)

- New entity **Variant clue**: `variant_id`, `clue_type` (from a config list, so new types need no code), `market` (or global), `value` or range, `strength`, `rules_out[]` (variant ids), source/date/confidence.
- New entity **Look-alike group**: variants that buyers confuse (same generation, same badge, or same marketing name across markets). Built automatically from overlapping specs, editable by staff.
- **Same table feeds listing matching (§8).** The rules that tell a human "this is the 77 kWh RWD" are the rules that match a listing to a variant. Build once, use twice. When listing feeds land, matches that fail go to Listing QA and fixes improve the clues.
- Diff view (feature 1) needs no new data: computed from published variants at build time.

## 5. Rules

- Never claim certainty we don't have: the finder answers "match", "two candidates + which clue settles it", or "can't tell, ask the seller for X".
- "Ask the seller" lines are templated per language (six languages) so buyers can copy them.
- Trim names are per market and per language; never translate a trim name, map it.
- Tooltips on every clue type ("What is the type-approval code?").

## 6. Open questions (agent-owned, not for Menno)

- WS1: RDW licence and whether plate → variant counts as personal data under GDPR 🟡.
- WS1/WS3: which makes encode battery in the VIN; start with the 40 hand-checked models 🔴.
- UX: diff highlight that works colour-blind safe (shape or weight, not only colour).
