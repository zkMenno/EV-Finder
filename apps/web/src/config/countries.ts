import type { Country, Currency } from "@ev/schema";

export type Lang = "en" | "nl" | "de" | "fr" | "es" | "it";
export const LANGS: readonly Lang[] = ["en", "nl", "de", "fr", "es", "it"];

/** Lowercase URL segment for a country. */
export type CountrySlug = "nl" | "de" | "fr" | "be" | "uk";

export interface ListingSite {
  id: string;
  name: string;
  /**
   * Public search URL template. Placeholders: {make}, {model} (slug-cased, URL-encoded)
   * {makeName}, {modelName} (display names) and {MAKE}, {MODEL} (upper-cased names), all URL-encoded. Only public search pages:
   * we link out, we never fetch these (Decision 004).
   */
  template: string;
  /** Lower = shown first. */
  priority: number;
  /** Per-site overrides for our make/model slugs, e.g. { "mercedes-benz": "mercedes" }. */
  params?: Record<string, string>;
  /** URL pattern not checked against the live site yet. */
  verified: boolean;
}

export interface CountryConfig {
  slug: CountrySlug;
  code: Country;
  name: string;
  currency: Currency;
  defaultLang: Lang;
  listings: ListingSite[];
}

// NOTE: every listing URL pattern below is an unverified best guess (verified: false).
// Someone must open each one by hand and confirm the path/params before launch.
export const COUNTRIES: Record<CountrySlug, CountryConfig> = {
  nl: {
    slug: "nl",
    code: "NL",
    name: "Nederland",
    currency: "EUR",
    defaultLang: "nl",
    listings: [
      { id: "autoscout24-nl", name: "AutoScout24", template: "https://www.autoscout24.nl/lst/{make}/{model}?fuel=E", priority: 1, verified: false },
      { id: "marktplaats", name: "Marktplaats", template: "https://www.marktplaats.nl/q/{makeName}+{modelName}/", priority: 2, verified: false },
      { id: "gaspedaal", name: "Gaspedaal", template: "https://www.gaspedaal.nl/{make}/{model}/elektrisch", priority: 3, verified: false },
    ],
  },
  de: {
    slug: "de",
    code: "DE",
    name: "Deutschland",
    currency: "EUR",
    defaultLang: "de",
    listings: [
      { id: "mobile-de", name: "mobile.de", template: "https://suchen.mobile.de/fahrzeuge/search.html?isSearchRequest=true&ft=ELECTRICITY&q={makeName}+{modelName}", priority: 1, verified: false },
      { id: "autoscout24-de", name: "AutoScout24", template: "https://www.autoscout24.de/lst/{make}/{model}?fuel=E", priority: 2, verified: false },
    ],
  },
  fr: {
    slug: "fr",
    code: "FR",
    name: "France",
    currency: "EUR",
    defaultLang: "fr",
    listings: [
      { id: "leboncoin", name: "leboncoin", template: "https://www.leboncoin.fr/recherche?category=2&text={makeName}+{modelName}&fuel=4", priority: 1, verified: false },
      { id: "lacentrale", name: "La Centrale", template: "https://www.lacentrale.fr/listing?makesModelsCommercialNames={MAKE}%3A{MODEL}&energies=elec", priority: 2, verified: false },
      { id: "autoscout24-fr", name: "AutoScout24", template: "https://www.autoscout24.fr/lst/{make}/{model}?fuel=E", priority: 3, verified: false },
    ],
  },
  be: {
    slug: "be",
    code: "BE",
    name: "België / Belgique",
    currency: "EUR",
    defaultLang: "nl",
    listings: [
      { id: "2dehands", name: "2dehands", template: "https://www.2dehands.be/q/{makeName}+{modelName}/", priority: 1, verified: false },
      { id: "autoscout24-be", name: "AutoScout24", template: "https://www.autoscout24.be/nl/lst/{make}/{model}?fuel=E", priority: 2, verified: false },
    ],
  },
  uk: {
    slug: "uk",
    code: "UK",
    name: "United Kingdom",
    currency: "GBP",
    defaultLang: "en",
    listings: [
      { id: "autotrader-uk", name: "Autotrader", template: "https://www.autotrader.co.uk/car-search?make={makeName}&model={modelName}&fuel-type=Electric", priority: 1, verified: false },
    ],
  },
};

export const COUNTRY_SLUGS = Object.keys(COUNTRIES) as CountrySlug[];

export function isCountrySlug(v: string | undefined | null): v is CountrySlug {
  return v != null && Object.prototype.hasOwnProperty.call(COUNTRIES, v);
}

export function isLang(v: string | undefined | null): v is Lang {
  return v != null && (LANGS as readonly string[]).includes(v);
}

function slugify(s: string): string {
  return s
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

export interface ListingLink {
  id: string;
  name: string;
  url: string;
  verified: boolean;
}

/** "See listings" deep links for one model, sorted by priority. Pure string templating, no fetching. */
export function listingLinks(country: CountrySlug, makeName: string, modelName: string): ListingLink[] {
  return [...COUNTRIES[country].listings]
    .sort((a, b) => a.priority - b.priority)
    .map((site) => {
      const make = site.params?.[slugify(makeName)] ?? slugify(makeName);
      const model = site.params?.[slugify(modelName)] ?? slugify(modelName);
      const url = site.template
        .replaceAll("{make}", encodeURIComponent(make))
        .replaceAll("{model}", encodeURIComponent(model))
        .replaceAll("{MAKE}", encodeURIComponent(makeName.toUpperCase()))
        .replaceAll("{MODEL}", encodeURIComponent(modelName.toUpperCase()))
        .replaceAll("{makeName}", encodeURIComponent(makeName))
        .replaceAll("{modelName}", encodeURIComponent(modelName));
      return { id: site.id, name: site.name, url, verified: site.verified };
    });
}
