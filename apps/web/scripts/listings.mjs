// Build-time loader for the "See listings" config (config/countries/<country>.yaml at the repo root).
// Validates every file and writes src/config/listings.generated.json, which the server imports.
// YAML is parsed here only, so no YAML library ever reaches the server or client bundles.
//
//   node scripts/listings.mjs           write the JSON (runs before `next build` and `next dev`)
//   node scripts/listings.mjs --check   fail if the committed JSON is out of date
//
// Decision 004: public search URLs only. Sampling targets, rates and partner ids never go here.
/* global process, console, URL */
import { existsSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import yaml from "js-yaml";

const here = path.dirname(fileURLToPath(import.meta.url));
export const CONFIG_DIR = path.resolve(here, "../../../config/countries");
export const OUT_FILE = path.resolve(here, "../src/config/listings.generated.json");

export const COUNTRIES = ["nl", "de", "fr", "be", "uk"];
const PLACEHOLDERS = new Set(["make", "model", "makeName", "modelName", "MAKE", "MODEL"]);
const FILTERS = new Set(["electric"]);
const SITE_KEYS = new Set(["site", "label", "url_template", "filters", "slug_overrides", "priority", "verified"]);
// Keys that would mean private sampling/partner config leaked into the public repo (Decision 004).
const FORBIDDEN = /(rate|sampl|affiliate|partner|token|secret|api[_-]?key|password|cookie|proxy)/i;

const isObj = (v) => v !== null && typeof v === "object" && !Array.isArray(v);
const isStrMap = (v) => isObj(v) && Object.entries(v).every(([k, s]) => k !== "" && typeof s === "string" && s !== "");

/** Validates one parsed country file; returns the normalised site list or throws with every problem. */
export function validateCountry(country, doc) {
  const errors = [];
  const fail = (m) => errors.push(`${country}: ${m}`);
  if (!isObj(doc)) throw new Error(`${country}: file must be a mapping`);
  if (doc.country !== country) fail(`country must be "${country}"`);
  for (const k of Object.keys(doc)) if (k !== "country" && k !== "listings") fail(`unknown top-level key "${k}"`);
  if (!Array.isArray(doc.listings)) fail("listings must be a list");
  const seen = new Set();
  const sites = [];
  for (const [i, s] of (Array.isArray(doc.listings) ? doc.listings : []).entries()) {
    const at = `listings[${i}]`;
    if (!isObj(s)) {
      fail(`${at} must be a mapping`);
      continue;
    }
    for (const k of Object.keys(s)) {
      if (!SITE_KEYS.has(k)) fail(`${at}: unknown key "${k}"`);
      if (FORBIDDEN.test(k)) fail(`${at}: "${k}" looks like private config (Decision 004)`);
    }
    if (typeof s.site !== "string" || !/^[a-z0-9][a-z0-9-]*$/.test(s.site)) fail(`${at}: site must be a lowercase id`);
    else if (seen.has(s.site)) fail(`${at}: duplicate site "${s.site}"`);
    else seen.add(s.site);
    if (typeof s.label !== "string" || !s.label.trim()) fail(`${at}: label is required`);
    if (typeof s.priority !== "number" || !Number.isFinite(s.priority)) fail(`${at}: priority must be a number`);
    if (typeof s.verified !== "boolean") fail(`${at}: verified must be true or false`);
    const t = s.url_template;
    if (typeof t !== "string" || !t.startsWith("https://")) fail(`${at}: url_template must be an https URL`);
    else {
      for (const m of t.matchAll(/\{([^}]*)\}/g)) if (!PLACEHOLDERS.has(m[1])) fail(`${at}: unknown placeholder {${m[1]}}`);
      try {
        const u = new URL(t.replace(/\{[^}]*\}/g, "x"));
        if (u.username || u.password) fail(`${at}: no credentials in URLs`);
        for (const k of u.searchParams.keys()) if (FORBIDDEN.test(k)) fail(`${at}: query "${k}" looks like private config (Decision 004)`);
      } catch {
        fail(`${at}: url_template is not a valid URL`);
      }
    }
    const filters = s.filters ?? {};
    if (!isObj(filters)) fail(`${at}: filters must be a mapping`);
    else
      for (const [f, params] of Object.entries(filters)) {
        if (!FILTERS.has(f)) fail(`${at}: unknown filter "${f}"`);
        if (!isStrMap(params)) fail(`${at}: filters.${f} must map query names to non-empty strings`);
        else for (const k of Object.keys(params)) if (FORBIDDEN.test(k)) fail(`${at}: query "${k}" looks like private config (Decision 004)`);
      }
    const overrides = s.slug_overrides ?? {};
    if (!isStrMap(overrides) && !(isObj(overrides) && Object.keys(overrides).length === 0)) fail(`${at}: slug_overrides must map slugs to slugs`);
    sites.push({
      site: s.site,
      label: s.label,
      url_template: t,
      filters: isObj(filters) ? filters : {},
      slug_overrides: isObj(overrides) ? overrides : {},
      priority: s.priority,
      verified: s.verified,
    });
  }
  if (errors.length) throw new Error(errors.join("\n"));
  return sites.sort((a, b) => a.priority - b.priority);
}

/** Reads and validates config/countries/*.yaml: one file per supported country, nothing else. */
export function loadListingConfig(dir = CONFIG_DIR) {
  const files = readdirSync(dir).filter((f) => f.endsWith(".yaml") || f.endsWith(".yml"));
  const extra = files.filter((f) => !COUNTRIES.includes(f.replace(/\.ya?ml$/, "")));
  if (extra.length) throw new Error(`unknown country files: ${extra.join(", ")}`);
  const out = {};
  for (const c of COUNTRIES) {
    const p = path.join(dir, `${c}.yaml`);
    if (!existsSync(p)) throw new Error(`${c}: missing ${p}`);
    out[c] = validateCountry(c, yaml.load(readFileSync(p, "utf8"), { schema: yaml.CORE_SCHEMA }));
  }
  return out;
}

export function serialize(config) {
  return JSON.stringify(config, null, 2) + "\n";
}

function main() {
  const check = process.argv.includes("--check");
  if (!existsSync(CONFIG_DIR)) {
    // e.g. a build context without the repo-level config: keep the committed JSON.
    if (check) throw new Error(`${CONFIG_DIR} not found`);
    console.warn(`listings: ${CONFIG_DIR} not found, keeping ${path.basename(OUT_FILE)}`);
    return;
  }
  const json = serialize(loadListingConfig());
  const current = existsSync(OUT_FILE) ? readFileSync(OUT_FILE, "utf8") : "";
  if (check) {
    if (current !== json) {
      console.error("listings: src/config/listings.generated.json is out of date; run `node scripts/listings.mjs`");
      process.exit(1);
    }
    return;
  }
  if (current !== json) writeFileSync(OUT_FILE, json);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
