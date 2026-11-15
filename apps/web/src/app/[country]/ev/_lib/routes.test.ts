import { describe, expect, it } from "vitest";
import { catalogue } from "@/test/helpers";
import {
  childSegment,
  findVariant,
  generationHref,
  generationParams,
  generationRows,
  modelHref,
  modelParams,
  modelRows,
  segmentCollisions,
  variantHref,
  variantParams,
} from "./routes";

const rows = catalogue.rows;

describe("slugs from stable ids", () => {
  it("strips the parent prefix when clean, else keeps the id", () => {
    expect(childSegment("audi-e-tron-ge", "audi-e-tron")).toBe("ge");
    expect(childSegment("vw-e-golf", "volkswagen")).toBe("vw-e-golf");
    expect(childSegment("audi-e-tron", "audi-e-tron")).toBe("audi-e-tron");
  });

  it("builds nested hrefs", () => {
    const r = rows.find((x) => x.variant_id === "nissan-leaf-ze1-62kwh")!;
    expect(modelHref("nl", r)).toBe("/nl/ev/nissan/leaf");
    expect(generationHref("nl", r)).toBe("/nl/ev/nissan/leaf/ze1");
    expect(variantHref("nl", r)).toBe("/nl/ev/nissan/leaf/ze1/62kwh");
    const golf = rows.find((x) => x.model_id === "vw-e-golf")!;
    expect(modelHref("de", golf)).toBe("/de/ev/volkswagen/vw-e-golf");
  });

  it("round-trips every fixture variant and has no collisions", () => {
    expect(segmentCollisions(rows)).toEqual([]);
    for (const p of variantParams(rows)) {
      const r = findVariant(rows, p.make, p.model, p.generation, p.variant);
      expect(r, JSON.stringify(p)).toBeDefined();
      expect(variantHref("nl", r!)).toBe(`/nl/ev/${p.make}/${p.model}/${p.generation}/${p.variant}`);
    }
  });

  it("finds rows per model and generation; unknown → empty (404)", () => {
    expect(modelRows(rows, "nissan", "leaf").length).toBe(4);
    expect(generationRows(rows, "nissan", "leaf", "ze1").length).toBe(2);
    expect(modelRows(rows, "nissan", "nope")).toEqual([]);
    expect(findVariant(rows, "nissan", "leaf", "ze1", "nope")).toBeUndefined();
  });

  it("static params are unique", () => {
    const m = modelParams(rows).map((p) => `${p.make}/${p.model}`);
    expect(new Set(m).size).toBe(m.length);
    const g = generationParams(rows).map((p) => `${p.make}/${p.model}/${p.generation}`);
    expect(new Set(g).size).toBe(g.length);
    expect(g).toHaveLength(new Set(rows.map((r) => r.generation_id)).size);
  });
});
