import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { buildPopularity, loadPopularity, OUT_FILE, parseConfig, pickScores, registrationScores, serialize } from "../../scripts/popularity.mjs";
import { popularityScore, rankGenerations, type PopularityInputs } from "./popularity";
import { sortRows } from "./filters";
import { MENU_SORTS, sortBy, defaultState, fromSearchParams, toSearchParams } from "./state";
import type { ExploreRow } from "./explore-data";

const inputs: PopularityInputs = {
  weights: { registrations: 0.8, owner_picks: 0.2 },
  models: { a: 8, b: 4, c: 0 },
  generations: { "b-gen2": 1 },
};

describe("popularityScore (T-130 blend)", () => {
  it("scales registrations to the top model and adds the owner pick", () => {
    expect(popularityScore("a", "a-gen1", inputs)).toBe(80); // 0.8 × 8/8
    expect(popularityScore("b", "b-gen1", inputs)).toBe(40); // 0.8 × 4/8
    expect(popularityScore("b", "b-gen2", inputs)).toBe(60); // + 0.2 × 1
  });
  it("is null when neither registrations nor a pick are known (never a guess)", () => {
    expect(popularityScore("zz", "zz-gen1", inputs)).toBeNull();
  });
  it("a pick alone still counts; zero registrations are a known zero", () => {
    expect(popularityScore("zz", "b-gen2", inputs)).toBe(20);
    expect(popularityScore("c", "c-gen1", inputs)).toBe(0);
  });
  it("weights are relative: doubling both changes nothing", () => {
    const double = { ...inputs, weights: { registrations: 1.6, owner_picks: 0.4 } };
    expect(popularityScore("b", "b-gen2", double)).toBe(popularityScore("b", "b-gen2", inputs));
  });
});

describe("rankGenerations", () => {
  const rows = [
    { model_id: "b", generation_id: "b-gen1" },
    { model_id: "a", generation_id: "a-gen1" },
    { model_id: "a", generation_id: "a-gen1" },
    { model_id: "b", generation_id: "b-gen2" },
    { model_id: "zz", generation_id: "zz-gen1" },
  ];
  it("ranks each generation once, highest first, unknowns unranked", () => {
    const r = rankGenerations(rows, inputs);
    expect([...r.entries()]).toEqual([
      ["a-gen1", { score: 80, rank: 1 }],
      ["b-gen2", { score: 60, rank: 2 }],
      ["b-gen1", { score: 40, rank: 3 }],
    ]);
  });
  it("breaks ties by id, so ranks are stable", () => {
    const tie = rankGenerations([{ model_id: "x", generation_id: "x-2" }, { model_id: "x", generation_id: "x-1" }], { ...inputs, models: { x: 1 } });
    expect(tie.get("x-1")?.rank).toBe(1);
  });
});

describe("popular sort", () => {
  const row = (id: string, pop?: number) => ({ variant_id: id, ...(pop === undefined ? {} : { pop }) }) as unknown as ExploreRow;
  it("sorts high to low with unknowns last", () => {
    const out = sortRows([row("u"), row("lo", 10), row("hi", 90)], "popular", "desc", "NL");
    expect(out.map((r) => r.variant_id)).toEqual(["hi", "lo", "u"]);
  });
  it("menu picks the natural direction and round-trips through the URL", () => {
    const s = sortBy(defaultState(), "popular");
    expect(s.dir).toBe("desc");
    expect(sortBy(defaultState(), "price").dir).toBe("asc");
    const back = fromSearchParams(Object.fromEntries(toSearchParams(s)));
    expect(back.sort).toBe("popular");
    expect(back.dir).toBe("desc");
    expect(MENU_SORTS[0]).toBe("popular");
  });
  it("the page's default view stays out of the URL; the other one is written (cards default on /cars)", () => {
    const table = { ...defaultState(), view: "table" as const };
    const cards = { ...defaultState(), view: "cards" as const };
    expect(toSearchParams(table).get("view")).toBeNull();
    expect(toSearchParams(cards).get("view")).toBe("cards");
    expect(toSearchParams(table, "cards").get("view")).toBe("table");
    expect(toSearchParams(cards, "cards").get("view")).toBeNull();
  });
});

describe("scripts/popularity.mjs", () => {
  it("committed JSON matches the YAML inputs (run `node scripts/popularity.mjs`)", () => {
    expect(readFileSync(OUT_FILE, "utf8")).toBe(serialize(loadPopularity()));
  });
  it("rejects bad weights", () => {
    expect(() => parseConfig({ weights: { registrations: 0, owner_picks: 0 }, pick_values: { shortlist: 1, consider: 0.5, fallback: 0.2 } })).toThrow();
    expect(() => parseConfig({ weights: { registrations: 1, owner_picks: -1 }, pick_values: { shortlist: 1, consider: 0.5, fallback: 0.2 } })).toThrow();
    expect(() => parseConfig({ weights: { registrations: 1, owner_picks: 0 }, pick_values: { shortlist: 2, consider: 0.5, fallback: 0.2 } })).toThrow();
  });
  it("reads ranked and outside-top models; drops bad ids", () => {
    expect(registrationScores({ models: [{ model_id: "a-b", score_pct: 2 }, { model_id: "Bad Id", score_pct: 1 }], seed_models_outside_top: [{ model_id: "c", score_pct: 0.5 }] })).toEqual({ "a-b": 2, c: 0.5 });
  });
  it("picks: best verdict + favourite bonus, capped at 1; unrated and ruled out give nothing", () => {
    const cfg = parseConfig({ weights: { registrations: 1, owner_picks: 1 }, pick_values: { shortlist: 1, consider: 0.6, fallback: 0.3 }, favourite_bonus: 0.2 });
    const doc = {
      primary_car_picks: [
        { seed_generation_id: "g1", verdict: "consider", favourite: true },
        { seed_generation_id: "g1", verdict: "fallback" },
        { seed_generation_id: "g2", verdict: "shortlist", favourite: true },
        { seed_generation_id: "g3", verdict: "unrated", notes: "note" },
        { seed_generation_id: "g4", verdict: "ruled_out" },
      ],
    };
    expect(pickScores(doc, cfg)).toEqual({ g1: 0.8, g2: 1 });
  });
  it("never carries sheet values into the output", () => {
    const out = JSON.stringify(buildPopularity({ models: [] }, { primary_car_picks: [{ seed_generation_id: "g", verdict: "shortlist", sheet_values: { secret: 1 } }] }, { weights: { registrations: 1, owner_picks: 1 }, pick_values: { shortlist: 1, consider: 0.6, fallback: 0.3 } }));
    expect(out).not.toContain("secret");
  });
});
