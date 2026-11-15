// Spec fields shown on variant, generation and compare pages, plus the pure "what differs"
// logic: change-vs-previous-column for the generation spec diff (T-009) and
// differs-from-the-others for the compare table (T-010). No React, safe anywhere.
import type { Country, PublishedVariant } from "@ev/schema";

export type SpecGroup = "battery" | "charging" | "range" | "performance" | "dimensions" | "practicality" | "availability";

export const SPEC_GROUPS: readonly SpecGroup[] = [
  "range",
  "battery",
  "charging",
  "performance",
  "dimensions",
  "practicality",
  "availability",
];

type NumKeyOf<T> = { [K in keyof T]-?: NonNullable<T[K]> extends number ? K : never }[keyof T];

/** Numeric PublishedVariant fields (identity years and release excluded). */
export type NumKey = Exclude<NumKeyOf<PublishedVariant>, "release" | "year_start" | "year_end">;

export type TextKey =
  | "chemistry_id"
  | "cooling_id"
  | "cell_format"
  | "voltage_class_id"
  | "voltage_label"
  | "charger_400v_mode"
  | "platform_name"
  | "drivetrain"
  | "body"
  | "segment"
  | "charge_100_daily"
  | "fast_on_400v";

interface FieldBase {
  group: SpecGroup;
  /** Glossary term id for the ⓘ (missing terms render the plain label). */
  term?: string;
}
export interface NumField extends FieldBase {
  kind: "num";
  key: NumKey;
  unit?: string;
  /** Display and comparison precision. */
  digits: number;
}
export interface TextField extends FieldBase {
  kind: "text";
  key: TextKey;
}
/** New price in the page's country (provenance key `price_new.<CC>`). */
export interface PriceField extends FieldBase {
  kind: "price";
  key: "price_new";
}
export type SpecField = NumField | TextField | PriceField;

const num = (key: NumKey, group: SpecGroup, unit: string | undefined, digits: number, term?: string): NumField => ({
  kind: "num",
  key,
  group,
  unit,
  digits,
  ...(term ? { term } : {}),
});
const text = (key: TextKey, group: SpecGroup, term?: string): TextField => ({ kind: "text", key, group, ...(term ? { term } : {}) });

/** Every field, in display order. Labels live in pages.*.json as `field.<key>`. */
export const SPEC_FIELDS: readonly SpecField[] = [
  num("real_range_km", "range", "km", 0, "real-range"),
  num("wltp_range_km", "range", "km", 0, "wltp"),
  num("consumption_kwh_100km", "range", "kWh/100 km", 1, "consumption"),
  num("consumption_motorway_kwh_100km", "range", "kWh/100 km", 1, "consumption"),

  num("battery_kwh_net", "battery", "kWh", 1, "usable-vs-gross"),
  text("chemistry_id", "battery", "chemistry"),
  text("charge_100_daily", "battery", "chemistry"),
  text("cooling_id", "battery", "cooling"),
  text("cell_format", "battery", "cell-format"),
  text("voltage_class_id", "battery", "voltage-class"),
  num("voltage_nominal_v", "battery", "V", 0, "nominal-voltage"),
  num("voltage_max_v", "battery", "V", 0, "nominal-voltage"),
  text("platform_name", "battery", "platform"),

  num("dc_km_per_20min", "charging", "km", 0, "dc-km-20min"),
  num("dc_km_per_10min", "charging", "km", 0, "dc-km-20min"),
  num("dc_peak_kw", "charging", "kW", 0, "peak-kw"),
  num("dc_avg_10_80_kw", "charging", "kW", 0, "10-80"),
  num("dc_minutes_10_80", "charging", "min", 0, "10-80"),
  num("dc_peak_held_min", "charging", "min", 0, "charge-curve"),
  text("charger_400v_mode", "charging", "400v-charger-behaviour"),
  num("charger_400v_kw", "charging", "kW", 0, "400v-charger-behaviour"),
  num("ac_kw", "charging", "kW", 1, "ac-charging"),
  num("ac_km_per_h", "charging", "km/h", 0, "ac-charging"),

  num("power_kw", "performance", "kW", 0),
  num("accel_0_100_s", "performance", "s", 1),
  text("drivetrain", "performance"),

  num("length_mm", "dimensions", "mm", 0),
  num("weight_kg", "dimensions", "kg", 0),

  num("boot_l", "practicality", "l", 0),
  num("seats", "practicality", undefined, 0),
  num("towing_kg", "practicality", "kg", 0),
  text("body", "practicality"),
  text("segment", "practicality"),

  { kind: "price", key: "price_new", group: "availability" },
  num("registered_count_nl", "availability", undefined, 0),
];

/** Rows of the per-generation spec diff (T-009): the fields that tell variants and years apart. */
export const DIFF_KEYS: readonly SpecField["key"][] = [
  "battery_kwh_net",
  "chemistry_id",
  "voltage_class_id",
  "charger_400v_mode",
  "real_range_km",
  "wltp_range_km",
  "dc_km_per_20min",
  "dc_peak_kw",
  "dc_minutes_10_80",
  "ac_kw",
  "power_kw",
  "accel_0_100_s",
  "drivetrain",
  "boot_l",
  "towing_kg",
];

export function fieldsFor(keys: readonly SpecField["key"][]): SpecField[] {
  return keys.flatMap((k) => SPEC_FIELDS.filter((f) => f.key === k));
}

export type CellValue = number | string | null;

/** Comparable value of a field: numbers rounded to the field's display precision, text as its raw id. */
export function cellValue(row: PublishedVariant, field: SpecField, country?: Country): CellValue {
  if (field.kind === "price") {
    const m = country ? row.price_new?.[country] : undefined;
    return m && Number.isFinite(m.amount) ? `${m.currency} ${Math.round(m.amount)}` : null;
  }
  const v = row[field.key];
  if (v === null || v === undefined) return null;
  if (field.kind === "num") {
    if (typeof v !== "number" || !Number.isFinite(v)) return null;
    const p = 10 ** field.digits;
    return Math.round(v * p) / p;
  }
  return String(v);
}

export function sameValue(a: CellValue, b: CellValue): boolean {
  return a === b;
}

/** Variants in timeline order: first year, then last year (open-ended last), then name. */
export function timelineOrder(rows: readonly PublishedVariant[]): PublishedVariant[] {
  return [...rows].sort(
    (a, b) =>
      a.year_start - b.year_start ||
      (a.year_end ?? 9999) - (b.year_end ?? 9999) ||
      a.variant_name.localeCompare(b.variant_name),
  );
}

export interface DiffCell {
  value: CellValue;
  /** Differs from the column to its left (the previous variant in timeline order). */
  changed: boolean;
}
export interface DiffRow {
  field: SpecField;
  cells: DiffCell[];
  /** Any cell changed. */
  changes: boolean;
}
export interface SpecDiff {
  columns: PublishedVariant[];
  rows: DiffRow[];
}

/**
 * Generation spec diff: columns = variants in timeline order, rows = fields.
 * A cell is "changed" when its value differs from the previous column. Rows where every
 * variant is missing the value are dropped (nothing to show).
 */
export function specDiff(rows: readonly PublishedVariant[], fields: readonly SpecField[], country?: Country): SpecDiff {
  const columns = timelineOrder(rows);
  const out: DiffRow[] = [];
  for (const field of fields) {
    const values = columns.map((r) => cellValue(r, field, country));
    if (values.every((v) => v === null)) continue;
    const cells = values.map((value, i) => ({ value, changed: i > 0 && !sameValue(values[i - 1] ?? null, value) }));
    out.push({ field, cells, changes: cells.some((c) => c.changed) });
  }
  return { columns, rows: out };
}

/**
 * Compare highlight (T-010): which cells differ from the others in their row.
 * All equal → none. Otherwise, if one value is the clear majority, the cells that differ
 * from it; with no clear majority (e.g. two cars, or all different) every cell.
 */
export function differingCells(values: readonly CellValue[]): boolean[] {
  if (values.length < 2 || values.every((v) => sameValue(v, values[0] ?? null))) return values.map(() => false);
  const counts = new Map<CellValue, number>();
  for (const v of values) counts.set(v, (counts.get(v) ?? 0) + 1);
  const sorted = [...counts.entries()].sort((a, b) => b[1] - a[1]);
  const [top, second] = sorted;
  const majority = top && top[1] >= 2 && (!second || top[1] > second[1]) ? top[0] : undefined;
  if (majority === undefined) return values.map(() => true);
  return values.map((v) => !sameValue(v, majority));
}

export function rowDiffers(values: readonly CellValue[]): boolean {
  return differingCells(values).some(Boolean);
}
