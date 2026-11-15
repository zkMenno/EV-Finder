// Tiny i18n: JSON dictionaries, key-by-key fallback to English, {var} interpolation. No library.
import type { Lang } from "@/config/countries";
import de from "./de.json";
import en from "./en.json";
import es from "./es.json";
import fr from "./fr.json";
import it from "./it.json";
import nl from "./nl.json";

export type MsgKey = keyof typeof en;
export type Dict = Record<MsgKey, string>;
export type Vars = Record<string, string | number>;
export type T = (key: MsgKey, vars?: Vars) => string;

const PARTIAL: Record<Lang, Partial<Record<string, string>>> = { en, nl, de, fr, es, it };

const merged = new Map<Lang, Dict>();

/** Full dictionary for a language: its own strings, English for every missing key. */
export function getDict(lang: Lang): Dict {
  let d = merged.get(lang);
  if (!d) {
    d = { ...en } as Dict;
    for (const [k, v] of Object.entries(PARTIAL[lang])) {
      if (typeof v === "string" && v !== "" && k in en) d[k as MsgKey] = v;
    }
    merged.set(lang, d);
  }
  return d;
}

export function interpolate(s: string, vars?: Vars): string {
  if (!vars) return s;
  return s.replace(/\{(\w+)\}/g, (m, k: string) => (k in vars ? String(vars[k]) : m));
}

export function makeT(dict: Dict): T {
  return (key, vars) => interpolate(dict[key] ?? key, vars);
}

export function getT(lang: Lang): T {
  return makeT(getDict(lang));
}
