// Nerd-mode price provenance for the hero cards (Decision 064, T-115). Pure, client-safe.
import type { T } from "@/i18n/t";
import { formatNumber } from "./format";
import type { PriceFit } from "./shortlist";

/** "NL" → "Netherlands" / "Nederland" in the page's language; the code itself if Intl can't say. */
function regionName(cc: string, locale: string): string {
  try {
    return new Intl.DisplayNames([locale], { type: "region" }).of(cc.toUpperCase()) ?? cc;
  } catch {
    return cc;
  }
}

/**
 * Nerd mode (Decision 064): how the price was made and where it comes from, built from the release
 * row's own fields (basis, scope, curve, curve_fitted_on, source, date), never a fixed citation.
 */
export function priceHowText(p: PriceFit, t: T, locale: string, money: (n: number) => string, sources: Record<string, string>): string | null {
  const unknown = t("hero.card.notKnown");
  const h = p.how ?? {};
  const date = h.date ?? unknown;
  if (p.basis === "estimate") {
    const on = (h.on ?? []).map((cc) => regionName(cc, locale)).join(", ");
    const [kind, segment] = (h.curve ?? "").split(":");
    const curve =
      kind === "fitted"
        ? t(segment ? "hero.card.curveFittedSegment" : "hero.card.curveFitted", { countries: on || unknown, segment: segment ?? "" })
        : kind === "published"
          ? t("hero.card.curvePublished")
          : unknown;
    return t("hero.card.estimateHow", {
      list: h.list ? money(h.list) : unknown,
      kept: h.kept ? `${formatNumber(h.kept * 100, locale, 0)} %` : unknown,
      curve,
      source: h.src ?? unknown,
      date,
      sources: (h.ls ?? []).map((id) => sources[id] ?? id).join(", ") || unknown,
    });
  }
  if (p.basis === "band") {
    const source = h.src ?? ((p.sourceIds ?? []).map((id) => sources[id] ?? id).join(", ") || unknown);
    const n = h.n ?? p.samples;
    return t(p.scope === "generation" ? "hero.card.bandHowGeneration" : "hero.card.bandHow", { n: n ? formatNumber(n, locale, 0) : unknown, source, date });
  }
  return null;
}
