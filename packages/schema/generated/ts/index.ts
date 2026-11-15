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
 * Fact field names. Enum-valued facts are checked at release time, not here (an if/then on Fact breaks the generated TS type): iso15118_20_support → Iso15118Support (yes/no/not-disclosed, default not-disclosed, never inferred); heat_pump → HeatPumpFitment; drag_coefficient → Cd 0-1. Units: frontal_area_m2 m², kerb_mass_kg kg (EU mass in running order), wheel_size_in = rim diameter code. Usable battery is battery_kwh_net (no separate usable_kwh field).
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
  | "wheel_size_in";
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
 * Kind of finance a FinanceProfile row describes. pcp = personal contract purchase (balloon at the end; UK, similar to FR LOA).
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "FinanceProduct".
 */
export type FinanceProduct = "used-car-loan" | "new-car-loan" | "private-lease" | "business-lease" | "pcp";
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
  /**
   * ABRP car model code for deep links (Decision 012); null = plain ABRP link.
   */
  abrp_typecode?: string | null;
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
  /**
   * ABRP car model code; null = plain ABRP link.
   */
  abrp_typecode?: string | null;
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
 * Row in data/taxonomy/usage_profiles.yaml: Fit-score weights per profile (trip-fit §6). A new row, not new code.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "UsageProfile".
 */
export interface UsageProfile {
  id: Id;
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
   * Factor → weight (price, efficiency, dc_km_20min_winter, winter_1000km_time, ac_speed, battery_risk ...).
   */
  weights?: {
    [k: string]: WeightLevel;
  };
  /**
   * Add-ons: factor → steps up (+) or down (-), e.g. battery_risk +1.
   */
  weight_steps?: {
    [k: string]: number;
  };
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
 * Text keyed by language (en, nl, de, fr, es, it); en required.
 *
 * This interface was referenced by `EvSchema`'s JSON-Schema
 * via the `definition` "LocalizedText".
 */
export interface LocalizedText48 {
  [k: string]: string;
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
  label?: LocalizedText49;
  /**
   * URL template with {placeholders}, e.g. ABRP car model; null = plain link.
   */
  deep_link_template?: string | null;
}
/**
 * Optional link label override.
 */
export interface LocalizedText49 {
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
  source: Source;
  source_record?: string;
  retrieved_at: string;
  confidence: Confidence;
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
