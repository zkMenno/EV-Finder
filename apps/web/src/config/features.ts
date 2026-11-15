// Feature flags read from the server environment at request time (pages render on demand).
// Server only: pass the result to client components as a prop.

/** Trip fit quick check (T-036): `TRIP_FIT=1` shows it; anything else hides the whole UI. */
export function tripFitEnabled(env: Record<string, string | undefined> = process.env): boolean {
  return env.TRIP_FIT === "1";
}
