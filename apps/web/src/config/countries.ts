import type { Country, Currency } from "@ev/schema";

export type Lang = "en" | "nl" | "de" | "fr" | "es" | "it";
export const LANGS: readonly Lang[] = ["en", "nl", "de", "fr", "es", "it"];

/** Lowercase URL segment for a country. */
export type CountrySlug = "nl" | "de" | "fr" | "be" | "uk";

export interface CountryConfig {
  slug: CountrySlug;
  code: Country;
  name: string;
  currency: Currency;
  defaultLang: Lang;
}

// "See listings" deep links live in config/countries/<slug>.yaml at the repo root (src/lib/listings.ts).
export const COUNTRIES: Record<CountrySlug, CountryConfig> = {
  nl: {
    slug: "nl",
    code: "NL",
    name: "Nederland",
    currency: "EUR",
    defaultLang: "nl",
  },
  de: {
    slug: "de",
    code: "DE",
    name: "Deutschland",
    currency: "EUR",
    defaultLang: "de",
  },
  fr: {
    slug: "fr",
    code: "FR",
    name: "France",
    currency: "EUR",
    defaultLang: "fr",
  },
  be: {
    slug: "be",
    code: "BE",
    name: "België / Belgique",
    currency: "EUR",
    defaultLang: "nl",
  },
  uk: {
    slug: "uk",
    code: "UK",
    name: "United Kingdom",
    currency: "GBP",
    defaultLang: "en",
  },
};

export const COUNTRY_SLUGS = Object.keys(COUNTRIES) as CountrySlug[];

export function isCountrySlug(v: string | undefined | null): v is CountrySlug {
  return v != null && Object.prototype.hasOwnProperty.call(COUNTRIES, v);
}

export function isLang(v: string | undefined | null): v is Lang {
  return v != null && (LANGS as readonly string[]).includes(v);
}
