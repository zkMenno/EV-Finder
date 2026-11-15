import type { KnownIssues } from "@ev/schema";
import { describe, expect, it } from "vitest";
import { knownIssuesFor, RDW_INTERIM_NAME, versusBaseline } from "./known-issues";
import { FALLBACK_WORDING } from "./credits";

const ki: KnownIssues = {
  country: "NL",
  source_id: "rdw-defects",
  retrieved_at: "2026-11-15",
  confidence: "medium",
  reported_from: "2022-06-02",
  reported_to: "2026-11-13",
  rate_basis: "Cars with the defect per 100 sampled cars of the same generation and first-registration year.",
  codes: [
    { code: "210", label_nl: "Remschijf versleten", article: "5.*.1" },
    { code: "AC1", label_nl: "Band profiel" },
  ],
  by_generation: {
    g1: [
      {
        first_registration_year: 2021,
        age_years: 5,
        age_band: "5-6 years",
        sample_cars: 300,
        cars_with_any_defect: 90,
        any_defect_per_100: 30,
        few_reports: false,
        cohort: { generations: 10, sample_cars: 5000, any_defect_per_100: 40 },
        defects: [
          { code: "AC1", cars_with_defect: 9, per_100: 3, cohort_per_100: 4 },
          { code: "210", cars_with_defect: 30, per_100: 10, cohort_per_100: 8 },
        ],
      },
      {
        first_registration_year: 2019,
        age_years: 7,
        age_band: "7-9 years",
        sample_cars: 200,
        cars_with_any_defect: 80,
        any_defect_per_100: 40,
        few_reports: false,
        cohort: { generations: 8, sample_cars: 4000, any_defect_per_100: 45 },
        defects: [{ code: "999", cars_with_defect: 5, per_100: 2.5, cohort_per_100: 1 }],
      },
      {
        first_registration_year: 2023,
        age_years: 3,
        age_band: "3-4 years",
        sample_cars: 400,
        cars_with_any_defect: 4,
        any_defect_per_100: 1,
        few_reports: true,
        cohort: { generations: 20, sample_cars: 9000, any_defect_per_100: 2 },
        defects: [{ code: "210", cars_with_defect: 3, per_100: 0.8, cohort_per_100: 1 }],
      },
    ],
  },
};

describe("knownIssuesFor", () => {
  it("returns null without data for the generation", () => {
    expect(knownIssuesFor(undefined, "g1")).toBeNull();
    expect(knownIssuesFor(ki, "nope")).toBeNull();
  });

  it("orders cohorts oldest first and defects by rate", () => {
    const v = knownIssuesFor(ki, "g1")!;
    expect(v.cohorts.map((c) => c.year)).toEqual([2019, 2021, 2023]);
    expect(v.cohorts[1]!.defects.map((d) => d.code)).toEqual(["210", "AC1"]);
  });

  it("pairs every rate with the baseline of its own first-registration year only (Q-078)", () => {
    const v = knownIssuesFor(ki, "g1")!;
    const c2021 = v.cohorts.find((c) => c.year === 2021)!;
    expect(c2021.baseline.anyPer100).toBe(40);
    expect(c2021.defects.find((d) => d.code === "210")!.cohortPer100).toBe(8);
    const c2019 = v.cohorts.find((c) => c.year === 2019)!;
    expect(c2019.baseline.anyPer100).toBe(45);
  });

  it("hides few_reports cohorts and drops their rates entirely", () => {
    const c = knownIssuesFor(ki, "g1")!.cohorts.find((x) => x.year === 2023)!;
    expect(c.hidden).toBe(true);
    expect(c.defects).toEqual([]);
  });

  it("keeps RDW's Dutch labels as published; unknown codes fall back to the code", () => {
    const v = knownIssuesFor(ki, "g1")!;
    const d = v.cohorts[1]!.defects.find((x) => x.code === "210")!;
    expect(d.labelNl).toBe("Remschijf versleten");
    expect(d.article).toBe("5.*.1");
    expect(v.cohorts[0]!.defects[0]!.labelNl).toBe("999");
  });

  it("carries provenance (source, confidence) and the rate basis once for the section", () => {
    const v = knownIssuesFor(ki, "g1")!;
    expect(v.provenance.source_ids).toEqual(["rdw-defects"]);
    expect(v.provenance.confidence).toBe("medium");
    expect(v.rateBasis).toContain("per 100 sampled cars");
  });
});

describe("versusBaseline", () => {
  it("reads within 20 % (or 1 per 100) as similar", () => {
    expect(versusBaseline(30, 40)).toBe("lower");
    expect(versusBaseline(50, 40)).toBe("higher");
    expect(versusBaseline(36, 40)).toBe("similar");
    expect(versusBaseline(1.5, 1)).toBe("similar");
  });
});

describe("RDW wording (Q-037 interim)", () => {
  it("uses the same interim name on the page and in the credits for both RDW sources", () => {
    expect(RDW_INTERIM_NAME).toBe("Dutch vehicle register (RDW open data, CC0)");
    expect(FALLBACK_WORDING.rdw?.override).toBe(RDW_INTERIM_NAME);
    expect(FALLBACK_WORDING["rdw-defects"]?.override).toBe(RDW_INTERIM_NAME);
  });
});
