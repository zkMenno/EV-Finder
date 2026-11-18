// One state shape for Explore, shared by the URL, localStorage and (later) accounts.
import type { Body, Era, Segment } from "@ev/schema";
import { isPayMode, type PayMode } from "@/lib/finance";

export const ERAS: readonly Era[] = ["pre-2018", "2018-20", "2021-22", "2023-24", "2025+"];
export const SEGMENTS: readonly Segment[] = ["A", "B", "C", "D", "E", "F", "J-small", "J-medium", "J-large"];
export const BODIES: readonly Body[] = ["hatchback", "sedan", "estate", "suv", "crossover", "coupe", "mpv", "cabrio"];

export const SORT_KEYS = [
  "name",
  "years",
  "era",
  "range",
  "battery",
  "dc",
  "ac",
  "price",
  "rdw",
  "quality",
  // T-067: order from the shortlist rules for the profile picked in the hero (src/lib/shortlist.ts).
  "suggested",
  // T-130: registrations + owner picks blend (src/lib/popularity.ts); the catalogue page's default order.
  "popular",
  // T-130 part 2: the cheapest used price where the visitor lives, and the winter range estimate.
  "used",
  "winter",
] as const;
export type SortKey = (typeof SORT_KEYS)[number];
export type SortDir = "asc" | "desc";
export type View = "table" | "cards";
/** Display level (Decision 010). */
export type Level = "simple" | "detailed" | "nerd";
export const LEVELS: readonly Level[] = ["simple", "detailed", "nerd"];

export interface ExploreFilters {
  priceMax: number | null;
  /** T-130 part 2: used price where the visitor lives (any build year's typical price within the range). */
  usedMin: number | null;
  usedMax: number | null;
  /** T-130 part 2: real winter range estimate (`real_range_winter_km`), at least this many km. */
  winterMin: number | null;
  eras: Era[];
  segments: Segment[];
  bodies: Body[];
  rangeMin: number | null;
  batteryMin: number | null;
  dcMin: number | null;
  bootMin: number | null;
  lengthMax: number | null;
  towingMin: number | null;
  /** T-080 refine: seats, home charging (AC kW) and build years (a variant matches when its years overlap). */
  seatsMin: number | null;
  acMin: number | null;
  yearMin: number | null;
  yearMax: number | null;
  /** T-080 refine: brands to include / exclude (make ids). */
  makes: string[];
  excludeMakes: string[];
  /** Taxonomy ids (data, not enums): validated as ids only. */
  voltageClasses: string[];
  voltageMin: number | null;
  voltageMax: number | null;
  fast400: boolean;
  chemistries: string[];
  coolings: string[];
  charge100: boolean;
  /**
   * Trip fit (T-036): only cars that do my trips in winter. The trip itself stays in the browser
   * (TRIP_KEY); the URL carries only this on/off flag, never a place. Ignored without a trip.
   */
  tripFit: boolean;
}

export interface ExploreState {
  /** Shape version, so stored/account copies can be migrated later. */
  v: 1;
  filters: ExploreFilters;
  sort: SortKey | null;
  dir: SortDir;
  view: View;
  level: Level;
  /** Price mode (Decision 017): outright price, loan per month or lease per month. URL `pay`. */
  pay: PayMode;
}

export const NUMERIC_FILTERS = [
  "priceMax",
  "usedMin",
  "usedMax",
  "winterMin",
  "rangeMin",
  "batteryMin",
  "dcMin",
  "bootMin",
  "lengthMax",
  "towingMin",
  "voltageMin",
  "voltageMax",
  "seatsMin",
  "acMin",
  "yearMin",
  "yearMax",
] as const satisfies readonly (keyof ExploreFilters)[];
export type NumericFilter = (typeof NUMERIC_FILTERS)[number];

/** URL parameter names (short, stable: links get shared). */
const NUM_PARAM: Record<NumericFilter, string> = {
  priceMax: "price",
  usedMin: "umin",
  usedMax: "umax",
  winterMin: "winter",
  rangeMin: "range",
  batteryMin: "kwh",
  dcMin: "dc",
  bootMin: "boot",
  lengthMax: "len",
  towingMin: "tow",
  voltageMin: "vmin",
  voltageMax: "vmax",
  seatsMin: "seats",
  acMin: "ac",
  yearMin: "ymin",
  yearMax: "ymax",
};

const ID_RE = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const LIST_PARAM = {
  voltageClasses: "volt",
  chemistries: "chem",
  coolings: "cool",
  makes: "make",
  excludeMakes: "xmake",
} as const;
const FLAG_PARAM = { fast400: "fast400", charge100: "c100", tripFit: "trip" } as const;
type ListFilter = keyof typeof LIST_PARAM;
type FlagFilter = keyof typeof FLAG_PARAM;

function ids(v: unknown): string[] {
  const parts: unknown[] = Array.isArray(v) ? v : typeof v === "string" ? v.split(",") : [];
  const out = new Set<string>();
  for (const p of parts) if (typeof p === "string" && ID_RE.test(p)) out.add(p);
  return [...out].sort();
}

export function defaultFilters(): ExploreFilters {
  return {
    priceMax: null,
    usedMin: null,
    usedMax: null,
    winterMin: null,
    eras: [],
    segments: [],
    bodies: [],
    rangeMin: null,
    batteryMin: null,
    dcMin: null,
    bootMin: null,
    lengthMax: null,
    towingMin: null,
    seatsMin: null,
    acMin: null,
    yearMin: null,
    yearMax: null,
    makes: [],
    excludeMakes: [],
    voltageClasses: [],
    voltageMin: null,
    voltageMax: null,
    fast400: false,
    chemistries: [],
    coolings: [],
    charge100: false,
    tripFit: false,
  };
}

export function defaultState(): ExploreState {
  return { v: 1, filters: defaultFilters(), sort: null, dir: "asc", view: "table", level: "detailed", pay: "buy" };
}

function num(v: unknown): number | null {
  if (typeof v === "number") return Number.isFinite(v) && v >= 0 ? v : null;
  if (typeof v !== "string" || v.trim() === "") return null;
  const n = Number(v);
  return Number.isFinite(n) && n >= 0 ? n : null;
}

function pick<T extends string>(allowed: readonly T[], v: unknown): T[] {
  const parts: unknown[] = Array.isArray(v) ? v : typeof v === "string" ? v.split(",") : [];
  const out: T[] = [];
  for (const p of parts) {
    if (typeof p === "string" && (allowed as readonly string[]).includes(p) && !out.includes(p as T)) {
      out.push(p as T);
    }
  }
  // Keep canonical order so equal states serialise to equal URLs.
  return out.sort((a, b) => allowed.indexOf(a) - allowed.indexOf(b));
}

type ParamSource = URLSearchParams | Record<string, string | string[] | undefined>;

function getParam(src: ParamSource, key: string): string | undefined {
  if (src instanceof URLSearchParams) return src.get(key) ?? undefined;
  const v = src[key];
  return Array.isArray(v) ? v[0] : v;
}

/** Parse URL search params. Unknown or invalid values are ignored, never thrown. */
export function fromSearchParams(src: ParamSource): ExploreState {
  const s = defaultState();
  for (const k of NUMERIC_FILTERS) s.filters[k] = num(getParam(src, NUM_PARAM[k]));
  s.filters.eras = pick(ERAS, getParam(src, "era"));
  s.filters.segments = pick(SEGMENTS, getParam(src, "seg"));
  s.filters.bodies = pick(BODIES, getParam(src, "body"));
  const sort = getParam(src, "sort");
  if (sort) {
    const desc = sort.startsWith("-");
    const key = desc ? sort.slice(1) : sort;
    if ((SORT_KEYS as readonly string[]).includes(key)) {
      s.sort = key as SortKey;
      s.dir = desc ? "desc" : "asc";
    }
  }
  if (getParam(src, "view") === "cards") s.view = "cards";
  for (const k of Object.keys(LIST_PARAM) as ListFilter[]) s.filters[k] = ids(getParam(src, LIST_PARAM[k]));
  for (const k of Object.keys(FLAG_PARAM) as FlagFilter[]) s.filters[k] = getParam(src, FLAG_PARAM[k]) === "1";
  const level = getParam(src, "level");
  if ((LEVELS as readonly string[]).includes(level ?? "")) s.level = level as Level;
  const pay = getParam(src, "pay");
  if (isPayMode(pay)) s.pay = pay;
  return s;
}

/** Whether the URL explicitly sets the price mode (else the remembered one wins). */
export function hasPayParam(src: ParamSource): boolean {
  return isPayMode(getParam(src, "pay"));
}

/** Whether the URL explicitly sets the display level (else the stored preference wins). */
export function hasLevelParam(src: ParamSource): boolean {
  return (LEVELS as readonly string[]).includes(getParam(src, "level") ?? "");
}

/** Whether the URL explicitly sets the view (else the stored preference wins). */
export function hasViewParam(src: ParamSource): boolean {
  const v = getParam(src, "view");
  return v === "cards" || v === "table";
}

/** Serialise to URL params; defaults are omitted so the plain page URL stays clean. */
/** `defaultView`: the page's own default, left out of the URL (Explore on /cars defaults to cards, T-130). */
export function toSearchParams(state: ExploreState, defaultView: View = "table"): URLSearchParams {
  const p = new URLSearchParams();
  const f = state.filters;
  for (const k of NUMERIC_FILTERS) {
    const v = f[k];
    if (v !== null) p.set(NUM_PARAM[k], String(v));
  }
  if (f.eras.length) p.set("era", pick(ERAS, f.eras).join(","));
  if (f.segments.length) p.set("seg", pick(SEGMENTS, f.segments).join(","));
  if (f.bodies.length) p.set("body", pick(BODIES, f.bodies).join(","));
  if (state.sort) p.set("sort", (state.dir === "desc" ? "-" : "") + state.sort);
  for (const k of Object.keys(LIST_PARAM) as ListFilter[]) if (f[k].length) p.set(LIST_PARAM[k], ids(f[k]).join(","));
  for (const k of Object.keys(FLAG_PARAM) as FlagFilter[]) if (f[k]) p.set(FLAG_PARAM[k], "1");
  if (state.view !== defaultView) p.set("view", state.view);
  if (state.level !== "detailed") p.set("level", state.level);
  if (state.pay !== "buy") p.set("pay", state.pay);
  return p;
}

/** For localStorage / account storage. */
export function serializeState(state: ExploreState): string {
  return JSON.stringify(normalizeState(state));
}

/** Accepts anything (corrupt storage included) and returns a valid state. */
export function deserializeState(raw: string | null | undefined): ExploreState {
  if (!raw) return defaultState();
  try {
    return normalizeState(JSON.parse(raw) as unknown);
  } catch {
    return defaultState();
  }
}

export function normalizeState(input: unknown): ExploreState {
  const s = defaultState();
  if (!input || typeof input !== "object") return s;
  const o = input as Record<string, unknown>;
  const f = (o.filters && typeof o.filters === "object" ? o.filters : {}) as Record<string, unknown>;
  for (const k of NUMERIC_FILTERS) s.filters[k] = num(f[k]);
  s.filters.eras = pick(ERAS, f.eras);
  s.filters.segments = pick(SEGMENTS, f.segments);
  s.filters.bodies = pick(BODIES, f.bodies);
  if (typeof o.sort === "string" && (SORT_KEYS as readonly string[]).includes(o.sort)) s.sort = o.sort as SortKey;
  if (o.dir === "desc") s.dir = "desc";
  if (o.view === "cards") s.view = "cards";
  for (const k of Object.keys(LIST_PARAM) as ListFilter[]) s.filters[k] = ids(f[k]);
  for (const k of Object.keys(FLAG_PARAM) as FlagFilter[]) s.filters[k] = f[k] === true;
  if (typeof o.level === "string" && (LEVELS as readonly string[]).includes(o.level)) s.level = o.level as Level;
  if (isPayMode(o.pay)) s.pay = o.pay;
  return s;
}

export function activeFilterCount(f: ExploreFilters): number {
  return (
    NUMERIC_FILTERS.filter((k) => f[k] !== null).length +
    (f.eras.length ? 1 : 0) +
    (f.segments.length ? 1 : 0) +
    (f.bodies.length ? 1 : 0) +
    (f.voltageClasses.length ? 1 : 0) +
    (f.chemistries.length ? 1 : 0) +
    (f.coolings.length ? 1 : 0) +
    (f.makes.length ? 1 : 0) +
    (f.excludeMakes.length ? 1 : 0) +
    (f.fast400 ? 1 : 0) +
    (f.charge100 ? 1 : 0) +
    (f.tripFit ? 1 : 0)
  );
}

/** Every URL key Explore owns; other params (e.g. ?lang=) are left alone. */
export const EXPLORE_PARAM_KEYS: readonly string[] = [
  ...Object.values(NUM_PARAM),
  ...Object.values(LIST_PARAM),
  ...Object.values(FLAG_PARAM),
  "era",
  "seg",
  "body",
  "sort",
  "view",
  "level",
  "pay",
];

/** Numeric columns sort high→low first; text-like columns low→high. */
const FIRST_DIR: Record<SortKey, SortDir> = {
  name: "asc",
  years: "desc",
  era: "desc",
  range: "desc",
  battery: "desc",
  dc: "desc",
  ac: "desc",
  price: "asc",
  rdw: "desc",
  quality: "desc",
  suggested: "desc",
  popular: "desc",
  used: "asc",
  winter: "desc",
};

/** Sort menu (T-130): pick a key in its natural first direction (numbers high→low, price low→high). */
export function sortBy(state: ExploreState, key: SortKey): ExploreState {
  return { ...state, sort: key, dir: FIRST_DIR[key] };
}

/** The keys the catalogue page's sort menu offers, in menu order (T-130 design). */
export const MENU_SORTS = ["popular", "used", "winter", "battery", "dc", "years"] as const satisfies readonly SortKey[];

/** Header click cycle: first direction → other direction → unsorted. */
export function nextSort(state: ExploreState, key: SortKey): ExploreState {
  if (state.sort !== key) return { ...state, sort: key, dir: FIRST_DIR[key] };
  if (state.dir === FIRST_DIR[key]) return { ...state, dir: FIRST_DIR[key] === "asc" ? "desc" : "asc" };
  return { ...state, sort: null, dir: "asc" };
}

export const VIEW_KEY = "ev-finder:view:v1";
export const LEVEL_KEY = "ev-finder:level:v1";
/** Trip fit answers (src/lib/trip-settings.ts): browser only, a town id at most, never coordinates. */
export const TRIP_KEY = "ev-finder:trip:v1";
