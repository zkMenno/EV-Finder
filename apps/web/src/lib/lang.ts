import { COUNTRIES, isCountrySlug, isLang, type Lang } from "@/config/countries";

/** ?lang= wins, then the `lang` cookie, then the country's default language, then English. */
export function resolveLang(pathname: string, query: string | null | undefined, cookie: string | null | undefined): Lang {
  if (isLang(query)) return query;
  if (isLang(cookie)) return cookie;
  const seg = pathname.split("/")[1];
  return isCountrySlug(seg) ? COUNTRIES[seg].defaultLang : "en";
}
