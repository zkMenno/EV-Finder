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

  it("shortlist scores (T-114): read from shortlist_scores.json next to catalogue.json, null without it", () => {
    const dir = releaseDir(8, "8");
    process.env.CATALOGUE_DIR = dir;
    expect(getCatalogue().shortlistScores()).toBeNull();
    expect(toClientCatalogue(8, [], getCatalogue().rows(), undefined, null).scores).toBe(false);

    const dir2 = releaseDir(9, "9");
    const vid = fixture.rows[0]!.variant_id;
    writeFileSync(
      path.join(dir2, "9", "shortlist_scores.json"),
      JSON.stringify({ release: 9, generated_at: "2026-11-17T00:00:00Z", variants: [{ variant_id: vid, derived: { winter_range_km: 300 }, scores: { "road-tripper": { score: 61.5, band: "shortlist", reasons: ["+dc-speed"] } } }] }),
    );
    process.env.CATALOGUE_DIR = dir2;
    const c = getCatalogue();
    expect(c.shortlistScores()?.variants.get(vid)?.scores["road-tripper"]).toEqual({ score: 61.5, band: "shortlist", reasons: ["+dc-speed"] });
    const client = toClientCatalogue(9, [], c.rows(), undefined, c.shortlistScores());
    expect(client.scores).toBe(true);
    expect(client.rows.find((r) => r.variant_id === vid)?.shortlist).toEqual({ s: { "road-tripper": [61.5, "shortlist", "+dc-speed"] }, d: { winter_range_km: 300 } });
  });

  it("dev fixture carries the pipeline-made fixture scores for every row", () => {
    process.env.CATALOGUE_DIR = mkdtempSync(path.join(tmpdir(), "ev-empty-"));
    const c = getCatalogue();
    const s = c.shortlistScores()!;
    for (const r of c.rows()) expect(s.variants.has(r.variant_id), r.variant_id).toBe(true);
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
