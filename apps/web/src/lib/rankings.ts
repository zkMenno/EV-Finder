// Ranking lists (T-011). Pure functions over published rows; pages render them.
import type { Country, Currency, PublishedVariant } from "@ev/schema";

export const RANKING_IDS = ["longest-real-range-under-30k", "fastest-dc", "most-available-nl"] as const;
export type RankingId = (typeof RANKING_IDS)[number];

export function isRankingId(v: string): v is RankingId {
  return (RANKING_IDS as readonly string[]).includes(v);
}

/**
 * New-price ceiling per currency for "under 30k". EUR 30,000; for the UK we use GBP 26,000
 * (roughly EUR 30,000 at late-2025 rates, rounded down to a common UK price point).
 */
export const PRICE_THRESHOLD: Record<Currency, number> = { EUR: 30000, GBP: 26000 };

export interface RankEntry {
  rank: number;
  row: PublishedVariant;
  value: number;
  /** Provenance key of `value` in row.provenance. */
  field: string;
  /** Value is an estimate (Decision 009 badge). */
  estimate: boolean;
  /** New price (only for the price-capped list). */
  price?: number;
}

const finite = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);

/** Sort desc by value, ties by name; ties share a rank (1, 1, 3). */
function rank(items: Omit<RankEntry, "rank">[], tiebreak?: (a: Omit<RankEntry, "rank">, b: Omit<RankEntry, "rank">) => number): RankEntry[] {
  const name = (r: PublishedVariant) => `${r.make_name} ${r.model_name} ${r.generation_name} ${r.variant_name}`;
  const sorted = [...items].sort((a, b) => b.value - a.value || (tiebreak?.(a, b) ?? 0) || name(a.row).localeCompare(name(b.row)));
  const out: RankEntry[] = [];
  sorted.forEach((e, i) => {
    const prev = out[i - 1];
    out.push({ ...e, rank: prev && prev.value === e.value ? prev.rank : i + 1 });
  });
  return out;
}

/** Longest real-world range with a new price in this country below the threshold. Rows without a price are left out. */
export function rangeUnderPrice(rows: readonly PublishedVariant[], country: Country, currency: Currency, limit = 50): RankEntry[] {
  const max = PRICE_THRESHOLD[currency];
  const items = rows.flatMap((row) => {
    const p = row.price_new?.[country];
    if (!p || p.currency !== currency || !finite(p.amount) || p.amount >= max || !finite(row.real_range_km)) return [];
    return [{ row, value: row.real_range_km, field: "real_range_km", estimate: !!row.provenance.real_range_km?.estimate, price: p.amount }];
  });
  return rank(items, (a, b) => (a.price ?? 0) - (b.price ?? 0)).slice(0, limit);
}

/** Fastest DC charging by km added in 20 minutes (Decision 009: not peak kW). */
export function fastestDc(rows: readonly PublishedVariant[], limit = 50): RankEntry[] {
  const items = rows.flatMap((row) =>
    finite(row.dc_km_per_20min) && row.dc_km_per_20min > 0
      ? [{ row, value: row.dc_km_per_20min, field: "dc_km_per_20min", estimate: !!row.provenance.dc_km_per_20min?.estimate }]
      : [],
  );
  return rank(items).slice(0, limit);
}

/**
 * Generations by RDW registrations in NL. The count is generation-level (the same on every
 * variant), so one row per generation; the representative row is the first variant in timeline order.
 */
export function mostAvailableNl(rows: readonly PublishedVariant[], limit = 50): RankEntry[] {
  const byGen = new Map<string, PublishedVariant>();
  for (const row of rows) {
    if (!finite(row.registered_count_nl) || row.registered_count_nl <= 0) continue;
    const cur = byGen.get(row.generation_id);
    if (
      !cur ||
      row.registered_count_nl! > cur.registered_count_nl! ||
      (row.registered_count_nl === cur.registered_count_nl && row.year_start < cur.year_start)
    ) {
      byGen.set(row.generation_id, row);
    }
  }
  const items = [...byGen.values()].map((row) => ({
    row,
    value: row.registered_count_nl as number,
    field: "registered_count_nl",
    estimate: !!row.provenance.registered_count_nl?.estimate,
  }));
  return rank(items).slice(0, limit);
}

export function ranking(id: RankingId, rows: readonly PublishedVariant[], country: Country, currency: Currency): RankEntry[] {
  switch (id) {
    case "longest-real-range-under-30k":
      return rangeUnderPrice(rows, country, currency);
    case "fastest-dc":
      return fastestDc(rows);
    case "most-available-nl":
      return mostAvailableNl(rows);
  }
}
