// "See listings" deep links (T-009). Pure URL templating over src/config/countries.ts:
// we link out to public search pages and never fetch them (Decision 004).
import type { PublishedVariant } from "@ev/schema";
import { COUNTRIES, listingLinks, type CountrySlug, type ListingLink } from "@/config/countries";

/** rel for every outbound listing link: no SEO endorsement, no window.opener. */
export const LISTING_REL = "nofollow noopener";
export const LISTING_TARGET = "_blank";

export interface SeeListingsLink extends ListingLink {
  rel: string;
  target: string;
}

/** Links for one model in one country, in the country's priority order. */
export function seeListings(country: CountrySlug, row: Pick<PublishedVariant, "make_name" | "model_name">): SeeListingsLink[] {
  return listingLinks(country, row.make_name, row.model_name).map((l) => ({ ...l, rel: LISTING_REL, target: LISTING_TARGET }));
}

/** True when any link pattern for the country is still unverified (shown as a note). */
export function hasUnverified(country: CountrySlug): boolean {
  return COUNTRIES[country].listings.some((l) => !l.verified);
}
