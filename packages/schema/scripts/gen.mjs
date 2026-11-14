// Generates TS types and Pydantic models from schemas/ev.schema.json.
// Run: pnpm --filter @ev/schema gen   (needs `uvx` for the Python side)
import { compile } from "json-schema-to-typescript";
import { readFileSync, writeFileSync, mkdirSync, copyFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const schemaPath = join(root, "schemas/ev.schema.json");
const schema = JSON.parse(readFileSync(schemaPath, "utf8"));
const banner = "// GENERATED from schemas/ev.schema.json by scripts/gen.mjs. Do not edit.\n";

const ts = await compile(schema, "EvSchema", {
  bannerComment: banner,
  unreachableDefinitions: true,
  additionalProperties: false,
  style: { singleQuote: false },
});
mkdirSync(join(root, "generated/ts"), { recursive: true });
writeFileSync(join(root, "generated/ts/index.ts"), ts);

const pyOut = join(root, "generated/python/ev_schema.py");
mkdirSync(dirname(pyOut), { recursive: true });
execFileSync(
  "uvx",
  [
    "--from",
    "datamodel-code-generator==0.26.3",
    "datamodel-codegen",
    "--input",
    schemaPath,
    "--input-file-type",
    "jsonschema",
    "--output",
    pyOut,
    "--output-model-type",
    "pydantic_v2.BaseModel",
    "--target-python-version",
    "3.12",
    "--use-standard-collections",
    "--use-union-operator",
    "--disable-timestamp",
    "--use-title-as-name",
    "--field-constraints",
  ],
  { stdio: "inherit" },
);
// The pipeline imports the same models (schema lane owns this copy).
copyFileSync(pyOut, join(root, "../../pipeline/ev_pipeline/schema_models.py"));
console.log("generated TS + Python types");
