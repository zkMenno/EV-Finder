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
  | "warranty_km";
/**
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "TaxonomyStatus".
 */
export type TaxonomyStatus = "mainstream" | "emerging" | "niche" | "legacy" | "experimental";

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
  consumption_kwh_100km?: number | null;
  ac_kw?: number | null;
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
  real_range_rung?: RealRangeRung | null;
  power_kw?: number | null;
  accel_0_100_s?: number | null;
  boot_l?: number | null;
  length_mm?: number | null;
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
  pros?: {
    [k: string]: string;
  }[];
  cons?: {
    [k: string]: string;
  }[];
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
