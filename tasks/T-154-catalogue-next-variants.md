# T-154 Next catalogue variants: EV3, Elroq 85 / RS, Model 3 year split, e-tron GT 2025, no-variant list
Role: builder   Lane: data/seed, data/manual (WS3)   Wave: launch
Status: todo

## Goal
The next biggest gaps in the variant queue get cited seed variants, and figures trimmed under the old Decision 068 reading come back (Decision 087).

## Acceptance criteria
- [ ] **Restore trimmed figures** (Decision 087): maker figures dropped from #156 (Audi e-tron GT) and #164 / #166 / #167 under "one figure per document" may come back, one car per document, never a whole table.
- [ ] **Kia EV3:** Standard, Long Range and AWD together (needs a Kia page for the AWD). Check the built drivetrain and WLTP against the seed (the 2026 two-motor data built a lone row as AWD / 583 km).
- [ ] **Škoda Elroq 85 and RS**, after T-153's "cited power wins" merges (or with a source hold on OpenEV "Base" if T-153 is not merged when you get there; say which).
- [ ] **Tesla Model 3 gen1:** split 2019–20 from the 2021+ refresh (WLTP 580–614 km) by year, cited.
- [ ] **Audi e-tron GT 2025 entry version** (RDW `SBMQ3C*`): seed it with Audi figures.
- [ ] **Abarth 500e:** OpenEV files it as `fiat-500e-332-abarth`. Hold it or move it to the Abarth model; say which and why.
- [ ] **No-variant list, biggest EU cars first:** MX-30, smart forfour 453, Model X gen1, Inster, EV6 facelift, Countryman E, Aceman. Stop when time runs out; list what's left in Handoff notes.
- [ ] `sh data/seed/data_qa.sh` and `ev verify --base main` pass; matching regression run (0 unintended moves); queue numbers before / after.

## Inputs
WS0 INBOX 2026-11-18 16:14 UTC (batch: catalogue, item 3) and 18:53 UTC (batch: variant queue, "Next for WS3"); tasks/T-148 Handoff notes; Decision 057, 068, 087; workstreams/WS3/START.md.

## Out of scope
Matcher or `ev verify` changes (T-153, WS1). Cargo versions (Decision 084). T-151's four fixes (separate task).

## Handoff notes

## Review
