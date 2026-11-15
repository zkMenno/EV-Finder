import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import type { PublishedVariant, UsedPriceBand } from "@ev/schema";
import { afterEach, describe, expect, it } from "vitest";
import fixture from "@/fixtures/catalogue.sample.json";
import { getCatalogue } from "./catalogue";
import { sitemapUrls } from "./sitemap";
import { isUsedPriceBand, USED_MIN_ENTRIES, usedBandFor, usedRanking, visibleUsedRankings } from "./used-rankings";

// Five fixture generations with a range each (FIXTURE values, not real data).
const gen = (i: number, range: number, extra: Partial<PublishedVariant> = {}): PublishedVariant =>
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
    provenance: { real_range_km: { source_ids: ["fixture"], confidence: "medium" } },
    ...extra,
  }) as PublishedVariant;
const ROWS = [gen(1, 200), gen(2, 250), gen(3, 300), gen(4, 350), gen(5, 400), gen(6, 380)];
// Schema shape (`UsedPriceBand`, packages/schema): median = typical price, p25/p75 = the band.
const band = (g: string, median: number, over: Partial<UsedPriceBand> = {}): UsedPriceBand => ({
  generation_id: g,
  country: "NL",
  currency: "EUR",
  p25: Math.round(median * 0.9),
  median,
  p75: Math.round(median * 1.1),
  samples: 12,
  period: "2026-10",
  age_band_years: null,
  source_id: "fixture-prices",
  fact_ids: [],
  ...over,
});

describe("best used EV under €15k / 20k / 25k", () => {
  it("hidden with fewer than 5 sourced prices, shown from 5 on", () => {
    const four = [band("g1", 9000), band("g2", 11000), band("g3", 12000), band("g4", 14000)];
    expect(visibleUsedRankings(ROWS, four, "NL", "EUR")).toEqual([]);
    const five = [...four, band("g5", 14500)];
    expect(usedRanking("best-used-under-15k", ROWS, five, "NL", "EUR")).toHaveLength(USED_MIN_ENTRIES);
    expect(visibleUsedRankings(ROWS, five, "NL", "EUR")).toEqual(["best-used-under-15k", "best-used-under-20k", "best-used-under-25k"]);
    // Another country has no prices: nothing there.
    expect(visibleUsedRankings(ROWS, five, "DE", "EUR")).toEqual([]);
  });

  it("only sourced bands with ≥ 5 samples under the cap count; ranked by km per 1,000", () => {
    const bands = [
      band("g1", 10000), // 20 km per 1k
      band("g2", 10000, { samples: 4 }), // too few samples
      band("g3", 10000, { source_id: "" }), // no source
      band("g4", 16000), // over the 15k cap
      band("g5", 10000), // 40 km per 1k
    ];
    const list = usedRanking("best-used-under-15k", ROWS, bands, "NL", "EUR");
    expect(list.map((e) => [e.row.generation_id, e.value, e.rank])).toEqual([
      ["g5", 40, 1],
      ["g1", 20, 2],
    ]);
    expect(usedRanking("best-used-under-20k", ROWS, bands, "NL", "EUR").map((e) => e.row.generation_id)).toEqual(["g5", "g4", "g1"]);
  });

  it("uses the generation's median-range variant, never the best one", () => {
    const rows = [gen(1, 200), gen(1, 300, { variant_id: "v1b" }), gen(1, 400, { variant_id: "v1c" })];
    expect(usedRanking("best-used-under-15k", rows, [band("g1", 10000)], "NL", "EUR")[0]?.rangeKm).toBe(300);
  });

  it("validates bands read from catalogue.json", () => {
    expect(isUsedPriceBand(band("g1", 1000))).toBe(true);
    expect(isUsedPriceBand({ ...band("g1", 1000), median: "1000" })).toBe(false);
    expect(isUsedPriceBand({ ...band("g1", 1000), currency: "USD" })).toBe(false);
    expect(isUsedPriceBand({ ...band("g1", 1000), p25: -1 })).toBe(false);
    expect(isUsedPriceBand({ ...band("g1", 1000), samples: 5.5 })).toBe(false);
    // The old web-only shape (typical/low/high, Q-085) no longer passes.
    expect(isUsedPriceBand({ generation_id: "g1", country: "NL", currency: "EUR", typical: 1000, samples: 12, source_ids: ["x"], retrieved_at: "2026-11-01" })).toBe(false);
  });

  it("one band per generation and country, in the market's currency, ≥ 5 samples", () => {
    const bands = [band("g1", 9000, { samples: 4 }), band("g1", 9500, { country: "UK", currency: "GBP" }), band("g1", 10000)];
    expect(usedBandFor(bands, "g1", "NL", "EUR")?.median).toBe(10000);
    expect(usedBandFor(bands, "g1", "UK", "GBP")?.median).toBe(9500);
    expect(usedBandFor(bands, "g1", "UK", "EUR")).toBeUndefined();
    expect(usedBandFor(bands, "g1", "DE", "EUR")).toBeUndefined();
  });

  it("a GBP band never counts on an EUR market", () => {
    const five = ["g1", "g2", "g3", "g4", "g5"].map((g) => band(g, 9000, { currency: "GBP" }));
    expect(visibleUsedRankings(ROWS, five, "NL", "EUR")).toEqual([]);
  });
});

describe("release → pages: lists appear once ≥ 5 priced generations exist", () => {
  const prev = process.env.CATALOGUE_DIR;
  afterEach(() => {
    if (prev === undefined) delete process.env.CATALOGUE_DIR;
    else process.env.CATALOGUE_DIR = prev;
  });
  const release = (extra: object) => {
    const dir = mkdtempSync(path.join(tmpdir(), "ev-used-"));
    mkdirSync(path.join(dir, "9"));
    writeFileSync(path.join(dir, "9", "catalogue.json"), JSON.stringify({ ...fixture, release: 9, ...extra }));
    writeFileSync(path.join(dir, "latest"), "9\n");
    return dir;
  };

  it("no used_prices (release 1 today): no list, nothing in the sitemap", () => {
    process.env.CATALOGUE_DIR = release({});
    const cat = getCatalogue();
    expect(cat.usedPrices()).toEqual([]);
    expect(sitemapUrls(cat, "https://x.test").some((u) => u.includes("best-used"))).toBe(false);
  });

  it("five priced generations in NL: lists and sitemap entries for NL only", () => {
    const rows = (fixture as unknown as { rows: PublishedVariant[] }).rows.filter((r) => typeof r.real_range_km === "number");
    const gens = [...new Set(rows.map((r) => r.generation_id))].slice(0, 5);
    expect(gens).toHaveLength(5);
    process.env.CATALOGUE_DIR = release({ used_prices: [...gens.map((g, i) => band(g, 9000 + i * 500)), { junk: true }] });
    const cat = getCatalogue();
    expect(cat.usedPrices()).toHaveLength(5);
    expect(visibleUsedRankings(cat.rows(), cat.usedPrices(), "NL", "EUR")).toContain("best-used-under-15k");
    const urls = sitemapUrls(cat, "https://x.test");
    expect(urls).toContain("https://x.test/nl/nl/top/best-used-under-15k");
    expect(urls.some((u) => u.startsWith("https://x.test/de/") && u.includes("best-used"))).toBe(false);
  });
});
