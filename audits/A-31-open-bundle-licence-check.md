# A-31 Open data bundle: licence gate check (START §3 item 7, Decision 016)

WS1, 2026-11-15, on release 1 (`data/releases/1/open/`).

## Result: pass, one open risk

- 🟢 The bundle ships with every release: `finish_release` always calls `write_open_bundle` before the folder goes live (qa/release_step.py).
- 🟢 Every exported value traces to its sources (`<field>_sources`); none is untraced.
- 🟢 Sources in the bundle: ademe, dft-veh, eea, fueleconomy, kba-fz10, kilowatt-openev, model-estimate, openev, rdw, rdw-tgk, seed-manual. All `active` in data/sources.yaml with an open licence (CC BY 4.0, CC0, CDLA-Permissive-2.0, Licence Ouverte 2.0, MIT-with-attribution, OGL-UK 3.0, US public domain, dl-de/by-2-0).
- 🟢 Nothing ODbL or blocked: no Washington DOL, no EAFO (aggregates only, not in the bundle), no Nyland.
- 🟢 The gate withholds values whose sources don't pass: 141 `platform_id`, 141 `charger_400v_mode`, 73 `voltage_class_id` are in the catalogue but empty in the bundle.
- 🟢 `shortlist_scores.json` (editorial) and `used_prices.json` (estimates) are not part of the bundle.

## Open risk
- 🔴 `kilowatt-openev` supplies 1,099 values in the bundle (curves, DC figures, specs). Q-047 asks whether some of those values were copied from ev-database.org (no open licence). The bundle follows the Q-047 default (import as a low-priority fallback). If Menno answers "keep it out", set the source to `internal` in data/sources.yaml and the gate drops it from the catalogue and the bundle in the next release: no code change needed.

## Method
Script read `open/variants.json`, split every `*_sources` cell and every `reg_*_source` cell, and checked each id against the release's source licences and the registry status.
