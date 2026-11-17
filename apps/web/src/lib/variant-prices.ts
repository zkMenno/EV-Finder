// Used price band per variant, build year and country (T-081, WS1): `used_prices.json` next to
// the release's catalogue.json. `method: model` bands are estimates (list price × value kept at
// that age); `samples` > 0 means counted listings. Missing country or year = not enough data.
// Pure parsing + a compact form for the browser (the hero re-ranks by budget, T-080).

export interface VariantBand {
  build_year: number;
  p25: number | null;
  median: number;
  p75: number | null;
  currency: string;
  samples: number;
  method: string;
  estimate: boolean;
  confidence: string;
  /** method model: the list price the estimate starts from, and the share of value kept at that age. */
  list_price: number | null;
  kept_share: number | null;
  /** method model: source ids of the list price; method samples: the sample source's name. */
  sources: string[];
}

/** variant id → country code → bands (oldest build year first). */
export type VariantUsedPrices = Map<string, Record<string, VariantBand[]>>;

/**
 * Compact per-row form for the client catalogue: country → [year, p25, median, p75, flags, list
 * price, kept share, sources]. flags: 1 = estimate, 2 = low confidence. The last three say how an
 * estimate was made (Decision 064, shown in Nerd mode); `sources` = source ids (model) or the
 * sample source's name (samples), comma-separated, or null.
 */
export type CompactBand = [number, number | null, number, number | null, number, (number | null)?, (number | null)?, (string | null)?];
export type CompactBands = Record<string, CompactBand[]>;

const num = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);
const optNum = (v: unknown): number | null => (num(v) && v >= 0 ? v : null);

function band(v: unknown): VariantBand | null {
  if (!v || typeof v !== "object") return null;
  const b = v as Record<string, unknown>;
  if (!Number.isInteger(b.build_year) || !num(b.median) || b.median <= 0) return null;
  const median = b.median;
  // A quartile on the wrong side of the median is a data error: show the median alone rather than
  // a range that reads backwards (found by the T-125 property tests).
  const p25 = optNum(b.p25);
  const p75 = optNum(b.p75);
  return {
    build_year: b.build_year as number,
    p25: p25 !== null && p25 <= median ? p25 : null,
    median,
    p75: p75 !== null && p75 >= median ? p75 : null,
    currency: typeof b.currency === "string" ? b.currency : "",
    samples: Number.isInteger(b.samples) ? (b.samples as number) : 0,
    method: typeof b.method === "string" ? b.method : "",
    estimate: b.estimate === true || b.method === "model",
    confidence: typeof b.confidence === "string" ? b.confidence : "",
    list_price: num(b.list_price) && b.list_price > 0 ? b.list_price : null,
    kept_share: num(b.kept_share) && b.kept_share > 0 && b.kept_share <= 1.5 ? b.kept_share : null,
    sources: Array.isArray(b.list_source_ids)
      ? b.list_source_ids.filter((x): x is string => typeof x === "string")
      : b.source && typeof b.source === "object" && typeof (b.source as Record<string, unknown>).name === "string"
        ? [(b.source as Record<string, string>).name!]
        : [],
  };
}

/** Parses the file; malformed rows are skipped, a malformed file gives an empty map. */
export function parseVariantUsedPrices(doc: unknown): VariantUsedPrices {
  const out: VariantUsedPrices = new Map();
  const variants = doc && typeof doc === "object" ? (doc as Record<string, unknown>).variants : null;
  if (!Array.isArray(variants)) return out;
  for (const v of variants) {
    if (!v || typeof v !== "object") continue;
    const id = (v as Record<string, unknown>).variant_id;
    const bands = (v as Record<string, unknown>).bands;
    if (typeof id !== "string" || !bands || typeof bands !== "object") continue;
    const per: Record<string, VariantBand[]> = {};
    for (const [cc, list] of Object.entries(bands as Record<string, unknown>)) {
      if (!/^[A-Z]{2}$/.test(cc) || !Array.isArray(list)) continue;
      const ok = list.map(band).filter((b): b is VariantBand => b !== null).sort((a, b) => a.build_year - b.build_year);
      if (ok.length) per[cc] = ok;
    }
    if (Object.keys(per).length) out.set(id, per);
  }
  return out;
}

// compactBands lives in explore-data.ts (scripts/budget.mjs loads that file in plain Node, which
// needs it to have no runtime imports).
