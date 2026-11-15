import { describe, expect, it } from "vitest";
import { EXPLORE_ENTRIES, exploreChunks, parseClientReferenceManifest } from "../../scripts/budget.mjs";

describe("perf budget script", () => {
  it("parses a client-reference manifest", () => {
    const src = 'globalThis.__RSC_MANIFEST = globalThis.__RSC_MANIFEST || {};\nglobalThis.__RSC_MANIFEST["/[country]/page"] = {"entryJSFiles":{"a":["x.js"]}};\n';
    expect(parseClientReferenceManifest(src)).toEqual({ entryJSFiles: { a: ["x.js"] } });
  });

  it("counts root + Explore entry chunks once and leaves noModule polyfills out", () => {
    const build = { rootMainFiles: ["r1.js", "r2.js"], polyfillFiles: ["poly.js"] };
    const entryJSFiles = Object.fromEntries(EXPLORE_ENTRIES.map((e, i) => [e, ["shared.js", `e${i}.js`, "style.css"]]));
    const { modern, polyfills } = exploreChunks(build, { entryJSFiles });
    expect(modern.sort()).toEqual(["e0.js", "e1.js", "r1.js", "r2.js", "shared.js"]);
    expect(polyfills).toEqual(["poly.js"]);
  });

  it("fails loudly when the Explore route is missing from the manifest", () => {
    expect(() => exploreChunks({}, { entryJSFiles: {} })).toThrow(/no entry/);
  });
});
