// Public URL shape (Decision 015): /{country}/{lang}/…. Client-safe (no Node APIs).
import {
  COUNTRIES,
  hreflangTag,
  servedPairs,
  type CountrySlug,
  type Lang,
} from "@/config/countries";

/** Path prefix for a country × language: "/be/fr". Every internal link starts with it. */
export function siteBase(country: CountrySlug, lang: Lang): string {
  return `/${country}/${lang}`;
}

/**
 * The x-default hreflang target: English in the first launch country. Language-neutral visitors
 * get English text; prices show in that country's currency (EUR).
 */
export const X_DEFAULT: { country: CountrySlug; lang: Lang } = { country: "nl", lang: "en" };

/** Canonical origin for absolute URLs (hreflang, sitemap): APP_URL (.env.example); no trailing slash. */
export function siteUrl(env: Record<string, string | undefined> = process.env): string {
  return (env.APP_URL ?? "http://localhost:3000").replace(/\/+$/, "");
}

/** Normalises the page path after the base: "" or "/ev/x/y" (leading slash, no trailing one). */
function restPath(rest: string): string {
  if (!rest || rest === "/") return "";
  return `/${rest.replace(/^\/+|\/+$/g, "")}`;
}

/** hreflang map for one page: every served country × language pair + x-default (relative URLs). */
export function hreflangs(rest: string): Record<string, string> {
  const r = restPath(rest);
  const out: Record<string, string> = {};
  for (const { country, lang } of servedPairs())
    out[hreflangTag(country, lang)] = `${siteBase(country, lang)}${r}`;
  out["x-default"] = `${siteBase(X_DEFAULT.country, X_DEFAULT.lang)}${r}`;
  return out;
}

/** Next.js `metadata.alternates` for a page: canonical = this pair, languages = hreflangs(rest). */
export function alternates(
  country: CountrySlug,
  lang: Lang,
  rest: string,
): { canonical: string; languages: Record<string, string> } {
  return { canonical: `${siteBase(country, lang)}${restPath(rest)}`, languages: hreflangs(rest) };
}

/** Same page in another language of the same country (query kept). */
export function swapLang(pathname: string, search: string, lang: Lang): string {
  const parts = pathname.split("/");
  // ["", country, lang, ...rest]
  if (parts.length >= 3) parts[2] = lang;
  return `${parts.join("/")}${search}`;
}

/**
 * Same page in another country. Keeps the language if the target serves it, otherwise uses the
 * target's default language. Query kept.
 */
export function swapCountry(pathname: string, search: string, to: CountrySlug): string {
  const parts = pathname.split("/");
  const lang = parts[2] as Lang | undefined;
  const target = COUNTRIES[to];
  const nextLang = lang && target.served.includes(lang) ? lang : target.defaultLang;
  const rest = parts.slice(3).join("/");
  return `${siteBase(to, nextLang)}${rest ? `/${rest}` : ""}${search}`;
}
