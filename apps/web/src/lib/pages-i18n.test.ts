import { describe, expect, it } from "vitest";
import en from "@/i18n/pages.en.json";
import nl from "@/i18n/pages.nl.json";
import { hasPageKey, pagesT } from "./pages-i18n";
import { RANKING_IDS } from "./rankings";
import { SPEC_FIELDS, SPEC_GROUPS } from "./spec-diff";

describe("pages i18n", () => {
  it("English is complete; NL has no extra keys", () => {
    for (const v of Object.values(en)) expect(v.length).toBeGreaterThan(0);
    for (const k of Object.keys(nl)) expect(Object.keys(en)).toContain(k);
  });
  it("falls back to English key by key", () => {
    expect(pagesT("nl")("compare.title")).toBe("Vergelijken");
    expect(pagesT("de")("compare.title")).toBe(en["compare.title"]);
    expect(pagesT("nl")("compare.printNote", { site: "S", release: 1 })).toBe("Printed from S, data release 1.");
  });
  it("has a label for every spec field, group and ranking", () => {
    for (const f of SPEC_FIELDS) expect(hasPageKey(`field.${f.key}`), f.key).toBe(true);
    for (const g of SPEC_GROUPS) expect(hasPageKey(`variant.group.${g}`), g).toBe(true);
    for (const id of RANKING_IDS) for (const s of ["title", "short", "metric", "method"]) expect(hasPageKey(`top.${id}.${s}`)).toBe(true);
  });
});
