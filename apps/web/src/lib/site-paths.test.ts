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
  it("Decision 082: every country serves English only, English is the default", () => {
    expect(COUNTRY_SLUGS).toHaveLength(7);
    for (const c of COUNTRY_SLUGS) {
      expect(COUNTRIES[c].served, c).toEqual(["en"]);
      expect(COUNTRIES[c].defaultLang, c).toBe("en");
      for (const l of ["nl", "de", "fr", "es", "it"]) expect(isServed(c, l), `${c}/${l}`).toBe(false);
    }
  });
  it("validates the YAML keys", () => {
    expect(() => validateLanguages("nl", { languages: ["nl"], default_language: "de" })).toThrow(/default_language/);
    expect(() => validateLanguages("nl", { languages: ["xx"], default_language: "xx" })).toThrow(/not one of/);
    expect(() => validateLanguages("nl", { languages: [], default_language: "nl" })).toThrow(/default_language/);
    expect(() => validateLanguages("nl", { default_language: "en" })).toThrow(/must be a list/);
    expect(validateLanguages("uk", { languages: ["en"], default_language: "en" }).served).toEqual(["en"]);
    // Empty list = English only (Decision 082); adding a language back serves it again.
    expect(validateLanguages("nl", { languages: [], default_language: "en" }).served).toEqual(["en"]);
    expect(validateLanguages("be", { languages: ["nl", "fr"], default_language: "nl" }).served).toEqual(["nl", "fr", "en"]);
  });
});

describe("hreflang and sitemap", () => {
  it("one hreflang per served pair + x-default, unique tags", () => {
    const h = hreflangs("/ev/a/b");
    const pairs = servedPairs();
    expect(Object.keys(h)).toHaveLength(pairs.length + 1);
    expect(h["fr-BE"]).toBeUndefined();
    expect(h["en-BE"]).toBe("/be/en/ev/a/b");
    expect(h["en-GB"]).toBe("/uk/en/ev/a/b");
    // Decision 082: only English alternates, one per launch country.
    expect(Object.keys(h).filter((k) => k !== "x-default").every((k) => k.startsWith("en-"))).toBe(true);
    expect(h["x-default"]).toBe(`${siteBase(X_DEFAULT.country, X_DEFAULT.lang)}/ev/a/b`);
    expect(new Set(pairs.map((p) => hreflangTag(p.country, p.lang))).size).toBe(pairs.length);
    expect(hreflangs("")["nl-NL"]).toBeUndefined();
    expect(hreflangs("")["en-NL"]).toBe("/nl/en");
    expect(alternates("de", "en", "top").canonical).toBe("/de/en/top");
  });
  it("sitemap lists only served pairs, every variant once per pair", () => {
    const cat = getCatalogue();
    const urls = sitemapUrls(cat, "https://x.example");
    expect(urls.some((u) => u.startsWith("https://x.example/nl/de"))).toBe(false);
    expect(urls.some((u) => u.startsWith("https://x.example/uk/nl"))).toBe(false);
    expect(urls).toContain("https://x.example/be/en");
    expect(urls.some((u) => /^https:\/\/x\.example\/[a-z]{2}\/(nl|de|fr|es|it)(\/|$)/.test(u))).toBe(false);
    expect(new Set(urls).size).toBe(urls.length);
    const variants = urls.filter((u) => u.split("/").length === 10);
    expect(variants).toHaveLength(cat.rows().length * servedPairs().length);
    expect(urls.some((u) => u.includes("/compare"))).toBe(false);
  });
});

describe("Spain and Italy (Decision 066, in English per Decision 082)", () => {
  it("are launch countries served in English, from config/countries/es.yaml and it.yaml", () => {
    expect(COUNTRY_SLUGS).toEqual(expect.arrayContaining(["es", "it"]));
    expect(COUNTRIES.es).toMatchObject({ code: "ES", currency: "EUR", defaultLang: "en", served: ["en"] });
    expect(COUNTRIES.it).toMatchObject({ code: "IT", currency: "EUR", defaultLang: "en", served: ["en"] });
    const pairs = servedPairs().map((p) => `${p.country}/${p.lang}`);
    expect(pairs).toEqual(expect.arrayContaining(["es/en", "it/en"]));
    expect(pairs).not.toContain("es/es");
    expect(pairs).not.toContain("it/it");
  });
  it("hreflang and sitemap carry en-ES / en-IT, not es-ES / it-IT", () => {
    const h = hreflangs("/learn");
    expect(h["en-ES"]).toBe("/es/en/learn");
    expect(h["en-IT"]).toBe("/it/en/learn");
    expect(h["es-ES"]).toBeUndefined();
    expect(h["it-IT"]).toBeUndefined();
    const urls = sitemapUrls(getCatalogue(), "https://x.example");
    expect(urls).toContain("https://x.example/es/en");
    expect(urls).toContain("https://x.example/it/en/learn");
    expect(urls).not.toContain("https://x.example/es/es");
  });
});
