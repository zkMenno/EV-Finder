// Taxonomy tables (Decision 010) localised for the UI. Everything is read from data:
// adding a voltage class, chemistry, cooling type or glossary term needs no code change.
import type { Taxonomy } from "@ev/schema";
import type { Lang } from "@/config/countries";

/** Generated types key these by string; the schema requires `en`. */
type LangMap = { [k: string]: string | undefined };

/** Per-language string with English fallback. */
export function loc(m: LangMap | undefined, lang: Lang): string {
  if (!m) return "";
  return m[lang] || m.en || "";
}

export interface UiOption {
  id: string;
  label: string;
  explainer?: string;
}
export interface UiChemistry extends UiOption {
  pros: string[];
  cons: string[];
  care: string[];
  charge100: boolean | null;
}
export interface UiVoltageClass extends UiOption {
  minV: number;
  maxV: number;
}
export interface UiTerm {
  id: string;
  label: string;
  technical?: string;
  short: string;
}
export interface UiTaxonomy {
  voltageClasses: UiVoltageClass[];
  chemistries: UiChemistry[];
  coolings: UiOption[];
  terms: Record<string, UiTerm>;
}

export function localizeTaxonomy(t: Taxonomy, lang: Lang): UiTaxonomy {
  const opt = (x: { id: string; label: LangMap; explainer?: LangMap }): UiOption => ({
    id: x.id,
    label: loc(x.label, lang),
    ...(x.explainer ? { explainer: loc(x.explainer, lang) } : {}),
  });
  return {
    voltageClasses: t.voltage_classes.map((v) => ({ ...opt(v), minV: v.min_v, maxV: v.max_v })),
    chemistries: t.chemistries.map((c) => ({
      ...opt(c),
      pros: (c.pros ?? []).map((x) => loc(x, lang)),
      cons: (c.cons ?? []).map((x) => loc(x, lang)),
      care: (c.care_tips ?? []).map((x) => loc(x, lang)),
      charge100: c.charge_100_daily,
    })),
    coolings: t.cooling_types.map(opt),
    terms: Object.fromEntries(
      t.glossary_terms.map((g) => [
        g.id,
        {
          id: g.id,
          label: loc(g.label, lang),
          ...(g.technical ? { technical: loc(g.technical, lang) } : {}),
          short: loc(g.short, lang),
        },
      ]),
    ),
  };
}

/** Slider bounds for nominal voltage, from the voltage class table. */
export function voltageBounds(t: UiTaxonomy): [number, number] {
  if (!t.voltageClasses.length) return [0, 1000];
  return [Math.min(...t.voltageClasses.map((v) => v.minV)), Math.max(...t.voltageClasses.map((v) => v.maxV))];
}
