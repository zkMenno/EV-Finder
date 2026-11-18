// The app's font files are copies of the design system's (UX owns docs/design/fonts): fail on drift.
import { readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

const here = path.dirname(new URL(import.meta.url).pathname);
const app = path.resolve(here, "../fonts");
const design = path.resolve(here, "../../../../docs/design/fonts");

describe("brand fonts", () => {
  const files = readdirSync(app).filter((f) => f.endsWith(".woff2"));
  it("ships Atkinson Hyperlegible (text) and Bitter (headings)", () => {
    expect(files.some((f) => f.startsWith("atkinson-hyperlegible-latin-400-normal"))).toBe(true);
    expect(files.some((f) => f.startsWith("atkinson-hyperlegible-latin-700-normal"))).toBe(true);
    expect(files.some((f) => f.startsWith("bitter-latin-700-normal"))).toBe(true);
  });
  it.each(files)("%s is byte-identical to docs/design/fonts", (f) => {
    expect(readFileSync(path.join(app, f)).equals(readFileSync(path.join(design, f)))).toBe(true);
  });
  it("fonts.ts loads every shipped file and nothing else", () => {
    const src = readFileSync(path.join(here, "fonts.ts"), "utf8");
    const used = [...src.matchAll(/\.\.\/fonts\/([\w.-]+\.woff2)/g)].map((m) => m[1]).sort();
    expect(used).toEqual([...files].sort());
  });
});
