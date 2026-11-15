import { existsSync, readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { buildCss, loadCss, OUT_FILE, TOKENS_FILE } from "../../scripts/theme.mjs";
import { memoryStorage } from "./storage";
import { effectiveTheme, readTheme, THEME_INIT_JS, THEME_KEY, writeTheme } from "./theme";

describe("theme (Day trip / Night drive)", () => {
  it("remembers only light or dark", () => {
    const s = memoryStorage();
    expect(readTheme(s)).toBeNull();
    expect(writeTheme("dark", s)).toBe(true);
    expect(readTheme(s)).toBe("dark");
    s.setItem(THEME_KEY, "purple");
    expect(readTheme(s)).toBeNull();
    expect(readTheme(null)).toBeNull();
  });

  it("follows the system unless a choice is stored", () => {
    expect(effectiveTheme(null, true)).toBe("dark");
    expect(effectiveTheme(null, false)).toBe("light");
    expect(effectiveTheme("light", true)).toBe("light");
  });

  it("init script reads the same key and survives storage errors", () => {
    expect(THEME_INIT_JS).toContain(JSON.stringify(THEME_KEY));
    expect(THEME_INIT_JS).toContain("catch");
  });

  it("CSS has both themes, the system default and resolved references", () => {
    const css = buildCss({
      color: {
        themes: [{ id: "light", name: "Day trip" }, { id: "dark", name: "Night drive" }],
        tokens: [
          { name: "ink", value: { light: "#222", dark: "#eee" } },
          { name: "focus", value: { light: "{ink}", dark: "{ink}" } },
        ],
      },
    });
    expect(css).toContain(':root[data-theme="dark"]');
    expect(css).toContain("prefers-color-scheme: dark");
    expect(css).toMatch(/--focus: #222;/);
    expect(css).toMatch(/--focus: #eee;/);
    expect(() => buildCss({ color: { tokens: [{ name: "x", value: { light: "{x}", dark: "#000" } }] } })).toThrow();
    expect(() => buildCss({ color: { tokens: [{ name: "x", value: { light: "red;}", dark: "#000" } }] } })).toThrow();
  });

  it.runIf(existsSync(TOKENS_FILE))("committed tokens.generated.css matches docs/design/tokens.json", () => {
    expect(readFileSync(OUT_FILE, "utf8")).toBe(loadCss());
  });
});
