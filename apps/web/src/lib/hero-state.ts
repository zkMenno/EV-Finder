// URL state of the hero (T-080). The country is the path; the picker answers, budget, new/used and
// the presets the visitor removed have their own short params; the refine filters are Explore's
// own filters and params (src/lib/state.ts), so a shared hero link opens the same table below.
import {
  AREAS,
  asksTrips,
  CHARGES,
  CONDITIONS,
  EMPTY_ANSWERS,
  PRESET_FIELDS,
  ROLES,
  TRIPS,
  type Answers,
  type Condition,
  type PresetField,
} from "./shortlist";
import { defaultFilters, EXPLORE_PARAM_KEYS, fromSearchParams, toSearchParams, defaultState, type ExploreFilters } from "./state";

/**
 * T-132: the hero asks one question at a time. The order is fixed; `trips` is skipped for a second
 * car. "results" is the top 10. The step is in the URL (`q`), so the back button goes to the
 * previous question and a shared link opens the same screen.
 */
export const HERO_STEPS = ["country", "role", "trips", "charge", "area", "budget", "results"] as const;
export type HeroStep = (typeof HERO_STEPS)[number];
/** The four driving questions (progress road stop 2). */
export const DRIVING_STEPS = ["role", "trips", "charge", "area"] as const satisfies readonly HeroStep[];

export interface HeroState {
  /** Explicit step from the URL; null = work it out from the answers (heroStep). */
  step: HeroStep | null;
  answers: Answers;
  budget: number | null;
  cond: Condition;
  presetsOff: PresetField[];
  filters: ExploreFilters;
}

export const HERO_PARAM_KEYS = ["q", "role", "trips", "charge", "area", "k8", "budget", "cond", "pxoff"] as const;

type ParamSource = URLSearchParams | Record<string, string | string[] | undefined>;

function get(src: ParamSource, key: string): string | undefined {
  if (src instanceof URLSearchParams) return src.get(key) ?? undefined;
  const v = src[key];
  return Array.isArray(v) ? v[0] : v;
}

function oneOf<T extends string>(all: readonly T[], v: string | undefined): T | null {
  return v !== undefined && (all as readonly string[]).includes(v) ? (v as T) : null;
}

/** Highest budget we accept from a URL (anything above is treated as "no budget"). */
export const BUDGET_MAX = 500_000;

export function defaultHeroState(): HeroState {
  return { step: null, answers: { ...EMPTY_ANSWERS }, budget: null, cond: "any", presetsOff: [], filters: defaultFilters() };
}

/** Parse; unknown or invalid values are dropped, never thrown. */
export function heroFromSearchParams(src: ParamSource): HeroState {
  const s = defaultHeroState();
  s.step = oneOf(HERO_STEPS, get(src, "q"));
  s.answers = {
    role: oneOf(ROLES, get(src, "role")),
    trips: oneOf(TRIPS, get(src, "trips")),
    charge: oneOf(CHARGES, get(src, "charge")),
    area: oneOf(AREAS, get(src, "area")),
    keep8: get(src, "k8") === "1",
  };
  const b = Number(get(src, "budget"));
  s.budget = get(src, "budget") && Number.isFinite(b) && b > 0 && b <= BUDGET_MAX ? Math.round(b) : null;
  s.cond = oneOf(CONDITIONS, get(src, "cond")) ?? "any";
  s.presetsOff = (get(src, "pxoff") ?? "")
    .split(",")
    .filter((x): x is PresetField => (PRESET_FIELDS as readonly string[]).includes(x))
    .filter((x, i, a) => a.indexOf(x) === i)
    .sort();
  s.filters = fromSearchParams(src).filters;
  // Trip fit is parked (Decision 051); the hero never carries it.
  s.filters.tripFit = false;
  return s;
}

/** The hero's own params, defaults omitted. */
export function heroOwnParams(s: HeroState): URLSearchParams {
  const p = new URLSearchParams();
  const a = s.answers;
  if (s.step && s.step !== "results") p.set("q", s.step);
  if (a.role) p.set("role", a.role);
  if (a.trips && a.role !== "second") p.set("trips", a.trips);
  if (a.charge) p.set("charge", a.charge);
  if (a.area) p.set("area", a.area);
  if (a.keep8) p.set("k8", "1");
  if (s.budget !== null) p.set("budget", String(s.budget));
  if (s.cond !== "any") p.set("cond", s.cond);
  if (s.presetsOff.length) p.set("pxoff", [...s.presetsOff].sort().join(","));
  return p;
}

/** Hero params + the refine filters as Explore writes them. */
export function heroToSearchParams(s: HeroState): URLSearchParams {
  const p = heroOwnParams(s);
  toSearchParams({ ...defaultState(), filters: s.filters }).forEach((v, k) => p.set(k, v));
  return p;
}

/**
 * Merge into an existing URL: hero keys and filter keys are replaced, Explore's view/sort/level
 * and anything else stay as they are.
 */
export function mergeHeroIntoUrl(href: string, s: HeroState): string {
  const url = new URL(href);
  const filterKeys = EXPLORE_PARAM_KEYS.filter((k) => !["sort", "view", "level", "pay"].includes(k));
  for (const k of [...HERO_PARAM_KEYS, ...filterKeys]) url.searchParams.delete(k);
  heroToSearchParams(s).forEach((v, k) => url.searchParams.set(k, v));
  return url.pathname + url.search + url.hash;
}

// ── Steps (T-132) ────────────────────────────────────────────────────────────────────────────

/** Steps that apply to these answers, in order (no trips question for a second car). */
export function stepsFor(a: Answers): HeroStep[] {
  return HERO_STEPS.filter((st) => st !== "trips" || asksTrips(a));
}

/**
 * The screen to show. An explicit step wins (a trips step for a second car becomes charge). Without
 * one: no answers → country; a full profile → results (old shared links open the top 10); else the
 * first unanswered driving question.
 */
export function heroStep(s: HeroState): HeroStep {
  const a = s.answers;
  const complete = a.role !== null && (!asksTrips(a) || a.trips !== null);
  if (s.step === "trips" && !asksTrips(a)) return "charge";
  if (s.step && (s.step !== "results" || complete)) return s.step;
  const unanswered = DRIVING_STEPS.filter((st) => (st === "trips" ? asksTrips(a) : true) && a[st] === null);
  const any = a.role !== null || a.trips !== null || a.charge !== null || a.area !== null || s.budget !== null;
  if (!any) return "country";
  if (complete) return "results";
  return unanswered[0] ?? "results";
}

/** The step after this one for these answers. */
export function nextStep(step: HeroStep, a: Answers): HeroStep {
  const all = stepsFor(a);
  const i = all.indexOf(step);
  return all[Math.min(i + 1, all.length - 1)] ?? "results";
}

/** The step before this one (country is first). */
export function prevStep(step: HeroStep, a: Answers): HeroStep {
  const all = stepsFor(a);
  const i = all.indexOf(step);
  return all[Math.max(i - 1, 0)] ?? "country";
}

/** Progress road stop (0 country · 1 your driving · 2 budget · 3 shortlist). */
export function roadStop(step: HeroStep): 0 | 1 | 2 | 3 {
  if (step === "country") return 0;
  if (step === "budget") return 2;
  if (step === "results") return 3;
  return 1;
}

/** "question n of m" inside the driving stop (m is 3 for a second car). */
export function drivingQuestion(step: HeroStep, a: Answers): { n: number; of: number } | null {
  const qs = DRIVING_STEPS.filter((st) => st !== "trips" || asksTrips(a));
  const i = (qs as readonly HeroStep[]).indexOf(step);
  return i < 0 ? null : { n: i + 1, of: qs.length };
}
