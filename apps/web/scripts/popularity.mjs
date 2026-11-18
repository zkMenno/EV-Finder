// Build-time inputs for the "Most popular" sort (T-130, Decision 038 blend). Reads
//   data/seed/top40.yaml           registration score per model (NL used fleet + UK fleet, WS1 pipeline)
//   data/editorial/menno-picks.yaml owner verdicts per generation (via owner-picks.mjs)
//   config/popularity.yaml          blend weights (never in code)
// and writes src/config/popularity.generated.json. The blend itself runs in src/lib/popularity.ts.
// YAML is parsed here only, so no YAML library reaches the bundles (same pattern as sources.mjs).
//
//   node scripts/popularity.mjs           write the JSON (runs before `next build` and `next dev`)
//   node scripts/popularity.mjs --check   fail if the committed JSON is out of date
/* global process, console */
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import * as yaml from "js-yaml";
import { PICKS_FILE, ownerNotes } from "./owner-picks.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
export const TOP40_FILE = path.resolve(here, "../../../data/seed/top40.yaml");
export const CONFIG_FILE = path.resolve(here, "../../../config/popularity.yaml");
export const OUT_FILE = path.resolve(here, "../src/config/popularity.generated.json");
const ID_RE = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const VERDICTS = ["shortlist", "consider", "fallback"];

const load = (file) => yaml.load(readFileSync(file, "utf8"), { schema: yaml.CORE_SCHEMA });
const num = (v) => (typeof v === "number" && Number.isFinite(v) ? v : null);

/** Validated blend config. Throws on anything the blend can't use. */
export function parseConfig(doc) {
  const w = doc?.weights ?? {};
  const reg = num(w.registrations);
  const picks = num(w.owner_picks);
  if (reg === null || picks === null || reg < 0 || picks < 0 || reg + picks <= 0) {
    throw new Error("popularity.yaml: weights.registrations and weights.owner_picks must be numbers ≥ 0, not both 0");
  }
  const pick_values = {};
  for (const v of VERDICTS) {
    const x = num(doc?.pick_values?.[v]);
    if (x === null || x < 0 || x > 1) throw new Error(`popularity.yaml: pick_values.${v} must be a number from 0 to 1`);
    pick_values[v] = x;
  }
  const bonus = num(doc?.favourite_bonus) ?? 0;
  if (bonus < 0 || bonus > 1) throw new Error("popularity.yaml: favourite_bonus must be from 0 to 1");
  return { registrations: reg, owner_picks: picks, pick_values, favourite_bonus: bonus };
}

/** model id → registration score (% share, top40 method), ranked and outside-top models together. */
export function registrationScores(doc) {
  const out = {};
  for (const m of [...(doc?.models ?? []), ...(doc?.seed_models_outside_top ?? [])]) {
    const id = m?.model_id;
    const s = num(m?.score_pct);
    if (typeof id !== "string" || !ID_RE.test(id) || s === null || s < 0) continue;
    out[id] = Math.max(out[id] ?? 0, s);
  }
  return Object.fromEntries(Object.keys(out).sort().map((k) => [k, out[k]]));
}

/** generation id → pick value 0..1: best verdict + favourite bonus, capped at 1. Unrated / ruled out → absent. */
export function pickScores(picksDoc, cfg) {
  const out = {};
  for (const [gen, notes] of Object.entries(ownerNotes(picksDoc).generations)) {
    let best = 0;
    for (const n of notes) {
      if (!n.verdict) continue;
      best = Math.max(best, Math.min(1, cfg.pick_values[n.verdict] + (n.favourite ? cfg.favourite_bonus : 0)));
    }
    if (best > 0) out[gen] = best;
  }
  return out;
}

export function buildPopularity(top40Doc, picksDoc, configDoc) {
  const cfg = parseConfig(configDoc);
  return {
    schema: "popularity-inputs/v1",
    weights: { registrations: cfg.registrations, owner_picks: cfg.owner_picks },
    inputs: {
      top40_generated_on: typeof top40Doc?.generated_on === "string" ? top40Doc.generated_on : null,
      picks_imported: typeof picksDoc?.source?.imported === "string" ? picksDoc.source.imported : null,
      registration_sources: ["rdw", "dft-veh"],
    },
    models: registrationScores(top40Doc),
    generations: pickScores(picksDoc, cfg),
  };
}

export function loadPopularity() {
  return buildPopularity(load(TOP40_FILE), load(PICKS_FILE), load(CONFIG_FILE));
}

export function serialize(x) {
  return JSON.stringify(x, null, 2) + "\n";
}

function main() {
  const check = process.argv.includes("--check");
  const missing = [TOP40_FILE, PICKS_FILE, CONFIG_FILE].filter((f) => !existsSync(f));
  if (missing.length) {
    // e.g. a Docker build context without data/ or config/: keep the committed JSON.
    if (check) throw new Error(`${missing.join(", ")} not found`);
    console.warn(`popularity: ${missing.map((f) => path.basename(f)).join(", ")} not found, keeping ${path.basename(OUT_FILE)}`);
    return;
  }
  const json = serialize(loadPopularity());
  const current = existsSync(OUT_FILE) ? readFileSync(OUT_FILE, "utf8") : "";
  if (check) {
    if (current !== json) {
      console.error("popularity: src/config/popularity.generated.json is out of date; run `node scripts/popularity.mjs`");
      process.exit(1);
    }
    return;
  }
  if (current !== json) writeFileSync(OUT_FILE, json);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
