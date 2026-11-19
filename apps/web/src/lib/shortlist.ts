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
import { BAND_ESTIMATE, BAND_GENERATION, BAND_LOW, type ExploreRow } from "./explore-data";
import type { PriceHow } from "./variant-prices";
import { comboFrom } from "./release-scores";
import { applyFilters, priceFor } from "./filters";
import { COUNTRIES } from "@/config/countries";
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
  /**
   * The car's own figure behind the factor, with the field it came from (T-097): what a buyer reads
   * ("387 km in 20 min"), never the scaled scoring unit (×3 = km/h, ×10 = Wh/km, basis scale).
   * Winter range and efficiency read the release's derived estimates, as the release scores them.
   */
  field: string | null;
  raw: number | string | boolean | null;
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

/** Which value a factor's score is built on when it isn't the rule's own `field`: the release's
 *  derived estimates (mirrors `field_overrides` in pipeline/ev_pipeline/derive/shortlist_params.yaml). */
const SCORED_FIELD: Record<string, string> = { "winter-range": "winter_range_km", efficiency: "real_wh_km" };

/** The car's own figure behind a factor (T-097), unscaled; null when not known. Yes/no factors
 *  whose field is a structure (bidi modes) read the release's 0/1 score. */
function ownValue(
  f: RuleFactor,
  row: ExploreRow,
  derived: Record<string, number>,
  score: number | null,
): { field: string | null; raw: number | string | boolean | null } {
  const field = SCORED_FIELD[f.id] ?? f.field;
  if (field === null) return { field, raw: null };
  const v = derived[field] ?? (row as unknown as Record<string, unknown>)[field];
  if (typeof v === "number" && Number.isFinite(v)) return { field, raw: v };
  if (typeof v === "boolean") return { field, raw: v };
  if (typeof v === "string" && v !== "not-disclosed") return { field, raw: v };
  if (f.kind === "bool" && (score === 0 || score === 1)) return { field, raw: score === 1 };
  return { field, raw: null };
}

/** The release score of one row for a profile; null when the release has none for it. */
export function scoreFor(row: ExploreRow, rp: ResolvedProfile, rules: ShortlistRules = RULES): PickScore | null {
  const c = comboFrom(row.shortlist, comboKey(rp));
  if (!c) return null;
  const trip = rp.base.id;
  const fv = row.shortlist?.f?.[trip] ?? {};
  const unknownAll = row.shortlist?.u?.[trip] ?? [];
  const derived = row.shortlist?.d ?? {};
  const rule = new Map([...rp.base.factors, ...(rp.layer?.extra_factors ?? [])].map((f) => [f.id, f]));
  const factors = factorRows(rp, rules).map((f) => {
    const score = typeof fv[f.id] === "number" ? fv[f.id]! : null;
    const r = rule.get(f.id);
    return { ...f, score, ...(r ? ownValue(r, row, derived, score) : { field: null, raw: null }) };
  });
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
    derived,
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
  /** Band rows: "generation" = the generation's samples standing in, "typical for this generation" (Decision 069). */
  scope?: "variant" | "generation";
  /** How the figure was made, from the release row's own fields (Nerd mode, Decision 064). */
  how?: PriceHow;
  /** Generation bands from the catalogue (`usedFit`): their source ids. */
  sourceIds?: string[];
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
    scope: "generation",
    sourceIds: [fit.b.source_id],
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
  const isEst = (flags: number) => (flags & BAND_ESTIMATE) === BAND_ESTIMATE;
  // An estimate never stands in for a build year that has a real band (Decision 064, step 1 first).
  const realYears = new Set(list.filter(([, , , , f]) => !isEst(f)).map(([y]) => y));
  const inYears = list.filter(
    ([y, , , , flags]) => y >= start && y <= end && (estimate === undefined || isEst(flags) === estimate) && !(estimate === true && realYears.has(y)),
  );
  const fits = budget === null ? inYears : inYears.filter(([, , median]) => median <= budget);
  if (!fits.length) return null;
  const newest = fits[fits.length - 1]!;
  const [year, p25, median, p75, flags, how] = newest;
  const est = isEst(flags);
  return {
    kind: "used",
    basis: est ? "estimate" : "band",
    amount: median,
    low: p25,
    high: p75,
    yearFrom: budget === null ? year : fits[0]![0],
    yearTo: year,
    estimate: est,
    lowConfidence: (flags & BAND_LOW) === BAND_LOW,
    ...(est ? {} : { scope: (flags & BAND_GENERATION) === BAND_GENERATION ? ("generation" as const) : ("variant" as const) }),
    ...(how ? { how } : {}),
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
  /** 1-based place among the priced picks; null for a car with no price (never ranked as a pick, Decision 064). */
  rank: number | null;
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
  /** Priced picks; they come first in `picks`. The rest have no price and no rank. */
  priced: number;
  /** Models that qualified (before cutting to TOP_N). */
  qualifying: number;
  /** How many of the picks have no price yet. */
  unpriced: number;
  /** T-152: models left out as fill-ins because what we know of their price is far over budget (only when there was room). */
  unpricedFar: number;
  /** T-152: unpriced models that fit but were cut by the UNPRICED_MAX cap. */
  unpricedCapped: number;
  ruledOutByGate: number;
  overBudget: number;
  /** Variants that passed the filters but have no release score for this profile. */
  unscored: number;
}

/**
 * Unpriced versions don't carry an expensive model into a cheap list (T-115 review, Decision 064).
 * An unpriced variant counts as over budget when its generation has known prices and none of them
 * fits; when its generation has no price at all, the same test runs on the model's other
 * generations. Any sibling that fits keeps it in (listed last, as unpriced). No budget: never over.
 * Prices are compared before the visitor's refine filters, so a filter can't hide the evidence.
 */
export function siblingsOverBudget(
  rows: readonly ExploreRow[],
  q: Pick<HeroQuery, "budget" | "cond">,
  pf: (row: ExploreRow) => { status: PriceStatus },
): (row: ExploreRow) => boolean {
  if (q.budget === null) return () => false;
  const groups = new Map<string, "fits" | "over">();
  for (const row of rows) {
    if (q.cond === "new" && row.on_sale_new !== true) continue;
    const st = pf(row).status;
    if (st === "unpriced") continue;
    for (const k of [`g:${row.generation_id}`, `m:${row.model_id}`]) {
      if (st === "fits") groups.set(k, "fits");
      else if (!groups.has(k)) groups.set(k, "over");
    }
  }
  return (row) => (groups.get(`g:${row.generation_id}`) ?? groups.get(`m:${row.model_id}`)) === "over";
}

/** An unpriced fill-in is left out when the cheapest price we hold is above this × the budget (T-152). */
export const FAR_OVER_FACTOR = 2;
/** At most this many unpriced fill-ins, after every priced car, when a budget is set (T-152). */
export const UNPRICED_MAX = 3;

const CURRENCY_OF: Partial<Record<string, string>> = Object.fromEntries(Object.values(COUNTRIES).map((c) => [c.code, c.currency]));

/**
 * Every price the release holds for a row in `currency`, any country (T-152): new list prices
 * (on sale or not) and used band medians. Other currencies are skipped, never converted.
 */
export function heldPrices(row: ExploreRow, currency: string): number[] {
  const out: number[] = [];
  for (const m of Object.values(row.price_new ?? {})) if (m && m.currency === currency) out.push(m.amount);
  for (const [cc, bands] of Object.entries(row.used_bands ?? {})) {
    if (CURRENCY_OF[cc] !== currency) continue;
    for (const b of bands ?? []) out.push(b[2]);
  }
  return out;
}

/**
 * T-152: an unpriced car (no price where the visitor lives) is not used as a fill-in when the
 * cheapest price we hold for it elsewhere is more than FAR_OVER_FACTOR × the budget. Evidence, in
 * order: the car's own prices in other countries; else its generation's; else, for a car with no
 * price anywhere, the cheapest car of its segment (an E or F segment car isn't shown at €15k
 * because no E/F car we know of costs under €30k). Same currency only. It only ever removes a car;
 * no price is made up or shown for it. No budget: never.
 */
export function farOverBudget(rows: readonly ExploreRow[], q: Pick<HeroQuery, "budget" | "country">): (row: ExploreRow) => boolean {
  if (q.budget === null) return () => false;
  const currency = CURRENCY_OF[q.country];
  if (!currency) return () => false;
  const limit = q.budget * FAR_OVER_FACTOR;
  const own = new Map<ExploreRow, number>();
  const gen = new Map<string, number>();
  const seg = new Map<string, number>();
  const lower = (m: Map<string, number>, k: string, v: number) => m.set(k, Math.min(m.get(k) ?? Infinity, v));
  for (const r of rows) {
    const held = heldPrices(r, currency);
    if (!held.length) continue;
    const min = Math.min(...held);
    own.set(r, min);
    lower(gen, r.generation_id, min);
    if (r.segment) lower(seg, r.segment, min);
  }
  return (row) => {
    const cheapest = own.get(row) ?? gen.get(row.generation_id) ?? (row.segment ? seg.get(row.segment) : undefined);
    return cheapest !== undefined && cheapest > limit;
  };
}

export function rankHero(
  rows: readonly ExploreRow[],
  rp: ResolvedProfile,
  q: HeroQuery,
  opts: { hasScores: boolean },
  rules: ShortlistRules = RULES,
): HeroResult {
  const empty: HeroResult = { status: "no-scores", picks: [], shortlistN: 0, priced: 0, qualifying: 0, unpriced: 0, unpricedFar: 0, unpricedCapped: 0, ruledOutByGate: 0, overBudget: 0, unscored: 0 };
  if (!opts.hasScores) return empty;
  const presets = presetsFor(rp).filter((p) => !q.presetsOff.includes(p.field));
  let ruledOutByGate = 0;
  let overBudget = 0;
  let unscored = 0;
  const best = new Map<string, HeroPick & { count: number }>();
  const priceOpts = { ...q, yearMin: q.filters.yearMin, yearMax: q.filters.yearMax };
  const fitOf = new Map<ExploreRow, ReturnType<typeof priceFit>>();
  const pf = (row: ExploreRow) => {
    let v = fitOf.get(row);
    if (!v) fitOf.set(row, (v = priceFit(row, priceOpts)));
    return v;
  };
  const over = siblingsOverBudget(rows, q, pf);
  const far = farOverBudget(rows, q);
  const farModels = new Set<string>();
  for (const row of applyFilters([...rows], q.filters, q.country)) {
    if (q.cond === "new" && row.on_sale_new !== true) continue;
    const checks = presets.map((p) => [p.field, presetCheck(row, p)] as const);
    if (checks.some(([, c]) => c === "fail")) continue;
    // Budget is a hard filter on the price (Decision 064); a car with no price at all stays, last.
    // An unpriced version whose siblings are all over budget doesn't carry its model in either.
    const { fit, status } = pf(row);
    if (status === "over" || (status === "unpriced" && over(row))) {
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
    // T-152: nor does an unpriced car whose prices elsewhere (else its segment's) are far over budget.
    // Checked after the score and gate, so "left out" counts only cars that would have been shown.
    if (status === "unpriced" && far(row)) {
      overBudget++;
      farModels.add(row.model_id);
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
  // Only priced cars get a place number: an unpriced car is never a ranked pick, so it can't sit in
  // places 1-5 when fewer than 5 priced cars fit (A-35 B2 on release 2: 1 priced + 8 unpriced at €15k).
  // With a budget, at most UNPRICED_MAX unpriced fill-ins follow the priced cars (T-152).
  const pricedAll = sorted.filter((p) => p.price !== null);
  const unpricedAll = sorted.filter((p) => p.price === null);
  const pricedTop = pricedAll.slice(0, TOP_N);
  const room = TOP_N - pricedTop.length;
  const fill = unpricedAll.slice(0, q.budget === null ? room : Math.min(room, UNPRICED_MAX));
  const picks = [...pricedTop, ...fill].map(({ count, ...p }, i) => ({ ...p, rank: p.price !== null ? i + 1 : null, alternatives: count - 1 }));
  const priced = pricedTop.length;
  for (const m of best.keys()) farModels.delete(m);
  return {
    status: "ranked",
    picks,
    shortlistN: Math.min(SHORTLIST_N, priced),
    priced,
    qualifying: sorted.length,
    unpriced: fill.length,
    unpricedFar: room > 0 ? farModels.size : 0,
    unpricedCapped: Math.min(unpricedAll.length, room) - fill.length,
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
