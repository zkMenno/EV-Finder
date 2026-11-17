// T-130: the landing page lost the full list; old Explore links move to /cars.

/** "?query" for /cars when `sp` is an old Explore link (view or sort, no hero answers); else null. */
export function catalogueRedirect(sp: Record<string, string | string[] | undefined>): string | null {
  const has = (k: string) => sp[k] !== undefined;
  if (!has("view") && !has("sort")) return null;
  if (["role", "trips", "charge", "area", "budget"].some(has)) return null;
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(sp)) for (const x of Array.isArray(v) ? v : v === undefined ? [] : [v]) q.append(k, x);
  return `?${q.toString()}`;
}
