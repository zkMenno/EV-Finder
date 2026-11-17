// Build-time loader for the owner's notes (T-067, Decision 038): reads data/editorial/menno-picks.yaml
// and writes src/config/owner-notes.generated.json, keyed by catalogue generation id. Only the verdict,
// favourite flag and Menno's own note reach the app (CC BY, his words); `sheet_values` never do.
//
//   node scripts/owner-picks.mjs           write the JSON (runs before `next build` and `next dev`)
//   node scripts/owner-picks.mjs --check   fail if the committed JSON is out of date
/* global process, console */
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import * as yaml from "js-yaml";

const here = path.dirname(fileURLToPath(import.meta.url));
export const PICKS_FILE = path.resolve(here, "../../../data/editorial/menno-picks.yaml");
export const OUT_FILE = path.resolve(here, "../src/config/owner-notes.generated.json");
const VERDICTS = new Set(["shortlist", "consider", "fallback"]);
const ID_RE = /^[a-z0-9]+(-[a-z0-9]+)*$/;

/** Picks linked to a catalogue generation → { generations: { id: notes[] } }. */
export function ownerNotes(doc) {
  const out = {};
  for (const e of doc?.primary_car_picks ?? []) {
    const gen = e?.seed_generation_id;
    if (typeof gen !== "string" || !ID_RE.test(gen)) continue;
    const verdict = VERDICTS.has(e.verdict) ? e.verdict : null;
    const note = typeof e.notes === "string" && e.notes.trim() ? e.notes.trim() : null;
    if (!verdict && !note) continue;
    (out[gen] ??= []).push({
      model_year: Number.isInteger(e.model_year) ? e.model_year : null,
      variant: typeof e.variant === "string" ? e.variant : null,
      verdict,
      favourite: e.favourite === true,
      note,
    });
  }
  for (const list of Object.values(out)) list.sort((a, b) => (b.model_year ?? 0) - (a.model_year ?? 0));
  return {
    imported: typeof doc?.source?.imported === "string" ? doc.source.imported : null,
    generations: Object.fromEntries(Object.keys(out).sort().map((k) => [k, out[k]])),
  };
}

export function loadOwnerNotes(file = PICKS_FILE) {
  return ownerNotes(yaml.load(readFileSync(file, "utf8"), { schema: yaml.CORE_SCHEMA }));
}

export function serialize(config) {
  return JSON.stringify(config, null, 2) + "\n";
}

function main() {
  const check = process.argv.includes("--check");
  if (!existsSync(PICKS_FILE)) {
    if (check) throw new Error(`${PICKS_FILE} not found`);
    console.warn(`owner-picks: ${PICKS_FILE} not found, keeping ${path.basename(OUT_FILE)}`);
    return;
  }
  const json = serialize(loadOwnerNotes());
  const current = existsSync(OUT_FILE) ? readFileSync(OUT_FILE, "utf8") : "";
  if (check) {
    if (current !== json) {
      console.error("owner-picks: src/config/owner-notes.generated.json is out of date; run `node scripts/owner-picks.mjs`");
      process.exit(1);
    }
    return;
  }
  if (current !== json) writeFileSync(OUT_FILE, json);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
