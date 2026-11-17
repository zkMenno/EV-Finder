# WS1 handoff — 2026-11-17 ~11:00 UTC

Chat: https://claude.ai/code/session_01JuyZEXwrHCn4kh6fda8bso (5th WS1 session). Next chat: "Read workstreams/WS1/HANDOFF.md and START.md and go."

## State
| PR | What | Where it stands |
|---|---|---|
| [#58](https://github.com/zkMenno/EV-Finder/pull/58) | T-063 optional on-board charger | **Fresh review done by this chat: pass, no must-fix** (notes in tasks/T-063). CI green on d46df28. WS0: merge. |
| [#66](https://github.com/zkMenno/EV-Finder/pull/66) | T-071 derived WLTP consumption x 1.16 charging losses (Decision 047) | Built by this chat. CI green on 23d5240. Needs a **fresh** reviewer (not this chat). |
| [#67](https://github.com/zkMenno/EV-Finder/pull/67) | T-072 `real_range_winter_km` on every row (WS2 hero) | Built by this chat; includes one additive schema line (asked WS0). CI dispatched on a89c456. Needs a fresh reviewer + WS0 ok on the schema line. |

## Next for WS1 (in order)
1. Follow-up for #58 after it merges: test for the rows guard (ac_kw_optional ≤ ac_kw dropped; mutation survives today) + open-data label for `ac_kw` ("standard where known, else source max").
2. **T-116 release 2** is WS1's (WS0 INBOX 11:50): start once #60 (T-110), #61/#62 (T-111), T-112 and T-113 are merged. Release 2 needs one release-scoped approval in config/approved_changes.yaml covering A-32 + #66 (58 consumption rows) + #67 (new winter field).
3. WS3 asks still open: `normalise.key` '+' → 'plus' (T-068; xfail waits in test_t124), `years:` on manual facts (T-031).
4. T-070 (real range + DC km from the matrix) still needs a WS0 Launch tag. Its DC km basis point is real: DC km divides battery-side kWh by a wall-basis motorway figure on all rows (≈12–14 % low).

## Findings worth keeping
- Official WLTP / battery-basis (net kWh / WLTP km) = 1.159 median, n 138, IQR 1.13–1.20 (release 1).
- Ioniq 6 53 kWh WLTP comes from EPA id 48363 x 1.12: 🔴 may be the long-range EPA car; WS3 to cite the type approval. Model Y LR WLTP 719 (OpenEV) is wrong; #60 fixes with RDW TGK.
- Release 1 has no consumption_matrix.json asset (predates T-033); dry runs rebuild the matrix from release rows without staging EPA tests.
- WebFetch of fueleconomy.gov needed an approval nobody answered; plan around it.
