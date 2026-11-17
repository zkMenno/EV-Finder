# T-066 Schema for shortlist rules, owner picks and missing scoring fields
Role: coordinator   Lane: packages/schema   Wave: 9
Status: merged (PR #30); fresh review via QA A-35; earlier note: WS0 coordinator, 2026-11-15; branch t-066-schema-shortlist-rules

## Goal
Give `data/editorial/` a schema so rules and picks are validated and typed (Decision 038).

## Acceptance criteria
- [x] `ShortlistProfile` (gates, factors with field / poor / great / weight, bonuses, penalties, bands per voltage class) and `EditorialPick` (seed ids, verdict enum shortlist|consider|fallback|ruled_out|unrated, favourite, flags, tier, notes; `sheet_values` marked internal and stripped from any published type)
- [x] New variant fields the rules need, all optional, `not-disclosed` allowed: `frunk_l`, `one_pedal` (yes / via setting / no), `regen_paddles`, `width_mm`, `ota_updates`
- [ ] (not in this PR, see handoff) Move `data/editorial/shortlist_rules.yaml` to `data/taxonomy/shortlist_rules.yaml`, wire into `validate_taxonomy.py`; update `backtest_rules.py` path
- [x] Profiles, modifiers, add-ons, picker and `filter_presets` (Decision 050); merge with `UsageProfile` so trip-fit and shortlist share one `usage_profiles` table (new rows: main-car-no-road-trips; ids road-tripper / daily-driver / runabout / kerbside-charger)
- [x] Fixtures valid + invalid

## Inputs
`data/editorial/shortlist_rules.yaml`, `data/editorial/menno-picks.yaml`, research/R-32, trip-fit §6 (`usage_profiles`: align factor ids).

## Out of scope
UI, scoring job.

## Handoff notes
2026-11-15, WS0 (schema lane only; PR "T-066 + T-065").
- **One profile type:** `UsageProfile` now carries the shortlist sections too (all optional): `aliases`, `picker` (shortlist_rules.yaml spelling of `applies_when`, same meaning), `matches_usage_profile` (transitional), `combines_with` (overlays such as kerbside-charger), `bands`, `gates`, `factors`, `extra_factors`, `bonuses`, `penalties`, `filter_presets`, `prefer`, `sort_default`, `not_rules`, `calibration`, `origin`, `why_a_profile`, `notes`, `status`. `weights` / `weight_steps` keys may now contain hyphens (`winter-range`), so trip-fit and shortlist factor ids can be the same ids. `ShortlistRules.profiles` and `.addons` are `UsageProfile[]`.
- **New defs:** `ShortlistRules` (file), `ShortlistModifier`, `PickerQuestion`, `ShortlistGate`, `ShortlistFactor`, `ShortlistAdjustment` (bonus/penalty), `FilterPreset` (Decision 050), `ShortlistBands` + `ShortlistBandThresholds` (per voltage class or `default`), `ShortlistRuleStatus` (ok/gap/calibrate/draft), `ShortlistBand` (shortlist/consider/fallback/ruled-out/not-enough-data), `ShortlistComboKey` (`road-tripper+kerbside.rural`), `ShortlistScore`, `ShortlistVariantScores`, `ShortlistScoresRelease` (shape of PR #15's shortlist_scores.json).
- **Per-variant score fields** on `PublishedVariant` (maps keyed by combo key): `shortlist_score`, `shortlist_band`, `shortlist_reasons`, `shortlist_unknown_factors`.
- **Variant fields** on `PublishedVariant`: `frunk_l`, `width_mm`, `one_pedal` (`OnePedal`: yes / via-setting / no / not-disclosed), `regen_paddles` (`FeatureAvailability`), `ota_updates` (`OtaUpdates`: full / infotainment-only / none / not-disclosed). `frunk_l` and `width_mm` were already FactFields.
- **Editorial picks:** `EditorialPick` (publishable; no `sheet_values` by design), `EditorialPickSheetRow` (internal row = pick + `sheet_values`), `EditorialSheetValues` (`use: internal`), `EditorialEraPick`, `EditorialUsedBudgetPick`, `EditorialPicks` (the whole menno-picks.yaml), `EditorialVerdict`, `EditorialFlag`. A test checks that no published file type (Catalogue, EditorialPick, ShortlistScoresRelease, TownsRelease, ConsumptionMatrixRelease, ChargingStatsRelease) can reach the sheet values.
- **Tests:** `packages/schema/test/editorial.test.ts` validates `shortlist_rules.yaml` (data/taxonomy first, data/editorial fallback, so the move needs no test change) and `menno-picks.yaml`, plus cross-checks: weight steps name existing factors, `combines_with` / `applies_with` point at real rows, picker answers exist. New devDependency `js-yaml` 5.5.0 (same version as apps/web) to read the YAML.
- **Not done here (outside the schema lane), for a follow-up:** move `shortlist_rules.yaml` to `data/taxonomy/`, wire into `validate_taxonomy.py`, update `backtest_rules.py` path; new `usage_profiles` rows (main-car-no-road-trips; ids road-tripper / daily-driver / runabout / kerbside-charger) and aligning trip-fit factor ids. FactField entries for `one_pedal`, `regen_paddles`, `ota_updates` are left out on purpose: pipeline `test_manual.py` requires a unit per FactField (pipeline/ev_pipeline/manual/facts.py), so they must land together with that pipeline change (WS1).

