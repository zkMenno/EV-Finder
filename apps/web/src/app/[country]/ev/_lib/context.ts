// Per-request render context shared by the ev, compare and top pages (server only).
import type { FieldProvenance } from "@ev/schema";
import type { NumLabels } from "@/components/num-labels";
import { numLabels } from "@/components/num-labels";
import type { TermText } from "@/components/Term";
import { COUNTRIES, type CountryConfig, type CountrySlug, type Lang } from "@/config/countries";
import { getT, type T } from "@/i18n";
import { getCatalogue, type Catalogue } from "@/lib/catalogue";
import { sourceNames } from "@/lib/explore-data";
import { localeFor } from "@/lib/format";
import { requestLang } from "@/lib/request-lang";
import { localizeTaxonomy, type UiTaxonomy } from "@/lib/taxonomy";

export interface PageCtx {
  country: CountrySlug;
  cfg: CountryConfig;
  lang: Lang;
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

export async function pageCtx(country: CountrySlug): Promise<PageCtx> {
  const lang = await requestLang(country);
  const t = getT(lang);
  const cat = getCatalogue();
  return {
    country,
    cfg: COUNTRIES[country],
    lang,
    locale: localeFor(lang),
    t,
    cat,
    labels: numLabels(t),
    sources: sourceNames(cat.sources()),
    tax: localizeTaxonomy(cat.taxonomy(), lang),
    asOf: cat.generatedAt().slice(0, 10),
    termText: { about: t("term.about"), learnMore: t("term.learnMore") },
  };
}

export function sourcesFor(ctx: PageCtx, prov: FieldProvenance | undefined): Record<string, string> {
  return Object.fromEntries((prov?.source_ids ?? []).map((s) => [s, ctx.sources[s] ?? s]));
}
