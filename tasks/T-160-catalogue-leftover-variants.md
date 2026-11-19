# T-160 Catalogue leftovers: MX-30, smart forfour 453, Model X gen1, EV6 63 kWh, then the rest
Role: builder   Lane: data/seed, data/manual (WS3)   Wave: launch
Status: todo

## Goal
The biggest no-variant groups left after T-154 get cited seed variants, so their EU registrations land on real rows.

## Acceptance criteria
- [ ] **Mazda MX-30** (EV, 35.5 kWh): seed variant(s) from Mazda documents.
- [ ] **smart forfour EQ (453)**: seed variant from smart / Mercedes documents.
- [ ] **Tesla Model X gen1**: split by pack / year as Tesla documents allow (cited WLTP per version).
- [ ] **Kia EV6 63 kWh** (facelift Standard Range): its own variant next to T-154's 84 kWh RWD / AWD.
- [ ] Then, biggest EU cars first, as time allows: Škoda Citigo e iV / SEAT Mii electric, Kia EV9, MG Marvel R, BYD Sealion 7. List what's left in Handoff notes.
- [ ] Maker documents only, cited per car, never a whole table (Decision 087). Check built drivetrain and WLTP against the seed (G-48).
- [ ] `sh data/seed/data_qa.sh` and `ev verify --base main` pass; matching regression run (0 unintended moves); queue numbers before / after (no-variant EU cars, % EU registrations on groups we have: 470,298 / 69.0 % after T-154).

## Inputs
WS0 INBOX 2026-11-19 09:15 UTC (batch: catalogue T-154, "Left on the list"); T-154 Handoff notes; Decision 057, 068, 087; workstreams/WS3/START.md.

## Out of scope
Matcher or rule changes (T-159, WS1). Cargo versions (Decision 084). T-156's items.

## Handoff notes

## Review
