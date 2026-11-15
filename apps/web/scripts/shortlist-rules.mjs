// Build-time loader for the hero shortlist (T-080, Decisions 038 / 050 / 051): reads
// data/editorial/shortlist_rules.yaml (rules are rows, not code) and writes
// src/config/shortlist-rules.generated.json, a compact, validated form the browser scores with.
//
//   node scripts/shortlist-rules.mjs           write the JSON (runs before `next build` and `next dev`)
//   node scripts/shortlist-rules.mjs --check   fail if the committed JSON is out of date
//
// Only rule rows reach the browser: no `evidence`, no `sheet_field` values, never `sheet_values`
// (Decision 038). The Docker build context has no data/editorial, so there the committed JSON is
// kept (a unit test keeps it in step with the YAML), same as scripts/finance.mjs.
//
// Units: the app reads published fields. A factor whose `sheet_field` is `dc_km_per_h` is written in
// km per hour, so the published `dc_km_per_20min` is multiplied by 3; `consumption_kwh_100km` is
// compared in Wh/km (x10), as the rules file notes. Every other number is in the field's own unit.
/* global process, console */
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import yaml from "js-yaml";

const here = path.dirname(fileURLToPath(import.meta.url));
export const RULES_FILE = path.resolve(here, "../../../data/editorial/shortlist_rules.yaml");
export const OUT_FILE = path.resolve(here, "../src/config/shortlist-rules.generated.json");

/** Fields the web scorer understands, with how a value turns into a 0..1 score. */
const LINEAR_FIELDS = new Set([
  "dc_km_per_20min",
  "real_range_km",
  "boot_l",
  "consumption_kwh_100km",
  "ac_kw",
  "length_mm",
]);
const KIND_BY_FIELD = {
  heat_pump: "heat-pump",
  cooling_id: "cooling",
  fast_on_400v: "bool",
  charge_100_daily: "bool",
};
/** Fields the hero can filter on (filter presets). */
const PRESET_FIELDS = new Set([
  "dc_km_per_20min",
  "real_range_km",
  "boot_l",
  "length_mm",
  "ac_kw",
  "seats",
  "towing_kg",
]);

const isObj = (v) => v !== null && typeof v === "object" && !Array.isArray(v);
const isNum = (v) => typeof v === "number" && Number.isFinite(v);
const text = (v) =>
  isObj(v) ? Object.fromEntries(Object.entries(v).filter(([, s]) => typeof s === "string")) : {};

function transform(row) {
  if (row.field === "dc_km_per_20min" && row.sheet_field === "dc_km_per_h") return 3;
  if (row.field === "consumption_kwh_100km") return 10;
  return 1;
}

function factor(row, at, fail) {
  if (!isObj(row) || typeof row.id !== "string") return fail(`${at}: needs an id`);
  if (!isNum(row.weight) || row.weight <= 0) return fail(`${at} ${row.id}: weight must be > 0`);
  const base = { id: row.id, weight: row.weight, field: typeof row.field === "string" ? row.field : null };
  if (row.status === "gap" || row.field === "bidi") return { ...base, kind: "unknown" };
  if (KIND_BY_FIELD[row.field]) return { ...base, kind: KIND_BY_FIELD[row.field] };
  if (!LINEAR_FIELDS.has(row.field)) return fail(`${at} ${row.id}: field '${row.field}' has no web scorer`);
  if (!isNum(row.poor) || !isNum(row.great) || row.poor === row.great)
    return fail(`${at} ${row.id}: linear factor needs poor and great`);
  return { ...base, kind: "linear", scale: transform(row), poor: row.poor, great: row.great };
}

function gate(row, at, fail) {
  const min = row.min_km_per_h ?? row.min_km;
  if (!isObj(row) || typeof row.id !== "string" || !LINEAR_FIELDS.has(row.field) || !isNum(min))
    return fail(`${at}: gate needs id, a numeric field and a minimum`);
  const scale = row.min_km_per_h !== undefined && row.field === "dc_km_per_20min" ? 3 : transform(row);
  return {
    id: row.id,
    field: row.field,
    scale,
    min,
    rural_min: isNum(row.rural_min_km) ? row.rural_min_km : null,
    reason: text(row.reason),
  };
}

function presets(list, at, fail) {
  const out = [];
  for (const [i, p] of (list ?? []).entries()) {
    if (!isObj(p) || !PRESET_FIELDS.has(p.field) || (!isNum(p.min) && !isNum(p.max))) {
      fail(`${at}.filter_presets[${i}]: unknown field or no min/max`);
      continue;
    }
    out.push({
      field: p.field,
      ...(isNum(p.min) ? { min: p.min } : {}),
      ...(isNum(p.max) ? { max: p.max } : {}),
      why: text(p.why),
    });
  }
  return out;
}

function steps(v) {
  return isObj(v) ? Object.fromEntries(Object.entries(v).filter(([, n]) => isNum(n))) : {};
}

function penalty(p) {
  return {
    id: p.id,
    points: p.points,
    applies_with: typeof p.applies_with === "string" ? p.applies_with : null,
    rule: typeof p.rule === "string" ? p.rule : "",
  };
}

/** Validates the parsed YAML and returns the compact rules the browser uses. */
export function validateRules(doc) {
  const errors = [];
  const fail = (m) => {
    errors.push(m);
    return null;
  };
  if (!isObj(doc) || !Array.isArray(doc.profiles)) throw new Error("profiles must be a list");
  const picker = (doc.picker ?? []).map((q) => ({
    id: q.id,
    answers: q.answers,
    ...(isObj(q.skip_if) ? { skip_if: q.skip_if } : {}),
  }));
  const answers = Object.fromEntries(picker.map((q) => [q.id, new Set(q.answers)]));
  const checkPicker = (p, at) => {
    for (const [q, vals] of Object.entries(isObj(p) ? p : {}))
      for (const v of vals) if (!answers[q]?.has(v)) fail(`${at}: picker ${q} has unknown answer '${v}'`);
    return isObj(p) ? p : {};
  };
  const profiles = doc.profiles.map((p, i) => {
    const at = `profiles[${i}] ${p.id}`;
    const factors = (p.factors ?? []).map((f, j) => factor(f, `${at}.factors[${j}]`, fail)).filter(Boolean);
    const extra = (p.extra_factors ?? []).map((f, j) => factor(f, `${at}.extra_factors[${j}]`, fail)).filter(Boolean);
    const ids = new Set(factors.map((f) => f.id));
    const bands = isObj(p.bands) ? p.bands : {};
    if (!p.combines_with && !isObj(bands.default) && !isObj(bands["400v"]))
      fail(`${at}: needs bands`);
    return {
      id: p.id,
      layer: Array.isArray(p.combines_with),
      picker: checkPicker(p.picker, at),
      label: text(p.label),
      short: text(p.short),
      calibrated: typeof p.calibration === "string" && /back-tested on/i.test(p.calibration),
      calibration: typeof p.calibration === "string" ? p.calibration : "",
      bands,
      gates: (p.gates ?? []).map((g, j) => gate(g, `${at}.gates[${j}]`, fail)).filter(Boolean),
      factors,
      extra_factors: extra,
      weight_steps: steps(p.weight_steps),
      bonuses: (p.bonuses ?? [])
        .filter((b) => isNum(b.points))
        .map((b) => ({ id: b.id, points: b.points })),
      penalties: (p.penalties ?? []).filter((x) => isNum(x.points)).map(penalty),
      filter_presets: presets(p.filter_presets, at, fail),
      ...(typeof p.sort_default === "string" ? { sort_default: p.sort_default } : {}),
      _ids: ids,
    };
  });
  const allFactorIds = new Set(profiles.flatMap((p) => [...p._ids, ...p.extra_factors.map((f) => f.id)]));
  const modifiers = (doc.modifiers ?? []).map((m, i) => ({
    id: m.id,
    picker: checkPicker(m.picker, `modifiers[${i}] ${m.id}`),
    label: text(m.label),
    weight_steps: steps(m.weight_steps),
    use_rural_gates: m.use_rural_gates === true,
    penalties: (m.penalties ?? []).filter((x) => isNum(x.points)).map(penalty),
  }));
  const addons = (doc.addons ?? []).map((a) => ({ id: a.id, label: text(a.label), weight_steps: steps(a.weight_steps) }));
  for (const g of [...profiles, ...modifiers, ...addons])
    for (const s of Object.keys(g.weight_steps))
      if (!allFactorIds.has(s)) fail(`${g.id}: weight step '${s}' names no factor`);
  if (errors.length) throw new Error(errors.join("\n"));
  return {
    schema: "web-shortlist-rules/v1",
    review: doc.review === true,
    weight_step_factor: isNum(doc.weight_step_factor) ? doc.weight_step_factor : 1.5,
    picker,
<<<<<<< HEAD
    profiles: profiles.map((p) => {
      const rest = { ...p };
      delete rest._ids;
      return rest;
    }),
=======
    profiles: profiles.map(({ _ids, ...rest }) => rest),
>>>>>>> c1958ab8272ae425c4d17796e1e54e6ffd02ef9a
    modifiers,
    addons,
  };
}

export function loadRules(file = RULES_FILE) {
  return validateRules(yaml.load(readFileSync(file, "utf8"), { schema: yaml.CORE_SCHEMA }));
}

export function serialize(config) {
  return JSON.stringify(config, null, 2) + "\n";
}

function main() {
  const check = process.argv.includes("--check");
  if (!existsSync(RULES_FILE)) {
    if (check) throw new Error(`${RULES_FILE} not found`);
    console.warn(`shortlist-rules: ${RULES_FILE} not found, keeping ${path.basename(OUT_FILE)}`);
    return;
  }
  const json = serialize(loadRules());
  const current = existsSync(OUT_FILE) ? readFileSync(OUT_FILE, "utf8") : "";
  if (check) {
    if (current !== json) {
      console.error("shortlist-rules: src/config/shortlist-rules.generated.json is out of date; run `node scripts/shortlist-rules.mjs`");
      process.exit(1);
    }
    return;
  }
  if (current !== json) writeFileSync(OUT_FILE, json);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
