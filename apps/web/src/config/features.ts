// Feature flags read from the server environment. Static pages read them at build time, dynamic
// pages at request time. Server only: pass the result to client components as a prop.
//
// Parked features (Decision 051, docs/spec/launch-scope.md): built work for features that wait
// until after launch stays in the code, switched off by default. Turn one on with its variable
// set to "1", or all of them with PARKED=1. To test them: build with PARKED=1, run e2e with E2E_PARKED=1.

type Env = Record<string, string | undefined>;

/** Trip fit quick check (T-036): `TRIP_FIT=1` shows it; anything else hides the whole UI. */
export function tripFitEnabled(env: Env = process.env): boolean {
  return env.TRIP_FIT === "1";
}

export const PARKED_FLAGS = {
  /** "Find a charger / plan a trip" link-out block (T-026). */
  chargingLinks: "CHARGING_LINKS",
  /** Country charging statistics page /charging (T-028). */
  chargingPages: "CHARGING_PAGES",
  /** Known issues from inspection data on generation pages (T-061). */
  knownIssues: "KNOWN_ISSUES",
  /** Official registration counts on generation / variant / compare pages (T-058). */
  registrations: "REGISTRATIONS",
  /** Rankings pages /top (T-011). */
  rankings: "RANKINGS",
} as const;
export type ParkedFeature = keyof typeof PARKED_FLAGS;

export function parkedEnabled(feature: ParkedFeature, env: Env = process.env): boolean {
  return env.PARKED === "1" || env[PARKED_FLAGS[feature]] === "1";
}
