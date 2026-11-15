import { describe, expect, it } from "vitest";
import type { Catalogue } from "@/lib/catalogue";
import { catalogue } from "@/test/helpers";
import { generationTitle, groupGenerations, yearsStatus } from "./data";

describe("generationTitle", () => {
  it("does not repeat make or model names", () => {
    expect(generationTitle({ make_name: "Audi", model_name: "e-tron", generation_name: "e-tron (GE)" })).toBe("Audi e-tron (GE)");
    expect(generationTitle({ make_name: "Honda", model_name: "e", generation_name: "Honda e" })).toBe("Honda e");
    expect(generationTitle({ make_name: "Nissan", model_name: "Leaf", generation_name: "ZE1" })).toBe("Nissan Leaf ZE1");
    expect(generationTitle({ make_name: "Polestar", model_name: "Polestar 2", generation_name: "Polestar 2" })).toBe("Polestar 2");
  });
});

describe("groupGenerations", () => {
  it("groups rows by generation in year order and carries the uncertain flag", () => {
    const leaf = catalogue.rows.filter((r) => r.model_id === "nissan-leaf");
    // Fixture generations, looked up the way the Catalogue does.
    const byId = new Map((catalogue.generations ?? []).map((g) => [g.id, g]));
    const cat = { generation: (id: string) => byId.get(id) } as unknown as Catalogue;
    const gens = groupGenerations(cat, leaf);
    // With no generation entities, they are rebuilt from the rows.
    const bare = groupGenerations({ generation: () => undefined } as unknown as Catalogue, leaf);
    expect(bare.map((g) => g.id)).toEqual(gens.map((g) => g.id));
    expect(gens.map((g) => g.id)).toEqual(["nissan-leaf-ze0", "nissan-leaf-aze0", "nissan-leaf-ze1"]);
    expect(gens.every((g) => typeof g.uncertain === "boolean")).toBe(true);
    expect(gens.find((g) => g.id === "nissan-leaf-ze1")!.rows).toHaveLength(2);
  });
});

describe("yearsStatus (T-061)", () => {
  const check = (agrees: boolean, year = 2020) => ({ boundary: "start" as const, year, agrees, source_id: "wikidata", retrieved_at: "2026-11-15" });
  it("keeps the old rule without an outside check", () => {
    expect(yearsStatus(true, undefined).kind).toBe("unchecked");
    expect(yearsStatus(false, undefined).kind).toBe("none");
  });
  it("corroborated when every check agrees, even if not hand-checked", () => {
    const s = yearsStatus(true, { corroborated: true, tolerance_years: 1, source_ids: ["wikidata"], checks: [check(true)] });
    expect(s.kind).toBe("corroborated");
  });
  it("disagrees when any check is off (details kept for Nerd)", () => {
    const s = yearsStatus(false, { corroborated: false, tolerance_years: 1, source_ids: ["wikidata"], checks: [check(false, 2024), check(true, 2019)] });
    expect(s.kind).toBe("disagrees");
    expect(s.kind === "disagrees" ? s.checks.map((c) => c.year) : []).toEqual([2024, 2019]);
    // A "corroborated" flag that contradicts a failing check never shows as checked.
    expect(yearsStatus(true, { corroborated: true, tolerance_years: 1, source_ids: ["wikidata"], checks: [check(false)] }).kind).toBe("disagrees");
  });
});
