import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { GEN_FILE, OUT_DIR, SRC_DIR, generate, plan } from "../../../scripts/scenes.mjs";
import { layerTransform } from "./ParallaxScene";

describe("scenes drift guard (UX owns docs/design/assets/Illustrations)", () => {
  it("scenes.generated.ts matches layers/manifest.json (run `pnpm scenes`)", () => {
    expect(readFileSync(GEN_FILE, "utf8")).toBe(generate(plan()));
  });
  it("every copied SVG is identical to the design-system original (run `pnpm scenes`)", () => {
    const stale: string[] = [];
    for (const modes of Object.values(plan().scenes)) {
      for (const m of Object.values(modes)) {
        for (const f of [m.flat, ...m.layers.map((l) => l.file)]) {
          if (readFileSync(join(SRC_DIR, f), "utf8") !== readFileSync(join(OUT_DIR, f), "utf8")) stale.push(f);
        }
      }
    }
    expect(stale).toEqual([]);
  });
  it("highway keeps UX's order: signs behind the road, traffic in front", () => {
    const files = plan().scenes.highway!.day.layers.map((l) => l.file.replace(/^layers\/highway-day-\d-/, ""));
    expect(files.indexOf("signs.svg")).toBeLessThan(files.indexOf("road.svg"));
    expect(files.indexOf("road.svg")).toBeLessThan(files.indexOf("traffic-far.svg"));
  });
});

describe("layerTransform (manifest: amp 180, tilt 32, drive 420)", () => {
  it("portrait scenes drift vertically by progress × depth × 180", () => {
    expect(layerTransform("y", 0.5, 1)).toBe("translate3d(0.0px,90.0px,0)");
    expect(layerTransform("y", -0.14, 1)).toBe("translate3d(0.0px,-25.2px,0)");
    expect(layerTransform("y", 0.5, 0)).toBe("translate3d(0.0px,0.0px,0)");
  });
  it("adds a pointer tilt of depth × 32", () => {
    expect(layerTransform("y", 0.5, 0, 0.5, 0)).toBe("translate3d(-8.0px,0.0px,0)");
  });
  it("wide bands slide sideways by progress × speed × 420", () => {
    expect(layerTransform("x", 1.35, 1)).toBe("translate3d(567.0px,0,0)");
    expect(layerTransform("x", 0.2, -0.5)).toBe("translate3d(-42.0px,0,0)");
  });
});
