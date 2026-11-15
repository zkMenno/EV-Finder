// Hero shortlist (T-080) and profile picker (T-067): the shortlist rules (Decisions 038 / 050) applied
// in the browser to published fields. Pure functions, shared by the server render and the client.
//
// Order of work (docs/spec/launch-scope.md): hard filters first (the visitor's own refine filters,
// country, new/used, budget), then the profile's gates and presets, then the score. A value we
// don't have never rules a car out and never counts as low: it scores neutral (0.5) and is shown
// as "not known yet" (Decision 038).
import type { Country, UsedPriceBand } from "@ev/schema";
import generated from "@/config/shortlist-rules.generated.json";
import type { ExploreRow } from "./explore-data";
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

// ── Scoring ─────────────────────────────────────────────────────────────────────────────────

export type Band = "shortlist" | "consider" | "fallback";

export interface FactorScore {
  id: string;
  /** 0..1; 0.5 when unknown. */
  score: number;
  known: boolean;
  /** Effective weight after weight steps (before renormalising). */
  weight: number;
  /** The value the factor read, in the rule's unit (e.g. km/h for road-tripper DC). */
  value: number | string | boolean | null;
}

export interface Adjustment {
  id: string;
  points: number;
}

export interface ScoreResult {
  score: number;
  band: Band;
  /** First gate failed on a known value, else null. */
  ruledOut: RuleGate | null;
  factors: FactorScore[];
  adjustments: Adjustment[];
  /** Factor ids without data (scored neutral). */
  unknown: string[];
}

export interface ScoreContext {
  /** model_id → newest year_start and how many distinct year_starts the model has. */
  modelYears: Map<string, { newest: number; distinct: number }>;
}

export function scoreContext(rows: readonly ExploreRow[]): ScoreContext {
  const years = new Map<string, Set<number>>();
  for (const r of rows) {
    const s = years.get(r.model_id) ?? new Set<number>();
    s.add(r.year_start);
    years.set(r.model_id, s);
  }
  const modelYears = new Map<string, { newest: number; distinct: number }>();
  for (const [id, s] of years) modelYears.set(id, { newest: Math.max(...s), distinct: s.size });
  return { modelYears };
}

/** Same maths as data/editorial/backtest_rules.py `lin`: linear, clamped, unknown = 0.5. */
export function lin(x: number | null, poor: number, great: number): number {
  if (x === null) return 0.5;
  return Math.max(0, Math.min(1, (x - poor) / (great - poor)));
}

function factorScore(row: ExploreRow, f: RuleFactor, weight: number): FactorScore {
  const base = { id: f.id, weight };
  switch (f.kind) {
    case "linear": {
      const raw = f.field ? fieldValue(row, f.field) : null;
      const v = raw === null ? null : raw * (f.scale ?? 1);
      return { ...base, score: lin(v, f.poor!, f.great!), known: v !== null, value: v };
    }
    case "heat-pump": {
      const hp = row.heat_pump;
      const s = hp === "standard" ? 1 : hp === "option" ? 0.6 : hp === "none" ? 0 : 0.5;
      return { ...base, score: s, known: hp === "standard" || hp === "option" || hp === "none", value: hp ?? null };
    }
    case "cooling": {
      const c = row.cooling_id;
      const s = c === "liquid" || c === "refrigerant" ? 1 : c === "air" || c === "passive" ? 0 : 0.5;
      return { ...base, score: s, known: s !== 0.5, value: c ?? null };
    }
    case "bool": {
      const v = f.field ? (row as unknown as Record<string, unknown>)[f.field] : undefined;
      const known = typeof v === "boolean";
      return { ...base, score: v === true ? 1 : v === false ? 0 : 0.5, known, value: known ? (v as boolean) : null };
    }
    default:
      return { ...base, score: 0.5, known: false, value: null };
  }
}

function bandKey(row: ExploreRow, bands: RuleProfile["bands"]): string {
  const v = row.voltage_class_id;
  const high = v === "800v" || v === "900v-plus" || (row.voltage_nominal_v ?? 0) >= 600;
  if (high && bands["800v"]) return "800v";
  if (v === "400v" && bands["400v"]) return "400v";
  return bands.default ? "default" : "400v";
}

/** "Wide or heavy SUV": kerb mass over ~2,300 kg (width is a gap field). Unknown mass = no penalty. */
function tooBig(row: ExploreRow): boolean {
  if (typeof row.kerb_mass_kg === "number") return row.kerb_mass_kg > 2300;
  // Mass in running order includes a 75 kg driver (Decision 023).
  if (typeof row.mass_running_order_kg === "number") return row.mass_running_order_kg > 2375;
  return false;
}

function penaltyApplies(id: string, row: ExploreRow): boolean {
  return id === "too-big-for-b-roads" ? tooBig(row) : false;
}

export function scoreRow(row: ExploreRow, rp: ResolvedProfile, ctx: ScoreContext, rules: ShortlistRules = RULES): ScoreResult {
  const { base, layer, modifier, addons } = rp;
  const rural = modifier?.use_rural_gates === true;
  let ruledOut: RuleGate | null = null;
  for (const g of base.gates) {
    const raw = fieldValue(row, g.field);
    if (raw === null) continue;
    const lim = rural && g.rural_min !== null ? g.rural_min : g.min;
    if (raw * g.scale < lim) {
      ruledOut = g;
      break;
    }
  }
  const steps: Record<string, number> = {};
  for (const src of [layer?.weight_steps, modifier?.weight_steps, ...addons.map((a) => a.weight_steps)]) {
    for (const [k, n] of Object.entries(src ?? {})) steps[k] = (steps[k] ?? 0) + n;
  }
  const rows = [...base.factors, ...(layer?.extra_factors ?? [])];
  const factors = rows.map((f) => factorScore(row, f, f.weight * Math.pow(rules.weight_step_factor, steps[f.id] ?? 0)));
  const wsum = factors.reduce((s, f) => s + f.weight, 0);
  let pts = wsum > 0 ? (100 * factors.reduce((s, f) => s + f.score * f.weight, 0)) / wsum : 50;

  const adjustments: Adjustment[] = [];
  const add = (id: string, points: number) => {
    adjustments.push({ id, points });
    pts += points;
  };
  const my = ctx.modelYears.get(row.model_id);
  const versions = my !== undefined && my.distinct > 1;
  for (const b of base.bonuses) {
    if (b.id === "newest-version" && versions && row.year_start === my.newest) add(b.id, b.points);
    if (b.id === "lfp-daily-100" && row.charge_100_daily === true) add(b.id, b.points);
  }
  const applied = new Set<string>();
  for (const p of base.penalties) {
    if (p.id === "older-version") {
      if (versions && row.year_start < my.newest) add(p.id, p.points);
      continue;
    }
    if (p.applies_with !== null && p.applies_with !== modifier?.id) continue;
    if (penaltyApplies(p.id, row)) {
      add(p.id, p.points);
      applied.add(p.id);
    }
  }
  for (const p of modifier?.penalties ?? []) {
    if (!applied.has(p.id) && penaltyApplies(p.id, row)) add(p.id, p.points);
  }

  const score = Math.round(pts * 10) / 10;
  const b = base.bands[bandKey(row, base.bands)] ?? { shortlist: 60, consider: 50 };
  const band: Band = score >= b.shortlist ? "shortlist" : score >= b.consider ? "consider" : "fallback";
  return { score, band, ruledOut, factors, adjustments, unknown: factors.filter((f) => !f.known).map((f) => f.id) };
}

// ── Prices: used band for the build years that fit, else the new price ─────────────────────

export type Condition = "any" | "new" | "used";
export const CONDITIONS: readonly Condition[] = ["any", "new", "used"];

export interface PriceFit {
  kind: "used" | "new";
  /** The amount compared with the budget (used: the band's median). */
  amount: number;
  low: number | null;
  high: number | null;
  /** Build years this price is for (used bands with an age band), else the variant's years. */
  yearFrom: number;
  yearTo: number | null;
  samples?: number;
  /** Our model, not counted listings (T-081 `method: model`). */
  estimate?: boolean;
  /** Built on a list price from a nearby year or another country. */
  lowConfidence?: boolean;
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
 * The used price that fits: among this generation's bands, the youngest one whose median is within
 * the budget (no budget: the youngest). Build years come from the band's age; the year of the
 * release is "now" so a page renders the same on every machine.
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
    amount: fit.b.median,
    low: fit.b.p25 ?? null,
    high: fit.b.p75 ?? null,
    yearFrom: fit.from,
    yearTo: fit.to,
    samples: fit.b.samples,
  };
}

/**
 * Per-variant bands by build year (T-081): the build years within the variant's years whose
 * typical price fits the budget; the price shown is the newest of those years (no budget: the
 * newest year). Null without bands for this country, or when none fits.
 */
export function variantFit(
  row: ExploreRow,
  country: Country,
  budget: number | null,
  years: { from?: number | null; to?: number | null } = {},
): PriceFit | null {
  const list = row.used_bands?.[country];
  if (!list?.length) return null;
  // Build years: the variant's own, narrowed by the visitor's build-year filter (refine).
  const start = Math.max(row.year_start, years.from ?? -Infinity);
  const end = Math.min(row.year_end ?? Infinity, years.to ?? Infinity);
  const inYears = list.filter(([y]) => y >= start && y <= end);
  const fits = budget === null ? inYears : inYears.filter(([, , median]) => median <= budget);
  if (!fits.length) return null;
  const newest = fits[fits.length - 1]!;
  const [year, p25, median, p75, flags] = newest;
  return {
    kind: "used",
    amount: median,
    low: p25,
    high: p75,
    yearFrom: budget === null ? year : fits[0]![0],
    yearTo: year,
    estimate: (flags & 1) === 1,
    lowConfidence: (flags & 2) === 2,
  };
}

function newFit(row: ExploreRow, country: Country): PriceFit | null {
  if (row.on_sale_new !== true) return null;
  const p = priceFor(row, country);
  return p === null ? null : { kind: "new", amount: p, low: null, high: null, yearFrom: row.year_start, yearTo: row.year_end ?? null };
}

/** The cheapest price that fits the condition and budget; `over` when every known price is over it. */
export function priceFit(
  row: ExploreRow,
  opts: { country: Country; cond: Condition; budget: number | null; usedBands?: UsedBands; nowYear: number; yearMin?: number | null; yearMax?: number | null },
): { fit: PriceFit | null; over: boolean } {
  const cands: PriceFit[] = [];
  if (opts.cond !== "new" && row.used_bands?.[opts.country]?.length) {
    // Per-variant bands by build year (T-081) win over generation bands.
    const yrs = { from: opts.yearMin, to: opts.yearMax };
    const v = variantFit(row, opts.country, opts.budget, yrs);
    if (v) cands.push(v);
    else {
      const any = variantFit(row, opts.country, null, yrs);
      if (any) cands.push({ ...any, amount: Infinity });
    }
  } else if (opts.cond !== "new") {
    const anyBand = usedFit(row, opts.usedBands?.[row.generation_id], null, opts.nowYear);
    const u = usedFit(row, opts.usedBands?.[row.generation_id], opts.budget, opts.nowYear);
    if (u) cands.push(u);
    else if (anyBand) cands.push({ ...anyBand, amount: Infinity });
  }
  if (opts.cond !== "used") {
    const n = newFit(row, opts.country);
    if (n) cands.push(n);
  }
  const known = cands.filter((c) => Number.isFinite(c.amount));
  const within = known.filter((c) => opts.budget === null || c.amount <= opts.budget).sort((a, b) => a.amount - b.amount);
  if (within.length) return { fit: within[0]!, over: false };
  return { fit: null, over: cands.length > 0 };
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
  result: ScoreResult;
  price: PriceFit | null;
  /** Presets this car passes only because the value is not known yet. */
  presetUnknown: PresetField[];
  /** Other variants of the same model that also qualified. */
  alternatives: number;
}

export interface HeroResult {
  picks: HeroPick[];
  /** Models that qualified (before cutting to TOP_N). */
  qualifying: number;
  /** How many of the qualifying picks have no price yet. */
  unpriced: number;
  ruledOutByGate: number;
  overBudget: number;
}

export function rankHero(rows: readonly ExploreRow[], rp: ResolvedProfile, q: HeroQuery, rules: ShortlistRules = RULES): HeroResult {
  const ctx = scoreContext(rows);
  const presets = presetsFor(rp).filter((p) => !q.presetsOff.includes(p.field));
  let ruledOutByGate = 0;
  let overBudget = 0;
  const best = new Map<string, HeroPick & { count: number }>();
  for (const row of applyFilters([...rows], q.filters, q.country)) {
    if (q.cond === "new" && row.on_sale_new !== true) continue;
    const checks = presets.map((p) => [p.field, presetCheck(row, p)] as const);
    if (checks.some(([, c]) => c === "fail")) continue;
    const { fit, over } = priceFit(row, { ...q, yearMin: q.filters.yearMin, yearMax: q.filters.yearMax });
    if (over && q.budget !== null) {
      overBudget++;
      continue;
    }
    const result = scoreRow(row, rp, ctx, rules);
    if (result.ruledOut) {
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
      const better =
        result.score > cur.result.score ||
        (result.score === cur.result.score && row.year_start > cur.row.year_start);
      if (better) best.set(row.model_id, { ...pick, count: cur.count + 1 });
      else cur.count++;
    }
  }
  const sorted = [...best.values()].sort(
    (a, b) =>
      b.result.score - a.result.score ||
      (b.row.real_range_km ?? 0) - (a.row.real_range_km ?? 0) ||
      `${a.row.make_name} ${a.row.model_name}`.localeCompare(`${b.row.make_name} ${b.row.model_name}`),
  );
  const picks = sorted.slice(0, TOP_N).map(({ count, ...p }, i) => ({ ...p, rank: i + 1, alternatives: count - 1 }));
  return {
    picks,
    qualifying: sorted.length,
    unpriced: picks.filter((p) => p.price === null).length,
    ruledOutByGate,
    overBudget,
  };
}

// ── "Why it ranks here" ─────────────────────────────────────────────────────────────────────

export interface Reason {
  id: string;
  value: number | string | boolean | null;
}

/** The two strongest known factors (score ≥ 0.6, by weighted score) plus the bonuses. */
export function reasons(result: ScoreResult, max = 2): Reason[] {
  return result.factors
    .filter((f) => f.known && f.score >= 0.6)
    .sort((a, b) => b.score * b.weight - a.score * a.weight)
    .slice(0, max)
    .map((f) => ({ id: f.id, value: f.value }));
}
