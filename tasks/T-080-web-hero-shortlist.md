# T-080 Hero: three steps to a top 10 with a top-5 shortlist
Role: WS2   Lane: apps/web   Wave: 10
Status: done (merged by WS2 with Menno's OK, 2026-11-17)

## Goal
The landing page asks country, profile and budget (plus optional refine) and returns a top 10 with the top 5 highlighted (Decision 051).

## Acceptance criteria
- [ ] Step 1 country (5 launch countries, sets currency/prices/links); step 2 the 4-tap profile picker from T-067 (Road-tripper, Daily driver, Runabout, Kerbside layer, where-you-live); step 3 budget in € with a rough "≈ €X/month" loan estimate under it (T-043 loan part only, CCD2 warning)
- [ ] Optional refine, collapsed: body type + seats, min winter range, towing, new/used + build years, brands include/exclude, other Explore filters; same filter components and URL params as Explore
- [ ] Result: top 10 rows = model + variant + build-year range that fits the budget in that country; top 5 visually marked "Your shortlist"; each with a one-line reason, winter range, used price band for those years, See listings link, add-to-Compare
- [ ] Ranking = shortlist rules (Decision 038) in the browser on release fields; hard filters first; unknown factors neutral and shown as "not known yet"; label that the road-tripper rules come from one owner's picks
- [ ] Whole state in the URL (shareable); works at 360 px; Simple/Detailed/Nerd; EN + NL complete
- [ ] Playwright: each of the 4 profiles returns 10 results on the fixture release; changing budget re-ranks without reload

## Inputs
docs/spec/launch-scope.md, Decisions 038, 050, 051, T-067, T-069, T-081, docs/design.

## Out of scope
Accounts, alerts, Trip fit routes, lease figures.

## Handoff notes
- 2026-11-15 WS2: Done on branch `t-080-hero-shortlist`. Decision 055 (hero above Explore at `/{country}/{lang}/`, presets lenient on missing data, rule units).
- Code: `src/lib/shortlist.ts` (picker → profile, scoring, presets, prices, top 10), `src/lib/hero-state.ts` (URL), `src/components/Hero.tsx`, `scripts/shortlist-rules.mjs` → `src/config/shortlist-rules.generated.json` (`--check` + unit test keep it in step with the YAML). Explore filters gain `seats`, `ac`, `ymin`/`ymax`, `make`/`xmake`.
- Scores match `data/editorial/backtest_rules.py` on a fixture (road-tripper). Unknown factors = 0.5 and listed as "not known yet" at Detailed; Nerd shows the factor table.
- Data gaps (release 1): no `used_prices` → most cars show "Price not known yet" (a notice says so); no winter range field → card shows "In winter: not known yet". Both light up from the release, no code change: used bands via `catalogue.usedPrices()` with `age_band_years` → build years; winter field needs adding to `rankHero`/card once named.
- T-067's picker is this one; T-067 still needs the Explore "Suggested" sort + "Why this order".
- JS budget: Explore first load 167.7 KB gzip (was 156.3).

## Review
