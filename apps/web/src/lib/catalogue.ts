// Server-only read path for the published catalogue (Decision 008).
// A Postgres implementation can sit behind the same `Catalogue` interface later.
import { readFileSync, statSync } from "node:fs";
import path from "node:path";
import type {
  BatteryPack,
  Catalogue as CatalogueFile,
  Generation,
  Id,
  Platform,
  PublishedVariant,
  Source,
  Taxonomy,
} from "@ev/schema";
import fixture from "../fixtures/catalogue.sample.json";

export interface Catalogue {
  release(): number;
  /** ISO timestamp of the release. */
  generatedAt(): string;
  /** "release" = a published pipeline release; "fixture" = the dev fixture fallback. */
  origin(): "release" | "fixture";
  rows(): PublishedVariant[];
  variant(id: Id): PublishedVariant | undefined;
  generation(id: Id): Generation | undefined;
  generations(): Generation[];
  sources(): Source[];
  /** Taxonomy tables (Decision 010). Falls back to the dev fixture's sample tables if a release has none. */
  taxonomy(): Taxonomy;
  platforms(): Platform[];
  batteryPacks(): BatteryPack[];
}

class JsonCatalogue implements Catalogue {
  private readonly byVariant: Map<Id, PublishedVariant>;
  private readonly byGeneration: Map<Id, Generation>;

  constructor(
    private readonly data: CatalogueFile,
    private readonly from: "release" | "fixture",
  ) {
    this.byVariant = new Map(data.rows.map((r) => [r.variant_id, r]));
    this.byGeneration = new Map((data.generations ?? []).map((g) => [g.id, g]));
  }
  release(): number {
    return this.data.release;
  }
  origin(): "release" | "fixture" {
    return this.from;
  }
  generatedAt(): string {
    return this.data.generated_at;
  }
  rows(): PublishedVariant[] {
    return this.data.rows;
  }
  variant(id: Id): PublishedVariant | undefined {
    return this.byVariant.get(id);
  }
  generation(id: Id): Generation | undefined {
    return this.byGeneration.get(id);
  }
  generations(): Generation[] {
    return this.data.generations ?? [];
  }
  sources(): Source[] {
    return this.data.sources;
  }
  taxonomy(): Taxonomy {
    return this.data.taxonomy ?? (fixture as unknown as CatalogueFile).taxonomy!;
  }
  platforms(): Platform[] {
    return this.data.platforms ?? [];
  }
  batteryPacks(): BatteryPack[] {
    return this.data.battery_packs ?? [];
  }
}

/** Directory holding `<n>/catalogue.json` and `latest`. CATALOGUE_DIR overrides it. */
export function releasesDir(): string {
  return process.env.CATALOGUE_DIR ?? path.resolve(process.cwd(), "../../data/releases");
}

/**
 * Path of the current release's catalogue.json, or null when no release exists.
 * `latest` may be a text file holding the release number, or a symlink/dir to the release.
 */
export function latestCataloguePath(dir: string = releasesDir()): string | null {
  const latest = path.join(dir, "latest");
  try {
    const st = statSync(latest);
    if (st.isDirectory()) {
      const p = path.join(latest, "catalogue.json");
      statSync(p);
      return p;
    }
    const n = readFileSync(latest, "utf8").trim();
    if (!/^\d+$/.test(n)) return null;
    const p = path.join(dir, n, "catalogue.json");
    statSync(p);
    return p;
  } catch {
    return null;
  }
}

let cache: { key: string; catalogue: Catalogue } | null = null;
const fixtureCatalogue = new JsonCatalogue(fixture as unknown as CatalogueFile, "fixture");

/** The current catalogue. Re-reads only when the release file changes (pointer swap = rollback). */
export function getCatalogue(): Catalogue {
  const p = latestCataloguePath();
  if (!p) return fixtureCatalogue;
  try {
    const key = `${p}:${statSync(p).mtimeMs}`;
    if (cache?.key === key) return cache.catalogue;
    const data = JSON.parse(readFileSync(p, "utf8")) as CatalogueFile;
    const catalogue = new JsonCatalogue(data, "release");
    cache = { key, catalogue };
    return catalogue;
  } catch (err) {
    // A half-written or broken release must not take the site down.
    console.error(`catalogue: could not read ${p}, using dev fixture`, err);
    return fixtureCatalogue;
  }
}

/** Public URL of the compact client catalogue for the current data. */
export function clientCatalogueKey(c: Catalogue): string {
  return c.origin() === "fixture" ? "dev" : String(c.release());
}
