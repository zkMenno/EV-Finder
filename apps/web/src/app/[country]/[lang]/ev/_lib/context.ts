// Render context shared by the ev, compare and top pages (server only).
import type { FieldProvenance } from "@ev/schema";
import type { NumLabels } from "@/components/num-labels";
import { numLabels } from "@/components/num-labels";
import type { TermText } from "@/components/Term";
import type { Metadata } from "next";
import { COUNTRIES, isCountrySlug, isServed, type CountryConfig, type CountrySlug, type Lang } from "@/config/countries";
import { getT, type T } from "@/i18n";
import { getCatalogue, type Catalogue } from "@/lib/catalogue";
import { sourceNames } from "@/lib/explore-data";
import { localeFor } from "@/lib/format";
import { alternates, siteBase } from "@/lib/site-paths";
import { localizeTaxonomy, type UiTaxonomy } from "@/lib/taxonomy";

export interface PageCtx {
  country: CountrySlug;
  cfg: CountryConfig;
  lang: Lang;
  /** Path prefix for links: "/{country}/{lang}" (Decision 015). */
  base: string;
  locale: string;
  t: T;
  cat: Catalogue;
  labels: NumLabels;
  /** All source id → name. Pass `sourcesFor(ctx, prov)` to <Num> to keep the payload small. */
  sources: Record<string, string>;
  tax: UiTaxonomy;
  asOf: string;
  termText: TermText;
}

/** Render context from the URL's country and language (no request headers: pages stay static). */
export function pageCtx(country: CountrySlug, lang: Lang): PageCtx {
  const t = getT(lang);
  const cat = getCatalogue();
  const tax = localizeTaxonomy(cat.taxonomy(), lang);
  const base = siteBase(country, lang);
  return {
    country,
    cfg: COUNTRIES[country],
    lang,
    base,
    locale: localeFor(lang),
    t,
    cat,
    labels: numLabels(t, { base, terms: tax.terms }),
    sources: sourceNames(cat.sources()),
    tax,
    asOf: cat.generatedAt().slice(0, 10),
    termText: { about: t("term.about"), learnMore: t("term.learnMore") },
  };
}

export function sourcesFor(ctx: PageCtx, prov: FieldProvenance | undefined): Record<string, string> {
  return Object.fromEntries((prov?.source_ids ?? []).map((s) => [s, ctx.sources[s] ?? s]));
}

/** The URL's country × language if it is a served pair (the layout 404s otherwise). */
export function servedRoute(p: { country: string; lang: string }): { country: CountrySlug; lang: Lang } | null {
  return isCountrySlug(p.country) && isServed(p.country, p.lang) ? { country: p.country, lang: p.lang } : null;
}

/** Page metadata with canonical + hreflang for every served pair (Decision 015). `rest` = path after /{country}/{lang}. */
export function pageMeta(route: { country: CountrySlug; lang: Lang }, rest: string, meta: Metadata = {}): Metadata {
  return { ...meta, alternates: alternates(route.country, route.lang, rest) };
}
