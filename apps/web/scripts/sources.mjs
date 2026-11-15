// Build-time loader for the source registry (data/sources.yaml at the repo root), used by the
// About / credits page as the attribution fallback when a release's `sources` entry lacks one.
// Writes src/config/sources.generated.json, which only server code imports. YAML is parsed
// here only, so no YAML library reaches the server or client bundles (same pattern as listings.mjs).
//
//   node scripts/sources.mjs           write the JSON (runs before `next build` and `next dev`)
//   node scripts/sources.mjs --check   fail if the committed JSON is out of date
/* global process, console */
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import * as yaml from "js-yaml";

const here = path.dirname(fileURLToPath(import.meta.url));
export const SOURCES_FILE = path.resolve(here, "../../../data/sources.yaml");
export const OUT_FILE = path.resolve(here, "../src/config/sources.generated.json");

const isObj = (v) => v !== null && typeof v === "object" && !Array.isArray(v);
const str = (v) => (typeof v === "string" && v.trim() ? v.trim() : undefined);

/**
 * Required attribution wording for one registry entry: an explicit `attribution:` field, else the
 * quoted text in `terms` that the registry marks as attribution ("attribution '…' required",
 * "visible attribution to '…'"), else a `terms` that starts with a quoted notice ("'Contains …'").
 */
export function attributionOf(entry) {
  const explicit = str(entry.attribution);
  if (explicit) return explicit;
  const terms = str(entry.terms);
  if (!terms) return undefined;
  const marked = terms.match(/attribution(?:\s+to)?\s+'([^']+)'/i);
  if (marked) return marked[1].trim();
  const leading = terms.match(/^'([^']+)'/);
  if (leading) return leading[1].trim();
  return undefined;
}

/** Parsed registry → { id: { name, owner?, licence, status, url?, attribution? } }, sorted by id. */
export function buildRegistry(doc) {
  if (!isObj(doc) || !Array.isArray(doc.sources)) throw new Error("sources.yaml: expected a mapping with a `sources` list");
  const out = {};
  for (const [i, s] of doc.sources.entries()) {
    if (!isObj(s) || !str(s.id) || !str(s.name) || !str(s.licence)) throw new Error(`sources.yaml: sources[${i}] needs id, name and licence`);
    if (out[s.id]) throw new Error(`sources.yaml: duplicate id "${s.id}"`);
    const entry = { name: str(s.name), licence: str(s.licence), status: str(s.status) ?? "unknown" };
    const owner = str(s.owner);
    if (owner) entry.owner = owner;
    const url = str(s.url);
    if (url) entry.url = url;
    const attribution = attributionOf(s);
    if (attribution) entry.attribution = attribution;
    out[s.id] = entry;
  }
  return Object.fromEntries(Object.entries(out).sort(([a], [b]) => a.localeCompare(b)));
}

export function loadRegistry(file = SOURCES_FILE) {
  return buildRegistry(yaml.load(readFileSync(file, "utf8"), { schema: yaml.CORE_SCHEMA }));
}

export function serialize(registry) {
  return JSON.stringify(registry, null, 2) + "\n";
}

function main() {
  const check = process.argv.includes("--check");
  if (!existsSync(SOURCES_FILE)) {
    // e.g. a Docker build context without data/: keep the committed JSON.
    if (check) throw new Error(`${SOURCES_FILE} not found`);
    console.warn(`sources: ${SOURCES_FILE} not found, keeping ${path.basename(OUT_FILE)}`);
    return;
  }
  const json = serialize(loadRegistry());
  const current = existsSync(OUT_FILE) ? readFileSync(OUT_FILE, "utf8") : "";
  if (check) {
    if (current !== json) {
      console.error("sources: src/config/sources.generated.json is out of date; run `node scripts/sources.mjs`");
      process.exit(1);
    }
    return;
  }
  if (current !== json) writeFileSync(OUT_FILE, json);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
