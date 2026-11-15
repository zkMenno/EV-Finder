// Known issues (T-061): RDW APK defect rates per generation × first-registration year, from the
// release's `known_issues` (T-059). Pure view logic, no React; server pages render it.
// Rules (Q-078): a rate is only ever set next to the baseline of the SAME first-registration year
// (all sampled BEVs of that year); cohorts flagged `few_reports` are hidden ("not enough
// inspections yet"); RDW's Dutch labels are shown as published (no invented translations).
import type { FieldProvenance, KnownIssueCohort, KnownIssues } from "@ev/schema";

/** Interim source wording for RDW data (Q-037), shared with the About page credits. */
export const RDW_INTERIM_NAME = "Dutch vehicle register (RDW open data, CC0)";

/** Codes shown at the Simple level (the rest appear at Detailed / Nerd). */
export const SIMPLE_TOP_N = 3;

export interface DefectView {
  code: string;
  /** RDW's own Dutch label, as published. */
  labelNl: string;
  article?: string;
  carsWithDefect: number;
  per100: number;
  /** Same rate over all sampled BEVs of the same first-registration year. */
  cohortPer100: number;
}

export interface CohortView {
  year: number;
  ageYears: number;
  ageBand: string;
  /** Too few reports: show "not enough inspections yet", no rates. */
  hidden: boolean;
  sampleCars: number;
  carsWithAnyDefect: number;
  anyPer100: number;
  /** Baseline: all sampled BEVs first registered in the same year. */
  baseline: { sampleCars: number; anyPer100: number; generations: number };
  defects: DefectView[];
  sourceRecords: string[];
}

export interface KnownIssuesView {
  sourceId: string;
  provenance: FieldProvenance;
  inspection?: string;
  reportedFrom?: string;
  reportedTo?: string;
  retrievedAt: string;
  rateBasis: string;
  sampleRule?: string;
  cohorts: CohortView[];
}

function cohortView(
  c: KnownIssueCohort,
  labels: Map<string, { label_nl: string; article?: string }>,
): CohortView {
  return {
    year: c.first_registration_year,
    ageYears: c.age_years,
    ageBand: c.age_band,
    hidden: c.few_reports,
    sampleCars: c.sample_cars,
    carsWithAnyDefect: c.cars_with_any_defect,
    anyPer100: c.any_defect_per_100,
    baseline: {
      sampleCars: c.cohort.sample_cars,
      anyPer100: c.cohort.any_defect_per_100,
      generations: c.cohort.generations,
    },
    // A hidden cohort carries no rates at all, so nothing can leak into the page.
    defects: c.few_reports
      ? []
      : [...c.defects]
          .sort((a, b) => b.per_100 - a.per_100 || a.code.localeCompare(b.code))
          .map((d) => {
            const l = labels.get(d.code);
            return {
              code: d.code,
              labelNl: l?.label_nl ?? d.code,
              ...(l?.article ? { article: l.article } : {}),
              carsWithDefect: d.cars_with_defect,
              per100: d.per_100,
              cohortPer100: d.cohort_per_100,
            };
          }),
    sourceRecords: c.source_records ?? [],
  };
}

/** The view for one generation, or null when the release has no defect data for it. */
export function knownIssuesFor(
  ki: KnownIssues | undefined,
  generationId: string,
): KnownIssuesView | null {
  const cohorts = ki?.by_generation[generationId];
  if (!ki || !cohorts?.length) return null;
  const labels = new Map(ki.codes.map((c) => [c.code, c]));
  return {
    sourceId: ki.source_id,
    provenance: {
      source_ids: [ki.source_id],
      confidence: ki.confidence,
      agreeing_sources: 1,
      derived: true,
      // No `note`: the rate basis is a paragraph; it is shown once per section (Nerd), not on every number.
    },
    ...(ki.inspection ? { inspection: ki.inspection } : {}),
    ...(ki.reported_from ? { reportedFrom: ki.reported_from } : {}),
    ...(ki.reported_to ? { reportedTo: ki.reported_to } : {}),
    retrievedAt: ki.retrieved_at,
    rateBasis: ki.rate_basis,
    ...(ki.sample_rule ? { sampleRule: ki.sample_rule } : {}),
    cohorts: [...cohorts]
      .sort((a, b) => a.first_registration_year - b.first_registration_year)
      .map((c) => cohortView(c, labels)),
  };
}

/** Per-100 rate above, below or about the same as the same-year baseline (text, not colour). */
export function versusBaseline(rate: number, baseline: number): "higher" | "lower" | "similar" {
  // Within 20 % of the baseline (or 1 per 100) reads as "about the same": the sample is ~10 %.
  const band = Math.max(1, baseline * 0.2);
  if (rate > baseline + band) return "higher";
  if (rate < baseline - band) return "lower";
  return "similar";
}
