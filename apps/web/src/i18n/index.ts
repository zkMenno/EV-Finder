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

/**
 * Key prefixes only server-rendered pages use (model, compare and ranking pages, staff pages).
 * They are left out of the dictionary handed to client components (Explore, CompareTray), so the
 * page payload doesn't grow with every server page. A client component must not use these keys.
 */
export const SERVER_ONLY_PREFIXES = ["about.", "crumb.", "model.", "gen.", "listings.", "reg.", "variant.", "field.", "drivetrain.", "top.", "staff."] as const;

const clientDicts = new Map<Lang, Dict>();

/** Dictionary for client components: the full dictionary minus SERVER_ONLY_PREFIXES keys. */
export function getClientDict(lang: Lang): Dict {
  let d = clientDicts.get(lang);
  if (!d) {
    const full = getDict(lang);
    // Typed as Dict for the client components' t(); the dropped keys are server-only (see above).
    d = Object.fromEntries(Object.entries(full).filter(([k]) => !SERVER_ONLY_PREFIXES.some((p) => k.startsWith(p)))) as Dict;
    clientDicts.set(lang, d);
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

/** For keys built at runtime (e.g. `field.${key}`): true when the English dictionary has it. */
export function hasMsgKey(key: string): key is MsgKey {
  return Object.prototype.hasOwnProperty.call(en, key);
}

export function getT(lang: Lang): T {
  return makeT(getDict(lang));
}
