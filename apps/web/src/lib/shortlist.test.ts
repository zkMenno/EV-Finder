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
  type UsedBands,
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
      // Without prices, the order is the release order alone (prices come first otherwise: T-115).
      const unpriced = fixtureRows.map((r) => ({ ...r, price_new: undefined, on_sale_new: undefined, used_bands: undefined }) as ExploreRow);
      const res = rankHero(unpriced, rp, q, { hasScores: true });
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
  it("Nerd values are the car's own figures (T-097), on the basis the release scored (T-114)", () => {
    const vid = fixtureRows.find((r) => typeof r.dc_km_per_20min === "number" && releaseScores.variants.get(r.variant_id)!.derived.winter_range_km)!;
    const s = scoreFor(vid, roadTripper)!;
    const f = (id: string) => s.factors.find((x) => x.id === id)!;
    // DC: the row's own km per 20 min, not ×3 km/h and not the basis-scaled value.
    expect(f("dc-speed")).toMatchObject({ field: "dc_km_per_20min", raw: vid.dc_km_per_20min });
    // Winter range and efficiency: the release's derived estimates the score was built on.
    expect(f("winter-range")).toMatchObject({ field: "winter_range_km", raw: s.derived.winter_range_km });
    expect(f("efficiency").field).toBe("real_wh_km");
    expect(f("efficiency").raw).toBe(s.derived.real_wh_km ?? null);
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
  it("over budget only when every known price is over; no price at all → unpriced, not over", () => {
    const r = row("n", { on_sale_new: true, price_new: { NL: { amount: 45000, currency: "EUR" } } as ExploreRow["price_new"] });
    expect(priceFit(r, { country: "NL", cond: "any", budget: 30000, nowYear: 2026 })).toEqual({ fit: null, status: "over" });
    expect(priceFit(row("x"), { country: "NL", cond: "any", budget: 30000, nowYear: 2026 })).toEqual({ fit: null, status: "unpriced" });
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
    expect(priceFit(r, { country: "NL", cond: "used", budget: 10000, nowYear: 2026 })).toEqual({ fit: null, status: "over" });
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

// ── Budget rule (T-115, Decision 064): band → estimate → new price → none ─────────────────────
describe("budget rule (Decision 064)", async () => {
  const { parseVariantUsedPrices } = await import("./variant-prices");
  const { compactBands } = await import("./explore-data");
  // Shapes as main's pipeline writes them (pipeline/ev_pipeline/derive/used_price.py, #64; schema UsedPriceYearBand).
  const FITTED_SOURCE = { name: "Depreciation curve fitted on our own used price samples (T-113)", ref: "pipeline/ev_pipeline/derive/used_price_params.yaml#fitted" };
  const model = (y: number, median: number, extra: Record<string, unknown> = {}) => ({
    build_year: y, p25: median - 2000, median, p75: median + 2000, currency: "EUR", samples: 0, method: "model", basis: "estimate", estimate: true,
    curve: "fitted", curve_fitted_on: ["BE", "NL"], source: FITTED_SOURCE, date: "2026-11-17",
    age_years: 2026 - y, kept_share: 0.55, list_price: Math.round(median / 0.55), list_basis: "year", list_source_ids: ["rdw-catalogusprijs"], confidence: "medium", ...extra,
  });
  const samples = (y: number, median: number, scope: "variant" | "generation" = "variant") => ({
    build_year: y, p25: median - 1500, median, p75: median + 1500, currency: "EUR", samples: 7, method: "samples", basis: "band", scope, estimate: false,
    date: "2026-11-01", observed_at: "2026-11-01", source: { name: "Manual sample (AutoScout24 search)", url: "https://example.org" }, source_id: "manual-autoscout24", confidence: "medium",
  });
  const withBands = (id: string, bands: object[], o: Partial<ExploreRow> = {}) =>
    row(id, { year_start: 2020, year_end: 2024, used_bands: compactBands(parseVariantUsedPrices({ variants: [{ variant_id: id, bands: { NL: bands } }] }).get(id)), ...o });
  const opts = (budget: number | null, cond: "any" | "new" | "used" = "any") => ({ country: "NL" as const, cond, budget, nowYear: 2026 });

  it("(1) a real used band for those build years: basis 'band', with its source", () => {
    const r = withBands("s", [samples(2021, 18000), model(2023, 26000)]);
    const { fit, status } = priceFit(r, opts(20000));
    expect(status).toBe("fits");
    expect(fit).toMatchObject({ kind: "used", basis: "band", scope: "variant", amount: 18000, yearFrom: 2021, yearTo: 2021, how: { src: "Manual sample (AutoScout24 search)", url: "https://example.org", date: "2026-11-01", n: 7 } });
  });
  it("(1) the generation's sourced band counts as a real band", () => {
    const r = row("g", { year_start: 2019, year_end: null });
    const bands = { "g-gen": [{ generation_id: "g-gen", country: "NL", currency: "EUR", median: 21000, p25: 19000, p75: 23000, samples: 9, period: "2026-10", source_id: "src-a", age_band_years: "3-5" }] } as UsedBands;
    expect(priceFit(r, { ...opts(25000), usedBands: bands }).fit).toMatchObject({ basis: "band", scope: "generation", amount: 21000, sourceIds: ["src-a"] });
  });
  it("(1) beats (2): a real band that fits wins over an estimate that fits", () => {
    const r = withBands("p", [samples(2021, 19000), model(2022, 18000)]);
    expect(priceFit(r, opts(20000)).fit).toMatchObject({ basis: "band", amount: 19000 });
  });
  it("(2) no real band: our used price estimate, labelled, with list price, kept share and source", () => {
    const r = withBands("e", [model(2021, 17000), model(2022, 21000), model(2023, 26000)]);
    const { fit, status } = priceFit(r, opts(22000));
    expect(status).toBe("fits");
    expect(fit).toMatchObject({ kind: "used", basis: "estimate", estimate: true, amount: 21000, yearFrom: 2021, yearTo: 2022 });
    expect(fit!.how).toEqual({ src: FITTED_SOURCE.name, ref: FITTED_SOURCE.ref, date: "2026-11-17", curve: "fitted", on: ["BE", "NL"], list: Math.round(21000 / 0.55), ls: ["rdw-catalogusprijs"], kept: 0.55 });
  });
  it("(3) the new price, for a car on sale new; 'new' condition uses only that", () => {
    const r = row("n", { on_sale_new: true, price_new: { NL: { amount: 33000, currency: "EUR" } } as ExploreRow["price_new"] });
    expect(priceFit(r, opts(35000)).fit).toMatchObject({ kind: "new", basis: "new", amount: 33000 });
    expect(priceFit(r, opts(30000))).toEqual({ fit: null, status: "over" });
    const both = withBands("nb", [model(2023, 24000)], { on_sale_new: true, price_new: { NL: { amount: 33000, currency: "EUR" } } as ExploreRow["price_new"] });
    expect(priceFit(both, opts(35000, "new")).fit).toMatchObject({ basis: "new", amount: 33000 });
    expect(priceFit(both, opts(35000, "any")).fit).toMatchObject({ basis: "estimate", amount: 24000 });
    expect(priceFit(both, opts(35000, "used")).fit).toMatchObject({ basis: "estimate" });
  });
  it("none: no band, no estimate, no new price → 'unpriced' (budget or not)", () => {
    expect(priceFit(row("x"), opts(15000))).toEqual({ fit: null, status: "unpriced" });
    expect(priceFit(row("x"), opts(null))).toEqual({ fit: null, status: "unpriced" });
    // A car only sold used has no new price to fall back on.
    const old = row("o", { on_sale_new: false, price_new: { NL: { amount: 30000, currency: "EUR" } } as ExploreRow["price_new"] });
    expect(priceFit(old, opts(35000)).status).toBe("unpriced");
  });
  it("over: every price the car has is above the budget", () => {
    const r = withBands("ov", [samples(2022, 28000), model(2023, 31000)]);
    expect(priceFit(r, opts(20000))).toEqual({ fit: null, status: "over" });
  });

  it("reads basis and scope, not only method/estimate: a generation band stands in as a real band", () => {
    const r = withBands("gs", [samples(2021, 18000, "generation"), model(2022, 21000)]);
    expect(priceFit(r, opts(20000)).fit).toMatchObject({ basis: "band", scope: "generation", estimate: false, amount: 18000 });
    // basis wins over a stale method/estimate pair.
    const odd = withBands("odd", [{ ...model(2022, 19000), basis: "band", method: "model" }]);
    expect(priceFit(odd, opts(20000)).fit).toMatchObject({ basis: "band" });
  });
  it("an estimate never stands in for a build year that has a real band (same year over budget → that year is over)", () => {
    const r = withBands("sy", [samples(2022, 26000), model(2022, 19000)]);
    expect(priceFit(r, opts(20000))).toEqual({ fit: null, status: "over" });
  });

  describe("Nerd price text is built from the row's own fields (Decision 064)", async () => {
    const { priceHowText } = await import("./price-how");
    const en = (await import("@/i18n/en.json")).default as Record<string, string>;
    const t = ((k: string, v: Record<string, string | number> = {}) => (en[k] ?? k).replace(/\{(\w+)\}/g, (_, x) => String(v[x] ?? `{${x}}`))) as never;
    const money = (n: number) => `€${n}`;
    const names = { "rdw-catalogusprijs": "RDW list prices" };
    const fitOf = (bands: object[], budget = 40000) => priceFit(withBands("h", bands), opts(budget)).fit!;
    it("fitted estimate: curve, countries, source and date from the row, list price source by name; no fixed R-40 citation", () => {
      const s = priceHowText(fitOf([model(2022, 21000)]), t, "en-GB", money, names)!;
      expect(s).toContain("fitted on our own used price samples from Belgium, Netherlands");
      expect(s).toContain(`Curve: ${FITTED_SOURCE.name} (2026-11-17)`);
      expect(s).toContain("RDW list prices");
      expect(s).toContain("55 %");
      expect(s).not.toMatch(/R-40/);
    });
    it("segment curve and published curve read differently", () => {
      expect(priceHowText(fitOf([model(2022, 21000, { curve: "fitted:J-medium" })]), t, "en-GB", money, names)).toContain("segment J-medium");
      const pub = priceHowText(fitOf([model(2022, 21000, { curve: "published", curve_fitted_on: undefined, source: { name: "DAT residual values (via autohaus.de)" }, date: "2026-09-28" })]), t, "en-GB", money, names)!;
      expect(pub).toContain("a published depreciation curve");
      expect(pub).toContain("DAT residual values (via autohaus.de) (2026-09-28)");
      expect(pub).not.toContain("fitted");
    });
    it("bands: variant scope names the version, generation scope says typical for this generation", () => {
      expect(priceHowText(fitOf([samples(2021, 18000)]), t, "en-GB", money, names)).toBe("Used price band from 7 counted listings of this version (2026-11-01). Source: Manual sample (AutoScout24 search).");
      expect(priceHowText(fitOf([samples(2021, 18000, "generation")]), t, "en-GB", money, names)).toBe("Used price band from 7 counted listings of all versions of this generation (2026-11-01). Source: Manual sample (AutoScout24 search).");
      // The card itself labels it at every level (Decision 069).
      expect(en["hero.card.generationBand"]).toMatch(/^Typical for this generation/);
    });
  });

  describe("ranking", () => {
    const q = (budget: number | null) => ({ country: "NL" as const, cond: "any" as const, budget, filters: defaultFilters(), presetsOff: [...PRESET_FIELDS], nowYear: 2026 });
    const on = { hasScores: true };
    // Unpriced cars score highest on purpose: they must still never reach the top 5.
    const rows: ExploreRow[] = [];
    for (let i = 0; i < 6; i++) rows.push(scored(row(`free${i}`), "road-tripper", 95 - i));
    for (let i = 0; i < 8; i++) rows.push(scored(withBands(`cheap${i}`, [model(2021, 12000 + i * 500)]), "road-tripper", 40 + i));
    for (let i = 0; i < 8; i++) rows.push(scored(withBands(`dear${i}`, [model(2023, 30000 + i * 500)]), "road-tripper", 60 + i));

    it("a car with no price is never in the top 5 and comes after every priced car", () => {
      for (const budget of [null, 15000, 35000]) {
        const res = rankHero(rows, roadTripper, q(budget), on);
        expect(res.shortlistN).toBe(5);
        const firstUnpriced = res.picks.findIndex((p) => p.price === null);
        if (firstUnpriced >= 0) {
          expect(firstUnpriced).toBeGreaterThanOrEqual(5);
          expect(res.picks.slice(firstUnpriced).every((p) => p.price === null)).toBe(true);
        }
        expect(res.picks.slice(0, 5).every((p) => p.price !== null)).toBe(true);
      }
    });
    it("fewer than five priced cars: the shortlist is shorter, never filled with unpriced cars", () => {
      const res = rankHero([...rows.slice(0, 6), ...rows.slice(6, 8)], roadTripper, q(15000), on);
      expect(res.shortlistN).toBe(2);
      expect(res.picks.slice(0, 2).every((p) => p.price !== null)).toBe(true);
    });
    it("release-2 shape (NL road-tripper €15k): 1 priced car + 8 higher-scoring unpriced → 1 ranked pick, then at most 3 unranked (A-35 B2, T-152)", () => {
      // Release 2 had Dacia Spring (€13,600 estimate, score 54) and 8 unpriced premium models
      // (Zeekr 001 78.9 … GV60 39.2). The unpriced cars may not take places 2-5.
      const spring = scored(withBands("spring", [model(2024, 13600)], { model_id: "spring" }), "road-tripper", 54);
      const premium = [78.9, 75.1, 68, 67.6, 56.1, 55, 47.9, 39.2].map((s, i) => scored(row(`prem${i}`, { model_id: `prem${i}`, generation_id: `prem${i}-g` }), "road-tripper", s));
      const res = rankHero([...premium, spring], roadTripper, q(15000), on);
      expect(res.priced).toBe(1);
      expect(res.shortlistN).toBe(1);
      // T-152: with a budget, at most UNPRICED_MAX unpriced fill-ins (was 8); the cut ones are counted.
      expect(res.picks.map((p) => p.rank)).toEqual([1, null, null, null]);
      expect(res.unpricedCapped).toBe(5);
      expect(res.picks[0]!.row.variant_id).toBe("spring");
      // No unpriced car carries a place number in 1-5, or anywhere.
      for (const p of res.picks) expect(p.rank === null).toBe(p.price === null);
      // Enough priced cars: places run 1..n over priced cars only.
      const full = rankHero(rows, roadTripper, q(35000), on);
      expect(full.picks.filter((p) => p.rank !== null).map((p) => p.rank)).toEqual(Array.from({ length: full.priced }, (_, i) => i + 1));
    });
    it("€15k and €35k give different top 10s, and every top-5 price is within the budget", () => {
      const low = rankHero(rows, roadTripper, q(15000), on);
      const high = rankHero(rows, roadTripper, q(35000), on);
      expect(low.picks.map((p) => p.row.variant_id)).not.toEqual(high.picks.map((p) => p.row.variant_id));
      for (const [res, b] of [[low, 15000], [high, 35000]] as const) {
        for (const p of res.picks.slice(0, res.shortlistN)) expect(p.price!.amount).toBeLessThanOrEqual(b);
      }
      expect(low.overBudget).toBe(8 + 1); // every "dear" car and cheap7 (€15,500); cheap6 is exactly €15,000
    });
    it("one card per model: a priced version wins over a higher-scoring unpriced one", () => {
      const a = scored(row("m-a", { model_id: "m" }), "road-tripper", 90);
      const b = scored(withBands("m-b", [model(2021, 14000)], { model_id: "m" }), "road-tripper", 50);
      const res = rankHero([a, b], roadTripper, q(15000), on);
      expect(res.picks.map((p) => p.row.variant_id)).toEqual(["m-b"]);
      expect(res.picks[0]!.alternatives).toBe(1);
    });
    it("an unpriced version doesn't carry a model whose priced versions are all over budget (T-115 review)", () => {
      // Same generation: one version priced at €40k, one unpriced. At €15k neither may show.
      const dear = scored(withBands("x-dear", [model(2023, 40000)], { model_id: "x", generation_id: "x-g1" }), "road-tripper", 60);
      const free = scored(row("x-free", { model_id: "x", generation_id: "x-g1" }), "road-tripper", 99);
      expect(rankHero([dear, free], roadTripper, q(15000), on).picks).toEqual([]);
      expect(rankHero([dear, free], roadTripper, q(15000), on).overBudget).toBe(2);
      // No budget: the unpriced version stays, listed last.
      expect(rankHero([dear, free], roadTripper, q(null), on).picks.map((p) => p.row.variant_id)).toEqual(["x-dear"]);
      // A sibling that fits keeps the generation in; the priced one is the card.
      const fits = scored(withBands("x-ok", [model(2021, 14000)], { model_id: "x", generation_id: "x-g1" }), "road-tripper", 30);
      expect(rankHero([dear, free, fits], roadTripper, q(15000), on).picks.map((p) => p.row.variant_id)).toEqual(["x-ok"]);
      // Generation without any price: the model's other generations decide.
      const newGen = scored(row("x-g2-free", { model_id: "x", generation_id: "x-g2" }), "road-tripper", 99);
      expect(rankHero([dear, newGen], roadTripper, q(15000), on).picks).toEqual([]);
      // A model with no price anywhere stays (unpriced, last), as Decision 064 says.
      const lone = scored(row("y-free", { model_id: "y", generation_id: "y-g1" }), "road-tripper", 99);
      expect(rankHero([dear, lone], roadTripper, q(15000), on).picks.map((p) => [p.row.variant_id, p.price])).toEqual([["y-free", null]]);
    });
    describe("unpriced fill-ins at a small budget (T-152)", () => {
      const spring = scored(withBands("spring", [model(2024, 13600)], { model_id: "spring", segment: "A" }), "road-tripper", 54);
      const unp = (id: string, score: number, o: Partial<ExploreRow> = {}) => scored(row(id, { model_id: id, generation_id: `${id}-g`, ...o }), "road-tripper", score);
      it("a car priced only in another country at more than 2× the budget is no fill-in; at 2× or less it stays", () => {
        const dear = unp("dear-de", 90, { price_new: { DE: { amount: 77250, currency: "EUR" } } });
        const near = unp("near-de", 80, { price_new: { DE: { amount: 30000, currency: "EUR" } } });
        const res = rankHero([dear, near, spring], roadTripper, q(15000), on);
        expect(res.picks.map((p) => p.row.variant_id)).toEqual(["spring", "near-de"]);
        expect(res.unpricedFar).toBe(1);
        expect(res.overBudget).toBe(1);
        // No price is made up: the fill-in still has none.
        expect(res.picks[1]!.price).toBeNull();
      });
      it("a used band in another country counts; the cheapest price we hold decides", () => {
        const usedFr = unp("used-fr", 90, { used_bands: { FR: [[2022, null, 40000, null, 0]] } as never });
        const mixed = unp("mixed", 85, { price_new: { DE: { amount: 60000, currency: "EUR" } }, used_bands: { BE: [[2020, null, 25000, null, 0]] } as never });
        const res = rankHero([usedFr, mixed, spring], roadTripper, q(15000), on);
        expect(res.picks.map((p) => p.row.variant_id)).toEqual(["spring", "mixed"]);
      });
      it("other currencies are never compared or converted", () => {
        const gbp = unp("gbp", 90, { price_new: { UK: { amount: 90000, currency: "GBP" } } });
        expect(rankHero([gbp, spring], roadTripper, q(15000), on).picks.map((p) => p.row.variant_id)).toEqual(["spring", "gbp"]);
      });
      it("no price for the car: its generation's prices elsewhere, else its segment's cheapest car", () => {
        const sib = scored(row("sib", { model_id: "g", generation_id: "g-g", price_new: { DE: { amount: 50000, currency: "EUR" } } }), "road-tripper", 10);
        const noPriceSameGen = scored(row("same-gen", { model_id: "g2", generation_id: "g-g" }), "road-tripper", 90);
        const lux = scored(row("lux-priced", { model_id: "lux", generation_id: "lux-g", segment: "F", price_new: { DE: { amount: 132000, currency: "EUR" } } }), "road-tripper", 10);
        const luxFree = unp("lux-free", 95, { segment: "F" });
        const smallFree = unp("small-free", 70, { segment: "A" });
        const noSeg = unp("no-seg", 60);
        const res = rankHero([sib, noPriceSameGen, lux, luxFree, smallFree, noSeg, spring], roadTripper, q(15000), on);
        // Spring (€13.6k, segment A) keeps the A car in; nothing is known for no-seg, so it stays.
        expect(res.picks.map((p) => p.row.variant_id)).toEqual(["spring", "small-free", "no-seg"]);
        // sib and lux-priced (only priced abroad, far over), same-gen (via sib), lux-free (via segment F).
        expect(res.unpricedFar).toBe(4);
      });
      it("at most 3 unpriced fill-ins with a budget, after every priced car; none dropped without a budget", () => {
        const many = Array.from({ length: 8 }, (_, i) => unp(`free-${i}`, 90 - i));
        const low = rankHero([...many, spring], roadTripper, q(15000), on);
        expect(low.picks.map((p) => p.row.variant_id)).toEqual(["spring", "free-0", "free-1", "free-2"]);
        expect([low.unpriced, low.unpricedCapped, low.qualifying]).toEqual([3, 5, 9]);
        const none = rankHero([...many, spring], roadTripper, q(null), on);
        expect(none.picks).toHaveLength(9);
        expect(none.unpricedCapped).toBe(0);
      });
      it("ten priced cars leave no room: nothing counts as left out", () => {
        const ten = Array.from({ length: 10 }, (_, i) => scored(withBands(`p${i}`, [model(2021, 10000 + i * 100)]), "road-tripper", 50 + i));
        const res = rankHero([...ten, unp("far", 99, { price_new: { DE: { amount: 90000, currency: "EUR" } } }), unp("free", 98)], roadTripper, q(15000), on);
        expect(res.priced).toBe(10);
        expect([res.unpriced, res.unpricedFar, res.unpricedCapped]).toEqual([0, 0, 0]);
      });
      it("only unpriced, far-over cars: an empty list that can say why", () => {
        const res = rankHero([unp("only-far", 90, { price_new: { DE: { amount: 99000, currency: "EUR" } } })], roadTripper, q(15000), on);
        expect(res.picks).toEqual([]);
        expect(res.unpricedFar).toBe(1);
      });
    });
    it("the visitor's refine filters can't hide the over-budget sibling", () => {
      const dear = scored(withBands("z-dear", [model(2023, 40000)], { model_id: "z", generation_id: "z-g1", real_range_km: 200 }), "road-tripper", 60);
      const free = scored(row("z-free", { model_id: "z", generation_id: "z-g1", real_range_km: 500 }), "road-tripper", 99);
      const res = rankHero([dear, free], roadTripper, { ...q(15000), filters: { ...defaultFilters(), rangeMin: 400 } }, on);
      expect(res.picks).toEqual([]);
    });
  });
});

