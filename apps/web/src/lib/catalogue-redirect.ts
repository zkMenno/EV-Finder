// T-130: the landing page lost the full list; old Explore links move to /cars.

/** "?query" for /cars when `sp` is an old Explore link (it carries view or sort, which the hero never writes); else null. */
export function catalogueRedirect(sp: Record<string, string | string[] | undefined>): string | null {
  const has = (k: string) => sp[k] !== undefined;
  if (!has("view") && !has("sort")) return null;
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(sp)) for (const x of Array.isArray(v) ? v : v === undefined ? [] : [v]) q.append(k, x);
  return `?${q.toString()}`;
}
