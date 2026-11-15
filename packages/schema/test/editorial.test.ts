// T-066: the editorial YAML files validate against the schema, and their cross-references hold.
import { describe, expect, it } from "vitest";
import Ajv2020 from "ajv/dist/2020";
import addFormats from "ajv-formats";
import { load } from "js-yaml";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import schema from "../schemas/ev.schema.json";
import type { EditorialPicks, ShortlistRules, UsageProfile } from "../generated/ts";

const ajv = new Ajv2020({ allErrors: true, strict: false });
addFormats(ajv);
ajv.addSchema(schema);
const ref = (def: string) => ajv.getSchema(`${schema.$id}#/$defs/${def}`)!;
const dataDir = join(import.meta.dirname, "../../../data");

// T-066 moves the rules to data/taxonomy; until then they live in data/editorial.
const rulesPath = ["taxonomy/shortlist_rules.yaml", "editorial/shortlist_rules.yaml"]
  .map((p) => join(dataDir, p))
  .find((p) => existsSync(p));
const picksPath = join(dataDir, "editorial/menno-picks.yaml");
const readYaml = (p: string): unknown => load(readFileSync(p, "utf8"));

describe("shortlist_rules.yaml", () => {
  it("exists", () => expect(rulesPath).toBeDefined());
  const rules = (rulesPath ? readYaml(rulesPath) : {}) as ShortlistRules;

  it("validates against ShortlistRules", () => {
    const validate = ref("ShortlistRules");
    expect(validate(rules), JSON.stringify(validate.errors, null, 1)).toBe(true);
  });

  const all: UsageProfile[] = [...(rules.profiles ?? []), ...(rules.addons ?? [])];
  const factorIds = new Set(
    all.flatMap((p) => [...(p.factors ?? []), ...(p.extra_factors ?? [])].map((f) => f.id)),
  );
  const profileIds = new Set((rules.profiles ?? []).map((p) => p.id));
  const modifierIds = new Set((rules.modifiers ?? []).map((m) => m.id));
  const questions = new Map((rules.picker ?? []).map((q) => [q.id, new Set(q.answers)]));

  it("weight steps name existing factors", () => {
    const owners = [...all, ...(rules.modifiers ?? [])];
    const bad = owners.flatMap((o) =>
      Object.keys(o.weight_steps ?? {})
        .filter((k) => !factorIds.has(k))
        .map((k) => `${o.id}: ${k}`),
    );
    expect(bad).toEqual([]);
  });

  it("combines_with and applies_with point at real rows", () => {
    const bad = [
      ...all.flatMap((p) => (p.combines_with ?? []).filter((id) => !profileIds.has(id))),
      ...all
        .flatMap((p) => [...(p.bonuses ?? []), ...(p.penalties ?? [])])
        .map((a) => a.applies_with)
        .filter((id): id is string => !!id && !modifierIds.has(id)),
    ];
    expect(bad).toEqual([]);
  });

  it("profile picker answers exist in the picker", () => {
    const owners = [...all, ...(rules.modifiers ?? [])];
    const bad = owners.flatMap((o) =>
      Object.entries<string[]>(
        o.picker ?? ("applies_when" in o ? o.applies_when : {}) ?? {},
      ).flatMap(([q, answers]) =>
        answers
          .filter((a: string) => !questions.get(q)?.has(a))
          .map((a: string) => `${o.id}: ${q}=${a}`),
      ),
    );
    expect(bad).toEqual([]);
  });
});

describe("menno-picks.yaml", () => {
  it("validates against EditorialPicks", () => {
    const picks = readYaml(picksPath) as EditorialPicks;
    const validate = ref("EditorialPicks");
    expect(validate(picks), JSON.stringify(validate.errors?.slice(0, 5), null, 1)).toBe(true);
  });
});

// sheet_values are internal (data/editorial/README.md): no published type may reach them.
describe("internal editorial types stay out of published types", () => {
  const defs = schema.$defs as Record<string, unknown>;
  const reachable = (start: string): Set<string> => {
    const seen = new Set<string>();
    const walk = (name: string) => {
      if (seen.has(name)) return;
      seen.add(name);
      const refs = JSON.stringify(defs[name]).match(/#\/\$defs\/[A-Za-z0-9]+/g) ?? [];
      refs.forEach((r) => walk(r.slice("#/$defs/".length)));
    };
    walk(start);
    return seen;
  };
  const published = [
    "Catalogue",
    "EditorialPick",
    "ShortlistScoresRelease",
    "TownsRelease",
    "ConsumptionMatrixRelease",
    "ChargingStatsRelease",
  ];
  for (const root of published) {
    it(`${root} never reaches sheet values`, () => {
      const r = reachable(root);
      expect(r.has("EditorialSheetValues")).toBe(false);
      expect(r.has("EditorialPickSheetRow")).toBe(false);
    });
  }
});
