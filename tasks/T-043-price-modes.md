# T-043 Price modes: outright, loan and lease per month
Role: WS3 (finance_profiles) + WS2 (UI)   Lane: data/taxonomy, apps/web   Wave: 7
Status: todo

## Goal
Let every price switch between buy outright, loan per month and lease per month (Decision 017).

## Acceptance criteria
- [ ] WS0: `FinanceProfile` in packages/schema (country, product, typical_apr, default_term_months, default_deposit_pct, source, retrieved_at)
- [ ] WS3: `data/taxonomy/finance_profiles.yaml` for NL, DE, FR, BE, UK with cited typical used-car loan rates
- [ ] WS2: price-mode control on Explore, model pages and Compare; remembered + in the URL
- [ ] WS2: calculator shows monthly amount, total over the term, assumptions, "estimate, not an offer" and the CCD2 warning in the page language
- [ ] No lender names, no finance links in the UK; lease mode shows a labelled link only (no figures) until partner feeds exist
- [ ] Glossary terms: loan, lease, private lease, balloon / PCP, residual value, total cost over the term (EN + NL)

## Inputs
docs/spec/master-spec-v2.md §8 "Ways to pay", Decision 017, research/R-03.

## Out of scope
Lease price feeds, finance affiliate links, credit checks.

## Handoff notes

## Review
