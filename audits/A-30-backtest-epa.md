# A-30 Back-test on EPA figures (proxy)

Release 1, generated 2026-11-15T06:58:53+00:00 by `ev_pipeline.backtest.epa` (T-035), run by WS1 on 2026-11-15 on release 1's catalogue and facts plus EPA tests fetched live the same day, with the calibrated consumption parameters (PR for T-035). From the next release on, the same numbers sit in `qa.json` → `backtest_epa`; regenerate with `python -m ev_pipeline.backtest epa-report data/releases/<n>`.

**Calibration note:** the consumption model's wltp-ratio parameters were calibrated on these same EPA figures (before: median error 22.8 %, model 21.8 % low; after: 6.1 %, +0.3 %). The consumption numbers below are therefore in-sample: they show the two rungs now agree, not out-of-sample accuracy.

EPA label values (fueleconomy.gov, public domain): US cycles, 5-cycle adjusted. A check that WLTP-based estimates land near an independent measurement, not the launch gate (El Prix / Nyland tests, spec §5).

## Real range vs EPA adjusted range

- **Median absolute error:** 7.59 % over 60 comparisons (60 variants); mean signed -1.02 % (model reads low).
- Status against a 10 % proxy gate: **pass**.
- Top-40 used models with data: 21 of 40.

| Body | n | median abs % | mean signed % |
|---|---:|---:|---:|
| crossover | 12 | 9.04 | -6.82 |
| hatchback | 5 | 8.46 | +10.62 |
| sedan | 22 | 5.39 | +3.8 |
| suv | 21 | 7.81 | -5.51 |

| Top-40 model | n | median abs % | mean signed % |
|---|---:|---:|---:|
| tesla-model-3 | 4 | 3.0 | -2.8 |
| tesla-model-y | 6 | 12.23 | -4.86 |
| kia-niro-ev | 1 | 7.37 | -7.37 |
| hyundai-kona-electric | 2 | 16.0 | -16.0 |
| audi-q4-e-tron | 2 | 7.55 | -7.55 |
| volvo-xc40-recharge | 2 | 5.88 | -5.88 |
| volkswagen-id4 | 1 | 6.26 | -6.26 |
| nissan-leaf | 1 | 4.3 | -4.3 |
| audi-e-tron | 3 | 7.27 | +0.76 |
| polestar-2 | 2 | 10.84 | +10.84 |
| bmw-i4 | 4 | 4.42 | +4.42 |
| mini-cooper-se | 2 | 23.0 | +23.0 |
| volvo-ex30 | 1 | 9.63 | -9.63 |
| kia-ev6 | 3 | 24.0 | -4.93 |
| hyundai-ioniq-5 | 3 | 11.11 | -15.26 |
| jaguar-i-pace | 1 | 2.66 | -2.66 |
| ford-mustang-mach-e | 1 | 10.24 | -10.24 |
| mercedes-eqb | 2 | 2.38 | -2.38 |
| porsche-taycan | 4 | 3.91 | +4.52 |
| volkswagen-e-golf | 1 | 5.37 | -5.37 |
| bmw-ix | 3 | 4.08 | -3.61 |

No data: volkswagen-id3, skoda-enyaq, peugeot-e-208, renault-zoe, mg-mg4, peugeot-e-2008, cupra-born, opel-corsa-e, mercedes-eqa, mg-zs-ev, bmw-ix1, bmw-ix3, fiat-500e, opel-mokka, bmw-i3, renault-megane-e-tech, citroen-e-c4, ford-explorer, mercedes-eqc.

Worst cases:

- mini-cooper-se-j01-se (range): +37.55 %
- hyundai-ioniq-5-gen1-58kwh-rwd (range): -35.42 %
- mercedes-cla-gen1-base (range): +27.87 %
- kia-ev6-gen1-58kwh-rwd (range): -26.59 %
- hyundai-kona-electric-sx2-standard-range (range): -24.2 %

## Consumption (wltp-ratio rung) vs EPA city/highway

- **Median absolute error:** 6.14 % over 100 comparisons (50 variants); mean signed +0.34 % (model reads high).
- Status against a 10 % proxy gate: **pass**.
- Top-40 used models with data: 18 of 40.

| Body | n | median abs % | mean signed % |
|---|---:|---:|---:|
| crossover | 22 | 4.79 | -1.84 |
| hatchback | 10 | 10.04 | +9.94 |
| sedan | 38 | 8.6 | -2.71 |
| suv | 30 | 5.03 | +2.61 |

| Top-40 model | n | median abs % | mean signed % |
|---|---:|---:|---:|
| tesla-model-3 | 6 | 4.12 | +3.65 |
| tesla-model-y | 8 | 4.69 | +7.88 |
| kia-niro-ev | 2 | 4.96 | +4.96 |
| hyundai-kona-electric | 4 | 5.15 | +2.32 |
| audi-q4-e-tron | 4 | 4.16 | +4.04 |
| volkswagen-id4 | 2 | 6.0 | +6.0 |
| nissan-leaf | 2 | 27.37 | +27.37 |
| audi-e-tron | 2 | 8.38 | +8.38 |
| bmw-i4 | 8 | 3.6 | -4.01 |
| mini-cooper-se | 4 | 6.83 | -7.12 |
| kia-ev6 | 6 | 10.92 | -3.09 |
| hyundai-ioniq-5 | 6 | 4.67 | +0.81 |
| jaguar-i-pace | 2 | 0.73 | -0.23 |
| ford-mustang-mach-e | 2 | 4.49 | -4.49 |
| mercedes-eqb | 4 | 7.1 | -6.82 |
| porsche-taycan | 8 | 10.87 | -12.82 |
| volkswagen-e-golf | 2 | 5.18 | +5.18 |
| bmw-ix | 6 | 7.26 | -4.91 |

No data: volkswagen-id3, skoda-enyaq, volvo-xc40-recharge, polestar-2, peugeot-e-208, renault-zoe, mg-mg4, volvo-ex30, peugeot-e-2008, cupra-born, opel-corsa-e, mercedes-eqa, mg-zs-ev, bmw-ix1, bmw-ix3, fiat-500e, opel-mokka, bmw-i3, renault-megane-e-tech, citroen-e-c4, ford-explorer, mercedes-eqc.

Worst cases:

- smart-eq-fortwo-453-eq (town): +40.39 %
- nissan-leaf-ze1-40kwh (town): +34.18 %
- smart-eq-fortwo-453-eq (rural): +22.45 %
- tesla-model-y-juniper-long-range-rwd (town): +21.06 %
- tesla-model-s-facelift-75d (rural): +20.95 %

## What this does not show

- Winter or motorway error: EPA cycles are mild-weather lab cycles (adjusted).
- EU-market differences (wheels, software, packs) between matched US and EU cars.
- The launch gate needs licence-cleared road tests (Q-059): this is a proxy only.

## Follow-up: EPA records attached to the wrong variant (WS1, 2026-11-15)

The worst range cases are matching errors, not model errors: US "Long Range" EPA rows sit on
the EU 58 kWh Ioniq 5 and EV6; the US 2024 "Cooper SE" (still the old F56) sits on the J01
Cooper SE; the US Kona "Standard Range" (99 kW) sits on an EU SX2 row. A trial power gate
(EPA motor kW vs variant power, the RDW rule of max(2 %, 3 kW)) was tested on staging and
rejected: US motor ratings differ from EU system power, so it dropped correct Tesla, Polestar
and Taycan matches and created new wrong ones. Next step (WS1, not started): an EPA-specific
rule that rules out variants whose "standard/long range" token or battery class contradicts
the EPA model text, plus model-year → generation checks for US model years that lag the EU
generation (Mini). Until then these few rows inflate the range error; the median is robust
to them.

**Update (same day, PR `fix/epa-range-class`):** a range-class rule now keeps EPA rows that
say "Long Range" / "Standard Range" off the other pack class (split at the biggest step in the
generation's pack sizes, only when that step is ≥ 10 %). Tried on today's staging: EV6 58 kWh
loses the two Long Range rows (they move to the 77 kWh car), Ioniq 5 58 kWh loses its Long
Range row, Model Y RWD and Model S 75D gain their Standard Range rows; nothing else moves.
Mini J01 (US model year lag) and the Kona SX2 row (its 36.5 kWh battery looks wrong in the
release itself) are still open.
