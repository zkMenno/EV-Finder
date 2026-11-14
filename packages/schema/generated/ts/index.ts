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
  | "registered_count";

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
  subject_type: "model" | "generation" | "variant" | "market_variant";
  subject_id: Id;
  field: FactField;
  value: number | string | boolean;
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
   * Derived: dc_avg_10_80_kw / consumption * 100 / 6.
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
}
