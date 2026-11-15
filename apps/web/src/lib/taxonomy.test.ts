import { describe, expect, it } from "vitest";
import { columnsFor } from "@/components/Explore";
import { catalogue, row, rows } from "@/test/helpers";
import { applyFilters } from "./filters";
import { defaultFilters } from "./state";
import { loc, localizeTaxonomy, voltageBounds } from "./taxonomy";

const f = (p: Partial<ReturnType<typeof defaultFilters>>) => ({ ...defaultFilters(), ...p });
const tax = catalogue.taxonomy!;

describe("taxonomy (Decision 010)", () => {
  it("localises with English fallback", () => {
    expect(loc({ en: "Air", nl: "Lucht" }, "nl")).toBe("Lucht");
    expect(loc({ en: "Air" }, "de")).toBe("Air");
    const ui = localizeTaxonomy(tax, "nl");
    expect(ui.coolings.find((c) => c.id === "liquid")?.label).toBe("Vloeistofkoeling");
    expect(ui.terms["real-range"]?.technical).toBeTruthy();
  });

  it("a new taxonomy row needs no code change", () => {
    const extra = {
      ...tax,
      chemistries: [...tax.chemistries, { id: "lmfp", family: "x", label: { en: "LMFP" }, status: "emerging" as const, charge_100_daily: true }],
    };
    const ui = localizeTaxonomy(extra, "en");
    expect(ui.chemistries.map((c) => c.id)).toContain("lmfp");
    const r = row({ variant_id: "x", chemistry_id: "lmfp" });
    expect(applyFilters([r], f({ chemistries: ["lmfp"] }), "NL")).toHaveLength(1);
  });

  it("voltage bounds come from the voltage class table", () => {
    expect(voltageBounds(localizeTaxonomy(tax, "en"))).toEqual([300, 1100]);
  });

  it("glossary related ids point at existing terms or taxonomy rows", () => {
    const ids = new Set([...tax.glossary_terms, ...tax.chemistries, ...tax.cooling_types, ...tax.voltage_classes].map((g) => g.id));
    for (const g of tax.glossary_terms) for (const r of g.related ?? []) expect(ids.has(r), `${g.id} → ${r}`).toBe(true);
  });

  it("row taxonomy ids exist in the tables (or are not-disclosed)", () => {
    const chem = new Set(tax.chemistries.map((c) => c.id));
    const cool = new Set(tax.cooling_types.map((c) => c.id));
    const volt = new Set(tax.voltage_classes.map((c) => c.id));
    for (const r of catalogue.rows) {
      if (r.chemistry_id && r.chemistry_id !== "not-disclosed") expect(chem.has(r.chemistry_id)).toBe(true);
      if (r.cooling_id && r.cooling_id !== "not-disclosed") expect(cool.has(r.cooling_id)).toBe(true);
      if (r.voltage_class_id && r.voltage_class_id !== "not-disclosed") expect(volt.has(r.voltage_class_id)).toBe(true);
    }
  });
});

describe("Decision 010 filters", () => {
  it("voltage class, fast on 400 V, charge to 100%", () => {
    const v800 = applyFilters(rows, f({ voltageClasses: ["800v"] }), "NL");
    expect(v800.length).toBeGreaterThan(0);
    expect(v800.every((r) => r.voltage_class_id === "800v")).toBe(true);
    expect(applyFilters(rows, f({ fast400: true }), "NL").every((r) => r.fast_on_400v === true)).toBe(true);
    const c100 = applyFilters(rows, f({ charge100: true }), "NL");
    expect(c100.length).toBeGreaterThan(0);
    expect(c100.every((r) => r.chemistry_id === "lfp")).toBe(true);
  });

  it("nominal voltage range excludes not-disclosed rows only while active", () => {
    const nd = row({ variant_id: "nd", voltage_class_id: "not-disclosed", voltage_nominal_v: null });
    expect(applyFilters([nd], defaultFilters(), "NL")).toHaveLength(1);
    expect(applyFilters([nd], f({ voltageMin: 300 }), "NL")).toHaveLength(0);
    expect(applyFilters([nd], f({ voltageClasses: ["not-disclosed"] }), "NL")).toHaveLength(1);
    const high = applyFilters(rows, f({ voltageMin: 600 }), "NL");
    expect(high.every((r) => (r.voltage_nominal_v ?? 0) >= 600)).toBe(true);
  });
});

describe("display levels", () => {
  it("simple has few columns, nerd the most", () => {
    const s = columnsFor("simple");
    const d = columnsFor("detailed");
    const n = columnsFor("nerd");
    expect(s.length).toBeLessThan(d.length);
    expect(d.length).toBeLessThan(n.length);
    expect(s).toEqual(["car", "years", "range", "dc", "price", "quality"]);
    expect(n).toContain("cool");
  });
});
