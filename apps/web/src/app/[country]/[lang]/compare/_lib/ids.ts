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

/**
 * `base` = "/{country}/{lang}". `pay` (Decision 017 price mode, "loan" | "lease") is kept so the
 * "differences only" toggle and remove links don't drop the price mode from a shared link.
 */
export function compareUrl(base: string, ids: readonly string[], onlyDiff = false, pay?: string | null): string {
  const parts: string[] = [];
  if (ids.length) parts.push(`ids=${ids.map(encodeURIComponent).join(",")}`);
  if (onlyDiff) parts.push("diff=1");
  if (pay === "loan" || pay === "lease") parts.push(`pay=${pay}`);
  return `${base}/compare${parts.length ? `?${parts.join("&")}` : ""}`;
}
