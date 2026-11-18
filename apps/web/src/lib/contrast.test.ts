// WCAG 2.2 1.4.11 (non-text contrast): control borders need 3:1 against every ground they sit on.
// --line-strong edges inputs, filter pills and answer tiles on paper, paper-sea (the hero),
// surface (cards, panels) and surface-sunk (input wells). Reads the design tokens directly.
import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

type Tok = { name: string; value: string | { light: string; dark: string } };
const file = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../../../../docs/design/tokens.json");
const tokens: Tok[] = JSON.parse(readFileSync(file, "utf8")).color.tokens;

function hex(name: string, theme: "light" | "dark"): string {
  const t = tokens.find((x) => x.name === name);
  if (!t) throw new Error(`no token ${name}`);
  const v = typeof t.value === "string" ? t.value : t.value[theme];
  return v.startsWith("{") ? hex(v.slice(1, -1), theme) : v;
}
function lum(h: string): number {
  const c = [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16) / 255).map((x) => (x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4));
  return 0.2126 * c[0]! + 0.7152 * c[1]! + 0.0722 * c[2]!;
}
function ratio(a: string, b: string): number {
  const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p);
  return (x! + 0.05) / (y! + 0.05);
}

describe("control border contrast (--line-strong)", () => {
  for (const theme of ["light", "dark"] as const)
    for (const ground of ["paper", "paper-sea", "surface", "surface-sunk"])
      it(`${theme}: line-strong on ${ground} ≥ 3:1`, () => {
        expect(ratio(hex("line-strong", theme), hex(ground, theme))).toBeGreaterThanOrEqual(3);
      });
});
