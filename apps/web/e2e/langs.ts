// Decision 082: English only at launch. Specs that test other languages (translations, the
// language banner and picker, per-language layout) skip while config serves English only, and
// switch back on by themselves once a country lists its languages again in config/countries/.
import { readFileSync } from "node:fs";

type LangCfg = Record<string, { served: string[] }>;
const cfg = JSON.parse(
  readFileSync(new URL("../src/config/countries.generated.json", import.meta.url), "utf8"),
) as LangCfg;

/** Every country served in English only (Decision 082)? */
export const ENGLISH_ONLY = Object.values(cfg).every((c) => c.served.length === 1 && c.served[0] === "en");
export const ENGLISH_ONLY_REASON = "Decision 082: English only at launch; other languages are hidden, not deleted";

/** Served country/language pairs from config, e.g. "nl/en". */
export const SERVED_ROUTES = Object.entries(cfg).flatMap(([c, v]) => v.served.map((l) => `${c}/${l}`));

/** The seven launch countries (config order). */
export const COUNTRIES = Object.keys(cfg);
