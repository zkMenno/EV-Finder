import { describe, expect, it } from "vitest";
import { catalogueRedirect } from "./catalogue-redirect";

describe("catalogueRedirect (T-130)", () => {
  it("sends old Explore links (view or sort) to /cars with the whole query", () => {
    expect(catalogueRedirect({ view: "table", range: "300" })).toBe("?view=table&range=300");
    expect(catalogueRedirect({ sort: "-dc", make: ["kia", "tesla"] })).toBe("?sort=-dc&make=kia&make=tesla");
  });
  it("leaves hero links and plain landing visits alone", () => {
    expect(catalogueRedirect({})).toBeNull();
    expect(catalogueRedirect({ range: "300" })).toBeNull();
    expect(catalogueRedirect({ role: "only", sort: "-suggested" })).toBeNull();
    expect(catalogueRedirect({ budget: "20000", view: "cards" })).toBeNull();
  });
});
