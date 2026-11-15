import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { parseOpenBundle } from "./open-data";

const here = path.dirname(fileURLToPath(import.meta.url));

describe("open data bundle (Decision 016)", () => {
  it("reads release 1's manifest: CSV first, sizes and sha256, GitHub release links", () => {
    const m = JSON.parse(readFileSync(path.resolve(here, "../../../../data/releases/1/manifest.json"), "utf8"));
    const b = parseOpenBundle(m)!;
    expect(b.release).toBe(1);
    expect(b.files.map((f) => f.name).slice(0, 2)).toEqual(["variants.csv", "variants.json"]);
    expect(b.files.every((f) => f.url.startsWith("https://github.com/zkMenno/EV-Finder/releases/download/data-v1/open."))).toBe(true);
  });
  it("skips unsafe rows and foreign hosts", () => {
    const base = { release: 2, files: [{ path: "open/x.csv", asset: "open.x.csv", bytes: 1, sha256: "a".repeat(64) }] };
    expect(parseOpenBundle({ ...base, storage: { download_url: "https://evil.example/{asset}" } })).toBeNull();
    expect(parseOpenBundle({ ...base, storage: { download_url: "http://github.com/{asset}" } })).toBeNull();
    expect(parseOpenBundle({ ...base, files: [{ ...base.files[0], path: "open/../x" }], storage: { download_url: "https://github.com/{asset}" } })).toBeNull();
    expect(parseOpenBundle({ ...base, storage: { download_url: "https://github.com/r/{asset}" } })!.files).toHaveLength(1);
    expect(parseOpenBundle(null)).toBeNull();
  });
});
