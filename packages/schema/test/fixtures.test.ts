import { describe, expect, it } from "vitest";
import Ajv2020 from "ajv/dist/2020";
import addFormats from "ajv-formats";
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import schema from "../schemas/ev.schema.json";
import type { PublishedVariant } from "../generated/ts";

const ajv = new Ajv2020({ allErrors: true, strict: false });
addFormats(ajv);
ajv.addSchema(schema);
const ref = (def: string) => ajv.getSchema(`${schema.$id}#/$defs/${def}`)!;
const fixturesDir = join(import.meta.dirname, "../fixtures");

// fixture file name: <entity-kebab>.<valid|invalid>.json
const defFor = (file: string) =>
  file
    .split(".")[0]
    .split("-")
    .map((p) => p[0].toUpperCase() + p.slice(1))
    .join("");

describe("schema fixtures", () => {
  for (const file of readdirSync(fixturesDir)) {
    const data = JSON.parse(readFileSync(join(fixturesDir, file), "utf8"));
    const shouldPass = file.includes(".valid.");
    it(`${file} is ${shouldPass ? "valid" : "rejected"}`, () => {
      const validate = ref(defFor(file));
      expect(validate(data), JSON.stringify(validate.errors)).toBe(shouldPass);
    });
  }

  it("generated TS type matches the fixture shape", () => {
    const row: PublishedVariant = JSON.parse(
      readFileSync(join(fixturesDir, "published-variant.valid.json"), "utf8"),
    );
    expect(row.era).toBe("2018-20");
  });
});
