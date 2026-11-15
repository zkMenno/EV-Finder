// Server-only read path for the published catalogue (Decision 008).
// A Postgres implementation can sit behind the same `Catalogue` interface later.
import { parseVariantUsedPrices, type VariantUsedPrices } from "./variant-prices";
import { existsSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import type {
  BatteryPack,
  Catalogue as CatalogueFile,
  ChargingStatsRelease,
  Generation,
  Id,
  KnownIssues,
  Platform,
  PublishedVariant,
  Source,
  Taxonomy,
  UsedPriceBand,
} from "@ev/schema";
import fixture from "../fixtures/catalogue.sample.json";
import { isUsedPriceBand } from "./used-rankings";

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
  /**
   * Sourced used-price bands per generation × country (`Catalogue.used_prices`, schema type
   * `UsedPriceBand`). Malformed entries are dropped. Empty until T-056 publishes used prices.
   */
  usedPrices(): UsedPriceBand[];
  /** RDW APK defect rates per generation × first-registration year (`known_issues`), if the release has them. */
  knownIssues(): KnownIssues | undefined;
  /**
   * Public charging statistics (Decision 012, aggregates only): `charging_stats.json` next to the
   * release's catalogue.json. Null when the release has none (or it can't be read).
   */
  chargingStats(): ChargingStatsRelease | null;
  /** Used price bands per variant × build year × country (`used_prices.json`, T-081); empty when the release has none. */
  variantUsedPrices(): VariantUsedPrices;
}

class JsonCatalogue implements Catalogue {
  private readonly byVariant: Map<Id, PublishedVariant>;
  private readonly byGeneration: Map<Id, Generation>;

  private charging: ChargingStatsRelease | null | undefined;
  private used: VariantUsedPrices | undefined;

  constructor(
    private readonly data: CatalogueFile,
    private readonly from: "release" | "fixture",
    /** Path of the release's charging_stats.json (read lazily), or null. */
    private readonly chargingPath: string | null = null,
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
  usedPrices(): UsedPriceBand[] {
    // Schema-typed, but still guarded at runtime: one malformed row must not break a page.
    const raw: unknown = this.data.used_prices;
    return Array.isArray(raw) ? raw.filter(isUsedPriceBand) : [];
  }
  knownIssues(): KnownIssues | undefined {
    return this.data.known_issues;
  }
  chargingStats(): ChargingStatsRelease | null {
    if (this.charging !== undefined) return this.charging;
    this.charging = readChargingStats(this.chargingPath);
    return this.charging;
  }
  variantUsedPrices(): VariantUsedPrices {
    if (this.used) return this.used;
    // Optional file next to charging_stats.json; missing or malformed = no bands (never breaks a page).
    const p = this.chargingPath ? path.join(path.dirname(this.chargingPath), "used_prices.json") : null;
    let doc: unknown = null;
    try {
      if (p && existsSync(p)) doc = JSON.parse(readFileSync(p, "utf8"));
    } catch {
      doc = null;
    }
    this.used = parseVariantUsedPrices(doc);
    return this.used;
  }
}

/** Reads a charging_stats.json; null when missing or malformed (an optional file never breaks a page). */
export function readChargingStats(p: string | null): ChargingStatsRelease | null {
  if (!p || !existsSync(p)) return null;
  try {
    const d = JSON.parse(readFileSync(p, "utf8")) as ChargingStatsRelease;
    return Array.isArray(d?.stats) && Array.isArray(d?.sources) ? d : null;
  } catch (err) {
    if (isBuild()) throw new Error(`catalogue: could not read ${p} during the build`, { cause: err });
    console.error(`catalogue: could not read ${p}`, err);
    return null;
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

/**
 * `next build` bakes static pages from the catalogue (Decision 015), so a release that is missing
 * or half-written while a releases folder exists must fail the build, never silently fall back
 * to the dev fixture (that would publish fixture pages and 404s). At run time the fallback stays.
 */
function isBuild(env: Record<string, string | undefined> = process.env): boolean {
  return env.NEXT_PHASE === "phase-production-build";
}

/** The current catalogue. Re-reads only when the release file changes (pointer swap = rollback). */
export function getCatalogue(): Catalogue {
  const p = latestCataloguePath();
  if (!p) {
    if (isBuild() && existsSync(path.join(releasesDir(), "latest"))) {
      throw new Error(`catalogue: ${releasesDir()}/latest exists but its catalogue.json can't be found (release being written?); refusing to build static pages from the dev fixture`);
    }
    return fixtureCatalogue;
  }
  try {
    const key = `${p}:${statSync(p).mtimeMs}`;
    if (cache?.key === key) return cache.catalogue;
    const data = JSON.parse(readFileSync(p, "utf8")) as CatalogueFile;
    const catalogue = new JsonCatalogue(data, "release", path.join(path.dirname(p), "charging_stats.json"));
    cache = { key, catalogue };
    return catalogue;
  } catch (err) {
    if (isBuild()) throw new Error(`catalogue: could not read ${p} during the build`, { cause: err });
    // A half-written or broken release must not take the site down.
    console.error(`catalogue: could not read ${p}, using dev fixture`, err);
    return fixtureCatalogue;
  }
}

/** Public URL of the compact client catalogue for the current data. */
export function clientCatalogueKey(c: Catalogue): string {
  return c.origin() === "fixture" ? "dev" : String(c.release());
}
