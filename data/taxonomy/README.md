# data/taxonomy

Taxonomy tables from Decision 010. They are data, not enums: filters, tooltips and `/learn/[term]` pages read them, so adding a row needs no code change. Schema ids such as `chemistry_id` are free strings that are checked against these files.

| File | Rows (schema `$defs`) | What it holds |
|---|---|---|
| `voltage_classes.yaml` | `VoltageClass` | 400v / 800v / 900v-plus, set by nominal pack voltage (`min_v` inclusive, `max_v` exclusive, no gaps) |
| `chemistries.yaml` | `Chemistry` | NMC, NCA, LFP, LMFP, LMO/NMC, sodium-ion, semi-solid, all-solid-state, LMR, with pros, cons, care tips and daily-100 % guidance |
| `cooling_types.yaml` | `CoolingType` | liquid, refrigerant, air, passive |
| `glossary_terms.yaml` | `GlossaryTerm` | UI terms: plain label, technical name, tooltip `short` (max 20 words), `long`, `nerd_note`, `related` |
| `bidi_modes.yaml`, `bidi_routes.yaml`, `bidi_protocols.yaml`, `bidi_caveats.yaml`, `bidi_status.yaml` | `BidiMode` … `BidiStatus` | Bidirectional charging terms (Decision 011, T-019): V2L/V2H/V2G/V2B, AC vs DC route, protocols, caveat badges with `{param}`, status per country |
| `connector_types.yaml` | `ConnectorType` | Plugs: Type 2, CCS2, CHAdeMO, early Tesla EU, J1772, CCS1, NACS/J3400, GB/T |
| `bidi_equipment.yaml` | `BidiEquipment` | Approved bidirectional boxes. Low confidence, from R-01 only; held back from releases until its sources are releasable |
| `charging_metrics.yaml`, `charging_definitions.yaml`, `power_bands.yaml` | `ChargingMetric`, `ChargingDefinition`, `PowerBand` | Charging statistics (Decision 012, T-024): what is counted, how each source counts (incl. public vs semi-public), our five bands + source bands with `maps_to` |
| `taxonomy_sources.yaml` | `Source` | Sources cited by the rows above (not the licence registry; that is `data/sources.yaml`) |

The per-country link-out block lives in `config/countries/<cc>.yaml` under `charging_links` (T-024) and is checked here too: every URL must appear in `docs/spec/charging-buildout.md`.

Strings are per-language maps (`en`, `nl`, `de`, `fr`, `es`, `it`). `en` is required everywhere. `nl` is required for every `label` and for glossary `short`. Glossary EN must be complete: `technical`, a `long` of 2–4 sentences, `nerd_note` and `related`. `related` can point to other glossary ids or to chemistry, cooling or voltage-class ids. Glossary ids must not reuse those ids.

The tables were written from general knowledge, without fetching sources. `first_year` is `null` for every chemistry on purpose: "first series EV" claims are easy to get wrong, so we only fill it in from a checked source. `charge_100_daily: null` means there are too few cars or no consistent maker guidance yet.

## Related seed files (in `data/seed/`)

- `platforms.yaml`: `Platform` rows behind the seed models, plus a few common 2023+ platforms not used yet.
- `battery_packs.yaml`: `BatteryPack` rows. Per-pack caveats go under `notes:` keyed by pack id, because the schema row allows no notes field.
- `variant_links.yaml`: maps every variant in `variants.yaml` to `platform_id`, `battery_pack_id`, `voltage` (`VariantVoltage`) and `charger_400v` (`Charger400vBehaviour`). Generations with no seed variants get a default keyed `generation_id`, with `battery_pack_options` when the packs differ. `uncertain: true` needs a note. `class_override_note` allows a stated class that differs from the one derived from `nominal_v`. For example, the E-GMP 58 kWh pack is sold as "800 V" but is about 522 V nominal.

All three seed files are wrapped in `source: {id: seed-manual, ...}` with `confidence: low`. They hold unchecked, hand-entered data that sourced data should replace.

## Validate

```
python3 -I data/taxonomy/validate_taxonomy.py             # all taxonomy + platform/pack/link files
python3 -I data/taxonomy/validate_taxonomy.py --self-test # validator checks itself on mutated copies
```

Needs PyYAML and jsonschema 4.18 or newer (`pip install --break-system-packages jsonschema` if it is missing). Each row is validated against `ev.schema.json#/$defs/<Def>` through a `referencing` registry. The validator then checks: unique ids, every cross-reference, voltage-class contiguity, nl and word-count rules, that every variant is linked exactly once, that 400 V-class cars are `native` and 800 V+ cars are not, and that a link's `nominal_v` matches its pack's. Unused packs or platforms and pack-versus-variant capacity mismatches over 6 % are warnings, not errors.
