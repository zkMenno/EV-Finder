// "Best used EV under €15k / €20k / €25k" per country (Addendum 5 backlog item 4, spec §rankings:
// "real range per € at the generation's typical used price"). Pure functions; pages render them.
//
// HIDDEN TONIGHT, ON PURPOSE: the release has no used prices yet (T-056 used-price layer 0 is
// todo, and the schema has no used-price field, see QUESTIONS.md Q-085). A list is only shown,
// linked from /top and listed in sitemap.xml when at least USED_MIN_ENTRIES generations qualify;
// otherwise /{country}/{lang}/top/best-used-under-… is not generated and answers 404. Nothing is
// guessed: no used price, no entry. Once the pipeline publishes `used_prices` in catalogue.json
// (read by catalogue.usedPrices()) and the site is rebuilt, the lists appear by themselves
// (src/lib/used-rankings.test.ts proves it with a fixture).
import type { Country, Currency, FieldProvenance, PublishedVariant } from "@ev/schema";
import { MIN_SAMPLES } from "@/components/PriceBand";

export const USED_RANKING_IDS = ["best-used-under-15k", "best-used-under-20k", "best-used-under-25k"] as const;
export type UsedRankingId = (typeof USED_RANKING_IDS)[number];

/** A list needs at least this many qualifying generations, else it is hidden (404, not linked). */
export const USED_MIN_ENTRIES = 5;

/**
 * Typical-used-price ceiling per list and currency. EUR as named; for the UK the nearest round
 * GBP price points (about 0.86 GBP per EUR in late 2025, rounded down, as PRICE_THRESHOLD does).
 */
export const USED_CAP: Record<UsedRankingId, Record<Currency, number>> = {
  "best-used-under-15k": { EUR: 15000, GBP: 13000 },
  "best-used-under-20k": { EUR: 20000, GBP: 17000 },
  "best-used-under-25k": { EUR: 25000, GBP: 21000 },
};

export function isUsedRankingId(v: string): v is UsedRankingId {
  return (USED_RANKING_IDS as readonly string[]).includes(v);
}

/**
 * One sourced used-price band for a generation in a country (proposed release shape, Q-085).
 * `typical` is the median asking/transaction price over `samples` observations.
 */
export interface UsedPriceBand {
  generation_id: string;
  country: Country;
  currency: Currency;
  typical: number;
  low?: number;
  high?: number;
  samples: number;
  source_ids: string[];
  /** ISO date the prices were retrieved. */
  retrieved_at: string;
  estimate?: boolean;
}

const finite = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);

/** Runtime check for one band read from catalogue.json (the field is not in the schema yet). */
export function isUsedPriceBand(v: unknown): v is UsedPriceBand {
  if (!v || typeof v !== "object") return false;
  const b = v as Record<string, unknown>;
  return (
    typeof b.generation_id === "string" &&
    typeof b.country === "string" &&
    (b.currency === "EUR" || b.currency === "GBP") &&
    finite(b.typical) &&
    b.typical > 0 &&
    finite(b.samples) &&
    Array.isArray(b.source_ids) &&
    b.source_ids.every((s) => typeof s === "string") &&
    typeof b.retrieved_at === "string"
  );
}

/** A band counts only with a source and enough samples (the PriceBand rule: ≥ MIN_SAMPLES). */
export function qualifies(b: UsedPriceBand): boolean {
  return b.source_ids.length > 0 && b.samples >= MIN_SAMPLES && b.typical > 0;
}

export interface UsedRankEntry {
  rank: number;
  /** Representative variant: the median real range of the generation (lower median). */
  row: PublishedVariant;
  band: UsedPriceBand;
  rangeKm: number;
  /** km of real range per 1,000 of the currency at the typical used price. */
  value: number;
  estimate: boolean;
  /** Provenance of the price band, for <Num>. */
  priceProvenance: FieldProvenance;
}

function representative(rows: PublishedVariant[]): PublishedVariant | null {
  const ranged = rows.filter((r) => finite(r.real_range_km)).sort((a, b) => a.real_range_km! - b.real_range_km! || a.variant_id.localeCompare(b.variant_id));
  return ranged.length ? ranged[Math.floor((ranged.length - 1) / 2)]! : null;
}

/** The ranked list for one cap, country and currency (one row per generation). */
export function usedRanking(
  id: UsedRankingId,
  rows: readonly PublishedVariant[],
  bands: readonly UsedPriceBand[],
  country: Country,
  currency: Currency,
  limit = 50,
): UsedRankEntry[] {
  const cap = USED_CAP[id][currency];
  const byGen = new Map<string, PublishedVariant[]>();
  for (const r of rows) byGen.set(r.generation_id, [...(byGen.get(r.generation_id) ?? []), r]);
  const items: Omit<UsedRankEntry, "rank">[] = [];
  for (const band of bands) {
    if (band.country !== country || band.currency !== currency || !qualifies(band) || band.typical >= cap) continue;
    const row = representative(byGen.get(band.generation_id) ?? []);
    if (!row) continue;
    const rangeKm = row.real_range_km!;
    items.push({
      row,
      band,
      rangeKm,
      value: Math.round((rangeKm / (band.typical / 1000)) * 10) / 10,
      estimate: !!row.provenance.real_range_km?.estimate || !!band.estimate,
      priceProvenance: {
        source_ids: band.source_ids as FieldProvenance["source_ids"],
        confidence: band.samples >= 20 ? "medium" : "low",
        estimate: !!band.estimate,
        note: `${band.samples} samples · ${band.retrieved_at}`,
      },
    });
  }
  // De-duplicate: one band per generation (the first in release order wins).
  const seen = new Set<string>();
  const unique = items.filter((e) => (seen.has(e.band.generation_id) ? false : (seen.add(e.band.generation_id), true)));
  unique.sort((a, b) => b.value - a.value || a.band.typical - b.band.typical || a.row.generation_id.localeCompare(b.row.generation_id));
  const out: UsedRankEntry[] = [];
  unique.forEach((e, i) => {
    const prev = out[i - 1];
    out.push({ ...e, rank: prev && prev.value === e.value ? prev.rank : i + 1 });
  });
  return out.slice(0, limit);
}

/** Lists with at least USED_MIN_ENTRIES entries for this country: the only ones that exist. */
export function visibleUsedRankings(
  rows: readonly PublishedVariant[],
  bands: readonly UsedPriceBand[],
  country: Country,
  currency: Currency,
): UsedRankingId[] {
  return USED_RANKING_IDS.filter((id) => usedRanking(id, rows, bands, country, currency).length >= USED_MIN_ENTRIES);
}
