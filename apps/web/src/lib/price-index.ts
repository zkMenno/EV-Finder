// Country price indices (price layer 0): placeholder structure only. Every value is null and nothing
// in the UI reads it yet. Source, method and base year are open (config/price-index/README.md).
// Real values must come through the pipeline with provenance (AGENTS.md data rules), not be typed in here.
import type { Country } from "@ev/schema";

export type PriceIndexCountry = Extract<Country, "NL" | "DE" | "FR" | "BE" | "UK">;
export const PRICE_INDEX_COUNTRIES: readonly PriceIndexCountry[] = ["NL", "DE", "FR", "BE", "UK"];

/** First and last year the placeholder covers (inclusive). */
export const PRICE_INDEX_YEARS = { from: 2010, to: 2026 } as const;

/** One index value per year; null = no value (all of them, for now). */
export type PriceIndexSeries = Readonly<Record<number, number | null>>;
export type PriceIndex = Readonly<Record<PriceIndexCountry, PriceIndexSeries>>;

function emptySeries(): PriceIndexSeries {
  const out: Record<number, number | null> = {};
  for (let y = PRICE_INDEX_YEARS.from; y <= PRICE_INDEX_YEARS.to; y++) out[y] = null;
  return Object.freeze(out);
}

export const PRICE_INDEX: PriceIndex = Object.freeze(
  Object.fromEntries(PRICE_INDEX_COUNTRIES.map((c) => [c, emptySeries()])) as Record<PriceIndexCountry, PriceIndexSeries>,
);

/** Index value for a country and year, or null when unknown (always, for now). */
export function priceIndex(country: PriceIndexCountry, year: number): number | null {
  return PRICE_INDEX[country][year] ?? null;
}
