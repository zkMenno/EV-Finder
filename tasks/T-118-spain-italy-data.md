# T-118 Spain and Italy: country config, finance defaults, links, prices
Role: builder   Lane: WS3 (+ WS1 for price data): config/countries/, data/taxonomy/finance_profiles.yaml, data/manual/, templates   Wave: launch fixes (A-35)
Status: review (WS3 builder agent, 2026-11-17; PR pending #71)

## Goal
Spain and Italy have everything the other launch countries have (Decision 066).

## Acceptance criteria
- [x] `config/countries/es.yaml` and `it.yaml`: euro, locale, default language es / it
- [x] Finance defaults with a sourced typical APR and the CCD2 warning in Spanish and Italian
- [x] Marketplace search link templates (link-outs only), checked like T-041
- [ ] Used price bands: price indices or samples where robots and terms allow (Decision 060), otherwise the Decision 064 estimate; new prices from T-112 (partial: 10 IT maker prices, 0 ES; the estimate needs the used_price_params change below)
- [ ] Verify skill run for the lane; evidence pack in the PR; `Verified:` line on every commit
- [ ] Fresh review (REVIEW.md from origin/main) passes; `## Review` line marks the A-35 finding(s) fixed

## Inputs
Decision 066, 060, 064

## Out of scope
Anything not on docs/spec/launch-scope.md.

## Handoff notes
WS3 builder agent, 2026-11-17.

**Done**
- `config/countries/es.yaml` (languages [es]) and `it.yaml` ([it]). Currency and locale are not
  country-file keys (the loaders reject unknown keys): they live in apps/web/src/config/countries.ts
  (`currency: "EUR"`, name) and format.ts (language locale), so T-119 adds the es/it entries there.
  The pipeline side is euro already (ECB rows, IT prices in EUR). Link-outs, all `verified: false`,
  evidence in the file comments, tap list in workstreams/WS3/T-041-checklist.md:
  ES Wallapop (`/coches-segunda-mano/{make}-{model}`, indexed) + AutoScout24.es (`/lst/`, same
  platform as the indexed .it/.nl); IT AutoScout24.it (`/lst/`, indexed) + Subito (free-text `q`
  search, weak evidence: guess). coches.net left out: it needs `model_3`-style slugs (overrides).
  No marketplace page was fetched. Charging links: Electromaps, ABRP, Chargemap, Chargeprice (spec URLs).
- Finance (data/taxonomy/finance_profiles.yaml): ECB MIR APRC, consumer loans excl. revolving,
  period 2026-09 (provisional), read 2026-11-17 from data-api.ecb.europa.eu:
  ES `MIR.M.ES.B.A2B.A.C.A.2250.EUR.N` = 7.54 (Aug 8.01); IT `MIR.M.IT...` = 10.78 (Aug 10.78).
  Licence: ECB website terms allow free use with the ECB cited
  (https://www.ecb.europa.eu/services/disclaimer/html/index.en.html).
- CCD2 warning (data/taxonomy/README.md): official directive texts, Art. 8(1).
  ES «Atención: tomar dinero prestado cuesta dinero» (DOUE via boe.es);
  IT «Attenzione! Prendere in prestito denaro costa denaro» (GUUE copy on dirittobancario.it;
  EUR-Lex returned nothing to this agent). Directive wording, not each country's transposition (Q-072).
- 10 Italian list prices (data/manual/new-prices/t118-it-maker-list-prices.yaml): Volkswagen
  Italia MY25 price list (ID.3 ×3, ID.4 ×3, ID.7 ×2) and Renault Italia R5 list of 05/11/2026 (×2).
  Value = "chiavi in mano" (incl. 22 % IVA + ~€820–835 messa su strada); the IVA-exclusive figure is
  in each quote. Mostly `low`: current/MY25 lists, not launch prices, and several of our seed rows
  disagree with the maker on kWh or kW (see notes per row).

**Not done / blocked**
- Spain list prices: 0. Spanish maker sites (checked Renault ES) show "desde" prices that include
  financing discounts and the CAE bonus, not a list price; Tesla prices load by script; no Spanish
  maker price-list PDFs found. Third-party price databases are off limits.
- Italy beyond VW/Renault: Tesla is script-only; Skoda, Fiat, Kia found only via third parties.

**Cross-lane changes (flagged for WS2 / WS1)**
- apps/web/scripts/listings.mjs: `PENDING_COUNTRIES = ["es", "it"]` so the new files don't break
  the "unknown country files" guard; validated, not served. T-119 moves es/it into COUNTRIES.
- apps/web/scripts/finance.mjs: COUNTRY_CODES += ES, IT; finance.generated.json regenerated.
- pipeline/tests/test_t034_climate.py: GeoNames reads config/countries, so ES/IT towns now ship
  (Madrid in the fixture). Next refresh fetches ES/IT GeoNames + Meteostat (WS1).
- WS2 (T-117): add `loan.warning` to es.json / it.json with the wording above.

**For WS0 / WS1**
- Depends on PR #71 (Country enum ES/IT): until it merges, `ev manual check` and
  test_manual.py reject country IT, so CI is red on the price commit only.
- The Decision 064 estimate for ES/IT needs `used_price_params.yaml` (gate file, own PR):
  countries + ES/IT, currency EUR, vat ES 0.21 / IT 0.22, cross_country_to + ES, IT. Then every
  variant with an NL list price gets an ES/IT estimate (low confidence).
- Found while checking: manual `price_new` facts carry no record year
  (`attach_manual_facts` passes year None), and `used_price.list_prices` skips facts without a
  year. So manual list prices (T-112's and these) never reach the estimate. Needs a WS1 fix.

## Review
<!-- Reviewer: name, date, head SHA, REVIEW.md items + verdicts; mark A-35 B5 fixed. -->
