import { describe, expect, it } from "vitest";
import { row } from "@/test/helpers";
import { EXPLORE_FIELDS } from "./explore-data";

describe("Explore rows keep WLTP, never EPA (T-061)", () => {
  it("does not ship epa_range_km to the browser", () => {
    expect(EXPLORE_FIELDS as readonly string[]).not.toContain("epa_range_km");
    const r = row({ variant_id: "x", wltp_range_km: 400, epa_range_km: 350, provenance: { epa_range_km: { source_ids: ["fueleconomy"], confidence: "medium" } } });
    expect(r).not.toHaveProperty("epa_range_km");
    expect(r.provenance).not.toHaveProperty("epa_range_km");
    expect(r.wltp_range_km).toBe(400);
  });
});
