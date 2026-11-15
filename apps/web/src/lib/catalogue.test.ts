import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { catalogue as fixture } from "@/test/helpers";
import { clientCatalogueKey, getCatalogue, latestCataloguePath } from "./catalogue";
import { toClientCatalogue } from "./explore-data";

const prev = process.env.CATALOGUE_DIR;
afterEach(() => {
  if (prev === undefined) delete process.env.CATALOGUE_DIR;
  else process.env.CATALOGUE_DIR = prev;
});

function releaseDir(n: number, latest: string | null) {
  const dir = mkdtempSync(path.join(tmpdir(), "ev-rel-"));
  mkdirSync(path.join(dir, String(n)));
  writeFileSync(path.join(dir, String(n), "catalogue.json"), JSON.stringify({ ...fixture, release: n }));
  if (latest !== null) writeFileSync(path.join(dir, "latest"), latest);
  return dir;
}

describe("catalogue", () => {
  it("falls back to the dev fixture when no release exists", () => {
    process.env.CATALOGUE_DIR = mkdtempSync(path.join(tmpdir(), "ev-empty-"));
    const c = getCatalogue();
    expect(c.origin()).toBe("fixture");
    expect(clientCatalogueKey(c)).toBe("dev");
    expect(c.rows().length).toBeGreaterThanOrEqual(25);
  });

  it("reads the release named by data/releases/latest", () => {
    process.env.CATALOGUE_DIR = releaseDir(7, "7\n");
    const c = getCatalogue();
    expect(c.origin()).toBe("release");
    expect(c.release()).toBe(7);
    expect(clientCatalogueKey(c)).toBe("7");
    const first = c.rows()[0]!;
    expect(c.variant(first.variant_id)).toBe(first);
    expect(c.generation(first.generation_id)?.id).toBe(first.generation_id);
    expect(c.generations().length).toBeGreaterThan(0);
    expect(c.sources().length).toBeGreaterThan(0);
  });

  it("ignores a bad latest pointer", () => {
    expect(latestCataloguePath(releaseDir(2, "nope"))).toBeNull();
    expect(latestCataloguePath(releaseDir(2, "3"))).toBeNull();
  });

  it("fixture: every non-null Explore number has provenance", () => {
    const numeric = ["real_range_km", "battery_kwh_net", "dc_km_per_20min", "dc_km_per_10min", "ac_km_per_h", "boot_l", "length_mm", "towing_kg", "registered_count_nl"] as const;
    for (const r of fixture.rows) {
      for (const f of numeric) if (r[f] != null) expect(r.provenance[f], `${r.variant_id}.${f}`).toBeDefined();
      for (const cc of Object.keys(r.price_new ?? {})) expect(r.provenance[`price_new.${cc}`]).toBeDefined();
    }
  });

  it("client JSON drops unused columns and nulls", () => {
    const c = toClientCatalogue(1, fixture.sources, fixture.rows);
    const r = c.rows[0]! as Record<string, unknown>;
    expect(r.weight_kg).toBeUndefined();
    expect(r.change_markers).toBeUndefined();
    expect(Object.values(r).includes(null)).toBe(false);
    expect(c.sources["dev-fixture"]).toBeDefined();
  });
});
