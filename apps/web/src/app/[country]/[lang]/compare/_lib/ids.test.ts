import { describe, expect, it } from "vitest";
import { compareHref } from "@/lib/compare-store";
import { compareUrl, parseCompareIds } from "./ids";

describe("parseCompareIds", () => {
  it("splits, trims, de-duplicates and caps at 4", () => {
    expect(parseCompareIds("a, b,,a,c,d,e")).toEqual(["a", "b", "c", "d"]);
    expect(parseCompareIds(["a,b", "c"])).toEqual(["a", "b", "c"]);
    expect(parseCompareIds(undefined)).toEqual([]);
    expect(parseCompareIds("")).toEqual([]);
  });
  it("drops ids that are not catalogue-shaped", () => {
    expect(parseCompareIds("ok-1,<script>,UPPER,../x")).toEqual(["ok-1"]);
  });
  it("reads what the tray links to", () => {
    const href = compareHref("/nl/nl", [
      { id: "vw-id3-gen1-pro", label: "x" },
      { id: "kia-ev6-cv-77kwh", label: "y" },
    ]);
    const ids = new URL(href, "http://x").searchParams.get("ids");
    expect(parseCompareIds(ids)).toEqual(["vw-id3-gen1-pro", "kia-ev6-cv-77kwh"]);
  });
});

describe("compareUrl", () => {
  it("keeps ids and the diff toggle in the URL", () => {
    expect(compareUrl("/nl/nl", ["a", "b"])).toBe("/nl/nl/compare?ids=a,b");
    expect(compareUrl("/nl/nl", ["a", "b"], true)).toBe("/nl/nl/compare?ids=a,b&diff=1");
    expect(compareUrl("/de/de", [])).toBe("/de/de/compare");
  });
});
