import { describe, expect, it } from "vitest";
import { resolveLevel } from "./use-level";

describe("resolveLevel", () => {
  it("URL wins, then the stored level, else detailed", () => {
    expect(resolveLevel("?level=nerd", "simple")).toBe("nerd");
    expect(resolveLevel("", "simple")).toBe("simple");
    expect(resolveLevel("?level=bogus", "junk")).toBe("detailed");
    expect(resolveLevel("", null)).toBe("detailed");
  });
});
