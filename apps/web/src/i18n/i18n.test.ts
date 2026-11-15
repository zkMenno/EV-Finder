import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { LANGS } from "@/config/countries";
import { routeLang, suggestLang } from "@/lib/lang";
import { RANKING_IDS } from "@/lib/rankings";
import { SPEC_FIELDS, SPEC_GROUPS } from "@/lib/spec-diff";
import en from "./en.json";
import { getClientDict, getDict, getT, hasMsgKey, interpolate, SERVER_ONLY_PREFIXES } from "./index";
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

  it("URL language routing (Decision 015): language URLs pass, the rest redirects", () => {
    // Served pairs pass through untouched.
    expect(routeLang("/nl/nl", "", null)).toBeNull();
    expect(routeLang("/be/fr/ev/a/b", "?x=1", "nl")).toBeNull();
    expect(routeLang("/staff/review", "", null)).toBeNull();
    expect(routeLang("/health", "", null)).toBeNull();
    // /{country}: remembered language if served, else the config default (temporary redirect).
    expect(routeLang("/de", "", null)).toEqual({ redirect: "/de/de", status: 307 });
    expect(routeLang("/de", "?range=300", "en")).toEqual({ redirect: "/de/en?range=300", status: 307 });
    expect(routeLang("/de/", "", "fr")).toEqual({ redirect: "/de/de", status: 307 });
    expect(routeLang("/be", "", null)).toEqual({ redirect: "/be/nl", status: 307 });
    expect(routeLang("/uk", "", "nl")).toEqual({ redirect: "/uk/en", status: 307 });
    expect(routeLang("/", "", null)).toEqual({ redirect: "/nl/nl", status: 307 });
    expect(routeLang("/nl", "?range=300&lang=en", "nl")).toEqual({ redirect: "/nl/en?range=300", status: 308 });
    expect(routeLang("/nl", "?lang=de", null)).toEqual({ redirect: "/nl/nl", status: 307 });
    // Old URLs: 308 to the default language, or to ?lang when the country serves it.
    expect(routeLang("/nl/ev/renault/zoe", "", null)).toEqual({ redirect: "/nl/nl/ev/renault/zoe", status: 308 });
    expect(routeLang("/nl/compare", "?ids=a,b&lang=en", "nl")).toEqual({ redirect: "/nl/en/compare?ids=a,b", status: 308 });
    expect(routeLang("/nl/top", "?lang=de", null)).toEqual({ redirect: "/nl/nl/top", status: 308 });
    expect(routeLang("/be/learn/real-range", "?lang=fr", null)).toEqual({ redirect: "/be/fr/learn/real-range", status: 308 });
    // A language the country doesn't serve → its default.
    expect(routeLang("/uk/nl/top", "", null)).toEqual({ redirect: "/uk/en/top", status: 308 });
  });

  it("Accept-Language only suggests a served language, never the current one", () => {
    expect(suggestLang(["fr-BE", "nl"], ["nl", "fr", "de", "en"], "nl")).toBe("fr");
    expect(suggestLang(["nl-NL", "fr"], ["nl", "fr", "de", "en"], "nl")).toBeNull();
    expect(suggestLang(["es-ES", "en-GB"], ["nl", "en"], "nl")).toBe("en");
    expect(suggestLang(["it"], ["en"], "en")).toBeNull();
    expect(suggestLang([], ["nl", "en"], "nl")).toBeNull();
  });

  it("page strings (model, compare, rankings) are merged and fall back to English", () => {
    expect(getT("nl")("compare.title")).toBe("Vergelijken");
    expect(getT("de")("compare.title")).toBe(en["compare.title"]);
    expect(getT("nl")("compare.printNote", { site: "S", release: 1 })).toBe("Afgedrukt van S, datarelease 1.");
    expect(getT("fr")("compare.printNote", { site: "S", release: 1 })).toBe("Printed from S, data release 1.");
    expect(getT("nl")("nav.rankings")).toBe("Ranglijsten");
  });

  it("has a label for every spec field, group and ranking", () => {
    for (const f of SPEC_FIELDS) expect(hasMsgKey(`field.${f.key}`), f.key).toBe(true);
    for (const g of SPEC_GROUPS) expect(hasMsgKey(`variant.group.${g}`), g).toBe(true);
    for (const id of RANKING_IDS) for (const s of ["title", "short", "metric", "method"]) expect(hasMsgKey(`top.${id}.${s}`)).toBe(true);
    expect(hasMsgKey("no.such.key")).toBe(false);
  });

  it("the client dictionary drops server-only keys and keeps the rest", () => {
    const d = getClientDict("nl");
    expect(d["nav.explore"]).toBe("Verkennen");
    expect(d["compare.add"]).toBe(getDict("nl")["compare.add"]);
    expect(Object.keys(d).some((k) => SERVER_ONLY_PREFIXES.some((p) => k.startsWith(p)))).toBe(false);
  });

  it("client components never use server-only keys", () => {
    const dir = path.resolve(__dirname, "../components");
    for (const f of readdirSync(dir).filter((n) => n.endsWith(".tsx"))) {
      const src = readFileSync(path.join(dir, f), "utf8");
      if (!src.startsWith('"use client"')) continue;
      for (const p of SERVER_ONLY_PREFIXES) {
        expect(src.includes(`t("${p}`) || src.includes(`t(\`${p}`), `${f} uses ${p}*`).toBe(false);
      }
    }
  });
});
