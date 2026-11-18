import { describe, expect, it } from "vitest";
import type { ExploreRow } from "./explore-data";
import { row } from "@/test/helpers";
import { brandCounts, generationCards, generationCount, usedSpan } from "./generation-cards";

const v = (id: string, gen: string, p: Record<string, unknown> = {}) =>
  row({ variant_id: id, generation_id: gen, make_id: gen.split("-")[0], make_name: gen.split("-")[0], ...p } as never);

describe("generationCards (T-130: one card per generation)", () => {
  const rows = [
    v("m3-sr", "tesla-m3", { year_start: 2019, year_end: 2023, real_range_km: 350, real_range_winter_km: 240, dc_km_per_20min: 250 }),
    v("zoe", "renault-zoe", { year_start: 2013, year_end: 2022, real_range_km: 280, real_range_winter_km: null }),
    v("m3-lr", "tesla-m3", { year_start: 2019, year_end: null, real_range_km: 480, real_range_winter_km: 330, dc_km_per_20min: 300 }),
  ];
  const cards = generationCards(rows, "NL");

  it("groups by generation in order of first appearance (the sort order carries over)", () => {
    expect(cards.map((c) => c.generation_id)).toEqual(["tesla-m3", "renault-zoe"]);
    expect(cards[0]!.lead.variant_id).toBe("m3-sr");
    expect(cards[0]!.rows.map((r) => r.variant_id)).toEqual(["m3-sr", "m3-lr"]);
  });

  it("spans the matching variants: years (still on sale = null), min–max facts, provenance row = highest", () => {
    const m3 = cards[0]!;
    expect([m3.yearStart, m3.yearEnd]).toEqual([2019, null]);
    expect(m3.summer).toMatchObject({ min: 350, max: 480 });
    expect(m3.winter?.row.variant_id).toBe("m3-lr");
    expect(m3.dc20).toMatchObject({ min: 250, max: 300 });
    const zoe = cards[1]!;
    expect(zoe.yearEnd).toBe(2022);
    // No value at all: no span (the card shows "—", never 0).
    expect(zoe.winter).toBeNull();
  });

  it("counts generations and brands", () => {
    expect(generationCount(rows)).toBe(2);
    expect(brandCounts(rows)).toEqual([
      { id: "renault", name: "renault", count: 1 },
      { id: "tesla", name: "tesla", count: 1 },
    ]);
  });
});

describe("usedSpan", () => {
  it("cheapest lower quartile to dearest upper quartile; estimate and low confidence carry over", () => {
    const a = { ...row({ variant_id: "a" } as never), used_bands: { NL: [[2020, 14000, 16000, 18000, 1, { src: "Curve", date: "2026-11-17" }]] } } as ExploreRow;
    const b = { ...row({ variant_id: "b" } as never), used_bands: { NL: [[2022, null, 25000, null, 2]] } } as ExploreRow;
    expect(usedSpan([a, b], "NL")).toEqual({ low: 14000, high: 25000, estimate: true, lowConfidence: true, how: { src: "Curve", date: "2026-11-17" } });
    expect(usedSpan([a, b], "DE")).toBeNull();
  });
});

describe("usedSpan follows the visitor's used-price and build-year filters", () => {
  const a = { ...row({ variant_id: "a" } as never), used_bands: { NL: [[2019, 9000, 10000, 11000, 0], [2021, 14000, 16000, 18000, 0], [2023, 24000, 27000, 30000, 1]] } } as ExploreRow;
  it("keeps the bands whose typical price and build year are inside the filters", () => {
    expect(usedSpan([a], "NL", { usedMax: 20000 })).toMatchObject({ low: 9000, high: 18000, estimate: false });
    expect(usedSpan([a], "NL", { yearMin: 2022 })).toMatchObject({ low: 24000, high: 30000, estimate: true });
    // Nothing inside the filters: all bands rather than none.
    expect(usedSpan([a], "NL", { usedMax: 5000 })).toMatchObject({ low: 9000, high: 30000 });
  });
});
