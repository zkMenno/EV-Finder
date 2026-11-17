# T-036 Trip fit quick range check (Core 1)
Role: WS2   Lane: apps/web   Wave: 7
Status: merged (PR #1); fresh review via QA A-35; earlier note: builder, 2026-11-15

## Goal
Profile picker + three inputs → "range you truly need" and an Explore column, no map.

## Acceptance criteria
- [ ] Profile picker (five taps) and inputs: longest regular round trip, motorway share, home town
- [ ] Result card: winter km on your mix, summer km, ≈ WLTP equivalent; Simple/Detailed/Nerd
- [ ] Explore column ✓/⚠/✗ + filter "does my trips in winter"; failing cars greyed with reason
- [ ] Stored in the browser only; works with a fixture matrix until T-033 lands

## Inputs
docs/spec/trip-fit.md §3–6 and §8.

## Out of scope
Routes (T-038).

## Handoff notes
- **Flag:** `TRIP_FIT=1` (`src/config/features.ts`, read per request) shows it; off means no trip UI, and a shared `?trip=1` is dropped server-side. `TRIP_FIT=0` is in `.env.example`.
- **Model:** `src/lib/trip-model.ts` (pure, browser-side per Decision 013). Need = km × WLTP battery consumption (usable kWh / WLTP km, else `consumption_kwh_100km`) × Σ road share × matrix multiplier × extras + warm-up per cold start. Have = usable × health × (daily limit − 10% buffer). ✓ margin ≥ 15% and the +15% band still fits; ⚠ 0–15% or band crosses zero; ✗ short (with "short by about N km"); "?" when battery or WLTP figure is missing (filter drops these). "Range you truly need" = (trip + warm-up) / (80% − 10%), shown as winter / summer km on your mix and ≈ WLTP (median body factor).
- **Fixture data (PROVISIONAL):** `src/fixtures/consumption-matrix.sample.json` (3 bodies × 3 road bands × 5 temperature bands + aliases, country motorway factors, extras, health, buffer) and `src/fixtures/towns.sample.json` (20 towns, Jan/Jul means typed from memory). Every number is shown through `<Num>` with an estimate provenance, rung "fixture matrix". Q-055 lists the defaults. When T-033 lands, swap `MATRIX` for the release matrix (same shape, or adapt `ConsumptionMatrix`).
- **UI:** `src/components/trip/TripModule.tsx` is loaded with `import()` only when the user opens the panel or has a saved trip, so it isn't in the Explore first-load JS. Panel: five profile questions (one tap each, all optional), round trip km, motorway share slider (defaults from driving profile), home town select. Result card Simple / Detailed (winter, summer, WLTP equivalents, temperatures, road-mix bar + text, "what your answers changed") / Nerd (Wh/km per band, P10–P90, rung, factors, JSON). Explore: "Your trips" column (table) and line (cards), failing rows greyed with the reason, chip + checkbox "Only cars that do my trips in winter".
- **Storage/privacy:** answers in localStorage `ev-finder:trip:v1` via `src/lib/trip-settings.ts` (normalises junk, drops anything that isn't a town id; never coordinates). URL/ExploreState only gets `filters.tripFit` (`trip=1`). "Forget my trip" clears it.
- **Also:** Explore rows now carry `wltp_range_km` and `consumption_kwh_100km` (no provenance; ≈0.5 KB gzip). Client components now import `makeT` from `@/i18n/t` so the dictionaries left the client bundle: Explore first-load JS 162.1 → **152.8 KB gzip**. Catalogue 48.1 KB gzip (release 1 rebuilt tonight; was 34.9).
- **Not done (Core 2 / later):** Fit score and ranking, routes, cold-snap toggle (only via "Snow / mountain roads"), preheat toggle, stop time, model-page widget, account sync, DE/FR/ES/IT strings (fall back to EN).
- **Tests:** `src/lib/trip-model.test.ts`, `src/lib/trip-settings.test.ts`, `state.test.ts` (trip flag), `e2e/trip.spec.ts` (flag on: panel → card → column → filter → reload; 360 px; `E2E_TRIP_FIT=0` checks the UI is gone).

## Review
