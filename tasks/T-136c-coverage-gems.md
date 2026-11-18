# T-136c Consolidated missing-model seed + coverage gems (EU match 86.7 % → 99.2 %)
Role: builder   Lane: data/seed (WS3, by Menno's request to WS1), pipeline/ev_pipeline/match   Wave: launch (R-41 task 2 + stretch)
Status: review (WS1 7th, 2026-11-18)

## Goal
One seed branch instead of two overlapping WS3 branches, plus the remaining EU-sold models ("gems") and the people carriers Menno put in scope, so ≥ 95 % of EU BEV registrations land on a seed model.

## Acceptance criteria
- [x] Builds on WS3's t-136-extra-models-2nd-chat (182 models, 97.7 %) and carries #129's three vans (EQV, ë-Berlingo, e-Rifter) unchanged
- [x] Van scope (Menno, 2026-11-18): people-carrier M1 versions; cargo vans stay out
- [x] Every new generation cites its EEA registrations by year (CC BY 4.0, counts only), `uncertain: true`
- [x] validate_seed.py OK; pytest green; EU model-level match measured: 99.18 %
- [x] Tests: every new model placed from a real EEA name; hybrids / cargo vans not placed

## Handoff notes
- Added (WS1): 20 people carriers (EQV, eVito Tourer, EQT, ë-Berlingo, ë-SpaceTourer, e-Rifter, e-Traveller, Combo-e Life, Zafira-e Life, Proace Verso / City Verso, e-Doblò, e-Ulysse, e-NV200 Evalia, Kangoo E-Tech, E-Tourneo Custom / Courier, Kia PV5, Townstar EV) and gems: SEAT Mii electric, Maxus Euniq 5/6 + Mifa 9, Dongfeng Box, Suzuki e Vitara, Lucid Air / Gravity, DS N°8, Bluecar Bluesummer, Hongqi EHS7, Mia, e.GO Life, Cadillac Lyriq, Maserati Grecale / GranTurismo Folgore, Skywell BE11, Yudo 3, Elaris Pio, Deepal S05/S07, VinFast VF8/VF6, Jaecoo 5 EV, JAC e-JS4, Rolls-Royce Spectre, Think City, Moke, Togg T10X, Aion V, Mobilize Limo, Exlantix ET. Make aliases: KG Mobility, DS Automobiles, VEPB, SEAT → Cupra for EEA.
- Matcher (WS1 lane): `find_record_model` = the one make/model lookup; a source alias written with its make ("SEAT BORN") now also applies when that make is itself in the seed (SEAT for the Mii). Test helpers in test_registrations/test_seed_t051 call it instead of copying the logic.
- Years are EEA first-registration years, not model years; segment/body are judgement calls like T-136's.
- Not placed on purpose: hybrids filed as electric (Prius, Auris, CT200h, RX450h), cargo vans, "TESLA MODEL" (no model name), EQE/EQS SUV (EEA doesn't name them apart: WS3 note).
- Remaining 0.8 %: misspellings and one-offs, see `model_level.biggest_unmatched` from `ev variants propose` (#127).
