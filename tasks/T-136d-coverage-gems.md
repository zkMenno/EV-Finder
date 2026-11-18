# T-136d Coverage gems on top of #129 (EU match 98.5 % → 99.0 %)
Role: builder   Lane: data/seed (WS3, by Menno's request to WS1), pipeline/ev_pipeline/match   Wave: launch (R-41 stretch, Decision 048)
Status: review (WS1 7th, 2026-11-18)

## Goal
Add the EU-sold models #129 still misses (SEAT Mii, the small makes, gems) and the matcher fix that lets a SEAT make coexist with KBA/EEA "SEAT BORN" → Cupra Born. Stacked on #129; replaces #138.

## Acceptance criteria
- [x] Only models whose EEA names #129 does not place yet (checked through the matcher before adding)
- [x] Every new generation cites its EEA registrations by year (CC BY 4.0, counts only), `uncertain: true`
- [x] validate_seed.py OK; pytest green; EU model-level match measured: 98.98 %
- [x] Tests: every new model and #129's people carriers placed from real EEA names; hybrids / cargo vans not placed; SEAT BORN still → Cupra

## Handoff notes
- Added: SEAT Mii electric (+ EEA/KBA "SEAT (CUPRA) BORN / TAVASCAN" → Cupra), DS N°8, Maxus Euniq 5/6 + Mifa 9, Dongfeng Box, Suzuki e Vitara, Lucid Air / Gravity, Bluecar Bluesummer, Hongqi EHS7, Mia, e.GO Life, Cadillac Lyriq, Maserati Grecale / GranTurismo Folgore, Skywell BE11, Yudo 3, Elaris Pio, Deepal S05 / S07, VinFast VF8 / VF6, Jaecoo 5 EV, JAC e-JS4, Rolls-Royce Spectre, Think City, Moke, Togg T10X, Aion V, Mobilize Limo, Exlantix ET (32 models, 23 new makes). Make aliases: KG Mobility, DS Automobiles, VEPB.
- Matcher (WS1 lane): `find_record_model` is the one make/model lookup (match_records, corroboration, test helpers); a source alias written with its make ("SEAT BORN") also applies when that make is in the seed.
- Years are EEA first-registration years, not model years; segment/body are judgement calls (T-136 method).
- Still out: Leapmotor T03 (20k, OpenEV China-only files: needs the OpenEV market filter WS3 asked WS1 for), hybrids filed as electric, "TESLA MODEL", Spanish "NUEVO ..." names.
- Release diff: new generations without variants add no rows; WS1 re-checks release 3's diff after #129 + #144 merge.
