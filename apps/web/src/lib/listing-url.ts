// Pure "See listings" URL templating (T-009), split out of listings.ts so client components (the
// hero, T-080) can build links from one country's sites without bundling every country.
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

/** Filters every "See listings" link applies (we only list EVs). */
export const DEFAULT_FILTERS: readonly ListingFilter[] = ["electric"];

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
    // Upper-case slots (La Centrale): an override is the site's own name and is used as written
    // (T-041); without one, our name in capitals.
    .replaceAll("{MAKE}", encodeURIComponent(site.slug_overrides[slugify(makeName)] ?? makeName.toUpperCase()))
    .replaceAll("{MODEL}", encodeURIComponent(site.slug_overrides[slugify(modelName)] ?? modelName.toUpperCase()))
    .replaceAll("{makeName}", encodeURIComponent(makeName))
    .replaceAll("{modelName}", encodeURIComponent(modelName));
  const query = filters.flatMap((f) => Object.entries(site.filters[f] ?? {})).map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`);
  if (query.length) url += (url.includes("?") ? "&" : "?") + query.join("&");
  return url;
}

