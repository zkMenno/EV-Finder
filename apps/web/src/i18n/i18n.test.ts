import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import * as yaml from "js-yaml";
import { describe, expect, it } from "vitest";
import { COUNTRY_SLUGS, LANGS } from "@/config/countries";
import { routeLang, suggestLang } from "@/lib/lang";
import { RANKING_IDS } from "@/lib/rankings";
import { SPEC_FIELDS, SPEC_GROUPS } from "@/lib/spec-diff";
import de from "./de.json";
import en from "./en.json";
import es from "./es.json";
import fr from "./fr.json";
import { getClientDict, getDict, getT, hasMsgKey, interpolate, SERVER_ONLY_PREFIXES } from "./index";
import itDict from "./it.json";
import nl from "./nl.json";

// Staff pages are EN only (apps/web/AGENTS.md rule 9); every other key is public.
const PUBLIC_KEYS = Object.keys(en).filter((k) => !k.startsWith("staff."));
const DICTS: Record<"nl" | "de" | "fr" | "es" | "it", Record<string, string>> = { nl, de, fr, es, it: itDict };
// DE/FR/ES/IT are agent drafts; EN and NL are the reviewed languages (Decision 066, REVIEW D6).
const DRAFT_LANGS = ["de", "fr", "es", "it"] as const;
const placeholders = (s: string) => (s.match(/\{\w+\}/g) ?? []).sort();

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

  it("missing keys fall back to English key by key", () => {
    // Staff keys are EN only, so they show the fallback in every other language (T-117: the
    // public keys are all translated now, so nav.explore no longer falls back).
    for (const l of ["nl", "de", "fr", "es", "it"] as const) {
      expect(getDict(l)["staff.review.title"]).toBe(en["staff.review.title"]);
    }
    expect(getT("nl")("nav.explore")).toBe("Verkennen");
    // Every language returns a full dictionary.
    for (const l of LANGS) expect(Object.keys(getDict(l))).toHaveLength(Object.keys(en).length);
  });

  it("interpolates variables and leaves unknown ones", () => {
    expect(getT("en")("explore.count", { shown: 3, total: 10 })).toBe("3 of 10 cars");
    expect(interpolate("{a} {b}", { a: 1 })).toBe("1 {b}");
  });

  it("URL language routing (Decision 015 + 082): only /{country}/en/ is served, the rest redirects", () => {
    // Decision 082: English only at launch. /{country}/en/… passes through untouched.
    expect(routeLang("/nl/en", "", null)).toBeNull();
    expect(routeLang("/be/en/ev/a/b", "?x=1", "nl")).toBeNull();
    expect(routeLang("/staff/review", "", null)).toBeNull();
    expect(routeLang("/health", "", null)).toBeNull();
    // Every hidden language, in every country, 308s to the same page in English (query kept).
    for (const country of COUNTRY_SLUGS)
      for (const lang of ["nl", "de", "fr", "es", "it"]) {
        expect(routeLang(`/${country}/${lang}`, "", null)).toEqual({ redirect: `/${country}/en`, status: 308 });
        expect(routeLang(`/${country}/${lang}/compare`, "?ids=a,b", null)).toEqual({
          redirect: `/${country}/en/compare?ids=a,b`,
          status: 308,
        });
      }
    // /{country}: English, whatever the remembered language cookie says (temporary redirect).
    expect(routeLang("/de", "", null)).toEqual({ redirect: "/de/en", status: 307 });
    expect(routeLang("/de", "?range=300", "de")).toEqual({ redirect: "/de/en?range=300", status: 307 });
    expect(routeLang("/be/", "", "fr")).toEqual({ redirect: "/be/en", status: 307 });
    expect(routeLang("/es", "", "es")).toEqual({ redirect: "/es/en", status: 307 });
    expect(routeLang("/", "", "nl")).toEqual({ redirect: "/nl/en", status: 307 });
    expect(routeLang("/nl", "?range=300&lang=en", "nl")).toEqual({ redirect: "/nl/en?range=300", status: 308 });
    expect(routeLang("/nl", "?lang=nl", null)).toEqual({ redirect: "/nl/en", status: 307 });
    // Old URLs without a language segment: 308 to English; ?lang is dropped.
    expect(routeLang("/nl/ev/renault/zoe", "", null)).toEqual({ redirect: "/nl/en/ev/renault/zoe", status: 308 });
    expect(routeLang("/nl/compare", "?ids=a,b&lang=en", "nl")).toEqual({ redirect: "/nl/en/compare?ids=a,b", status: 308 });
    expect(routeLang("/be/learn/real-range", "?lang=fr", null)).toEqual({ redirect: "/be/en/learn/real-range", status: 308 });
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
    expect(getT("de")("compare.title")).toBe("Vergleichen");
    expect(getT("nl")("compare.printNote", { site: "S", release: 1 })).toBe("Afgedrukt van S, datarelease 1.");
    expect(getT("fr")("compare.printNote", { site: "S", release: 1 })).toBe("Imprimé depuis S, version des données 1.");
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

  describe("all six languages (T-117, REVIEW D6, A-35 B5)", () => {
    for (const [lang, dict] of Object.entries(DICTS)) {
      it(`${lang} has every public key`, () => {
        expect(PUBLIC_KEYS.filter((k) => !(k in dict))).toEqual([]);
      });

      it(`${lang} has no keys English lacks (except the _draft label)`, () => {
        expect(Object.keys(dict).filter((k) => k !== "_draft" && !(k in en))).toEqual([]);
      });

      it(`${lang} has no empty strings`, () => {
        expect(Object.entries(dict).filter(([, v]) => !v.trim()).map(([k]) => k)).toEqual([]);
      });

      it(`${lang} keeps every {placeholder} of the English string`, () => {
        const en2 = en as Record<string, string>;
        const bad = Object.entries(dict).filter(([k, v]) => k in en2 && placeholders(v).join() !== placeholders(en2[k]!).join());
        expect(bad.map(([k]) => k)).toEqual([]);
      });
    }

    it("DE, FR, ES and IT are labelled as drafts; EN and NL are not", () => {
      for (const l of DRAFT_LANGS) expect(DICTS[l]._draft, l).toMatch(/^DRAFT \(/);
      expect("_draft" in nl).toBe(false);
      expect("_draft" in en).toBe(false);
    });

    it("every glossary term has a label and tooltip in all six languages", () => {
      const file = path.resolve(__dirname, "../../../../data/taxonomy/glossary_terms.yaml");
      type Row = { id: string; label: Record<string, string>; short: Record<string, string> };
      const rows = (yaml.load(readFileSync(file, "utf8")) as { glossary_terms: Row[] }).glossary_terms;
      expect(rows.length).toBeGreaterThan(0);
      const gaps = rows.flatMap((r) =>
        LANGS.flatMap((l) => [!r.label[l]?.trim() ? `${r.id} label.${l}` : null, !r.short[l]?.trim() ? `${r.id} short.${l}` : null]).filter(Boolean),
      );
      expect(gaps).toEqual([]);
    });

    it("the draft label never reaches a page dictionary", () => {
      for (const l of LANGS) expect("_draft" in getDict(l)).toBe(false);
    });
  });
});
