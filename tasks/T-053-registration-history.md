# T-053 Registration history
Role: WS1   Lane: pipeline/ev_pipeline/sources/{kba_fz10,eea}   Wave: proposed by overnight 1
Status: merged (PR #1); fresh review via QA A-35; earlier note: pipeline builder, 2026-11-15

## Goal
Fetch KBA FZ10 back to 2012 and EEA back to 2010 so older generations get DE/FR/BE counts (coverage-gaps finding 9).

## Acceptance criteria
- [ ] Per-year new registrations for DE/FR/BE in registrations[]
- [ ] Fetch stays within fair-use limits; snapshots via the refresh loop
- [ ] Tests cover it (fixtures, no live network calls)

## Inputs
MORNING.md, data/review/coverage-gaps.md, QUESTIONS.md, audits/.

## Out of scope
Anything not named above.

## Handoff notes
- Scope set by the coordinator: 2018 onward (Q-074 "used" = first registered 2018–2024), not 2012/2010.
- **KBA** (`sources/kba_fz10`): newest file + every December since `HISTORY_FROM = 2018`, 1 s apart; remote names `.xlsx` or `_xlsx.xlsx` (2018–2020), saved as `fz10_<y>_12.xlsx`. Old layout ("mit Elektroantrieb", licence in "Inhaltsverzeichnis", bare "SONSTIGE" make) handled; "/", ".", "X" cells = no count. 2018 file has no licence line → skipped and listed in `_fetch.json` `skipped` (Q-082). No xlrd needed (pre-2018 `.xls` out of range). Live: 898 records, 2019–2026.
- **EEA** (`sources/eea`): `TABLES` = final 2018–2024 + 2025 provisional; 2018/2019 via the all-years `[co2cars]` table pinned to `Status='F'` + `Version_file`. Licence checked per year's SDI record; one query per table, 2 s apart; rows carry `table`. Final years confidence high. Live: 6,329 count records 2018–2025 (+4,906 corroboration).
- Periods: KBA `YYYY-01..12` per file, EEA = year, so `registrations[]` gets one entry per year (matcher unchanged).
- Per-year numbers: `data/SOURCES.md`. Not done: release (coordinator); matching of older Modellreihe / commercial names is the seed/match lane's.

## Review
