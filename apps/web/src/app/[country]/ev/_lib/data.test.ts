import { describe, expect, it } from "vitest";
import type { Catalogue } from "@/lib/catalogue";
import { catalogue } from "@/test/helpers";
import { generationTitle, groupGenerations, withCountries } from "./data";

describe("generationTitle", () => {
  it("does not repeat make or model names", () => {
    expect(generationTitle({ make_name: "Audi", model_name: "e-tron", generation_name: "e-tron (GE)" })).toBe("Audi e-tron (GE)");
    expect(generationTitle({ make_name: "Honda", model_name: "e", generation_name: "Honda e" })).toBe("Honda e");
    expect(generationTitle({ make_name: "Nissan", model_name: "Leaf", generation_name: "ZE1" })).toBe("Nissan Leaf ZE1");
    expect(generationTitle({ make_name: "Polestar", model_name: "Polestar 2", generation_name: "Polestar 2" })).toBe("Polestar 2");
  });
});

describe("withCountries", () => {
  it("crosses params with all 5 countries", () => {
    expect(withCountries([{ a: "x" }])).toHaveLength(5);
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
