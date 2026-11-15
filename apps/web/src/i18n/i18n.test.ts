import { describe, expect, it } from "vitest";
import { LANGS } from "@/config/countries";
import { resolveLang } from "@/lib/lang";
import en from "./en.json";
import { getDict, getT, interpolate } from "./index";
import nl from "./nl.json";

describe("i18n", () => {
  it("English is complete and non-empty", () => {
    for (const v of Object.values(en)) expect(v.length).toBeGreaterThan(0);
  });

  it("NL has no keys English lacks", () => {
    for (const k of Object.keys(nl)) expect(Object.keys(en)).toContain(k);
  });

  it("NL covers the main UI strings", () => {
    const prefixes = ["nav.", "explore.", "filters.", "compare.", "col."];
    const main = Object.keys(en).filter((k) => prefixes.some((p) => k.startsWith(p)));
    for (const k of main) expect(Object.keys(nl), k).toContain(k);
  });

  it("empty dictionaries fall back to English key by key", () => {
    for (const l of ["de", "fr", "es", "it"] as const) {
      expect(getDict(l)["nav.explore"]).toBe(en["nav.explore"]);
    }
    expect(getT("nl")("nav.explore")).toBe("Verkennen");
    // Every language returns a full dictionary.
    for (const l of LANGS) expect(Object.keys(getDict(l))).toHaveLength(Object.keys(en).length);
  });

  it("interpolates variables and leaves unknown ones", () => {
    expect(getT("en")("explore.count", { shown: 3, total: 10 })).toBe("3 of 10 cars");
    expect(interpolate("{a} {b}", { a: 1 })).toBe("1 {b}");
  });

  it("resolves language: ?lang → cookie → country default", () => {
    expect(resolveLang("/de", "fr", "nl")).toBe("fr");
    expect(resolveLang("/de", null, "nl")).toBe("nl");
    expect(resolveLang("/de", "xx", undefined)).toBe("de");
    expect(resolveLang("/be/compare", null, null)).toBe("nl");
    expect(resolveLang("/uk", null, null)).toBe("en");
    expect(resolveLang("/", null, null)).toBe("en");
  });
});
