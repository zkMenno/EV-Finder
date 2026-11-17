// Filtering and sorting for Explore. Pure functions, shared by the server render and the client.
import type { Country, QualityTier } from "@ev/schema";
import type { ExploreRow } from "./explore-data";
import type { ExploreFilters, SortDir, SortKey } from "./state";
import { defaultFilters, ERAS } from "./state";
import { hasDcData } from "./dc";

type NumGetter = (r: ExploreRow) => number | null | undefined;

export function priceFor(row: ExploreRow, country: Country): number | null {
  return row.price_new?.[country]?.amount ?? null;
}

/** A row with a missing value is excluded only when that filter is active. */
export function applyFilters(rows: ExploreRow[], f: ExploreFilters, country: Country): ExploreRow[] {
  const checks: ((r: ExploreRow) => boolean)[] = [];
  const min = (get: NumGetter, limit: number | null) => {
    if (limit === null) return;
    checks.push((r) => {
      const v = get(r);
      return typeof v === "number" && v >= limit;
    });
  };
  const max = (get: NumGetter, limit: number | null) => {
    if (limit === null) return;
    checks.push((r) => {
      const v = get(r);
      return typeof v === "number" && v <= limit;
    });
  };
  max((r) => priceFor(r, country), f.priceMax);
  min((r) => r.real_range_km, f.rangeMin);
  min((r) => r.battery_kwh_net, f.batteryMin);
  // Decision 009: the DC filter uses km added in 20 min (motorway consumption).
  min((r) => r.dc_km_per_20min, f.dcMin);
  min((r) => r.boot_l, f.bootMin);
  max((r) => r.length_mm, f.lengthMax);
  min((r) => r.towing_kg, f.towingMin);
  min((r) => r.seats, f.seatsMin);
  min((r) => r.ac_kw, f.acMin);
  // Build years: the variant's years overlap the chosen range (a car still on sale runs to today).
  if (f.yearMin !== null) {
    const y = f.yearMin;
    checks.push((r) => r.year_end === null || r.year_end === undefined || r.year_end >= y);
  }
  if (f.yearMax !== null) {
    const y = f.yearMax;
    checks.push((r) => r.year_start <= y);
  }
  // Decision 010 (taxonomy ids; "not-disclosed" never matches a chosen id).
  min((r) => r.voltage_nominal_v, f.voltageMin);
  max((r) => r.voltage_nominal_v, f.voltageMax);
  const inIds = (sel: string[], get: (r: ExploreRow) => string | null | undefined) => {
    if (sel.length) checks.push((r) => { const v = get(r); return typeof v === "string" && sel.includes(v); });
  };
  inIds(f.voltageClasses, (r) => r.voltage_class_id);
  inIds(f.chemistries, (r) => r.chemistry_id);
  inIds(f.coolings, (r) => r.cooling_id);
  inIds(f.makes, (r) => r.make_id);
  if (f.excludeMakes.length) checks.push((r) => !f.excludeMakes.includes(r.make_id));
  if (f.fast400) checks.push((r) => r.fast_on_400v === true && hasDcData(r));
  if (f.charge100) checks.push((r) => r.charge_100_daily === true);
  if (f.eras.length) checks.push((r) => f.eras.includes(r.era));
  if (f.segments.length) checks.push((r) => r.segment !== undefined && f.segments.includes(r.segment));
  if (f.bodies.length) checks.push((r) => r.body !== undefined && f.bodies.includes(r.body));
  if (!checks.length) return rows;
  return rows.filter((r) => checks.every((c) => c(r)));
}

const TIER_RANK: Record<QualityTier, number> = { checked: 3, sourced: 2, "single-source": 1 };

export function displayName(r: ExploreRow): string {
  return `${r.make_name} ${r.model_name} ${r.variant_name}`;
}

/** Score per row for the "suggested" sort; null = ruled out or no profile (sorts last). */
export type Scorer = (r: ExploreRow) => number | null;

function sortValue(r: ExploreRow, key: SortKey, country: Country, score?: Scorer): number | string | null {
  switch (key) {
    case "suggested":
      return score ? score(r) : null;
    case "name":
      return displayName(r).toLowerCase();
    case "years":
      return r.year_start;
    case "era":
      return ERAS.indexOf(r.era);
    case "range":
      return r.real_range_km ?? null;
    case "battery":
      return r.battery_kwh_net ?? null;
    case "dc":
      return r.dc_km_per_20min ?? null;
    case "ac":
      return r.ac_km_per_h ?? null;
    case "price":
      return priceFor(r, country);
    case "rdw":
      return r.registered_count_nl ?? null;
    case "quality":
      return TIER_RANK[r.quality_tier];
  }
}

/**
 * Stable sort; missing values always go last whatever the direction.
 * With no sort key, rows keep catalogue order.
 */
export function sortRows(rows: ExploreRow[], key: SortKey | null, dir: SortDir, country: Country, score?: Scorer): ExploreRow[] {
  if (!key) return rows;
  const sign = dir === "desc" ? -1 : 1;
  return rows
    .map((r, i) => ({ r, i, v: sortValue(r, key, country, score) }))
    .sort((a, b) => {
      if (a.v === null && b.v === null) return a.i - b.i;
      if (a.v === null) return 1;
      if (b.v === null) return -1;
      const c = typeof a.v === "string" && typeof b.v === "string" ? a.v.localeCompare(b.v) : Number(a.v) - Number(b.v);
      return c !== 0 ? c * sign : a.i - b.i;
    })
    .map((x) => x.r);
}

/**
 * One removable filter, for the empty state ("No cars match: remove the 'Charging voltage' filter").
 * Groups fields that one control sets together (the voltage range).
 */
export const FILTER_GROUPS = [
  ["priceMax"],
  ["eras"],
  ["segments"],
  ["bodies"],
  ["rangeMin"],
  ["batteryMin"],
  ["dcMin"],
  ["bootMin"],
  ["lengthMax"],
  ["towingMin"],
  ["seatsMin"],
  ["acMin"],
  ["yearMin", "yearMax"],
  ["makes"],
  ["excludeMakes"],
  ["voltageClasses"],
  ["voltageMin", "voltageMax"],
  ["fast400"],
  ["chemistries"],
  ["coolings"],
  ["charge100"],
  ["tripFit"],
] as const satisfies readonly (readonly (keyof ExploreFilters)[])[];
export type FilterGroup = (typeof FILTER_GROUPS)[number][0];

function isActive(f: ExploreFilters, k: keyof ExploreFilters): boolean {
  const v = f[k];
  return Array.isArray(v) ? v.length > 0 : typeof v === "boolean" ? v : v !== null;
}

/** Filter groups that are on now (in FILTER_GROUPS order). */
export function activeGroups(f: ExploreFilters): FilterGroup[] {
  return FILTER_GROUPS.filter((g) => g.some((k) => isActive(f, k))).map((g) => g[0]);
}

/** `f` with one group turned off (back to its default). */
export function withoutGroup(f: ExploreFilters, group: FilterGroup): ExploreFilters {
  const keys = FILTER_GROUPS.find((g) => g[0] === group) ?? [group];
  const d = defaultFilters();
  const out: ExploreFilters = { ...f };
  for (const k of keys) (out as unknown as Record<string, unknown>)[k] = d[k];
  return out;
}

/**
 * The most restrictive active filter: the single group whose removal brings back the most cars.
 * `count(filters)` runs the same pipeline Explore shows (filters + trip fit). Ties go to the
 * earlier group. Null when no single removal helps (or nothing is active).
 */
export function mostRestrictive(f: ExploreFilters, count: (f: ExploreFilters) => number): { group: FilterGroup; count: number } | null {
  let best: { group: FilterGroup; count: number } | null = null;
  for (const group of activeGroups(f)) {
    const n = count(withoutGroup(f, group));
    if (n > 0 && (!best || n > best.count)) best = { group, count: n };
  }
  return best;
}
