import { describe, expect, it } from "vitest";
import { row, rows } from "@/test/helpers";
import { applyFilters, sortRows } from "./filters";
import { defaultFilters } from "./state";

const f = (p: Partial<ReturnType<typeof defaultFilters>>) => ({ ...defaultFilters(), ...p });

describe("applyFilters", () => {
  it("no active filter returns every row", () => {
    expect(applyFilters(rows, defaultFilters(), "NL")).toHaveLength(rows.length);
  });

  it("missing values are excluded only when that filter is active", () => {
    const a = row({ variant_id: "a", real_range_km: 400 });
    const b = row({ variant_id: "b", real_range_km: null });
    expect(applyFilters([a, b], f({ bootMin: null }), "NL")).toHaveLength(2);
    expect(applyFilters([a, b], f({ rangeMin: 300 }), "NL").map((r) => r.variant_id)).toEqual(["a"]);
    // A filter on another field ignores the missing range.
    expect(applyFilters([a, b], f({ eras: ["2018-20"] }), "NL")).toHaveLength(2);
  });

  it("price uses the country's new price; rows without one drop out", () => {
    const priced = rows.filter((r) => r.price_new?.UK);
    const out = applyFilters(rows, f({ priceMax: 1_000_000 }), "UK");
    expect(out).toHaveLength(priced.length);
    expect(applyFilters(rows, f({ priceMax: 30000 }), "NL").every((r) => (r.price_new?.NL?.amount ?? Infinity) <= 30000)).toBe(true);
  });

  it("max length and min towing", () => {
    expect(applyFilters(rows, f({ lengthMax: 4100 }), "NL").every((r) => (r.length_mm ?? 0) <= 4100)).toBe(true);
    expect(applyFilters(rows, f({ towingMin: 1500 }), "NL").every((r) => (r.towing_kg ?? 0) >= 1500)).toBe(true);
  });

  it("DC filter uses km in 20 min (Decision 009)", () => {
    const a = row({ variant_id: "a", dc_km_per_20min: 200, dc_km_per_10min: 50 });
    expect(applyFilters([a], f({ dcMin: 150 }), "NL")).toHaveLength(1);
  });

  it("era, segment and body are OR within a group, AND across groups", () => {
    const out = applyFilters(rows, f({ eras: ["pre-2018", "2018-20"], bodies: ["hatchback"] }), "NL");
    expect(out.length).toBeGreaterThan(0);
    expect(out.every((r) => ["pre-2018", "2018-20"].includes(r.era) && r.body === "hatchback")).toBe(true);
    expect(applyFilters([row({ variant_id: "x" })], f({ segments: ["C"] }), "NL")).toHaveLength(0);
  });
});

describe("sortRows", () => {
  const a = row({ variant_id: "a", real_range_km: 300, make_name: "Zeta" });
  const b = row({ variant_id: "b", real_range_km: null, make_name: "Alpha" });
  const c = row({ variant_id: "c", real_range_km: 500, make_name: "Mid" });

  it("keeps catalogue order without a key", () => {
    expect(sortRows([a, b, c], null, "asc", "NL")).toEqual([a, b, c]);
  });
  it("puts missing values last in both directions", () => {
    expect(sortRows([a, b, c], "range", "desc", "NL").map((r) => r.variant_id)).toEqual(["c", "a", "b"]);
    expect(sortRows([a, b, c], "range", "asc", "NL").map((r) => r.variant_id)).toEqual(["a", "c", "b"]);
  });
  it("sorts by name", () => {
    expect(sortRows([a, b, c], "name", "asc", "NL").map((r) => r.variant_id)).toEqual(["b", "c", "a"]);
  });
  it("sorts the fixture by price for the country", () => {
    const out = sortRows(rows, "price", "asc", "UK");
    const prices = out.map((r) => r.price_new?.UK?.amount ?? null);
    const firstNull = prices.indexOf(null);
    const head = prices.slice(0, firstNull) as number[];
    expect(head).toEqual([...head].sort((x, y) => x - y));
    expect(prices.slice(firstNull).every((p) => p === null)).toBe(true);
  });
});
