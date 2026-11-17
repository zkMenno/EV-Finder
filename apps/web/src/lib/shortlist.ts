// Hero shortlist (T-080) and profile picker (T-067). Pure functions, shared by the server render and
// the client.
//
// Order of work (docs/spec/launch-scope.md): hard filters first (the visitor's own refine filters,
// country, new/used, budget, the profile's presets), then the score. Scores, bands, gates and
// reasons come only from the release (`shortlist_scores.json`, T-069; Decision 065): the web no
// longer scores factors itself, so the back-tested ranking is the one visitors see. The rules file
// still gives the picker, the presets, the factor names and their weights (display only).
import type { Country, ShortlistBand, UsedPriceBand } from "@ev/schema";
import generated from "@/config/shortlist-rules.generated.json";
import type { ExploreRow } from "./explore-data";
import { comboFrom } from "./release-scores";
import { applyFilters, priceFor } from "./filters";
import type { ExploreFilters } from "./state";

// ── Rules (src/config/shortlist-rules.generated.json, from data/editorial/shortlist_rules.yaml) ──

type Text = Partial<Record<string, string>>;

export interface RuleFactor {
  id: string;
  weight: number;
  field: string | null;
  kind: "linear" | "heat-pump" | "cooling" | "bool" | "unknown";
  scale?: number;
  poor?: number;
  great?: number;
}
export interface RuleGate {
  id: string;
  field: string;
  scale: number;
  min: number;
  rural_min: number | null;
  reason: Text;
}
export interface RulePreset {
  field: PresetField;
  min?: number;
  max?: number;
  why: Text;
}
export interface RulePenalty {
  id: string;
  points: number;
  applies_with: string | null;
  rule: string;
}
export interface RuleProfile {
  id: string;
  layer: boolean;
  picker: Record<string, string[]>;
  label: Text;
  short: Text;
  calibrated: boolean;
  calibration: string;
  bands: Record<string, { shortlist: number; consider: number }>;
  gates: RuleGate[];
  factors: RuleFactor[];
  extra_factors: RuleFactor[];
  weight_steps: Record<string, number>;
  bonuses: { id: string; points: number }[];
  penalties: RulePenalty[];
  filter_presets: RulePreset[];
  sort_default?: string;
}
export interface RuleModifier {
  id: string;
  picker: Record<string, string[]>;
  label: Text;
  weight_steps: Record<string, number>;
  use_rural_gates: boolean;
  penalties: RulePenalty[];
}
export interface RuleAddon {
  id: string;
  label: Text;
  weight_steps: Record<string, number>;
}
export interface ShortlistRules {
  schema: string;
  review: boolean;
  weight_step_factor: number;
  picker: { id: string; answers: string[]; skip_if?: Record<string, string[]> }[];
  profiles: RuleProfile[];
  modifiers: RuleModifier[];
  addons: RuleAddon[];
}

export const RULES = generated as unknown as ShortlistRules;

// ── Picker answers ──────────────────────────────────────────────────────────────────────────

export const ROLES = ["only", "main", "second"] as const;
export const TRIPS = ["never", "few_a_year", "monthly", "often"] as const;
export const CHARGES = ["home", "work", "public_only"] as const;
export const AREAS = ["city", "town", "countryside"] as const;
export type Role = (typeof ROLES)[number];
export type Trips = (typeof TRIPS)[number];
export type Charge = (typeof CHARGES)[number];
export type Area = (typeof AREAS)[number];

export interface Answers {
  role: Role | null;
  trips: Trips | null;
  charge: Charge | null;
  area: Area | null;
  /** Add-on "keep it 8+ years" (Decision 050). */
  keep8: boolean;
}

export const EMPTY_ANSWERS: Answers = { role: null, trips: null, charge: null, area: null, keep8: false };

/** Long trips are not asked for a second car (picker skip_if). */
export function asksTrips(a: Answers): boolean {
  return a.role !== "second";
}

/** Enough answers to pick a base profile. */
export function isComplete(a: Answers): boolean {
  return a.role !== null && (!asksTrips(a) || a.trips !== null);
}

export interface ResolvedProfile {
  base: RuleProfile;
  /** The kerbside-charger layer (no charger at home), stacked on the base profile. */
  layer: RuleProfile | null;
  modifier: RuleModifier | null;
  addons: RuleAddon[];
}

function matches(picker: Record<string, string[]>, a: Answers): boolean {
  const vals: Record<string, string | null> = {
    car_role: a.role,
    long_trips: a.trips,
    charge_where: a.charge,
    home_area: a.area,
  };
  const keys = Object.keys(picker);
  return keys.length > 0 && keys.every((k) => vals[k] !== null && vals[k] !== undefined && picker[k]!.includes(vals[k]!));
}

/** Answers → base profile + kerbside layer + where-you-live modifier + add-ons. Null until complete. */
export function resolveProfile(a: Answers, rules: ShortlistRules = RULES): ResolvedProfile | null {
  if (!isComplete(a)) return null;
  const bases = rules.profiles.filter((p) => !p.layer);
  const base = bases.find((p) => matches(p.picker, a));
  if (!base) return null;
  const layer = rules.profiles.find((p) => p.layer && matches(p.picker, a)) ?? null;
  const modifier = rules.modifiers.find((m) => matches(m.picker, a)) ?? null;
  const addons = a.keep8 ? rules.addons.filter((x) => x.id === "keep-8-years") : [];
  return { base, layer, modifier, addons };
}

// ── Filter presets ("Set by your profile") ──────────────────────────────────────────────────

export const PRESET_FIELDS = ["dc_km_per_20min", "real_range_km", "boot_l", "length_mm", "ac_kw", "seats", "towing_kg"] as const;
export type PresetField = (typeof PRESET_FIELDS)[number];

export interface ActivePreset extends RulePreset {
  /** Which profile set it (base or layer id). */
  from: string;
}

/** Base presets, then the layer's; one per field and direction, the stricter wins. */
export function presetsFor(rp: ResolvedProfile): ActivePreset[] {
  const out: ActivePreset[] = [];
  for (const p of [rp.base, ...(rp.layer ? [rp.layer] : [])]) {
    for (const pre of p.filter_presets) {
      const dir = pre.min !== undefined ? "min" : "max";
      const i = out.findIndex((o) => o.field === pre.field && (o.min !== undefined ? "min" : "max") === dir);
      const next: ActivePreset = { ...pre, from: p.id };
      if (i < 0) out.push(next);
      else if (dir === "min" ? (pre.min ?? 0) > (out[i]!.min ?? 0) : (pre.max ?? Infinity) < (out[i]!.max ?? Infinity)) out[i] = next;
    }
  }
  return out;
}

function fieldValue(row: ExploreRow, field: string): number | null {
  const v = (row as unknown as Record<string, unknown>)[field];
  return typeof v === "number" && Number.isFinite(v) ? v : null;
}

/** "fail" only on a known value outside the preset; unknown values pass (shown as not known yet). */
export function presetCheck(row: ExploreRow, p: RulePreset): "pass" | "fail" | "unknown" {
  const v = fieldValue(row, p.field);
  if (v === null) return "unknown";
  if (p.min !== undefined && v < p.min) return "fail";
  if (p.max !== undefined && v > p.max) return "fail";
  return "pass";
}

// ── Scores: read from the release, never computed here (Decision 065) ─────────────────────

export type Band = ShortlistBand;

/** The pipeline's key for a resolved profile (pipeline/ev_pipeline/derive/shortlist.py `combos`):
 *  trip profile + "+kerbside" (no charger at home) + ".urban" / ".rural" (no suffix = town). */
export function comboKey(rp: ResolvedProfile): string {
  const area = rp.modifier && rp.modifier.id !== "suburban" ? `.${rp.modifier.id}` : "";
  return `${rp.base.id}${rp.layer ? "+kerbside" : ""}${area}`;
}

export interface FactorView {
  id: string;
  /** 0..1 from the release; null when the car's value is not known (scored 0.5 there). */
  score: number | null;
  /** The rule weight after the layer's and modifier's weight steps (display only). */
  weight: number;
}

export interface Adjustment {
  id: string;
  points: number;
}

export interface PickScore {
  score: number;
  band: Band;
  /** Release reason codes ('+dc-speed', 'bonus:newest-version', …). */
  reasons: string[];
  factors: FactorView[];
  adjustments: Adjustment[];
  /** Factor ids without data (from the release). */
  unknown: string[];
  /** Release-derived inputs (winter_range_km, real_wh_km), estimates. */
  derived: Record<string, number>;
}

/** Weight steps from the kerbside layer and the where-you-live modifier (the pipeline's combos;
 *  add-ons such as keep-8-years are not in the release yet, so they don't change the order). */
function steps(rp: ResolvedProfile): Record<string, number> {
  const out: Record<string, number> = {};
  for (const src of [rp.layer?.weight_steps, rp.modifier?.weight_steps]) {
    for (const [k, n] of Object.entries(src ?? {})) out[k] = (out[k] ?? 0) + n;
  }
  return out;
}

/** The factor rows of a profile with their effective weights (for the Nerd table). */
export function factorRows(rp: ResolvedProfile, rules: ShortlistRules = RULES): { id: string; weight: number }[] {
  const st = steps(rp);
  return [...rp.base.factors, ...(rp.layer?.extra_factors ?? [])].map((f) => ({
    id: f.id,
    weight: Math.round(f.weight * Math.pow(rules.weight_step_factor, st[f.id] ?? 0) * 10) / 10,
  }));
}

/** The release score of one row for a profile; null when the release has none for it. */
export function scoreFor(row: ExploreRow, rp: ResolvedProfile, rules: ShortlistRules = RULES): PickScore | null {
  const c = comboFrom(row.shortlist, comboKey(rp));
  if (!c) return null;
  const trip = rp.base.id;
  const fv = row.shortlist?.f?.[trip] ?? {};
  const unknownAll = row.shortlist?.u?.[trip] ?? [];
  const factors = factorRows(rp, rules).map((f) => ({ ...f, score: typeof fv[f.id] === "number" ? fv[f.id]! : null }));
  const points = new Map<string, number>();
  for (const b of rp.base.bonuses) points.set(`bonus:${b.id}`, b.points);
  for (const p of [...rp.base.penalties, ...(rp.modifier?.penalties ?? [])]) points.set(`penalty:${p.id}`, p.points);
  const adjustments = c.reasons
    .filter((r) => r.startsWith("bonus:") || r.startsWith("penalty:"))
    .map((r) => ({ id: r.slice(r.indexOf(":") + 1), points: points.get(r) ?? 0 }));
  return {
    score: c.score,
    band: c.band,
    reasons: c.reasons,
    factors,
    adjustments,
    unknown: factors.filter((f) => f.score === null && unknownAll.includes(f.id)).map((f) => f.id),
    derived: row.shortlist?.d ?? {},
  };
}

/** Explore's "Suggested" sort: the release score; ruled out or not scored → null (sorted last). */
export function suggestedScore(row: ExploreRow, rp: ResolvedProfile): number | null {
  const c = comboFrom(row.shortlist, comboKey(rp));
  return c && c.band !== "ruled-out" ? c.score : null;
}

// ── Prices (Decision 064): used band → used price estimate → new price → none ─────────────

export type Condition = "any" | "new" | "used";
export const CONDITIONS: readonly Condition[] = ["any", "new", "used"];

/** Where a price comes from (Decision 064): a real used band, our used price estimate, or the new price. */
export type PriceBasis = "band" | "estimate" | "new";

export interface PriceFit {
  kind: "used" | "new";
  basis: PriceBasis;
  /** The amount compared with the budget (used: the band's median). */
  amount: number;
  low: number | null;
  high: number | null;
  /** Build years this price is for (used bands with an age band), else the variant's years. */
  yearFrom: number;
  yearTo: number | null;
  samples?: number;
  /** Our model, not counted listings (T-081 `method: model`); same as basis "estimate". */
  estimate?: boolean;
  /** Built on a list price from a nearby year or another country. */
  lowConfidence?: boolean;
  /** Estimate method inputs for Nerd mode: the list price and the share of value kept. */
  listPrice?: number | null;
  keptShare?: number | null;
  /** Source ids (estimate: of the list price) or a source name (band). */
  sources?: string[];
}

/** Bands for one generation in one country with enough samples (PriceBand.MIN_SAMPLES = 5). */
export type UsedBands = Record<string, UsedPriceBand[]>;

/** "3-5" → [3, 5]; "8+" → [8, 30]; anything else null. */
export function ageRange(s: string | null | undefined): [number, number] | null {
  if (!s) return null;
  const m = /^(\d+)\s*(?:-|–|to)\s*(\d+)$/.exec(s.trim());
  if (m) return [Number(m[1]), Number(m[2])];
  const p = /^(\d+)\s*\+$/.exec(s.trim());
  return p ? [Number(p[1]), 30] : null;
}

/**
 * The used price that fits from this generation's sourced bands (real bands, `Catalogue.used_prices`):
 * the youngest band whose median is within the budget (no budget: the youngest). Build years come
 * from the band's age; the year of the release is "now" so a page renders the same on every machine.
 */
export function usedFit(row: ExploreRow, bands: UsedPriceBand[] | undefined, budget: number | null, nowYear: number): PriceFit | null {
  if (!bands?.length) return null;
  const opts = bands
    .map((b) => {
      const age = ageRange(b.age_band_years);
      const from = age ? Math.max(row.year_start, nowYear - age[1]) : row.year_start;
      const to = age ? Math.min(row.year_end ?? nowYear, nowYear - age[0]) : (row.year_end ?? null);
      return { b, from, to, youngest: age ? age[0] : 99 };
    })
    .filter((o) => o.to === null || o.from <= o.to)
    .sort((x, y) => x.youngest - y.youngest);
  const fit = budget === null ? opts[0] : opts.find((o) => o.b.median <= budget);
  if (!fit) return null;
  return {
    kind: "used",
    basis: "band",
    amount: fit.b.median,
    low: fit.b.p25 ?? null,
    high: fit.b.p75 ?? null,
    yearFrom: fit.from,
    yearTo: fit.to,
    samples: fit.b.samples,
    sources: [fit.b.source_id],
  };
}

/**
 * Per-variant bands by build year (T-081, `used_prices.json`) of one basis: the build years within
 * the variant's years (narrowed by the visitor's build-year filter) whose median fits the budget;
 * the price shown is the newest of those years (no budget: the newest year). `estimate` picks the
 * model bands (Decision 064 step 2), otherwise the counted-listing bands (step 1); undefined = both.
 */
export function variantFit(
  row: ExploreRow,
  country: Country,
  budget: number | null,
  years: { from?: number | null; to?: number | null } = {},
  estimate?: boolean,
): PriceFit | null {
  const list = row.used_bands?.[country];
  if (!list?.length) return null;
  const start = Math.max(row.year_start, years.from ?? -Infinity);
  const end = Math.min(row.year_end ?? Infinity, years.to ?? Infinity);
  const inYears = list.filter(([y, , , , flags]) => y >= start && y <= end && (estimate === undefined || ((flags & 1) === 1) === estimate));
  const fits = budget === null ? inYears : inYears.filter(([, , median]) => median <= budget);
  if (!fits.length) return null;
  const newest = fits[fits.length - 1]!;
  const [year, p25, median, p75, flags, listPrice, keptShare, sources] = newest;
  const est = (flags & 1) === 1;
  return {
    kind: "used",
    basis: est ? "estimate" : "band",
    amount: median,
    low: p25,
    high: p75,
    yearFrom: budget === null ? year : fits[0]![0],
    yearTo: year,
    estimate: est,
    lowConfidence: (flags & 2) === 2,
    listPrice: listPrice ?? null,
    keptShare: keptShare ?? null,
    sources: sources ? sources.split(",") : [],
  };
}

function newFit(row: ExploreRow, country: Country): PriceFit | null {
  if (row.on_sale_new !== true) return null;
  const p = priceFor(row, country);
  return p === null ? null : { kind: "new", basis: "new", amount: p, low: null, high: null, yearFrom: row.year_start, yearTo: row.year_end ?? null };
}

/**
 * "fits": a price within the budget (or any price, without a budget); "over": the car has a price
 * but none fits; "unpriced": no price of any kind (never in the top 5, listed last, Decision 064).
 */
export type PriceStatus = "fits" | "over" | "unpriced";

/**
 * The price the budget compares against (Decision 064), in order: (1) a real used band for those
 * build years (variant bands from counted listings, else the generation's sourced bands); (2) our
 * used price estimate (variant model bands: list price × value kept at that age); (3) the new
 * price, for cars on sale new. Used and new both fitting: the cheaper one is shown.
 */
export function priceFit(
  row: ExploreRow,
  opts: { country: Country; cond: Condition; budget: number | null; usedBands?: UsedBands; nowYear: number; yearMin?: number | null; yearMax?: number | null },
): { fit: PriceFit | null; status: PriceStatus } {
  const yrs = { from: opts.yearMin, to: opts.yearMax };
  const b = opts.budget;
  let used: PriceFit | null = null;
  let hasPrice = false;
  if (opts.cond !== "new") {
    const gen = opts.usedBands?.[row.generation_id];
    // Step 1, real bands: the variant's counted-listing bands, else the generation's sourced bands.
    const real = variantFit(row, opts.country, b, yrs, false) ?? usedFit(row, gen, b, opts.nowYear);
    // Step 2, our estimate, only where no real band fits.
    used = real ?? variantFit(row, opts.country, b, yrs, true);
    hasPrice = !!(variantFit(row, opts.country, null, yrs) ?? usedFit(row, gen, null, opts.nowYear));
  }
  let fresh: PriceFit | null = null;
  if (opts.cond !== "used") {
    const n = newFit(row, opts.country);
    if (n) hasPrice = true;
    if (n && (b === null || n.amount <= b)) fresh = n;
  }
  const fit = used && fresh ? (fresh.amount < used.amount ? fresh : used) : (used ?? fresh);
  return { fit, status: fit ? "fits" : hasPrice ? "over" : "unpriced" };
}

// ── Ranking: one card per model, top 10, top 5 = "your shortlist" ───────────────────────────

export const TOP_N = 10;
export const SHORTLIST_N = 5;

export interface HeroQuery {
  country: Country;
  cond: Condition;
  budget: number | null;
  /** The visitor's own refine filters (strict, as in Explore). */
  filters: ExploreFilters;
  /** Preset fields the visitor removed. */
  presetsOff: readonly string[];
  usedBands?: UsedBands;
  nowYear: number;
}

export interface HeroPick {
  rank: number;
  row: ExploreRow;
  result: PickScore;
  price: PriceFit | null;
  /** Presets this car passes only because the value is not known yet. */
  presetUnknown: PresetField[];
  /** Other variants of the same model that also qualified. */
  alternatives: number;
}

export interface HeroResult {
  /** "no-scores": the release has no shortlist_scores.json, so nothing is ranked (Decision 065). */
  status: "ranked" | "no-scores";
  picks: HeroPick[];
  /** How many of the picks form "Your shortlist": priced cars only, at most SHORTLIST_N (Decision 064). */
  shortlistN: number;
  /** Models that qualified (before cutting to TOP_N). */
  qualifying: number;
  /** How many of the qualifying picks have no price yet. */
  unpriced: number;
  ruledOutByGate: number;
  overBudget: number;
  /** Variants that passed the filters but have no release score for this profile. */
  unscored: number;
}

export function rankHero(
  rows: readonly ExploreRow[],
  rp: ResolvedProfile,
  q: HeroQuery,
  opts: { hasScores: boolean },
  rules: ShortlistRules = RULES,
): HeroResult {
  const empty: HeroResult = { status: "no-scores", picks: [], shortlistN: 0, qualifying: 0, unpriced: 0, ruledOutByGate: 0, overBudget: 0, unscored: 0 };
  if (!opts.hasScores) return empty;
  const presets = presetsFor(rp).filter((p) => !q.presetsOff.includes(p.field));
  let ruledOutByGate = 0;
  let overBudget = 0;
  let unscored = 0;
  const best = new Map<string, HeroPick & { count: number }>();
  for (const row of applyFilters([...rows], q.filters, q.country)) {
    if (q.cond === "new" && row.on_sale_new !== true) continue;
    const checks = presets.map((p) => [p.field, presetCheck(row, p)] as const);
    if (checks.some(([, c]) => c === "fail")) continue;
    // Budget is a hard filter on the price (Decision 064); a car with no price at all stays, last.
    const { fit, status } = priceFit(row, { ...q, yearMin: q.filters.yearMin, yearMax: q.filters.yearMax });
    if (status === "over") {
      overBudget++;
      continue;
    }
    const result = scoreFor(row, rp, rules);
    if (!result) {
      unscored++;
      continue;
    }
    if (result.band === "ruled-out") {
      ruledOutByGate++;
      continue;
    }
    const pick = {
      rank: 0,
      row,
      result,
      price: fit,
      presetUnknown: checks.filter(([, c]) => c === "unknown").map(([f]) => f),
      alternatives: 0,
      count: 1,
    };
    const cur = best.get(row.model_id);
    if (!cur) best.set(row.model_id, pick);
    else {
      // A priced version beats an unpriced one; then the release score; then the newer one.
      const priced = Number(fit !== null) - Number(cur.price !== null);
      const better =
        priced > 0 ||
        (priced === 0 &&
          (result.score > cur.result.score || (result.score === cur.result.score && row.year_start > cur.row.year_start)));
      if (better) best.set(row.model_id, { ...pick, count: cur.count + 1 });
      else cur.count++;
    }
  }
  // Priced cars first (Decision 064: a car with no price is listed after every priced car), then
  // the release score.
  const sorted = [...best.values()].sort(
    (a, b) =>
      Number(b.price !== null) - Number(a.price !== null) ||
      b.result.score - a.result.score ||
      (b.row.real_range_km ?? 0) - (a.row.real_range_km ?? 0) ||
      `${a.row.make_name} ${a.row.model_name}`.localeCompare(`${b.row.make_name} ${b.row.model_name}`),
  );
  const picks = sorted.slice(0, TOP_N).map(({ count, ...p }, i) => ({ ...p, rank: i + 1, alternatives: count - 1 }));
  return {
    status: "ranked",
    picks,
    shortlistN: Math.min(SHORTLIST_N, picks.filter((p) => p.price !== null).length),
    qualifying: sorted.length,
    unpriced: picks.filter((p) => p.price === null).length,
    ruledOutByGate,
    overBudget,
    unscored,
  };
}

// ── "Why it ranks here" ─────────────────────────────────────────────────────────────────────

export interface Reason {
  id: string;
}

/** The release's strongest plus factors (in its order, at most `max`) plus its bonuses. */
export function reasons(result: PickScore, max = 2): Reason[] {
  const plus = result.reasons.filter((r) => r.startsWith("+")).slice(0, max).map((r) => ({ id: r.slice(1) }));
  return plus;
}
