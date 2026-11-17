# A-32 Release 2 dry run: what the release diff blocks (T-123 / T-127)

**Date:** 2026-11-17 · **By:** WS1 (session_01JuyZEWFXbkeYSii8dVSWnx) · **Status:** open, needs a data review before release 2

## Method
Live staging recorded today in a scratch data dir (`ev refresh --no-release`: 13 of 14 sources ok; rdw-tgk failed with `SnapshotError: nothing to snapshot`). Then `ev verify` on branch `t-127-verify-pipeline` (includes T-123): release 2 rebuilt from that staging and diffed against the committed release 1 under `config/approved_changes.yaml` (no approvals). Peak memory 421 MB, ~50 s plus tests.

## Result
- 273 variants (226 in release 1): 48 added, 1 retired (`hyundai-ioniq-5-gen1-n` → facelift, T-068).
- **239 blocking** (152 changed beyond threshold, 87 cleared), 4117 review (mostly registration periods rolling forward, review only by design).
- Back-tests (report only): EPA proxy range 7.45 %, consumption 6.19 %, consumption out of sample 7.17 %; all under the 10 % proxy gate. Used prices vs NL samples: median −14.5 %.

## Findings (blocking, someone must decide)
1. 🟡 **WLTP consumption down ~11 % median** on 45 variants (39 down): EV6 58 RWD 16.6 → 14.7, Kona 39 15.0 → 12.9, Ioniq 6 AWD 15.0 → 12.5 kWh/100 km. DC km-in-10/20-min fields move with it (DC km = kWh / consumption). It looks like one systematic change (source upstream, or wall vs battery basis), not 45 separate ones. Check which source wins `consumption_kwh_100km` now vs release 1 before approving.
2. 🔴 **19 variants lose `wltp_range_km`** (and with it real range, consumption, DC km): BMW i3 120Ah / i3s / i3s 94Ah, Born 77, Mach-E SR RWD, EV6 GT, Niro DE 39/64, Soul SK3 39/64, EQA 300/350, MG ZS EV 44 / SR, Enyaq 85, Model 3 SR+ / SR+ LFP, Model S 75D, Model Y RWD, XC40 P8. Data loss, likely a matching or upstream change; fix, don't approve.
3. 🟡 9 WLTP values move > 5 %: e.g. Atto 3 60 kWh 510 → 420, bZ4X 470 → 416, CLA 808 → 743, Taycan Turbo S 405 → 440.
4. 🟡 Ioniq 5 gen1 `year_end` 2025 → 2023 (facelift split, T-068: probably intended → approve with T-068's PR).
5. 🟡 EV6 gen1 loses FR list prices and `weight_kg` on three variants; EV6 77 RWD NL price 49,290 → 57,260 €.
6. Still present: Model Y LR gen1 and Juniper LR AWD both 11.0 kWh/100 km and 387 km DC in 20 min (HANDOFF note, told WS0 earlier).

## Next
- WS1: trace findings 1–2 (which source/rule changed per field) as a follow-up task; WS0 to number it.
- Whoever ships release 2: approve the intended moves (T-068 facelift split, new registration periods are review only anyway) with a release-scoped entry naming the PR; fix the data losses.
- rdw-tgk snapshot failure: check before the next scheduled refresh.
