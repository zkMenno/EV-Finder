import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import fixture from "@/fixtures/catalogue.sample.json";
import { getCatalogue } from "./catalogue";
import { toClientCatalogue } from "./explore-data";

describe("used_prices.json next to the release (T-081)", () => {
  const prev = process.env.CATALOGUE_DIR;
  afterEach(() => {
    if (prev === undefined) delete process.env.CATALOGUE_DIR;
    else process.env.CATALOGUE_DIR = prev;
  });
  const release = (used?: unknown) => {
    const dir = mkdtempSync(path.join(tmpdir(), "ev-vp-"));
    mkdirSync(path.join(dir, "7"));
    writeFileSync(path.join(dir, "7", "catalogue.json"), JSON.stringify({ ...fixture, release: 7 }));
    if (used !== undefined) writeFileSync(path.join(dir, "7", "used_prices.json"), typeof used === "string" ? used : JSON.stringify(used));
    writeFileSync(path.join(dir, "latest"), "7\n");
    return dir;
  };
  const id = (fixture as { rows: { variant_id: string }[] }).rows[0]!.variant_id;

  it("reaches the client catalogue rows in compact form", () => {
    process.env.CATALOGUE_DIR = release({ variants: [{ variant_id: id, bands: { NL: [{ build_year: 2022, p25: 1, median: 2, p75: 3, method: "model" }] } }] });
    const cat = getCatalogue();
    const rows = toClientCatalogue(cat.release(), cat.sources(), cat.rows(), cat.variantUsedPrices()).rows;
    expect(rows.find((r) => r.variant_id === id)?.used_bands).toEqual({ NL: [[2022, 1, 2, 3, 1]] });
    expect(rows.filter((r) => r.used_bands).length).toBe(1);
  });
  it("missing or broken file = no bands, never an error", () => {
    process.env.CATALOGUE_DIR = release();
    expect(getCatalogue().variantUsedPrices().size).toBe(0);
    process.env.CATALOGUE_DIR = release("{not json");
    expect(getCatalogue().variantUsedPrices().size).toBe(0);
  });
});
