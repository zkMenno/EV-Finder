// "See listings" deep links (T-009). Pure URL templating over config/countries/<country>.yaml,
// which scripts/listings.mjs validates and turns into src/config/listings.generated.json at build
// time (no YAML library at runtime). We link out to public search pages and never fetch them
// (Decision 004). Server only: the page passes finished links to <SeeListings>.
import type { PublishedVariant } from "@ev/schema";
import type { CountrySlug } from "@/config/countries";
import generated from "@/config/listings.generated.json";

import { buildListingUrl, type ListingSite } from "./listing-url";

export { buildListingUrl, DEFAULT_FILTERS, type ListingFilter, type ListingSite } from "./listing-url";

// The JSON was validated by scripts/listings.mjs (and a test checks it matches the YAML); JSON
// inference gives each site its own literal shape, so widen via unknown.
export const LISTING_SITES: Record<CountrySlug, readonly ListingSite[]> = generated as unknown as Record<CountrySlug, ListingSite[]>;

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
