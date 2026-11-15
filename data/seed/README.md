# data/seed

`models.yaml` is the hand-curated seed list of used-EV favourites (Make → Model → Generation, schema `seed-models/v1`), with year spans, mid-generation change markers and `name_aliases` for matching source records.
Validate it with `python3 -I data/seed/validate_seed.py data/seed/models.yaml` (needs PyYAML); `--self-test` checks the validator itself against small inline fixtures.
It was written from model knowledge only, without fetching sources, so no value here is traceable yet: treat it as a seed for matching, not as published data.
Every generation with `uncertain: true` must be hand-checked against a primary source (manufacturer or registration data) before it is relied on; its `notes` field says what is in doubt.

## variants.yaml

`variants.yaml` holds hand-entered key battery/drivetrain variants (e.g. Zoe R110, i3 94 Ah, Kona 64 kWh) for generations in `models.yaml`, mainly those starting before 2023 that OpenEV Data (our base spec source, mostly model year 2023+) does not cover.
It is **unchecked, low-confidence data written from model knowledge**, without fetching sources: every entry has `confidence: low`, unknown fields are left out, approximate WLTP ranges sit in `notes` rather than in `wltp_range_km`, and there are deliberately no prices.
Downstream, OpenEV wins on any duplicate; each entry is meant to be replaced by sourced data (manufacturer, homologation or OpenEV) as soon as one exists.
Validate it with `python3 -I data/seed/validate_variants.py` (checks ids, generation links and year spans against `models.yaml`, allowed spec keys and plausible ranges, and no price keys).

### Cited values (`cited:`)

A variant may carry `cited:` values next to its unchecked `specs`: `field: {value, source_url, source_name, retrieved, quote and/or locator, confidence, notes}`.
Each cited value must come from a public page (https), name the date it was read, and set its confidence honestly; a field is either in `specs` or in `cited`, never both.
The pipeline turns each one into its own `seed-manual` record, so the published fact carries that URL and retrieval date instead of the file date.
Only add a cited value when a manufacturer or official source states it; if none is found, leave the field out and note it.
