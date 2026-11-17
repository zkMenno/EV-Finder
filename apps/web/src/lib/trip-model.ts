// Trip fit quick check (T-036, trip-fit spec sections 5 and 8): "the range you truly need" and a
// ✓ / ⚠ / ✗ verdict per car, computed in the browser (Decision 013). Core 1 has no routes: one
// round trip in km, a motorway share and a home town for the temperature.
//
// Energy needed  = km × WLTP battery consumption × Σ(road share × matrix multiplier) × extras
//                  + warm-up per cold start (winter)
// Energy at hand = usable kWh × battery health × (daily charge limit − arrival buffer)
//
// The multipliers come from a FIXTURE matrix (src/fixtures/consumption-matrix.sample.json,
// PROVISIONAL) until the T-033 consumption matrix ships with the release. Every number this
// file returns is an estimate on the "fixture matrix" rung. Pure: no DOM, no storage.
import type { Body } from "@ev/schema";
import type { CountrySlug } from "@/config/countries";
import matrixJson from "@/fixtures/consumption-matrix.sample.json";
import townsJson from "@/fixtures/towns.sample.json";
import type { ExploreRow } from "./explore-data";
import type { Driving, Extra, TripSettings } from "./trip-settings";

export type RoadBand = "town" | "rural" | "motorway";
export const ROAD_BANDS: readonly RoadBand[] = ["town", "rural", "motorway"];
type BandTable = Record<RoadBand, Record<string, number>>;

export interface ConsumptionMatrix {
  status: string;
  label: string;
  rung: string;
  temperature_bands: { id: string; label: string; max_c: number | null }[];
  bodies: Record<string, BandTable>;
  body_alias: Record<string, string>;
  default_body: string;
  country_motorway_factor: Record<string, number>;
  warmup_kwh_per_start: Record<string, number>;
  starts_per_round_trip: number;
  road_split: Record<Driving, { town: number; rural: number }>;
  default_motorway_pct: Record<Driving, number>;
  extras_factor: Partial<Record<Extra, number>>;
  battery_health: { new: number; used: number; keep8: number };
  daily_charge_limit: { default: number; charge_100_daily: number };
  arrival_buffer: number;
  uncertainty_pct: number;
  tight_margin: number;
  cold_snap_offset_c: number;
}

export interface Town {
  id: string;
  name: string;
  country: string;
  jan_c: number;
  jul_c: number;
}

export const MATRIX = matrixJson as unknown as ConsumptionMatrix;
export const TOWNS: readonly Town[] = (townsJson as { towns: Town[] }).towns;
/** Rung shown in Nerd mode for every trip number until T-033 lands. */
export const TRIP_RUNG = MATRIX.rung;

export type Verdict = "ok" | "tight" | "fail" | "unknown";

export type TripRow = Pick<ExploreRow, "variant_id" | "body" | "battery_kwh_net" | "wltp_range_km" | "consumption_kwh_100km" | "year_end" | "charge_100_daily">;

export interface Conditions {
  km: number;
  country: CountrySlug;
  town: Town;
  /** Road shares, summing to 1. */
  shares: Record<RoadBand, number>;
  winterC: number;
  summerC: number;
  winterBand: string;
  summerBand: string;
  extrasFactor: number;
  keep8: boolean;
  /** What the profile changed, as message ids for the Detailed view. */
  changes: string[];
}

export function townsFor(country: CountrySlug): Town[] {
  return TOWNS.filter((t) => t.country === country);
}

/** The trip check needs a home town with climate; a country without towns gets no trip check,
 *  never another country's weather (ES/IT until WS1 ships sourced GeoNames + Meteostat towns). */
export function hasTowns(country: CountrySlug): boolean {
  return townsFor(country).length > 0;
}

export function findTown(id: string | null, country: CountrySlug): Town {
  return TOWNS.find((t) => t.id === id) ?? townsFor(country)[0] ?? TOWNS[0]!;
}

export function temperatureBand(c: number, m: ConsumptionMatrix = MATRIX): string {
  for (const b of m.temperature_bands) if (b.max_c === null || c <= b.max_c) return b.id;
  return m.temperature_bands[m.temperature_bands.length - 1]!.id;
}

/** Turns the answers into trip conditions (defaults fill every skipped step). */
export function conditionsFor(s: TripSettings, country: CountrySlug, m: ConsumptionMatrix = MATRIX): Conditions | null {
  if (!s.roundTripKm) return null;
  const changes: string[] = [];
  const driving: Driving = s.driving ?? "mixed";
  const mwPct = s.motorwayPct ?? m.default_motorway_pct[driving];
  if (s.motorwayPct === null) changes.push("trip.change.motorwayDefault");
  const mw = Math.min(Math.max(mwPct, 0), 100) / 100;
  const split = m.road_split[driving];
  const shares = { town: (1 - mw) * split.town, rural: (1 - mw) * split.rural, motorway: mw };
  const town = findTown(s.townId, country);
  let winterC = town.jan_c;
  if (s.extras.includes("snow")) {
    winterC += m.cold_snap_offset_c;
    changes.push("trip.change.snow");
  }
  let extrasFactor = 1;
  for (const e of s.extras) {
    const f = m.extras_factor[e];
    if (f) {
      extrasFactor *= f;
      changes.push(`trip.change.${e}`);
    }
  }
  if (s.extras.includes("keep8")) changes.push("trip.change.keep8");
  // Car role, long trips and charging place feed the Fit score (Core 2); say so instead of hiding it.
  if (s.role || s.longTrips || s.charging) changes.push("trip.change.later");
  return {
    km: s.roundTripKm,
    country,
    town,
    shares,
    winterC,
    summerC: town.jul_c,
    winterBand: temperatureBand(winterC, m),
    summerBand: temperatureBand(town.jul_c, m),
    extrasFactor,
    keep8: s.extras.includes("keep8"),
    changes,
  };
}

function bodyTable(body: Body | undefined, m: ConsumptionMatrix): BandTable {
  const id = body ? (m.bodies[body] ? body : m.body_alias[body]) : undefined;
  return m.bodies[id ?? m.default_body] ?? m.bodies[m.default_body]!;
}

/** Multiplier on WLTP consumption for one body at one temperature band, on the trip's road mix. */
export function mixFactor(c: Conditions, band: string, body: Body | undefined, m: ConsumptionMatrix = MATRIX): number {
  const t = bodyTable(body, m);
  const mwFactor = m.country_motorway_factor[c.country] ?? 1;
  let f = 0;
  for (const b of ROAD_BANDS) f += c.shares[b] * (t[b][band] ?? 1) * (b === "motorway" ? mwFactor : 1);
  return f * c.extrasFactor;
}

/** Median mix factor over the matrix bodies (the "WLTP ratio for that mix", spec section 5). */
export function medianMixFactor(c: Conditions, band: string, m: ConsumptionMatrix = MATRIX): number {
  const vals = Object.keys(m.bodies)
    .map((b) => mixFactor(c, band, b as Body, m))
    .sort((a, b) => a - b);
  const mid = Math.floor(vals.length / 2);
  return vals.length % 2 ? vals[mid]! : (vals[mid - 1]! + vals[mid]!) / 2;
}

/** WLTP battery consumption, kWh/100 km: usable kWh / WLTP km, else the published consumption. */
export function wltpConsumption(r: TripRow): number | null {
  if (r.battery_kwh_net && r.wltp_range_km) return (r.battery_kwh_net / r.wltp_range_km) * 100;
  return r.consumption_kwh_100km && r.consumption_kwh_100km > 0 ? r.consumption_kwh_100km : null;
}

export interface Need {
  /** Full-battery range needed on your mix in winter (incl. warm-up), km. */
  winterKm: number;
  summerKm: number;
  /** Same, as WLTP km (to compare with ads). */
  winterWltpKm: number;
  summerWltpKm: number;
  /** Wh/km per road band for a reference car, winter and summer (Nerd). */
  whPerKm: Record<RoadBand, { winter: number; summer: number }>;
  winterFactor: number;
  summerFactor: number;
  /** P10–P90 of winterKm. */
  winterLow: number;
  winterHigh: number;
}

/** Reference WLTP consumption for the car-independent card, kWh/100 km. */
const REF_KWH_100KM = 16;

/**
 * "The range you truly need": the full-battery range a car must have on your mix so the trip
 * fits between a daily 80% charge and the arrival buffer.
 */
export function rangeNeeded(c: Conditions, m: ConsumptionMatrix = MATRIX): Need {
  const window = m.daily_charge_limit.default - m.arrival_buffer;
  const wF = medianMixFactor(c, c.winterBand, m);
  const sF = medianMixFactor(c, c.summerBand, m);
  const warm = (m.warmup_kwh_per_start[c.winterBand] ?? 0) * m.starts_per_round_trip;
  const warmKm = warm / ((REF_KWH_100KM * wF) / 100);
  const summerWarm = (m.warmup_kwh_per_start[c.summerBand] ?? 0) * m.starts_per_round_trip;
  const summerWarmKm = summerWarm / ((REF_KWH_100KM * sF) / 100);
  const winterKm = (c.km + warmKm) / window;
  const summerKm = (c.km + summerWarmKm) / window;
  const u = m.uncertainty_pct / 100;
  const t = bodyTable(undefined, m);
  const mw = m.country_motorway_factor[c.country] ?? 1;
  const wh = (b: RoadBand, band: string) => REF_KWH_100KM * 10 * (t[b][band] ?? 1) * (b === "motorway" ? mw : 1) * c.extrasFactor;
  const whPerKm = Object.fromEntries(ROAD_BANDS.map((b) => [b, { winter: wh(b, c.winterBand), summer: wh(b, c.summerBand) }])) as Need["whPerKm"];
  return {
    winterKm,
    summerKm,
    winterWltpKm: winterKm * wF,
    summerWltpKm: summerKm * sF,
    whPerKm,
    winterFactor: wF,
    summerFactor: sF,
    winterLow: winterKm * (1 - u),
    winterHigh: winterKm * (1 + u),
  };
}

export interface CarFit {
  verdict: Verdict;
  /** Full-battery winter range on your mix, km (what "this car has about …" shows). */
  winterKm: number | null;
  summerKm: number | null;
  /** kWh the trip needs in winter and what the car has for it (daily limit − buffer). */
  needKwh: number | null;
  haveKwh: number | null;
  /** (have − need) / usable; negative = short. */
  margin: number | null;
  /** Winter km the car is short by (fail only). */
  shortKm: number | null;
  health: number;
  startCharge: number;
}

const UNKNOWN: CarFit = { verdict: "unknown", winterKm: null, summerKm: null, needKwh: null, haveKwh: null, margin: null, shortKm: null, health: 1, startCharge: 0.8 };

/** Verdict for one car (spec section 5: ✓ margin ≥ 15%, ⚠ 0–15% or the band crosses zero, ✗ short). */
export function fitCar(r: TripRow, c: Conditions, m: ConsumptionMatrix = MATRIX, year = new Date().getFullYear()): CarFit {
  const usable = r.battery_kwh_net;
  const base = wltpConsumption(r);
  if (!usable || usable <= 0 || !base) return UNKNOWN;
  const used = r.year_end != null && r.year_end < year;
  const health = c.keep8 ? m.battery_health.keep8 : used ? m.battery_health.used : m.battery_health.new;
  const startCharge = r.charge_100_daily ? m.daily_charge_limit.charge_100_daily : m.daily_charge_limit.default;
  const wF = mixFactor(c, c.winterBand, r.body, m);
  const sF = mixFactor(c, c.summerBand, r.body, m);
  const kwhPerKm = (base * wF) / 100;
  const warm = (m.warmup_kwh_per_start[c.winterBand] ?? 0) * m.starts_per_round_trip;
  const needKwh = c.km * kwhPerKm + warm;
  const haveKwh = usable * health * (startCharge - m.arrival_buffer);
  const margin = (haveKwh - needKwh) / usable;
  const u = m.uncertainty_pct / 100;
  let verdict: Verdict;
  if (needKwh > haveKwh) verdict = "fail";
  else if (margin < m.tight_margin || needKwh * (1 + u) > haveKwh) verdict = "tight";
  else verdict = "ok";
  return {
    verdict,
    winterKm: (usable * health) / kwhPerKm,
    summerKm: (usable * health) / ((base * sF) / 100),
    needKwh,
    haveKwh,
    margin,
    shortKm: verdict === "fail" ? (needKwh - haveKwh) / kwhPerKm : null,
    health,
    startCharge,
  };
}

/** Verdicts for every row, keyed by variant id. */
export function fitAll(rows: readonly TripRow[], c: Conditions, m: ConsumptionMatrix = MATRIX): Map<string, CarFit> {
  const year = new Date().getFullYear();
  return new Map(rows.map((r) => [r.variant_id, fitCar(r, c, m, year)]));
}

/** The "does my trips in winter" filter keeps ✓ and ⚠ (a tight fit still does the trip). */
export function passesTrip(fit: CarFit | undefined): boolean {
  return fit?.verdict === "ok" || fit?.verdict === "tight";
}
