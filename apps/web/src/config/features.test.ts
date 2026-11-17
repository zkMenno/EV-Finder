import { describe, expect, it } from "vitest";
import { parkedEnabled, PARKED_FLAGS, tripFitEnabled } from "./features";

describe("feature flags (Decision 051)", () => {
  it("parked features are off by default", () => {
    for (const f of Object.keys(PARKED_FLAGS) as (keyof typeof PARKED_FLAGS)[]) expect(parkedEnabled(f, {})).toBe(false);
    expect(tripFitEnabled({})).toBe(false);
  });
  it("one variable turns one on; PARKED=1 turns all on", () => {
    expect(parkedEnabled("rankings", { RANKINGS: "1" })).toBe(true);
    expect(parkedEnabled("knownIssues", { RANKINGS: "1" })).toBe(false);
    expect(parkedEnabled("chargingLinks", { PARKED: "1" })).toBe(true);
    expect(parkedEnabled("chargingLinks", { CHARGING_LINKS: "true" })).toBe(false);
  });
});
