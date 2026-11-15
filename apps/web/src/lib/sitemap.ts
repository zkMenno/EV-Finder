// sitemap.xml entries (Decision 015): every indexable page in every served country × language
// pair (a country's own languages + EN), from the current release's model / generation /
// variant ids. Compare and staff pages are noindex and left out.
import { servedPairs } from "@/config/countries";
import {
  generationParams,
  modelParams,
  variantParams,
} from "@/app/[country]/[lang]/ev/_lib/routes";
import type { Catalogue } from "@/lib/catalogue";
import { articles } from "@/lib/learn";
import { RANKING_IDS } from "@/lib/rankings";
import { siteBase } from "@/lib/site-paths";

/** Page paths below /{country}/{lang} ("" = Explore). */
export function pagePaths(cat: Catalogue): string[] {
  const rows = cat.rows();
  return [
    "",
    "/top",
    ...RANKING_IDS.map((l) => `/top/${l}`),
    "/about",
    "/learn",
    ...articles().map((a) => `/learn/${a.slug}`),
    ...cat.taxonomy().glossary_terms.filter((g) => !articles().some((a) => a.slug === g.id)).map((g) => `/learn/${g.id}`),
    ...modelParams(rows).map((p) => `/ev/${p.make}/${p.model}`),
    ...generationParams(rows).map((p) => `/ev/${p.make}/${p.model}/${p.generation}`),
    ...variantParams(rows).map((p) => `/ev/${p.make}/${p.model}/${p.generation}/${p.variant}`),
  ];
}

/** Absolute URLs, one per served pair × page. */
export function sitemapUrls(cat: Catalogue, origin: string): string[] {
  const paths = pagePaths(cat);
  return servedPairs().flatMap(({ country, lang }) =>
    paths.map((p) => `${origin}${siteBase(country, lang)}${p}`),
  );
}
