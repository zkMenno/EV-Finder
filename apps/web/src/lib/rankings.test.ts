import type { PublishedVariant } from "@ev/schema";
import { describe, expect, it } from "vitest";
import { catalogue } from "@/test/helpers";
import { fastestDc, isRankingId, mostAvailableNl, PRICE_THRESHOLD, ranking, rangeUnderPrice, RANKING_IDS } from "./rankings";

const rows = catalogue.rows;

function v(over: Partial<PublishedVariant> & { variant_id: string }): PublishedVariant {
  return {
    release: 1,
    variant_name: over.variant_id,
    generation_id: `g-${over.variant_id}`,
    generation_name: "G",
    model_id: "m",
    model_name: "M",
    make_id: "mk",
    make_name: "Make",
    year_start: 2020,
    era: "2018-20",
    quality_tier: "sourced",
    provenance: {},
    ...over,
  };
}

describe("ranking ids", () => {
  it("are the three lists", () => {
    expect(RANKING_IDS).toHaveLength(3);
    expect(isRankingId("fastest-dc")).toBe(true);
    expect(isRankingId("nope")).toBe(false);
  });
});

describe("rangeUnderPrice", () => {
  it("thresholds: €30,000 and £26,000", () => {
    expect(PRICE_THRESHOLD).toEqual({ EUR: 30000, GBP: 26000 });
  });

  it("keeps only priced rows under the threshold, sorted by real range", () => {
    const out = rangeUnderPrice(rows, "FR", "EUR");
    expect(out.length).toBeGreaterThan(0);
    for (const e of out) {
      expect(e.row.price_new!.FR!.amount).toBeLessThan(30000);
      expect(e.field).toBe("real_range_km");
    }
    // Renault 5 40 kWh (27,990) and Fiat 500e (29,990) are under €30k in FR in the fixture.
    expect(out.map((e) => e.row.variant_id)).toEqual(["fiat-500e-332-42kwh", "renault-5-gen1-40kwh"]);
    expect(out[0]!.rank).toBe(1);
  });

  it("uses the GBP threshold for the UK and ignores other currencies", () => {
    const out = rangeUnderPrice(rows, "UK", "GBP");
    for (const e of out) expect(e.row.price_new!.UK!.amount).toBeLessThan(26000);
    // fixture: Renault 5 52 kWh is £26,995 (over), 40 kWh has no UK price → nothing
    expect(out).toEqual([]);
    const wrongCurrency = [v({ variant_id: "x", real_range_km: 300, price_new: { UK: { amount: 20000, currency: "EUR" } } })];
    expect(rangeUnderPrice(wrongCurrency, "UK", "GBP")).toEqual([]);
  });

  it("is empty (never guesses) when no row has a price for the country", () => {
    const unpriced = rows.map((r) => ({ ...r, price_new: {} }));
    expect(rangeUnderPrice(unpriced, "NL", "EUR")).toEqual([]);
  });

  it("drops priced rows without a real range", () => {
    expect(rangeUnderPrice([v({ variant_id: "x", price_new: { NL: { amount: 20000, currency: "EUR" } } })], "NL", "EUR")).toEqual([]);
  });

  it("breaks range ties by lower price", () => {
    const out = rangeUnderPrice(
      [
        v({ variant_id: "dear", real_range_km: 300, price_new: { NL: { amount: 29000, currency: "EUR" } } }),
        v({ variant_id: "cheap", real_range_km: 300, price_new: { NL: { amount: 25000, currency: "EUR" } } }),
      ],
      "NL",
      "EUR",
    );
    expect(out.map((e) => e.row.variant_id)).toEqual(["cheap", "dear"]);
    expect(out.map((e) => e.rank)).toEqual([1, 1]);
  });
});

describe("fastestDc", () => {
  it("ranks by km in 20 min, not peak kW", () => {
    const out = fastestDc([
      v({ variant_id: "peaky", dc_peak_kw: 350, dc_km_per_20min: 150 }),
      v({ variant_id: "flat", dc_peak_kw: 150, dc_km_per_20min: 220 }),
      v({ variant_id: "none", dc_peak_kw: 100 }),
    ]);
    expect(out.map((e) => e.row.variant_id)).toEqual(["flat", "peaky"]);
  });

  it("flags estimates from provenance", () => {
    const out = fastestDc([
      v({
        variant_id: "est",
        dc_km_per_20min: 100,
        provenance: { dc_km_per_20min: { source_ids: ["model-estimate"], confidence: "low", estimate: true } },
      }),
    ]);
    expect(out[0]!.estimate).toBe(true);
  });

  it("is sorted descending on the fixture and respects the limit", () => {
    const out = fastestDc(rows, 5);
    expect(out).toHaveLength(5);
    const vals = out.map((e) => e.value);
    expect([...vals].sort((a, b) => b - a)).toEqual(vals);
    expect(out[0]!.row.variant_id).toBe("hyundai-ioniq-5-ne-84kwh");
  });

  it("shares ranks on ties", () => {
    const out = fastestDc([v({ variant_id: "a", dc_km_per_20min: 100 }), v({ variant_id: "b", dc_km_per_20min: 100 }), v({ variant_id: "c", dc_km_per_20min: 90 })]);
    expect(out.map((e) => e.rank)).toEqual([1, 1, 3]);
  });
});

describe("mostAvailableNl", () => {
  it("one row per generation, by RDW count", () => {
    const out = mostAvailableNl(rows);
    const gens = out.map((e) => e.row.generation_id);
    expect(new Set(gens).size).toBe(gens.length);
    expect(out[0]!.row.generation_id).toBe("tesla-model-3-gen1");
    expect(out[0]!.value).toBe(51200);
    expect(out.every((e) => e.field === "registered_count_nl")).toBe(true);
    // generations without a count are left out
    expect(gens).not.toContain("hyundai-kona-sx2");
  });

  it("picks the earliest variant as the representative row", () => {
    const out = mostAvailableNl([
      v({ variant_id: "b", generation_id: "g1", year_start: 2021, registered_count_nl: 10 }),
      v({ variant_id: "a", generation_id: "g1", year_start: 2019, registered_count_nl: 10 }),
    ]);
    expect(out).toHaveLength(1);
    expect(out[0]!.row.variant_id).toBe("a");
  });
});

describe("ranking()", () => {
  it("dispatches each list", () => {
    for (const id of RANKING_IDS) expect(Array.isArray(ranking(id, rows, "NL", "EUR"))).toBe(true);
  });
});
