// The open data bundle (Decision 016): the CC BY 4.0 files of the current release, read from its
// manifest.json (Decision 035). Files outside git are published as release assets; the page
// links to them by the manifest's download URL and shows size and sha256 so anyone can check.
// Server only (reads the release folder next to catalogue.json).
import { readFileSync } from "node:fs";
import path from "node:path";
import { latestCataloguePath } from "./catalogue";

export interface OpenFile {
  /** File name inside open/, e.g. "variants.csv". */
  name: string;
  bytes: number;
  sha256: string;
  url: string;
}

export interface OpenBundle {
  release: number;
  generatedAt: string;
  files: OpenFile[];
}

/** Hosts a download link may point at (same list as data/releases/publish.yaml). */
const HOSTS = new Set(["github.com"]);
/** Files people want first. */
const ORDER = ["variants.csv", "variants.json", "README.md", "ATTRIBUTION.md", "LICENSE"];

const isObj = (v: unknown): v is Record<string, unknown> => v !== null && typeof v === "object" && !Array.isArray(v);

/** Pure: manifest JSON → bundle, or null when it has no valid open/ files. Bad rows are skipped. */
export function parseOpenBundle(manifest: unknown): OpenBundle | null {
  if (!isObj(manifest) || !Number.isInteger(manifest.release) || !Array.isArray(manifest.files)) return null;
  const storage = isObj(manifest.storage) ? manifest.storage : {};
  const tpl = typeof storage.download_url === "string" ? storage.download_url : "";
  const files: OpenFile[] = [];
  for (const f of manifest.files) {
    if (!isObj(f) || typeof f.path !== "string" || !f.path.startsWith("open/")) continue;
    const name = f.path.slice(5);
    if (!/^[A-Za-z0-9._-]+$/.test(name) || typeof f.asset !== "string" || !/^[A-Za-z0-9._-]+$/.test(f.asset)) continue;
    if (typeof f.bytes !== "number" || typeof f.sha256 !== "string" || !/^[0-9a-f]{64}$/.test(f.sha256)) continue;
    let url: URL;
    try {
      url = new URL(tpl.replace("{asset}", encodeURIComponent(f.asset)));
    } catch {
      continue;
    }
    if (url.protocol !== "https:" || !HOSTS.has(url.hostname)) continue;
    files.push({ name, bytes: f.bytes, sha256: f.sha256, url: url.toString() });
  }
  if (!files.length) return null;
  const rank = (n: string) => (ORDER.includes(n) ? ORDER.indexOf(n) : ORDER.length);
  files.sort((a, b) => rank(a.name) - rank(b.name) || a.name.localeCompare(b.name));
  return {
    release: manifest.release as number,
    generatedAt: typeof manifest.generated_at === "string" ? manifest.generated_at : "",
    files,
  };
}

/** The current release's bundle; null without a release or a manifest. */
export function openDataBundle(): OpenBundle | null {
  const p = latestCataloguePath();
  if (!p) return null;
  try {
    return parseOpenBundle(JSON.parse(readFileSync(path.join(path.dirname(p), "manifest.json"), "utf8")));
  } catch {
    return null;
  }
}
