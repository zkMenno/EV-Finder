# T-043 Price modes: outright, loan and lease per month
Role: WS3 (finance_profiles) + WS2 (UI)   Lane: data/taxonomy, apps/web   Wave: 7
Status: merged (PR #1); fresh review via QA A-35; earlier note: WS2 UI part; WS0/WS3 parts done by the other builder

## Goal
Let every price switch between buy outright, loan per month and lease per month (Decision 017).

## Acceptance criteria
- [ ] WS0: `FinanceProfile` in packages/schema (country, product, typical_apr, default_term_months, default_deposit_pct, source, retrieved_at)
- [ ] WS3: `data/taxonomy/finance_profiles.yaml` for NL, DE, FR, BE, UK with cited typical used-car loan rates
- [x] WS2: price-mode control on Explore, model pages and Compare; remembered + in the URL
- [x] WS2: calculator shows monthly amount, total over the term, assumptions, "estimate, not an offer" and the CCD2 warning in the page language (DE/FR fall back to EN, Q-072)
- [x] No lender names, no finance links in the UK; lease mode shows a labelled link only (no figures) until partner feeds exist
- [ ] Glossary terms: loan, lease, private lease, balloon / PCP, residual value, total cost over the term (EN + NL)

## Inputs
docs/spec/master-spec-v2.md §8 "Ways to pay", Decision 017, research/R-03.

## Out of scope
Lease price feeds, finance affiliate links, credit checks.

## Handoff notes
**2026-11-15, web builder (overnight, proto/overnight-1), WS2 part.**

What was done:
- Config: `apps/web/scripts/finance.mjs` parses `data/taxonomy/finance_profiles.yaml` at build time (server only, no YAML at runtime) into `src/config/finance.generated.json`, keyed by country; it refuses an APR without an https source and a retrieval date. Build/dev run it; a unit test fails when the JSON is stale. The Docker context has no `data/taxonomy`, so the committed JSON is used there. `src/lib/finance-profiles.ts` (`financeProfile(code)`) is the only reader.
- Maths (`src/lib/finance.ts`, pure): r = (1 + APR)^(1/12) − 1, annuity P × r / (1 − (1 + r)^−n), totals (`totalOverTerm` = deposit + instalments, `costOfCredit`). Inputs: user value → sourced profile value → labelled default (term 48 months, deposit 0 %, both "assumption, change it"). **No APR default:** with `typical_apr: null` (NL today) the field is empty and asks for a rate, and no monthly figure is shown anywhere until the user enters one.
- State: `ExploreState.pay` (`buy` | `loan` | `lease`, URL `pay`, omitted for buy, tested), remembered in localStorage (`ev-finder:pay:v1`; the URL wins). The user's loan inputs are browser-only (`ev-finder:loan:v1`), shared by Explore, variant, generation and compare pages.
- UI (`src/components/PriceMode.tsx`): `PayModeToggle`, `LoanBox` (inputs with their origin label, monthly / total over the term / cost of the loan, assumptions line, CCD2 warning + "estimate, not an offer", Nerd: formula, monthly rate and the APR source with series id, period, date, scope note and review flag), `LeaseNotice` (labelled placeholder, no figures; UK: "not available in the UK"), `PricePanel` (variant + generation + compare pages; one car = calculator, several = monthly per car). Explore's price column and cards follow the mode (`≈ €x/month` with an "estimate" note; hover still shows the price's source). Model overview pages have no prices, so the control sits on generation and variant pages.
- Glossary ⓘ: loan, lease, private-lease, balloon-pcp, residual-value, total-cost-over-term (from the release; missing ids render no ⓘ).
- i18n: EN + NL complete (`pay.*`, `loan.*`, `lease.*`, `finance.*`); DE/FR have the labels, the CCD2 warning falls back to EN (Q-072).
- Tests: `src/lib/finance.test.ts` (maths, origins, no-APR case, storage, UK rule, YAML drift + source rule), state tests, `e2e/price-modes.spec.ts` (NL asks for a rate, CCD2 text, URL + remembered mode, DE sourced APR + Nerd source, lease placeholder + UK, compare per car).

Left: lease partner feeds (Next); legal wording per country (Q-072, R-03); UK finance links stay off until the FCA question is answered.

## Review
- Reviewed by QA, 2026-11-17 (main @ d086d49, REVIEW.md draft R0–R3 + triggered D items): changes needed — NL hero has no monthly estimate (A-35 S6); the Buy/Loan/Lease toggle on catalogue pages is a parked mode (S4).
