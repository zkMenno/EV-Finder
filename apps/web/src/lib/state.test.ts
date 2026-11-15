import { describe, expect, it } from "vitest";
import {
  activeFilterCount,
  defaultState,
  deserializeState,
  fromSearchParams,
  hasViewParam,
  nextSort,
  serializeState,
  toSearchParams,
  type ExploreState,
} from "./state";

const full: ExploreState = {
  v: 1,
  filters: {
    priceMax: 40000,
    eras: ["2018-20", "pre-2018"],
    segments: ["C"],
    bodies: ["suv", "hatchback"],
    rangeMin: 300,
    batteryMin: 50,
    dcMin: 150,
    bootMin: 400,
    lengthMax: 4500,
    towingMin: 750,
    voltageClasses: ["800v"],
    voltageMin: 300,
    voltageMax: 900,
    fast400: true,
    chemistries: ["lfp", "nmc"],
    coolings: ["liquid"],
    charge100: true,
    tripFit: true,
  },
  sort: "range",
  dir: "desc",
  view: "cards",
  level: "nerd",
};

describe("ExploreState URL (de)serialise", () => {
  it("default state gives an empty query", () => {
    expect(toSearchParams(defaultState()).toString()).toBe("");
    expect(fromSearchParams(new URLSearchParams())).toEqual(defaultState());
  });

  it("round-trips a full state through the URL", () => {
    const qs = toSearchParams(full).toString();
    const back = fromSearchParams(new URLSearchParams(qs));
    expect(back.filters.eras).toEqual(["pre-2018", "2018-20"]); // canonical order
    expect(back).toEqual({ ...full, filters: { ...full.filters, eras: ["pre-2018", "2018-20"], bodies: ["hatchback", "suv"] } });
    expect(toSearchParams(back).toString()).toBe(qs);
  });

  it("uses short stable keys and -key for descending sort", () => {
    const p = toSearchParams(full);
    expect(p.get("price")).toBe("40000");
    expect(p.get("sort")).toBe("-range");
    expect(p.get("view")).toBe("cards");
    expect(p.get("era")).toBe("pre-2018,2018-20");
    expect(p.get("chem")).toBe("lfp,nmc");
    expect(p.get("fast400")).toBe("1");
    expect(p.get("level")).toBe("nerd");
    expect(p.get("trip")).toBe("1");
  });

  it("trip fit flag (T-036): only an on/off flag in the URL, never a place", () => {
    expect(fromSearchParams({ trip: "1" }).filters.tripFit).toBe(true);
    expect(fromSearchParams({ trip: "yes" }).filters.tripFit).toBe(false);
    const qs = toSearchParams({ ...defaultState(), filters: { ...defaultState().filters, tripFit: true } }).toString();
    expect(qs).toBe("trip=1");
    expect(activeFilterCount({ ...defaultState().filters, tripFit: true })).toBe(1);
    expect(deserializeState(JSON.stringify({ filters: { tripFit: true, townId: "nl-amsterdam", lat: 52.3 } })).filters).toEqual({ ...defaultState().filters, tripFit: true });
  });

  it("taxonomy ids are free data: any well-formed id passes, junk is dropped", () => {
    const s = fromSearchParams({ chem: "lmfp,Bad Id,sodium-ion", volt: "1200v", c100: "yes" });
    expect(s.filters.chemistries).toEqual(["lmfp", "sodium-ion"]);
    expect(s.filters.voltageClasses).toEqual(["1200v"]);
    expect(s.filters.charge100).toBe(false);
    expect(fromSearchParams({ level: "simple" }).level).toBe("simple");
    expect(fromSearchParams({ level: "expert" }).level).toBe("detailed");
  });

  it("ignores garbage without throwing", () => {
    const s = fromSearchParams({ price: "abc", range: "-5", era: "1999,2025+,2025+", seg: "Z", sort: "-nope", view: "grid" });
    expect(s.filters.priceMax).toBeNull();
    expect(s.filters.rangeMin).toBeNull();
    expect(s.filters.eras).toEqual(["2025+"]);
    expect(s.filters.segments).toEqual([]);
    expect(s.sort).toBeNull();
    expect(s.view).toBe("table");
  });

  it("accepts Next.js searchParams records with array values", () => {
    const s = fromSearchParams({ kwh: ["60", "70"], sort: "price" });
    expect(s.filters.batteryMin).toBe(60);
    expect(s.sort).toBe("price");
    expect(s.dir).toBe("asc");
  });

  it("detects an explicit view param", () => {
    expect(hasViewParam({ view: "table" })).toBe(true);
    expect(hasViewParam({})).toBe(false);
  });
});

describe("ExploreState storage (de)serialise", () => {
  it("round-trips through JSON", () => {
    expect(deserializeState(serializeState(full)).filters.towingMin).toBe(750);
    expect(deserializeState(serializeState(full)).view).toBe("cards");
  });
  it("falls back to defaults on corrupt input", () => {
    expect(deserializeState("{not json")).toEqual(defaultState());
    expect(deserializeState(null)).toEqual(defaultState());
    expect(deserializeState('{"filters":{"priceMax":"x","eras":"nope"}}')).toEqual(defaultState());
  });
});

describe("sort cycle and counters", () => {
  it("numeric column: desc → asc → off", () => {
    let s = nextSort(defaultState(), "range");
    expect([s.sort, s.dir]).toEqual(["range", "desc"]);
    s = nextSort(s, "range");
    expect([s.sort, s.dir]).toEqual(["range", "asc"]);
    s = nextSort(s, "range");
    expect(s.sort).toBeNull();
  });
  it("name column starts ascending", () => {
    expect(nextSort(defaultState(), "name").dir).toBe("asc");
  });
  it("counts active filters", () => {
    expect(activeFilterCount(defaultState().filters)).toBe(0);
    expect(activeFilterCount(full.filters)).toBe(18);
  });
});
