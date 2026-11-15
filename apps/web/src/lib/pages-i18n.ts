// Strings for the model, compare and ranking pages (T-009/010/011). Kept apart from the main
// dictionaries while another lane owns them; falls back to English key by key.
import type { Lang } from "@/config/countries";
import { interpolate, type Vars } from "@/i18n";
import en from "@/i18n/pages.en.json";
import nl from "@/i18n/pages.nl.json";

export type PageKey = keyof typeof en;
export type PT = (key: PageKey, vars?: Vars) => string;

const DICTS: Partial<Record<Lang, Partial<Record<string, string>>>> = { en, nl };

export function pagesT(lang: Lang): PT {
  const own = DICTS[lang] ?? {};
  return (key, vars) => {
    const s = own[key];
    return interpolate(typeof s === "string" && s !== "" ? s : en[key], vars);
  };
}

/** Lookup for keys built at runtime (e.g. `field.${key}`); unknown keys return the fallback. */
export function hasPageKey(key: string): key is PageKey {
  return Object.prototype.hasOwnProperty.call(en, key);
}
