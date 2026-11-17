// GENERATED from schemas/ev.schema.json by scripts/gen.mjs. Do not edit.

/**
 * Stable id: lowercase, hyphen-separated.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Id".
 */
export type Id = string;
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Country".
 */
export type Country = "NL" | "DE" | "FR" | "BE" | "UK";
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Currency".
 */
export type Currency = "EUR" | "GBP";
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Confidence".
 */
export type Confidence = "high" | "medium" | "low";
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Body".
 */
export type Body = "hatchback" | "sedan" | "estate" | "suv" | "crossover" | "coupe" | "mpv" | "cabrio";
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Segment".
 */
export type Segment = "A" | "B" | "C" | "D" | "E" | "F" | "J-small" | "J-medium" | "J-large";
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Drivetrain".
 */
export type Drivetrain = "fwd" | "rwd" | "awd";
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Era".
 */
export type Era = "pre-2018" | "2018-20" | "2021-22" | "2023-24" | "2025+";
/**
 * checked = staff hand-checked; sourced = 2+ agreeing sources; single-source = one source only.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "QualityTier".
 */
export type QualityTier = "checked" | "sourced" | "single-source";
/**
 * Which rung of the real-range fallback ladder produced the value (highest first).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "RealRangeRung".
 */
export type RealRangeRung =
  "owner-data" | "exact-test" | "sibling-variant" | "brand-body-drivetrain-ratio" | "body-ratio";
/**
 * Fact field names. Enum-valued facts are checked at release time, not here (an if/then on Fact breaks the generated TS type): iso15118_20_support → Iso15118Support (yes/no/not-disclosed, default not-disclosed, never inferred); heat_pump → HeatPumpFitment; drag_coefficient → Cd 0-1. Units: frontal_area_m2 m², kerb_mass_kg kg (kerb weight without driver; mass in running order is mass_running_order_kg, Decision 023), wheel_size_in = rim diameter code. Usable battery is battery_kwh_net (no separate usable_kwh field).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "FactField".
 */
export type FactField =
  | "battery_kwh_net"
  | "battery_kwh_gross"
  | "wltp_range_km"
  | "epa_range_km"
  | "consumption_kwh_100km"
  | "ac_kw"
  | "dc_peak_kw"
  | "dc_avg_10_80_kw"
  | "power_kw"
  | "accel_0_100_s"
  | "top_speed_kmh"
  | "boot_l"
  | "frunk_l"
  | "length_mm"
  | "width_mm"
  | "height_mm"
  | "wheelbase_mm"
  | "weight_kg"
  | "towing_kg"
  | "seats"
  | "price_new"
  | "real_range_km"
  | "registered_count"
  | "dc_curve"
  | "dc_minutes_10_80"
  | "dc_peak_kw_claim"
  | "consumption_motorway_kwh_100km"
  | "real_range_summer_km"
  | "real_range_motorway_km"
  | "real_range_winter_km"
  | "voltage_nominal_v"
  | "voltage_max_v"
  | "chemistry_id"
  | "cooling_id"
  | "cell_format"
  | "charger_400v_behaviour"
  | "warranty_years"
  | "warranty_km"
  | "iso15118_20_support"
  | "heat_pump"
  | "drag_coefficient"
  | "frontal_area_m2"
  | "kerb_mass_kg"
  | "wheel_size_in"
  | "nedc_range_km"
  | "nedc_consumption_kwh_100km"
  | "wltp_range_km_worst"
  | "wltp_consumption_kwh_100km_worst"
  | "mass_running_order_kg"
  | "power_30min_kw";
/**
 * Any market as an ISO 3166-1 alpha-2 code, except UK for the United Kingdom (same as Country). Wider than Country so US/AU/NZ/CA rows (Phase 4) need no schema change; checked against config at release time.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "CountryCode".
 */
export type CountryCode = string;
/**
 * option = fitted on some cars only; for used cars show both cases until the owner confirms.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "HeatPumpFitment".
 */
export type HeatPumpFitment = "standard" | "option" | "none" | "not-disclosed";
/**
 * One-pedal driving (regen to a full stop): yes = default or one button; via-setting = a menu setting to turn on; no; not-disclosed.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "OnePedal".
 */
export type OnePedal = "yes" | "via-setting" | "no" | "not-disclosed";
/**
 * Generic yes / no / not-disclosed for a car feature. Default not-disclosed; never inferred.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "FeatureAvailability".
 */
export type FeatureAvailability = "yes" | "no" | "not-disclosed";
/**
 * Over-the-air updates: full = drive / battery / charging software too; infotainment-only = maps and media only.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "OtaUpdates".
 */
export type OtaUpdates = "full" | "infotainment-only" | "none" | "not-disclosed";
/**
 * Band of a scored variant (Decision 038). ruled-out = failed a gate; not-enough-data = more than half the weight unknown.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ShortlistBand".
 */
export type ShortlistBand = "shortlist" | "consider" | "fallback" | "ruled-out" | "not-enough-data";
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "TaxonomyStatus".
 */
export type TaxonomyStatus = "mainstream" | "emerging" | "niche" | "legacy" | "experimental";
/**
 * A country, or an aggregate area for EAFO (EU27, EUROPE) and IEA (WORLD) series.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ChargingArea".
 */
export type ChargingArea = CountryCode | ("EU27" | "EUROPE" | "WORLD");
/**
 * The three route bands of the consumption matrix (Decision 013): town ≤50 km/h, rural 60-90, motorway 100+.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "RoadBand".
 */
export type RoadBand = "town" | "rural" | "motorway";
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "WeightLevel".
 */
export type WeightLevel = "off" | "low" | "medium" | "high" | "very-high";
/**
 * gap = field not in the data yet (factor scores 0.5, never a guess); calibrate = thresholds still to check; draft = not used for scoring yet.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ShortlistRuleStatus".
 */
export type ShortlistRuleStatus = "ok" | "gap" | "calibrate" | "draft";
/**
 * Kind of finance a FinanceProfile row describes. pcp = personal contract purchase (balloon at the end; UK, similar to FR LOA).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "FinanceProduct".
 */
export type FinanceProduct = "used-car-loan" | "new-car-loan" | "private-lease" | "business-lease" | "pcp";
/**
 * Shape of the value a clue of this type carries. number / text / code / boolean use VariantClue.value; number-range and date-range use VariantClue.range. code = an identifier matched as written (type-approval code, VIN character).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ClueValueKind".
 */
export type ClueValueKind = "number" | "number-range" | "date-range" | "text" | "code" | "boolean";
/**
 * Where a buyer finds the clue: ad text, ad photos, registration papers, on the car itself, or the VIN.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ClueFoundIn".
 */
export type ClueFoundIn = "ad" | "photos" | "papers" | "car" | "vin";
/**
 * How far a clue settles which variant it is (variant finder spec §3). decisive = on its own it separates the variant from every look-alike in rules_out; strong = usually settles it but sources or ads can be wrong; weak = a hint only (e.g. battery kWh in ads, often wrong).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ClueStrength".
 */
export type ClueStrength = "decisive" | "strong" | "weak";
/**
 * Why buyers confuse the group's variants: overlapping specs in one generation, the same badge, or the same marketing name across markets.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "LookalikeReason".
 */
export type LookalikeReason = "same-generation" | "same-badge" | "same-marketing-name";
/**
 * Car-side ISO 15118-20 support. Default not-disclosed; never inferred from model year (Decision 011).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Iso15118Support".
 */
export type Iso15118Support = "yes" | "no" | "not-disclosed";
/**
 * Fallback ladder rung (trip-fit §5): measured for this variant → same platform/pack scaled → physics → WLTP × class ratio.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ConsumptionRung".
 */
export type ConsumptionRung = "measured" | "platform" | "physics" | "wltp-ratio";
/**
 * Profile combination key: <profile>[+<overlay>][.<modifier>], e.g. 'road-tripper', 'runabout+kerbside.rural'.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ShortlistComboKey".
 */
export type ShortlistComboKey = string;
/**
 * Owner's verdict from the sheet colour (data/editorial/README.md legend).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "EditorialVerdict".
 */
export type EditorialVerdict = "shortlist" | "consider" | "fallback" | "ruled_out" | "unrated";
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "EditorialFlag".
 */
export type EditorialFlag = "love" | "like" | "watching" | "expensive";

/**
 * EV Finder catalogue schema v0. Single source of truth: TS and Python types are generated from this file. Stable ids never change; slugs may.
 */
export interface EvSchema {
  [k: string]: unknown;
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Money".
 */
export interface Money {
  amount: number;
  currency: Currency;
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ChangeMarker".
 */
export interface ChangeMarker {
  year: number;
  text: string;
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Source".
 */
export interface Source {
  id: Id;
  name: string;
  url?: string;
  /**
   * SPDX id or licence name, e.g. CDLA-Permissive-2.0, CC0-1.0.
   */
  licence: string;
  attribution?: string;
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Make".
 */
export interface Make {
  id: Id;
  name: string;
  slug: Id;
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Model".
 */
export interface Model {
  id: Id;
  make_id: Id;
  name: string;
  slug: Id;
  segment?: Segment;
  body?: Body;
  aliases?: string[];
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Generation".
 */
export interface Generation {
  id: Id;
  model_id: Id;
  name: string;
  slug: Id;
  year_start: number;
  /**
   * null = still on sale.
   */
  year_end?: number | null;
  /**
   * Year boundaries not hand-checked yet.
   */
  uncertain?: boolean;
  change_markers?: ChangeMarker[];
  years_corroboration?: GenerationYearsCorroboration;
}
/**
 * Outside sources checking a generation's hand-entered years. Corroboration only: the years themselves never change (T-059).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "GenerationYearsCorroboration".
 */
export interface GenerationYearsCorroboration {
  /**
   * true when every check agrees.
   */
  corroborated: boolean;
  tolerance_years: number;
  /**
   * @minItems 1
   */
  source_ids: [Id, ...Id[]];
  /**
   * @minItems 1
   */
  checks: [GenerationYearCheck, ...GenerationYearCheck[]];
}
/**
 * One outside production year compared with a generation boundary (T-059).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "GenerationYearCheck".
 */
export interface GenerationYearCheck {
  boundary: "start" | "end";
  year: number;
  /**
   * Within tolerance_years of the generation's year_start (start) or year_end (end).
   */
  agrees: boolean;
  source_id: Id;
  source_record?: string;
  /**
   * The source's own label for the item (e.g. the Wikidata item label).
   */
  label?: string;
  retrieved_at: string;
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Variant".
 */
export interface Variant {
  id: Id;
  generation_id: Id;
  name: string;
  slug: Id;
  year_start: number;
  year_end?: number | null;
  drivetrain?: Drivetrain;
  platform_id?: Id;
  battery_pack_id?: Id;
  voltage?: VariantVoltage;
  charger_400v?: Charger400VBehaviour;
  /**
   * ABRP car model code for deep links (Decision 012); null = plain ABRP link.
   */
  abrp_typecode?: string | null;
  /**
   * ABRP lists abrp_typecode as deprecated (old codes still work in the planner, R-24).
   */
  abrp_deprecated?: boolean;
  /**
   * ABRP's replacement typecode when abrp_typecode is deprecated (R-24). An ABRP code, not a variant id: renamed or merged variants go in Catalogue.retired_ids.
   */
  abrp_replaced_by?: string | null;
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "VariantVoltage".
 */
export interface VariantVoltage {
  /**
   * Stated nominal voltage.
   */
  nominal_v?: number | "not-disclosed";
  /**
   * Stated max voltage.
   */
  max_v?: number | "not-disclosed";
  /**
   * e.g. '800V', or 'not-disclosed'.
   */
  marketing_label?: string;
  /**
   * Derived from nominal_v via voltage_classes.
   */
  class_id?: Id | "not-disclosed";
  /**
   * Pack can switch between 400 and 800 V.
   */
  switchable?: boolean | null;
}
/**
 * How an 800 V+ car behaves on older 400 V DC chargers.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Charger400vBehaviour".
 */
export interface Charger400VBehaviour {
  mode: "native" | "booster" | "limited" | "not-disclosed";
  /**
   * Max kW on a 400 V charger (booster or limited).
   */
  kw?: number | null;
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "MarketVariant".
 */
export interface MarketVariant {
  id: Id;
  variant_id: Id;
  country: Country;
  local_name?: string;
  price_new?: Money;
  wltp_km?: number;
  epa_km?: number;
  drive_side?: "lhd" | "rhd";
  on_sale_new?: boolean;
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Fact".
 */
export interface Fact {
  id: string;
  subject_type: "model" | "generation" | "variant" | "market_variant" | "platform" | "battery_pack";
  subject_id: Id;
  field: FactField;
  /**
   * Scalar, or a ChargeCurve when field = dc_curve.
   */
  value: (number | string | boolean) | ChargeCurve;
  /**
   * Metric unit (kWh, km, kW, kWh/100km, l, mm, kg, s, km/h, count) or currency code for prices.
   */
  unit: string;
  /**
   * Set for market-specific facts (prices, registrations).
   */
  country?: "NL" | "DE" | "FR" | "BE" | "UK";
  source: Source;
  /**
   * Pointer to the raw record, e.g. a file path or row key.
   */
  source_record?: string;
  retrieved_at: string;
  observed_at?: string;
  confidence: Confidence;
  /**
   * true when the value is a maker claim rather than measured.
   */
  claim?: boolean;
}
/**
 * DC charge curve: list of (state of charge %, kW) points plus test conditions.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ChargeCurve".
 */
export interface ChargeCurve {
  /**
   * @minItems 2
   */
  points: [[unknown, unknown], [unknown, unknown], ...[unknown, unknown][]];
  status: "measured" | "estimated" | "default";
  conditions?: {
    battery_temp_c?: number;
    preconditioned?: boolean;
    ambient_temp_c?: number;
    charger_kw?: number;
    software_version?: string;
  };
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "FieldProvenance".
 */
export interface FieldProvenance {
  /**
   * @minItems 1
   */
  source_ids: [Id, ...Id[]];
  confidence: Confidence;
  fact_ids?: string[];
  /**
   * true when computed by us from other facts.
   */
  derived?: boolean;
  note?: string;
  /**
   * Number of independent sources agreeing within the field tolerance (UI badge 'N sources agree').
   */
  agreeing_sources?: number;
  /**
   * true when the value comes from a model/ratio rather than any source.
   */
  estimate?: boolean;
}
/**
 * One wide row per variant per release. What the web app reads.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "PublishedVariant".
 */
export interface PublishedVariant {
  release: number;
  variant_id: Id;
  variant_name: string;
  generation_id: Id;
  generation_name: string;
  generation_uncertain?: boolean;
  model_id: Id;
  model_name: string;
  make_id: Id;
  make_name: string;
  year_start: number;
  year_end?: number | null;
  era: Era;
  segment?: Segment;
  body?: Body;
  drivetrain?: Drivetrain;
  battery_kwh_net?: number | null;
  wltp_range_km?: number | null;
  /**
   * EPA (US 5-cycle) range in km, from fueleconomy.gov / OpenEV. Its own field: agreement is only ever counted against other EPA figures, never against WLTP (T-059).
   */
  epa_range_km?: number | null;
  /**
   * EPA city range, km (R-28).
   */
  epa_range_city_km?: number | null;
  /**
   * EPA highway range, km (R-28). The EPA highway cycle is not 120 km/h motorway driving.
   */
  epa_range_hwy_km?: number | null;
  consumption_kwh_100km?: number | null;
  /**
   * EPA label consumption (combined), kWh/100 km, wall basis. Separate from the WLTP consumption_kwh_100km (R-28).
   */
  consumption_epa_kwh_100km?: number | null;
  ac_kw?: number | null;
  /**
   * Optional bigger on-board charger, kW (Decision 034, T-063). ac_kw stays the standard one; null = no option or not known.
   */
  ac_kw_optional?: number | null;
  /**
   * EPA 240 V empty-to-full charge time, hours (R-28). Info only; never used to derive ac_kw.
   */
  ac_full_charge_h?: number | null;
  dc_peak_kw?: number | null;
  dc_avg_10_80_kw?: number | null;
  /**
   * Derived: ac_kw / consumption * 100.
   */
  ac_km_per_h?: number | null;
  /**
   * Derived: km added in 10 min at motorway consumption (dc_avg_10_80_kw / motorway consumption * 100 / 6).
   */
  dc_km_per_10min?: number | null;
  real_range_km?: number | null;
  /**
   * Derived estimate (T-072): km on a full usable battery at -5 °C and colder, mixed driving, from the consumption matrix. The temperature step is not validated by winter road tests yet (Q-059).
   */
  real_range_winter_km?: number | null;
  real_range_rung?: RealRangeRung | null;
  power_kw?: number | null;
  accel_0_100_s?: number | null;
  boot_l?: number | null;
  /**
   * Front boot, litres. 0 = no frunk; null = not known.
   */
  frunk_l?: number | null;
  length_mm?: number | null;
  /**
   * Width without mirrors, mm.
   */
  width_mm?: number | null;
  weight_kg?: number | null;
  towing_kg?: number | null;
  seats?: number | null;
  on_sale_new?: boolean;
  /**
   * New price per country (local currency).
   */
  price_new?: {
    [k: string]: Money;
  };
  /**
   * RDW registrations, counted at generation level.
   */
  registered_count_nl?: number | null;
  quality_tier: QualityTier;
  change_markers?: ChangeMarker[];
  /**
   * Field name → where the value came from. Every non-null number above must have an entry.
   */
  provenance: {
    [k: string]: FieldProvenance;
  };
  /**
   * Minutes 10-80%.
   */
  dc_minutes_10_80?: number | null;
  /**
   * Derived: km added in 20 min at motorway consumption. Used for the DC ranking.
   */
  dc_km_per_20min?: number | null;
  /**
   * Minutes above 90% of peak.
   */
  dc_peak_held_min?: number | null;
  /**
   * Motorway consumption used for km-in-N-minutes.
   */
  consumption_motorway_kwh_100km?: number | null;
  dc_curve_status?: ("measured" | "estimated" | "default") | null;
  /**
   * true when dc_peak_kw is a maker claim, not measured.
   */
  dc_peak_kw_is_claim?: boolean;
  platform_id?: string | null;
  platform_name?: string | null;
  battery_pack_id?: string | null;
  /**
   * Taxonomy id or 'not-disclosed'.
   */
  chemistry_id?: string | null;
  cooling_id?: string | null;
  cell_format?: string | null;
  voltage_nominal_v?: number | null;
  voltage_max_v?: number | null;
  voltage_label?: string | null;
  /**
   * Derived class id, or 'not-disclosed'.
   */
  voltage_class_id?: string | null;
  voltage_switchable?: boolean | null;
  charger_400v_mode?: "native" | "booster" | "limited" | "not-disclosed" | null;
  charger_400v_kw?: number | null;
  /**
   * Derived: native 400 V car, or booster/limited at >= 50 kW on 400 V chargers.
   */
  fast_on_400v?: boolean | null;
  /**
   * From the chemistry row.
   */
  charge_100_daily?: boolean | null;
  /**
   * Per country: official counts (fleet and/or new registrations).
   */
  registrations?: {
    [k: string]: RegistrationCount[];
  };
  /**
   * ABRP car model code; null = plain ABRP link.
   */
  abrp_typecode?: string | null;
  /**
   * ABRP's replacement typecode when abrp_typecode is deprecated (R-24).
   */
  abrp_replaced_by?: string | null;
  /**
   * Car-side ISO 15118-20. Default not-disclosed; never inferred.
   */
  iso15118_20_support?: "yes" | "no" | "not-disclosed";
  /**
   * Bidirectional capabilities incl. rows inherited from the platform; keyed by model_years and per-country market_status.
   */
  bidi?: BidiCapability[];
  /**
   * Charging inlets per market and model-year range.
   */
  ports?: ChargingPort[];
  /**
   * Heat pump: standard / option / none / not-disclosed.
   */
  heat_pump?: HeatPumpFitment | null;
  /**
   * One-pedal driving (T-066). null = not in the data yet; not-disclosed = looked for, not stated.
   */
  one_pedal?: OnePedal | null;
  /**
   * Steering-wheel paddles to change regen strength (T-066).
   */
  regen_paddles?: FeatureAvailability | null;
  /**
   * Over-the-air software updates (T-066).
   */
  ota_updates?: OtaUpdates | null;
  /**
   * Cd, unitless.
   */
  drag_coefficient?: number | null;
  frontal_area_m2?: number | null;
  /**
   * EU mass in running order.
   */
  kerb_mass_kg?: number | null;
  /**
   * Rim diameter codes offered (e.g. [18, 19, 20]).
   */
  wheel_sizes_in?: number[] | null;
  /**
   * Look-alike groups this variant is in (Catalogue.lookalike_groups); empty or absent = none known.
   */
  lookalike_group_ids?: Id[];
  /**
   * Number of clues for this variant in Catalogue.variant_clues, so the web app can skip the 'spot it' box without loading clues.
   */
  clue_count?: number;
  /**
   * Profile combination → score 0..100 (T-069). Editorial opinion, not fact.
   */
  shortlist_score?: {
    [k: string]: number;
  };
  /**
   * Profile combination → band (T-069).
   */
  shortlist_band?: {
    [k: string]: ShortlistBand;
  };
  /**
   * Profile combination → reason codes (see ShortlistScore.reasons).
   */
  shortlist_reasons?: {
    [k: string]: string[];
  };
  /**
   * Profile combination → factors / gates without data.
   */
  shortlist_unknown_factors?: {
    [k: string]: string[];
  };
  /**
   * NEDC range (old EU cycle). Never used to fill WLTP.
   */
  nedc_range_km?: number | null;
  /**
   * Worst-case WLTP range of the type approval (wltp_range_km is the best case or the single stated value).
   */
  wltp_range_km_worst?: number | null;
  /**
   * Mass in running order (incl. 75 kg driver), as in type approval; weight_kg stays kerb weight.
   */
  mass_running_order_kg?: number | null;
}
/**
 * One official count for a country. Kinds are not added together.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "RegistrationCount".
 */
export interface RegistrationCount {
  count: number;
  /**
   * fleet = cars on the road (stock); new_registrations = first registrations in the period.
   */
  kind: "fleet" | "new_registrations";
  /**
   * e.g. '2026-Q2', '2025', '2026-01..10'.
   */
  period?: string;
  /**
   * Level the count was matched at; model-level counts repeat on every generation.
   */
  level?: "generation" | "model";
  source_id: Id;
}
/**
 * One bidirectional mode for a variant, or for a platform (inherited by its variants). Decision 011, spec bidirectional-and-connectors §3.2. Eligibility is shown as conditions, never a plain tick, whenever min_software, min_battery_net_kwh or build_date_from is set.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "BidiCapability".
 */
export interface BidiCapability {
  id: Id;
  subject_type: "variant" | "platform";
  subject_id: Id;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  mode_id: string;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  route_id: string;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  protocol_id?: string;
  max_kw_out?: number | "not-disclosed";
  /**
   * e.g. 'ID. Software 3.5'.
   */
  min_software?: string | null;
  min_battery_net_kwh?: number | null;
  build_date_from?: string | null;
  /**
   * Model years covered; empty or absent = all years of the subject.
   */
  model_years?: number[];
  /**
   * bidi_equipment ids (approved boxes).
   */
  equipment_ids?: Id[];
  /**
   * A specific energy contract is needed (names per country in market_status).
   */
  tariff_required?: boolean | "not-disclosed";
  caveats?: BidiCaveatRef[];
  /**
   * Country → status. A country that is absent means not known (shown as not disclosed).
   */
  market_status: {
    [k: string]: BidiMarketStatus;
  };
  /**
   * Maker's eligibility page (used-car checklist deep link).
   */
  eligibility_url?: string;
  /**
   * Ids of rows in the catalogue sources list.
   *
   * @minItems 1
   */
  source_ids: [Id, ...Id[]];
  retrieved_at: string;
  confidence: Confidence;
  fact_ids?: string[];
  /**
   * Internal note; never shown as a caveat.
   */
  notes?: string;
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "BidiCaveatRef".
 */
export interface BidiCaveatRef {
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  id: string;
  /**
   * Optional parameter, typed by the caveat row's param_kind (number, ISO date, version string).
   */
  param?: number | string;
}
/**
 * Status of one capability in one country. Older than 90 days = 'may be out of date'.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "BidiMarketStatus".
 */
export interface BidiMarketStatus {
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  status_id: string;
  /**
   * Date the status started (launch date), if known.
   */
  since?: string;
  /**
   * Ids of rows in the catalogue sources list.
   *
   * @minItems 1
   */
  source_ids: [Id, ...Id[]];
  /**
   * Last date a source confirmed this status.
   */
  checked_at: string;
  confidence: Confidence;
  /**
   * Required energy contracts in this country, e.g. 'Mobilize Power'.
   */
  tariff_names?: string[];
  /**
   * Country-only caveats, added to the capability caveats.
   */
  caveats?: BidiCaveatRef[];
  fact_ids?: string[];
}
/**
 * Charging inlets of a variant per market and model-year range (US ports switch CCS1 → NACS by model year).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ChargingPort".
 */
export interface ChargingPort {
  id: Id;
  variant_id: Id;
  market: CountryCode;
  model_year_from: number;
  /**
   * null = still current.
   */
  model_year_to?: number | null;
  ac_inlet_id: string | "not-disclosed";
  /**
   * connector_types id; null = no DC charging.
   */
  dc_inlet_id: Id | "not-disclosed" | null;
  /**
   * Whether the listed DC connector is the car's own inlet or reached through an included adapter.
   */
  native_or_adapter?: "native" | "adapter" | "not-disclosed";
  /**
   * (US) Can it use Tesla Superchargers, and how.
   */
  supercharger_access?: "native" | "adapter" | "magic-dock" | "none" | "not-disclosed";
  adapters_included?: AdapterRef[];
  /**
   * Ids of rows in the catalogue sources list.
   *
   * @minItems 1
   */
  source_ids: [Id, ...Id[]];
  retrieved_at: string;
  confidence: Confidence;
  notes?: string;
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "AdapterRef".
 */
export interface AdapterRef {
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  from_connector_id: string;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  to_connector_id: string;
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Catalogue".
 */
export interface Catalogue {
  release: number;
  generated_at: string;
  sources: Source[];
  generations?: Generation[];
  rows: PublishedVariant[];
  taxonomy?: Taxonomy;
  platforms?: Platform[];
  battery_packs?: BatteryPack[];
  variant_clues?: VariantClue[];
  lookalike_groups?: LookalikeGroup[];
  known_issues?: KnownIssues;
  /**
   * Optional; empty until a licensed used-price source exists (T-056).
   */
  used_prices?: UsedPriceBand[];
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Taxonomy".
 */
export interface Taxonomy {
  voltage_classes: VoltageClass[];
  chemistries: Chemistry[];
  cooling_types: CoolingType[];
  glossary_terms: GlossaryTerm[];
  bidi_modes?: BidiMode[];
  bidi_routes?: BidiRoute[];
  bidi_protocols?: BidiProtocol[];
  bidi_caveats?: BidiCaveat[];
  bidi_status?: BidiStatus[];
  connector_types?: ConnectorType[];
  bidi_equipment?: BidiEquipment[];
  charging_metrics?: ChargingMetric[];
  charging_definitions?: ChargingDefinition[];
  power_bands?: PowerBand[];
  road_classes?: RoadClass[];
  speed_profiles?: SpeedProfile[];
  temperature_bands?: TemperatureBand[];
  heater_types?: HeaterType[];
  usage_profiles?: UsageProfile[];
  finance_profiles?: FinanceProfile[];
  clue_types?: ClueType[];
}
/**
 * Row in data/taxonomy/voltage_classes.yaml. Data, not an enum: add a row, no code change.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "VoltageClass".
 */
export interface VoltageClass {
  id: Id;
  /**
   * Display label. Keyed by language (en, nl, de, fr, es, it); en required.
   */
  label: {
    [k: string]: string;
  };
  min_v: number;
  max_v: number;
  status: TaxonomyStatus;
  /**
   * Plain-language explainer. Keyed by language (en, nl, de, fr, es, it); en required.
   */
  explainer?: {
    [k: string]: string;
  };
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Chemistry".
 */
export interface Chemistry {
  id: Id;
  family: string;
  /**
   * Display label. Keyed by language (en, nl, de, fr, es, it); en required.
   */
  label: {
    [k: string]: string;
  };
  status: TaxonomyStatus;
  /**
   * Items: One pro. Keyed by language (en, nl, de, fr, es, it); en required.
   */
  pros?: {
    [k: string]: string;
  }[];
  /**
   * Items: One con. Keyed by language (en, nl, de, fr, es, it); en required.
   */
  cons?: {
    [k: string]: string;
  }[];
  /**
   * Items: One tip. Keyed by language (en, nl, de, fr, es, it); en required.
   */
  care_tips?: {
    [k: string]: string;
  }[];
  /**
   * true = maker guidance allows charging to 100% daily (typical for LFP). null = unclear.
   */
  charge_100_daily: boolean | null;
  /**
   * First year in a series-production passenger EV.
   */
  first_year?: number | null;
  /**
   * Plain-language explainer. Keyed by language (en, nl, de, fr, es, it); en required.
   */
  explainer?: {
    [k: string]: string;
  };
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "CoolingType".
 */
export interface CoolingType {
  id: Id;
  /**
   * Display label. Keyed by language (en, nl, de, fr, es, it); en required.
   */
  label: {
    [k: string]: string;
  };
  /**
   * Plain-language explainer. Keyed by language (en, nl, de, fr, es, it); en required.
   */
  explainer?: {
    [k: string]: string;
  };
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "GlossaryTerm".
 */
export interface GlossaryTerm {
  id: Id;
  /**
   * Plain-language label. Keyed by language (en, nl, de, fr, es, it); en required.
   */
  label: {
    [k: string]: string;
  };
  /**
   * Technical name shown under the plain label. Keyed by language (en, nl, de, fr, es, it); en required.
   */
  technical?: {
    [k: string]: string;
  };
  /**
   * Tooltip text, at most 20 words. Keyed by language (en, nl, de, fr, es, it); en required.
   */
  short: {
    [k: string]: string;
  };
  /**
   * Learn-page text. Keyed by language (en, nl, de, fr, es, it); en required.
   */
  long?: {
    [k: string]: string;
  };
  /**
   * Extra detail for Nerd mode. Keyed by language (en, nl, de, fr, es, it); en required.
   */
  nerd_note?: {
    [k: string]: string;
  };
  related?: Id[];
}
/**
 * Row in data/taxonomy/bidi_modes.yaml (v2l, v2h, v2g, v2b). Decision 011.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "BidiMode".
 */
export interface BidiMode {
  id: Id;
  label: LocalizedText;
  technical?: LocalizedText1;
  short?: LocalizedText2;
  explainer?: LocalizedText3;
  /**
   * Display order.
   */
  order?: number;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  glossary_id?: string;
}
/**
 * Plain-language label.
 */
export interface LocalizedText {
  [k: string]: string;
}
/**
 * Technical name shown under the plain label.
 */
export interface LocalizedText1 {
  [k: string]: string;
}
/**
 * Tooltip text, at most 20 words.
 */
export interface LocalizedText2 {
  [k: string]: string;
}
/**
 * Plain-language explainer for /learn and Detailed mode.
 */
export interface LocalizedText3 {
  [k: string]: string;
}
/**
 * Row in data/taxonomy/bidi_routes.yaml (ac-onboard, dc-offboard, chademo-dc, proprietary).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "BidiRoute".
 */
export interface BidiRoute {
  id: Id;
  label: LocalizedText4;
  technical?: LocalizedText5;
  short?: LocalizedText6;
  explainer?: LocalizedText7;
  /**
   * Where the inverter sits; decides the home box price (R-01 §3).
   */
  inverter_location?: "car" | "wallbox" | "varies";
  /**
   * true = needs a bidirectional box beyond a normal wallbox.
   */
  needs_special_box?: boolean | null;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  glossary_id?: string;
}
/**
 * Plain-language label.
 */
export interface LocalizedText4 {
  [k: string]: string;
}
/**
 * Technical name shown under the plain label.
 */
export interface LocalizedText5 {
  [k: string]: string;
}
/**
 * Tooltip text, at most 20 words.
 */
export interface LocalizedText6 {
  [k: string]: string;
}
/**
 * Plain-language explainer for /learn and Detailed mode.
 */
export interface LocalizedText7 {
  [k: string]: string;
}
/**
 * Row in data/taxonomy/bidi_protocols.yaml (iso15118-20, iso15118-2-ext, chademo, proprietary, not-disclosed).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "BidiProtocol".
 */
export interface BidiProtocol {
  id: Id;
  label: LocalizedText8;
  technical?: LocalizedText9;
  short?: LocalizedText10;
  explainer?: LocalizedText11;
  /**
   * Formal standard name, e.g. 'EN ISO 15118-20:2022'. Nerd mode.
   */
  standard?: string;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  glossary_id?: string;
}
/**
 * Plain-language label.
 */
export interface LocalizedText8 {
  [k: string]: string;
}
/**
 * Technical name shown under the plain label.
 */
export interface LocalizedText9 {
  [k: string]: string;
}
/**
 * Tooltip text, at most 20 words.
 */
export interface LocalizedText10 {
  [k: string]: string;
}
/**
 * Plain-language explainer for /learn and Detailed mode.
 */
export interface LocalizedText11 {
  [k: string]: string;
}
/**
 * Row in data/taxonomy/bidi_caveats.yaml. The UI shows caveats only from this table, never free text. label/short may contain '{param}', filled from BidiCaveatRef.param.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "BidiCaveat".
 */
export interface BidiCaveat {
  id: Id;
  label: LocalizedText12;
  technical?: LocalizedText13;
  short: LocalizedText14;
  explainer?: LocalizedText15;
  /**
   * Type of the optional parameter a capability row may pass.
   */
  param_kind?: "none" | "number" | "date" | "version";
  /**
   * Metric unit of a number param, e.g. kWh.
   */
  param_unit?: string;
  /**
   * condition = shown as an eligibility condition, never a plain tick.
   */
  severity?: "info" | "condition" | "blocker";
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  glossary_id?: string;
}
/**
 * Plain-language label.
 */
export interface LocalizedText12 {
  [k: string]: string;
}
/**
 * Technical name shown under the plain label.
 */
export interface LocalizedText13 {
  [k: string]: string;
}
/**
 * Tooltip text, at most 20 words.
 */
export interface LocalizedText14 {
  [k: string]: string;
}
/**
 * Plain-language explainer for /learn and Detailed mode.
 */
export interface LocalizedText15 {
  [k: string]: string;
}
/**
 * Row in data/taxonomy/bidi_status.yaml (live, pilot, announced, hardware-ready-not-enabled, not-offered, not-disclosed).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "BidiStatus".
 */
export interface BidiStatus {
  id: Id;
  label: LocalizedText16;
  technical?: LocalizedText17;
  short?: LocalizedText18;
  explainer?: LocalizedText19;
  /**
   * live matches the default filter; pilot-or-announced only with 'Include pilots and announced'.
   */
  filter_group?: "live" | "pilot-or-announced" | "not-available";
  order?: number;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  glossary_id?: string;
}
/**
 * Plain-language label.
 */
export interface LocalizedText16 {
  [k: string]: string;
}
/**
 * Technical name shown under the plain label.
 */
export interface LocalizedText17 {
  [k: string]: string;
}
/**
 * Tooltip text, at most 20 words.
 */
export interface LocalizedText18 {
  [k: string]: string;
}
/**
 * Plain-language explainer for /learn and Detailed mode.
 */
export interface LocalizedText19 {
  [k: string]: string;
}
/**
 * Row in data/taxonomy/connector_types.yaml (type1-j1772, type2, ccs1, ccs2, nacs-j3400, chademo, tesla-eu-legacy, gbt-ac, gbt-dc).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ConnectorType".
 */
export interface ConnectorType {
  id: Id;
  label: LocalizedText20;
  technical?: LocalizedText21;
  short?: LocalizedText22;
  explainer?: LocalizedText23;
  /**
   * What the plug carries.
   *
   * @minItems 1
   */
  current?: ["ac" | "dc", ...("ac" | "dc")[]];
  /**
   * e.g. 'SAE J3400', 'IEC 62196-3'.
   */
  standard?: string;
  /**
   * Where it is common, e.g. 'EU', 'US', 'JP' (display hint, not a rule).
   */
  regions?: string[];
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  glossary_id?: string;
}
/**
 * Plain-language label.
 */
export interface LocalizedText20 {
  [k: string]: string;
}
/**
 * Technical name shown under the plain label.
 */
export interface LocalizedText21 {
  [k: string]: string;
}
/**
 * Tooltip text, at most 20 words.
 */
export interface LocalizedText22 {
  [k: string]: string;
}
/**
 * Plain-language explainer for /learn and Detailed mode.
 */
export interface LocalizedText23 {
  [k: string]: string;
}
/**
 * Row in data/taxonomy/bidi_equipment.yaml: an approved bidirectional box. New boxes are new rows.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "BidiEquipment".
 */
export interface BidiEquipment {
  id: Id;
  name: string;
  maker: string;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  route_id: string;
  current?: "ac" | "dc";
  max_kw?: number | "not-disclosed";
  /**
   * bidi_modes ids it supports.
   */
  mode_ids?: Id[];
  /**
   * bidi_protocols ids it supports.
   */
  protocol_ids?: Id[];
  price_band?: PriceBandEur | "not-disclosed";
  markets?: CountryCode[];
  compatible_platform_ids?: Id[];
  compatible_variant_ids?: Id[];
  url?: string;
  /**
   * Ids of rows in the catalogue sources list.
   *
   * @minItems 1
   */
  source_ids: [Id, ...Id[]];
  retrieved_at?: string;
  notes?: string;
}
/**
 * Price band in euros (converted at display time). Euros internally (AGENTS.md units).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "PriceBandEur".
 */
export interface PriceBandEur {
  min: number;
  max?: number | null;
  as_of?: string;
  /**
   * e.g. list vs intro price, original currency.
   */
  note?: string;
}
/**
 * Row in data/taxonomy/charging_metrics.yaml (public-points, public-points-dc, installed-kw, evs-per-point, ...). Decision 012.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ChargingMetric".
 */
export interface ChargingMetric {
  id: Id;
  label: LocalizedText24;
  technical?: LocalizedText25;
  short?: LocalizedText26;
  explainer?: LocalizedText27;
  /**
   * Metric unit: count, kW, %, per 100k people, EVs per point, kW per EV.
   */
  unit: string;
  /**
   * false for evs-per-point; null = neutral.
   */
  higher_is_better?: boolean | null;
  /**
   * true when we compute it (ratios) rather than read it from a source.
   */
  derived?: boolean;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  glossary_id?: string;
}
/**
 * Plain-language label.
 */
export interface LocalizedText24 {
  [k: string]: string;
}
/**
 * Technical name shown under the plain label.
 */
export interface LocalizedText25 {
  [k: string]: string;
}
/**
 * Tooltip text, at most 20 words.
 */
export interface LocalizedText26 {
  [k: string]: string;
}
/**
 * Plain-language explainer for /learn and Detailed mode.
 */
export interface LocalizedText27 {
  [k: string]: string;
}
/**
 * Row in data/taxonomy/charging_definitions.yaml: how one source counts (afir-recharging-point, uk-dft-evse-2026, ...). A chart draws one definition; a new definition starts a new series with a marked break.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ChargingDefinition".
 */
export interface ChargingDefinition {
  id: Id;
  label: LocalizedText28;
  technical?: LocalizedText29;
  short?: LocalizedText30;
  explainer?: LocalizedText31;
  /**
   * Unit counted: a point is not a device is not a location is not a connector.
   */
  counts: "point" | "device" | "location" | "connector" | "port";
  country?: ChargingArea;
  source_id: Id;
  /**
   * Supermarket / car-park points etc.
   */
  includes_semi_public?: boolean | null;
  fast_label?: LocalizedText32;
  valid_from?: string;
  valid_to?: string | null;
  /**
   * Definition that continues the series after a break.
   */
  replaced_by?: Id | null;
  /**
   * true only for EAFO / IEA definitions.
   */
  comparable_across_countries?: boolean;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  glossary_id?: string;
}
/**
 * Plain-language label.
 */
export interface LocalizedText28 {
  [k: string]: string;
}
/**
 * Technical name shown under the plain label.
 */
export interface LocalizedText29 {
  [k: string]: string;
}
/**
 * Tooltip text, at most 20 words.
 */
export interface LocalizedText30 {
  [k: string]: string;
}
/**
 * Plain-language explainer for /learn and Detailed mode.
 */
export interface LocalizedText31 {
  [k: string]: string;
}
/**
 * The source's own word for 'fast' (Nerd mode), e.g. 'Schnellladepunkt (>22 kW)'.
 */
export interface LocalizedText32 {
  [k: string]: string;
}
/**
 * Row in data/taxonomy/power_bands.yaml. Our bands (AC <22 kW, AC 22 kW, DC 50-149, DC 150-349, DC 350+) plus each source's own bands, mapped to ours with maps_to.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "PowerBand".
 */
export interface PowerBand {
  id: Id;
  label: LocalizedText33;
  technical?: LocalizedText34;
  short?: LocalizedText35;
  explainer?: LocalizedText36;
  current: "ac" | "dc" | "any";
  /**
   * Inclusive lower bound.
   */
  min_kw: number;
  /**
   * Exclusive upper bound; null = open-ended.
   */
  max_kw?: number | null;
  /**
   * true = one of our display bands.
   */
  ours?: boolean;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  source_id?: string;
  /**
   * Our band ids this source band falls into (one when it maps cleanly).
   */
  maps_to?: Id[];
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  glossary_id?: string;
}
/**
 * Plain-language label.
 */
export interface LocalizedText33 {
  [k: string]: string;
}
/**
 * Technical name shown under the plain label.
 */
export interface LocalizedText34 {
  [k: string]: string;
}
/**
 * Tooltip text, at most 20 words.
 */
export interface LocalizedText35 {
  [k: string]: string;
}
/**
 * Plain-language explainer for /learn and Detailed mode.
 */
export interface LocalizedText36 {
  [k: string]: string;
}
/**
 * Row in data/taxonomy/road_classes.yaml: OSM highway tags → road band.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "RoadClass".
 */
export interface RoadClass {
  id: Id;
  label: LocalizedText37;
  explainer?: LocalizedText38;
  band: RoadBand;
  /**
   * OSM highway=* values, e.g. motorway, trunk, residential.
   */
  osm_highway?: string[];
  /**
   * Typical limit when the way has no maxspeed tag.
   */
  max_speed_kmh?: number | null;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  glossary_id?: string;
}
/**
 * Plain-language label.
 */
export interface LocalizedText37 {
  [k: string]: string;
}
/**
 * Plain-language explainer for /learn and Detailed mode.
 */
export interface LocalizedText38 {
  [k: string]: string;
}
/**
 * Row in data/taxonomy/speed_profiles.yaml: typical speeds per road band for one country (NL 100 by day, FR 130, DE advisory 130, UK 70 mph).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "SpeedProfile".
 */
export interface SpeedProfile {
  id: Id;
  label?: LocalizedText39;
  explainer?: LocalizedText40;
  country: CountryCode;
  speeds_kmh: BandSpeeds;
  /**
   * Offset applied per driving style; spec default -10 / 0 / +10.
   */
  style_offset_kmh?: {
    slower?: number;
    at_limit?: number;
    faster?: number;
  };
  source_ids?: Id[];
  valid_from?: string;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  glossary_id?: string;
}
/**
 * Plain-language label.
 */
export interface LocalizedText39 {
  [k: string]: string;
}
/**
 * Plain-language explainer for /learn and Detailed mode.
 */
export interface LocalizedText40 {
  [k: string]: string;
}
/**
 * Typical driving speed per road band, km/h.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "BandSpeeds".
 */
export interface BandSpeeds {
  town: number;
  rural: number;
  motorway: number;
}
/**
 * Row in data/taxonomy/temperature_bands.yaml: one of the matrix temperature columns (5 at launch).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "TemperatureBand".
 */
export interface TemperatureBand {
  id: Id;
  label: LocalizedText41;
  short?: LocalizedText42;
  /**
   * Inclusive; null = open-ended.
   */
  min_c?: number | null;
  /**
   * Exclusive; null = open-ended.
   */
  max_c?: number | null;
  /**
   * Temperature the matrix cell is computed at.
   */
  representative_c: number;
  order?: number;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  glossary_id?: string;
}
/**
 * Plain-language label.
 */
export interface LocalizedText41 {
  [k: string]: string;
}
/**
 * Tooltip text, at most 20 words.
 */
export interface LocalizedText42 {
  [k: string]: string;
}
/**
 * Row in data/taxonomy/heater_types.yaml (heat-pump, resistive, unknown) with its default temperature curve.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "HeaterType".
 */
export interface HeaterType {
  id: Id;
  label: LocalizedText43;
  short?: LocalizedText44;
  explainer?: LocalizedText45;
  /**
   * (ambient °C, consumption factor vs 20 °C) points; a car's own winter test replaces it.
   */
  temperature_curve?: [unknown, unknown][];
  /**
   * Energy per cold start (cabin + battery); dropped when preheated on the plug.
   */
  warm_up_kwh?: number | null;
  source_ids?: Id[];
  confidence?: Confidence;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  glossary_id?: string;
}
/**
 * Plain-language label.
 */
export interface LocalizedText43 {
  [k: string]: string;
}
/**
 * Tooltip text, at most 20 words.
 */
export interface LocalizedText44 {
  [k: string]: string;
}
/**
 * Plain-language explainer for /learn and Detailed mode.
 */
export interface LocalizedText45 {
  [k: string]: string;
}
/**
 * Row in data/taxonomy/usage_profiles.yaml and in shortlist_rules.yaml profiles / addons: one profile type for Trip fit (weights, trip-fit §6) and the shortlist (gates, factors, bands, Decision 038). A new row, not new code. kind addon = ticked extra on top of a base profile.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "UsageProfile".
 */
export interface UsageProfile {
  id: Id;
  /**
   * Older ids that still resolve to this row (URLs, saved profiles).
   */
  aliases?: Id[];
  label: LocalizedText46;
  short?: LocalizedText47;
  kind?: "base" | "addon";
  /**
   * Picker answers that select this profile: question id → accepted answer ids.
   */
  applies_when?: {
    [k: string]: string[];
  };
  /**
   * shortlist_rules.yaml spelling of applies_when (same meaning). New rows: use applies_when.
   */
  picker?: {
    [k: string]: string[];
  };
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  matches_usage_profile?: string;
  /**
   * Overlay profile (e.g. kerbside-charger): applied on top of these base profiles.
   */
  combines_with?: Id[];
  /**
   * Factor → weight (price, efficiency, dc_km_20min_winter, winter_1000km_time, ac_speed, battery_risk ...).
   */
  weights?: {
    [k: string]: WeightLevel;
  };
  /**
   * Add-ons, modifiers and overlays: factor id → steps up (+) or down (-), e.g. battery-health-risk +1. One step = × weight_step_factor, then renormalised.
   */
  weight_steps?: {
    [k: string]: number;
  };
  bands?: ShortlistBands;
  gates?: ShortlistGate[];
  factors?: ShortlistFactor[];
  /**
   * Overlays and add-ons: factors added to the base profile's.
   */
  extra_factors?: ShortlistFactor[];
  bonuses?: ShortlistAdjustment[];
  penalties?: ShortlistAdjustment[];
  filter_presets?: FilterPreset[];
  /**
   * Soft preference: PublishedVariant field → preferred values (sorts up, never filters).
   */
  prefer?: {
    [k: string]: (string | number | boolean)[];
  };
  /**
   * Default Explore sort for this profile, e.g. price_used_asc.
   */
  sort_default?: string;
  /**
   * What the owner cares about but is deliberately not scored.
   */
  not_rules?: string[];
  /**
   * How the thresholds were checked (back-test, research).
   */
  calibration?: string;
  origin?: string;
  why_a_profile?: string;
  notes?: string;
  status?: ShortlistRuleStatus;
  order?: number;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  glossary_id?: string;
}
/**
 * Plain-language label.
 */
export interface LocalizedText46 {
  [k: string]: string;
}
/**
 * Tooltip text, at most 20 words.
 */
export interface LocalizedText47 {
  [k: string]: string;
}
/**
 * Voltage class id (voltage_classes) or 'default' → thresholds. 'default' is used when the car's class has no row.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ShortlistBands".
 */
export interface ShortlistBands {
  [k: string]: ShortlistBandThresholds;
}
/**
 * Score 0..100 at or above which a car is 'shortlist' / 'consider'; below = fallback.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ShortlistBandThresholds".
 */
export interface ShortlistBandThresholds {
  shortlist: number;
  consider: number;
}
/**
 * Hard rule: a known value under the floor rules the car out with `reason`. Unknown values pass and are listed as unknown.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ShortlistGate".
 */
export interface ShortlistGate {
  id: Id;
  /**
   * PublishedVariant field(s) the app reads.
   */
  field: string | [string, ...string[]];
  /**
   * Owner-sheet column used by the back-test only (internal).
   */
  sheet_field?: string | [string, ...string[]];
  min?: number;
  max?: number;
  min_km?: number;
  /**
   * Floor used instead of min_km with the rural modifier.
   */
  rural_min_km?: number;
  min_km_per_h?: number;
  status?: ShortlistRuleStatus;
  reason?: LocalizedText48;
  /**
   * Why the rule exists (owner picks, research).
   */
  evidence?: string;
}
/**
 * Plain words shown to users when the gate fails.
 */
export interface LocalizedText48 {
  [k: string]: string;
}
/**
 * Scored factor: value mapped linearly onto 0..1 between `poor` and `great` (clamped; poor > great means lower is better), times weight. Categorical fields (one_pedal, bidi, heat_pump, cooling_id) map by the scoring job's table and have no poor/great.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ShortlistFactor".
 */
export interface ShortlistFactor {
  id: Id;
  label?: LocalizedText49;
  /**
   * PublishedVariant field(s) the app reads.
   */
  field: string | [string, ...string[]];
  /**
   * Owner-sheet column used by the back-test only (internal).
   */
  sheet_field?: string | [string, ...string[]];
  poor?: number;
  great?: number;
  weight: number;
  status?: ShortlistRuleStatus;
  note?: string;
  evidence?: string;
}
/**
 * Text keyed by language (en, nl, de, fr, es, it); en required.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "LocalizedText".
 */
export interface LocalizedText49 {
  [k: string]: string;
}
/**
 * Bonus (points > 0) or penalty (points < 0) with a plain-language rule.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ShortlistAdjustment".
 */
export interface ShortlistAdjustment {
  id: Id;
  points: number;
  rule?: string;
  field?: string | [string, ...string[]];
  /**
   * Internal, back-test only.
   */
  sheet_field?: string | [string, ...string[]];
  /**
   * Internal, back-test only.
   */
  sheet_rule?: string;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  applies_with?: string;
  status?: ShortlistRuleStatus;
  evidence?: string;
}
/**
 * Explore filter a profile preselects, shown as a removable chip 'Set by your profile' (Decision 050).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "FilterPreset".
 */
export interface FilterPreset {
  field: string;
  min?: number;
  max?: number;
  equals?: string | number | boolean;
  why?: LocalizedText49;
}
/**
 * Row in data/taxonomy/finance_profiles.yaml: typical finance terms per country and product, read by the price-mode calculator (Decision 017). null = no citable figure; the calculator asks the user instead of guessing.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "FinanceProfile".
 */
export interface FinanceProfile {
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  id: string;
  country: CountryCode;
  product: FinanceProduct;
  /**
   * Typical annual percentage rate of charge, in percent (8.91 = 8.91 %). null = no citable source; the calculator asks for a rate.
   */
  typical_apr: number | null;
  /**
   * Sourced typical term; null = no source, the calculator uses its own labelled default.
   */
  default_term_months: number | null;
  /**
   * Sourced typical deposit as percent of the price; null = no source.
   */
  default_deposit_pct: number | null;
  /**
   * Required (not null) whenever typical_apr has a value.
   */
  source: FinanceSource | null;
  /**
   * When the source was read. Required (not null) whenever typical_apr has a value.
   */
  retrieved_at: string | null;
  /**
   * Staff notes: caveats, why a value is null, what the figure does and does not cover.
   */
  notes?: string;
  /**
   * true = entered by an agent or not yet checked by a person; goes to the review queue.
   */
  review: boolean;
}
/**
 * Where a FinanceProfile figure comes from. Central-bank statistics only for typical_apr (Decision 017).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "FinanceSource".
 */
export interface FinanceSource {
  /**
   * Publisher and dataset, e.g. 'ECB Data Portal, MFI interest rate statistics'.
   */
  name: string;
  url: string;
  /**
   * Reuse terms as stated by the publisher; '(to confirm)' if not checked.
   */
  licence?: string;
  /**
   * The publisher's series key, e.g. 'MIR.M.DE.B.A2B.A.C.A.2250.EUR.N'.
   */
  series_id?: string;
  /**
   * The publisher's own title for the series (Nerd mode).
   */
  series_title?: string;
  /**
   * Observation period of the figure: YYYY, YYYY-MM or YYYY-MM-DD.
   */
  period?: string;
}
/**
 * Row in data/taxonomy/clue_types.yaml (build-date-range, power-kw, battery-kwh, trim-name, type-approval-code, vin-position, visible-feature, onboard-charger, ...). Decision 019, variant finder spec §3-4. A new clue type is a new row, no code change; clue_type_id values are checked against this table at release time (Decision 010 pattern).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ClueType".
 */
export interface ClueType {
  id: Id;
  label: LocalizedText50;
  technical?: LocalizedText51;
  short: LocalizedText52;
  explainer?: LocalizedText53;
  value_kind: ClueValueKind;
  /**
   * Metric unit for number values (kW, kWh, in for rim size code); absent for text, code and date values.
   */
  unit?: string;
  /**
   * Where a buyer can read it, most useful first.
   *
   * @minItems 1
   */
  found_in: [ClueFoundIn, ...ClueFoundIn[]];
  /**
   * Country → field on that country's registration papers or open registration data, e.g. FR 'P.2', NL 'vermogen (RDW)'. Absent country = not on the papers there or not checked.
   */
  paper_fields?: {
    [k: string]: string;
  };
  ask_seller?: LocalizedText54;
  /**
   * Typical strength of this clue type; each VariantClue still states its own.
   */
  default_strength?: "decisive" | "strong" | "weak";
  /**
   * Display order in the 'spot it in an ad' box.
   */
  order?: number;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  glossary_id?: string;
}
/**
 * Text keyed by language (en, nl, de, fr, es, it); en required.
 */
export interface LocalizedText50 {
  [k: string]: string;
}
/**
 * Text keyed by language (en, nl, de, fr, es, it); en required.
 */
export interface LocalizedText51 {
  [k: string]: string;
}
/**
 * Text keyed by language (en, nl, de, fr, es, it); en required.
 */
export interface LocalizedText52 {
  [k: string]: string;
}
/**
 * Text keyed by language (en, nl, de, fr, es, it); en required.
 */
export interface LocalizedText53 {
  [k: string]: string;
}
/**
 * Text keyed by language (en, nl, de, fr, es, it); en required.
 */
export interface LocalizedText54 {
  [k: string]: string;
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Platform".
 */
export interface Platform {
  id: Id;
  name: string;
  /**
   * Group that owns the platform, e.g. Volkswagen Group.
   */
  owner?: string;
  nominal_v?: number | "not-disclosed";
  voltage_class_id?: Id | "not-disclosed";
  notes?: string;
}
/**
 * A battery pack shared by one or more variants. Variants inherit its facts unless they have their own measured fact.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "BatteryPack".
 */
export interface BatteryPack {
  id: Id;
  name: string;
  supplier?: string;
  chemistry_id?: Id | "not-disclosed";
  /**
   * e.g. NMC811, NMC622.
   */
  cathode_detail?: string;
  cell_format?: "pouch" | "prismatic" | "cylindrical" | "blade" | "not-disclosed";
  cell_to_pack?: boolean | null;
  gross_kwh?: number | "not-disclosed";
  usable_kwh?: number | "not-disclosed";
  nominal_v?: number | "not-disclosed";
  max_v?: number | "not-disclosed";
  cooling_id?: Id | "not-disclosed";
  warranty?: Warranty | "not-disclosed";
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Warranty".
 */
export interface Warranty {
  years?: number;
  km?: number;
  min_soh_pct?: number;
}
/**
 * One fact a buyer can read in an ad, on the registration papers or on the car that points to this variant (Decision 019, variant finder spec §3-4). Set exactly one of value or range (checked at release time, together with the value shape against the clue type's value_kind). The same rows feed listing matching later (spec §8).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "VariantClue".
 */
export interface VariantClue {
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  id: string;
  variant_id: Id;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  clue_type_id: string;
  /**
   * Country where the clue holds (trim names, paper fields), or 'global'.
   */
  market: CountryCode | "global";
  /**
   * Single value for number / text / code / boolean clue types. Trim names are stored as written in that market, never translated.
   */
  value?: number | string | boolean;
  range?: ClueRange;
  /**
   * Metric unit when value or range is a number; must match the clue type's unit.
   */
  unit?: string;
  /**
   * Character position (1-based) for VIN-position clue types.
   */
  position?: number;
  description?: LocalizedText55;
  strength: ClueStrength;
  /**
   * Variant ids this clue rules out; they must exist and share a look-alike group with variant_id (checked at release time).
   */
  rules_out: Id[];
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  lookalike_group_id?: string;
  /**
   * Evidence; two or more where possible.
   *
   * @minItems 1
   */
  sources: [ClueSourceRef, ...ClueSourceRef[]];
  /**
   * Last date a source confirmed the clue.
   */
  retrieved_at: string;
  confidence: Confidence;
  entered_by?: "pipeline" | "staff";
  /**
   * Facts the clue is derived from, if any (e.g. the power_kw fact).
   */
  fact_ids?: string[];
  /**
   * Internal note; never shown.
   */
  notes?: string;
}
/**
 * For number-range and date-range clue types.
 */
export interface ClueRange {
  /**
   * Lower bound (inclusive); null = open.
   */
  min: number | string | null;
  /**
   * Upper bound (inclusive); null = open (e.g. still built).
   */
  max: number | string | null;
}
/**
 * Text keyed by language (en, nl, de, fr, es, it); en required.
 */
export interface LocalizedText55 {
  [k: string]: string;
}
/**
 * One piece of evidence for a clue: a row in the catalogue sources list plus the exact page where the clue was read.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ClueSourceRef".
 */
export interface ClueSourceRef {
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  source_id: string;
  /**
   * Exact page (maker brochure, press release, registration-data docs). Required for staff-entered clues (checked at release time).
   */
  url?: string;
  /**
   * Where on the page or in the document, e.g. 'p. 12, technical data table'. No copied tables.
   */
  locator?: string;
  /**
   * Pointer to a raw record, for pipeline-derived clues.
   */
  source_record?: string;
  retrieved_at: string;
}
/**
 * Variants that buyers confuse (Decision 019, variant finder spec §4). Built automatically from overlapping specs; staff overrides in data/manual.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "LookalikeGroup".
 */
export interface LookalikeGroup {
  id: Id;
  /**
   * @minItems 2
   */
  variant_ids: [Id, Id, ...Id[]];
  reason: LookalikeReason;
  /**
   * staff = created or edited by hand; the pipeline keeps it as written.
   */
  built_by: "pipeline" | "staff";
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  generation_id?: string;
  /**
   * Markets where the confusion applies (same-marketing-name); absent = everywhere.
   */
  markets?: CountryCode[];
  label?: LocalizedText56;
  built_at?: string;
  /**
   * Internal note; never shown.
   */
  notes?: string;
}
/**
 * Text keyed by language (en, nl, de, fr, es, it); en required.
 */
export interface LocalizedText56 {
  [k: string]: string;
}
/**
 * Optional 'Known issues' section from RDW APK defect data (T-059): aggregates per generation x first-registration year, never per car.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "KnownIssues".
 */
export interface KnownIssues {
  country: Country;
  source_id: Id;
  retrieved_at: string;
  confidence: Confidence;
  inspection?: string;
  reported_from?: string;
  reported_to?: string;
  sample_rule?: string;
  /**
   * What the per-100 rates are per (plain sentence).
   */
  rate_basis: string;
  min_sample_cars?: number;
  min_cars_per_code?: number;
  top_n?: number;
  codes: KnownIssueCode[];
  /**
   * Generation id -> cohorts, oldest first-registration year first.
   */
  by_generation: {
    /**
     * @minItems 1
     */
    [k: string]: [KnownIssueCohort, ...KnownIssueCohort[]];
  };
}
/**
 * An RDW APK defect code with RDW's own Dutch label (dataset hx2c-gt7k). RDW publishes no English label.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "KnownIssueCode".
 */
export interface KnownIssueCode {
  code: string;
  label_nl: string;
  /**
   * RDW article number (gebrek_artikel_nummer).
   */
  article?: string;
}
/**
 * APK defects for one generation and one first-registration year. Compare only with cohorts of the same first-registration year (Q-078).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "KnownIssueCohort".
 */
export interface KnownIssueCohort {
  first_registration_year: number;
  /**
   * Fetch year minus first-registration year.
   */
  age_years: number;
  age_band: string;
  sample_cars: number;
  cars_with_any_defect: number;
  any_defect_per_100: number;
  /**
   * Too few defect reports to read anything into (young cohort or small counts): hide by default.
   */
  few_reports: boolean;
  cohort: {
    /**
     * Generations in the catalogue with a cohort this year.
     */
    generations: number;
    /**
     * All sampled BEVs of this first-registration year (every make).
     */
    sample_cars: number;
    any_defect_per_100: number;
  };
  defects: KnownIssueDefect[];
  source_records?: string[];
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "KnownIssueDefect".
 */
export interface KnownIssueDefect {
  code: string;
  cars_with_defect: number;
  /**
   * Sampled cars with this defect per 100 sampled cars of this generation and first-registration year.
   */
  per_100: number;
  /**
   * The same rate over all sampled BEVs of the same first-registration year (the comparison baseline).
   */
  cohort_per_100: number;
}
/**
 * Typical used asking-price band for a generation in one country. Only from sourced samples; shown only with >= 5 samples.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "UsedPriceBand".
 */
export interface UsedPriceBand {
  generation_id: Id;
  country: CountryCode;
  currency: Currency;
  p25?: number | null;
  median: number;
  p75?: number | null;
  samples: number;
  period: string;
  age_band_years?: string | null;
  source_id: Id;
  fact_ids?: string[];
}
/**
 * One aggregate number per country (or region), date, metric and power band. Never point-level data. Decision 012.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ChargingStat".
 */
export interface ChargingStat {
  id: string;
  country: ChargingArea;
  /**
   * Sub-national region (e.g. a German state), null = whole country.
   */
  region?: string | null;
  /**
   * As-of date of the figure.
   */
  period_end: string;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  metric_id: string;
  /**
   * power_bands id; null = all bands.
   */
  power_band_id?: Id | null;
  value: number;
  unit: string;
  source_id: Id;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  definition_id: string;
  confidence: Confidence;
  entered_by: "pipeline" | "staff";
  /**
   * Required when entered_by = staff (data/manual/charging/*.yaml).
   */
  source_url?: string;
  source_record?: string;
  /**
   * The source's own label for the figure (Nerd mode).
   */
  source_label?: string;
  retrieved_at: string;
  notes?: string;
}
/**
 * Row in config: the 'Find a charger / plan a trip' link-out block. Pure links, no API calls. Decision 012.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "CountryChargingLink".
 */
export interface CountryChargingLink {
  /**
   * ALL = pan-European / global tool shown everywhere.
   */
  country: CountryCode | "ALL";
  /**
   * Tool name, e.g. 'Chargemap'.
   */
  tool: string;
  url: string;
  job: "official-map" | "local-app" | "map" | "route-planner" | "price-compare";
  order: number;
  label?: LocalizedText57;
  /**
   * URL template with {placeholders}, e.g. ABRP car model; null = plain link.
   */
  deep_link_template?: string | null;
}
/**
 * Text keyed by language (en, nl, de, fr, es, it); en required.
 */
export interface LocalizedText57 {
  [k: string]: string;
}
/**
 * One condition-tagged consumption measurement (Bjørn Nyland 90/120 km/h, ADAC, NAF El Prix ...). Input to ConsumptionModel.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ConsumptionTest".
 */
export interface ConsumptionTest {
  id: string;
  variant_id: Id;
  /**
   * constant-speed = steady speed run; route = mixed real route; cycle = lab cycle.
   */
  test_kind: "constant-speed" | "route" | "cycle" | "owner-data";
  /**
   * Constant speed, or average speed for a route.
   */
  speed_kmh?: number | null;
  /**
   * Band the test represents, if a single one.
   */
  road_band?: RoadBand | null;
  /**
   * Route tests: km per road band.
   */
  band_km?: {
    town?: number;
    rural?: number;
    motorway?: number;
  };
  distance_km?: number | null;
  climb_m?: number | null;
  /**
   * Ambient temperature (average for the test).
   */
  temperature_c: number;
  /**
   * Rim diameter code (ISO/ETRTO designation, inches by convention).
   */
  wheel_size_in?: number | null;
  /**
   * Tyre size, e.g. '235/45 R19'.
   */
  tyre?: string | null;
  tyre_season?: "summer" | "winter" | "all-season" | "not-disclosed";
  consumption_wh_km: number;
  /**
   * battery = from the car's own meter / SoC; wall = includes charging losses.
   */
  energy_basis: "battery" | "wall" | "not-disclosed";
  /**
   * Range result, if the test reports one.
   */
  range_km?: number | null;
  /**
   * Test date.
   */
  observed_at?: string;
  conditions?: {
    preconditioned?: boolean;
    /**
     * e.g. '21 °C auto'.
     */
    hvac?: string;
    heat_pump_fitted?: boolean | null;
    wind?: string;
    precipitation?: "dry" | "wet" | "snow" | "not-disclosed";
    payload_kg?: number;
    battery_soh_pct?: number;
    software_version?: string;
    notes?: string;
  };
  /**
   * Full Source in staging files; a SourceRef inside consumption_matrix.json (the file lists the Sources once).
   */
  source: Source | SourceRef;
  source_record?: string;
  retrieved_at: string;
  confidence: Confidence;
}
/**
 * Pointer to a Source listed elsewhere in the same file (e.g. the file's `sources`).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "SourceRef".
 */
export interface SourceRef {
  id: Id;
}
/**
 * One road band × temperature band cell.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ConsumptionCell".
 */
export interface ConsumptionCell {
  road_band: RoadBand;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  temperature_band_id: string;
  /**
   * Stable id: lowercase, hyphen-separated.
   */
  heater_type_id?: string;
  wh_km: number;
  p10_wh_km?: number;
  p90_wh_km?: number;
  rung: ConsumptionRung;
  confidence: Confidence;
  /**
   * ConsumptionTest ids behind a measured cell.
   */
  test_ids?: string[];
}
/**
 * Derived per-variant consumption matrix (3 road bands × temperature bands), static JSON per release. The browser scores trips with it.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ConsumptionModel".
 */
export interface ConsumptionModel {
  variant_id: Id;
  release: number;
  /**
   * Version of the model code that built it.
   */
  model_version?: string;
  heat_pump?: HeatPumpFitment;
  usable_kwh?: number | null;
  /**
   * Mass used for climb energy.
   */
  mass_kg?: number | null;
  /**
   * Per cold start; overrides the heater_types default.
   */
  warm_up_kwh?: number | null;
  /**
   * Share of climb energy recovered downhill (~0.6).
   */
  regen_recovery?: number | null;
  drivetrain_efficiency?: number | null;
  /**
   * @minItems 1
   */
  cells: [ConsumptionCell, ...ConsumptionCell[]];
  generated_at?: string;
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "MonthlyClimate".
 */
export interface MonthlyClimate {
  month: number;
  /**
   * Mean daily temperature.
   */
  mean_c: number;
  /**
   * Colder 10th-percentile day (cold snap check).
   */
  p10_c?: number | null;
  mean_min_c?: number | null;
}
/**
 * Climate normals for one town or grid cell (Meteostat / ERA5). Town ids from GeoNames (CC BY 4.0).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ClimateNormal".
 */
export interface ClimateNormal {
  id: Id;
  location_kind: "town" | "grid-cell";
  name?: string;
  country?: CountryCode;
  geonames_id?: number | null;
  lat: number;
  lon: number;
  grid_resolution_deg?: number | null;
  elevation_m?: number | null;
  /**
   * Reference period, e.g. '1991-2020'.
   */
  period: string;
  /**
   * @minItems 12
   * @maxItems 12
   */
  months: [
    MonthlyClimate,
    MonthlyClimate,
    MonthlyClimate,
    MonthlyClimate,
    MonthlyClimate,
    MonthlyClimate,
    MonthlyClimate,
    MonthlyClimate,
    MonthlyClimate,
    MonthlyClimate,
    MonthlyClimate,
    MonthlyClimate
  ];
  source_id: Id;
  retrieved_at: string;
}
/**
 * Inclusive range. Numbers for number-range clue types; ISO year-month ('2021-06') or date ('2021-06-14') for date-range types. null = open-ended on that side.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ClueRange".
 */
export interface ClueRange1 {
  /**
   * Lower bound (inclusive); null = open.
   */
  min: number | string | null;
  /**
   * Upper bound (inclusive); null = open (e.g. still built).
   */
  max: number | string | null;
}
/**
 * data/releases/<n>/charging_stats.json: aggregate charging statistics shipped next to the catalogue (Decision 012, T-059).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ChargingStatsRelease".
 */
export interface ChargingStatsRelease {
  release: number;
  generated_at: string;
  sources: Source[];
  /**
   * Stat source_id (taxonomy id) -> data/sources.yaml id (Q-075).
   */
  source_aliases?: {
    [k: string]: Id;
  };
  stats: ChargingStat[];
}
/**
 * Source, date, licence and confidence for a whole block of a release file (data rule 1).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ProvenanceNote".
 */
export interface ProvenanceNote {
  source_id: Id;
  /**
   * ISO date the source was read.
   */
  retrieved_at: string | null;
  licence: string;
  confidence: Confidence;
}
/**
 * ProvenanceNote plus how the station climate figures were made (T-034, Decision 041).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ClimateProvenance".
 */
export interface ClimateProvenance {
  source_id: Id;
  retrieved_at: string | null;
  licence: string;
  confidence: Confidence;
  /**
   * Temperature unit, °C.
   */
  unit?: string;
  /**
   * Reference period, e.g. '1991-2020'.
   */
  period?: string | null;
  method?: string;
  /**
   * Field name → plain-language definition (Nerd mode).
   */
  definitions?: {
    [k: string]: string;
  };
}
/**
 * Climate figures of one weather station, listed once per towns file (T-034).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "WeatherStation".
 */
export interface WeatherStation {
  name?: string | null;
  lat: number;
  lon: number;
  elevation_m?: number | null;
  /**
   * Mean of daily mean temperature per month, Jan..Dec, °C.
   *
   * @minItems 12
   * @maxItems 12
   */
  months_mean_c?:
    | [
        number | null,
        number | null,
        number | null,
        number | null,
        number | null,
        number | null,
        number | null,
        number | null,
        number | null,
        number | null,
        number | null,
        number | null
      ]
    | null;
  jan_mean_c?: number | null;
  /**
   * How jan_mean_c was computed (e.g. 'daily').
   */
  jan_mean_method?: string | null;
  /**
   * 10th percentile of January daily mean temperature, 1991-2020 (Decision 041).
   */
  jan_p10_c?: number | null;
  /**
   * Full Januaries behind the figures.
   */
  jan_years?: number | null;
}
/**
 * One town for the Trip fit town search (GeoNames, CC BY 4.0).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "Town".
 */
export interface Town {
  /**
   * Source-scoped id, e.g. 'geonames:2759794'.
   */
  id: string;
  name: string;
  /**
   * Name per UI language when it differs.
   */
  names?: {
    [k: string]: string;
  };
  /**
   * Lowercase country code as in the file name (uk for the United Kingdom).
   */
  country: string;
  lat: number;
  lon: number;
  population?: number | null;
  /**
   * GeoNames admin1 code (region).
   */
  admin1?: string;
  elevation_m?: number | null;
  /**
   * Key in the file's `stations`; null = no station in range, the app uses its country default.
   */
  station_id: string | null;
  station_km?: number;
}
/**
 * releases/<n>/towns/<cc>.json: towns + January climate for Trip fit, one file per country (T-034).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "TownsRelease".
 */
export interface TownsRelease {
  release: number;
  generated_at: string;
  country: string;
  sources: Source[];
  provenance: {
    towns: ProvenanceNote;
    /**
     * null = climate source gated or missing; towns ship without climate.
     */
    climate: ClimateProvenance | null;
  };
  stations: {
    [k: string]: WeatherStation;
  };
  towns: Town[];
}
/**
 * releases/<n>/consumption_matrix.json: per-variant consumption matrix (T-033). Every cell is a model output.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ConsumptionMatrixRelease".
 */
export interface ConsumptionMatrixRelease {
  release: number;
  generated_at: string;
  model_version: string;
  estimate: true;
  note?: string;
  road_bands?: RoadBand[];
  band_speed_kmh?: BandSpeeds;
  temperature_bands?: TemperatureBand[];
  heater_types?: HeaterType[];
  /**
   * Model parameters (all estimates, pipeline/ev_pipeline/derive/consumption_params.yaml).
   */
  params?: {
    wall_to_battery?: number;
    climb_regen_recovery?: number;
    drivetrain_efficiency?: number;
  };
  sources?: Source[];
  /**
   * Tests behind measured cells; source is a SourceRef into `sources`.
   */
  tests?: ConsumptionTest[];
  variants: ConsumptionModel[];
}
/**
 * One question of the profile picker (4 taps; ids shared with trip-fit §4, Decision 050).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "PickerQuestion".
 */
export interface PickerQuestion {
  id: string;
  question: LocalizedText49;
  /**
   * @minItems 2
   */
  answers: [string, string, ...string[]];
  /**
   * Skip this question when an earlier answer matches.
   */
  skip_if?: {
    [k: string]: string[];
  };
}
/**
 * 'Where you live' modifier (city / town / countryside): changes thresholds and weights of any profile.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ShortlistModifier".
 */
export interface ShortlistModifier {
  id: Id;
  label: LocalizedText49;
  short?: LocalizedText49;
  /**
   * Picker answers that select this row: question id → accepted answer ids.
   */
  picker?: {
    [k: string]: string[];
  };
  /**
   * Factor id → steps up (+) or down (-); one step = × weight_step_factor, then renormalised.
   */
  weight_steps?: {
    [k: string]: number;
  };
  gate_scale?: number;
  /**
   * Gates with rural_min_km use that value.
   */
  use_rural_gates?: boolean;
  penalties?: ShortlistAdjustment[];
  hints?: string[];
}
/**
 * shortlist_rules.yaml: selection rules per profile (Decision 038), modifiers, add-ons and the picker (Decision 050). Rules are rows, not code.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ShortlistRules".
 */
export interface ShortlistRules {
  schema: string;
  derived_from?: string;
  /**
   * true = agent-derived, owner still to confirm thresholds.
   */
  review?: boolean;
  /**
   * @minItems 1
   */
  profiles: [UsageProfile, ...UsageProfile[]];
  modifiers?: ShortlistModifier[];
  addons?: UsageProfile[];
  weight_step_factor?: number;
  picker?: PickerQuestion[];
}
/**
 * Score of one variant for one profile combination (T-069).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ShortlistScore".
 */
export interface ShortlistScore {
  score: number;
  band: ShortlistBand;
  /**
   * Reason codes: '+<factor>', '-<factor>', 'gate:<id>', 'bonus:<id>', 'penalty:<id>'; the app turns them into plain words.
   */
  reasons?: string[];
  /**
   * Factors / gates without data (scored 0.5 or passed).
   */
  unknown?: string[];
}
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ShortlistVariantScores".
 */
export interface ShortlistVariantScores {
  variant_id: Id;
  /**
   * Derived inputs (winter range, real Wh/km, ...), all estimates.
   */
  derived?: {
    [k: string]: number | null;
  };
  /**
   * Profile id → factor id → 0..1 value (null = unknown).
   */
  factors?: {
    [k: string]: {
      [k: string]: number | null;
    };
  };
  /**
   * Profile id → unknown factors / gates.
   */
  unknown?: {
    [k: string]: string[];
  };
  /**
   * Profile combination → score.
   */
  scores: {
    [k: string]: ShortlistScore;
  };
}
/**
 * releases/<n>/shortlist_scores.json (T-069): editorial scores per variant and profile combination.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "ShortlistScoresRelease".
 */
export interface ShortlistScoresRelease {
  release: number;
  generated_at: string;
  model_version?: string;
  estimate?: boolean;
  /**
   * true: one owner's rules, opinion not fact.
   */
  editorial?: boolean;
  note?: string;
  rules?: {
    path?: string;
    sha256?: string;
    schema?: string | null;
    review?: boolean;
  };
  licence?: string;
  combos?: ShortlistComboKey[];
  bands?: ShortlistBand[];
  variants: ShortlistVariantScores[];
}
/**
 * INTERNAL ONLY: values copied by hand from other sites into the owner's sheet. Calibrate the rules; never in a release, the app or open data (data rules 1-2). No published type contains this.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "EditorialSheetValues".
 */
export interface EditorialSheetValues {
  use: "internal";
  [k: string]: string | number | boolean | null | "internal";
}
/**
 * Publishable owner pick ('Owner's pick'): verdict, tier, flags and notes, always labelled as one person's opinion (Decision 038). Has no sheet_values by design.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "EditorialPick".
 */
export interface EditorialPick {
  /**
   * Sheet tab.
   */
  tab?: string;
  row?: number;
  section?: string;
  group?: string | null;
  make: string;
  model: string;
  model_year?: number | null;
  variant?: string | null;
  seed_model_id?: Id | null;
  seed_generation_id?: Id | null;
  in_seed?: boolean;
  /**
   * Cross-reference id only (link check); never used to copy data.
   */
  evdb_car_id?: number | null;
  /**
   * Rank inside a group, lower is better (1.1-1.5).
   */
  tier?: number | null;
  verdict: EditorialVerdict;
  favourite: boolean;
  flags?: EditorialFlag[];
  /**
   * Owner's own words (CC BY 4.0).
   */
  notes?: string | null;
}
/**
 * INTERNAL row of menno-picks.yaml primary_car_picks: an EditorialPick plus sheet_values. Strip sheet_values to get an EditorialPick.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "EditorialPickSheetRow".
 */
export interface EditorialPickSheetRow {
  /**
   * Sheet tab.
   */
  tab?: string;
  row?: number;
  section?: string;
  group?: string | null;
  make: string;
  model: string;
  model_year?: number | null;
  variant?: string | null;
  seed_model_id?: Id | null;
  seed_generation_id?: Id | null;
  in_seed?: boolean;
  /**
   * Cross-reference id only (link check); never used to copy data.
   */
  evdb_car_id?: number | null;
  /**
   * Rank inside a group, lower is better (1.1-1.5).
   */
  tier?: number | null;
  verdict: EditorialVerdict;
  favourite: boolean;
  flags?: EditorialFlag[];
  /**
   * Owner's own words (CC BY 4.0).
   */
  notes?: string | null;
  sheet_values: EditorialSheetValues;
}
/**
 * Row of menno-picks.yaml eras: model-level verdict per era (OTHER EVs tab).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "EditorialEraPick".
 */
export interface EditorialEraPick {
  /**
   * Sheet tab.
   */
  tab?: string;
  row?: number;
  era: string;
  make: string;
  model: string;
  seed_model_id?: Id | null;
  seed_generation_id?: Id | null;
  in_seed?: boolean;
  battery_options_kwh?: number[] | null;
  verdict: EditorialVerdict;
  favourite: boolean;
  remark?: string | null;
}
/**
 * INTERNAL row of menno-picks.yaml used_budget_bands_2025_07 (stale July 2025 used-market analysis).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "EditorialUsedBudgetPick".
 */
export interface EditorialUsedBudgetPick {
  /**
   * Sheet tab.
   */
  tab?: string;
  row?: number;
  price_band: string;
  /**
   * Sheet tier code, e.g. 'A1'.
   */
  tier?: string | null;
  make: string;
  model: string;
  seed_model_id?: Id | null;
  seed_generation_id?: Id | null;
  in_seed?: boolean;
  battery_kwh?: number | null;
  verdict: EditorialVerdict;
  favourite: boolean;
  availability?: string | null;
  pros?: string | null;
  cons?: string | null;
  sheet_values?: EditorialSheetValues;
}
/**
 * data/editorial/menno-picks.yaml (generated by import_menno_sheet.py). Internal file: publish EditorialPick rows only.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "EditorialPicks".
 */
export interface EditorialPicks {
  schema: string;
  author: string;
  source?: {
    name?: string;
    imported?: string;
    importer?: string;
  };
  scope?: string;
  licence?: string;
  primary_car_picks: EditorialPickSheetRow[];
  eras?: EditorialEraPick[];
  used_budget_bands_2025_07?: {
    note?: string;
    rows?: EditorialUsedBudgetPick[];
  };
}
/**
 * Ids that were published before and are gone now: old id → successor id, or null when there is no successor (T-062). The web app redirects old URLs with it.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "RetiredIds".
 */
export interface RetiredIds {
  [k: string]: Id | null;
}
/**
 * releases/<n>/retired_ids.json (T-062). Becomes Catalogue.retired_ids once the pipeline test for the in-catalogue path lands with it (WS1); the pipeline switches on its own when Catalogue has the property.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "RetiredIdsFile".
 */
export interface RetiredIdsFile {
  release: number;
  generated_at: string;
  retired_ids: RetiredIds;
}
