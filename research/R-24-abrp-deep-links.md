# R-24 ABRP deep links and car-model typecodes

Researcher, 2026-11-15. Feeds T-029 (WS3) and the WS5 ABRP outreach draft.

**Answer.** ABRP's own deep-link docs (Postman, "ABetterRouteplanner.com deep links") list exactly six URL parameters on `https://abetterrouteplanner.com/`: `car_model`, `plan_uuid`, `embedded`, `charger_id`, `lat`, `lon`, plus `destinations` (a JSON array). The parameter is called **`car_model`, not `typecode`**; its value is an ABRP "typecode" such as `kia:ev6:22:77`. 🟢 The docs say deep linking is **free**, on one condition: it must give end users a view of ABRP or a plan in ABRP, and **the link text has to mention ABRP or ABetterRouteplanner.com**. 🟢 No API key is needed for the link itself. There is **no documented deep-link parameter for initial state of charge** (SoC); `initial_soc_perc` exists only in the paid planning API. 🔴 for SoC in links. The official typecode list endpoint (`get_carmodels_list`) is described as key-less, but it answered `401 Unauthorized Key` today, so a free telemetry API key (or an answer from ABRP) is needed to pull the live list. 🟢 (observed). I found typecodes for all five sample models, two of them confirmed in Iternio's own GitHub repos or docs.

## 1. Deep-link parameters (as documented)

Source: ABRP deep links collection, published 2021-02-16, linked from ABRP's API page and help centre. 🟢

| Parameter | Value | What it does (their words, shortened) | Conf. |
| --- | --- | --- | --- |
| `car_model` | ABRP typecode | "Select a certain car model typecode in the app." | 🟢 |
| `plan_uuid` | UUID | Loads a pre-made plan with all its settings. The UUID comes from the ABRP URL after planning. | 🟢 |
| `embedded` | `1` | Stripped-down iframe mode; use with `plan_uuid` to show one trip. | 🟢 |
| `charger_id` | ABRP charger ID | Opens the charger information page. | 🟢 |
| `lat`, `lon` | numbers | Initial map centre before a plan loads. (Listed but disabled in the example.) | 🟢 |
| `destinations` | JSON array of `{address, lat, lon}` | Pre-fills destinations. Uses the destination object of the planning API (`id`, `lat`/`lon`, `address`, `locationid`, ...). | 🟢 documented, 🟡 works |
| initial SoC, units, speed, etc. | none | Not documented as deep-link parameters. Do not use. | 🔴 |

The generic template from the docs:
`https://abetterrouteplanner.com/?car_model=<ABRP typecode>&plan_uuid=UUID&embedded=1&charger_id=<ABRP ID of charger>`

Notes:
- 🟡 `destinations` may be flaky: a 2024 bug report on ABRP's support board says a link with `car_model` + `destinations` opens the default map instead of the route (status "In Progress", no replies). Ship `car_model` alone first; test `destinations` by hand before using it.
- 🟡 The docs say "the set of deep links will be extended if there is interest", so ask ABRP whether anything newer exists (SoC, the 2026 three-car compare).
- 🔴 I could not open ABRP's 2026 car-comparison guide (fetch blocked in this session), so I don't know if the compare view has a link format.

## 2. Typecode format

- Colon-separated string, lowercase: `make:model:year:battery-or-trim[:extra]`. Examples: `tesla:m3:19:bt36:none`, `hyundai:kona:19:64:other`, `renault:zoe:20:52:r135`. 🟢 (format seen in Iternio docs and repos)
- The planning API docs say: "Additional options are added at the end, separated by ':'". So a base code can have option suffixes. 🟢
- Codes are not regular enough to build by rule. Some legacy codes are not colon-style at all (`3standard`, `3long`, shown in Iternio's own examples). 🟢
- Codes can be **deprecated**, with a `replaced_by` field pointing to the new code; old codes "still work in the planner". 🟢 Store this and re-check from time to time.
- Third-party projects disagree on codes: evDash uses `kia:ev6:22:77:lr` and `renault:zoe:ze50:52:other`, but neither appears in the list dump below. 🟡 Only trust codes from ABRP's own list.

**Official list sources** (pick in this order):
1. `https://api.iternio.com/1/tlm/get_carmodels_list`: name → typecode pairs. Docs call it key-less, but it returned `401 Unauthorized Key` today. Free telemetry API keys can be made in an ABRP account (that needs a login, so ask Menno first). 🟢
2. `https://api.iternio.com/1/get_vehicle_library`: full data incl. options, `deprecated`, `replaced_by`. Planning API; needs a key from contact@iternio.com. 🟢
3. Public GitHub dump of the old `get_carmodels` output (birkir/evrangev2, 375 entries, newest cars from about 2022–23). Useful for a first pass only. 🟡 old, third-party.

## 3. Five sample models

Links open ABRP with the car pre-selected. Not tested in a browser (ABRP is a JavaScript app). 🟡

| Car | Typecode | Example link | Evidence | Conf. |
| --- | --- | --- | --- | --- |
| Hyundai Kona Electric 64 kWh (2019–20) | `hyundai:kona:19:64:other` | https://abetterrouteplanner.com/?car_model=hyundai:kona:19:64:other | Iternio Planning API example, Iternio autopi-link repo, list dump, EVNotify, evDash | 🟢 |
| Kia EV6 Long Range 77 kWh | `kia:ev6:22:77` | https://abetterrouteplanner.com/?car_model=kia:ev6:22:77 | Iternio autopi-link repo, list dump (RWD/AWD likely an option suffix; evDash uses `:lr`) | 🟢 base / 🟡 RWD vs AWD |
| VW ID.3 Pro 58 kWh | `volkswagen:id3:20:58:mr` | https://abetterrouteplanner.com/?car_model=volkswagen:id3:20:58:mr | List dump, EVNotify, evDash agree | 🟡 |
| Renault Zoe ZE50 R135 | `renault:zoe:20:52:r135` | https://abetterrouteplanner.com/?car_model=renault:zoe:20:52:r135 | List dump only ("Z.E. 50 R135 with CCS") | 🟡 |
| Tesla Model 3 Long Range (2021) | `tesla:m3:20:bt37:heatpump` | https://abetterrouteplanner.com/?car_model=tesla:m3:20:bt37:heatpump | List dump only; LR has 4+ codes by year | 🟡 |
| Tesla Model 3 Highland (2024+) | not found | none | Not in any source I could open | 🔴 |

Example with destinations (documented, not yet proven working, 🟡):
`https://abetterrouteplanner.com/?car_model=kia:ev6:22:77&destinations=[{"address":"Angoulême, France"},{"address":"Bordeaux, France"}]` (URL-encode the JSON when building it).

## 4. Terms, keys and branding

- 🟢 Deep links: free; for showing users ABRP or a plan in ABRP; link text must mention "ABRP" or "ABetterRouteplanner.com". So "Plan a trip with this car in ABRP" passes.
- 🟢 No API key for deep links. Telemetry keys are free. The planning API (`plan`) has a setup cost plus a fee per plan; all other calls are free. Keys via contact@iternio.com.
- 🔴 No branding or logo rules found. Don't use the ABRP logo unless they say yes.
- 🟡 The API page footer now links to **Rivian's** privacy notice and terms of use. I didn't read those terms; WS5 should check them for linking or trademark clauses before launch.
- Support portal: abrp.featurebase.app. Contact email in the Iternio docs: contact@iternio.com. (The outreach draft says no email is published; that's out of date.)

## 5. What T-029 needs

1. Field: `abrp_typecode` (string, nullable) per variant, plus source URL, retrieved_at and confidence (Data rule 1). Also `abrp_deprecated` / `abrp_replaced_by` if the list provides them.
2. Note in data/seed/README.md: parameter name is `car_model`; value is an opaque ABRP typecode; never build it from parts; refresh from the official list.
3. Get the live list: either (a) a free ABRP telemetry key (needs Menno to log in to ABRP, so ask first), or (b) ABRP sends the list or confirms the endpoint. Until then, use the table below and the old dump only as 🟡 and mark them that way.
4. One variant can map to several codes (e.g. Model 3 LR by year, Zoe with or without CCS). Pick the code that matches the variant's years; leave null when unsure.
5. WS2: link text must say "ABRP"; open in a new tab; send `car_model` only for now (no SoC, `destinations` after a hand test).

## 6. What WS5's ABRP email should change and ask

- Fix the wording: the parameter is `car_model` (value = typecode), not `typecode`. Their docs already allow free linking under the link-text condition, so question 1 becomes "we follow your deep-link terms; is this use fine on public model pages, with a UTM tag?"
- Ask: (a) official, stable way to get the typecode list without a planning key (the "key-less" `get_carmodels_list` now returns 401); (b) how deprecations and `replaced_by` are announced; (c) any deep-link parameter for starting SoC, or for the three-car compare view; (d) whether `destinations` deep links are supported (the 2024 bug report); (e) logo or naming rules, and whether Rivian's terms now apply to linking.
- Add contact@iternio.com as a possible route next to the contact page and featurebase portal.

## Ready-to-import table

`variant_slug_hint` uses ids seen in data/seed/variants.yaml. All links opened 2026-11-15.

| variant_slug_hint | abrp_typecode | source_url | retrieved_at | confidence |
| --- | --- | --- | --- | --- |
| hyundai-kona-electric-os-64kwh | hyundai:kona:19:64:other | https://github.com/iternio/autopi-link/blob/ab65ec3dfe1248977b2e98674d43ead7f262af75/autopi_cars.json | 2026-11-15 | 🟢 |
| hyundai-kona-electric-os-39kwh | hyundai:kona:19:39:other | https://github.com/iternio/autopi-link/blob/ab65ec3dfe1248977b2e98674d43ead7f262af75/autopi_cars.json | 2026-11-15 | 🟢 |
| hyundai-kona-electric-os-64kwh (2021 facelift) | hyundai:kona:21:64:other | https://github.com/birkir/evrangev2/blob/04e8e235e152cf68a265d234c20b6f84efdbef91/src/data/abrp.json | 2026-11-15 | 🟡 |
| kia-ev6-gen1-77kwh-rwd | kia:ev6:22:77 | https://github.com/iternio/autopi-link/blob/ab65ec3dfe1248977b2e98674d43ead7f262af75/autopi_cars.json | 2026-11-15 | 🟡 (base code; drive option unknown) |
| kia-ev6-gen1-77kwh-awd | kia:ev6:22:77 | https://github.com/iternio/autopi-link/blob/ab65ec3dfe1248977b2e98674d43ead7f262af75/autopi_cars.json | 2026-11-15 | 🟡 (base code; drive option unknown) |
| kia-ev6-gen1-58kwh-rwd | kia:ev6:22:58 | https://github.com/iternio/autopi-link/blob/ab65ec3dfe1248977b2e98674d43ead7f262af75/autopi_cars.json | 2026-11-15 | 🟢 |
| volkswagen-id3-gen1-pro | volkswagen:id3:20:58:mr | https://github.com/birkir/evrangev2/blob/04e8e235e152cf68a265d234c20b6f84efdbef91/src/data/abrp.json | 2026-11-15 | 🟡 |
| volkswagen-id3-gen1-pro-s | volkswagen:id3:20:77:lr | https://github.com/birkir/evrangev2/blob/04e8e235e152cf68a265d234c20b6f84efdbef91/src/data/abrp.json | 2026-11-15 | 🟡 |
| volkswagen-id3-gen1-pure | volkswagen:id3:20:45:sr | https://github.com/birkir/evrangev2/blob/04e8e235e152cf68a265d234c20b6f84efdbef91/src/data/abrp.json | 2026-11-15 | 🟡 |
| renault-zoe-ph2-r135 | renault:zoe:20:52:r135 | https://github.com/birkir/evrangev2/blob/04e8e235e152cf68a265d234c20b6f84efdbef91/src/data/abrp.json | 2026-11-15 | 🟡 |
| renault-zoe-ph2-r110 | renault:zoe:20:52:r110 | https://github.com/birkir/evrangev2/blob/04e8e235e152cf68a265d234c20b6f84efdbef91/src/data/abrp.json | 2026-11-15 | 🟡 |
| tesla-model-3-gen1-long-range (2021) | tesla:m3:20:bt37:heatpump | https://github.com/birkir/evrangev2/blob/04e8e235e152cf68a265d234c20b6f84efdbef91/src/data/abrp.json | 2026-11-15 | 🟡 |
| tesla-model-3-gen1-long-range (2022) | tesla:m3:22:e3cd:heatpump | https://github.com/birkir/evrangev2/blob/04e8e235e152cf68a265d234c20b6f84efdbef91/src/data/abrp.json | 2026-11-15 | 🟡 |
| tesla-model-3-gen1-sr-plus (2019–20) | tesla:m3:19:bt36:none | https://documenter.getpostman.com/view/7396339/SWTK5a8w | 2026-11-15 | 🟢 |
| tesla-model-3 Highland (2024+) | null | n/a | 2026-11-15 | 🔴 |

Corroboration: the VW ID.3 58 kWh, Zoe ZE50 R110 and Kona 64 codes also appear in EVNotify's ABRP integration; ID.3 and Kona also appear in evDash.

## Sources (all opened 2026-11-15)

- ABRP deep links (Postman): https://documenter.getpostman.com/view/7396339/TWDTNeds (read via its public JSON: https://documenter.gw.postman.com/api/collections/7396339/TWDTNeds)
- Iternio Telemetry API (Postman, `get_carmodels_list`, example `tesla:m3:19:bt36:none`): https://documenter.getpostman.com/view/7396339/SWTK5a8w
- Iternio Planning API (Postman: `get_vehicle_library`, options suffix, `deprecated`/`replaced_by`, `initial_soc_perc`, destination object, pricing): https://documenter.getpostman.com/view/7396339/SWTK3YsN
- Official list endpoint (returned 401 Unauthorized Key): https://api.iternio.com/1/tlm/get_carmodels_list
- ABRP API page: https://abetterrouteplanner.com/resources/api
- ABRP help, Iternio APIs: https://abrp.featurebase.app/help/articles/1764088-iternio-apis
- ABRP support board, deep-linking bug report (2024): https://abrp.featurebase.app/p/deeplinking-to-abrp-ios-app-2
- Iternio autopi-link (first-party): https://github.com/iternio/autopi-link/blob/ab65ec3dfe1248977b2e98674d43ead7f262af75/autopi_cars.json
- Iternio ev-obd-pids (first-party, wildcard codes like `peugeot:e208:*`): https://github.com/Iternio-Planning-AB/ev-obd-pids/blob/1cb4f34b1d50208d99de5a0d019667a5340f9f25/obdble_cars.json
- Old `get_carmodels` dump (third-party): https://github.com/birkir/evrangev2/blob/04e8e235e152cf68a265d234c20b6f84efdbef91/src/data/abrp.json
- EVNotify ABRP integration: https://github.com/EVNotify/EVNotifyBackend/blob/63d6d73915327e696584ad724c0ecd91f05569c1/modules/integrations/abrp/index.js
- evDash car model list: https://github.com/nickn17/evDash/blob/af84ea1dc5320d27bc8a88f51b03dabc5cceb35c/src/CarModelUtils.cpp
- Not opened (blocked): https://abetterrouteplanner.com/resources/article/2026-02-15_car-comparison-guide
