# R-05 Data QA: back-tests and release checks

**Answer:** every release runs automatic checks before it can swap in; the two models that produce our own numbers (real-world range and Trip fit consumption) are back-tested against measured tests, and Trip fit only launches when the median error on the top-40 used models is under 10 %. Owner: WS1 (T-035); WS0 reviews the report at each phase gate.

## 1. Release checks (every release, blocking)

| Check | Rule | On failure |
|---|---|---|
| Schema | Every published object validates against `packages/schema` | Release blocked |
| Provenance | Every non-null number has source, date, confidence, licence | Release blocked |
| Licence gate | Only sources with a named licence or written permission (Decision 009) | Facts dropped, listed in report |
| Diff vs previous release | Variant count, field coverage, value changes per field | > 2 % of variants lost, or any headline field change > its tolerance on > 20 variants → review |
| Outliers | Per field, per segment: values outside P1–P99 of the previous release, or physically impossible (usable > gross kWh, WLTP km / usable kWh > 10 km/kWh, DC avg > peak) | Review queue |
| Charging stats | Month-on-month change > 15 % or any drop (Decision 012) | Review queue |
| Coverage | Share of top-40 used models with ≥ 2 agreeing sources per headline field | Report; target 80 % before launch |

## 2. Real-range ratio model (what Explore shows today)

- **Ground truth:** measured mixed-driving tests with conditions: NAF El Prix summer, ADAC, Edmunds (US later), Bjørn Nyland 90 km/h once permitted.
- **Method:** leave-one-out per variant: predict from body × drivetrain × brand ratios without that car's own test, compare with the test.
- **Report:** median absolute % error overall, per body type, per brand, per model year band; the 10 worst cars with reasons.
- **Gate:** median < 10 % before "real range" is shown without an "estimate" label. Above that, the column keeps the estimate badge.

## 3. Trip fit consumption model (T-033)

- **Ground truth:** condition-tagged tests (speed, temperature, wheels) and El Prix routes with known town / motorway / mountain mix.
- **Method:** for each held-out test, run the fallback ladder as if that test didn't exist; compare predicted kWh for the route or speed with measured.
- **Slices:** rung (measured, platform, physics, WLTP ratio), temperature band, heater type, road band.
- **Gate (spec):** median error < 10 % on the top-40 used models before launch; each rung's error sets the width of its P10–P90 band.
- **Regression guard:** a release where any top-40 model's error worsens by > 3 points goes to review.

## 4. Where results live

- `audits/A-NN-backtest-<release>.md` per phase gate (WS0 hands out the number), plus a machine-readable `data/releases/<n>/qa.json`.
- The staff dashboard shows the coverage report and the review queue (spec "Source matrix").

## Open items
- Bjørn Nyland permission (WS5) decides whether 90/120 km/h tests join the ground truth.
- 🔴 Warm-up kWh per cold start and towing/roof-box factors need data before they leave "estimate".
