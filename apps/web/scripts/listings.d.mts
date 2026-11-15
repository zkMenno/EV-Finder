// Types for scripts/listings.mjs (imported by the drift-guard test).
export interface ListingSiteConfig {
  site: string;
  label: string;
  url_template: string;
  filters: Record<string, Record<string, string>>;
  slug_overrides: Record<string, string>;
  priority: number;
  verified: boolean;
}
export const CONFIG_DIR: string;
export const OUT_FILE: string;
export const COUNTRIES: string[];
export function validateCountry(country: string, doc: unknown): ListingSiteConfig[];
export function loadListingConfig(dir?: string): Record<string, ListingSiteConfig[]>;
export function serialize(config: Record<string, ListingSiteConfig[]>): string;
