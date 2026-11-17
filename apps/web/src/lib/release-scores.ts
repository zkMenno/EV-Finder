// Shortlist scores from the release (T-114, Decision 065): `shortlist_scores.json` next to the
// release's catalogue.json, written by the pipeline (T-069, pipeline/ev_pipeline/derive/shortlist.py).
// The web never computes factor scores itself: it applies the hard filters and sorts by these.
// Pure parsing + a compact per-row form for the browser. No runtime imports (scripts/budget.mjs
// loads this file in plain Node).
import type { ShortlistBand, ShortlistScoresRelease } from "@ev/schema";

export const SCORES_FILE = "shortlist_scores.json";

export const SCORE_BANDS: readonly ShortlistBand[] = ["shortlist", "consider", "fallback", "ruled-out", "not-enough-data"];

/** One profile combination (`road-tripper+kerbside.rural`): score 0..100, band, reason codes. */
export interface ComboScore {
  score: number;
  band: ShortlistBand;
  /** '+<factor>', '-<factor>', 'gate:<id>', 'bonus:<id>', 'penalty:<id>' (pipeline codes). */
  reasons: string[];
}

export interface VariantScores {
  /** Combination key → score. */
  scores: Record<string, ComboScore>;
  /** Trip profile id → factor id → 0..1 (null = not known). */
  factors: Record<string, Record<string, number | null>>;
  /** Trip profile id → factors / gates / penalties without data. */
  unknown: Record<string, string[]>;
  /** Derived inputs the scores used (winter_range_km, real_wh_km), all estimates. */
  derived: Record<string, number>;
}

export interface ReleaseScores {
  release: number;
  generatedAt: string;
  /** sha256 of the rules file the scores came from (shown in Nerd mode). */
  rulesSha: string | null;
  rulesPath: string | null;
  variants: Map<string, VariantScores>;
}

/**
 * Compact per-row form in the client catalogue: `s` combo → [score, band, ...reasons];
 * `f` trip → factor → 0..1 (unknown factors left out, listed in `u`); `d` derived values.
 */
export interface CompactScores {
  s: Record<string, [number, ShortlistBand, ...string[]]>;
  f?: Record<string, Record<string, number>>;
  u?: Record<string, string[]>;
  d?: Record<string, number>;
}

const isObj = (v: unknown): v is Record<string, unknown> => !!v && typeof v === "object" && !Array.isArray(v);
const num = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);
const strs = (v: unknown): string[] => (Array.isArray(v) ? v.filter((x): x is string => typeof x === "string") : []);

function comboScore(v: unknown): ComboScore | null {
  if (!isObj(v) || !num(v.score) || !SCORE_BANDS.includes(v.band as ShortlistBand)) return null;
  return { score: v.score, band: v.band as ShortlistBand, reasons: strs(v.reasons) };
}

/** Parses the file. Malformed variants or scores are skipped; a malformed file gives null. */
export function parseShortlistScores(doc: unknown): ReleaseScores | null {
  if (!isObj(doc) || !Array.isArray(doc.variants)) return null;
  const d = doc as unknown as ShortlistScoresRelease;
  const variants = new Map<string, VariantScores>();
  for (const v of doc.variants as unknown[]) {
    if (!isObj(v) || typeof v.variant_id !== "string" || !isObj(v.scores)) continue;
    const scores: Record<string, ComboScore> = {};
    for (const [k, s] of Object.entries(v.scores)) {
      const c = comboScore(s);
      if (c) scores[k] = c;
    }
    if (!Object.keys(scores).length) continue;
    const factors: VariantScores["factors"] = {};
    for (const [trip, fs] of Object.entries(isObj(v.factors) ? v.factors : {})) {
      if (!isObj(fs)) continue;
      factors[trip] = Object.fromEntries(Object.entries(fs).map(([k, x]) => [k, num(x) ? x : null]));
    }
    const unknown: VariantScores["unknown"] = {};
    for (const [trip, list] of Object.entries(isObj(v.unknown) ? v.unknown : {})) unknown[trip] = strs(list);
    const derived: VariantScores["derived"] = {};
    for (const [k, x] of Object.entries(isObj(v.derived) ? v.derived : {})) if (num(x)) derived[k] = x;
    variants.set(v.variant_id, { scores, factors, unknown, derived });
  }
  return {
    release: num(d.release) ? d.release : 0,
    generatedAt: typeof d.generated_at === "string" ? d.generated_at : "",
    rulesSha: typeof d.rules?.sha256 === "string" ? d.rules.sha256 : null,
    rulesPath: typeof d.rules?.path === "string" ? d.rules.path : null,
    variants,
  };
}

// compactScores lives in explore-data.ts (scripts/budget.mjs loads that file in plain Node, which
// needs it to have no runtime imports).

/** One combination's score from a compact row entry; null when the release has none for it. */
export function comboFrom(c: CompactScores | undefined, key: string): ComboScore | null {
  const e = c?.s[key];
  if (!e) return null;
  const [score, band, ...reasons] = e;
  return { score, band, reasons };
}
