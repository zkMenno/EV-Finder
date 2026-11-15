// Build-time loader for each country's UI languages (Decision 015): reads `languages` and
// `default_language` from config/countries/<country>.yaml, validates them and writes
// src/config/countries.generated.json, which src/config/countries.ts imports (client-safe, tiny).
// Served languages = the country's own languages + English (until translations are reviewed).
//
//   node scripts/countries.mjs           write the JSON (runs before `next build` and `next dev`)
//   node scripts/countries.mjs --check   fail if the committed JSON is out of date
/* global process, console */
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import yaml from "js-yaml";
import { COUNTRIES, CONFIG_DIR } from "./listings.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
export const OUT_FILE = path.resolve(here, "../src/config/countries.generated.json");
export const LANGS = ["en", "nl", "de", "fr", "es", "it"];

const isObj = (v) => v !== null && typeof v === "object" && !Array.isArray(v);

/** Validates one parsed country file's language keys; returns { languages, default_language, served }. */
export function validateLanguages(country, doc) {
  const errors = [];
  const fail = (m) => errors.push(`${country}: ${m}`);
  if (!isObj(doc)) throw new Error(`${country}: file must be a mapping`);
  const langs = doc.languages;
  if (!Array.isArray(langs) || langs.length === 0) fail("languages must be a non-empty list");
  const list = Array.isArray(langs) ? langs : [];
  for (const l of list)
    if (!LANGS.includes(l)) fail(`languages: "${l}" is not one of ${LANGS.join(", ")}`);
  if (new Set(list).size !== list.length) fail("languages has duplicates");
  const def = doc.default_language;
  if (typeof def !== "string" || !list.includes(def))
    fail(`default_language must be one of languages (${list.join(", ")})`);
  if (errors.length) throw new Error(errors.join("\n"));
  const served = [...list, ...(list.includes("en") ? [] : ["en"])];
  return { languages: list, default_language: def, served };
}

export function loadCountryLanguages(dir = CONFIG_DIR) {
  const out = {};
  for (const c of COUNTRIES) {
    const p = path.join(dir, `${c}.yaml`);
    if (!existsSync(p)) throw new Error(`${c}: ${p} not found`);
    out[c] = validateLanguages(c, yaml.load(readFileSync(p, "utf8"), { schema: yaml.CORE_SCHEMA }));
  }
  return out;
}

export function serialize(config) {
  return JSON.stringify(config, null, 2) + "\n";
}

function main() {
  const check = process.argv.includes("--check");
  if (!existsSync(CONFIG_DIR)) {
    if (check) throw new Error(`${CONFIG_DIR} not found`);
    console.warn(`countries: ${CONFIG_DIR} not found, keeping ${path.basename(OUT_FILE)}`);
    return;
  }
  const json = serialize(loadCountryLanguages());
  const current = existsSync(OUT_FILE) ? readFileSync(OUT_FILE, "utf8") : "";
  if (check) {
    if (current !== json) {
      console.error(
        "countries: src/config/countries.generated.json is out of date; run `node scripts/countries.mjs`",
      );
      process.exit(1);
    }
    return;
  }
  if (current !== json) writeFileSync(OUT_FILE, json);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
