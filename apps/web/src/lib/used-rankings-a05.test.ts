// A-05 L3 (ranking value has its own provenance, shown through <Num>) and L4 (hreflang on
// used-price lists only for countries where the list exists). FIXTURE values, not real data.
import type { PublishedVariant, UsedPriceBand } from "@ev/schema";
import { describe, expect, it } from "vitest";
import { COUNTRIES, type CountrySlug } from "@/config/countries";
import { hreflangs } from "./site-paths";
import { usedRanking, valueProvenance, visibleUsedRankings } from "./used-rankings";

const gen = (i: number, range: number, conf: "high" | "medium" | "low" = "high"): PublishedVariant =>
  ({
    release: 1,
    variant_id: `v${i}`,
    variant_name: `V${i}`,
    generation_id: `g${i}`,
    generation_name: `G${i}`,
    model_id: `m${i}`,
    model_name: `M${i}`,
    make_id: "mk",
    make_name: "Make",
    year_start: 2019,
    era: "2018-20",
    quality_tier: "sourced",
    real_range_km: range,
    provenance: { real_range_km: { source_ids: ["model-estimate"], confidence: conf, estimate: true, fact_ids: [`f${i}`] } },
  }) as PublishedVariant;
const band = (g: string, median: number, country = "NL", samples = 12): UsedPriceBand => ({
  generation_id: g,
  country: country as UsedPriceBand["country"],
  currency: "EUR",
  p25: median - 500,
  median,
  p75: median + 500,
  samples,
  period: "2026-10",
  age_band_years: null,
  source_id: "fixture-prices",
  fact_ids: [`p-${g}`],
});
const ROWS = [1, 2, 3, 4, 5].map((i) => gen(i, 200 + i * 20));

describe("L3: used-ranking value provenance", () => {
  it("derived estimate listing the range and price sources, lower confidence of the two", () => {
    const p = valueProvenance(ROWS[0]!.provenance.real_range_km, band("g1", 10000));
    expect(p).toMatchObject({ derived: true, estimate: true, confidence: "low" }); // 12 samples → price "low"
    expect(p.source_ids).toEqual(["model-estimate", "fixture-prices"]);
    expect(p.fact_ids).toEqual(["f1", "p-g1"]);
    expect(p.note).toContain("12 samples");
    const medium = valueProvenance({ source_ids: ["a"], confidence: "high" }, band("g1", 10000, "NL", 25));
    expect(medium.confidence).toBe("medium");
    expect(valueProvenance(undefined, band("g1", 10000, "NL", 25)).confidence).toBe("low");
  });

  it("every ranked entry carries it", () => {
    const list = usedRanking("best-used-under-15k", ROWS, ROWS.map((r) => band(r.generation_id, 12000, "NL", 25)), "NL", "EUR");
    expect(list).toHaveLength(5);
    for (const e of list) {
      expect(e.valueProvenance.estimate).toBe(true);
      expect(e.valueProvenance.source_ids).toContain("fixture-prices");
    }
  });
});

describe("L4: hreflang on used-price lists", () => {
  const exists = (bands: UsedPriceBand[]) => (c: CountrySlug) =>
    visibleUsedRankings(ROWS, bands, COUNTRIES[c].code, COUNTRIES[c].currency).includes("best-used-under-15k");

  it("lists only countries where the list exists; x-default stays on /nl/en when NL has it", () => {
    const h = hreflangs("top/best-used-under-15k", exists(ROWS.map((r) => band(r.generation_id, 12000, "NL"))));
    const keys = Object.keys(h).filter((k) => k !== "x-default");
    expect(keys.length).toBeGreaterThan(0);
    for (const k of keys) expect(h[k]).toMatch(/^\/nl\//);
    expect(h["x-default"]).toBe("/nl/en/top/best-used-under-15k");
  });

  it("x-default moves to a country that has the list when NL has none", () => {
    const h = hreflangs("top/best-used-under-15k", exists(ROWS.map((r) => band(r.generation_id, 12000, "DE"))));
    for (const v of Object.values(h)) expect(v).toMatch(/^\/de\//);
    expect(h["x-default"]).toBe("/de/en/top/best-used-under-15k");
  });

  it("no filter: every served pair (other pages unchanged)", () => {
    expect(Object.keys(hreflangs("top")).length).toBeGreaterThan(5);
  });
});
