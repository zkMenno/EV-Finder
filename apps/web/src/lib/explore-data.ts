// Compact rows shipped to the browser for Explore. Same field names as PublishedVariant,
// only the columns Explore needs, nulls dropped. Pure: safe on server and client.
import type { FieldProvenance, PublishedVariant, Source } from "@ev/schema";

export const EXPLORE_FIELDS = [
  "variant_id",
  "variant_name",
  "generation_id",
  "generation_name",
  "model_id",
  "model_name",
  "make_id",
  "make_name",
  "year_start",
  "year_end",
  "era",
  "segment",
  "body",
  "real_range_km",
  "real_range_rung",
  "battery_kwh_net",
  // Trip fit (T-036): WLTP battery consumption = usable kWh / WLTP km (fallback: published consumption).
  "wltp_range_km",
  "consumption_kwh_100km",
  "dc_km_per_20min",
  "dc_km_per_10min",
  "dc_peak_kw",
  "dc_peak_kw_is_claim",
  // Not shown in Explore; carried so hasDcData() (src/lib/dc.ts) gives the same answer as on spec pages.
  "dc_avg_10_80_kw",
  "dc_minutes_10_80",
  "ac_km_per_h",
  "boot_l",
  "length_mm",
  "towing_kg",
  "price_new",
  "registered_count_nl",
  "quality_tier",
  // Decision 010
  "voltage_class_id",
  "voltage_nominal_v",
  "voltage_label",
  "charger_400v_mode",
  "charger_400v_kw",
  "fast_on_400v",
  "chemistry_id",
  "cooling_id",
  "cell_format",
  "charge_100_daily",
  "platform_name",
  "battery_pack_id",
  // Hero shortlist scoring (T-080, shortlist rules): AC speed, heat pump, seats, mass, new or used.
  "ac_kw",
  "heat_pump",
  "seats",
  "kerb_mass_kg",
  "mass_running_order_kg",
  "on_sale_new",
] as const satisfies readonly (keyof PublishedVariant)[];

/** Numeric fields that carry provenance in the client JSON. */
const NUMERIC = new Set<string>([
  "real_range_km",
  "battery_kwh_net",
  // wltp_range_km / consumption_kwh_100km ship without provenance: Explore never shows them, they
  // only feed the trip estimate, which carries its own "fixture matrix" provenance (T-036).
  "dc_km_per_20min",
  "dc_km_per_10min",
  "dc_peak_kw",
  "ac_km_per_h",
  "boot_l",
  "length_mm",
  "towing_kg",
  "registered_count_nl",
  "voltage_nominal_v",
  "charger_400v_kw",
]);

export type ExploreRow = Pick<PublishedVariant, (typeof EXPLORE_FIELDS)[number]> & {
  provenance: Record<string, FieldProvenance>;
};

export interface ClientCatalogue {
  release: number;
  /** source id → display name, for the provenance popovers. */
  sources: Record<string, string>;
  rows: ExploreRow[];
}

export function toExploreRow(row: PublishedVariant): ExploreRow {
  const out: Record<string, unknown> = {};
  for (const f of EXPLORE_FIELDS) {
    const v = row[f];
    if (v !== null && v !== undefined) out[f] = v;
  }
  const prov: Record<string, FieldProvenance> = {};
  for (const [k, p] of Object.entries(row.provenance ?? {})) {
    if (NUMERIC.has(k) || k.startsWith("price_new")) prov[k] = p;
  }
  out.provenance = prov;
  return out as ExploreRow;
}

export function sourceNames(sources: Source[]): Record<string, string> {
  return Object.fromEntries(sources.map((s) => [s.id, s.name]));
}

export function toClientCatalogue(release: number, sources: Source[], rows: PublishedVariant[]): ClientCatalogue {
  return { release, sources: sourceNames(sources), rows: rows.map(toExploreRow) };
}
