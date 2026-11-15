# T-056 Used price layer0
Role: WS1 + WS5   Lane: pipeline, config   Wave: proposed by overnight 1
Status: review (WS1, 2026-11-15)

## Goal
Used prices: ingest the free published price indices (layer 0: Autotrader RPI, AutoScout24 AGPI, Indicata) where terms allow, so PriceBand can show something.

## Acceptance criteria
- [x] Terms checked per index; only allowed ones ingested
- [x] PriceBand shows a band only with ≥ 5 samples, else 'not enough data'
- [x] Tests cover it (fixtures, no live network calls)

## Inputs
MORNING.md, data/review/coverage-gaps.md, QUESTIONS.md, audits/.

## Out of scope
Anything not named above.

## Handoff notes
- Done (WS1, 2026-11-15), in the T-081 PR: terms checked in research/R-40 §1. AGPI, Autotrader RPI and Indicata publish without a licence → not ingested, internal sanity checks only; public trend lines need permission (WS5). AUTO1 index has no BEV split. The ≥5 samples rule is in `used_price_params.yaml` (`min_samples`) and tested.

## Review
