import { describe, expect, it } from "vitest";
import { PRICE_INDEX, PRICE_INDEX_COUNTRIES, PRICE_INDEX_YEARS, priceIndex } from "./price-index";

describe("price index placeholder (layer 0)", () => {
  it("has every country and year, all null", () => {
    expect(Object.keys(PRICE_INDEX).sort()).toEqual([...PRICE_INDEX_COUNTRIES].sort());
    const years = PRICE_INDEX_YEARS.to - PRICE_INDEX_YEARS.from + 1;
    for (const c of PRICE_INDEX_COUNTRIES) {
      expect(Object.keys(PRICE_INDEX[c])).toHaveLength(years);
      expect(Object.values(PRICE_INDEX[c]).every((v) => v === null)).toBe(true);
    }
    expect(priceIndex("NL", 2020)).toBeNull();
    expect(priceIndex("UK", 1990)).toBeNull();
  });
});
