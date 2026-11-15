// ?ids=a,b,c,d → variant ids (T-010). The URL is the state (design principle 3).
import { COMPARE_MAX } from "@/lib/compare-store";

/** Comma-separated (or repeated) ids, trimmed, de-duplicated, at most COMPARE_MAX. */
export function parseCompareIds(raw: string | string[] | undefined | null): string[] {
  const parts = (Array.isArray(raw) ? raw : raw ? [raw] : []).flatMap((s) => s.split(","));
  const out: string[] = [];
  for (const p of parts) {
    const id = p.trim();
    if (id && /^[a-z0-9][a-z0-9-]*$/.test(id) && !out.includes(id)) out.push(id);
    if (out.length === COMPARE_MAX) break;
  }
  return out;
}

export function compareUrl(country: string, ids: readonly string[], onlyDiff = false): string {
  const q = ids.length ? `?ids=${ids.map(encodeURIComponent).join(",")}${onlyDiff ? "&diff=1" : ""}` : onlyDiff ? "?diff=1" : "";
  return `/${country}/compare${q}`;
}
