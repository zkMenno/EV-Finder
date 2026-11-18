import { describe, expect, it } from "vitest";
import type { ExploreRow } from "./explore-data";
import { row, rows } from "@/test/helpers";
import { activeGroups, applyFilters, mostRestrictive, sortRows, withoutGroup } from "./filters";
import { defaultFilters, type ExploreFilters } from "./state";

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

describe("empty state: most restrictive filter (Wave 5 polish)", () => {
  const rows = [
    row({ variant_id: "a", real_range_km: 300, voltage_class_id: "400v" }),
    row({ variant_id: "b", real_range_km: 450, voltage_class_id: "400v" }),
    row({ variant_id: "c", real_range_km: 500, voltage_class_id: "800v" }),
  ];
  const count = (f: ExploreFilters) => applyFilters(rows, f, "NL").length;

  it("names the single filter whose removal brings back the most cars", () => {
    const f = { ...defaultFilters(), rangeMin: 600, voltageClasses: ["400v"] };
    expect(count(f)).toBe(0);
    // Dropping the range filter → 2 cars (a, b); dropping the voltage filter → 0.
    expect(mostRestrictive(f, count)).toEqual({ group: "rangeMin", count: 2 });
  });

  it("groups the voltage range and returns null when no single removal helps", () => {
    const f = { ...defaultFilters(), voltageMin: 900, voltageMax: 950 };
    expect(activeGroups(f)).toEqual(["voltageMin"]);
    expect(withoutGroup(f, "voltageMin")).toEqual(defaultFilters());
    const g = { ...defaultFilters(), rangeMin: 600, voltageClasses: ["900v-plus"] };
    expect(mostRestrictive(g, count)).toBeNull();
    expect(mostRestrictive(defaultFilters(), count)).toBeNull();
  });
});

describe("used price and winter range (T-130 part 2)", () => {
  // Compact bands: [build year, p25, median, p75, flags].
  const a = { ...row({ variant_id: "a", real_range_winter_km: 280 } as never), used_bands: { NL: [[2020, 14000, 16000, 18000, 1], [2022, 20000, 23000, 26000, 1]] } } as ExploreRow;
  const b = { ...row({ variant_id: "b", real_range_winter_km: 180 } as never), used_bands: { NL: [[2019, 9000, 10000, 11000, 0]] } } as ExploreRow;
  const c = row({ variant_id: "c", real_range_winter_km: null });

  it("used price: some build year's typical price inside the range; rows without bands drop out", () => {
    const ids = (p: Partial<ExploreFilters>) => applyFilters([a, b, c], f(p), "NL").map((r) => r.variant_id);
    expect(ids({ usedMax: 15000 })).toEqual(["b"]);
    expect(ids({ usedMin: 15000 })).toEqual(["a"]);
    expect(ids({ usedMin: 17000, usedMax: 22000 })).toEqual([]);
    expect(ids({ usedMin: 9000, usedMax: 30000 })).toEqual(["a", "b"]);
    // Another country has no bands: nothing matches a used price there.
    expect(applyFilters([a, b], f({ usedMax: 50000 }), "DE")).toEqual([]);
  });

  it("winter range: at least the chosen km; missing values drop out only while it is on", () => {
    expect(applyFilters([a, b, c], f({ winterMin: 200 }), "NL").map((r) => r.variant_id)).toEqual(["a"]);
    expect(applyFilters([a, b, c], f({}), "NL")).toHaveLength(3);
  });

  it("sorts by the cheapest used price (low first) and by winter range (long first), missing last", () => {
    expect(sortRows([a, c, b], "used", "asc", "NL").map((r) => r.variant_id)).toEqual(["b", "a", "c"]);
    expect(sortRows([b, c, a], "winter", "desc", "NL").map((r) => r.variant_id)).toEqual(["a", "b", "c"]);
  });

  it("the used-price pair is one removable group", () => {
    const g = f({ usedMin: 1, usedMax: 2, winterMin: 100 });
    expect(activeGroups(g)).toEqual(["usedMin", "winterMin"]);
    expect(withoutGroup(g, "usedMin")).toMatchObject({ usedMin: null, usedMax: null, winterMin: 100 });
  });
});

describe("used price with build years (review #126)", () => {
  const a = { ...row({ variant_id: "a", year_start: 2018 } as never), used_bands: { NL: [[2018, 9000, 10000, 11000, 0], [2022, 22000, 24000, 26000, 0]] } } as ExploreRow;
  it("a cheap band from before the chosen build years doesn't make the car match", () => {
    expect(applyFilters([a], f({ usedMax: 15000, yearMin: 2021 }), "NL")).toEqual([]);
    expect(applyFilters([a], f({ usedMax: 25000, yearMin: 2021 }), "NL")).toHaveLength(1);
  });
});

describe("official WLTP range (T-143, Decision 085)", () => {
  const a = row({ variant_id: "a", real_range_km: 380, wltp_range_km: 450 });
  const b = row({ variant_id: "b", real_range_km: 400, wltp_range_km: null });
  const c = row({ variant_id: "c", real_range_km: 300, wltp_range_km: 520 });

  it("WLTP filter: at least the chosen km; a car without WLTP never matches (no back-fill from real range)", () => {
    expect(applyFilters([a, b, c], f({ wltpMin: 400 }), "NL").map((r) => r.variant_id)).toEqual(["a", "c"]);
    expect(applyFilters([a, b, c], f({ wltpMin: 500 }), "NL").map((r) => r.variant_id)).toEqual(["c"]);
    expect(applyFilters([a, b, c], f({}), "NL")).toHaveLength(3);
  });

  it("range sort stays on real range; the WLTP sort orders by WLTP, missing last", () => {
    expect(sortRows([a, b, c], "range", "desc", "NL").map((r) => r.variant_id)).toEqual(["b", "a", "c"]);
    expect(sortRows([a, b, c], "wltp", "desc", "NL").map((r) => r.variant_id)).toEqual(["c", "a", "b"]);
    expect(sortRows([a, b, c], "wltp", "asc", "NL").map((r) => r.variant_id)).toEqual(["a", "c", "b"]);
  });

  it("the WLTP filter is its own removable group", () => {
    const fl = f({ wltpMin: 400, winterMin: 200 });
    expect(activeGroups(fl)).toEqual(expect.arrayContaining(["wltpMin", "winterMin"]));
    expect(withoutGroup(fl, "wltpMin")).toMatchObject({ wltpMin: null, winterMin: 200 });
  });
});
