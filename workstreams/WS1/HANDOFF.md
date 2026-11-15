# WS1 handoff — 2026-11-15 ~10:30 UTC

Chat: https://claude.ai/code/session_01JuyZEUoRSsomn4V9CyYzLY. Next chat: "Read workstreams/WS1/HANDOFF.md and START.md and go."

## State: 8 PRs open, a chain (each branch contains the previous ones)

Merge in this order (all CI-green apart from main's own failures, which WS0 fixed in #8):

| PR | Branch | What |
|---|---|---|
| [#4](https://github.com/zkMenno/EV-Finder/pull/4) | `t-064-releases-out-of-git` | T-064 part 1: manifest.json + per-generation split, `ev release package/publish/fetch/verify`, GitHub Release assets `data-v<n>`, `data-publish.yml`, web `fetch-release.mjs` |
| [#5](https://github.com/zkMenno/EV-Finder/pull/5) | `fix/sources-decision-036-037` | sources.yaml housekeeping; EAFO `active_pending_confirmation` (new releasable status); RDW credit |
| [#7](https://github.com/zkMenno/EV-Finder/pull/7) | `t-025-charging-stats` | T-025: manual charging YAML, release diff → `data/review/charging_changes.csv`, refresh fix (`STAGING_SUFFIX`) |
| [#9](https://github.com/zkMenno/EV-Finder/pull/9) | `t-034-climate-normals` | T-034: GeoNames towns + Meteostat climate → `towns/<cc>.json`; ERA5-Land stub |
| [#10](https://github.com/zkMenno/EV-Finder/pull/10) | `t-033-consumption-model` | T-032/T-033: EPA consumption tests + `consumption_matrix.json` |
| [#11](https://github.com/zkMenno/EV-Finder/pull/11) | `t-035-backtest-epa` | T-035: proxy back-test on EPA (`qa.json backtest_epa`, audits/A-30), consumption calibration |
| [#12](https://github.com/zkMenno/EV-Finder/pull/12) | `t-062-retired-ids` | T-062 pipeline part: `retired_ids.json` (+ A-30 follow-up note) |
| [#13](https://github.com/zkMenno/EV-Finder/pull/13) | `fix/epa-range-class` | EPA Long/Standard Range rows only attach to that pack class |

If WS0 squashes/rebases #4 first, rebase the next branch with `git rebase --onto origin/main <old-tip-of-previous-branch>`.

## Waiting on others
- **T-064 part 2** (after #4 merges): Actions → Data publish → release `1`; check `data-v1` has 98 assets; then remove release 1's big files from git (`git rm --cached`, .gitignore already covers them) and ask WS0 to set the release cap back to 5 MB. WS4 must add a fetch step to `apps/web/Dockerfile` first (WS4 INBOX).
- **Schema (WS0 INBOX):** `TownsRelease`, `ConsumptionMatrixRelease`, `Catalogue.retired_ids`, `ac_kw_optional` (T-063 is blocked on it).
- **Decisions to log (WS0):** proposed 040 (charging defaults, Q-075/Q-076) and 041 (P10 definition, town→station rule, consumption reference basis).
- **WS3:** taxonomy rows (power bands, DfT valid_from, temperature_bands, heater_types), per-variant `heat_pump`, `data/manual/charging/*.yaml`, `data/seed/retired_ids.yaml`.
- **Menno (via QUESTIONS):** Q-047 (KilowattApp provenance) blocks rows for Kia EV3 / Hyundai Inster (KilowattApp-only records); Q-059 (NAF/Nyland permission) blocks the real launch gate.

## Open work for WS1 (next, in order)
1. **EPA matching, rest** (A-30): the range-class rule is in PR #13. Still open: US model-year lag (US 2024 "Cooper SE" is the old F56 but lands on Mini J01) and the Kona SX2 row whose 36.5 kWh battery looks wrong in the release itself. Test on staging like this: copy `openev`, `kilowatt-openev`, `fueleconomy` staging into a scratch data dir with the repo seed/taxonomy and diff the fueleconomy facts per variant.
2. **ERA5-Land loader** once `CDSAPI_KEY` is in the server env (Q-093): request in `sources/era5_land/adapter.py`.
3. T-064 part 2, T-063 after the schema lands.
4. R-21/R-22 follow-ups only if WS3 asks in the INBOX (START §3 item 8).

## Decisions made in this chat (engineering defaults)
- Release files: GitHub Release assets, flat asset names (`catalogue.generations.<id>.json`); git keeps manifest + `in_git` files; a release with a manifest on main never changes; unmerged ones may be replaced.
- Charging diff: growth > 15 % a month (compound), any fall, revisions, vanished series → review only.
- Towns: cities5000, names in 6 UI languages, coords 2 dp; nearest station ≤ 60 km and ≤ 250 m elevation gap, prefer one with P10; no interpolation.
- Consumption: battery basis (wall × 0.88); EPA adjusted = measured town/rural; motorway = EPA highway × 1.18 (body-specific); wltp-ratio calibrated to EPA (in-sample).

## Scratch data (lost with this container)
Live staging from today lived in `/tmp/evdata` (bnetza, dft-charging, eafo, geonames, meteostat, fueleconomy, openev, kilowatt-openev). Re-fetch with `EV_DATA_DIR=<dir> uv run ev fetch <id> && uv run ev normalise <id>`; meteostat needs geonames first (≈2 min, 1,000 stations).
