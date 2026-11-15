import type { PublishedVariant } from "@ev/schema";
import { describe, expect, it } from "vitest";
import { registrationItemKey, registrationsFor, registrationsKey, registrationsProvKey } from "./registrations";

const row: Pick<PublishedVariant, "registrations"> = {
  registrations: {
    NL: [
      { count: 900, kind: "new_registrations", period: "2025", level: "generation", source_id: "eea" },
      { count: 5000, kind: "fleet", period: "2026-Q2", level: "generation", source_id: "rdw" },
      { count: 1100, kind: "new_registrations", period: "2026-01..10", level: "generation", source_id: "eea" },
    ],
    UK: [{ count: 12000, kind: "fleet", period: "2026-Q1", level: "model", source_id: "dft-veh" }],
  },
};

describe("registrations", () => {
  it("lists fleet first, then new registrations by newest period; never sums kinds", () => {
    const nl = registrationsFor(row, "NL");
    expect(nl.map((r) => `${r.kind} ${r.period}`)).toEqual(["fleet 2026-Q2", "new_registrations 2026-01..10", "new_registrations 2025"]);
    expect(nl).toHaveLength(3);
  });

  it("is empty for a country without counts", () => {
    expect(registrationsFor(row, "DE")).toEqual([]);
    expect(registrationsFor({}, "NL")).toEqual([]);
    expect(registrationsKey({}, "NL")).toBeNull();
  });

  it("keeps the level, so model-level counts can be labelled", () => {
    expect(registrationsFor(row, "UK")[0]?.level).toBe("model");
  });

  it("compare key changes with any count and the provenance key is per country", () => {
    const other = { registrations: { NL: [{ count: 5001, kind: "fleet" as const, period: "2026-Q2", source_id: "rdw" }] } };
    expect(registrationsKey(row, "NL")).not.toBe(registrationsKey(other, "NL"));
    expect(registrationsProvKey("NL")).toBe("registrations.NL");
  });

  // Q-066: RDW shared-year cars (generation unknown) sit next to the generation-level count with
  // the same kind, period and source. Shape taken from release 1 (Renault Zoe ph1).
  const shared: Pick<PublishedVariant, "registrations"> = {
    registrations: {
      NL: [
        { count: 2720, kind: "fleet", period: "2026-11-15", level: "model", source_id: "rdw" },
        { count: 900, kind: "new_registrations", period: "2019", level: "generation", source_id: "eea" },
        { count: 4794, kind: "fleet", period: "2026-11-15", level: "generation", source_id: "rdw" },
      ],
    },
  };

  it("lists the generation-level count before the model-level one of the same period", () => {
    expect(registrationsFor(shared, "NL").map((r) => `${r.kind} ${r.level} ${r.count}`)).toEqual([
      "fleet generation 4794",
      "fleet model 2720",
      "new_registrations generation 900",
    ]);
  });

  it("list keys stay unique when a row has a generation- and a model-level count for one period", () => {
    const keys = registrationsFor(shared, "NL").map(registrationItemKey);
    expect(new Set(keys).size).toBe(keys.length);
    expect(registrationItemKey({ kind: "fleet", period: "2026-Q2", source_id: "rdw" })).toBe(
      registrationItemKey({ kind: "fleet", period: "2026-Q2", level: "generation", source_id: "rdw" }),
    );
  });

  it("compare key tells a model-level count apart from a generation-level one", () => {
    const genOnly = { registrations: { NL: shared.registrations!.NL!.filter((r) => r.level !== "model") } };
    expect(registrationsKey(shared, "NL")).not.toBe(registrationsKey(genOnly, "NL"));
  });
});
