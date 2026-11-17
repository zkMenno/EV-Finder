import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import type { PublishedVariant, ShortlistBand, UsedPriceBand } from "@ev/schema";
import fixtureCatalogue from "../fixtures/catalogue.sample.json";
import fixtureScores from "../fixtures/shortlist-scores.sample.json";
import { loadRules, OUT_FILE, serialize } from "../../scripts/shortlist-rules.mjs";
import { toExploreRow, type ExploreRow } from "./explore-data";
import { parseShortlistScores } from "./release-scores";
import {
  ageRange,
  comboKey,
  isComplete,
  presetCheck,
  presetsFor,
  priceFit,
  rankHero,
  reasons,
  resolveProfile,
  PRESET_FIELDS,
  RULES,
  scoreFor,
  suggestedScore,
  type Answers,
  type ResolvedProfile,
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

// ── Release scores (T-114, Decision 065) ─────────────────────────────────────────────────────
// The fixture is the pipeline's own output (pipeline/ev_pipeline/derive/shortlist.py, T-069) for
// the dev fixture rows; see its `note`. The web must show exactly these scores, never its own.
const fixtureCat = fixtureCatalogue as unknown as { rows: PublishedVariant[] };
const releaseScores = parseShortlistScores(fixtureScores)!;
const fixtureRows = fixtureCat.rows.map((r) => toExploreRow(r, undefined, releaseScores));

/** A row carrying a release score for one combination. */
function scored(r: ExploreRow, combo: string, score: number, band: ShortlistBand = "shortlist", reasonCodes: string[] = []): ExploreRow {
  return { ...r, shortlist: { s: { ...(r.shortlist?.s ?? {}), [combo]: [score, band, ...reasonCodes] } } };
}

/** Every complete answer set → its profile. */
const ALL_PROFILES: ResolvedProfile[] = [];
for (const role of ["only", "main", "second"] as const)
  for (const trips of [null, "never", "few_a_year", "monthly", "often"] as const)
    for (const charge of ["home", "work", "public_only"] as const)
      for (const area of [null, "city", "town", "countryside"] as const) {
        const rp = resolveProfile(A({ role, trips, charge, area }));
        if (rp) ALL_PROFILES.push(rp);
      }

describe("release scores (Decision 065)", () => {
  it("every picker answer set maps onto a combination the pipeline ships", () => {
    const combos = new Set((fixtureScores as { combos: string[] }).combos);
    expect(ALL_PROFILES.length).toBeGreaterThan(20);
    for (const rp of ALL_PROFILES) expect(combos.has(comboKey(rp)), comboKey(rp)).toBe(true);
    expect(comboKey(roadTripper)).toBe("road-tripper");
    expect(comboKey(resolveProfile(A({ role: "only", trips: "often", charge: "public_only", area: "countryside" }))!)).toBe("road-tripper+kerbside.rural");
    expect(comboKey(resolveProfile(A({ role: "second", charge: "home", area: "city" }))!)).toBe("runabout.urban");
  });
  it("parses the pipeline's file and skips malformed entries", () => {
    expect(releaseScores.variants.size).toBe(fixtureCat.rows.length);
    expect(parseShortlistScores(null)).toBeNull();
    expect(parseShortlistScores({ variants: "x" })).toBeNull();
    const p = parseShortlistScores({ release: 2, generated_at: "t", variants: [
      { variant_id: "a", scores: { "road-tripper": { score: 70, band: "shortlist", reasons: ["+dc-speed", 3] }, bad: { score: "x", band: "shortlist" }, odd: { score: 1, band: "great" } } },
      { variant_id: "b", scores: {} },
      { scores: { "road-tripper": { score: 1, band: "fallback" } } },
    ] })!;
    expect([...p.variants.keys()]).toEqual(["a"]);
    expect(p.variants.get("a")!.scores).toEqual({ "road-tripper": { score: 70, band: "shortlist", reasons: ["+dc-speed"] } });
  });
  it("shows exactly the release score, band and reasons for every variant and profile", () => {
    for (const rp of ALL_PROFILES) {
      for (const r of fixtureRows) {
        const want = releaseScores.variants.get(r.variant_id)!.scores[comboKey(rp)]!;
        const got = scoreFor(r, rp)!;
        expect(got.score).toBe(want.score);
        expect(got.band).toBe(want.band);
        expect(got.reasons).toEqual(want.reasons);
      }
    }
  });
  it("the hero order is the release order: best score per model, ruled-out cars never shown", () => {
    const q = { country: "NL" as const, cond: "any" as const, budget: null, filters: defaultFilters(), presetsOff: [...PRESET_FIELDS], nowYear: 2026 };
    for (const rp of ALL_PROFILES) {
      const res = rankHero(fixtureRows, rp, q, { hasScores: true });
      const best = new Map<string, number>();
      for (const r of fixtureRows) {
        const s = releaseScores.variants.get(r.variant_id)!.scores[comboKey(rp)]!;
        if (s.band === "ruled-out") continue;
        best.set(r.model_id, Math.max(best.get(r.model_id) ?? -1, s.score));
      }
      const want = [...best.values()].sort((x, y) => y - x).slice(0, 10);
      expect(res.status).toBe("ranked");
      expect(res.picks.map((p) => p.result.score), comboKey(rp)).toEqual(want);
      expect(res.picks.every((p) => p.result.band !== "ruled-out")).toBe(true);
    }
  });
  it("no scores file → 'ranking not available', never a ranking on another basis", () => {
    const res = rankHero(fixtureRows, roadTripper, { country: "NL", cond: "any", budget: null, filters: defaultFilters(), presetsOff: [], nowYear: 2026 }, { hasScores: false });
    expect(res).toMatchObject({ status: "no-scores", picks: [], qualifying: 0 });
  });
  it("a car the release didn't score for this profile is not ranked (counted as unscored)", () => {
    const rows = [scored(row("a"), "road-tripper", 60), row("b"), scored(row("c"), "runabout", 90)];
    const res = rankHero(rows, roadTripper, { country: "NL", cond: "any", budget: null, filters: defaultFilters(), presetsOff: [], nowYear: 2026 }, { hasScores: true });
    expect(res.picks.map((p) => p.row.variant_id)).toEqual(["a"]);
    expect(res.unscored).toBe(2);
  });
  it("reason line codes come from the release: plus factors first, bonuses as adjustments", () => {
    const r = scored(row("a"), "road-tripper", 71.2, "shortlist", ["+dc-speed", "+winter-range", "+space", "-efficiency", "bonus:newest-version"]);
    const s = scoreFor(r, roadTripper)!;
    expect(reasons(s).map((x) => x.id)).toEqual(["dc-speed", "winter-range"]);
    expect(s.adjustments).toEqual([{ id: "newest-version", points: 4 }]);
  });
  it("Nerd factors: release 0..1 values with rule weights; unknown stays null", () => {
    const vid = fixtureRows.find((r) => releaseScores.variants.get(r.variant_id)!.unknown["road-tripper"]?.includes("one-pedal"))!;
    const s = scoreFor(vid, roadTripper)!;
    expect(s.factors.map((f) => f.id)).toEqual(roadTripper.base.factors.map((f) => f.id));
    expect(s.factors.find((f) => f.id === "one-pedal")!.score).toBeNull();
    const dc = releaseScores.variants.get(vid.variant_id)!.factors["road-tripper"]!["dc-speed"];
    expect(s.factors.find((f) => f.id === "dc-speed")!.score).toBe(dc);
    expect(s.derived).toEqual(releaseScores.variants.get(vid.variant_id)!.derived);
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
    rows.push(scored(row(`car${i}`, { dc_km_per_20min: 200 + i * 10, real_range_km: 350 + i * 10, boot_l: 400 }), "road-tripper", 40 + i));
  }
  rows.push(scored(row("car13b", { model_id: "car13-model", year_start: 2020, dc_km_per_20min: 200, real_range_km: 350, boot_l: 400 }), "road-tripper", 41));
  const q = { country: "NL" as const, cond: "any" as const, budget: null, filters: defaultFilters(), presetsOff: [], nowYear: 2026 };
  const on = { hasScores: true };

  it("one card per model, top 10, best first", () => {
    const res = rankHero(rows, roadTripper, q, on);
    expect(res.picks).toHaveLength(10);
    expect(res.picks[0]!.row.variant_id).toBe("car13");
    expect(res.picks[0]!.alternatives).toBe(1);
    expect(new Set(res.picks.map((p) => p.row.model_id)).size).toBe(10);
  });
  it("presets are hard filters on known values; removing one brings cars back", () => {
    const withPresets = rankHero(rows, roadTripper, q, on).qualifying;
    const off = rankHero(rows, roadTripper, { ...q, presetsOff: ["dc_km_per_20min", "real_range_km"] }, on).qualifying;
    const strict = rankHero(rows, roadTripper, { ...q, filters: { ...defaultFilters(), rangeMin: 420 } }, on).qualifying;
    expect(off).toBe(withPresets);
    expect(strict).toBeLessThan(withPresets);
  });
  it("budget re-ranks: cars with a known price over budget drop out", () => {
    const priced = rows.map((r, i) => ({ ...r, on_sale_new: true, price_new: { NL: { amount: 20000 + i * 3000, currency: "EUR" } } }) as ExploreRow);
    const all = rankHero(priced, roadTripper, q, on);
    const cheap = rankHero(priced, roadTripper, { ...q, budget: 40000 }, on);
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
    // The visitor's build-year filter narrows the years a price may come from.
    expect(variantFit(r, "NL", 30000, { from: 2021, to: 2021 })).toMatchObject({ amount: 19000, yearFrom: 2021, yearTo: 2021 });
  });
  it("priceFit: over budget when the car has bands but none fit", () => {
    expect(priceFit(r, { country: "NL", cond: "used", budget: 10000, nowYear: 2026 })).toEqual({ fit: null, over: true });
    expect(priceFit(r, { country: "NL", cond: "used", budget: 23000, nowYear: 2026 }).fit?.amount).toBe(22000);
  });
});

describe("Explore 'Suggested' sort (T-067)", async () => {
  const { sortRows } = await import("./filters");
  const { topFactors } = await import("@/components/SuggestedSort");
  it("orders by score, ruled-out cars last, and the URL key round-trips", async () => {
    const { fromSearchParams, toSearchParams, defaultState } = await import("./state");
    const rows = [
      scored(row("slow"), "road-tripper", 0, "ruled-out", ["gate:dc-not-terrible"]),
      scored(row("good"), "road-tripper", 72),
      scored(row("ok"), "road-tripper", 55, "consider"),
      row("unscored"),
    ];
    const score = (r: ExploreRow) => suggestedScore(r, roadTripper);
    expect(sortRows(rows, "suggested", "desc", "NL", score).map((r) => r.variant_id)).toEqual(["good", "ok", "slow", "unscored"]);
    const st = { ...defaultState(), sort: "suggested" as const, dir: "desc" as const };
    expect(fromSearchParams(toSearchParams(st)).sort).toBe("suggested");
  });
  it("names the heaviest factors after the layer's and modifier's weight steps", () => {
    expect(topFactors(roadTripper)).toEqual(["dc-speed", "winter-range", "space"]);
    const kerb = resolveProfile(A({ role: "main", trips: "never", charge: "public_only" }))!;
    expect(topFactors(kerb)[0]).toBe("efficiency");
  });
});
