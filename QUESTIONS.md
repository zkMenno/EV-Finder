# Questions for Menno

Agents add questions here when they're blocked. Menno answers inline under **Answer:**. Once answered, the coordinator moves the outcome into DECISIONS.md or the task file and marks the question closed.

Format: `Q-NNN` · task id (if any) · who asked · date.

---

## Open

### Q-001 · Server capacity · coordinator · 2026-11-15
Does the AppInfra server have room for EV Finder? Partly answered (see Decision 006): CAX31, 16 GB, shared with GardenLayer and Dungeon Tracker; fits on paper while Cahier stays off. Still needed from the "EV Finder capacity check" chat: real `docker stats`, free disk, existing job timers (to confirm the 00:30–02:30 UTC window), and off-site backup status.

**Answer:**

### Q-002 · Package managers · coordinator · 2026-11-15
Default proposal: **pnpm** for the web app and **uv** for the Python pipeline (both fast and widely used by agents). OK, or do you prefer npm / pip?

**Answer:**

### Q-003 · Pull requests on `main` · coordinator · 2026-11-15
Right now `main` only blocks force-pushes and deletion. Once code arrives, should `main` require a pull request with green CI (agents can't push straight to `main`)? Recommended: yes, from wave 1.

**Answer:**

### Q-005 · Conflicting rules: "stop and ask" vs "never stop" · coordinator · 2026-11-15
AGENTS.md says a blocked builder stops and asks; the overnight brief says never stop. Repo files win, but nobody could answer overnight. **Default:** builders picked the safest option, logged it here and carried on, which is what "ask in QUESTIONS.md" amounts to when unattended. Should unattended runs get an explicit exception in AGENTS.md?

**Answer:**

### Q-006 · Where deploy files live · coordinator · 2026-11-15
The brief says `deploy/`; AGENTS.md and the README name `infra/` for deploy config. **Default:** repo wins, so the files are in `infra/deploy/` (`compose.ev.yml`, `ev.caddy`). Never applied. OK?

**Answer:**

### Q-007 · OpenEV Data coverage of older cars · T-004 · coordinator · 2026-11-15
OpenEV Data (CDLA-Permissive-2.0) mostly covers model years 2023+. Pre-2020 used favourites (Leaf ZE0, e-Golf, Zoe Q210/R240, i3 60 Ah, Ioniq 28 kWh, Soul EV) have few or no rows, so their generation pages show "no sourced specs yet". **Default:** leave them empty rather than fill from memory. Which open source should cover pre-2020 cars?

**Answer:**

### Q-008 · Maker documents and unclear-licence registries · coordinator · 2026-11-15
Decision 009 lets only sources with a named licence or written permission reach a release. Maker spec sheets and price lists have no licence; we would cite single facts by URL and date. KBA, SDES and EU Safety Gate reuse terms weren't checked tonight. **Default:** all four are `blocked` in data/sources.yaml. Can cited single facts from maker documents count as releasable (facts aren't copyrightable, but EU database right may apply)?

**Answer:**

### Q-009 · `dc_curve` cannot pass through SourceRecord · T-004 · builder · 2026-11-15
The schema now has `FactField.dc_curve` with a `ChargeCurve` value, but `records.SpecValue.value` is still `float | str | bool`, so an adapter cannot emit a curve. **Default:** no curves emitted. This costs nothing tonight: no OpenEV record has a `dc_charge_curve`. Should the coordinator widen `SpecValue.value` to `float | str | bool | ChargeCurve` between waves?

**Answer:**

### Q-010 · RDW: counting BEVs without a join · T-004 · builder · 2026-11-15
Socrata refuses joins, so we can't link fuel type (`8ys7-d773`) to make/model (`m9d7-ebf2`) server-side. **Default:** count in `m9d7-ebf2` with the proxy "passenger car, no engine displacement, first admitted 2010 or later". In 1,000-row checks it was 99.8 % precise with 100 % recall (details in data/SOURCES.md). The exact alternative would download about 1.2M kentekens from both datasets and join them locally. That isn't row-level spec data, but it's far heavier. OK to keep the proxy?

**Answer:**

### Q-011 · EEA: which year, and how confident are the counts · T-004 · builder · 2026-11-15
**Default:** use the latest table, 2025 provisional (`co2cars_2025Pv31`), rather than 2024 final (`co2cars_2024Fv30`). Counts get confidence `medium` because the table is provisional; type-approval averages get `low`. Prefer final data, or `high` for counts?

**Answer:**

### Q-012 · OpenEV field choices · T-004 · builder · 2026-11-15
1. OpenEV's DC peak is a maker figure. **Default:** keep it as `dc_peak_kw` (as briefed) and not also as `dc_peak_kw_claim`. Should it move to `dc_peak_kw_claim`?
2. `architecture_voltage_class` ("400v"/"800v", 723 files) has no numeric fact field. **Default:** not emitted; only `voltage_nominal_v` (161 records) and `voltage_max_v` (3) are. Is a voltage-class fact wanted?
3. **Default:** categorical facts (`chemistry_id`, `cooling_id`) use unit `"id"`. Generic "li-ion" is not emitted as a chemistry. OK?

**Answer:**

### Q-013 · Nyland sheet column mapping · T-004 · builder · 2026-11-15
The importer skeleton expects our own placeholder headers (`make, model, variant, year, range_km, consumption_kwh_100km, usable_kwh, dc_avg_10_80_kw`). The real sheet layout is unknown, and with permission pending we shouldn't look. **Default:** map the real headers once permission is logged. The real-range field may then need to split into summer/motorway/winter (the new `real_range_*_km` fields).

**Answer:**

## Closed

### Q-004 · Push access · coordinator · 2026-11-15
The overnight session could clone the repo (it's public) but was refused push access, so nothing could be pushed to `proto/overnight-1` and no draft PR could be opened. **Default:** all work is committed locally on `proto/overnight-1` and handed over as a git bundle; you push it with `git fetch <bundle> proto/overnight-1:proto/overnight-1 && git push -u origin proto/overnight-1`. Next time, attach the repo with write access before starting the session.

**Answer:** Menno granted push access at 00:49. Closed: branch pushed normally.


