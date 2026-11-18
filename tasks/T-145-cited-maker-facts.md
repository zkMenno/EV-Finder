# T-145 Cited facts: Tesla Model 3 gen1 WLTP, Audi e-tron GT 2024 update (Decision 057 split)
Role: builder   Lane: data/seed, data/manual (WS3)   Wave: launch
Status: done (batch: catalogue, 2026-11-18, PR #156 + gate #157)

## Goal
Fill the "not known" WLTP on the Model 3 gen1 Long Range / Performance rows and give the 2024 e-tron GT its own generation with cited S / RS / RS performance variants (WS0 INBOX 2026-11-18 12:40 and 12:50; WS3 lane thread "e-tron GT facelift").

## Acceptance criteria
- [x] tesla-model-3-gen1-long-range and -performance get a cited `wltp_range_km` (type-approval document, Decision 068)
- [x] audi-e-tron-gt split per Decision 057: gen1 2021-2024, facelift 2024-
- [x] S / RS / RS performance seed variants, every value cited from an Audi document
- [x] OpenEV's MY2024-25 e-tron GT files (old pack) can't land on the new generation
- [x] data_qa.sh, ev manual check, ev verify; built rows printed and checked

## Handoff notes
- Tesla: data/manual/specs/t145-cited-maker-facts.yaml. Source = RDW TGK (CC0) for EU type approval e4*2007/46*1293, variant E3D: versions BB* (233 km/h) = Long Range 560 km / 16.0 kWh/100 km; PP* (261 km/h, the seed's Performance top speed) = Performance 530 km / 16.6 kWh. Same figures on extensions 00-12 (2019-01 to 2020-08). Later extensions carry the refreshed cars (LR 580 / 614 / 602 km, Performance 567 / 547 km): in each fact's notes. The seed variants span 2019-2023 in one row; a year split would let the 2021+ figures show (not done).
- e-tron GT: generation `audi-e-tron-gt-facelift` [2024, null]; gen1 now ends 2024 (shared year). Seed variants `audi-e-tron-gt-facelift-s`, `-rs`, `-rs-performance` carry names and years only; figures are `manual` facts in data/manual/specs/t145-cited-maker-facts.yaml (seed `cited:` would be maker-docs, which is blocked). After the #156 review, kept to the figures no other source gives (Decision 068, one-figure scope question sent to WS0): power_kw = Audi's **normal** maximum (S 435 kW audi.co.uk; RS 500 kW data sheet 06.09.2024; RS performance 550 kW audi.com), launch-control figures only in the locators; RS WLTP 599 km and consumption 18.4 (data sheet); RS performance consumption 18.7 (press release 17.09.2024); S consumption 18.0 (audi.com). DC 320 kW cited from Audi too (KilowattApp alone doesn't set dc_peak_kw); battery 97 kWh and AC 11 kW come from KilowattApp and agree with Audi. WLTP for S (571 km, RDW plates) and RS performance (608 km, RDW type approval) comes from RDW, not from Audi. Cross-lane one-liner: `manual` cited_hosts in data/sources.yaml gain audi-mediacenter.com, uploads.audi-mediacenter.com, www.audi.com, www.audi.co.uk.
- New pack `audi-e-tron-gt-105` (NMC, 105 / 97 kWh, cited in the pack notes) and platform `vw-j1` (Audi technology portal names the J1 platform for the e-tron GT concept; uncertain) for the three links; 400 V behaviour and pack voltage not-disclosed.
- source_holds: OpenEV `quattro` / `RS` on the facelift generation (MY2025 files repeat the 85 / 93.4 kWh pack). MY2024 files land on gen1 by battery evidence.
- Built rows (isolated rebuild, today's staging, after the review fixes): S 97 kWh / 571 km (RDW plates) / 435 kW / 320 kW DC / 18.0; RS 97 / 599 km (manual) / 500 kW / 320 / 18.4; RS performance 97 / 608 km (RDW type approval) / 550 kW / 320 / 18.7. gen1 rows unchanged; no OpenEV MY2025 e-tron GT row appears (held).
- Release diff vs main (same staging): 3 rows + 1 generation added; Model 3 LR WLTP filled 560, consumption 15.6 -> 16.0; Performance WLTP filled 530, consumption 15.0 -> 16.6 (+ motorway 19.5 -> 21.6) and its road-tripper+kerbside band shortlist -> consider: 4 blocking, approved in the gate PR. The 15.0 had no type-approval basis (the type approval says 166 Wh/km for every 2019-2020 Performance version).
- Not done: WLTP for S and RS performance (Audi says up to 609 km for the S in its June 2024 release, not read here); the 2025 'E-TRON GT' entry version (RDW variant SBMQ3C*, 494 km in RDW TGK); My manual read of RDW TGK's upper-bound columns (476-483 km) is the worst case; the pipeline's RDW best-case figures (571 / 608 km) ship and are plausible.

## Review
- 2026-11-18 fresh subagent review of 9244eef: R0-R3, D1, D2, D4 PASS WITH NITS (4 should-fix, all fixed in d9c8f81); re-review of d9c8f81: PASS WITH NITS (2 doc nits, fixed with this record). Gate #157 re-review of aa346a4: PASS.
