import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import type { UsedPriceBand } from "@ev/schema";
import { loadRules, OUT_FILE, serialize } from "../../scripts/shortlist-rules.mjs";
import type { ExploreRow } from "./explore-data";
import {
  ageRange,
  isComplete,
  presetCheck,
  presetsFor,
  priceFit,
  rankHero,
  reasons,
  resolveProfile,
  RULES,
  scoreContext,
  scoreRow,
  type Answers,
} from "./shortlist";
import { defaultFilters } from "./state";

const here = path.dirname(fileURLToPath(import.meta.url));

function row(id: string, o: Partial<ExploreRow> = {}): ExploreRow {
  return {
    variant_id: id,
    variant_name: id,
    generation_id: `${id}-gen`,
    generation_name: "gen",
    model_id: o.model_id ?? `${id}-model`,
    model_name: id,
    make_id: "make",
    make_name: "Make",
    year_start: 2022,
    era: "2021-22",
    body: "hatchback",
    quality_tier: "sourced",
    provenance: {},
    ...o,
  } as ExploreRow;
}

const A = (o: Partial<Answers>): Answers => ({ role: null, trips: null, charge: null, area: null, keep8: false, ...o });
const roadTripper = resolveProfile(A({ role: "only", trips: "monthly", charge: "home", area: "town" }))!;

describe("generated rules", () => {
  it("is in step with data/editorial/shortlist_rules.yaml", () => {
    expect(readFileSync(OUT_FILE, "utf8")).toBe(serialize(loadRules()));
  });
  it("never carries sheet values or evidence (Decision 038)", () => {
    const raw = readFileSync(path.resolve(here, "../config/shortlist-rules.generated.json"), "utf8");
    expect(raw).not.toMatch(/sheet_value|sheet_field|evidence/);
  });
});

describe("picker → profile (Decision 050)", () => {
  it("needs a role, and long trips unless it is a second car", () => {
    expect(isComplete(A({ role: "main" }))).toBe(false);
    expect(isComplete(A({ role: "second" }))).toBe(true);
  });
  it("maps answers onto the four profiles, the kerbside layer and the modifier", () => {
    expect(roadTripper.base.id).toBe("road-tripper");
    expect(resolveProfile(A({ role: "main", trips: "never" }))!.base.id).toBe("daily-driver");
    expect(resolveProfile(A({ role: "second" }))!.base.id).toBe("runabout");
    const kerb = resolveProfile(A({ role: "only", trips: "often", charge: "public_only", area: "city" }))!;
    expect(kerb.layer?.id).toBe("kerbside-charger");
    expect(kerb.modifier?.id).toBe("urban");
    expect(resolveProfile(A({ role: "second", keep8: true }))!.addons.map((a) => a.id)).toEqual(["keep-8-years"]);
  });
  it("merges presets, the stricter one wins", () => {
    const kerb = resolveProfile(A({ role: "only", trips: "often", charge: "work" }))!;
    const dc = presetsFor(kerb).filter((p) => p.field === "dc_km_per_20min");
    expect(dc).toHaveLength(1);
    expect(dc[0]!.min).toBe(200);
    expect(presetsFor(kerb).some((p) => p.field === "ac_kw")).toBe(true);
  });
  it("an unknown value passes a preset as 'unknown', never 'fail'", () => {
    const p = { field: "boot_l" as const, min: 380, why: {} };
    expect(presetCheck(row("a"), p)).toBe("unknown");
    expect(presetCheck(row("a", { boot_l: 300 }), p)).toBe("fail");
  });
});

describe("scoring parity with data/editorial/backtest_rules.py (road-tripper)", () => {
  // Expected scores come from backtest_rules.score() on the same values (sheet units: DC in km/h,
  // efficiency in Wh/km), run on 2026-11-15. Unknown factors (one-pedal, V2L, V2H) are 0.5 in both.
  const cars: [string, Partial<ExploreRow>, number, string][] = [
    ["fast800", { dc_km_per_20min: 260, real_range_km: 430, boot_l: 520, consumption_kwh_100km: 18, ac_kw: 11, voltage_class_id: "800v" }, 62.9, "fallback"],
    ["mid400", { dc_km_per_20min: 160, real_range_km: 380, boot_l: 400, consumption_kwh_100km: 16.5, ac_kw: 11, voltage_class_id: "400v", charge_100_daily: true }, 39, "fallback"],
    ["unknownboot", { dc_km_per_20min: 200, real_range_km: 400, consumption_kwh_100km: 15, ac_kw: 22, voltage_class_id: "400v" }, 52.8, "shortlist"],
  ];
  const ctx = scoreContext([]);
  for (const [id, o, score, band] of cars) {
    it(`${id}: ${score} (${band})`, () => {
      const r = scoreRow(row(id, o), roadTripper, ctx);
      expect(r.score).toBe(score);
      expect(r.band).toBe(band);
      expect(r.ruledOut).toBeNull();
    });
  }
  it("a known value under a gate rules the car out; an unknown one never does", () => {
    expect(scoreRow(row("slow", { dc_km_per_20min: 90, real_range_km: 300 }), roadTripper, ctx).ruledOut?.id).toBe("dc-not-terrible");
    expect(scoreRow(row("blank"), roadTripper, ctx).ruledOut).toBeNull();
    expect(scoreRow(row("blank"), roadTripper, ctx).score).toBe(50);
  });
  it("rural gates use the rural minimum", () => {
    const daily = resolveProfile(A({ role: "main", trips: "never", area: "countryside" }))!;
    expect(scoreRow(row("r", { real_range_km: 220 }), daily, ctx).ruledOut?.id).toBe("winter-range-daily");
    const dailyTown = resolveProfile(A({ role: "main", trips: "never", area: "town" }))!;
    expect(scoreRow(row("r", { real_range_km: 220 }), dailyTown, ctx).ruledOut).toBeNull();
  });
  it("newest version +4, older version −6, heavy SUV −16 in the countryside", () => {
    const rows = [row("old", { model_id: "m", year_start: 2021 }), row("new", { model_id: "m", year_start: 2024 })];
    const c = scoreContext(rows);
    expect(scoreRow(rows[1]!, roadTripper, c).score).toBe(54);
    expect(scoreRow(rows[0]!, roadTripper, c).score).toBe(44);
    const rural = resolveProfile(A({ role: "only", trips: "often", area: "countryside" }))!;
    expect(scoreRow(row("big", { kerb_mass_kg: 2500 }), rural, ctx).adjustments).toEqual([{ id: "too-big-for-b-roads", points: -16 }]);
    const daily = resolveProfile(A({ role: "main", trips: "never", area: "countryside" }))!;
    expect(scoreRow(row("big", { kerb_mass_kg: 2500 }), daily, ctx).adjustments).toEqual([{ id: "too-big-for-b-roads", points: -8 }]);
  });
  it("reasons name the strongest known factors only", () => {
    const r = scoreRow(row("fast800", cars[0]![1]), roadTripper, ctx);
    expect(reasons(r).map((x) => x.id)).toEqual(["winter-range", "efficiency"]);
  });
});

describe("prices", () => {
  const band = (o: Partial<UsedPriceBand>): UsedPriceBand => ({
    generation_id: "u-gen",
    country: "NL",
    currency: "EUR",
    median: 20000,
    samples: 9,
    period: "2026-10",
    source_id: "src",
    ...o,
  });
  it("parses age bands", () => {
    expect(ageRange("3-5")).toEqual([3, 5]);
    expect(ageRange("8+")).toEqual([8, 30]);
    expect(ageRange(null)).toBeNull();
  });
  it("picks the youngest used band within budget and its build years", () => {
    const r = row("u", { year_start: 2018, year_end: null });
    const bands = { "u-gen": [band({ age_band_years: "1-2", median: 30000 }), band({ age_band_years: "3-5", median: 21000, p25: 19000, p75: 23000 })] };
    const { fit } = priceFit(r, { country: "NL", cond: "used", budget: 25000, usedBands: bands, nowYear: 2026 });
    expect(fit).toMatchObject({ kind: "used", amount: 21000, yearFrom: 2021, yearTo: 2023, low: 19000 });
  });
  it("over budget only when every known price is over; no price → not over", () => {
    const r = row("n", { on_sale_new: true, price_new: { NL: { amount: 45000, currency: "EUR" } } as ExploreRow["price_new"] });
    expect(priceFit(r, { country: "NL", cond: "any", budget: 30000, nowYear: 2026 })).toEqual({ fit: null, over: true });
    expect(priceFit(row("x"), { country: "NL", cond: "any", budget: 30000, nowYear: 2026 })).toEqual({ fit: null, over: false });
  });
});

describe("rankHero", () => {
  const rows: ExploreRow[] = [];
  for (let i = 0; i < 14; i++) {
    rows.push(row(`car${i}`, { dc_km_per_20min: 200 + i * 10, real_range_km: 350 + i * 10, boot_l: 400 }));
  }
  rows.push(row("car13b", { model_id: "car13-model", year_start: 2020, dc_km_per_20min: 200, real_range_km: 350, boot_l: 400 }));
  const q = { country: "NL" as const, cond: "any" as const, budget: null, filters: defaultFilters(), presetsOff: [], nowYear: 2026 };

  it("one card per model, top 10, best first", () => {
    const res = rankHero(rows, roadTripper, q);
    expect(res.picks).toHaveLength(10);
    expect(res.picks[0]!.row.variant_id).toBe("car13");
    expect(res.picks[0]!.alternatives).toBe(1);
    expect(new Set(res.picks.map((p) => p.row.model_id)).size).toBe(10);
  });
  it("presets are hard filters on known values; removing one brings cars back", () => {
    const withPresets = rankHero(rows, roadTripper, q).qualifying;
    const off = rankHero(rows, roadTripper, { ...q, presetsOff: ["dc_km_per_20min", "real_range_km"] }).qualifying;
    const strict = rankHero(rows, roadTripper, { ...q, filters: { ...defaultFilters(), rangeMin: 420 } }).qualifying;
    expect(off).toBe(withPresets);
    expect(strict).toBeLessThan(withPresets);
  });
  it("budget re-ranks: cars with a known price over budget drop out", () => {
    const priced = rows.map((r, i) => ({ ...r, on_sale_new: true, price_new: { NL: { amount: 20000 + i * 3000, currency: "EUR" } } }) as ExploreRow);
    const all = rankHero(priced, roadTripper, q);
    const cheap = rankHero(priced, roadTripper, { ...q, budget: 40000 });
    expect(cheap.picks[0]!.row.variant_id).not.toBe(all.picks[0]!.row.variant_id);
    expect(cheap.picks.every((p) => (p.price?.amount ?? 0) <= 40000)).toBe(true);
  });
  it("uses the real rules file", () => {
    expect(RULES.profiles.map((p) => p.id)).toEqual(["road-tripper", "daily-driver", "runabout", "kerbside-charger"]);
  });
});

describe("per-variant used bands by build year (T-081)", async () => {
  const { variantFit } = await import("./shortlist");
  const { parseVariantUsedPrices } = await import("./variant-prices");
  const { compactBands } = await import("./explore-data");
  const doc = {
    variants: [
      {
        variant_id: "v",
        bands: {
          NL: [
            { build_year: 2021, p25: 17000, median: 19000, p75: 21000, currency: "EUR", samples: 0, method: "model", estimate: true, confidence: "medium" },
            { build_year: 2023, p25: 24000, median: 26000, p75: 28000, currency: "EUR", samples: 0, method: "model", estimate: true, confidence: "low" },
            { build_year: 2022, p25: 20000, median: 22000, p75: 24000, currency: "EUR", samples: 0, method: "model", estimate: true, confidence: "medium" },
            { build_year: "x", median: 1 },
          ],
          xx: [{ build_year: 2022, median: 5 }],
        },
      },
    ],
  };
  const r = row("v", { year_start: 2021, year_end: 2023, used_bands: compactBands(parseVariantUsedPrices(doc).get("v")) });
  it("parses, sorts by year and drops bad rows and keys", () => {
    expect(r.used_bands).toEqual({ NL: [[2021, 17000, 19000, 21000, 1], [2022, 20000, 22000, 24000, 1], [2023, 24000, 26000, 28000, 3]] });
  });
  it("the newest build year within budget sets the price; the years that fit are listed", () => {
    expect(variantFit(r, "NL", 23000)).toMatchObject({ amount: 22000, low: 20000, high: 24000, yearFrom: 2021, yearTo: 2022, estimate: true, lowConfidence: false });
    expect(variantFit(r, "NL", null)).toMatchObject({ amount: 26000, yearFrom: 2023, yearTo: 2023, lowConfidence: true });
    expect(variantFit(r, "NL", 10000)).toBeNull();
    expect(variantFit(r, "DE", 30000)).toBeNull();
  });
  it("priceFit: over budget when the car has bands but none fit", () => {
    expect(priceFit(r, { country: "NL", cond: "used", budget: 10000, nowYear: 2026 })).toEqual({ fit: null, over: true });
    expect(priceFit(r, { country: "NL", cond: "used", budget: 23000, nowYear: 2026 }).fit?.amount).toBe(22000);
  });
});
