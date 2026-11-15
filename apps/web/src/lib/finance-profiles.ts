// Server only: finance profiles from data/taxonomy/finance_profiles.yaml, parsed at build time by
// scripts/finance.mjs into src/config/finance.generated.json (no YAML at runtime). Pages pass one
// country's profile to client components as a prop.
import type { Country } from "@ev/schema";
import generated from "@/config/finance.generated.json";
import type { FinanceProfileView } from "@/lib/finance";

const profiles = generated as unknown as Partial<Record<Country, FinanceProfileView>>;

export function financeProfile(country: Country): FinanceProfileView | null {
  return profiles[country] ?? null;
}
