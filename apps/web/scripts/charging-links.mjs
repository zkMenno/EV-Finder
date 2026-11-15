// Build-time loader for the "Find a charger / plan a trip" link-out block (T-026, spec tab
// "Charging buildout": What we build, Link rules). Reads the optional `charging_links` list in
// config/countries/<country>.yaml (written by T-024), validates it and writes
// src/config/charging-links.generated.json, which the server imports (no YAML at runtime).
// A country without `charging_links` gets an empty list and the block renders nothing.
//
//   node scripts/charging-links.mjs           write the JSON (runs before `next build` and `next dev`)
//   node scripts/charging-links.mjs --check   fail if the committed JSON is out of date
//
// Pure links: no API keys, no affiliate tags, no tracking ids beyond our own UTM tag (added at
// render time in src/lib/charging-links.ts).
/* global process, console, URL */
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import yaml from "js-yaml";
import { COUNTRIES, CONFIG_DIR } from "./listings.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
export const OUT_FILE = path.resolve(here, "../src/config/charging-links.generated.json");
export const MAX_LINKS = 5;

const LINK_KEYS = new Set(["job", "label", "url", "order", "tool", "official", "utm", "deep_link_template", "note"]);
// Same guard as listings.mjs (Decision 004): no partner, affiliate or secret config in the public repo.
const FORBIDDEN = /(rate|sampl|affiliate|partner|token|secret|api[_-]?key|password|cookie|proxy)/i;
const ID_RE = /^[a-z0-9][a-z0-9-]*$/;

const isObj = (v) => v !== null && typeof v === "object" && !Array.isArray(v);

/** Validates one country's `charging_links` (may be undefined); returns the sorted list or throws. */
export function validateChargingLinks(country, list) {
  if (list === undefined || list === null) return [];
  const errors = [];
  const fail = (m) => errors.push(`${country}: charging_links${m}`);
  if (!Array.isArray(list)) throw new Error(`${country}: charging_links must be a list`);
  if (list.length > MAX_LINKS) fail(`: at most ${MAX_LINKS} links (spec Link rules), found ${list.length}`);
  const out = [];
  const seen = new Set();
  for (const [i, l] of list.entries()) {
    const at = `[${i}]`;
    if (!isObj(l)) {
      fail(`${at} must be a mapping`);
      continue;
    }
    for (const k of Object.keys(l)) {
      if (!LINK_KEYS.has(k)) fail(`${at}: unknown key "${k}"`);
      if (FORBIDDEN.test(k)) fail(`${at}: "${k}" looks like private config (Decision 004)`);
    }
    if (typeof l.job !== "string" || !ID_RE.test(l.job)) fail(`${at}: job must be a lowercase id`);
    if (typeof l.label !== "string" || !l.label.trim()) fail(`${at}: label is required`);
    if (typeof l.order !== "number" || !Number.isFinite(l.order)) fail(`${at}: order must be a number`);
    if (l.tool !== undefined && (typeof l.tool !== "string" || !ID_RE.test(l.tool))) fail(`${at}: tool must be a lowercase id`);
    for (const k of ["official", "utm"]) if (l[k] !== undefined && typeof l[k] !== "boolean") fail(`${at}: ${k} must be true or false`);
    if (l.deep_link_template !== undefined && l.deep_link_template !== null && typeof l.deep_link_template !== "string") fail(`${at}: deep_link_template must be a string`);
    if (typeof l.url !== "string" || !l.url.startsWith("https://")) fail(`${at}: url must be an https URL`);
    else {
      try {
        const u = new URL(l.url);
        if (u.username || u.password) fail(`${at}: no credentials in URLs`);
        for (const k of u.searchParams.keys()) if (FORBIDDEN.test(k)) fail(`${at}: query "${k}" looks like private config (Decision 004)`);
        const key = u.href;
        if (seen.has(key)) fail(`${at}: duplicate url ${key}`);
        seen.add(key);
      } catch {
        fail(`${at}: url is not a valid URL`);
      }
    }
    out.push({
      job: l.job,
      label: typeof l.label === "string" ? l.label.trim() : "",
      url: l.url,
      order: l.order,
      tool: l.tool ?? null,
      official: l.official === true,
      utm: l.utm !== false,
    });
  }
  if (errors.length) throw new Error(errors.join("\n"));
  return out.sort((a, b) => a.order - b.order);
}

/** Reads every supported country's file; a missing file or missing key means no links. */
export function loadChargingLinks(dir = CONFIG_DIR) {
  const out = {};
  for (const c of COUNTRIES) {
    const p = path.join(dir, `${c}.yaml`);
    const doc = existsSync(p) ? yaml.load(readFileSync(p, "utf8"), { schema: yaml.CORE_SCHEMA }) : null;
    out[c] = validateChargingLinks(c, isObj(doc) ? doc.charging_links : undefined);
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
    console.warn(`charging-links: ${CONFIG_DIR} not found, keeping ${path.basename(OUT_FILE)}`);
    return;
  }
  const json = serialize(loadChargingLinks());
  const current = existsSync(OUT_FILE) ? readFileSync(OUT_FILE, "utf8") : "";
  if (check) {
    if (current !== json) {
      console.error("charging-links: src/config/charging-links.generated.json is out of date; run `node scripts/charging-links.mjs`");
      process.exit(1);
    }
    return;
  }
  if (current !== json) writeFileSync(OUT_FILE, json);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
