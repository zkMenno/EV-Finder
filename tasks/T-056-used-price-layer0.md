# T-056 Used price layer0
Role: WS1 + WS5   Lane: pipeline, config   Wave: proposed by overnight 1
Status: todo

## Goal
Used prices: ingest the free published price indices (layer 0: Autotrader RPI, AutoScout24 AGPI, Indicata) where terms allow, so PriceBand can show something.

## Acceptance criteria
- [ ] Terms checked per index; only allowed ones ingested
- [ ] PriceBand shows a band only with ≥ 5 samples, else 'not enough data'
- [ ] Tests cover it (fixtures, no live network calls)

## Inputs
MORNING.md, data/review/coverage-gaps.md, QUESTIONS.md, audits/.

## Out of scope
Anything not named above.

## Handoff notes

## Review
