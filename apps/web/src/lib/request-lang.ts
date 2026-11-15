import { headers } from "next/headers";
import { COUNTRIES, isLang, type CountrySlug, type Lang } from "@/config/countries";

/** Language for this request (set by src/proxy.ts). */
export async function requestLang(country?: CountrySlug): Promise<Lang> {
  const h = (await headers()).get("x-ev-lang");
  if (isLang(h)) return h;
  return country ? COUNTRIES[country].defaultLang : "en";
}
