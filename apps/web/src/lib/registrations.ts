// Official registration counts per country (PublishedVariant.registrations, schema wave 5):
// fleet (cars on the road) and new registrations, each with its period, level and source.
// Kinds are never summed: each count is its own line. Pure: safe anywhere.
import type { Country, PublishedVariant, RegistrationCount } from "@ev/schema";

const KIND_ORDER: Record<RegistrationCount["kind"], number> = { fleet: 0, new_registrations: 1 };

/** Counts for one country: fleet first, then new registrations; newest period first; by source. */
export function registrationsFor(row: Pick<PublishedVariant, "registrations">, country: Country): RegistrationCount[] {
  const list = row.registrations?.[country] ?? [];
  return list
    .filter((r) => typeof r.count === "number" && Number.isFinite(r.count) && r.count >= 0)
    .sort(
      (a, b) =>
        KIND_ORDER[a.kind] - KIND_ORDER[b.kind] ||
        (b.period ?? "").localeCompare(a.period ?? "") ||
        a.source_id.localeCompare(b.source_id),
    );
}

/** Comparable value for the compare table's "differs" marker (null = no counts). */
export function registrationsKey(row: Pick<PublishedVariant, "registrations">, country: Country): string | null {
  const list = registrationsFor(row, country);
  return list.length ? list.map((r) => `${r.kind}:${r.period ?? ""}:${r.level ?? ""}:${r.source_id}:${r.count}`).join("|") : null;
}

/** Provenance key for a country's registration counts. */
export const registrationsProvKey = (country: Country) => `registrations.${country}`;
