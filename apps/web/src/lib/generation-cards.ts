// One catalogue card per generation (T-130 part 2 design): the filtered, sorted variant rows are
// grouped by generation in order of first appearance, so the sort order carries over (a generation
// sits where its best-placed variant sits). Pure: shared by the server render and the client.
import type { Country } from "@ev/schema";
import { BAND_ESTIMATE, BAND_LOW, type ExploreRow } from "./explore-data";
import type { PriceHow } from "./variant-prices";

/** Lowest and highest value over a generation's matching variants; `row` holds the highest (its provenance). */
export interface Span {
  min: number;
  max: number;
  row: ExploreRow;
}

export interface UsedSpan {
  /** Lower quartile (or typical price) of the cheapest band, upper quartile of the dearest. */
  low: number;
  high: number;
  /** Any band is our model, not counted listings (Decision 064). */
  estimate: boolean;
  /** Any band leans on a list price from a nearby year or another country. */
  lowConfidence: boolean;
  /** How the first band with notes was made (Nerd line). */
  how?: PriceHow;
}

export interface GenCard {
  generation_id: string;
  /** The generation's matching variants, in the current order. */
  rows: ExploreRow[];
  /** First matching variant in the current order: names, links, compare and the "#n popular" tag. */
  lead: ExploreRow;
  yearStart: number;
  /** null = still on sale. */
  yearEnd: number | null;
  used: UsedSpan | null;
  winter: Span | null;
  summer: Span | null;
  dc20: Span | null;
  battery: Span | null;
  newPrice: Span | null;
}

function span(rows: ExploreRow[], get: (r: ExploreRow) => number | null | undefined): Span | null {
  let out: Span | null = null;
  for (const r of rows) {
    const v = get(r);
    if (typeof v !== "number" || !Number.isFinite(v)) continue;
    if (!out) out = { min: v, max: v, row: r };
    else {
      if (v < out.min) out.min = v;
      if (v > out.max) {
        out.max = v;
        out.row = r;
      }
    }
  }
  return out;
}

/** The visitor's used-price and build-year filters: the card shows the bands they asked for. */
export interface BandScope {
  usedMin?: number | null;
  usedMax?: number | null;
  yearMin?: number | null;
  yearMax?: number | null;
}

/**
 * Used price band of the matching variants where the visitor lives: the build years and typical
 * prices inside the visitor's filters (no filter: all build years). If the filters leave no band
 * (a build-year filter on a variant without bands for those years), all bands are used.
 */
export function usedSpan(rows: ExploreRow[], country: Country, scope: BandScope = {}): UsedSpan | null {
  const all = rows.flatMap((r) => r.used_bands?.[country] ?? []);
  const min = scope.usedMin ?? -Infinity;
  const max = scope.usedMax ?? Infinity;
  const y0 = scope.yearMin ?? -Infinity;
  const y1 = scope.yearMax ?? Infinity;
  const inScope = all.filter(([y, , m]) => m >= min && m <= max && y >= y0 && y <= y1);
  let out: UsedSpan | null = null;
  for (const [, p25, median, p75, flags, how] of inScope.length ? inScope : all) {
    const lo = p25 ?? median;
    const hi = p75 ?? median;
    const est = (flags & BAND_ESTIMATE) !== 0;
    const low = (flags & BAND_LOW) !== 0;
    if (!out) out = { low: lo, high: hi, estimate: est, lowConfidence: low, ...(how ? { how } : {}) };
    else {
      out.low = Math.min(out.low, lo);
      out.high = Math.max(out.high, hi);
      out.estimate ||= est;
      out.lowConfidence ||= low;
      if (!out.how && how) out.how = how;
    }
  }
  return out;
}

export function generationCards(rows: ExploreRow[], country: Country, scope: BandScope = {}): GenCard[] {
  const groups = new Map<string, ExploreRow[]>();
  for (const r of rows) {
    const g = groups.get(r.generation_id);
    if (g) g.push(r);
    else groups.set(r.generation_id, [r]);
  }
  return [...groups.entries()].map(([id, list]) => {
    const lead = list[0]!;
    const onSale = list.some((r) => r.year_end === null || r.year_end === undefined);
    return {
      generation_id: id,
      rows: list,
      lead,
      yearStart: Math.min(...list.map((r) => r.year_start)),
      yearEnd: onSale ? null : Math.max(...list.map((r) => r.year_end as number)),
      used: usedSpan(list, country, scope),
      winter: span(list, (r) => r.real_range_winter_km),
      summer: span(list, (r) => r.real_range_km),
      dc20: span(list, (r) => r.dc_km_per_20min),
      battery: span(list, (r) => r.battery_kwh_net),
      newPrice: span(list, (r) => r.price_new?.[country]?.amount),
    };
  });
}

/** Distinct generations in a list of variant rows ("214 models · 87 match"). */
export function generationCount(rows: readonly ExploreRow[]): number {
  return new Set(rows.map((r) => r.generation_id)).size;
}

/** Brand → number of generations, most first, then by name ("Kia 8" in the brand filter). */
export function brandCounts(rows: readonly ExploreRow[]): { id: string; name: string; count: number }[] {
  const per = new Map<string, { name: string; gens: Set<string> }>();
  for (const r of rows) {
    const e = per.get(r.make_id) ?? { name: r.make_name, gens: new Set<string>() };
    e.gens.add(r.generation_id);
    per.set(r.make_id, e);
  }
  return [...per.entries()]
    .map(([id, e]) => ({ id, name: e.name, count: e.gens.size }))
    .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name));
}
