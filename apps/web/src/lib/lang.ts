// URL language routing (Decision 015), pure so it is unit-tested. src/proxy.ts applies it.
// Public URLs are /{country}/{lang}/…; the language in the URL always wins. Headers
// (Accept-Language) never redirect: they only drive the client-side suggestion banner.
import {
  COUNTRIES,
  isCountrySlug,
  isLang,
  isServed,
  type CountrySlug,
  type Lang,
} from "@/config/countries";

/** Cookie the language switcher writes: the remembered choice, used only where the URL has no language. */
export const LANG_COOKIE = "lang";

export type LangRoute = { redirect: string; status: 307 | 308 } | null;

/** The remembered language if this country serves it, else the country's default (from config). */
export function preferredLang(country: CountrySlug, remembered: string | null | undefined): Lang {
  return isServed(country, remembered) ? remembered : COUNTRIES[country].defaultLang;
}

/**
 * Where a request should go, or null to serve it as is.
 * - `/` (= `/nl`) and `/{country}`: 307 to the remembered language (if served) or the country
 *   default. Temporary, because the target depends on the cookie.
 * - Any URL without a language segment but with a served `?lang=`: 308 to that language.
 * - Old `/{country}/…` URLs (no language segment): 308 to the same page in `?lang=` if served,
 *   else the country default; `?lang` is dropped, the rest of the query kept.
 * - `/{country}/{lang}/…` with a language the country doesn't serve: 308 to the default language.
 */
export function routeLang(pathname: string, search: string, remembered?: string | null): LangRoute {
  const parts = pathname.split("/").filter(Boolean);
  const [country, second, ...rest] = parts.length ? parts : ["nl"];
  if (!isCountrySlug(country)) return null;
  if (second !== undefined && isLang(second)) {
    if (isServed(country, second)) return null;
    const tail = rest.length ? `/${rest.join("/")}` : "";
    return {
      redirect: `/${country}/${COUNTRIES[country].defaultLang}${tail}${search}`,
      status: 308,
    };
  }
  // No language segment: `/`, `/{country}` or an old URL from before Decision 015.
  // Keep the query as written (commas in ?ids= stay commas); only the `lang` pair is dropped.
  const pairs = search.replace(/^\?/, "").split("&").filter(Boolean);
  const fromQuery = new URLSearchParams(search).get("lang");
  const qs = pairs.filter((p) => p.split("=")[0] !== "lang").join("&");
  const tail = [second, ...rest].filter((x) => x !== undefined).join("/");
  const q = qs ? `?${qs}` : "";
  if (isServed(country, fromQuery))
    return { redirect: `/${country}/${fromQuery}${tail ? `/${tail}` : ""}${q}`, status: 308 };
  if (!tail)
    return { redirect: `/${country}/${preferredLang(country, remembered)}${q}`, status: 307 };
  return { redirect: `/${country}/${COUNTRIES[country].defaultLang}/${tail}${q}`, status: 308 };
}

/**
 * First browser language (navigator.languages, i.e. Accept-Language) that this country serves and
 * that differs from the page's language; null when there is nothing to suggest.
 */
export function suggestLang(
  browser: readonly string[],
  served: readonly Lang[],
  current: Lang,
): Lang | null {
  for (const tag of browser) {
    const base = tag.toLowerCase().split("-")[0];
    if (!isLang(base)) continue;
    if (base === current) return null;
    if (served.includes(base)) return base;
  }
  return null;
}
