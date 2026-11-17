import type { Country, Currency } from "@ev/schema";
// Languages per country come from config/countries/<cc>.yaml (`languages`, `default_language`),
// validated into this JSON by scripts/countries.mjs (Decision 015). Never hard-code them here.
import languages from "./countries.generated.json";

export type Lang = "en" | "nl" | "de" | "fr" | "es" | "it";
export const LANGS: readonly Lang[] = ["en", "nl", "de", "fr", "es", "it"];

/** Lowercase URL segment for a country. */
export type CountrySlug = "nl" | "de" | "fr" | "be" | "uk" | "es" | "it";

export interface CountryConfig {
  slug: CountrySlug;
  code: Country;
  name: string;
  currency: Currency;
  /** /{country}/ redirects here (config `default_language`). */
  defaultLang: Lang;
  /** The country's own UI languages (config `languages`). */
  languages: readonly Lang[];
  /** Languages we serve URLs for: its own languages + English (Decision 015). */
  served: readonly Lang[];
}

type LangConfig = { languages: string[]; default_language: string; served: string[] };
const langCfg = languages as Record<CountrySlug, LangConfig>;
const lc = (slug: CountrySlug) => ({
  defaultLang: langCfg[slug].default_language as Lang,
  languages: langCfg[slug].languages as Lang[],
  served: langCfg[slug].served as Lang[],
});

// "See listings" deep links live in config/countries/<slug>.yaml at the repo root (src/lib/listings.ts).
export const COUNTRIES: Record<CountrySlug, CountryConfig> = {
  nl: {
    slug: "nl",
    code: "NL",
    name: "Nederland",
    currency: "EUR",
    ...lc("nl"),
  },
  de: {
    slug: "de",
    code: "DE",
    name: "Deutschland",
    currency: "EUR",
    ...lc("de"),
  },
  fr: {
    slug: "fr",
    code: "FR",
    name: "France",
    currency: "EUR",
    ...lc("fr"),
  },
  be: {
    slug: "be",
    code: "BE",
    name: "België / Belgique",
    currency: "EUR",
    ...lc("be"),
  },
  uk: {
    slug: "uk",
    code: "UK",
    name: "United Kingdom",
    currency: "GBP",
    ...lc("uk"),
  },
  // Decision 066: Spain and Italy, served in their own language only (/es/es, /it/it) + English.
  es: {
    slug: "es",
    code: "ES",
    name: "España",
    currency: "EUR",
    ...lc("es"),
  },
  it: {
    slug: "it",
    code: "IT",
    name: "Italia",
    currency: "EUR",
    ...lc("it"),
  },
};

export const COUNTRY_SLUGS = Object.keys(COUNTRIES) as CountrySlug[];

export function isCountrySlug(v: string | undefined | null): v is CountrySlug {
  return v != null && Object.prototype.hasOwnProperty.call(COUNTRIES, v);
}

export function isLang(v: string | undefined | null): v is Lang {
  return v != null && (LANGS as readonly string[]).includes(v);
}

/** Is `lang` served for `country` (its own languages + English)? */
export function isServed(country: CountrySlug, lang: string | undefined | null): lang is Lang {
  return isLang(lang) && COUNTRIES[country].served.includes(lang);
}

/** Every served country × language pair, in config order (static params, hreflang, sitemap). */
export function servedPairs(): { country: CountrySlug; lang: Lang }[] {
  return COUNTRY_SLUGS.flatMap((country) => COUNTRIES[country].served.map((lang) => ({ country, lang })));
}

/** BCP 47 tag for hreflang: language-REGION (uk → GB). */
export function hreflangTag(country: CountrySlug, lang: Lang): string {
  return `${lang}-${country === "uk" ? "GB" : country.toUpperCase()}`;
}
