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
  /** Decision 064: "band" = counted listings, "estimate" = list price × value kept (our model). */
  basis: "band" | "estimate";
  /** Band rows (Decision 069): "variant" = this variant's own samples, "generation" = its generation's standing in. */
  scope: "variant" | "generation" | null;
  /** Estimate rows: which curve ("fitted", "fitted:<segment>", "published", "published:<cc>"). */
  curve: string | null;
  /** Estimate rows on a fitted curve: the countries whose samples fitted it. */
  curve_fitted_on: string[];
  /** Where the figure comes from: the sample source (band) or the curve's source (estimate). */
  source: { name: string; url: string | null; ref: string | null } | null;
  /** Date of the samples (band) or of the curve (estimate). */
  date: string | null;
  /** Estimate rows: the list price it starts from, its source ids, and the share of value kept at that age. */
  list_price: number | null;
  list_source_ids: string[];
  kept_share: number | null;
}

/** variant id → country code → bands (oldest build year first). */
export type VariantUsedPrices = Map<string, Record<string, VariantBand[]>>;

/**
 * How a band was made (Decision 064, shown in Nerd mode), copied from the row's own fields:
 * src = source name, url/ref = its link or file reference, date, n = counted listings (band), curve +
 * on (estimate: curve id and the countries it was fitted on), list + ls + kept (estimate: list price,
 * its source ids, value kept).
 */
export interface PriceHow {
  n?: number;
  src?: string;
  url?: string;
  ref?: string;
  date?: string;
  curve?: string;
  on?: string[];
  list?: number;
  ls?: string[];
  kept?: number;
}

/**
 * Compact per-row form for the client catalogue: country → [year, p25, median, p75, flags, how?].
 * flags (BAND_* in explore-data.ts): 1 = estimate (basis), 2 = low confidence, 4 = generation-scope band.
 */
export type CompactBand = [number, number | null, number, number | null, number, PriceHow?];
export type CompactBands = Record<string, CompactBand[]>;

const num = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);
const str = (v: unknown): string | null => (typeof v === "string" && v.trim() ? v : null);
const strs = (v: unknown): string[] => (Array.isArray(v) ? v.filter((x): x is string => typeof x === "string" && x.trim() !== "") : []);
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
  // Decision 064: `basis` says band or estimate; older files only had method / estimate.
  const estimate = b.basis === "estimate" || (b.basis !== "band" && (b.estimate === true || b.method === "model"));
  const src = b.source && typeof b.source === "object" ? (b.source as Record<string, unknown>) : null;
  return {
    build_year: b.build_year as number,
    p25: p25 !== null && p25 <= median ? p25 : null,
    median,
    p75: p75 !== null && p75 >= median ? p75 : null,
    currency: typeof b.currency === "string" ? b.currency : "",
    samples: Number.isInteger(b.samples) ? (b.samples as number) : 0,
    method: typeof b.method === "string" ? b.method : "",
    estimate,
    confidence: typeof b.confidence === "string" ? b.confidence : "",
    basis: estimate ? "estimate" : "band",
    scope: b.scope === "variant" || b.scope === "generation" ? b.scope : null,
    curve: str(b.curve),
    curve_fitted_on: strs(b.curve_fitted_on),
    source: src && str(src.name) ? { name: str(src.name)!, url: str(src.url), ref: str(src.ref) } : null,
    date: str(b.date),
    list_price: num(b.list_price) && b.list_price > 0 ? b.list_price : null,
    list_source_ids: strs(b.list_source_ids),
    kept_share: num(b.kept_share) && b.kept_share > 0 && b.kept_share <= 1.5 ? b.kept_share : null,
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
