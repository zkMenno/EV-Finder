// Official registration counts per country (PublishedVariant.registrations, schema wave 5):
// fleet (cars on the road) and new registrations, each with its period, level and source.
// Kinds are never summed: each count is its own line. Pure: safe anywhere.
import type { Country, PublishedVariant, RegistrationCount } from "@ev/schema";

const KIND_ORDER: Record<RegistrationCount["kind"], number> = { fleet: 0, new_registrations: 1 };
/** Generation-level first; a model-level count (e.g. RDW shared-year cars, Q-066) follows it. */
const levelRank = (r: RegistrationCount) => (r.level === "model" ? 1 : 0);

/** Counts for one country: fleet first, then new registrations; newest period first; by source;
 *  generation-level before model-level. */
export function registrationsFor(row: Pick<PublishedVariant, "registrations">, country: Country): RegistrationCount[] {
  const list = row.registrations?.[country] ?? [];
  return list
    .filter((r) => typeof r.count === "number" && Number.isFinite(r.count) && r.count >= 0)
    .sort(
      (a, b) =>
        KIND_ORDER[a.kind] - KIND_ORDER[b.kind] ||
        (b.period ?? "").localeCompare(a.period ?? "") ||
        a.source_id.localeCompare(b.source_id) ||
        levelRank(a) - levelRank(b),
    );
}

/** Stable, unique-per-row list key: a row can hold a generation-level and a model-level count
 *  with the same kind, period and source (Q-066), so the level is part of the key. */
export function registrationItemKey(r: Pick<RegistrationCount, "kind" | "period" | "level" | "source_id">): string {
  return `${r.kind}-${r.period ?? ""}-${r.level ?? "generation"}-${r.source_id}`;
}

/** Comparable value for the compare table's "differs" marker (null = no counts). */
export function registrationsKey(row: Pick<PublishedVariant, "registrations">, country: Country): string | null {
  const list = registrationsFor(row, country);
  return list.length ? list.map((r) => `${r.kind}:${r.period ?? ""}:${r.level ?? ""}:${r.source_id}:${r.count}`).join("|") : null;
}

/** Provenance key for a country's registration counts. */
export const registrationsProvKey = (country: Country) => `registrations.${country}`;
