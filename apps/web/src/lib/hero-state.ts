// URL state of the hero (T-080). The country is the path; the picker answers, budget, new/used and
// the presets the visitor removed have their own short params; the refine filters are Explore's
// own filters and params (src/lib/state.ts), so a shared hero link opens the same table below.
import {
  AREAS,
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

export interface HeroState {
  answers: Answers;
  budget: number | null;
  cond: Condition;
  presetsOff: PresetField[];
  filters: ExploreFilters;
}

export const HERO_PARAM_KEYS = ["role", "trips", "charge", "area", "k8", "budget", "cond", "pxoff"] as const;

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
  return { answers: { ...EMPTY_ANSWERS }, budget: null, cond: "any", presetsOff: [], filters: defaultFilters() };
}

/** Parse; unknown or invalid values are dropped, never thrown. */
export function heroFromSearchParams(src: ParamSource): HeroState {
  const s = defaultHeroState();
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
