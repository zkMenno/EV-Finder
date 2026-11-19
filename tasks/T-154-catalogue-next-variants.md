# T-154 Next catalogue variants: EV3, Elroq 85 / RS, Model 3 year split, e-tron GT 2025, no-variant list
Role: builder   Lane: data/seed, data/manual (WS3)   Wave: launch
Status: done (merged #184, #182, #183, #187; WS0 2026-11-19)

## Goal
The next biggest gaps in the variant queue get cited seed variants, and figures trimmed under the old Decision 068 reading come back (Decision 087).

## Acceptance criteria
- [x] **Restore trimmed figures** (Decision 087): the Audi e-tron GT figures trimmed from #156 under "one figure per document" (see T-145 Handoff notes) may come back, cited per car, never a whole table.
- [x] **Kia EV3:** Standard, Long Range and AWD together (needs a Kia page for the AWD). Check the built drivetrain and WLTP against the seed (the 2026 two-motor data built a lone row as AWD / 583 km).
- [x] **Škoda Elroq 85 and RS**, after T-153's "cited power wins" merges (or with a source hold on OpenEV "Base" if T-153 is not merged when you get there; say which).
- [x] **Tesla Model 3 gen1:** split 2019–20 from the 2021+ refresh (WLTP 580–614 km) by year, cited.
- [x] **Audi e-tron GT 2025 entry version** (RDW `SBMQ3C*`): seed it with Audi figures.
- [x] **Abarth 500e:** OpenEV files it as `fiat-500e-332-abarth`. Hold it or move it to the Abarth model; say which and why.
- [x] **No-variant list, biggest EU cars first:** MX-30, smart forfour 453, Model X gen1, Inster, EV6 facelift, Countryman E, Aceman. Stop when time runs out; list what's left in Handoff notes.
- [x] `sh data/seed/data_qa.sh` and `ev verify --base main` pass; matching regression run (0 unintended moves); queue numbers before / after.

## Inputs
WS0 INBOX 2026-11-18 16:14 UTC (batch: catalogue, item 3) and 18:53 UTC (batch: variant queue, "Next for WS3"); tasks/T-148 Handoff notes; Decision 057, 068, 087; workstreams/WS3/START.md.

## Out of scope
Matcher or `ev verify` changes (T-153, WS1). Cargo versions (Decision 084). T-151's four fixes (separate task).

## Handoff notes
PRs: gate #184 (release-4 approvals), #182 (e-tron GT), #183 (EV3, Elroq, Model 3, Abarth), plus a no-variant PR (Inster, Countryman E, Aceman, EV6 facelift; see its body). Measured with isolated rebuilds on the same staging (2026-11-19): each branch built as a release, diffed against the one before it.
- **e-tron GT (#182):** the trimmed Audi figures are back per car (battery net / gross, AC, top speed, 0-100, length), plus Audi WLTP for the S (609 km) and RS performance (592 km); 800 V class on the links. New row `audi-e-tron-gt-facelift-quattro` (2025 entry car, RDW SBMQ3C*). Rule quirk for WS0: Decision 038's newest-version rule compares versions model-wide, so the 2025 entry trim turns the 2024 S / RS / RS performance into "older versions" (about -10 points); approved in #184, not changed.
- **EV3 (#183):** rows Standard Range, Long Range and Long Range AWD (Kia UK). Names decide where US EPA rows go, so the Long Range stays FWD. The AWD row holds both two-motor versions (195 kW AWD, 215 kW GT) without a power figure until power evidence can split them. Open: RDW TGK F5E22 (Long Range) records tie Long Range vs AWD (TGK evidence has no drivetrain or power yet; T-153), so the Long Range has no WLTP yet.
- **Elroq (#183):** rows 85 and RS from Škoda's data sheet. **T-153 was not merged, so a source hold on OpenEV "Base" was used**; `skoda-elroq-gen1-base` is retired to the 85. **Follow-up: remove that hold once T-153's "cited power wins" merges**, then check that the 85 gets Base's DC and charging data.
- **Model 3 gen1 (#183):** split by RDW TGK variant: 2019-2020 (E3D / E5D) and 2021+ (E3LD / E5LD). The new rows cite the most-registered E5LD figures: Long Range 602 km / 14.7, Performance 547 km / 16.5. The BE 2022 list prices move with them. A variant split, not a generation (same body, no visible facelift).
- **Abarth 500e (#183): moved, not held.** OpenEV has no Abarth file; the old Fiat-generation row was our own seed row. Now `abarth-500e-gen1-base`; the old id is retired.
- **Queue (`ev variants propose`, same staging, no-variant EU cars):** main 632,534 -> #183 567,917 -> no-variant PR 470,298; EU registrations on groups we have: 67.9 % -> 68.5 % -> 69.0 %. The no-variant PR leaves new ties (EV6 facelift RWD vs AWD on single-motor groups, Countryman E vs SE ALL4, Inster 42 vs 49 on one group), so 48k more EU cars sit in ties rather than no-variant. The stated single vs dual motor in T-153's split evidence would settle them.
- **Left on the no-variant list:** MX-30 (Mazda press PDF found, not read: the download is a JS wrapper), smart forfour 453, Model X gen1 (many packs), EV6 facelift 63 kWh (no Kia page read), Citigo e iV / Mii electric (same 36.8 kWh e-up! pack row), EV9, MG Marvel R, BYD Sealion 7, Countryman / Aceman JCW, EV6 GT facelift.

## Review
