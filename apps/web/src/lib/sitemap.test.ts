import { afterEach, describe, expect, it } from "vitest";
import { getCatalogue } from "./catalogue";
import { pagePaths } from "./sitemap";

describe("sitemap and parked features (Decision 051)", () => {
  afterEach(() => {
    delete process.env.PARKED;
  });
  it("leaves out parked pages by default and lists the launch pages", () => {
    const paths = pagePaths(getCatalogue());
    expect(paths).not.toContain("/top");
    expect(paths).not.toContain("/charging");
    expect(paths).toEqual(expect.arrayContaining(["", "/about", "/learn"]));
  });
  it("lists them when switched on", () => {
    process.env.PARKED = "1";
    const paths = pagePaths(getCatalogue());
    expect(paths).toEqual(expect.arrayContaining(["/top", "/charging"]));
  });
});
