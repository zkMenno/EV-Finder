// "See listings" deep links (T-009). Pure URL templating over config/countries/<country>.yaml,
// which scripts/listings.mjs validates and turns into src/config/listings.generated.json at build
// time (no YAML library at runtime). We link out to public search pages and never fetch them
// (Decision 004). Server only: the page passes finished links to <SeeListings>.
import type { PublishedVariant } from "@ev/schema";
import type { CountrySlug } from "@/config/countries";
import generated from "@/config/listings.generated.json";

export type ListingFilter = "electric";

export interface ListingSite {
  site: string;
  label: string;
  /** https URL; placeholders {make} {model} (slugs), {makeName} {modelName}, {MAKE} {MODEL}; all URL-encoded. */
  url_template: string;
  /** Our filter → query parameters on this site. */
  filters: Partial<Record<ListingFilter, Record<string, string>>>;
  /** Our make/model slug → the site's slug, e.g. { "mercedes-benz": "mercedes" }. */
  slug_overrides: Record<string, string>;
  /** Lower = shown first. */
  priority: number;
  /** URL pattern checked against the live site by hand. */
  verified: boolean;
}

// The JSON was validated by scripts/listings.mjs (and a test checks it matches the YAML); JSON
// inference gives each site its own literal shape, so widen via unknown.
export const LISTING_SITES: Record<CountrySlug, readonly ListingSite[]> = generated as unknown as Record<CountrySlug, ListingSite[]>;

/** Filters every "See listings" link applies (we only list EVs). */
const DEFAULT_FILTERS: readonly ListingFilter[] = ["electric"];

/** rel for every outbound listing link: no SEO endorsement, no window.opener. */
export const LISTING_REL = "nofollow noopener";
export const LISTING_TARGET = "_blank";

export interface ListingLink {
  id: string;
  name: string;
  url: string;
  verified: boolean;
}

export interface SeeListingsLink extends ListingLink {
  rel: string;
  target: string;
}

function slugify(s: string): string {
  return s
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

/** Fills one site's template for one model and appends its filter parameters. */
export function buildListingUrl(site: ListingSite, makeName: string, modelName: string, filters: readonly ListingFilter[] = DEFAULT_FILTERS): string {
  const make = site.slug_overrides[slugify(makeName)] ?? slugify(makeName);
  const model = site.slug_overrides[slugify(modelName)] ?? slugify(modelName);
  let url = site.url_template
    .replaceAll("{make}", encodeURIComponent(make))
    .replaceAll("{model}", encodeURIComponent(model))
    .replaceAll("{MAKE}", encodeURIComponent(makeName.toUpperCase()))
    .replaceAll("{MODEL}", encodeURIComponent(modelName.toUpperCase()))
    .replaceAll("{makeName}", encodeURIComponent(makeName))
    .replaceAll("{modelName}", encodeURIComponent(modelName));
  const query = filters.flatMap((f) => Object.entries(site.filters[f] ?? {})).map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`);
  if (query.length) url += (url.includes("?") ? "&" : "?") + query.join("&");
  return url;
}

/** "See listings" deep links for one model, sorted by priority. Pure string templating, no fetching. */
export function listingLinks(country: CountrySlug, makeName: string, modelName: string): ListingLink[] {
  return [...LISTING_SITES[country]]
    .sort((a, b) => a.priority - b.priority)
    .map((site) => ({ id: site.site, name: site.label, url: buildListingUrl(site, makeName, modelName), verified: site.verified }));
}

/** Links for one model in one country, in the country's priority order. */
export function seeListings(country: CountrySlug, row: Pick<PublishedVariant, "make_name" | "model_name">): SeeListingsLink[] {
  return listingLinks(country, row.make_name, row.model_name).map((l) => ({ ...l, rel: LISTING_REL, target: LISTING_TARGET }));
}

/** True when any link pattern for the country is still unverified (shown as a note). */
export function hasUnverified(country: CountrySlug): boolean {
  return LISTING_SITES[country].some((l) => !l.verified);
}
