# T-145 Cited facts: Tesla Model 3 gen1 WLTP, Audi e-tron GT 2024 update (Decision 057 split)
Role: builder   Lane: data/seed, data/manual (WS3)   Wave: launch
Status: review (batch: catalogue, 2026-11-18)

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
- e-tron GT: generation `audi-e-tron-gt-facelift` [2024, null]; gen1 now ends 2024 (shared year). Seed variants `audi-e-tron-gt-facelift-s`, `-rs`, `-rs-performance`, all values under `cited:`. RS from Audi's data sheet 'Audi RS e-tron GT 500 kW' (09/06/2024): 97 / 105 kWh, 630 kW (launch control; 500 kW normal), 11 / 320 kW, 250 km/h, 2.8 s, WLTP 527-599 (599 kept), 21.1-18.4 kWh (18.4 kept), 4997 mm. RS performance from Audi's press release of 17 Sep 2024: 97 / 105 kWh, 680 kW, 320 kW DC, 20.8-18.7 kWh (18.7 kept); no WLTP in it. S: battery 97 kWh net, 500 kW (launch control; 435 kW normal), 11 / 320 kW from Audi UK's S e-tron GT battery-and-powertrain page; consumption 19.7-18.0 (18.0 kept) from audi.com. No WLTP (Audi UK gives 367-374 miles for UK equipment).
- New pack `audi-e-tron-gt-105` (NMC, 105 / 97 kWh, cited in the pack notes) and platform `vw-j1` (uncertain, not read from a maker document) for the three links; 400 V behaviour and pack voltage not-disclosed.
- source_holds: OpenEV `quattro` / `RS` on the facelift generation (MY2025 files repeat the 85 / 93.4 kWh pack). MY2024 files land on gen1 by battery evidence.
- Not done: WLTP for S and RS performance (Audi says up to 609 km for the S in its June 2024 release, not read here); the 2025 'E-TRON GT' entry version (RDW variant SBMQ3C*, 494 km in RDW TGK); RDW TGK WLTP for the facelift (476-483 km, Wh/km 226-245) does not match Audi's data sheets, so not used.

## Review
