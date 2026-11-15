export interface CountryLanguages {
  languages: string[];
  default_language: string;
  served: string[];
}
export const OUT_FILE: string;
export const LANGS: string[];
export function validateLanguages(country: string, doc: unknown): CountryLanguages;
export function loadCountryLanguages(dir?: string): Record<string, CountryLanguages>;
export function serialize(config: unknown): string;
