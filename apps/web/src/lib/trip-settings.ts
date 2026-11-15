// Trip fit quick check (T-036): the user's answers, stored in the browser only (localStorage via
// src/lib/storage.ts). Holds a town id from the fixture list, never coordinates or addresses
// (trip-fit spec section 7, Decision 013). Pure: safe on server and client.
import { readStorage, writeStorage, type KeyValueStorage } from "./storage";
import { TRIP_KEY } from "./state";

export const ROLES = ["only", "main", "second"] as const;
export const LONG_TRIPS = ["never", "few", "monthly", "often"] as const;
export const CHARGING = ["home", "work", "public"] as const;
export const DRIVING = ["town", "mixed", "motorway"] as const;
export const EXTRAS = ["tow", "roofbox", "full", "snow", "keep8"] as const;

export type Role = (typeof ROLES)[number];
export type LongTrips = (typeof LONG_TRIPS)[number];
export type Charging = (typeof CHARGING)[number];
export type Driving = (typeof DRIVING)[number];
export type Extra = (typeof EXTRAS)[number];

export interface TripSettings {
  /** Shape version, for later migration (accounts sync summaries only). */
  v: 1;
  role: Role | null;
  longTrips: LongTrips | null;
  charging: Charging | null;
  driving: Driving | null;
  extras: Extra[];
  /** Longest regular round trip, km. */
  roundTripKm: number | null;
  /** Share of that trip on the motorway, 0–100. null = from the driving profile. */
  motorwayPct: number | null;
  /** Id from the fixture town list (src/fixtures/towns.sample.json). Never coordinates. */
  townId: string | null;
}

export const MAX_TRIP_KM = 2000;
const TOWN_ID_RE = /^[a-z]{2}-[a-z0-9-]{1,40}$/;

export function defaultTripSettings(): TripSettings {
  return { v: 1, role: null, longTrips: null, charging: null, driving: null, extras: [], roundTripKm: null, motorwayPct: null, townId: null };
}

function oneOf<T extends string>(allowed: readonly T[], v: unknown): T | null {
  return typeof v === "string" && (allowed as readonly string[]).includes(v) ? (v as T) : null;
}

function bounded(v: unknown, max: number): number | null {
  const n = typeof v === "string" && v.trim() !== "" ? Number(v) : v;
  if (typeof n !== "number" || !Number.isFinite(n) || n < 0) return null;
  return Math.min(Math.round(n), max);
}

/** Accepts anything (corrupt storage included) and returns valid settings. */
export function normalizeTripSettings(input: unknown): TripSettings {
  const s = defaultTripSettings();
  if (!input || typeof input !== "object") return s;
  const o = input as Record<string, unknown>;
  s.role = oneOf(ROLES, o.role);
  s.longTrips = oneOf(LONG_TRIPS, o.longTrips);
  s.charging = oneOf(CHARGING, o.charging);
  s.driving = oneOf(DRIVING, o.driving);
  const ex = Array.isArray(o.extras) ? o.extras : [];
  s.extras = EXTRAS.filter((e) => ex.includes(e));
  const km = bounded(o.roundTripKm, MAX_TRIP_KM);
  s.roundTripKm = km && km > 0 ? km : null;
  s.motorwayPct = bounded(o.motorwayPct, 100);
  // Only an id from our list shape; anything that looks like coordinates or free text is dropped.
  s.townId = typeof o.townId === "string" && TOWN_ID_RE.test(o.townId) ? o.townId : null;
  return s;
}

/** True once the user entered a trip: only then does Explore show the column and the filter. */
export function hasTrip(s: TripSettings | null): s is TripSettings & { roundTripKm: number } {
  return !!s && s.roundTripKm !== null && s.roundTripKm > 0;
}

export function readTripSettings(storage?: KeyValueStorage | null): TripSettings | null {
  const raw = storage === undefined ? readStorage(TRIP_KEY) : readStorage(TRIP_KEY, storage);
  if (!raw) return null;
  try {
    return normalizeTripSettings(JSON.parse(raw) as unknown);
  } catch {
    return null;
  }
}

export function writeTripSettings(s: TripSettings, storage?: KeyValueStorage | null): boolean {
  const json = JSON.stringify(normalizeTripSettings(s));
  return storage === undefined ? writeStorage(TRIP_KEY, json) : writeStorage(TRIP_KEY, json, storage);
}
