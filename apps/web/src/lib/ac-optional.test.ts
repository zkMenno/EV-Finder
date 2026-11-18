import { describe, expect, it } from "vitest";
import { acOptionalKw } from "./ac-optional";

describe("acOptionalKw (optional on-board charger)", () => {
  it("returns the optional kW when it is above the standard one", () => {
    expect(acOptionalKw({ ac_kw: 7.4, ac_kw_optional: 11 })).toBe(11);
  });
  it("hides it when missing, zero, equal or lower", () => {
    expect(acOptionalKw({ ac_kw: 7.4, ac_kw_optional: null })).toBeNull();
    expect(acOptionalKw({ ac_kw: 7.4 })).toBeNull();
    expect(acOptionalKw({ ac_kw: 11, ac_kw_optional: 0 })).toBeNull();
    expect(acOptionalKw({ ac_kw: 11, ac_kw_optional: 11 })).toBeNull();
    expect(acOptionalKw({ ac_kw: 22, ac_kw_optional: 11 })).toBeNull();
  });
  it("still shows it when the standard power is unknown", () => {
    expect(acOptionalKw({ ac_kw: null, ac_kw_optional: 11 })).toBe(11);
  });
});
