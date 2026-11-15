import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { COUNTRIES, COUNTRY_SLUGS, hreflangTag, isServed, servedPairs } from "@/config/countries";
import { OUT_FILE, serialize, loadCountryLanguages, validateLanguages } from "../../scripts/countries.mjs";
import { getCatalogue } from "./catalogue";
import { sitemapUrls } from "./sitemap";
import { alternates, hreflangs, siteBase, X_DEFAULT } from "./site-paths";

describe("country languages from config (Decision 015)", () => {
  it("the committed JSON matches config/countries/*.yaml", () => {
    expect(readFileSync(OUT_FILE, "utf8")).toBe(serialize(loadCountryLanguages()));
  });
  it("serves each country's own languages + EN; default from config", () => {
    expect(COUNTRIES.be.served).toEqual(["nl", "fr", "de", "en"]);
    expect(COUNTRIES.uk.served).toEqual(["en"]);
    expect(COUNTRIES.be.defaultLang).toBe("nl");
    for (const c of COUNTRY_SLUGS) {
      expect(COUNTRIES[c].served).toContain("en");
      expect(COUNTRIES[c].served).toContain(COUNTRIES[c].defaultLang);
    }
    expect(isServed("nl", "de")).toBe(false);
    expect(isServed("be", "de")).toBe(true);
  });
  it("validates the YAML keys", () => {
    expect(() => validateLanguages("nl", { languages: ["nl"], default_language: "en" })).toThrow(/default_language/);
    expect(() => validateLanguages("nl", { languages: ["xx"], default_language: "xx" })).toThrow(/not one of/);
    expect(() => validateLanguages("nl", { languages: [], default_language: "nl" })).toThrow(/non-empty/);
    expect(validateLanguages("uk", { languages: ["en"], default_language: "en" }).served).toEqual(["en"]);
  });
});

describe("hreflang and sitemap", () => {
  it("one hreflang per served pair + x-default, unique tags", () => {
    const h = hreflangs("/ev/a/b");
    const pairs = servedPairs();
    expect(Object.keys(h)).toHaveLength(pairs.length + 1);
    expect(h["fr-BE"]).toBe("/be/fr/ev/a/b");
    expect(h["en-GB"]).toBe("/uk/en/ev/a/b");
    expect(h["x-default"]).toBe(`${siteBase(X_DEFAULT.country, X_DEFAULT.lang)}/ev/a/b`);
    expect(new Set(pairs.map((p) => hreflangTag(p.country, p.lang))).size).toBe(pairs.length);
    expect(hreflangs("")["nl-NL"]).toBe("/nl/nl");
    expect(alternates("de", "en", "top").canonical).toBe("/de/en/top");
  });
  it("sitemap lists only served pairs, every variant once per pair", () => {
    const cat = getCatalogue();
    const urls = sitemapUrls(cat, "https://x.example");
    expect(urls.some((u) => u.startsWith("https://x.example/nl/de"))).toBe(false);
    expect(urls.some((u) => u.startsWith("https://x.example/uk/nl"))).toBe(false);
    expect(urls).toContain("https://x.example/be/fr");
    expect(new Set(urls).size).toBe(urls.length);
    const variants = urls.filter((u) => u.split("/").length === 10);
    expect(variants).toHaveLength(cat.rows().length * servedPairs().length);
    expect(urls.some((u) => u.includes("/compare"))).toBe(false);
  });
});
