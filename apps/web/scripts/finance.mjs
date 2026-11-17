// Build-time loader for the price-mode calculator (Decision 017, T-043): reads
// data/taxonomy/finance_profiles.yaml (rows = schema FinanceProfile), validates the fields the
// web app relies on and writes src/config/finance.generated.json, keyed by country code. Only the
// server imports it (pages pass one country's profile to client components as a prop).
//
//   node scripts/finance.mjs           write the JSON (runs before `next build` and `next dev`)
//   node scripts/finance.mjs --check   fail if the committed JSON is out of date
//
// The Docker build context has no data/taxonomy, so there the committed JSON is kept (a unit
// test keeps it in step with the YAML), same as scripts/sources.mjs.
/* global process, console */
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import * as yaml from "js-yaml";

const here = path.dirname(fileURLToPath(import.meta.url));
export const FINANCE_FILE = path.resolve(here, "../../../data/taxonomy/finance_profiles.yaml");
export const OUT_FILE = path.resolve(here, "../src/config/finance.generated.json");
export const COUNTRY_CODES = ["NL", "DE", "FR", "BE", "UK", "ES", "IT"]; // ES, IT: Decision 066 (T-118)
/** The calculator only handles this product today; lease has no figures (Decision 017). */
export const PRODUCT = "used-car-loan";

const isObj = (v) => v !== null && typeof v === "object" && !Array.isArray(v);
const numOrNull = (v, min, max) =>
  v === null || (typeof v === "number" && Number.isFinite(v) && v >= min && v <= max);

/** Validates the parsed YAML and returns { [country]: profile } for PRODUCT rows. */
export function validateFinance(doc) {
  const errors = [];
  const fail = (m) => errors.push(m);
  if (!isObj(doc) || !Array.isArray(doc.finance_profiles))
    throw new Error("finance_profiles must be a list");
  const out = {};
  for (const [i, r] of doc.finance_profiles.entries()) {
    const at = `finance_profiles[${i}]`;
    if (!isObj(r)) {
      fail(`${at} must be a mapping`);
      continue;
    }
    if (!COUNTRY_CODES.includes(r.country))
      fail(`${at}: country must be one of ${COUNTRY_CODES.join(", ")}`);
    if (r.product !== PRODUCT) continue;
    if (!numOrNull(r.typical_apr, 0, 100)) fail(`${at}: typical_apr must be a percentage or null`);
    if (!(
      r.default_term_months === null ||
      (Number.isInteger(r.default_term_months) &&
        r.default_term_months >= 1 &&
        r.default_term_months <= 120)
    ))
      fail(`${at}: default_term_months must be 1–120 or null`);
    if (!numOrNull(r.default_deposit_pct, 0, 100))
      fail(`${at}: default_deposit_pct must be a percentage or null`);
    // Every number is traceable: a rate needs a source with a URL, a period and a retrieval date.
    if (r.typical_apr !== null) {
      if (
        !isObj(r.source) ||
        typeof r.source.name !== "string" ||
        typeof r.source.url !== "string" ||
        !r.source.url.startsWith("https://")
      )
        fail(`${at}: typical_apr needs source.name and an https source.url`);
      if (typeof r.retrieved_at !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(r.retrieved_at))
        fail(`${at}: typical_apr needs retrieved_at (YYYY-MM-DD)`);
    }
    if (out[r.country]) fail(`${at}: duplicate ${PRODUCT} row for ${r.country}`);
    const src = isObj(r.source) ? r.source : null;
    out[r.country] = {
      id: r.id,
      country: r.country,
      product: r.product,
      typical_apr: r.typical_apr,
      default_term_months: r.default_term_months,
      default_deposit_pct: r.default_deposit_pct,
      source: src
        ? {
            name: src.name,
            url: src.url,
            series_id: typeof src.series_id === "string" ? src.series_id : null,
            period: src.period === undefined || src.period === null ? null : String(src.period),
          }
        : null,
      retrieved_at: r.retrieved_at ?? null,
      review: r.review === true,
    };
  }
  if (errors.length) throw new Error(errors.join("\n"));
  return Object.fromEntries(COUNTRY_CODES.filter((c) => out[c]).map((c) => [c, out[c]]));
}

export function loadFinance(file = FINANCE_FILE) {
  return validateFinance(yaml.load(readFileSync(file, "utf8"), { schema: yaml.CORE_SCHEMA }));
}

export function serialize(config) {
  return JSON.stringify(config, null, 2) + "\n";
}

function main() {
  const check = process.argv.includes("--check");
  if (!existsSync(FINANCE_FILE)) {
    if (check) throw new Error(`${FINANCE_FILE} not found`);
    console.warn(`finance: ${FINANCE_FILE} not found, keeping ${path.basename(OUT_FILE)}`);
    if (!existsSync(OUT_FILE)) writeFileSync(OUT_FILE, serialize({}));
    return;
  }
  const json = serialize(loadFinance());
  const current = existsSync(OUT_FILE) ? readFileSync(OUT_FILE, "utf8") : "";
  if (check) {
    if (current !== json) {
      console.error(
        "finance: src/config/finance.generated.json is out of date; run `node scripts/finance.mjs`",
      );
      process.exit(1);
    }
    return;
  }
  if (current !== json) writeFileSync(OUT_FILE, json);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
