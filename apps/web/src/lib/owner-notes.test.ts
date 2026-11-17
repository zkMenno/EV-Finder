import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { loadOwnerNotes, OUT_FILE, ownerNotes, serialize } from "../../scripts/owner-picks.mjs";

describe("owner's notes (T-067, Decision 038)", () => {
  it("generated JSON is in step with data/editorial/menno-picks.yaml", () => {
    expect(readFileSync(OUT_FILE, "utf8")).toBe(serialize(loadOwnerNotes()));
  });
  it("carries verdict and note only, never sheet values", () => {
    const raw = readFileSync(OUT_FILE, "utf8");
    expect(raw).not.toMatch(/sheet_values|efficiency_wh_km|dc_km_per_h|evdb/);
    const out = ownerNotes({
      primary_car_picks: [
        { seed_generation_id: "a-b-gen1", model_year: 2022, verdict: "shortlist", notes: " Good ", sheet_values: { x: 1 } },
        { seed_generation_id: "a-b-gen1", model_year: 2024, verdict: "unrated", notes: null },
        { seed_generation_id: null, verdict: "shortlist", notes: "no id" },
        { seed_generation_id: "BAD ID", verdict: "shortlist" },
      ],
    }) as { generations: Record<string, unknown[]> };
    expect(out.generations).toEqual({
      "a-b-gen1": [{ model_year: 2022, variant: null, verdict: "shortlist", favourite: false, note: "Good" }],
    });
  });
});
